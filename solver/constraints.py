"""
Constraint checking for timetable entries.

Hard constraints → must never be violated (return False = conflict)
Soft constraints → should be avoided, tracked as a penalty score

Hard constraints:
  1. Room capacity must fit number of students
  2. Room must have all required equipment
  3. No room double-booked in the same timeslot
  4. No lecturer double-booked in the same timeslot
  5. Lecturer must be available in the timeslot

Soft constraints (penalty-based):
  6. Lecturer should not exceed max_courses_per_day
  7. Same course's sessions should be spread across different days
"""

from .models import Course, Room, Timeslot, Lecturer, ScheduleEntry


# ---------------------------------------------------------------------------
# Hard constraints
# ---------------------------------------------------------------------------

def room_has_capacity(room: Room, course: Course) -> bool:
    return room.capacity >= course.students


def room_has_equipment(room: Room, course: Course) -> bool:
    return all(eq in room.equipment for eq in course.required_equipment)


def room_is_free(
    room: Room,
    timeslot: Timeslot,
    existing: list[ScheduleEntry],
) -> bool:
    return not any(
        e.room.id == room.id and e.timeslot.id == timeslot.id
        for e in existing
    )


def lecturer_is_free(
    lecturer: Lecturer,
    timeslot: Timeslot,
    existing: list[ScheduleEntry],
) -> bool:
    return not any(
        e.lecturer.id == lecturer.id and e.timeslot.id == timeslot.id
        for e in existing
    )


def lecturer_is_available(lecturer: Lecturer, timeslot: Timeslot) -> bool:
    return timeslot.id not in lecturer.unavailable_timeslots


def check_hard_constraints(
    course: Course,
    room: Room,
    timeslot: Timeslot,
    lecturer: Lecturer,
    existing: list[ScheduleEntry],
) -> tuple[bool, list[str]]:
    """
    Returns (is_valid, list_of_violated_constraints).
    """
    violations = []

    if not room_has_capacity(room, course):
        violations.append(
            f"Capacity: {room.name} holds {room.capacity}, "
            f"but {course.name} needs {course.students} seats"
        )
    if not room_has_equipment(room, course):
        missing = [e for e in course.required_equipment if e not in room.equipment]
        violations.append(f"Equipment missing in {room.name}: {missing}")
    if not room_is_free(room, timeslot, existing):
        violations.append(f"Room conflict: {room.name} already booked at {timeslot}")
    if not lecturer_is_free(lecturer, timeslot, existing):
        violations.append(f"Lecturer conflict: {lecturer.name} already teaching at {timeslot}")
    if not lecturer_is_available(lecturer, timeslot):
        violations.append(f"Availability: {lecturer.name} unavailable at {timeslot}")

    return len(violations) == 0, violations


# ---------------------------------------------------------------------------
# Soft constraints (penalty scoring)
# ---------------------------------------------------------------------------

def penalty_lecturer_overloaded(
    lecturer: Lecturer,
    timeslot: Timeslot,
    existing: list[ScheduleEntry],
) -> int:
    """Penalty if lecturer already teaches max_courses_per_day on this day."""
    courses_that_day = sum(
        1 for e in existing
        if e.lecturer.id == lecturer.id and e.timeslot.day == timeslot.day
    )
    return 10 if courses_that_day >= lecturer.max_courses_per_day else 0


def penalty_course_sessions_same_day(
    course: Course,
    timeslot: Timeslot,
    existing: list[ScheduleEntry],
) -> int:
    """Penalty if another session of the same course is already on this day."""
    same_day = sum(
        1 for e in existing
        if e.course.id == course.id and e.timeslot.day == timeslot.day
    )
    return 5 * same_day


def score_entry(
    course: Course,
    room: Room,
    timeslot: Timeslot,
    lecturer: Lecturer,
    existing: list[ScheduleEntry],
) -> int:
    """
    Lower score = better placement.
    Only call this after hard constraints pass.
    """
    penalty = 0
    penalty += penalty_lecturer_overloaded(lecturer, timeslot, existing)
    penalty += penalty_course_sessions_same_day(course, timeslot, existing)
    return penalty
