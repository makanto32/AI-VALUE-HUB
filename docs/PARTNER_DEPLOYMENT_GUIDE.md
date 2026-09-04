# Partner Deployment Guide

This guide separates a fast product evaluation from the work required for a client production environment.

## Evaluate the application

### Prerequisites

- Git
- Docker Desktop, or Docker Engine with Docker Compose v2
- 4 GB of free memory recommended for image builds

### Start

```bash
git clone https://github.com/makanto32/AI-VALUE-HUB.git
cd AI-VALUE-HUB
docker compose up --build
```

Open `http://localhost:8080`. The browser calls the API at `http://localhost:8000`; Swagger is available at `http://localhost:8000/docs`.

Use one of these demo accounts:

| Role | User | Password |
|---|---|---|
| Business analyst | `analista.finanzas` | `Demo1234!` |
| Technical reviewer | `analista.tecnologia` | `Demo1234!` |
| Administrator | `admin.valuehub` | `Demo1234!` |

The API stores SQLite data and local context files in a named Docker volume. `docker compose down` preserves it; `docker compose down --volumes` deletes it.

### Configure

Copy `.env.example` to `.env` before building when the default host ports are unavailable. `VITE_API_URL` is compiled into the browser bundle, so it must be a URL reachable from the user's browser, not the Compose service name `api`.

```dotenv
FRONTEND_PORT=8080
API_PORT=8000
VITE_API_URL=http://localhost:8000
AIHUB_AUTH_PROVIDER=demo
```

### Verify

```bash
docker compose ps
curl http://localhost:8000/health
```

Then select a language, sign in, create an idea, and verify that it remains after `docker compose down` followed by `docker compose up`.

## Understand the code

| Area | Entry point | Responsibility |
|---|---|---|
| Web application | `frontend/src/App.jsx` | Localized role-based workflow and API calls |
| API | `api/app/main.py` | FastAPI routes, demo authentication, and workflow orchestration |
| Models | `api/app/models.py` | API request and response contracts |
| Persistence | `api/app/store.py` | Current SQLite repository |
| File storage | `api/app/blob_storage.py` | Azure Blob integration with local fallback |
| Containers | `compose.yaml` | Portable evaluation topology |
| Azure templates | `infra/` | Reference Azure Container Apps infrastructure |

## Production readiness gates

Do not promote the Compose configuration directly to a client environment. Complete and validate these gates first:

1. Implement Microsoft Entra ID token validation and authorization; `AIHUB_AUTH_PROVIDER=entra` is currently a roadmap placeholder.
2. Replace SQLite with a managed relational database and add migrations, connection pooling, backups, and restore tests.
3. Use Azure Blob Storage with managed identity. Keep connection strings and client secrets in Key Vault, never in images or source control.
4. Restrict CORS to approved frontend origins and expose both services through TLS-enabled ingress with custom domains.
5. Define tenant isolation, least-privilege roles, audit retention, privacy classification, and deletion policies with the client.
6. Add Application Insights telemetry, availability probes, alerts, dashboards, and operational runbooks.
7. Add rate limiting, dependency scanning, container image scanning, penetration testing, and an incident response process.
8. Define availability and scale requirements, then configure replicas, autoscaling, zone strategy, and disaster recovery accordingly.
9. Replace sample data and demo credentials, and run client security, Responsible AI, compliance, performance, and cost reviews.

The files under `infra/` are references tied to an Azure Container Apps design. Parameterize client-specific resource IDs, domains, registry names, secrets, and regions before deployment; do not reuse a captured `*-live.yaml` resource export as a general-purpose template.