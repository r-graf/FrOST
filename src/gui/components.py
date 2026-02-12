import numpy as np
from scipy.special import erf
from scipy.special import gamma as gamma_func
from scipy.special import kv
import matplotlib.pyplot as plt

# A. Berechnung des Geometric Loss und Pointing Errors für FSO-Kommunikation

def calculate_geometric_and_pointing_loss(L, theta, a, jitter_sigma, n_samples=10000):
    """
    Docstring for calculate_geometric_and_pointing_loss
    
    :param L: Distanz (km)
    :param theta: Divergenzwinkel (rad)
    :param a: Radius der Empfangsaperatur (m)
    :param jitter_sigma: Standardabweichung des Jitters (m) am Empfänger
    :param n_samples: Anzahl der Stichproben für die Monte-Carlo-Simulation
    """

    # 1. Strahlradius am Empfänger (w_L)
    # Annahme: Fernfeld, w0 vernachlässigbar klein im Vergleich zu theta*L
    w_L = theta * L

    # 2. Geometrischer Verlust (ohne Misalignment) - Deterministic
    # Verhältnis v berechnen
    v = (np.sqrt(np.pi) * a) / (np.sqrt(2) * w_L)
    
    # A0: Maximale Fraktion der Leistung, die gesammelt werden kann
    A0 = erf(v)**2
    
    # 3. Pointing Error (Misalignment) - Stochastic
    # Äquivalente Strahlbreite (w_eq) nach Farid & Hranilovic
    w_eq_sq = (w_L**2 * np.sqrt(np.pi) * erf(v)) / (2 * v * np.exp(-v**2))
    
    # Simulation der radialen Verschiebung r (Rayleigh-verteilt)
    # r entsteht aus x und y Jitter (beide normalverteilt mit sigma)
    # numpy.random.rayleigh nimmt 'scale' Parameter, der sigma entspricht
    r = np.random.rayleigh(scale=jitter_sigma, size=n_samples)
    
    # Berechnung des Dämpfungsfaktors h_p für jedes Sample
    # h_p beinhaltet SOWOHL geometric loss (A0) ALS AUCH misalignment
    h_p = A0 * np.exp(-2 * r**2 / w_eq_sq)
    
    return h_p, A0 # Array von Dämpfungsfaktoren (0 bis A0)

def calculate_geometric_and_pointing_loss_paper(L, theta, d1, d2, jitter_sigma, n_samples=10000):
    """
    Kombiniert den geometrischen Verlust aus dem Paper mit stochastischem Jitter.
    
    Parameter:
    L            : Distanz in Metern 
    theta        : Divergenz in Milliradiant 
    d1           : Durchmesser Sender (m) 
    d2           : Durchmesser Empfänger (m) 
    jitter_sigma : Standardabweichung des Wackelns am Empfänger (m)
    n_samples    : Anzahl der simulierten Zeitpunkte
    """
    
    # --- Teil A: Deterministischer Geometric Loss (nach Paper Sutrisno) ---
    
    # Strahlbreite am Empfänger (Nenner der Formel)
    # Formel: (d1 + L*theta)^2 
    beam_width = d1 + (L * theta)
    
    # GL_static ist das Verhältnis der Flächen (d2^2 / beam_width^2)
    # Dies ist die maximale Leistung, die wir bei perfekter Ausrichtung kriegen.
    GL_static = (d2**2) / (beam_width**2)
    
    # Clip auf 1.0, falls Empfänger größer als Strahl ist (unwahrscheinlich bei FSO)
    if GL_static > 1.0: GL_static = 1.0

    # --- Teil B: Stochastische Pointing Errors (Zusatz) ---
    
    # Wir simulieren das Wackeln des Strahls (Rayleigh-Verteilt)
    # r ist der radiale Abstand vom Zentrum des Empfängers
    r = np.random.rayleigh(scale=jitter_sigma, size=n_samples)
    
    # Um den Verlust durch Jitter zu berechnen, brauchen wir ein Strahlprofil.
    # Auch wenn das Paper einfach rechnet, ist die Annahme eines Gaußschen Abfalls
    # für den Jitter-Verlust am realistischsten.
    
    # Wir schätzen den äquivalenten Strahlradius w_eq ab:
    w_L = beam_width / 2.0 # Radius des Strahls am Ziel
    
    # Berechnung des Dämpfungsfaktors durch Verschiebung r
    # Formel angelehnt an Farid & Hranilovic (vereinfacht für Simulation)
    # h_p variiert zwischen 0 und 1
    pointing_loss_factor = np.exp(-2 * (r**2) / (w_L**2))
    
    # --- Gesamter Kanal-Koeffizient ---
    # Das ist der Anteil der Sendeleistung, der tatsächlich ankommt
    h_total = GL_static * pointing_loss_factor
    
    return h_total

def calculate_atmospheric_loss(L_km, visibility_km, wavelength_nm):
    """
    Berechnet den atmosphärischen Verlust nach dem Kim-Modell
    
    :param L_km: Abstand (km)
    :param visibility_km: Sichtweite (km)
    :param wavelength_nm : Wellenlänge des Lasers (nm)
    
    Returns:
    h_atm : float Transmissionsfaktor (linear, 0 bis 1)
    loss_dB : Dämpfung (dB, positiv)
    """
    # 1. Bestimmung des q-Faktors nach Kim-Modell
    if visibility_km > 50:
        q = 1.6
    elif visibility_km > 6:
        q = 1.3
    else:
        # Dies ist der kritische Bereich für Nebel
        q = 0.585 * (visibility_km**(1/3))   

    # 2. Berechnung des Dämpfungskoeffizienten sigma (in 1/km)
    # 3.91 entspricht -ln(0.02), basierend auf 2% Kontrastschwelle für Sichtweite
    sigma = (3.91 / visibility_km) * ((wavelength_nm / 550.0)**(-q))
    
    # 3. Berechnung der Transmission nach Beer-Lambert
    h_atm = np.exp(-sigma * L_km)
    
    # 4. Umrechnung in dB
    loss_dB = -10 * np.log10(h_atm)
    
    return h_atm, loss_dB

def calculate_scintillation_params(Cn2, L_m, wavelength_m):
    """
    Berechnet Alpha und Beta für das Gamma-Gamma Modell basierend auf
    der Rytov-Varianz (für eine ebene Welle / Plane Wave Approximation).
    
    Parameter:
    Cn2 : float - Refractive Index Structure Parameter (z.B. 1e-14)
    L_m : float - Distanz (m)
    wavelength_m : float - Wellenlänge (m)
    """
    k = 2 * np.pi / wavelength_m
    
    # Rytov Varianz (Maß für Turbulenzstärke)
    sigma_R2 = 1.23 * Cn2 * (k**(7/6)) * (L_m**(11/6))
    
    # Berechnung von Alpha (Large-Scale Scattering)
    term_alpha = (0.49 * sigma_R2) / ((1 + 1.11 * sigma_R2**(12/5))**(7/6))
    alpha = 1 / (np.exp(term_alpha) - 1)
    
    # Berechnung von Beta (Small-Scale Scattering)
    term_beta = (0.51 * sigma_R2) / ((1 + 0.69 * sigma_R2**(12/5))**(5/6))
    beta = 1 / (np.exp(term_beta) - 1)
    
    return alpha, beta, sigma_R2

def simulate_gamma_gamma_fading(alpha, beta, n_samples=10000):
    """
    Erzeugt Zufallszahlen nach der Gamma-Gamma Verteilung.
    """
    # Wir ziehen zwei unabhängige Gamma-Verteilungen
    # scale = 1/alpha, damit der Mittelwert 1 bleibt
    I_x = np.random.gamma(shape=alpha, scale=1/alpha, size=n_samples)
    I_y = np.random.gamma(shape=beta, scale=1/beta, size=n_samples)
    
    # Das resultierende Fading ist das Produkt
    I_total = I_x * I_y
    return I_total

def calculate_noise_power(
    fov_mrad, 
    aperture_diameter_cm, 
    optical_filter_width_nm, 
    electrical_bandwidth_Hz,
    sky_condition='cloudy'
):
    """
    Berechnet die Rausch-Varianz (Sigma^2) basierend auf Hintergrundlicht und Elektronik.
    
    Parameter:
    fov_mrad : Field of View des Empfängers (Milliradiant)
    aperture_diameter_cm : Linsendurchmesser
    optical_filter_width_nm : Breite des optischen Bandpassfilters (z.B. 10nm)
    electrical_bandwidth_Hz : Bandbreite der Datenübertragung (z.B. 1e9 für 1Gbps)
    sky_condition : 'sunny', 'cloudy', 'night'
    """
    
    # --- Konstanten ---
    q = 1.602e-19       # Elementarladung (C)
    kB = 1.38e-23       # Boltzmann (J/K)
    T = 300             # Temperatur (K)
    R_resp = 0.9        # Responsivity der Photodiode (A/W) bei 1550nm
    R_load = 50         # Widerstand (Ohm)
    
    # --- 1. Hintergrund-Strahlung (Spectral Radiance) ---
    # Werte in W / (m^2 * sr * nm)
    if sky_condition == 'direct_sun':
        L_sky = 100.0   # Extreme Einstrahlung (Sonne im FOV) - sehr hoch!
    elif sky_condition == 'sunny_sky':
        L_sky = 0.05    # Heller Taghimmel (indirekt)
    elif sky_condition == 'cloudy':
        L_sky = 0.01    # Bewölkt / Dämmerung
    elif sky_condition == 'night':
        L_sky = 1e-6    # Nacht (Sternenlicht/Mond)
    else:
        L_sky = 0.01

    # --- 2. Geometrie ---
    # Aperturfläche A_rx (m^2)
    radius_m = (aperture_diameter_cm / 100) / 2
    A_rx = np.pi * radius_m**2
    
    # Raumwinkel Omega (sr)
    theta_rad = fov_mrad / 1000.0
    Omega = np.pi * (theta_rad / 2)**2
    
    # --- 3. Hintergrundleistung P_bg ---
    # P = L_sky * A_rx * Omega * Delta_Lambda
    P_bg = L_sky * A_rx * Omega * optical_filter_width_nm
    
    # --- 4. Rausch-Varianzen (Ströme in A^2) ---
    
    # DC-Strom durch Hintergrund
    I_bg = R_resp * P_bg
    
    # A) Shot Noise Variance (sigma^2)
    # 2 * q * I * B
    sigma_sq_shot = 2 * q * I_bg * electrical_bandwidth_Hz
    
    # B) Thermal Noise Variance (sigma^2)
    # 4 * k * T * B / R
    sigma_sq_thermal = (4 * kB * T * electrical_bandwidth_Hz) / R_load
    
    # Gesamtrauschen
    sigma_sq_total = sigma_sq_shot + sigma_sq_thermal
    
    return sigma_sq_total, sigma_sq_shot, sigma_sq_thermal, I_bg

# Beispielwerte
loss_factors, max_fraction = calculate_geometric_and_pointing_loss(
    L=1000,          # 1 km
    theta=1e-3,      # 1 rad Divergenz
    a=0.1,           # 10 cm Radius Linse
    jitter_sigma=0.2 # 20 cm Wackeln (sehr viel, nur als Beispiel)
)

loss_factors_paper = calculate_geometric_and_pointing_loss_paper(
    L=1000,          # 1 km
    theta=1e-3,      # 1 rad Divergenz
    d1=0.1,          # 10 cm Senderdurchmesser
    d2=0.1,          # 10 cm Empfängerdurchmesser
    jitter_sigma=0.2,# 20 cm Wackeln
)

print(f"Mittlerer Dämpfungsfaktor:                     {np.mean(loss_factors):.6f}")
print(f"Mittlerer Dämpfungsfaktor (Paper + Jitter):    {np.mean(loss_factors_paper):.6f}")

print("\nFarid & Hranilovic Modell (mit Jitter) - Beispielverteilung der Dämpfungsfaktoren:")

# --- Beispielrechnung ---
# Parameter (Beispielwerte anpassen!)
distanz = 1000.0        # 1 km
divergenz_mrad = 2.0    # 2 mrad Vollwinkel
apertur_durchm = 0.20   # 20 cm Linse

# Umrechnung
theta_val = (divergenz_mrad / 1000) / 2  # Halber Winkel in rad
apertur_radius = apertur_durchm / 2

# Jitter-Szenarien (wenig Wind vs. viel Wind/Gebäudeschwanken)
jitter_low = 0.05  # 5 cm
jitter_high = 0.30 # 30 cm

loss_low, A0_val = calculate_geometric_and_pointing_loss(distanz, theta_val, apertur_radius, jitter_low)
loss_high, _     = calculate_geometric_and_pointing_loss(distanz, theta_val, apertur_radius, jitter_high)

# Ausgabe der Ergebnisse
print(f"Maximal möglicher Empfang (Geometric Loss A0): {A0_val:.6f} ({-10*np.log10(A0_val):.2f} dB Verlust)")
print(f"Durchschnittlicher Verlust mit wenig Jitter:   {np.mean(loss_low):.6f} ({-10*np.log10(np.mean(loss_low)):.2f} dB Verlust)")
print(f"Durchschnittlicher Verlust mit viel Jitter:    {np.mean(loss_high):.6f} ({-10*np.log10(np.mean(loss_high)):.2f} dB Verlust)")

# Visualisierung
plt.figure(figsize=(10, 5))
plt.hist(10*np.log10(loss_low), bins=50, alpha=0.7, label='Wenig Jitter (5cm)')
plt.hist(10*np.log10(loss_high), bins=50, alpha=0.7, label='Viel Jitter (30cm)')
plt.xlabel('Verlust (dB)')
plt.ylabel('Häufigkeit')
plt.title('Verteilung der Dämpfung durch Geometric Loss & Pointing Errors')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()


# --- Beispielrechnung & Visualisierung ---

# Parameter
distanz = 1.0        # 1 km Link
wavelength = 1550.0  # 1550 nm Laser

# Wir simulieren verschiedene Wetterbedingungen von dichtem Nebel bis klarer Sicht
visibilities = np.logspace(np.log10(0.1), np.log10(50), 100) # 100m bis 50km
losses_dB = []

for v in visibilities:
    _, dB = calculate_atmospheric_loss(distanz, v, wavelength)
    losses_dB.append(dB)

# Plot
plt.figure(figsize=(10, 6))
plt.loglog(visibilities, losses_dB, linewidth=2, color='darkorange')
plt.grid(True, which="both", ls="-", alpha=0.4)

# Zonen markieren
plt.axvline(x=0.5, color='gray', linestyle='--')
plt.text(0.15, 1, 'Dichter Nebel', color='gray')
plt.text(1.0, 1, 'Dunst / Leichter Nebel', color='gray')
plt.text(20, 1, 'Klare Sicht', color='gray')

plt.xlabel('Sichtweite (km)')
plt.ylabel(f'Atmosphärische Dämpfung (dB) bei {distanz} km')
plt.title(f'Atmospheric Loss (Kim Model) @ {wavelength}nm')
plt.gca().invert_yaxis() # Optional: Umgekehrt, damit Verlust nach unten geht (oder normal lassen)
# Hier lassen wir es normal: Hoher Wert = Hoher Verlust
plt.gca().invert_yaxis() # Achse invertieren ist bei Dämpfung oft verwirrend, ich nehme es zurück:
plt.gca().invert_yaxis() # Reset visual
plt.close() # Reset für sauberen Plot unten

# Neuer sauberer Plot ohne Invertierung für Klarheit
plt.figure(figsize=(10, 6))
plt.loglog(visibilities, losses_dB, linewidth=2, color='firebrick')
plt.grid(True, which="both", ls="-", alpha=0.4)
plt.axvline(x=0.5, color='gray', linestyle='--')
plt.xlabel('Sichtweite V (km)')
plt.ylabel('Dämpfung (dB)')
plt.title(f'Atmospheric Loss vs. Sichtweite (Distanz={distanz}km, $\lambda$={wavelength}nm)')
plt.show()

# Ein paar konkrete Werte ausgeben
print("--- Beispiele ---")
for v in [0.2, 0.5, 2.0, 10.0]:
    h, dB = calculate_atmospheric_loss(distanz, v, wavelength)
    print(f"Sichtweite {v:4.1f} km -> Dämpfung: {dB:6.2f} dB (Transmission: {h*100:.2f}%)")


    # --- Beispielrechnung ---
distanz = 1000.0       # 1 km
welle = 1550e-9        # 1550 nm

# Drei typische Szenarien
scenarios = {
    "Schwach (Morgen)": 5e-16,
    "Moderat (Bewölkt)": 5e-15,
    "Stark (Mittagssonne)": 5e-14
}

plt.figure(figsize=(10, 6))

for name, cn2 in scenarios.items():
    # 1. Parameter berechnen
    a, b, sig = calculate_scintillation_params(cn2, distanz, welle)
    
    # 2. Simulation durchführen
    fading_samples = simulate_gamma_gamma_fading(a, b, n_samples=50000)
    
    # 3. Plotten
    # Wir schneiden sehr hohe Werte für die Übersichtlichkeit ab
    fading_samples = fading_samples[fading_samples < 5] 
    
    plt.hist(fading_samples, bins=100, density=True, alpha=0.5, label=f'{name}\n$C_n^2$={cn2:.0e}, $\\alpha$={a:.1f}, $\\beta$={b:.1f}')

plt.title(f"Intensitäts-Verteilung durch Szintillation (Gamma-Gamma)\nDistanz: {distanz}m")
plt.xlabel("Normalisierte Intensität I (1 = Durchschnitt)")
plt.ylabel("Wahrscheinlichkeit")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()