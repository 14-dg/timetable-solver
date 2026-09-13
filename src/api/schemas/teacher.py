from pydantic import BaseModel

class LecturerSchema(BaseModel):
    id: int
    name: str