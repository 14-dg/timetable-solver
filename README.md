# timetable-solver

A Python sandbox for experimenting with automatic timetable generation.

This is a simplified model of the constraints used in [myroomfinder.de](https://myroomfinder.de) — a SaaS platform for room and timetable management at German universities. The goal is to develop and test scheduling algorithms here before integrating them into the main product.

---

## Problem

Given a set of **courses**, **rooms**, **lecturers**, and **weekly timeslots**, assign each course session to a room and timeslot such that:

### Hard constraints (must never be violated)
| # | Constraint |
|---|-----------|
| 1 | Room capacity ≥ number of students |
| 2 | Room has all equipment the course requires |
| 3 | No room is double-booked in the same timeslot |
| 4 | No lecturer teaches two courses at the same time |
| 5 | Lecturer is available in the assigned timeslot |

### Soft constraints (should be minimized)
| # | Constraint |
|---|-----------|
| 6 | Lecturer should not exceed their `max_courses_per_day` |
| 7 | Multiple sessions of the same course should be spread across different days |

---

## Project structure

```
timetable-solver/
├── data/
│   └── sample_data.json      # Rooms, lecturers, courses, timeslots
├── solver/
│   ├── models.py             # Dataclasses: Course, Room, Lecturer, Timeslot, ScheduleEntry
│   ├── constraints.py        # Hard + soft constraint functions
│   └── greedy_solver.py      # Greedy solver (most-constrained-first)
├── main.py                   # Entry point, prints formatted schedule
├── requirements.txt
└── README.md
```

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python main.py
# or with a custom data file:
python main.py data/sample_data.json
```

---

## Data format

Edit `data/sample_data.json` to change the input. Key fields:

**Rooms**
```json
{ "id": 1, "name": "Room 101", "capacity": 30, "equipment": ["projector"] }
```

**Lecturers**
```json
{ "id": 1, "name": "Prof. Schmidt", "unavailable_timeslots": [1, 2], "max_courses_per_day": 2 }
```

**Courses**
```json
{
  "id": 1, "name": "Mathematik 1", "lecturer_id": 1,
  "students": 55, "required_equipment": ["projector", "microphone"],
  "sessions_per_week": 2
}
```

---

## Ideas for improvement

The current greedy solver is intentionally simple — it's a starting point, not a final solution. Some directions to explore:

- **Backtracking** — undo bad decisions and try alternatives when stuck
- **Local search / hill climbing** — start with a valid schedule, then swap entries to improve the soft-constraint score
- **CP-SAT (Google OR-Tools)** — model everything as a constraint satisfaction problem and let the solver find the optimal solution
  ```bash
  pip install ortools
  ```
  Good starting point: [OR-Tools CP-SAT Python examples](https://developers.google.com/optimization/reference/python/sat/python/cp_model)

- **Additional constraints to model:**
  - Courses from the same semester should not overlap (students can't attend both)
  - Some courses need consecutive double-slots
  - Preferred timeslots per lecturer

---

## Relation to myroomfinder schema

| This project | myroomfinder DB |
|---|---|
| `Course` | `lectures` + `lecture_timeslots` |
| `Room` | `rooms` + `room_equipment` |
| `Lecturer` | `lecturers` |
| `Timeslot` | `lecture_timeslots.day_of_week` + `start_time`/`end_time` |
| `ScheduleEntry` | `lecture_instances` |
