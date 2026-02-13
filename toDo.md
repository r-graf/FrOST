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

Skript in core/fso_channel.py schreiben.
Modell gibt es schon in gui/components.py

## Aufräumen

doc/graphics/Block-Diagram-DSP-Chain.svg
src/core/osc_sim.py
src/gui/components.py
toDo.md