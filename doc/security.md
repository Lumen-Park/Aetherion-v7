# Security Architecture

Aetherion was designed with defence‑in‑depth principles from the ground up.
Every layer — sandbox, network, authentication, secrets, and audit — is hardened
for production self‑hosted deployments.

## Sandbox Execution

All AI‑generated code runs inside a gVisor (`runsc`) container by default.
The sandbox enforces:

- `--network none` (or controlled egress via Squid proxy)
- `--memory 256m`, `--cpus 0.5`, `--pids‑limit 50`
- Read‑only root filesystem with `tmpfs` for `/tmp`
- `--security-opt no-new-privileges:true`, `--cap-drop=ALL`
- Custom seccomp profile (disabled when gVisor is active)
- User namespace remapping (`--userns=host`)

Before any code reaches the container, a static analyser blocks patterns such as
`os.system`, `eval`, `exec`, `subprocess`, `socket`, and `requests`.

## Network Egress Control

When network access is required (e.g., for agents that call external APIs),
a dedicated **Squid proxy** sidecar enforces domain and CIDR allow‑lists.
Three modes are available:

| Mode | Description |
|------|-------------|
| `none` | Complete isolation (default) |
| `allow_list` | Only approved domains / CIDRs |
| `host` | Full host network (insecure – for trusted code only) |

## Authentication & Authorization

Three authentication methods are supported:

1. **API Keys** – hashed and stored in memory; configured via environment.
2. **JWT** – signed with a configurable secret; supports role assignment.
3. **OAuth2 / OIDC** – enterprise SSO with Google, GitHub, or custom providers.

Three role levels are enforced:

| Role | Permissions |
|------|-------------|
| `admin` | Full access, including human override |
| `operator` | Can run pipelines, lab experiments, view agents |
| `viewer` | Read‑only access |

When `AETHERION_REQUIRE_AUTH=false` (default for local use), the API is open.
For production, set `AETHERION_REQUIRE_AUTH=true` and configure at least one
authentication provider.

## Tamper‑Proof Audit Logging

Every human override and Council verdict is recorded in a cryptographically
chained append‑only log (`audit/audit.log`). Each entry contains:

- The SHA‑256 hash of the previous entry
- An optional RSA digital signature (if a private key is provided)
- Full event metadata (operator, task ID, reason, timestamp)

An external party can verify the log’s integrity using the public key and the
`verify()` method in `utils/tamper_log.py`.

## Secret Management

Sensitive values (SMTP passwords, API keys) can be stored encrypted in `.env`.
The `SecretsManager` uses Fernet symmetric encryption with a key derived from a
master password via PBKDF2 (`AETHERION_MASTER_KEY`). Encrypted values have the
format `ENC[base64‑encoded‑ciphertext]`.

## Rate Limiting

A FastAPI middleware applies a per‑IP rate limit (default 30 requests/minute).
Exceeding the limit returns HTTP 429. The limit is configurable via
`RATE_LIMIT_REQUESTS_PER_MINUTE`.

## Health Probes

The API exposes two endpoints for orchestration:

- `/health/live` – returns 200 if the process is alive.
- `/health/ready` – checks Ollama and ChromaDB connectivity; returns 503 if either is down.

These probes are used by the Kubernetes deployment manifest and Docker Compose
health checks.

## Reporting Vulnerabilities

Please see [SECURITY.md](../SECURITY.md) for instructions on responsible
disclosure.
