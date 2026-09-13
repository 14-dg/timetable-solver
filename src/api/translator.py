from api.schemas.schema import SolveRequestPayload
from solver.models.event_type import EventType
from solver.models.lecture import Lecture, OccurenceRule
from solver.models.room import Room, RoomType
from solver.models.teacher import Teacher
from solver.models.cohort import Cohort  # WICHTIG: Wieder importieren!
from solver.models.solver_config import SolverConfig, ConstraintState


class DataTranslator:
    def __init__(self, payload: SolveRequestPayload):
        self.payload = payload
        self.grid = payload.grid_config
        
        # Grid-Dimensionen dynamisch berechnen
        start_mins = self.grid.day_start_time.hour * 60 + self.grid.day_start_time.minute
        end_mins = self.grid.day_end_time.hour * 60 + self.grid.day_end_time.minute
        
        self.slots_per_day = (end_mins - start_mins) // self.grid.slot_duration_minutes
        self.slots_per_week = self.slots_per_day * self.grid.days_per_week
        
        # Für das MVP fixieren wir es auf 14 Wochen (kann später ans Semester-Datum gekoppelt werden)
        self.total_weeks = 14 

    def slot_index_to_time(self, slot_index: int, duration_slots: int) -> tuple[str, str]:
        """ Wandelt einen Tages-Slot zurück in HH:MM Strings (z.B. '08:00', '09:30'). """
        start_mins = (self.grid.day_start_time.hour * 60 + self.grid.day_start_time.minute) + (slot_index * self.grid.slot_duration_minutes)
        end_mins = start_mins + (duration_slots * self.grid.slot_duration_minutes)
        
        start_str = f"{start_mins // 60:02d}:{start_mins % 60:02d}"
        end_str = f"{end_mins // 60:02d}:{end_mins % 60:02d}"
        
        return start_str, end_str

    def translate_rooms(self) -> list[Room]:
        rooms: list[Room] = []
        for r in self.payload.rooms:
            if not r.accessible or r.is_locked:
                continue
            
            available_slots = set(range(self.total_weeks * self.slots_per_week))
            
            rooms.append(Room(
                id=r.id, name=r.name, campus="Main", seats=r.seats,
                room_types={RoomType.SEMINARRAUM}, equipment=set(),
                available_slots=available_slots
            ))
        return rooms

    def translate_teachers(self) -> list[Teacher]:
        teachers: list[Teacher] = []
        for t in self.payload.lecturers:
            available_slots = set(range(self.total_weeks * self.slots_per_week))
            teachers.append(Teacher(
                id=t.id, name=t.name, max_hours_per_day=None, max_consecutive_blocks=None,
                available_slots=available_slots, preffered_slots=set()
            ))
        return teachers

    def translate_lectures(self, teachers: list[Teacher]) -> list[Lecture]:
        lectures: list[Lecture] = []
        teacher_map = {t.id: t for t in teachers}
        
        for api_l in self.payload.lectures:
            e_type = EventType.VORLESUNG
            try:
                if api_l.type: e_type = EventType(api_l.type.lower())
            except ValueError:
                pass
                
            assigned_teachers = [teacher_map[t_id] for t_id in api_l.lecturer_ids if t_id in teacher_map]
            
            # NEU: Kohorten (Studiengang + Semester) dynamisch aus dem neuen Array aufbauen
            mandatory_cohorts: list[Cohort] = []
            for fs in api_l.fachsemester:
                # Wir bauen eine eindeutige ID aus Studiengang und Semester
                cohort_id = f"COS{fs.course_of_study_id}_SEM{fs.semester}"
                mandatory_cohorts.append(Cohort(
                    id=cohort_id, 
                    studiengang=str(fs.course_of_study_id), 
                    fachsemester=fs.semester
                ))
            
            # Die OccurenceRules anlegen
            rules = [OccurenceRule(
                duration_slots=r.duration_slots,
                week_step=r.week_step,
                week_offset=r.week_offset
            ) for r in api_l.rules]

            lectures.append(Lecture(
                id=api_l.id,
                title=api_l.title,
                event_type=e_type,
                is_online=False,
                estimated_visitors=30, # MVP Fallback (Da es nicht aus der DB kommt)
                allow_weekends=False,  # MVP: Vorlesungen nur Mo-Fr
                occurence_rules=rules,
                teachers=assigned_teachers,
                mandatory_for=mandatory_cohorts, # <--- Integriert die Kohorten für Hard-Constraints!
                elective_for=[],
                required_room_type=None,
                room_equipment_required=set(),
                possible_rooms=None, preffered_rooms=None, impossible_rooms=None
            ))
        return lectures

    def get_solver_config(self) -> SolverConfig:
        return SolverConfig(
            check_room_capacity=ConstraintState.HARD,
            check_room_equipment=ConstraintState.IGNORED,
        )