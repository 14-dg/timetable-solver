from pydantic import BaseModel
from datetime import time

class GridConfigSchema(BaseModel):
    days_per_week: int = 7
    slot_duration_minutes: int = 15         # Die kleinste atomare Zeiteinheit
    day_start_time: time = time(8, 0)       # z.B. 08:00 Uhr
    day_end_time: time = time(20, 0)        # z.B. 20:00 Uhr