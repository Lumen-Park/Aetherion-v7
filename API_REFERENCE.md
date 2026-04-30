# Aetherion API Reference v3.4.0

The Aetherion REST API is served by FastAPI. Full interactive documentation (Swagger UI) is available at
`/docs` when the server is running.

All endpoints are prefixed with `/api`. Authentication is required when
`AETHERION_REQUIRE_AUTH=true` is set; otherwise the API runs in open mode.

## Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate and receive a JWT |
| GET  | `/api/auth/providers` | List available OAuth2/OIDC providers |

### POST `/api/auth/login`

Request body (JSON):
```json
{
  "provider": "google",        // OAuth2 login (with code)
  "code": "auth_code_from_redirect"
}
```

or

```json
{
  "api_key": "your-api-key"    // API key login
}
```

Response (200):

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "admin",
  "user": { "email": "user@example.com", "role": "admin" }
}
```

All subsequent requests must include the JWT in the Authorization header:

```
Authorization: Bearer eyJ...
```

---

Tasks

Run a Pipeline

POST /api/tasks/pipeline

Required header: Idempotency‑Key (a unique client‑generated key, 8‑256 chars)

Request body:

```json
{
  "goal": "Write a function to check if a number is prime",
  "mode": "pipeline"       // optional, default "pipeline"
}
```

Response (200):

```json
{
  "task_id": "task_1712345678",
  "status": "queued",
  "cached": false
}
```

If the same Idempotency‑Key is used again, the previously queued job ID is returned
and cached will be true.

Get Pipeline Status

GET /api/tasks/pipeline/{task_id}

Response (200):

```json
{
  "task_id": "task_1712345678",
  "status": "completed",
  "council_verdict": {
    "verdict": "APPROVED",
    "score": 8.5,
    "votes": [ ... ]
  },
  "result": "def is_prime(n): ..."
}
```

Real‑time Progress

GET /api/tasks/pipeline/{task_id}/progress

Response (200):

```json
{
  "state": "RESEARCHING",
  "elapsed": 12.3,
  "updated_at": 1712345680.0,
  "estimated_remaining": 85,
  "progress_percent": 34
}
```

Run an Experiment (Lab Mode)

POST /api/tasks/lab

Same request body as /pipeline (goal and mode=lab). Also requires Idempotency‑Key.

Response (200):

```json
{
  "task_id": "task_1712345689",
  "status": "queued",
  "cached": false
}
```

Status and progress can be polled at /api/tasks/lab/{task_id}.

Human Override

POST /api/tasks/override/{task_id}?reason=Accepted%20after%20review

Requires admin role.

Response (200):

```json
{
  "status": "success",
  "task_id": "task_1712345678"
}
```

---

Agents

Method Endpoint Description
GET /api/agents List all 70+ agents
GET /api/agents/colleges List all colleges and their agents

GET /api/agents

Response (200):

```json
{
  "agents": [
    {
      "name": "PhysicistAgent",
      "college": "Natural Sciences",
      "expertise": "Physics (classical, quantum, thermodynamics)"
    },
    ...
  ]
}
```

Agent Catalog (Workspace‑specific enable/disable)

Method Endpoint Description
GET /api/agent‑catalog/{workspace_id} Get enable/disable states
PUT /api/agent‑catalog/{workspace_id} Update states

Requires admin role.

PUT body:

```json
{
  "agents": {
    "PhysicistAgent": true,
    "ChemistAgent": false
  }
}
```

---

Council

Method Endpoint Description
GET /api/council/stats Approval rate, average score
GET /api/council/judges List the 7 judges

---

Constitution (Workspace Governance)

Method Endpoint Description
GET /api/constitution/{workspace_id} Current constitution
PUT /api/constitution/{workspace_id} Update constitution
GET /api/constitution/{workspace_id}/audit Constitution change history

Requires admin role.

PUT body:

```json
{
  "judges": {
    "Security": { "prompt": "...", "enabled": true, "weight": 1.0 },
    ...
  },
  "thresholds": {
    "approved": 7.5,
    "revision": 5.0
  }
}
```

POST /api/constitution/preview – test a constitution against sample output.

Request body:

```json
{
  "output": "def is_prime(n): ...",
  "goal": "Write a prime checker",
  "constitution": { ... }
}
```

---

Compliance (GDPR / CCPA)

Method Endpoint Description
GET /api/compliance/export/{workspace_id} Download all workspace data
DELETE /api/compliance/delete/{workspace_id} Permanently delete workspace
POST /api/compliance/consent/{workspace_id}?consented=true Record consent
GET /api/compliance/consent/{workspace_id} Check consent status

All require admin role.

---

WebSocket

Real‑time Deliberation Stream

Connect to ws://<host>/api/ws/deliberation. The server sends messages like:

```json
{
  "type": "vote",
  "judge": "Security",
  "verdict": "REJECT",
  "score": 2.0
}
```

---

Health Probes

Endpoint Purpose Response
/health/live Liveness {"status": "alive"}
/health/ready Readiness {"status": "ready"} or 503

---

Observability Metrics

GET /api/metrics returns Prometheus‑format metrics.

---

Error Responses

All errors follow a standard format:

```json
{
  "detail": "Error description"
}
```

Status Meaning
400 Bad request (invalid goal, missing fields)
401 Authentication required
403 Insufficient role permissions
404 Task or workspace not found
429 Rate limit exceeded
503 Service unavailable (Ollama/ChromaDB down)

---

Rate Limiting

Default: 30 requests per minute per IP. Exceeding this returns 429 Too Many Requests.

Idempotency

For POST /api/tasks/pipeline and POST /api/tasks/lab, include an Idempotency‑Key header
to safely retry without creating duplicate tasks.

```
