from datetime import time, datetime

# API Schemas (Deine Pydantic Modelle)
from api.schemas.request_payload import SolveRequestPayload


# Solver Modelle (Deine Dataclasses)
from solver.models.event_type import EventType
from solver.models.lecture import Lecture, OccurenceRule
from solver.models.room import Room, RoomType
from solver.models.teacher import Teacher
from solver.models.cohort import Cohort
from solver.models.solver_config import SolverConfig, ConstraintState

class DataTranslator:
    def __init__(self, payload: SolveRequestPayload, slots_per_day: int = 6):
        self.payload = payload
        self.grid = payload.grid_config
        self.slots_per_day = slots_per_day
        self.days_per_week = 7
        self.slots_per_week = slots_per_day * self.days_per_week
        
        # Berechnung der Semesterdauer in Wochen (vereinfacht)
        delta = self.payload.semester.end_date - self.payload.semester.start_date
        self.total_weeks = max(1, delta.days // 7)

    def _time_to_slot_index(self, t: time) -> int:
        """ Wandelt eine beliebige Uhrzeit mathematisch in den relativen Tages-Slot um. """
        start_mins = self.grid.day_start_time.hour * 60 + self.grid.day_start_time.minute
        t_mins = t.hour * 60 + t.minute
        
        if t_mins < start_mins:
            return 0  # Fallback, falls jemand vor Öffnung plant
            
        # Integer-Division ergibt genau den richtigen Slot-Index
        return (t_mins - start_mins) // self.grid.slot_duration_minutes

    def _datetime_to_absolute_slot(self, dt: datetime, semester_start: datetime) -> int:
        """ Wandelt ein absolutes Datum in eine globale Slot-ID (0 bis N) um. """
        days_since_start = (dt.date() - semester_start.date()).days
        week = days_since_start // 7
        day_of_week = dt.isoweekday() # 1 = Montag, 7 = Sonntag
        
        if day_of_week > self.days_per_week:
            return -1 # Wochenende (außerhalb des Rasters)
            
        day_offset = (day_of_week - 1) * self.slots_per_day
        time_slot = self._time_to_slot_index(dt.time())
        
        return (week * self.slots_per_week) + day_offset + time_slot

    def translate_rooms(self) -> list[Room]:
        rooms: list[Room] = []
        semester_start = datetime.combine(self.payload.semester.start_date, time.min)
        
        for r in self.payload.rooms:
            if not r.accessible or r.is_locked:
                continue
                
            # Basis: Raum ist immer frei
            available_slots = set(range(self.total_weeks * self.slots_per_week))
            
            # Geblockte Zeiten (bookings) entfernen
            for booking in self.payload.blocked_room_bookings:
                if booking.room_id == r.id:
                    start_slot = self._datetime_to_absolute_slot(booking.start_time, semester_start)
                    end_slot = self._datetime_to_absolute_slot(booking.end_time, semester_start)
                    
                    if start_slot != -1 and end_slot != -1:
                        # Entferne alle Slots, die in diesen Bereich fallen
                        blocked = set(range(start_slot, end_slot + 1))
                        available_slots -= blocked
            
            # Mapping des RoomType (Fallback auf SEMINARRAUM)
            rt_enum = RoomType.SEMINARRAUM
            try:
                if r.room_type_id:
                    rt_enum = RoomType(r.room_type_id.lower())
            except ValueError:
                pass

            rooms.append(Room(
                id=r.id,
                name=r.name,
                campus="Main", # Wird im Schema noch nicht mitgeliefert
                seats=r.seats,
                room_types={rt_enum},
                equipment=set(r.equipment_ids),
                available_slots=available_slots
            ))
        return rooms

    def translate_teachers(self) -> list[Teacher]:
        teachers: list[Teacher] = []
        
        for t in self.payload.lecturers:
            available_slots: set[int] = set()
            preferred_slots: set[int] = set()
            
            # Verfügbarkeiten aus dem Payload filtern
            availabilities = [a for a in self.payload.lecturer_availability if a.lecturer_id == t.id]
            
            for a in availabilities:
                day_offset = (a.day_of_week - 1) * self.slots_per_day
                start_idx = self._time_to_slot_index(a.start_time)
                end_idx = self._time_to_slot_index(a.end_time)
                
                # Wir generieren die Slots für jede Woche des Semesters
                for w in range(self.total_weeks):
                    week_offset = w * self.slots_per_week
                    slots = set(range(week_offset + day_offset + start_idx, week_offset + day_offset + end_idx + 1))
                    
                    if a.constraint_type == 'hard':
                        available_slots.update(slots)
                    elif a.constraint_type == 'soft':
                        preferred_slots.update(slots)
            
            # Fallback: Wenn keine Hard-Constraints definiert sind, nehmen wir volle Verfügbarkeit an
            if not available_slots:
                available_slots = set(range(self.total_weeks * self.slots_per_week))
                
            teachers.append(Teacher(
                id=t.id,
                name=t.name,
                max_hours_per_day=None,
                max_consecutive_blocks=None,
                available_slots=available_slots,
                preffered_slots=preferred_slots
            ))
        return teachers

    def translate_cohorts_and_lectures(self, teachers: list[Teacher], rooms: list[Room]) -> tuple[list[Cohort], list[Lecture]]:
        cohorts_dict: dict[str, Cohort] = {}
        lectures_dict: dict[int, Lecture] = {}
        
        teacher_map = {t.id: t for t in teachers}
        
        # 1. Kohorten dynamisch aus den Timeslots aufbauen
        for ts in self.payload.lecture_timeslots:
            for cos_id in ts.course_of_study_ids:
                for sem in ts.fachsemester:
                    c_id = f"{cos_id}_{sem}"
                    if c_id not in cohorts_dict:
                        cohorts_dict[c_id] = Cohort(id=c_id, studiengang=str(cos_id), fachsemester=sem)
        
        # 2. Timeslots nach lecture_id gruppieren
        for ts in self.payload.lecture_timeslots:
            l_id = ts.lecture_id
            
            if l_id not in lectures_dict:
                # Neues Lecture-Objekt anlegen
                e_type = EventType.VORLESUNG
                try:
                    if ts.lecture_type:
                        e_type = EventType(ts.lecture_type.lower())
                except ValueError:
                    pass

                assigned_teachers = [teacher_map[t_id] for t_id in ts.lecturer_ids if t_id in teacher_map]
                mand_cohorts = [cohorts_dict[f"{c}_{s}"] for c in ts.course_of_study_ids for s in ts.fachsemester]

                lectures_dict[l_id] = Lecture(
                    id=l_id,
                    title=ts.lecture_title,
                    event_type=e_type,
                    is_online=ts.is_online,
                    estimated_visitors=0, # Könnte aus Kohorten-Größen berechnet werden
                    occurence_rules=[],
                    teachers=assigned_teachers,
                    mandatory_for=mand_cohorts,
                    elective_for=[],
                    required_room_type=None,
                    room_equipment_required=set(),
                    possible_rooms=None,
                    preffered_rooms=None,
                    impossible_rooms=None
                )
            
            # Die OccurenceRule aus dem Timeslot ableiten
            duration = 1
            if ts.start_time and ts.end_time:
                start_idx = self._time_to_slot_index(ts.start_time)
                end_idx = self._time_to_slot_index(ts.end_time)
                duration = max(1, end_idx - start_idx)

            rule = OccurenceRule(
                duration_slots=duration,
                week_step=ts.week_skip + 1,
                week_offset=0
            )
            lectures_dict[l_id].occurence_rules.append(rule)

        return list(cohorts_dict.values()), list(lectures_dict.values())

    def get_solver_config(self) -> SolverConfig:
        return SolverConfig(
            check_room_capacity=ConstraintState.HARD,
            check_room_equipment=ConstraintState.HARD,
            avoid_hohlstunden=ConstraintState.SOFT,
            weight_hohlstunden=10
        )

    def _slot_index_to_time(self, slot_index: int, duration_slots: int) -> tuple[str, str]:
        """ Wandelt einen Tages-Slot zurück in HH:MM Strings. """
        start_mins = (self.grid.day_start_time.hour * 60 + self.grid.day_start_time.minute) + (slot_index * self.grid.slot_duration_minutes)
        end_mins = start_mins + (duration_slots * self.grid.slot_duration_minutes)
        
        start_str = f"{start_mins // 60:02d}:{start_mins % 60:02d}"
        end_str = f"{end_mins // 60:02d}:{end_mins % 60:02d}"
        
        return start_str, end_str