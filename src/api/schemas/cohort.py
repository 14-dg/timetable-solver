from pydantic import BaseModel


class ApiCohort(BaseModel):
    id: str
    studiengang: str
    fachsemester: int