# Timetable Solver Wiki

## Legende
Lehrer = Lehrpersonal
Lehrveranstaltung = LV = Vorlesung, Praktikum, Übung, etc.
Lehreinheit = Ein konkreter Lehrveranstaltungstermin
Raum = Hörsaal, Seminarraum, Labor, etc.
Kohorte = Gruppe von Studierenden desselben Studiengangs und Fachsemesters

## Funktionale Anforderungen

Erstellung von Pro- Semester Stundenplänen. Dafür werden Lehrveranstaltungen Räume zugewiesen, wobei Einschränkungen beachtet werden.

### Vom System zu unterstützen

#### Lehrer
- Lehrer halten gleichzeitig eine Lehreinheit/Lehrveranstaltung(Beispiel: 1 Professor und 1 Wissenschaftlicher Mitarbeiter führen mit den Studenten ein Praktikum durch)
- Lehrer haben Regelmäßige Zeiträume in denen Sie verfügbar sind
- Lehrer haben Unregelmäßige Zeiträume in denen Sie nicht verfügbar sind (einzelne Termine)
- Lehrer haben Bevorzugte Zeiträume in denen Sie verfügbar sind
- Lehrer haben eine maximale Anzahl an Lehrstunden pro Tag
- Lehrer haben eine maximale Belastungsgrenze (z.B. nicht mehr als 3 Blöcke unmittelbar am Stück unterrichten, um Pausen zu garantieren)

#### Lehrveranstaltungen
- Lehrveranstaltungen haben einen spezifischen Typ (Vorlesung, Seminar, Übung, Praktikum) zur logischen Gruppierung
- Lehrveranstaltungen kann eine Liste an möglichen Austragunsräumen gegeben werden
- Lehrveranstaltungen kann eine Liste an bevorzugten Austragungsräumen gegeben werden
- Lehrveranstaltungen kann eine Liste an nicht möglichen Austragungsräumen gegeben werden
- Online Veranstaltung (Keine zuordnung der Räume, aber Lehrer an Online-LV gebunden)
- Lehrveranstaltungen sind fest an spezifische Studiengänge und Fachsemester gebunden (Kohorten-Zuordnung für Pflichtmodule)
- Lehrveranstaltungen sind für einen Studiengang Pflicht und für einen anderen Wahl

#### Räume
- Räume haben spezifische Typen (z.B. Hörsaal, Chemielabor, PC-Pool), die von der LV gefordert werden können
- Räume haben Regelmäßige Zeiträume in denen Sie verfügbar sind
- Räume sind geografisch hierarchisch aufgeteilt (Campus -> Gebäude -> Raum)
- Entfernung zwischen Räumen kann berechnet/geschätzt werden, wenn informationen eingetragen, basierend darauf, auf welchem Campus ein Raum liegt

### Features

#### An und Auschaltbare Constraints. Falls Daten nicht existieren, kann ein Constraint ausgeschaltet werden.
#### Einige Constraints können zwischen Hard und soft wechseln. Falls keine Lösung gefunden wird, kann ein Constraint auf Soft gewechselt werden.
- **(aktivierbarer Hard/Soft Constraint 10)**: Prüfung der Raumausstattung gegen Anforderungen (Z.B. Lautsprecheranlage vorhanden, oder Rollstuhlgerecht).
- **(aktivierbarer Hard/Soft Constraint 11)**: Prüfung, dass Raum genug Sitztplätze hat
- **(aktivierbarer Soft Constraint 20)**: Vermeidung von Hohlstunden: Minimierung der freien Zeit zwischen den Vorlesungen, damit Studenten so wenig Zeit wie möglich auf die nächste Vorlesung warten müssen. Optional einstellbar, dass Vorlesungen mit hoher Hörerzahl stärker gewichtet werden.
- **(aktivierbarer Soft Constraint 30)**: Vermeidung von Tagesrandzeiten: Lehrveranstaltungen sollen möglichst nicht früh, oder spät beginnen. Optional einstellbar, dass Vorlesungen mit hoher Hörerzahl stärker gewichtet werden.
- **(aktivierbarer Soft Constraint 40)**: Konstanter LV Austragungsraum: Lehrveranstaltungen sollten an ihren Regelmäßigen Terminen möglichst den selben Raum nutzen.
- **(aktivierbarer Soft Constraint 50)**: Vermeidung der Überlappung von Pflicht-LV eines Studiengangs unterschiedlicher Fachsemester. Für Studenten, die eine Pflicht-LV wiederholen müssen.
- **(aktivierbarer Soft Constraint 60)**: Vermeidung der Überlappung von Wahl-LVen deren potenzielle Hörer eine Schnittmenge Bilden. Minimierung der Gesamtschnittmenge.
- **(aktivierbarer Soft Constraint 70)**: Beachten der Bevorzugten Zeiträume der Lehrer. Maximieren der zuordung in bevorzugte Zeiträume.
- **(aktivierbarer Hard/Soft Constraint 80)**: Beachten der Maximalen Lehrzeit von Lehrern
- **(aktivierbarer Hard Constraint 90)**: Beachten der Wegzeiten zwischen Räumen

## Solver Constraints

Die Solver Constraints, die für jede Lehreinheit erfüllt sein müssen/sollten.

### Must
- Alle Lehrer einer LV sind Zeitlich verfügbar
- Alle Lehrer einer LV haben gleichzeitig keine andere LV
- Ein Raum hat gleichzeitig maximal eine LV
- Pflicht-LV darf mit keiner anderen Pflicht-LV des selben Studiengangs des selben Fachsemesters überschneiden (Kohorten-Schutz)
- Wahl-LV ist in mindestens einem Fachsemester von keiner Pflicht-LV blockiert
- Raum ist Zeitlich verfügbar
- Raum hat den Richtigen Typ
- **(aktivierbarer Hard Constraint 90)** Wegzeiten zwischen den Vorlesungen sind zumutbar

### Should
- Minimale überschneidung von Wahl-LV mit Pflicht-LV eines Studiengangs Optional: Studiengangsgröße als Gewicht.
- **(aktivierbarer Soft Constraint 20)** Minimale Hohlstunden zwischen Lehrveranstaltungen für Kohorten
- **(aktivierbarer Soft Constraint 30)** Minimale Randzeiten der Lehrveranstaltungen
- **(aktivierbarer Soft Constraint 40)** Minimale Änderung der Autragungsorte innerhalb einer LV
- **(aktivierbarer Soft Constraint 50)** Minimale Überlappung von Pflicht-LV eines Studiengangs unterschiedlicher Fachsemester
- **(aktivierbarer Soft Constraint 60)** Minimale Überschneidung von Wahl-LV mit selber Zuhörerschaft
- **(aktivierbarer Soft Constraint 70)** Maximale Zuweisung der LV in bevorzugte Zeitbereiche der verknüpften Lehrer

### Switchable
- **(aktivierbarer Hard/Soft Constraint 10)** Raumausstattung erfüllt die Anforderungen der LV
- **(aktivierbarer Hard/Soft Constraint 11)** Raum hat genug Sitzplätze
- **(aktivierbarer Hard/Soft Constraint 80)** Maximale Anzahl an Lehrstunden pro Tag nicht überschritten