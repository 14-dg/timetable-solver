import random
import time

# Importiere deine Modelle (Passe die Pfade an, falls nötig)
from solver.models.lecture import Lecture, ApiOccurenceRule
from solver.models.room import Room, RoomType
from solver.models.teacher import Teacher
from solver.models.cohort import Cohort
from solver.models.solver_config import SolverConfig, ConstraintState
from custom_types.event_type import EventType
from solver.solver import UniversityTimetableSolver

def generate_massive_dataset() -> tuple[list[Lecture], list[Room], list[Teacher], list[Cohort]]:
    print("Generiere Testdaten...")
    
    # 1. Kohorten (Studiengänge & Semester)
    cohorts: list[Cohort] = []
    for i in range(1, 21):  # 20 verschiedene Kohorten
        cohorts.append(Cohort(id=f"C{i}", studiengang=f"Studiengang_{i%5}", fachsemester=(i%6)+1))

    # 2. Räume (Campus, Typen und Kapazitäten)
    # Wir nehmen an, das Semester hat 14 Wochen, 30 Slots pro Woche = 420 Slots.
    # Für den Stresstest machen wir die Räume fast immer verfügbar.
    full_availability: set[int] = set(range(420))
    rooms: list[Room] = []
    
    # 5 große Hörsäle
    for i in range(5):
        rooms.append(Room(
            id=100+i, name=f"Hörsaal {i+1}", campus="Main", seats=250, 
            room_types={RoomType.HOERSAAL}, equipment={"Beamer", "Mikrofon"}, 
            available_slots=full_availability.copy()
        ))
    
    # 10 Seminarräume
    for i in range(10):
        rooms.append(Room(
            id=200+i, name=f"Seminar {i+1}", campus="Nord", seats=40, 
            room_types={RoomType.SEMINARRAUM}, equipment={"Beamer"}, 
            available_slots=full_availability.copy()
        ))
        
    # 5 PC-Pools & Labore
    for i in range(5):
        rooms.append(Room(
            id=300+i, name=f"Labor {i+1}", campus="Main", seats=25, 
            room_types={RoomType.LABOR, RoomType.PC_POOL}, equipment={"PCs", "Beamer"}, 
            available_slots=full_availability.copy()
        ))

    # 3. Lehrkräfte (Teachers)
    teachers: list[Teacher] = []
    for i in range(20):
        # Jeder Lehrer hat zufällige Präferenzen (z.B. bevorzugt Vormittage)
        pref_slots: set[int] = set(random.sample(list(range(420)), 50))
        teachers.append(Teacher(
            id=1000+i, name=f"Prof. {chr(65+i)}", 
            max_hours_per_day=None, max_consecutive_blocks=None,
            available_slots=full_availability.copy(), preffered_slots=pref_slots
        ))

    # 4. Vorlesungen (Lectures) generieren
    lectures: list[Lecture] = []
    lecture_id = 1
    
    # Wir generieren 100 verschiedene Kurse!
    for _ in range(45):
        e_type = random.choice(list(EventType))
        req_room_type = {
            EventType.VORLESUNG: RoomType.HOERSAAL,
            EventType.SEMINAR: RoomType.SEMINARRAUM,
            EventType.UEBUNG: RoomType.SEMINARRAUM,
            EventType.PRAKTIKUM: RoomType.LABOR
        }[e_type]
        
        visitors = random.randint(15, 200) if e_type == EventType.VORLESUNG else random.randint(10, 35)
        
        is_biweekly = random.random() > 0.8
        week_step = 2 if is_biweekly else 1
        duration = random.choice([1, 2, 2]) # 1 bis 2 Zeitslots lang (entschärft das Problem weiter)
        
        rules: list[ApiOccurenceRule] = [
            ApiOccurenceRule(duration_slots=duration, week_step=week_step, week_offset=0)
        ]
        
        assigned_teachers = random.sample(teachers, random.choice([1, 1, 2]))
        
        # Jede Vorlesung ist nur für EINE Kohorte ein Pflichtfach (verhindert gigantische Überschneidungen)
        mand_cohorts = random.sample(cohorts, 1) 
        
        lectures.append(Lecture(
            id=lecture_id, 
            title=f"Modul {lecture_id} ({e_type.value})", 
            event_type=e_type, 
            is_online=False, 
            estimated_visitors=visitors,
            occurence_rules=rules, 
            teachers=assigned_teachers,
            mandatory_for=mand_cohorts, 
            elective_for=[],
            required_room_type=req_room_type, 
            room_equipment_required=set(),
            possible_rooms=None, preffered_rooms=None, impossible_rooms=None
        ))
        lecture_id += 1

    return lectures, rooms, teachers, cohorts

def run_massive_test():
    # 1. Daten generieren
    lectures, rooms, teachers, cohorts = generate_massive_dataset()
    print(f"Generiert: {len(lectures)} Vorlesungen, {len(rooms)} Räume, {len(teachers)} Lehrer.")

    # 2. Config aufsetzen (Strenge Hard Constraints)
    config = SolverConfig(
        check_room_capacity=ConstraintState.HARD,
        check_room_equipment=ConstraintState.HARD,
        maximize_teacher_preferences=ConstraintState.SOFT
    )

    # 3. Solver initialisieren
    solver = UniversityTimetableSolver(
        lectures=lectures, 
        rooms=rooms, 
        teachers=teachers, 
        config=config, 
        slots_per_week=30, 
        total_weeks=14
    )

    # 4. Lösen
    start_time = time.time()
    result_df = solver.solve()
    end_time = time.time()

    print(f"\nBenötigte Zeit: {end_time - start_time:.2f} Sekunden")

    if result_df is not None and not result_df.empty:
        print("\n--- AUSZUG AUS DEM STUNDENPLAN ---")
        # Wir zeigen die ersten 15 Zuweisungen sortiert nach Start-Slot an
        sorted_result = result_df.sort_values(by=["base_slot"])
        for _, row in sorted_result.head(45).iterrows():
            room = next(r for r in rooms if r.id == row['room_id'])
            print(f"Slot {row['base_slot']:03d} | Termin: {row['termin_id']} -> {room.name} (Kapazität: {room.seats})")
    else:
        print("Der Solver konnte keinen gültigen Plan finden. (Zu viele Konflikte!)")