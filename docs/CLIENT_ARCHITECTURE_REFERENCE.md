# AI Value Hub - Client Architecture Reference

## 1. Purpose

AI Value Hub is a reference solution that helps organizations evaluate and shape AI use cases from idea intake to technical validation, human approval, economic gating, and architecture packaging. The platform is designed to be understandable, extensible, and reusable as a baseline for customer-facing implementations.

This document provides a structured view of the solution so that a client or partner can understand:

- the functional intent of the platform,
- the main system components and responsibilities,
- the runtime flow of a use case,
- the recommended deployment model,
- and the extension points for future production scenarios.

## 2. Solution Summary

The solution combines:

- a web experience for users to submit and review ideas,
- an API layer for business and technical workflows,
- a context engine that evaluates the initiative against business and technical constraints,
- and a persistence and storage strategy for ideas, context documents, and generated artifacts.

## 3. Architecture Principles

The reference architecture is guided by the following principles:

1. Separation of concerns
   - UI, API, domain logic, data access, and storage are separated by responsibility.

2. Owner and tenant scoping
  - Business users access their own ideas. Authorized technical reviewers and admins can access ideas within their tenant.

3. Progressive maturity
   - The current implementation targets an MVP, but it is structured to evolve toward production-grade services.

4. Extensibility
   - New workflows, validators, and storage providers can be introduced without major rewrites.

5. Security-by-design readiness
   - Authentication hooks, storage abstraction, and environment-based configuration are prepared for enterprise adoption.

## 4. Logical Architecture

### 4.1 Layers

- Presentation Layer
  - React + Vite frontend for user interaction.
  - Supports login, idea capture, and results visualization.

- Application Layer
  - FastAPI backend that exposes business workflows and API endpoints.
  - Implements validation and architecture generation capabilities.

- Intelligence Layer
  - Deterministic context, matching, technical validation, and value-economics logic.
  - Produces architecture package outputs and recommendations.
  - Does not currently call Microsoft Foundry or another hosted model runtime.

- Data Layer
  - SQLite as the current persistence layer.
  - Blob storage abstraction for documents and context artifacts.

- Integration Layer
  - Azure Blob Storage integration with local fallback and optional Fabric exports.
  - Microsoft Entra ID token validation and future enterprise connectors remain roadmap items.

## 5. Component Map

| Area | Repository Location | Responsibility |
|---|---|---|
| Frontend | frontend/ | User interface, demo flows, idea interactions |
| API | api/app/ | FastAPI app, endpoints, models, storage handlers |
| Data | data/ | Local persistence, sample documents, local storage artifacts |
| Infrastructure | infra/ | Deployment templates and infrastructure definitions |
| Automation | scripts/ | Demo and deployment helpers |
| Documentation | docs/ | Implementation notes, architecture references, and generated assets |

## 6. Core Runtime Flow

### 6.1 Idea Intake

1. A user logs in through the frontend.
2. The UI sends the idea and context payload to the backend.
3. The API stores the idea and related metadata.
4. The system prepares the context for validation and architecture generation.

### 6.2 Technical Validation

1. An idea that passes business validation receives an automatic deterministic technical assessment.
2. The assessment can continue, request guided clarification, or reject the idea when blockers exceed thresholds.
3. A technical reviewer examines the result and records final human approval or rejection.
4. Value economics is calculated for reviewer context and enforced when moving an initiative to funding. Marginal, unfavorable, and unquantified cases require an explicit override.

### 6.3 Architecture Package Generation

1. After a successful technical interaction, the backend produces an architecture package for the idea.
2. The package includes components, integrations, risks, and deployment considerations.
3. The package can be downloaded as a generated PDF and used during implementation planning. It remains a draft that requires qualified architecture review.

## 7. Deployment Options

### Local Reference Deployment

- Python environment with FastAPI and frontend dependencies.
- SQLite and local file-based storage.
- Suitable for demos and technical validation.

### Azure-Aligned Deployment

- The API has a Container Apps manifest with HTTPS ingress, system-assigned identity, ACR image, and SQLite on Azure Files.
- The frontend and API have container definitions and update automation; full-stack Bicep declarations remain incomplete.
- Azure Blob Storage is implemented for context uploads, with a local fallback when cloud configuration fails.
- Microsoft Entra ID is a target architecture component, not an implemented authentication option. Selecting it currently returns HTTP 501.
- Use this deployment only for development or controlled pilot validation until the production gaps are closed.

## 8. Security and Operational Considerations

- Authentication currently uses opaque demo bearer sessions. Demo credentials must not be used in production.
- SQLite is the active system of record. PostgreSQL provisioning is optional infrastructure only and the application has not been migrated to it.
- Blob uploads can use managed identity or a connection string and fall back to local storage in development.
- Environment configuration should be used for secrets and service endpoints.
- Logging, immutable audit records, alerts, runbooks, backup/restore validation, and network isolation must be completed for production deployment.

## 9. How a Client Can Reuse This Architecture

A client can use this repository as a reference in the following ways:

- Use the frontend and backend structure as a starting point for a custom AI opportunity evaluation platform.
- Reuse the validation and packaging workflow as the core business logic for internal innovation programs.
- Adapt the storage layer to enterprise databases and document services.
- Replace or augment the current demo authentication with corporate identity providers.
- Use the generated architecture package as a baseline for solution design workshops.

## 10. Recommended Evolution Path

Phase 1: Stabilize the MVP
- Update the existing workflow scripts for current response contracts and automate regression testing.
- Remove development debug output and define versioned API contracts.
- Rerun end-to-end, container-build, and Bicep checks against a release candidate.

Phase 2: Production Readiness
- Replace SQLite with a managed relational store and migration tooling.
- Implement Microsoft Entra ID token validation, application roles, and least-privilege RBAC.
- Complete observability, secrets references, private connectivity, full-stack IaC, CI/CD, backups, and recovery tests.

Phase 3: Enterprise Scaling
- Introduce multi-tenant capabilities.
- Add orchestration, queue-based processing, and more advanced AI workflows.
- Connect to enterprise systems and knowledge repositories.

## 11. Summary

AI Value Hub provides a practical and extensible reference implementation for evaluating AI use cases. Clients can use it as a blueprint for a structured innovation platform, a controlled technical proof of concept, or a foundation for a more mature enterprise solution after completing the documented production controls.
