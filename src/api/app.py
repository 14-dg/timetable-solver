from typing import Any

from fastapi import BackgroundTasks, FastAPI, HTTPException, Header
import uuid
from api.store import jobs_db
from api.background_task import run_solver_background_task
from api.schemas.schema import SolveRequestPayload

app = FastAPI()
JOBS: dict[str, Any] = {}

SHARED_SECRET = "dev-secret"

def check_auth(auth: str | None):
    if auth != f"Bearer {SHARED_SECRET}":
        raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/health")
def health():
    """ Liveness check, no auth required """
    return {"status": "ok"}

@app.post("/solve/start", status_code=202)
async def start(
    payload: SolveRequestPayload,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(None)
):
    check_auth(authorization)
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {"status": "queued"}
    background_tasks.add_task(run_solver_background_task, job_id, payload)

    return {"job_id": job_id, "status": "queued"}

@app.get("/solve/{job_id}")
def get_solve_status(job_id: str, authorization: str | None = Header(None)) -> dict[str, Any]:
    """ Poll for job status and result[cite: 20] """
    check_auth(authorization)
        
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_data = jobs_db[job_id]
    
    # Die Basis-Antwort
    response = {
        "job_id": job_id,
        "status": job_data["status"]
    }
    
    # Je nach Status weitere Felder anhängen
    if job_data["status"] in ["solved", "no_solution"]:
        response["result"] = job_data.get("result", {})
    elif job_data["status"] == "failed":
        response["error"] = job_data.get("error", "Unknown error")
        
    return response