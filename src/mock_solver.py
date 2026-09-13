"""
================================================================================
MOCK SOLVER — Testservice für die Supabase Edge Function `run-solver`
================================================================================

ZWECK
-----
Dieser Mock simuliert die Python-FastAPI des echten Timetable-Solvers, damit
die Edge Function `run-solver` lokal End-to-End getestet werden kann, ohne
dass der echte Solver-Code fertig ist. Der Mock implementiert genau die drei
Endpunkte aus der CONTRACT.md:

    GET  /health        → {"status": "ok"}
    POST /solve/start   → {"job_id": "<uuid>", "status": "queued"}
    GET  /solve/{id}    → beim ersten Poll: "running"
                          beim zweiten Poll: "solved" mit Mock-Result

Der Mock ändert keine Daten in der Datenbank. Er antwortet nur mit einem
leeren Vorschlag (`proposed_changes: []`), aber einem gültigen `score`.


--------------------------------------------------------------------------------
1. MOCK STARTEN
--------------------------------------------------------------------------------

Vom Repo-Root des Solver-Projekts (dort, wo diese Datei liegt):

    pip install fastapi uvicorn        # nur beim ersten Mal nötig
    uvicorn mock_solver:app --host 0.0.0.0 --port 8000

Wichtig ist `--host 0.0.0.0`, damit der Container der Edge Function auf den
Mock zugreifen kann (nicht nur localhost).

Erwartete Ausgabe:

    INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)


--------------------------------------------------------------------------------
2. MOCK DIREKT TESTEN (ohne Edge Function)
--------------------------------------------------------------------------------

Der Mock prüft den Shared Secret im `Authorization`-Header. Der erwartete
Wert ist unten in der Konstante `SECRET` gesetzt (Standard: "dev-secret").

Health-Check (kein Secret nötig):

    curl http://127.0.0.1:8000/health
    → {"status":"ok"}

Solve-Job starten:

    curl -X POST http://127.0.0.1:8000/solve/start \
      -H "Authorization: Bearer dev-secret" \
      -H "Content-Type: application/json" \
      -d '{"dummy": true}'
    → {"job_id":"<uuid>","status":"queued"}

Job-Status pollen (zweimal aufrufen, um "solved" zu sehen):

    curl http://127.0.0.1:8000/solve/<uuid> \
      -H "Authorization: Bearer dev-secret"
    → 1. Aufruf: {"job_id":"...","status":"running"}
    → 2. Aufruf: {"job_id":"...","status":"solved","result":{...}}


--------------------------------------------------------------------------------
3. EDGE FUNCTION LOKAL TESTEN
--------------------------------------------------------------------------------

Voraussetzungen:
    a) Der Mock läuft auf Port 8000 (siehe Schritt 1).
    b) Die Migrationen sind angewendet:  npx supabase migration up
    c) Die Datei `supabase/functions/.env.local` existiert mit:

        SOLVER_URL=http://host.docker.internal:8000
        SOLVER_SHARED_SECRET=dev-secret

       Hinweis: `host.docker.internal` ist auf Linux nicht immer verfügbar.
       Falls die Edge Function den Mock nicht erreicht, stattdessen die
       LAN-IP des Rechners verwenden:

        SOLVER_URL=http://192.168.x.y:8000     (per `hostname -I` ermitteln)

       Die Werte `SUPABASE_URL` und `SUPABASE_SERVICE_ROLE_KEY` NICHT in
       `.env.local` eintragen — Supabase CLI setzt sie automatisch und
       ignoriert eigene Werte mit `SUPABASE_`-Präfix.

    d) Edge Function starten (in einem zweiten Terminal, aus dem Repo-Root):

        npx supabase functions serve run-solver --no-verify-jwt \
          --env-file supabase/functions/.env.local

       Die Function läuft dann unter:
        http://127.0.0.1:54321/functions/v1/run-solver


--------------------------------------------------------------------------------
4. ADMIN-JWT BESORGEN
--------------------------------------------------------------------------------

Die Edge Function akzeptiert nur Admins. Das JWT muss also zu einem User
gehören, dessen Profil `role = 'admin'` hat.

    a) Anon-Key aus `npx supabase status` entnehmen.

    b) Token anfordern:

        curl -X POST "http://127.0.0.1:54321/auth/v1/token?grant_type=password" \
          -H "apikey: <anon-key>" \
          -H "Content-Type: application/json" \
          -d '{"email":"admin@muster-uni.de","password":"<passwort>"}'

       Das zurückgegebene `access_token` ist das JWT.

       Das Passwort steht im Seed-Skript `scripts/seed_general_users.ts`.
       Falls kein User existiert: `npx supabase db reset` und die Seed-
       Skripte erneut ausführen.

    c) JWT in eine Shell-Variable laden (der Kürze halber):

        JWT="eyJhbGci..."


--------------------------------------------------------------------------------
5. EDGE FUNCTION AUFRUFEN
--------------------------------------------------------------------------------

Semester-ID und Studiengang-ID müssen in der lokalen DB existieren.
Prüfen mit:

    psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
      -c "SELECT id, name FROM semesters;" \
      -c "SELECT id, name FROM courses_of_study;"

Dann den Solver-Lauf auslösen:

    curl -X POST "http://127.0.0.1:54321/functions/v1/run-solver" \
      -H "Authorization: Bearer $JWT" \
      -H "Content-Type: application/json" \
      -d '{"semester_id": <id>, "target_course_of_study_ids": [<id>]}'

Erwartete Antwort bei Erfolg (Mock):

    {"proposal_id":"<uuid>","status":"pending_review","score":0.87}

Prüfen, dass der Vorschlag in der DB angekommen ist:

    psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
      -c "SELECT id, semester_id, status, score FROM schedule_proposals;"


--------------------------------------------------------------------------------
6. HÄUFIGE FEHLERQUELLEN
--------------------------------------------------------------------------------

"unauthorized"
    → JWT fehlt, abgelaufen oder falsch. Neu über Schritt 4 holen.
    → Der User ist kein Admin (Profil-Rolle prüfen).

"profile_not_found"
    → Der User hat kein Profil in der lokalen DB. Seed-Skript ausführen.

"validation_error"
    → Body enthält nicht `semester_id` und `target_course_of_study_ids`.

"proposal_insert_failed" ... semester_id_fkey
    → Die angegebene Semester-ID existiert nicht. IDs per psql prüfen.

"solver_network_error"
    → Die Edge Function erreicht den Mock nicht. `SOLVER_URL` prüfen:
        - `host.docker.internal` funktioniert nicht auf Linux.
        - LAN-IP verwenden (`hostname -I`).
        - `--host 0.0.0.0` beim Uvicorn-Start setzen.

"solver_start_failed" mit 401
    → Der Shared Secret zwischen Edge Function und Mock stimmt nicht.
       `SOLVER_SHARED_SECRET` in `.env.local` muss `SECRET` in dieser Datei
       entsprechen.

"Env name cannot start with SUPABASE_"
    → Harmlose Warnung. Die betroffenen Variablen werden automatisch von
       Supabase CLI bereitgestellt und dürfen nicht in `.env.local` stehen.


--------------------------------------------------------------------------------
7. PRODUKTIVBETRIEB (Render)
--------------------------------------------------------------------------------

Für einen echten Test gegen den Render-Deployment:

    npx supabase functions deploy run-solver --no-verify-jwt
    npx supabase secrets set SOLVER_URL=https://<render-url>.onrender.com
    npx supabase secrets set SOLVER_SHARED_SECRET=<secret>

Danach kann der Aufruf über die Produktiv-URL des Supabase-Projekts
erfolgen:

    curl -X POST "https://<project-ref>.supabase.co/functions/v1/run-solver" \
      -H "Authorization: Bearer <produktiv-jwt>" \
      -H "Content-Type: application/json" \
      -d '{"semester_id": <id>, "target_course_of_study_ids": [<id>]}'


================================================================================
Dieser Mock ist bewusst minimal gehalten. Sobald der echte Solver läuft,
kann diese Datei gelöscht oder als Referenz für das Request/Response-Format
aufbewahrt werden.
================================================================================
"""

from fastapi import FastAPI, Request, HTTPException, Header
import uuid

app = FastAPI()
JOBS: dict = {}

SECRET = "dev-secret"

def check_auth(auth: str | None):
    if auth != f"Bearer {SECRET}":
        raise HTTPException(status_code=401)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/solve/start")
async def start(request: Request, authorization: str | None = Header(None)):
    check_auth(authorization)
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"polls": 0}
    return {"job_id": job_id, "status": "queued"}

@app.get("/solve/{job_id}")
def poll(job_id: str, authorization: str | None = Header(None)):
    check_auth(authorization)
    if job_id not in JOBS:
        raise HTTPException(status_code=404)
    JOBS[job_id]["polls"] += 1
    if JOBS[job_id]["polls"] < 2:
        return {"job_id": job_id, "status": "running"}
    return {
        "job_id": job_id,
        "status": "solved",
        "result": {
            "proposed_changes": [],
            "unresolved": [],
            "violations": [],
            "score": 0.87
        }
    }