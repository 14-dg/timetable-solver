from typing import Any
from api.schemas.schema import SolveRequestPayload
from api.translator import DataTranslator
from solver.solver import UniversityTimetableSolver

from api.store import jobs_db

def run_solver_background_task(job_id: str, payload: SolveRequestPayload):
    jobs_db[job_id] = {"status": "running"}
    
    try:
        translator = DataTranslator(payload)
        rooms = translator.translate_rooms()
        teachers = translator.translate_teachers()
        lectures = translator.translate_lectures(teachers)
        config = translator.get_solver_config()
        
        solver = UniversityTimetableSolver(
            lectures=lectures,
            rooms=rooms,
            teachers=teachers,
            config=config,
            slots_per_week=translator.slots_per_week,
            total_weeks=translator.total_weeks
        )
        
        result_df = solver.solve()
        
        if result_df is not None and not result_df.empty:
            generated_schedule: list[dict[str, Any]] = []
            
            for _, row in result_df.iterrows():
                # 1. Wochentag ausrechnen (1 = Montag)
                day_offset = (row["base_slot"] % translator.slots_per_week) // translator.slots_per_day
                day_of_week = day_offset + 1  
                
                # 2. Uhrzeit ausrechnen
                slot_of_day = (row["base_slot"] % translator.slots_per_week) % translator.slots_per_day
                start_time_str, end_time_str = translator.slot_index_to_time(
                    slot_index=slot_of_day, 
                    duration_slots=row["duration_slots"]
                )
                
                # 3. Zum fertigen Stundenplan hinzufügen
                generated_schedule.append({
                    "lecture_id": row["lecture_id"],
                    "day_of_week": day_of_week,
                    "start_time": start_time_str,
                    "end_time": end_time_str,
                    "room_id": row["room_id"],
                    "lecturer_ids": row["teachers"]
                })
                
            jobs_db[job_id] = {
                "status": "solved",
                "result": {
                    "schedule": generated_schedule
                }
            }
        else:
            jobs_db[job_id] = {
                "status": "no_solution",
                "result": {"unresolved": [{"lecture_id": "all", "reason": "infeasible (zu wenig Räume für das Curriculum)"}]}
            }
            
    except Exception as e:
        jobs_db[job_id] = {
            "status": "failed",
            "error": str(e)
        }