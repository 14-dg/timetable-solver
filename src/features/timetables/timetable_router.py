from fastapi import APIRouter

from features.timetables.schemas.timetable_task_request import TimetableTaskRequest
from features.timetables.schemas.timetable_task_status import TimetableTaskStatus

timetable_router = APIRouter(
    prefix="/timetable",
    tags=["TIMETABLE_SOLVER"]
)

@timetable_router.post(path="/")
async def solve_timetable(task_request: TimetableTaskRequest):
    pass


@timetable_router.get(path="/")
async def get_all_tasks():
    pass


@timetable_router.get(path="/{task_id}")
async def get_status() -> TimetableTaskStatus:
    pass


@timetable_router.get(path="/{task_id}/solutions")
async def get_solutions():
    pass


@timetable_router.delete(path="/{task_id}")
async def cancel_task():
    pass