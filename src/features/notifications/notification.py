import logging

import httpx

from core.solve.solver_task_status import SolverTaskStatus

logger = logging.getLogger(__name__)


async def send_webhook(url: str, task_status: SolverTaskStatus):
    async with httpx.AsyncClient() as client:
        try:
            response: httpx.Response = await client.post(url=url, json=task_status.model_dump())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occured on task completion webhhok.\nStatus Code: {e.response.status_code}\nError message: {e.response.text}")