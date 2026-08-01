import random
import pandas as pd
from faker import Faker
from models.lecture import Lecture
from models.room import Room
from models.teacher import Teacher

class MockGenerator:

    def __init__(self):
        self.fake = Faker('de_DE')
        self.possible_intervals = self.generate_time_intervals()

    def generate_time_intervals(self):
        possible_intervals: list[pd.Interval] = []
        base_date = pd.Timestamp("2026-10-12 08:00") # Ein fiktiver Montag

        for day_offset in range(5): # Montag bis Freitag
            for hour in [8, 10, 12, 14, 16]: # Vorlesungsblöcke
                start = base_date + pd.Timedelta(days=day_offset, hours=hour - 8)
                end = start + pd.Timedelta(hours=1, minutes=30) # 90 Minuten Blöcke
                possible_intervals.append(pd.Interval(start, end, closed='both'))
        return possible_intervals

    def generate_teachers(self) -> list[Teacher]:
        teachers: list[Teacher] = []
        for i in range(1, 6): # 5 Dozenten
            # Ziehe 3 bis 6 zufällige Intervalle aus dem Pool
            random_slots = set(random.sample(self.possible_intervals, k=random.randint(3, 6)))
            teachers.append(
                Teacher(id=i, name=f"Prof. {self.fake.last_name()}", available=random_slots)
            )
        return teachers

    
    def generate_rooms(self) -> list[Room]:
        rooms: list[Room] = []
        for i in range(1, 4): # 3 Räume
            # Räume sind meistens öfter frei als Dozenten (hier 10 bis 15 Slots)
            random_slots = set(random.sample(self.possible_intervals, k=random.randint(10, 15)))
            rooms.append(
                Room(id=i, seats=random.choice([30, 60, 150, 300]), available=random_slots)
            )
        return rooms

    
    def generate_lectures(self) -> list[Lecture]:
        lectures: list[Lecture] = []
        subjects = ["Analysis", "Lineare Algebra", "Datenbanken", "Algorithmen", "IT-Recht"]
        for i, sub in enumerate(subjects, start=1):
            lectures.append(
                Lecture(id=i, name=sub, visitors=random.randint(15, 120))
            )
        return lectures

    
    def generate_mock_data(self):

        return self.generate_teachers(), self.generate_rooms(), self.generate_lectures()