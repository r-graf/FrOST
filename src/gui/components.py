import numpy as np
from scipy.special import erf
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
    
    return h_p # Array von Dämpfungsfaktoren (0 bis A0)

# Berechnung von Geometric Loss + Pointing Errors für FSO-Kommunikation

def simulate_paper_loss_with_jitter(L, theta, d1, d2, jitter_sigma, n_samples=10000):
    """
    Kombiniert den geometrischen Verlust aus dem Paper mit stochastischem Jitter.
    
    Parameter:
    L            : Distanz in Metern 
    theta   : Divergenz in Milliradiant 
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

# Beispielwerte
loss_factors = calculate_geometric_and_pointing_loss(
    L=1000,          # 1 km
    theta=1e-3,      # 1 mrad Divergenz
    a=0.1,           # 10 cm Radius Linse
    jitter_sigma=0.2 # 20 cm Wackeln (sehr viel, nur als Beispiel)
)

loss_factors_paper = simulate_paper_loss_with_jitter(
    L=1000,          # 1 km
    theta=1e-3,      # 1 rad Divergenz
    d1=0.1,          # 10 cm Senderdurchmesser
    d2=0.1,          # 10 cm Empfängerdurchmesser
    jitter_sigma=0.2,# 20 cm Wackeln
)

print(f"Mittlerer Dämpfungsfaktor:                     {np.mean(loss_factors):.6f}")
print(f"Mittlerer Dämpfungsfaktor (Paper + Jitter):    {np.mean(loss_factors_paper):.6f}")

print("\nFarid & Hranilovic Modell (mit Jitter) - Beispielverteilung der Dämpfungsfaktoren:")


# A. Simulation von Geometric Loss + Pointing Errors für FSO-Kommunikation

def simulate_gaussian_beam_loss(L, theta, a, jitter_sigma, n_samples=10000):
    """
    Simuliert den Verlust durch Geometric Loss + Pointing Errors
    Basierend auf dem Farid & Hranilovic Modell (wie in Zedini et al., arXiv:1702.04098).
    
    Parameter:
    ----------
    L : float
        Distanz (Link distance) in Metern.
    theta : float
        Divergenzwinkel (halber Winkel!) in Radiant (oft wird Vollwinkel angegeben, dann /2).
        Beispiel: 2 mrad Vollwinkel -> theta = 0.001 rad.
    a : float
        Radius der Empfänger-Apertur (Aperture radius) in Metern.
    jitter_sigma : float
        Standardabweichung des Jitters (Pointing Error displacement std. dev) in Metern.
    n_samples : int
        Anzahl der Simulationsschritte.
        
    Returns:
    --------
    h_p : array
        Array mit den Dämpfungsfaktoren (0 bis A0) für jeden Zeitschritt.
    """
    
    # 1. Strahlradius am Empfänger (Beam waist at distance L)
    # w_L entspricht w_z im Paper
    w_L = theta * L 
    
    # 2. Geometrischer Verlust A0 (Fraction of collected power at r=0)
    # v entspricht nu im Paper
    v = (np.sqrt(np.pi) * a) / (np.sqrt(2) * w_L)
    A0 = erf(v)**2
    
    # 3. Äquivalente Strahlbreite w_eq (Equivalent beam width)
    # Wichtig für die korrekte Kopplung von Jitter und Strahlbreite
    w_eq_sq = (w_L**2 * np.sqrt(np.pi) * erf(v)) / (2 * v * np.exp(-v**2))
    
    # 4. Simulation der Verschiebung r (Radial displacement)
    # Der radiale Fehler r folgt einer Rayleigh-Verteilung, wenn x/y Gauß-verteilt sind.
    # scale entspricht der Jitter-Standardabweichung sigma_s
    r = np.random.rayleigh(scale=jitter_sigma, size=n_samples)
    
    # 5. Berechnung des momentanen Verlusts h_p
    # Formel: h_p(r) = A0 * exp(-2 * r^2 / w_eq^2)
    h_p = A0 * np.exp(-2 * r**2 / w_eq_sq)
    
    return h_p, A0

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

loss_low, A0_val = simulate_gaussian_beam_loss(distanz, theta_val, apertur_radius, jitter_low)
loss_high, _     = simulate_gaussian_beam_loss(distanz, theta_val, apertur_radius, jitter_high)

# Ausgabe der Ergebnisse
print(f"Maximal möglicher Empfang (Geometric Loss A0): {A0_val:.6f} ({-10*np.log10(A0_val):.2f} dB Verlust)")
print(f"Durchschnittlicher Verlust mit wenig Jitter:   {np.mean(loss_low):.6f} ({-10*np.log10(np.mean(loss_low)):.2f} dB Verlust)")
print(f"Durchschnittlicher Verlust mit viel Jitter:    {np.mean(loss_high):.6f} {-10*np.log10(np.mean(loss_high)):.2f} dB Verlust)")

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