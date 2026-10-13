from typing import Self

from pydantic import BaseModel, Field, model_validator

from features.timetables.input_models.lecture_in import LectureIn
from features.timetables.input_models.room_in import RoomIn
from features.timetables.input_models.time_grid_in import TimeGridIn
from features.timetables.types import UniqueID


class TimetableProblem(BaseModel):
    lectures: list[LectureIn] = Field()
    rooms: list[RoomIn] = Field()
    time_grid: TimeGridIn = Field()


    @model_validator(mode="after")
    def validate_lectures_unique_ids(self) -> Self:
        """
        Ensure that all lectures have unique IDs to avoid conflicts.
        """
        lecture_ids: set[UniqueID] = {lecture.id for lecture in self.lectures}
        if len(lecture_ids) != len(self.lectures):
            raise ValueError("Lecture IDs must be unique.")
        return self


    @model_validator(mode="after")
    def validate_rooms_unique_ids(self) -> Self:
        """
        Ensure that all rooms have unique IDs to avoid conflicts.
        """
        room_ids: set[UniqueID] = {room.id for room in self.rooms}
        if len(room_ids) != len(self.rooms):
            raise ValueError("Room IDs must be unique.")
        return self


    @model_validator(mode="after")
    def validate_teachers_unique_ids(self) -> Self:
        """
        Ensure that all teachers have unique IDs to avoid conflicts.
        """
        teacher_ids: set[UniqueID] = set()

        for lecture in self.lectures:
            if lecture.teacher.id in teacher_ids:
                raise ValueError("Teacher IDs must be unique.")
            else:
                teacher_ids.add(lecture.teacher.id)
        return self


    @model_validator(mode="after")
    def remove_room_availablity_slots_outside_time_grid(self) -> Self:
        """
        removes room availibility timeslots that are negative
        or greater than the max timeslot (time_grid.n_slots)
        """
        max_slot = self.time_grid.n_slots
        for room in self.rooms:
            # invalide slots werden entfernt
            room.availability &= set(range(max_slot))
        return self


    @model_validator(mode="after")
    def remove_teacher_availablity_slots_outside_time_grid(self) -> Self:
        """
        removes teacher availibility timeslots that are negative
        or greater than the max timeslot (time_grid.n_slots)
        """
        max_slot = self.time_grid.n_slots
        for lecture in self.lectures:
            teacher = lecture.teacher
            # invalide slots werden entfernt
            teacher.availability &= set(range(max_slot))
        return self


    @model_validator(mode="after")
    def validate_max_lecture_duration(self) -> Self:
        for lecture in self.lectures:
            if lecture.duration > self.time_grid.slots_per_day:
                raise ValueError(
                    f"""Lecture [{lecture.name}] has invalid duration value:
                    \n{lecture.duration} exceeds the daily amount of timeslots [{self.time_grid.slots_per_day}]"""
                )
        return self