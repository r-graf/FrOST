# Free Space Optical Simulation Tool (FrOST) 

**Version:** 0.2.0  
**Status:** Development (alpha)  
**Autor:** Robin Graf  
**Lizenz:** --  
**Letztes Update:** Mai 2026  

*(ehemals: optical-satcom-sim)*

---
## Block Diagram

![Block Diagramm](./doc/graphics/Block-Diagram-DSP-Chain.png)
---

## Überblick

**FrOST** ist ein modulares Simulationstool zur Untersuchung und Bewertung digitaler Signalverarbeitungsketten (DSP Chains) für **freie optische Kommunikation (FSO)** und **optische Satellitenlinks**.  
Der Fokus liegt auf Wiederverwendbarkeit, Erweiterbarkeit und wissenschaftlicher Nachvollziehbarkeit.
Das Tool schlägt eine Brücke zwischen der physikalischen optischen Übertragung (Link-Budget, Atmosphärendämpfung) und der nachrichtentechnischen Signalauswertung auf dem Physical Layer.
Die Leistungsbewertung erfolgt über die **Bit Error Rate (BER)** als Funktion von **Eb/N₀** sowie der resultierenden **Sendeleistung ($P_{tx}$)**.
---

## Motivation

- Erforschung von *FSO*- und *optischen Satcom-Systemen*  
- Vergleich von *Reed–Solomon*, *LDPC*, *Turbo*- und zukünftigen Codes  
- Simulation typischer *Atmosphäreneffekte* (Turbulenz, Pointing, Extinktion)  
- Experimentelle *DSP-Algorithmen* in TensorFlow für spätere GPU-Integration  

---

## Technologie-Stack

| Bereich | Tools |
|----------|--------|
| Programmiersprache | Python ≥ 3.12 |
| Simulation | TensorFlow, NVIDIA Sionna |
| Optischer Kanal | NumPy, SciPy (fso_channel.py) |
| Visualisierung | Matplotlib |
| Konfiguration | PyYAML |
| Versionierung | Git + GitHub |

---

## Projektstruktur

```text
frost/
├── src/
│   ├── osc_sim.py      # Hauptskript zum Starten der Simulation
│   ├── osc_def.py      # Definition der DSP-Chain und Plot-Logik
│   ├── fso_channel.py  # Physikalische Kanalmodelle (Turbulenz, Extinktion)
│   └── config.yaml     # Parameter für Link-Budget und Empfänger
├── doc/
│   └── graphics/       # Abbildungen (Blockdiagramme etc.)
├── README.md
└── requirements.txt
```
---

## Quickstart & Usage

Alle physikalischen Parameter (Distanz, Sichtweite, Wellenlänge, Apertur) werden zentral in der config.yaml definiert:
YAML

### Auszug aus config.yaml
```yaml
link_params:
  L_km: 2.0
  visibility_km: 4.0
  wavelength_nm: 1550.0
  theta_mrad: 1.5
```

Die Simulation wird über das Terminal gestartet. Das Skript lädt automatisch die Parameter, generiert den Bitstream, lässt ihn durch den AWGN/FSO-Kanal laufen und plottet die Performance der Codes:
```Bash

# Virtuelle Umgebung aktivieren
source .venv/bin/activate

# Simulation starten
python src/osc_sim.py
```