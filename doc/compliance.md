```markdown
# Compliance & Data Protection

Aetherion provides built‑in features to assist with GDPR, CCPA, and SOC2
compliance for self‑hosted deployments.

## GDPR / CCPA Endpoints

All compliance endpoints require the `admin` role.

### Data Export (Right of Access / Portability)

```

GET /api/compliance/export/{workspace_id}

```

Returns a downloadable `.tar.gz` archive containing:
- Constitution and agent configuration
- Knowledge graph entries
- Full audit log history

### Right to Deletion

```

DELETE /api/compliance/delete/{workspace_id}

```

Permanently removes a workspace and all its data (knowledge graph, audit logs,
configurations). This action is irreversible.

### Consent Management

```

POST /api/compliance/consent/{workspace_id}?consented=true
GET  /api/compliance/consent/{workspace_id}

```

Records and retrieves the consent status for a workspace. Consent must be
`true` before the workspace can be used in environments where GDPR applies.

## Audit Trail (SOC2 Readiness)

Aetherion includes a cryptographically chained, append‑only audit log that
records:

- Every human override (operator, task ID, reason, timestamp)
- Every Council verdict
- Every constitution change

The log supports external verification via RSA digital signatures. Combined
with role‑based access control, encrypted secrets, and backup procedures, the
system provides the technical controls necessary for a SOC2 Type I audit.

A formal SOC2 or ISO 27001 audit has not yet been performed, but the technical
foundation is in place.

## Data Retention

By default, data is retained indefinitely. To configure automatic cleanup,
use the workspace deletion endpoint or the backup/restore scripts to manage
retention policies externally.

## Third‑Party Integrations

When deploying with OAuth2/OIDC, SMTP email, or external APIs (Alpha Vantage,
weather APIs), those services operate under their own privacy policies.
Aetherion itself does not send data to these services unless explicitly
configured by the administrator.

## Legal Documents

- [Terms of Service](../TERMS.md)
- [Privacy Policy](../PRIVACY.md)
```
