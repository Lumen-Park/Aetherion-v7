# Aetherion v7 — Full Codebase Audit: Bug Catalog (Final)

## P0 — CRITICAL (Blocks startup or causes crashes)

| ID | File | Bug Description | Fix |
|---|---|---|---|
| P0-1 | `dashboard/vite.config.js` | Missing — no Vite config file exists in dashboard dir. Build and dev server will fail without it. | Create vite.config.js with React plugin and proxy |
| P0-2 | `dashboard/postcss.config.js` | Missing — PostCSS config required for Tailwind CSS processing. Build will fail. | Create postcss.config.js with tailwind and autoprefixer plugins |
| P0-3 | `api/routers/council.py` | Double-prefix: router has `prefix="/constitution"` but included with `prefix="/api/council"`. Results in `/api/council/constitution/{ws}` instead of `/api/council/{ws}`. Also tagged as "Constitution" but should be "Council". | Remove prefix from router definition (make it `APIRouter()`) and change tags to "Council" |
| P0-4 | `api/routers/oauth_routes.py` | Double-prefix: router has `prefix="/oauth"` but included with `prefix="/api/oauth"`. Results in `/api/oauth/oauth/login/{provider}` instead of `/api/oauth/login/{provider}`. | Remove prefix from router definition |
| P0-5 | `api/routers/constitution.py` + `api/routers/council.py` | Both routers use `prefix="/constitution"` and `tags=["Constitution"]`. They have overlapping routes at `/{workspace_id}` GET and PUT — FastAPI will silently overwrite one with the other. | Rename council.py to use `/council` prefix and "Council" tags |
| P0-6 | `api/routers/compliance.py` + `api/routers/constitution.py` | Both routers use `prefix="/compliance"` and `prefix="/constitution"` respectively, included with `prefix="/api"`. Compliance has `/consent/{workspace_id}` GET and POST — both map to same path. | Verify path uniqueness |
| P0-7 | `aetherion-mobile/src/api/client.js` | Leading ` ```javascript ` code block marker on line 1 — invalid JavaScript syntax | Remove the opening code fence |
| P0-8 | `aetherion-mobile/App.js` | Leading ` ```jsx ` code block marker on line 1 — invalid JavaScript syntax | Remove the opening code fence |
| P0-9 | `aetherion-mobile/src/screens/*.js` (all 6 files) | Leading ` ```jsx ` code block markers — invalid JavaScript syntax | Remove from all files |
| P0-10 | `aetherion-desktop/main.js` | Leading ` ```javascript ` code block marker — invalid JavaScript syntax | Remove the opening code fence |
| P0-11 | `aetherion-desktop/preload.js` | Leading ` ```javascript ` code block marker — invalid JavaScript syntax | Remove the opening code fence |
| P0-12 | `api/routers/oauth_routes.py` | `RedirectResponse` imported but never used (dead import) | Remove the import |

## P1 — HIGH (Functional errors, incorrect behavior)

| ID | File | Bug Description | Fix |
|---|---|---|---|
| P1-1 | `core/protocol.py` | `LLMWrapper` reads `OPENAI_API_BASE` env var, but `.env` defines `OLLAMA_HOST`. Mismatch causes LLM calls to fail when Ollama is not at the expected URL. | Add fallback: try `OLLAMA_HOST` then `OPENAI_API_BASE` |
| P1-2 | `api/routers/tasks.py` | `run_pipeline` passes `user.get("auth_token")` to Celery but the `user` dict from `get_current_user` never contains `auth_token` — it only has `role`, `sub`, `email`, `name`, `provider`, or `auth_disabled`. The token is lost. | Change to pass `user` dict or extract token differently |
| P1-3 | `api/routers/tasks.py` | `run_lab` same issue — `user.get("auth_token")` returns None. | Same fix as P1-2 |
| P1-4 | `api/routers/tasks.py` | `accept_override` passes `user.get("auth_token")` — same None issue. | Same fix as P1-2 |
| P1-5 | `main.py` | `mission_mode()` calls `scout.search_github_issues()` but `ScoutAgent` requires authenticated GitHub API calls which may fail without token. | Add error handling |
| P1-6 | `mission/mission_agent.py` | `ScoutAgent.search_github_issues()` uses GitHub API without any auth — rate-limited to 60 requests/hour unauthenticated, will fail under load. | Add optional GitHub token support |
| P1-7 | `agents/council/council.py` | The `Security` judge's absolute veto check: the code checks `v.verdict == Verdict.REJECT` which is correct, BUT the veto only fires for `Verdict.REJECT`, not for low scores. The test expects `Verdict.REJECT` from Security judge. | This is actually correct — the tests confirm the behavior |
| P1-8 | `api/routers/council.py` | Router paths overlap with `constitution.py` at `/{workspace_id}` GET and PUT. Since both are included with `prefix="/api"`, FastAPI will register the last one's route and overwrite the first. | Fix the prefix to `/council` for council.py |
| P1-9 | `dashboard/src/components/Override.jsx` | Override form doesn't send auth token with the request. The backend `accept_override` requires authentication. | Add auth header from stored token |

## P2 — MEDIUM (Logic errors, quality issues)

| ID | File | Bug Description | Fix |
|---|---|---|---|
| P2-1 | `api/middleware/rate_limit.py` | Rate limiter uses in-memory dict, not shared across Uvicorn workers. In production with multiple workers, rate limit is per-worker not global. | Use Redis for distributed rate limiting |
| P2-2 | `dashboard/package.json` | No `"proxy"` field for dev server. API calls from port 3000 to port 8000 will fail in development mode. | Add `"proxy": "http://localhost:8000"` |
| P2-3 | `dashboard/src/components/AgentCatalog.jsx` | Race condition: `toggleAgent` sends stale state to backend. Multiple rapid toggles can lose updates. | Re-read from server after toggle |
| P2-4 | `dashboard/src/api/client.js` | `tasksAPI.runPipeline(goal, mode, key)` passes mode but the backend `TaskRequest` model has `goal` and `mode` fields. The POST body sends both — this is actually correct. | No fix needed — confirmed working |
| P2-5 | `aetherion-mobile/src/api/client.js` | `tasksAPI.runPipeline(goal, idempotencyKey)` only sends `{ goal }` — missing `mode`. Backend defaults to `"pipeline"` so it works but is implicit. | Add `mode` parameter |
| P2-6 | `agents/interfaces/interfaces.py` | `EmailSender.send_report()` logs warning about plaintext SMTP password but continues execution. Should be a hard failure for remote SMTP. | Raise error for non-localhost remote SMTP |
| P2-7 | `api/routers/tasks.py` | No idempotency key handling. The `require_idempotency_key` function exists in `api/idempotency.py` but is never used in the tasks router. Duplicate submissions can create duplicate tasks. | Add idempotency middleware to tasks endpoints |
| P2-8 | `core/auth.py` | `authenticate` method: when auth is disabled, it returns `{"role": "admin", "auth_disabled": True}` which grants admin access to everyone. This is intentional but should be documented as a security risk. | Add warning comment |
| P2-9 | `utils/sandbox.py` | `--userns=host` flag is set by default which disables user namespace isolation, undermining the security model. | Default to `--userns=keep-id` or remove the flag |
| P2-10 | `api/tasks/celery_tasks.py` | `run_lab_task` on resume path hardcodes `PipelineMode.STANDARD` instead of using the original mode. | Store and restore mode |

## P3 — LOW (Cosmetic, documentation, minor)

| ID | File | Bug Description | Fix |
|---|---|---|---|
| P3-1 | `utils/logger.py` | No log rotation — logs accumulate indefinitely in a single file. | Add max-size rotation |
| P3-2 | `agents/improvement/self_improve.py` | `RefactorArchitect.propose_changes` may apply malformed LLM output as code diff, potentially corrupting the codebase. | Add diff validation before applying |
| P3-3 | `utils/egress_proxy.py` | Squid proxy config written to `/tmp` which may be cleaned by OS before proxy finishes. | Use a dedicated temp dir with longer lifetime |
| P3-4 | `docker-compose.yml` | Agent microservices not included in compose file — `generate_agent_services.py` script must be run manually and output appended. | Include generated services in compose or add auto-generation |
| P3-5 | `api/__init__.py` | `__all__` doesn't include `"compliance"` but compliance router is imported and used. | Add to `__all__` |
