```markdown
# CONTRACT.md — Timetable Solver API

Version: 0.2 (draft)
Owner: myroomfinder (Daniel Graef)
Consumer: `timetable-solver` service

## 1. Purpose

This document defines the interface between the myroomfinder Supabase Edge
Function (`run-solver`) and the external `timetable-solver` service. The
solver receives the current scheduling state for one institution and returns
a **proposed** schedule. It never writes to the myroomfinder database
directly — all proposals are reviewed and applied by an admin (see #183).

## 2. Architecture

```
Frontend (app.myroomfinder.de)
   │  HTTPS + JWT (Supabase Auth)
   ▼
Supabase Edge Function: run-solver
   │  HTTPS + shared secret (Authorization: Bearer <secret>)
   ▼
timetable-solver (FastAPI, own deployment on Render free tier)
```

- `run-solver` collects data from Postgres, calls the solver, and writes the
  result into `schedule_proposals` (see §8). It never applies the proposal.
- The solver is asynchronous by design (see §5). It must not require the
  caller to hold a connection open longer than a few seconds.
- The solver holds no state of its own beyond the lifetime of a job. All
  configuration (constraints, weights) is sent in the request, not stored in
  the solver repo.

## 3. Granularity: timeslot, not lecture

**This is the most important modeling decision in this contract.** A
`lecture` in myroomfinder is a course entity (e.g. "Mathematik 1") that can
have **multiple** `lecture_timeslots` — one per weekly recurring slot. Room,
lecturer assignment, and the online flag all live on the **timeslot**, not on
the lecture:

- `lecture_timeslots.room_id`, `.is_online`, `.day_of_week`, `.start_time`,
  `.end_time`, `.week_skip` — per timeslot.
- `timeslot_lecturers` (join table) — lecturer assignment per timeslot, not
  per lecture. A timeslot can have more than one lecturer.

The solver therefore operates on **`lecture_timeslots`** as the schedulable
unit. A `lecture_id` groups timeslots together for informational purposes
(title, course-of-study links, fachsemester) but is not itself something the
solver moves.

**Pinning:** `lecture_timeslots.is_solver_pinned boolean NOT NULL DEFAULT false`
marks a timeslot that the solver must not move. Admins pin a timeslot when
they want to freeze it regardless of solver optimisation. Unpinned timeslots
are free to be relocated by the solver.

## 4. Authentication

- The solver is **not publicly documented or linked**; it is reachable only
  from the `run-solver` Edge Function.
- Every request carries `Authorization: Bearer <shared-secret>`. The secret
  is an environment variable on both sides, rotated manually for now.
- The solver returns `401` if the header is missing or wrong, before
  touching the payload.
- No end-user JWT ever reaches the solver — auth and row-level security are
  fully handled on the Supabase side before the request is built.

## 5. Endpoints

### `GET /health`

Liveness check, no auth required.

```json
{ "status": "ok" }
```

### `POST /solve/start`

Starts an asynchronous solve job. Must return immediately (target: < 1s).
The solver enqueues the work internally and returns a job id.

Request body: see §6.

Response (`202 Accepted`):

```json
{
  "job_id": "b7e2b8b0-...-uuid",
  "status": "queued"
}
```

### `GET /solve/{job_id}`

Poll for job status and result. The frontend/edge function polls this on an
interval (suggested: every 2–3s, with backoff after ~30s).

Response while running:

```json
{
  "job_id": "b7e2b8b0-...-uuid",
  "status": "running",
  "progress": 0.42
}
```

`progress` is optional — omit it if the solver has no meaningful way to
estimate it; the caller must not depend on it being present.

Response when done — see §7 for the full result schema:

```json
{
  "job_id": "b7e2b8b0-...-uuid",
  "status": "solved",
  "result": { "...": "see §7" }
}
```

Terminal `status` values: `solved`, `no_solution`, `failed`.

- `solved` — a schedule was produced (`result.score` indicates quality; it
  may still contain `unresolved` entries or soft-constraint `violations`).
- `no_solution` — the solver determined no feasible schedule exists under
  hard constraints. `result.unresolved` should list what blocked it.
- `failed` — internal error. `error` (string) must be set; `result` may be
  omitted.

### Job lifetime

Jobs and their results should be retained by the solver for at least 24h
after completion (in case a poll is delayed) but do not need permanent
storage — the myroomfinder side is the system of record once it copies the
result into `schedule_proposals`.

## 6. Request schema (`POST /solve/start`)

```json
{
  "institution_id": "uuid",
  "semester": {
    "id": 3,
    "name": "WiSe 2026/27",
    "start_date": "2026-10-01",
    "end_date": "2027-01-31"
  },
  "target_course_of_study_ids": [1, 2],

  "rooms": [
    {
      "id": 5,
      "name": "HS1",
      "seats": 200,
      "room_type_id": "hoersaal",
      "equipment_ids": ["beamer", "whiteboard"],
      "is_locked": false,
      "accessible": true
    }
  ],

  "lecturers": [
    { "id": 12, "name": "Prof. Müller", "department": "F07" }
  ],

  "lecture_timeslots": [
    {
      "timeslot_id": 42,
      "lecture_id": 7,
      "lecture_title": "Mathematik 1",
      "lecture_type": "Vorlesung",
      "course_of_study_ids": [1, 2],
      "fachsemester": [1],
      "lecturer_ids": [12],
      "room_id": 5,
      "day_of_week": 1,
      "start_time": "08:00",
      "end_time": "09:45",
      "week_skip": 0,
      "is_online": false,
      "is_solver_pinned": false
    }
  ],

  "lecturer_availability": [
    {
      "lecturer_id": 12,
      "day_of_week": 1,
      "start_time": "08:00",
      "end_time": "10:00",
      "constraint_type": "hard"
    }
  ],

  "blocked_room_bookings": [
    {
      "room_id": 5,
      "start_time": "2026-10-15T14:00:00Z",
      "end_time": "2026-10-15T16:00:00Z"
    }
  ],

  "constraints": {
    "max_teaching_days_per_week": 5,
    "max_consecutive_hours": 4,
    "break_after_hours": 2,
    "break_duration_minutes": 60,
    "min_break_minutes_between_events": 15,
    "cluster_preference_weight": 0.5,
    "prefer_morning_weight": 0.0,

    "config": {
      "10_room_equipment":     { "enabled": true,  "mode": "hard" },
      "11_room_seats":         { "enabled": true,  "mode": "hard" },
      "20_idle_gaps":          { "enabled": true,  "weight": 1.0, "weight_by_attendees": false },
      "30_edge_hours":         { "enabled": true,  "weight": 1.0, "weight_by_attendees": false },
      "40_room_consistency":   { "enabled": true,  "weight": 0.5 },
      "50_mandatory_overlap":  { "enabled": true,  "weight": 0.7 },
      "60_elective_overlap":   { "enabled": true,  "weight": 0.7 },
      "70_preferred_times":    { "enabled": true,  "weight": 0.5 },
      "80_max_teaching_hours": { "enabled": true,  "mode": "hard" },
      "90_walking_times":      { "enabled": false }
    }
  },

  "lecture_type_workload": {
    "Vorlesung": 1.0,
    "Uebung": 0.7,
    "Praktikum": 1.2
  }
}
```

### Field notes

| Field | Source table | Notes |
|---|---|---|
| `rooms[]` | `rooms`, `room_equipment` | `equipment_ids` flattened from the join table |
| `lecturers[]` | `lecturers` | Only `id`/`name`/`department` — solver does not need contact info |
| `lecture_timeslots[]` | `lecture_timeslots`, `lectures`, `timeslot_lecturers`, `lecture_courses`, `lecture_fachsemester` | Denormalized/joined by the Edge Function before sending |
| `lecturer_availability[]` | `lecturer_availability` | `constraint_type` values: `hard` / `soft` |
| `blocked_room_bookings[]` | `bookings` | External one-off bookings that block a room regardless of the regular timetable |
| `constraints` | `scheduling_config` (#179) | One row per institution |
| `constraints.config` | `scheduling_config.constraint_config` (jsonb) | See §6.1 for the exact schema |
| `lecture_type_workload` | `lecture_type_workload` (#179) | Keyed by the `lecture_type` enum |

### 6.1 Conventions

- **`day_of_week`:** `1 = Monday` … `7 = Sunday` (ISO).
- **Timezone:** All timestamps in the payload are UTC (they are
  `timestamptz` in Postgres; serialise with `Z` suffix).
- **`constraint_type`:** `hard` or `soft`. A `hard` availability entry means
  the lecturer must not be scheduled in that window; `soft` means the solver
  should prefer not to.
- **`constraint_config`:** Each key is optional. If a key is missing, the
  solver MUST assume `{ "enabled": true, "mode": "hard", "weight": 1.0 }` as
  a safe default. Do not raise on unknown or missing keys.
- **Pinning:** `is_solver_pinned = true` means the solver must not change
  `day_of_week`, `start_time`, `end_time`, `room_id`, or `lecturer_ids` for
  that timeslot. The solver may still consider the timeslot for conflict
  detection.

### 6.2 Must-constraints (never switchable)

These are always enforced by the solver. They are not part of
`constraint_config` and cannot be turned off:

- All lecturers of a timeslot must be available at the scheduled time.
- No lecturer may be double-booked at the same time.
- A room may host at most one timeslot at the same time.
- **Kohorten-Schutz:** Mandatory lectures of the same (course of study,
  fachsemester) must not overlap.
- Each elective lecture must be schedulable in at least one fachsemester
  without overlapping a mandatory lecture of that same (course, fachsemester).

If any of these cannot be satisfied, the job should return `no_solution`
with `unresolved` entries explaining which constraint blocked the schedule.

## 7. Response / result schema (§5, embedded in `GET /solve/{job_id}`)

```json
{
  "proposed_changes": [
    {
      "change_type": "move",
      "timeslot_id": 42,
      "lecture_id": 7,
      "day_of_week": 2,
      "start_time": "10:35",
      "end_time": "12:20",
      "week_skip": 0,
      "room_id": 6,
      "lecturer_ids": [12]
    },
    {
      "change_type": "new",
      "timeslot_id": null,
      "lecture_id": 9,
      "day_of_week": 3,
      "start_time": "14:00",
      "end_time": "15:45",
      "week_skip": 0,
      "room_id": 6,
      "lecturer_ids": [15]
    }
  ],
  "unresolved": [
    { "lecture_id": 99, "reason": "no_available_room" }
  ],
  "violations": [
    { "type": "soft", "rule": "prefer_morning", "timeslot_id": 42, "message": "Scheduled at 10:35, preferred morning slot" }
  ],
  "score": 0.87
}
```

### `change_type` values

- `move` — an existing `timeslot_id` is relocated. `run-solver` applies this
  as `UPDATE lecture_timeslots SET ... WHERE id = timeslot_id`.
- `new` — a new timeslot is proposed for an existing `lecture_id`.
  `timeslot_id` is `null`; `run-solver` applies this as an `INSERT`.
- `unchanged` — optional, only include if the solver wants to explicitly
  confirm a timeslot was considered and left in place. Not required.

This mirrors the existing `change_requests` table pattern already used in
the schema (jsonb `proposed_changes`, admin review, `status` field) —
`schedule_proposals` (see §8) is structured the same way on purpose so the
admin-review UI (#183) can reuse logic.

### `unresolved[]`

Anything the solver could not place at all. `reason` is a short machine-
readable code (`no_available_room`, `no_available_slot`,
`lecturer_conflict`, `cohort_overlap`, etc.) — keep this to a small fixed
vocabulary rather than free text, so the frontend can localize/display it.

### `violations[]`

Soft-constraint breaches in the returned schedule (the solver still
produced a schedule, but it isn't perfect). `type` is always `"soft"` here —
a hard-constraint breach should instead result in the affected lecture
showing up in `unresolved`, or in the whole job returning `no_solution` if
no feasible schedule exists at all.

### `score`

Float in `[0, 1]`, higher is better. Exact definition is up to the solver
(e.g. weighted sum of satisfied soft constraints) — document the formula in
the solver repo once implemented, but the contract only requires that higher
= better and it's comparable across runs for the same institution.

## 8. myroomfinder-side storage (for context, not part of the solver's job)

```
schedule_proposals
  id                 uuid PK
  institution_id     uuid FK
  semester_id        int8 FK
  requested_by       uuid FK -> profiles
  job_id             text          -- solver job id, for tracing
  request_payload    jsonb         -- what was sent to /solve/start
  result_payload     jsonb         -- the result from §7
  status             text          -- 'pending_review' | 'accepted' | 'rejected' | 'failed'
  score              float
  error_message      text
  created_at         timestamptz
  reviewed_at        timestamptz nullable
  reviewed_by        uuid nullable FK -> profiles
```

RLS: same pattern as every other table — `institution_id =
get_user_institution_id()` for SELECT, `get_user_role() = 'admin'` for
writes. Not the solver's concern, listed here only so the solver author
understands what happens to its output.

## 9. Error handling

| Status | Meaning | Body |
|---|---|---|
| `401` | Missing/invalid shared secret | `{ "error": "unauthorized" }` |
| `422` | Request failed schema validation | `{ "error": "validation_error", "details": [...] }` |
| `500` | Unhandled solver error | `{ "error": "internal_error" }` |

For `GET /solve/{job_id}` on an unknown job id: `404`.

## 10. Non-goals for v0.1

- The solver does not read from or write to Supabase directly.
- The solver does not handle multi-institution batching — one `institution_id`
  per job.
- The solver does not need to persist results beyond the 24h window in §5.4.
- Authentication beyond the shared secret (e.g. per-solver-instance keys) is
  out of scope until there is more than one solver deployment.
- Walking distances between rooms (constraint `90_walking_times`) are not
  available yet; the constraint defaults to `enabled: false` and the solver
  should ignore it unless explicitly enabled later.
- Per-lecturer overrides for max teaching hours are not modelled yet; the
  global values in `scheduling_config` apply to all lecturers.
- Allowed/preferred/forbidden rooms per lecture are not modelled yet; the
  solver treats every room as available subject to §6.2.
- Irregular unavailability (single-date blocks) for lecturers is not
  modelled yet.
- Regular availability windows for rooms are not modelled yet.

## 11. Next steps

1. Ship the `is_solver_pinned` migration on `lecture_timeslots` (§3).
2. Ship `scheduling_config` + `lecture_type_workload` + `schedule_proposals`
   migrations (#179).
3. Solver author implements `/health` and a mocked `/solve/start` +
   `/solve/{job_id}` pair returning static data, matching this schema
   exactly, and deploys it on Render free tier.
4. Build `run-solver` Edge Function against the mock.
5. Only after the mock round-trip works end-to-end: real solver logic
   (OR-Tools CP-SAT).
6. Follow-up data-model extensions tracked separately in #217:
   allowed/preferred/forbidden rooms, lecturer irregular unavailability,
   room regular availability, walking distances.
```