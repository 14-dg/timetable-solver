import uuid
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.background_task import run_solver_background_task
from api.schemas.schema import SolveRequestPayload
from api.store import jobs_db

app = FastAPI()

SHARED_SECRET = "dev-secret"

# Dies teilt FastAPI und Swagger mit, dass wir Bearer-Tokens nutzen
security = HTTPBearer()

def check_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # HTTPBearer nimmt dir die Arbeit ab: Es prüft automatisch, ob der Header da ist, 
    # ob "Bearer " davor steht, und gibt dir in .credentials nur noch das nackte Passwort.
    if credentials.credentials != SHARED_SECRET:
        raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/health")
def health():
    """ Liveness check, no auth required """
    return {"status": "ok"}

@app.post("/solve/start", status_code=202)
async def start(
    payload: SolveRequestPayload,
    background_tasks: BackgroundTasks,
    _ = Depends(check_auth)  # <--- HIER: So wird die Auth automatisch vor dem Start geprüft
):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {"status": "queued"}
    background_tasks.add_task(run_solver_background_task, job_id, payload)

    return {"job_id": job_id, "status": "queued"}

@app.get("/solve/{job_id}")
def get_solve_status(job_id: str, auth = Depends(check_auth)) -> dict[str, Any]:
    """ Poll for job status and result """
    
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job_data = jobs_db[job_id]
    
    response = {
        "job_id": job_id,
        "status": job_data["status"]
    }
    
    if job_data["status"] in ["solved", "no_solution"]:
        response["result"] = job_data.get("result", {})
    elif job_data["status"] == "failed":
        response["error"] = job_data.get("error", "Unknown error")
        
    return response