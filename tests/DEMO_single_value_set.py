import numpy as np
from scipy.special import erf

def main():
    print("==================================================")
    print("      FSO LINK BUDGET DEMO (SINGLE VALUE SET)     ")
    print("==================================================")

    # ==========================================
    # 0. PARAMETER-DEFINITION (Der "Wertesatz")
    # ==========================================
    # System
    wavelength_nm = 1550.0       # Wellenlänge (nm)
    L_km = 1.0                   # Distanz (km)
    L_m = L_km * 1000            # Distanz (m)
    P_tx_dBm = 30.0              # Sendeleistung (dBm) -> 1 W
    #P_tx_dBm = 10.0              # Sendeleistung (dBm) -> 10 mW
    data_rate = 1e9              # 1 Gbps

    # Optik
    theta_mrad = 2.0             # Divergenz Vollwinkel (mrad)
    rx_aperture_cm = 10.0        # Empfänger-Durchmesser (cm)
    fov_mrad = 2.0               # Field of View (mrad)
    filter_width_nm = 10.0       # Optischer Bandpass (nm)
    
    # Kanal / Umwelt
    visibility_km = 2.0          # Sichtweite (km) -> leichter Nebel
    jitter_sigma_m = 0.05        # 5 cm Wackeln (RMS)
    Cn2 = 5e-14                  # Mittlere bis starke Turbulenz
    
    # Empfänger-Elektronik
    R_resp = 0.9                 # Responsivity (A/W)
    T_kelvin = 300               # Temperatur
    R_load = 50                  # Lastwiderstand (Ohm)

    q_charge = 1.602e-19          # Elementarladung (C)
    kB = 1.38e-23                 # Boltzmann-Konstante (J/K)

    print(f"Szenario: {L_km} km Distanz, {visibility_km} km Sichtweite, {wavelength_nm} nm Laser, {P_tx_dBm} dBm Sendeleistung")
    print("--------------------------------------------------\n")


    # ==========================================
    # A. GEOMETRIC & POINTING LOSS
    # ==========================================
    print(">>> A. Geometric & Pointing Loss")
    
    # 1. Strahlaufweitung (w_L)
    theta_rad = (theta_mrad / 1000.0) / 2.0  # Halber Winkel in rad
    w_L = theta_rad * L_m
    
    # 2. Geometrischer Basis-Verlust (A0)
    rx_radius_m = (rx_aperture_cm / 100.0) / 2.0
    v = (np.sqrt(np.pi) * rx_radius_m) / (np.sqrt(2) * w_L)
    A0 = erf(v)**2
    
    # 3. Pointing Error (Für die Demo nehmen wir exakt 1x Sigma als festen Offset an)
    r_offset = jitter_sigma_m 
    w_eq_sq = (w_L**2 * np.sqrt(np.pi) * erf(v)) / (2 * v * np.exp(-v**2))
    h_p = A0 * np.exp(-2 * r_offset**2 / w_eq_sq)

    print(f"  - Strahlradius am Ziel (w_L):  {w_L:.3f} m")
    print(f"  - Basis-Geometrie Loss (A0):   {A0:.6f} ({10*np.log10(A0):.2f} dB)")
    print(f"  - Effektiver Loss mit Jitter:  {h_p:.6f} ({10*np.log10(h_p):.2f} dB)\n")


    # ==========================================
    # B. ATMOSPHERIC LOSS (Kim Model)
    # ==========================================
    print(">>> B. Atmospheric Loss")
    
    if visibility_km > 50:
        q = 1.6
    elif visibility_km > 6:
        q = 1.3
    else:
        q = 0.585 * (visibility_km**(1/3))
        
    sigma_atm = (3.91 / visibility_km) * ((wavelength_nm / 550.0)**(-q))
    h_atm = np.exp(-sigma_atm * L_km)

    print(f"  - q-Faktor (Kim):              {q:.3f}")
    print(f"  - Dämpfungskoeffizient:        {sigma_atm:.3f} 1/km")
    print(f"  - Atmosphärische Transmission: {h_atm:.6f} ({10*np.log10(h_atm):.2f} dB)\n")


    # ==========================================
    # C. ATMOSPHERIC TURBULENCE (Scintillation)
    # ==========================================
    print(">>> C. Atmospheric Turbulence (Parameters)")
    
    k = 2 * np.pi / (wavelength_nm * 1e-9)
    sigma_R2 = 1.23 * Cn2 * (k**(7/6)) * (L_m**(11/6))
    
    term_alpha = (0.49 * sigma_R2) / ((1 + 1.11 * sigma_R2**(12/5))**(7/6))
    alpha = 1 / (np.exp(term_alpha) - 1)
    
    term_beta = (0.51 * sigma_R2) / ((1 + 0.69 * sigma_R2**(12/5))**(5/6))
    beta = 1 / (np.exp(term_beta) - 1)

    print(f"  - Rytov Varianz (Stärke):      {sigma_R2:.3f}")
    print(f"  - Gamma-Gamma Alpha:           {alpha:.3f}")
    print(f"  - Gamma-Gamma Beta:            {beta:.3f}")
    print("  (Hinweis: Für das mittlere Link-Budget wird h_turb = 1.0 angenommen)\n")


    # Berechnung der Fading Margin via Monte-Carlo Simulation
    # 1. Ziel-Zuverlässigkeit festlegen (z.B. 99.9% -> Outage = 1e-3)
    p_outage = 1e-3 
    
    # 2. Simulation einer großen Anzahl von Werten
    # Trick: I = x * y, wobei x ~ Gamma(alpha) und y ~ Gamma(beta)
    # scale = 1/shape, damit der Mittelwert 1 bleibt
    num_samples = 1_000_000
    x = np.random.gamma(shape=alpha, scale=1/alpha, size=num_samples)
    y = np.random.gamma(shape=beta, scale=1/beta, size=num_samples)
    I_sim = x * y
    
    # 3. Den Schwellenwert (I_th) finden, der das 0.1% Quantil darstellt
    I_th = np.percentile(I_sim, p_outage * 100) # percentile nimmt Prozent (0 bis 100)
    
    # 4. Marge berechnen (Abstand vom Mittelwert 1.0 in dB)
    margin_dB = -10 * np.log10(I_th)
    
    print(f"  - Schwellenwert (für {100-p_outage*100}%):    {I_th:.4f}")
    print(f"  - BENÖTIGTE FADING MARGIN:     {margin_dB:.2f} dB\n")


    # ==========================================
    # D. BACKGROUND NOISE & THERMAL NOISE
    # ==========================================
    print(">>> D. Receiver Noise Power")
    
    # P_tx in Watt umrechnen und P_rx berechnen (Mittelwert ohne Turbulenz-Fading)
    P_tx_W = 10**(P_tx_dBm / 10) * 1e-3
    P_rx_avg = P_tx_W * h_p * h_atm

    # HIER kommt der Turbulenz-Outage (C) ins Spiel!
    # Wir berechnen das System für den Moment, in dem das Signal am schwächsten ist.
    P_rx_worst = P_rx_avg * I_th
    
    # Signalstrom (I_signal) berechnen
    I_signal_worst = R_resp * P_rx_worst

    # Hintergrundrauschen (bewölkter Tag: L_sky = 0.01 W/m^2/sr/nm)
    L_sky = 0.01 
    A_rx = np.pi * rx_radius_m**2
    Omega = np.pi * (fov_mrad / 1000.0 / 2)**2
    P_bg = L_sky * A_rx * Omega * filter_width_nm
    I_bg = R_resp * P_bg
    
    # Rauischen: Shot Noise + Thermal Noise
    # Beachte: Das Shot-Noise hängt vom (schwachen) Signalstrom + Hintergrund ab
    sigma_sq_shot = 2 * q_charge * (I_signal_worst + I_bg) * data_rate
    sigma_sq_thermal = (4 * kB * T_kelvin * data_rate) / R_load
    
    sigma_sq_total = sigma_sq_shot + sigma_sq_thermal

    print(f"  - Empfangene Opt. Leistung:    {P_rx_avg*1e6:.2f} µW")
    print(f"  - Signalstrom (I_sig):         {I_signal_worst*1e6:.2f} µA")
    print(f"  - Shot Noise Varianz:          {sigma_sq_shot:.3e} A^2")
    print(f"  - Thermal Noise Varianz:       {sigma_sq_thermal:.3e} A^2")
    print(f"  - Dominierendes Rauschen:      {'Thermal' if sigma_sq_thermal > sigma_sq_shot else 'Shot'}\n")


    # ==========================================
    # ZIELGRÖSSE: SNR & Eb/N0
    # ==========================================
    print(">>> ZIELGRÖSSEN FÜR DIGITALE SIMULATION")
    
    # --- 1. Der Durchschnittsfall (Mittelwert ohne Turbulenz-Einbrüche) ---
    SNR_linear_worst = (I_signal_worst**2) / sigma_sq_total
    SNR_dB_worst = 10 * np.log10(SNR_linear_worst)
    EbN0_dB_worst = SNR_dB_worst # (Annahme: Bandbreite == Bitrate)

    print(f"Unter Berücksichtigung aller Verluste und des schwächsten Signals (99.9% Zuverlässigkeit) ergibt sich:")
    print(f"  => Mittleres elektrisches SNR: {SNR_dB_worst:.2f} dB")
    print(f"  => Mittleres Eb/N0:            {EbN0_dB_worst:.2f} dB")
    print("==================================================")

if __name__ == "__main__":
    main()