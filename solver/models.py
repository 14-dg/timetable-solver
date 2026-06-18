"""
Data models for the timetable solver.
These mirror the core concepts from the myroomfinder database schema,
simplified for algorithmic experimentation.
"""

from dataclasses import dataclass, field


@dataclass
class Timeslot:
    id: int
    day: str        # e.g. "Monday"
    start: str      # e.g. "08:00"
    end: str        # e.g. "09:30"

    def __repr__(self):
        return f"{self.day} {self.start}–{self.end}"


@dataclass
class Room:
    id: int
    name: str
    capacity: int
    equipment: list[str] = field(default_factory=list)

    def __repr__(self):
        return self.name


@dataclass
class Lecturer:
    id: int
    name: str
    unavailable_timeslots: list[int] = field(default_factory=list)   # timeslot IDs
    max_courses_per_day: int = 3

    def __repr__(self):
        return self.name


@dataclass
class Course:
    id: int
    name: str
    lecturer_id: int
    students: int                       # number of students → determines room size
    required_equipment: list[str] = field(default_factory=list)
    sessions_per_week: int = 1          # how many timeslots to assign per week

    def __repr__(self):
        return self.name


@dataclass
class ScheduleEntry:
    """A single assignment: one course session in a specific room at a specific time."""
    course: Course
    room: Room
    timeslot: Timeslot
    lecturer: Lecturer

    def __repr__(self):
        return (
            f"{self.course.name} | {self.room.name} | "
            f"{self.timeslot} | {self.lecturer.name}"
        )
