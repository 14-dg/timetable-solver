from dataclasses import dataclass


@dataclass(kw_only=True)
class Cohort:
    id: str
    studiengang: str
    fachsemester: int