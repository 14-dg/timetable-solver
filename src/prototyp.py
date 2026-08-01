import pandas as pd
from ortools.sat.python import cp_model

def solve_timetable():
    
    # Vorlesungen und wer sie hält
    df_lectures = pd.DataFrame([
        ("Mathe_1", "Prof_Müller"),
        ("Mathe_2", "Prof_Müller"), 
        ("Info_1",  "Prof_Schmidt")
    ], columns=["Lecture", "Teacher"])

    # Wann haben die Dozenten Zeit
    df_teacher_avail = pd.DataFrame([
        ("Prof_Müller", "Montag_08:00"),
        ("Prof_Müller", "Montag_10:00"),
        ("Prof_Schmidt", "Montag_10:00"),
        ("Prof_Schmidt", "Dienstag_08:00")
    ], columns=["Teacher", "Timeslot"])

    # Wann sind die Räume verfügbar
    df_room_avail = pd.DataFrame([
        ("Raum_A", "Montag_08:00"),
        ("Raum_A", "Montag_10:00"),
        ("Raum_B", "Montag_10:00"),
        ("Raum_B", "Dienstag_08:00")
    ], columns=["Room", "Timeslot"])


    
    # Verbinde Vorlesungen mit den Zeiten, an denen der Dozent Zeit hat
    df = pd.merge(df_lectures, df_teacher_avail, on="Teacher")

    print("--- Erster merge ---")
    print(df.to_string(), "\n")
    
    # Verbinde das Ergebnis mit den Räumen, die zu diesen Zeiten frei sind
    df = pd.merge(df, df_room_avail, on="Timeslot")
    
    print("--- Suchraum (Alle gültigen Kombinationen) ---")
    print(df.to_string(), "\n")

    # OR-TOOLS
    model = cp_model.CpModel()

    # Erstellt eine Bool-Variable für jede verbliebene Zeile in df
    x = model.new_bool_var_series(name="x", index=df.index)

    # Constraints

    # Jede Vorlesung MUSS exakt einmal stattfinden
    # df.groupby("Lecture") gruppiert alle Zeilen, die zur selben Vorlesung gehören
    for _, group in df.groupby("Lecture"):
        model.add_exactly_one(x[group.index])

    # Ein Dozent kann zur selben Zeit maximal in einem Raum sein
    # gruppieren nach Dozent UND Zeit
    for _, group in df.groupby(["Teacher", "Timeslot"]):
        model.add_at_most_one(x[group.index])

    # Ein Raum darf zur selben Zeit nur maximal eine Vorlesung haben
    # gruppieren nach Raum UND Zeit
    for _, group in df.groupby(["Room", "Timeslot"]):
        model.add_at_most_one(x[group.index])

    # objective


    # lösung ausgeben
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("--- Fertiger Stundenplan ---")
        
        selected_rows = df.loc[solver.boolean_values(x).loc[lambda x: x].index]
        
        for _, row in selected_rows.iterrows():
            print(f"[{row['Timeslot']}] {row['Lecture']} bei {row['Teacher']} in {row['Room']}")
    else:
        print("Kein machbarer Stundenplan gefunden!")

if __name__ == "__main__":
    solve_timetable()