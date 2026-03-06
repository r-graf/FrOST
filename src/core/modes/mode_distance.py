from core.fso_channel import calculate_geometric_and_pointing_loss

# Hier später noch das Skript einfügen, dass dann die Berechnung startet. Das muss ich aber noch schreiben

def mode_distance(data: dict):
    """
    Berechnet die Bitfehlerrate (BER) basierend auf einer festen Distanz und variabler Leistung.
    
    Args:
    
    Returns:
    """
    import numpy as np
    
    # Extrahiere Argumente für Geometrische- und Ausrichtungsverluste 
    distance_km = data.get("distance_km")
    start_power_W = data.get("start_power_W")
    end_power_W = data.get("end_power_W")
    steps = data.get("steps")

    theta = data.get("theta_")
    a = data.get("bckgrnd_aperture_diameter_cm")
    jitter_sigma = data.get("jitter_sigma")

    
    geo_point_loss = calculate_geometric_and_pointing_loss(distance_km, theta, a, jitter_sigma, n_samples=10000 )

    # Debug Output, x-Achse der Simulation
    print("Geo- and Pointing losses: ", geo_point_loss)
    return {}