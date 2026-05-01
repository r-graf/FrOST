import numpy as np
from scipy.special import erf
from scipy.special import gamma as gamma_func
from scipy.special import kv
import matplotlib.pyplot as plt

# A.1 Berechnung des Geometric Loss und Pointing Errors für FSO-Kommunikation

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

# A.2 Kontrolle mit Vereinfachung im Paper

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

# B.1 Berechnung von atmosphärischem Verlust

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

# C Berechnung von Scintillationseffekten auch Atmospheric Turbulence Induced Fading gennant(Gamma-Gamma Modell)

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

# C.1 Simulation von Gamma-Gamma Fading

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

# D. Berechnung von Rauschleistung basierend auf Hintergrundlicht und Elektronik

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