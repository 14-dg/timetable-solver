from typing import Any

from api.schemas.request_payload import SolveRequestPayload
from api.translator import DataTranslator
from solver.solver import UniversityTimetableSolver
from api.store import jobs_db


def run_solver_background_task(job_id: str, payload: SolveRequestPayload):
    """
    Diese Funktion läuft im Hintergrund. Sie übersetzt die Daten, 
    startet den Solver und speichert das Ergebnis in der jobs_db.
    """

    jobs_db[job_id] = {"status": "running"}
    
    try:
        # 1. API-JSON in mathematische Dataclasses übersetzen
        translator = DataTranslator(payload)
        rooms = translator.translate_rooms()
        teachers = translator.translate_teachers()
        cohorts, lectures = translator.translate_cohorts_and_lectures(teachers, rooms)
        config = translator.get_solver_config()
        
        # 2. Solver initialisieren
        solver = UniversityTimetableSolver(
            lectures=lectures,
            rooms=rooms,
            teachers=teachers,
            config=config,
            slots_per_week=translator.slots_per_week,
            total_weeks=translator.total_weeks
        )
        
        # 3. Solver ausführen (CP-SAT Berechnung)
        result_df = solver.solve()
        
        if result_df is not None and not result_df.empty:
            # 4. Reverse-Translation: Pandas Grid-Resultate zurück in das JSON-Format mappen
            proposed_changes: list[dict[str, Any]] = []
            
            for _, row in result_df.iterrows():
                # Hier rechnest du den 'base_slot' wieder in 'day_of_week' und 'start_time' um
                # Dies ist eine vereinfachte Platzhalter-Logik basierend auf deinem Grid:
                day_offset = (row["base_slot"] % translator.slots_per_week) // translator.slots_per_day
                day_of_week = day_offset + 1  # 1 = Montag
                
                proposed_changes.append({
                    "change_type": "move", # oder "new", je nachdem ob die timeslot_id existierte
                    "timeslot_id": None,   # Muss im Translator gemappt und hier eingefügt werden
                    "lecture_id": row["lecture_id"],
                    "day_of_week": day_of_week,
                    "start_time": "08:00", # Hier das _slot_index_to_time() Mapping anwenden
                    "end_time": "09:30",
                    "week_skip": 0,
                    "room_id": row["room_id"],
                    "lecturer_ids": row["teachers"]
                })
                
            jobs_db[job_id] = {
                "status": "solved",
                "result": {
                    "proposed_changes": proposed_changes,
                    "unresolved": [],
                    "violations": [],
                    "score": 1.0 # Platzhalter für deine Zielfunktions-Bewertung
                }
            }
        else:
            # Wenn der Solver "None" zurückgibt (Infeasible)
            jobs_db[job_id] = {
                "status": "no_solution",
                "result": {
                    "unresolved": [{"lecture_id": "all", "reason": "hard_constraints_conflict"}]
                }
            }
            
    except Exception as e:
        jobs_db[job_id] = {
            "status": "failed",
            "error": str(e)
        }