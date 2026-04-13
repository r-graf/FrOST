# Hier später noch das Skript einfügen, dass dann die Berechnung startet. Das muss ich aber noch schreiben

def mode_ebn0(data: dict):
    """
    Berechnet die Bitfehlerrate (BER) basierend auf dem Signal-Rausch-Verhältnis (Eb/N0).
    
    Args:
    
    Returns:
    """
    import numpy as np
    
    # Extrahiere Eb/N0 in dB
    ebn0_min = data.get("ebn0_min")
    ebn0_max = data.get("ebn0_max")
    ebn0_step = data.get("steps")

    # Debug Output, x-Achse der Simulation
    print("Start Eb/N0: ", ebn0_min, "dB bis", ebn0_max, "dB in", ebn0_step, "Schritten")
    return {}