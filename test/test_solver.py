import pytest
import pandas as pd

from models.lecture import Lecture, EventType, Appointment
from models.room import Room, RoomType
from models.teacher import Teacher
from models.cohort import Cohort
from config.solver_config import SolverConfig, ConstraintState

from solver.solver import UniversityTimetableSolver

# ==========================================
# TEST 1: Die Zeit-Mathematik (Occurrences)
# ==========================================
def test_get_occurrences() -> None:
    # Wir brauchen nur einen leeren Solver für die Hilfsfunktion
    solver = UniversityTimetableSolver(
        lectures=[], rooms=[], teachers=[], config=SolverConfig(), 
        slots_per_week=30, total_weeks=4
    )
    
    # Fall A: Wöchentlich (week_skip=0), startet in Woche 0, Dauer 2 Slots, Basis-Slot 0 (Montag 08:00)
    # Erwartung: Slots 0,1 (Woche 0), 30,31 (Woche 1), 60,61 (Woche 2), 90,91 (Woche 3)
    occ1 = solver._get_occurrences(base_slot=0, duration=2, week_skip=0, start_week=0)
    assert occ1 == {0, 1, 30, 31, 60, 61, 90, 91}
    
    # Fall B: 14-tägig (week_skip=1), startet in Woche 1, Dauer 1 Slot, Basis-Slot 32 (Woche 1, Montag 12:00)
    # Erwartung: Slot 32 (Woche 1), Slot 92 (Woche 3)
    occ2 = solver._get_occurrences(base_slot=32, duration=1, week_skip=1, start_week=1)
    assert occ2 == {32, 92}

# ==========================================
# FIXTURES FÜR BASIS-DATEN
# ==========================================
@pytest.fixture
def base_room() -> Room:
    # Raum ist nur in Woche 0 und 1 jeweils am Montag von 08:00 bis 12:00 (Slots 0,1 und 30,31) frei
    return Room(
        id=1, name="Labor A", campus="Main", seats=30, 
        room_types={RoomType.LABOR}, equipment={"Beamer"}, 
        available_slots={0, 1, 30, 31}
    )

@pytest.fixture
def base_teacher() -> Teacher:
    # Lehrer hat exakt die gleichen Zeiten wie der Raum frei
    return Teacher(
        id=1, name="Prof. Test", max_hours_per_day=None, max_consecutive_blocks=None,
        available_slots={0, 1, 30, 31}, preffered_slots={0, 30}
    )

@pytest.fixture
def base_cohort() -> Cohort:
    return Cohort(id="C1", studiengang="Informatik", fachsemester=1)

# ==========================================
# TEST 2: Machbarer Stundenplan (Feasible)
# ==========================================
def test_solver_finds_valid_schedule(
    base_room: Room, base_teacher: Teacher, base_cohort: Cohort
) -> None:
    # 1. Termin: 2 Slots lang, wöchentlich, Start Woche 0
    appt = Appointment(duration_slots=2, week_skip=0, start_week=0)
    
    lecture = Lecture(
        id=1, title="Mathe 1", event_type=EventType.VORLESUNG, is_online=False, 
        estimated_visitors=20, appointments=[appt], teachers=[base_teacher], 
        mandatory_for=[base_cohort], elective_for=[], 
        required_room_type=RoomType.LABOR, room_equipment_required=set(),
        possible_rooms=None, preffered_rooms=None, impossible_rooms=None
    )
    
    config = SolverConfig(check_room_capacity=ConstraintState.HARD)
    
    # Solver initialisieren (Wir simulieren nur 2 Wochen für schnelle Tests)
    solver = UniversityTimetableSolver(
        lectures=[lecture], rooms=[base_room], teachers=[base_teacher], 
        config=config, slots_per_week=30, total_weeks=2
    )
    
    result = solver.solve()
    
    # Püfungen
    assert result is not None, "Solver hätte eine Lösung finden müssen!"
    assert not result.empty, "Ergebnis-DataFrame darf nicht leer sein!"
    assert len(result) == 1, "Es sollte exakt ein Termin geplant werden."
    
    # Der Solver MUSS Slot 0 als Basis wählen, da 0 und 1 die einzigen zusammenhängenden freien Slots sind
    assert result.iloc[0]["base_slot"] == 0

# ==========================================
# TEST 3: Unmachbarer Stundenplan (Double Booking)
# ==========================================
def test_solver_fails_on_double_booking(
    base_room: Room, base_teacher: Teacher, base_cohort: Cohort
) -> None:
    # Wir erstellen ZWEI Vorlesungen, die beide 2 Slots dauern und wöchentlich sind.
    # Da der Raum/Lehrer pro Woche nur exakt 2 Slots frei hat ({0, 1}), 
    # können physikalisch nicht beide Vorlesungen stattfinden.
    
    appt1 = Appointment(duration_slots=2, week_skip=0, start_week=0)
    lecture1 = Lecture(
        id=1, title="Mathe 1", event_type=EventType.VORLESUNG, is_online=False, 
        estimated_visitors=20, appointments=[appt1], teachers=[base_teacher], 
        mandatory_for=[base_cohort], elective_for=[], 
        required_room_type=RoomType.LABOR, room_equipment_required=set(),
        possible_rooms=None, preffered_rooms=None, impossible_rooms=None
    )
    
    appt2 = Appointment(duration_slots=2, week_skip=0, start_week=0)
    lecture2 = Lecture(
        id=2, title="Info 1", event_type=EventType.VORLESUNG, is_online=False, 
        estimated_visitors=20, appointments=[appt2], teachers=[base_teacher], 
        mandatory_for=[base_cohort], elective_for=[], 
        required_room_type=RoomType.LABOR, room_equipment_required=set(),
        possible_rooms=None, preffered_rooms=None, impossible_rooms=None
    )
    
    config = SolverConfig(check_room_capacity=ConstraintState.HARD)
    
    solver = UniversityTimetableSolver(
        lectures=[lecture1, lecture2], rooms=[base_room], teachers=[base_teacher], 
        config=config, slots_per_week=30, total_weeks=2
    )
    
    result = solver.solve()
    
    # Prüfung: Der Solver muss mit 'None' abbrechen, da die Constraint-Regeln verletzen würden
    assert result is None, "Solver hätte abbrechen müssen, da ein Double Booking vorliegt!"