import pandas as pd
from ortools.sat.python import cp_model
from typing import Any

from models.lecture import Lecture
from models.room import Room
from models.teacher import Teacher
from config.solver_config import SolverConfig

class UniversityTimetableSolver:
    def __init__(
        self, 
        lectures: list[Lecture], 
        rooms: list[Room], 
        teachers: list[Teacher], 
        config: SolverConfig,
        slots_per_week: int = 30,
        total_weeks: int = 14
    ) -> None:
        self.lectures: list[Lecture] = lectures
        self.rooms: dict[int, Room] = {r.id: r for r in rooms}
        self.teachers: dict[int, Teacher] = {t.id: t for t in teachers}
        self.config: SolverConfig = config
        
        self.slots_per_week: int = slots_per_week
        self.total_weeks: int = total_weeks
        
        self.model: cp_model.CpModel = cp_model.CpModel()
        self.df_domain: pd.DataFrame = pd.DataFrame()
        
        # NEU: Ein streng typisiertes Dictionary statt einer Pandas Series!
        self.x_vars: dict[int, cp_model.IntVar] = {}

    def _get_occurrences(self, base_slot: int, duration: int, week_skip: int, start_week: int) -> set[int]:
        """ Berechnet alle absoluten Slots im Semester, die durch diesen Termin belegt werden. """
        occupied_slots: set[int] = set()
        step_weeks: int = week_skip + 1
        base_week_offset: int = base_slot % self.slots_per_week
        
        current_week: int = start_week
        while current_week < self.total_weeks:
            week_start_slot = current_week * self.slots_per_week
            for d in range(duration):
                occupied_slots.add(week_start_slot + base_week_offset + d)
            current_week += step_weeks
            
        return occupied_slots

    def _prepare_search_space(self) -> None:
        """ PHASE 1: Pandas Filterung & Sparsity """
        # Strenge Typisierung für die Pandas-Rohdaten
        rows: list[dict[str, Any]] = []
        
        for lecture in self.lectures:
            for t_idx, appt in enumerate(lecture.appointments):
                termin_id: str = f"L{lecture.id}_A{t_idx}"
                possible_rooms = lecture.possible_rooms if lecture.possible_rooms else list(self.rooms.values())
                
                for room in possible_rooms:
                    # Hard Constraints Filtern
                    if self.config.check_room_capacity.value == 2 and room.seats < lecture.estimated_visitors:
                        continue
                    if self.config.check_room_equipment.value == 2 and not lecture.room_equipment_required.issubset(room.equipment):
                        continue
                    if lecture.required_room_type and lecture.required_room_type not in room.room_types:
                        continue
                    if lecture.impossible_rooms and room in lecture.impossible_rooms:
                        continue

                    # Zeit-Raster Filtern
                    start_week_begin = appt.start_week * self.slots_per_week
                    start_week_end = start_week_begin + self.slots_per_week

                    for base_slot in range(start_week_begin, start_week_end):
                        occurrences: set[int] = self._get_occurrences(base_slot, appt.duration_slots, appt.week_skip, appt.start_week)
                        
                        if not occurrences.issubset(room.available_slots):
                            continue
                            
                        teachers_available: bool = True
                        for teacher in lecture.teachers:
                            if not occurrences.issubset(teacher.available_slots):
                                teachers_available = False
                                break
                                
                        if not teachers_available:
                            continue

                        # Metriken berechnen
                        is_pref_room: int = 1 if (lecture.preffered_rooms and room in lecture.preffered_rooms) else 0
                        pref_score: int = sum(
                            len(occurrences.intersection(t.preffered_slots)) 
                            for t in lecture.teachers
                        )

                        # Sauberes, typisiertes Dictionary anhängen
                        row: dict[str, Any] = {
                            "termin_id": termin_id,
                            "lecture_id": lecture.id,
                            "room_id": room.id,
                            "base_slot": base_slot,
                            "occurrences": occurrences,
                            "is_pref_room": is_pref_room,
                            "pref_teacher_score": pref_score,
                            "mandatory_cohorts": [c.id for c in lecture.mandatory_for],
                            "teachers": [t.id for t in lecture.teachers]
                        }
                        rows.append(row)
                        
        self.df_domain = pd.DataFrame(rows)
        print(f"Suchraum erstellt: {len(self.df_domain)} gültige Variablen.")

    def _build_model(self) -> None:
        """ PHASE 2: Modellierung der Constraints im CP-SAT Solver """
        if self.df_domain.empty:
            return
            
        # 1. OR-Tools Variablen im sauberen Dictionary erstellen (Verhindert __getitem__ Fehler)
        for idx in self.df_domain.index:
            idx_int = int(str(idx))
            self.x_vars[idx_int] = self.model.new_bool_var(name=f"x_{idx_int}")

        # 2. Genau Einmal Bedingung
        for _, group in self.df_domain.groupby("termin_id"):
            # Typensichere Liste von IntVars generieren
            group_vars: list[cp_model.IntVar] = [self.x_vars[int(str(i))] for i in group.index]
            self.model.add_exactly_one(group_vars)

        # 3. Hilfs-Datenstrukturen mit perfekten Typ-Signaturen
        slot_occupancy_room: dict[tuple[int, int], list[cp_model.IntVar]] = {}
        slot_occupancy_teacher: dict[tuple[int, int], list[cp_model.IntVar]] = {}
        slot_occupancy_cohort: dict[tuple[str, int], list[cp_model.IntVar]] = {}

        # itertuples() ist deutlich typensicherer als iterrows()
        for row in self.df_domain.itertuples():
            idx_int = int(str(row.Index))
            var: cp_model.IntVar = self.x_vars[idx_int]
            
            # Die Listen in itertuples() behalten ihre Typen aus dem DataFrame
            for active_slot in row.occurrences:  # type: ignore (Pandas NamedTuple dynamisch)
                slot_occupancy_room.setdefault((row.room_id, active_slot), []).append(var)
                
                for t_id in row.teachers:
                    slot_occupancy_teacher.setdefault((t_id, active_slot), []).append(var)
                    
                for c_id in row.mandatory_cohorts:
                    slot_occupancy_cohort.setdefault((c_id, active_slot), []).append(var)

        # 4. Überschneidungsverbote
        for vars_in_slot in slot_occupancy_room.values():
            self.model.add_at_most_one(vars_in_slot)

        for vars_in_slot in slot_occupancy_teacher.values():
            self.model.add_at_most_one(vars_in_slot)

        for vars_in_slot in slot_occupancy_cohort.values():
            self.model.add_at_most_one(vars_in_slot)

        # 5. Zielfunktion
        objective_terms: list[cp_model.LinearExpr] = []
        
        if "is_pref_room" in self.df_domain.columns:
            # Wir bauen die Listen für den Solver explizit zusammen (löst weighted_sum Fehler)
            pref_rooms_vars: list[cp_model.IntVar] = []
            pref_rooms_coeffs: list[int] = []
            
            for row in self.df_domain.itertuples():
                if row.is_pref_room > 0:
                    pref_rooms_vars.append(self.x_vars[int(str(row.Index))])
                    pref_rooms_coeffs.append(int(row.is_pref_room * self.config.weight_constant_room))
                    
            if pref_rooms_vars:
                objective_terms.append(cp_model.LinearExpr.weighted_sum(pref_rooms_vars, pref_rooms_coeffs))

        if self.config.maximize_teacher_preferences.value == 1:
            pref_times_vars: list[cp_model.IntVar] = []
            pref_times_coeffs: list[int] = []
            
            for row in self.df_domain.itertuples():
                if row.pref_teacher_score > 0:
                    pref_times_vars.append(self.x_vars[int(str(row.Index))])
                    pref_times_coeffs.append(int(row.pref_teacher_score * self.config.weight_teacher_preferences))
                    
            if pref_times_vars:
                objective_terms.append(cp_model.LinearExpr.weighted_sum(pref_times_vars, pref_times_coeffs))

        if objective_terms:
            self.model.maximize(sum(objective_terms))

    def solve(self) -> pd.DataFrame | None:
        """ PHASE 3: Solver Ausführung """
        self._prepare_search_space()
        
        if self.df_domain.empty:
            print("Abbruch: Suchraum ist leer.")
            return None
            
        self._build_model()
        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        
        print("Starte den Google OR-Tools Solver...")
        status = solver.solve(self.model)

        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print(f"Lösung gefunden! Status: {solver.status_name(status)}")
            
            # Lösung ohne anonymes, untypisiertes Lambda in .loc() filtern
            selected_indices: list[int] = [
                idx for idx, var in self.x_vars.items() 
                if solver.value(var) == 1
            ]
            
            return self.df_domain.loc[selected_indices].copy()
        else:
            print("Keine Lösung gefunden (INFEASIBLE).")
            return None