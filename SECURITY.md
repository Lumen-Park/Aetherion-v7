# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version        | Supported          |
|----------------|--------------------|
| v3.4.x (latest) | :white_check_mark: |
| v3.3.x          | :white_check_mark: |
| v3.2.x          | :x:                |
| < v3.2          | :x:                |

## Reporting a Vulnerability

We take the security of Aetherion seriously. If you discover a security vulnerability, we appreciate your help in disclosing it to us responsibly.

**Please do not open a public GitHub issue.** Instead, email us at:

>ashpeterpark@gmail.com

(If you do not have a dedicated email, replace with your personal/project email or a private reporting mechanism.)

### What to Include

- A clear description of the vulnerability
- Steps to reproduce the issue
- The affected component(s) (e.g., sandbox, Council, API, dashboard)
- Any potential impact or exploit scenarios
- Your suggestions for remediation (if any)

### What to Expect

- **Acknowledgment:** Within 48 hours of receiving your report.
- **Investigation:** We will triage and validate the issue.
- **Resolution:** A fix will be developed and released as a patch to supported versions.
- **Credit:** With your permission, we will publicly acknowledge your contribution in the release notes.

## Security Best Practices for Users

Aetherion is designed with defence‑in‑depth security, but proper configuration is essential:

1. **Always enable gVisor** (`SANDBOX_RUNTIME=runsc`) for maximum container isolation.
2. **Set up network egress controls** (`SANDBOX_NETWORK_MODE=allow_list`) if agents need external access.
3. **Use encrypted secrets** via the included `SecretsManager` — never store plain‑text credentials in `.env`.
4. **Enable authentication** (`AETHERION_REQUIRE_AUTH=true`) and assign the principle of least privilege (viewer → operator → admin).
5. **Deploy behind a reverse proxy** (nginx, Traefik) with HTTPS in production.
6. **Keep your deployment up to date** with the latest patches.

## Built‑in Security Features

| Feature                           | Purpose                                                    |
|-----------------------------------|------------------------------------------------------------|
| **gVisor sandbox**                | User‑space kernel isolation for generated code execution   |
| **Seccomp profiles**              | Restrict available syscalls within the sandbox             |
| **Read‑only root filesystem**     | Prevent unauthorised writes                                |
| **User namespace remapping**      | Root‑in‑container ≠ root‑on‑host                           |
| **Tamper‑proof audit logging**    | Cryptographically chained and signed logs                  |
| **Encrypted secrets manager**     | Fernet‑encrypted environment variables                     |
| **RBAC (API keys, JWT, OAuth2)**  | Fine‑grained role‑based access control                     |
| **Idempotency keys**              | Safe‑retry for API calls                                   |
| **Rate limiting**                 | Per‑IP throttling                                          |
| **Security Council veto**         | Absolute rejection of unsafe outputs                       |

## Disclosure Policy

We follow a coordinated disclosure process:

1. Reporter submits vulnerability privately.
2. We validate and develop a fix.
3. A patch release is issued for supported versions.
4. A public advisory is published, crediting the reporter (with consent).

## Acknowledgements

We thank the following individuals and organisations for responsibly disclosing security issues:

*(This list will be updated as contributions are received.)*

---

**Aetherion — Governed by reason. Secured by design.**
