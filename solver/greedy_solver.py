"""
Greedy timetable solver.

Strategy:
  - Sort courses by difficulty (most constrained first)
  - For each course session, try every (timeslot, room) combination
  - Pick the first combination that satisfies all hard constraints,
    preferring the one with the lowest soft-constraint penalty score
  - If no slot works → report as unscheduled

This is intentionally simple. The next step would be a backtracking solver
or a CP-SAT model (Google OR-Tools) for better global optimality.
"""

import json
from pathlib import Path
from .models import Timeslot, Room, Lecturer, Course, ScheduleEntry
from .constraints import check_hard_constraints, score_entry


def load_data(path: str | Path) -> tuple[
    list[Timeslot], list[Room], dict[int, Lecturer], list[Course]
]:
    with open(path) as f:
        data = json.load(f)

    timeslots = [Timeslot(**ts) for ts in data["timeslots"]]
    rooms     = [Room(**r)      for r in data["rooms"]]
    lecturers = {
        l["id"]: Lecturer(**l) for l in data["lecturers"]
    }
    courses = [Course(**c) for c in data["courses"]]

    return timeslots, rooms, lecturers, courses


def difficulty_score(course: Course, rooms: list[Room]) -> int:
    """
    Estimate how hard it is to place this course.
    Higher = harder = schedule first.
    Factors: many required students, rare equipment, many sessions.
    """
    eligible_rooms = sum(
        1 for r in rooms
        if r.capacity >= course.students
        and all(eq in r.equipment for eq in course.required_equipment)
    )
    return (1000 - eligible_rooms * 10) + course.sessions_per_week * 5


def solve(data_path: str | Path) -> tuple[list[ScheduleEntry], list[Course]]:
    """
    Run the greedy solver.

    Returns:
        schedule    - list of ScheduleEntry (successfully assigned sessions)
        unscheduled - list of Course objects that could not be placed
    """
    timeslots, rooms, lecturers, courses = load_data(data_path)

    # Sort courses: hardest to place first
    sorted_courses = sorted(
        courses,
        key=lambda c: difficulty_score(c, rooms),
        reverse=True,
    )

    schedule: list[ScheduleEntry] = []
    unscheduled: list[Course] = []

    for course in sorted_courses:
        lecturer = lecturers[course.lecturer_id]
        sessions_needed = course.sessions_per_week
        sessions_placed = 0

        # Collect all valid (timeslot, room, penalty) combinations
        candidates = []
        for timeslot in timeslots:
            for room in rooms:
                valid, _ = check_hard_constraints(
                    course, room, timeslot, lecturer, schedule
                )
                if valid:
                    penalty = score_entry(course, room, timeslot, lecturer, schedule)
                    candidates.append((penalty, timeslot.id, room.id, timeslot, room))

        # Sort by penalty (lowest first), then timeslot id for determinism
        candidates.sort(key=lambda x: (x[0], x[1], x[2]))

        for _, _, _, timeslot, room in candidates:
            if sessions_placed >= sessions_needed:
                break
            # Re-check constraints: earlier sessions of this course
            # may have used this timeslot/room already
            valid, _ = check_hard_constraints(
                course, room, timeslot, lecturer, schedule
            )
            if valid:
                entry = ScheduleEntry(
                    course=course,
                    room=room,
                    timeslot=timeslot,
                    lecturer=lecturer,
                )
                schedule.append(entry)
                sessions_placed += 1

        if sessions_placed < sessions_needed:
            unscheduled.append(course)
            print(
                f"⚠ Could not schedule all sessions for '{course.name}' "
                f"({sessions_placed}/{sessions_needed} placed)"
            )

    return schedule, unscheduled
