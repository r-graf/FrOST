# ToDo

## GUI

Hier läuft bis jetzt die Modenauswahl.
Jetzt noch Modell schreiben, welches die richtigen Werte berechnet um dann ein tf erstellt, der dann als "x-Achse" in die Simlulation geladen werden kann.

### Abfrage der Werte in den Moden

#### Berechnung über Eb/N0

Keine weiteren Werte müssen abgefragt werden. Die Werte können direkt genommen werden, um die Simulation zu starten.

Return:
- 'mode': 'ebn0'
- 'ebn0_min': 0.0
- 'ebn0_max': 12.0
- 'steps': 5

#### Berechung über Leistung

Ziel ist es, hier ein Eb/N0 mit den korresponierenden Sendeleistungen zu erhalten. Alle Leistgung werden in \[W\] umgerechnet. In die Funktion kann die Start- und Enddistanz eingegeben werden.

Return:
- 'mode': 'power'
- 'p_tx': 10.0
- 'min_dist': 1.0
- 'max_dist': 100.0
- 'steps': 5

#### Berechung über Distanz

Hier soll die Distanz verändert werden. In die erste Funktion kann ebenfalls die Länge eingegeben werden.

Return:
- 'mode': 'distance'
- 'distance': 36000.0
- 'start_power': 10.0
- 'end_power': 100.0
- 'steps': 5

## Modell

### to Do
Verifikation via Literatur

### Done
Skript in core/fso_channel.py schreiben

## Aufräumen

doc/graphics/Block-Diagram-DSP-Chain.svg
src/core/osc_sim.py
src/gui/components.py
toDo.md

## GIT
Umbenennen in "FROST"

# Struktur der Parameter Abfrage in der GUI

## Abfrage der Modi
- Fixe Distanz
- Fixe Leistung
- Über eine definierte Range von normierter Leistung (Eb/N0)

## 1. Schritt: Abfrage der Parameter des optischen Kommunikationsterminals (OCT)
Allgemeine Parameter Laser

[NEU] Mögliche Stahlungsleistung
Eingabe der allgemeinen Parameter
Divergenzwinkel
Radius am Empfangsaperatur
Durchmesser Sender
Durchmesser Empfänger
Wellenlänge
Bandbreite des optischen Bandpassfilter
Elektrische Bandbreite der Datenübertragung
Jitter optische Bodenstation (OGS) oder Platform
Sichtfeld (FOV) für das Hintergrundstrahlen auf den Empfänger

## 2. Schritt

Allgemeine Parameter Kanal
Wetterbedingungen
- Visibility
- Sky condition (clear, cloudy, night, ...)
Cn2
Mögliche Distanz, als einzelnen Punkt oder als Range

## 3. Simulationsparameter
Simulationsauflösung in der Berechung des Eb/N0
Anzahl der Stichproben (Samples) der Montecarlosimulation in der Berechung der geometrischen Verluste

# Abruf der Simulation nach Modi Selektion

Erzeugen des Tensors, welcher als Basis für die Berechung der BER im FSO Channel Skript verwendet werden soll.
Dieser soll wie eine Tabelle aufgebaut werden.
Für die jeweiligen Einträge über die Parameterabfrage sollen korrenspodierende Werte berechnet werden.
Ein Entwurf für die Instanziierung wird unterhalb wie folgt definiert:

'Simulation_Range'
|Name|Notiz|
|-|-|
| EbN0 | Eingangsparameter für FSO Channel Skript |
| power | Sendeleistung des Lasers |
| disntance | Link Distanz |

## Berechung nach Eb/N0

Argumente:
- min. Eb/N0 [dB]
- max. Eb/N0 [dB]
- Simulationsauflösung [1]
- Simluation Range [tf]
Return:
- Tensorflow Array -> Update von Simluation Range [tf]

### Funktion
Die X-Achse wird wie folgt definiert.
Nur das Eb/N0 spielt eine Rolle.
Keine Abfrage weiterer Parameter ist 

## Berechung über die Leistung
Argumente:
- Sendeleistung [W]
- min. Distanz [km]
- max. Distanz [km]
- Simulationsauflösung [1]
- Simluation Range [tf]
Return:
- Tensorflow Array -> Update von Simluation Range [tf]

## Berechnung über Distanz
Argumente:
