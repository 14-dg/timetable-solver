from typing import Any

import pandas as pd
from ortools.sat.python import cp_model

from mock_data.generate import MockGenerator

# Importiere hier deine Dataclasses und den MockGenerator
# from models.lecture import Lecture
# from models.room import Room
# from models.teacher import Teacher
# from mock_generator import MockGenerator

def solve_university_schedule():
    # 1. Daten generieren
    generator = MockGenerator()
    mock_teachers, mock_rooms, mock_lectures = generator.generate_mock_data()

    print(f"Generiert: {len(mock_lectures)} Vorlesungen, {len(mock_teachers)} Dozenten, {len(mock_rooms)} Räume\n")

    # ==========================================
    # PHASE 1: PANDAS DATEN-PIPELINE (Sparsity erzeugen)
    # ==========================================

    # A) Dozenten DataFrame aufbauen (inkl. Präferenzen)
    teacher_rows: list[dict[str, Any]] = []
    for t in mock_teachers:
        available_list = list(t.available) # Set in Liste wandeln für sichere Iteration
        for idx, interval in enumerate(available_list):
            teacher_rows.append({
                "teacher_id": t.id,
                "teacher_name": t.name,
                "interval": interval,
                "is_preferred": 1 if idx in t.preffered else 0 # Präferenz als 0 oder 1 speichern
            })
    df_teachers = pd.DataFrame(teacher_rows)

    # B) Räume DataFrame aufbauen (Explode)
    room_rows: list[dict[str, Any]] = [{"room_id": r.id, "seats": r.seats, "interval": i} for r in mock_rooms for i in r.available]
    df_rooms = pd.DataFrame(room_rows)

    # C) Vorlesungen DataFrame
    df_lectures = pd.DataFrame([vars(l) for l in mock_lectures])
    df_lectures = df_lectures.rename(columns={"id": "lecture_id", "name": "lecture_name"})

    # D) JOINS & FILTER (Die Magie)
    
    # Inner Join auf 'interval': Behält NUR Zeiten, wo Dozent UND Raum gleichzeitig verfügbar sind!
    df_slots = pd.merge(df_teachers, df_rooms, on="interval", how="inner")
    
    # Cross Join: Jeder machbare Slot mit jeder Vorlesung kombinieren
    df = pd.merge(df_lectures, df_slots, how="cross")
    
    # Hard Filter: Die Vorlesung muss zwingend in den Raum passen
    df = df[df["visitors"] <= df["seats"]].reset_index(drop=True)

    print(f"Suchraum optimiert auf {len(df)} physikalisch mögliche Kombinationen.\n")

    # ==========================================
    # PHASE 2: OR-TOOLS MODELLIERUNG
    # ==========================================

    model = cp_model.CpModel()
    
    # Für jede verbliebene, gültige Kombination eine BoolVar erstellen
    x = model.new_bool_var_series(name="x", index=df.index)

    # --- Harte Bedingungen (Hard Constraints) ---

    # 1. Jede Vorlesung MUSS exakt einmal stattfinden
    for _, group in df.groupby("lecture_id"):
        model.add_exactly_one(x[group.index])

    # 2. Ein Dozent darf im selben Zeitintervall maximal eine Vorlesung halten
    for _, group in df.groupby(["teacher_id", "interval"]):
        model.add_at_most_one(x[group.index])

    # 3. Ein Raum darf im selben Zeitintervall maximal eine Vorlesung hosten
    for _, group in df.groupby(["room_id", "interval"]):
        model.add_at_most_one(x[group.index])

    # --- Weiche Bedingungen (Soft Constraints / Objective) ---
    
    # Wir wollen so viele Vorlesungen wie möglich in die bevorzugten Zeiten der Dozenten legen.
    # Wir summieren alle Variablen auf, bei denen is_preferred == 1 ist, und maximieren diesen Wert.
    preferred_score = cp_model.LinearExpr.weighted_sum( # type: ignore
    x.tolist(), 
    df["is_preferred"].tolist()
)
    model.maximize(preferred_score)

    # ==========================================
    # PHASE 3: SOLVER STARTEN
    # ==========================================

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    # Ergebnisse auswerten
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        if status == cp_model.OPTIMAL:
            print("PERFEKTER PLAN GEFUNDEN (Optimal):\n")
        else:
            print("GÜLTIGER PLAN GEFUNDEN (Feasible, aber vielleicht nicht alle Präferenzen erfüllt):\n")
            
        # Nur die Zeilen extrahieren, bei denen die Variable auf 1 (True) gesetzt wurde
        selected = df.loc[solver.boolean_values(x).loc[lambda val: val].index] # type: ignore
        
        # Sortieren für eine schöne Ausgabe (nach Zeit, dann Raum)
        selected = selected.sort_values(by=["interval", "room_id"])
        
        for _, row in selected.iterrows():
            pref_text = " (⭐ Bevorzugte Zeit)" if row["is_preferred"] else ""
            zeit = f"{row['interval'].left.strftime('%a %H:%M')} - {row['interval'].right.strftime('%H:%M')}"
            
            print(f"[{zeit}] {row['lecture_name']} ({row['visitors']} Stud.)")
            print(f" -> Raum: {row['room_id']} (Kapazität: {row['seats']})")
            print(f" -> Dozent: {row['teacher_name']}{pref_text}\n")
            
    else:
        print("Kein machbarer Stundenplan gefunden! (Infeasible)")
        print("Gründe könnten sein: Zu wenig große Räume, oder zu viele Vorlesungen für die verfügbaren Zeiten.")