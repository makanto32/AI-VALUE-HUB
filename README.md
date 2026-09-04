# AI Value Hub

Reference implementation and deployment kit for governing and prioritizing enterprise AI initiatives on Azure.

**Architecture design:** Marco Antonio Salas Robles, Sr. Cloud Solution Architect.

> [!IMPORTANT]
> This is a personal, community-maintained project. It is not an official Microsoft product or Azure service, and Microsoft does not provide support or warranties for it. The repository contains a working demo, infrastructure templates, and operational guidance; items marked as roadmap are not implemented. Review security, compliance, availability, and cost requirements before using it in production.

## License
This repository is licensed under MIT.
See full terms in [LICENSE](LICENSE).

## ⭐ Star Here - Quick Start

**AI Value Hub** is an AI initiative management and validation reference platform for enterprises. It implements a three-stage workflow with context-aware business validation, deterministic technical assessment, human technical approval, economic gating before funding, and duplicate detection.

### 🎯 Key Value Proposition
- **Three-Stage Validation**: Intake → context-aware business validation → automatic technical assessment and final human approval
- **Heuristic Duplicate Gate**: normalized exact title, title containment, and token-overlap thresholds prevent likely duplicate intake within a tenant
- **Economic Viability Gate**: Validates financial viability (cost-to-value ratio) before funding
- **Multi-role**: Business Analyst, Technical Reviewer, Admin
- **Deployable Reference Demo**: Sample data and a complete local workflow; Microsoft Entra ID integration remains a production roadmap item

---

## 🚀 Live Views - Interactive Demonstrations (GitHub Pages)

Access the project's visual views directly. All views below are read-only and require no local installation:

- **📊 [Control Center](https://makanto32.github.io/AI-VALUE-HUB/)** - Main navigation dashboard
- **💡 [AI Value Hub Interactive Demo](https://makanto32.github.io/AI-VALUE-HUB/ai-value-hub-demo.html)** - Visual workflow of complete journey
- **🏗️ [Technical Architecture (EN)](https://makanto32.github.io/AI-VALUE-HUB/architecture-diagram.html)** - Component and integration diagrams
- **🏗️ [Technical Architecture (ES)](https://makanto32.github.io/AI-VALUE-HUB/architecture-diagram.es.html)** - Spanish localized version
- **📈 [Microsoft Fabric Architecture + Executive Dashboard](https://makanto32.github.io/AI-VALUE-HUB/architecture-fabric-live.html)** - Live Power BI/Fabric integration for KPI metrics
- **📖 [Use Case Factory & Company Context Engine](https://makanto32.github.io/AI-VALUE-HUB/AI_Use_Case_Factory_Company_Context_Engine_EN.html)** - Architectural reference document and patterns

---

## 🎯 Core Capabilities

### Phase 1: Intake & Context
- ✅ Structured idea capture with problem statement and expected value
- ✅ Per-tenant Context Engine: evaluates viability within business baseline
- ✅ Localized workflows and generated responses in ES, EN, and PT, with Spanish as the canonical language
- ✅ Owner-scoped idea access, with tenant-scoped access for authorized technical reviewers and admins

### Phase 2: Business Validation (Context-Aware)
- ✅ Dynamic validation questionnaire based on business context
- ✅ **Heuristic Duplicate Gate** on active tenant initiatives:
  - Normalized exact-title matching
  - Normalized title containment
  - Jaccard token overlap across title and problem statement
  - Returns the likely duplicate and owner contact for human follow-up
- ✅ Automatic scoring based on responses
- ✅ Interactive clarification flow if scoring is low

### Phase 3: Technical Validation (With Economic Gate)
- ✅ **Dedicated technical queue** for technical reviewers
- ✅ **Automatic deterministic assessment** followed by mandatory human technical approval for the standard approval endpoint
- ✅ **Automatic Value Economics analysis**:
  - Extracts expected value from description (high/medium/low confidence)
  - Calculates monthly infrastructure consumption cost
  - Computes value-to-cost ratio and payback period
  - Period normalization (monthly/annual/quarterly/weekly/daily)
- ✅ **Economic Viability Gate**: blocks movement to funding for unfavorable, marginal, or unquantified ideas unless a technical reviewer explicitly overrides it
  - Verdicts: favorable (>=3.0x), acceptable (>=1.5x), marginal (>=1.0x), unfavorable (<1.0x)
  - Optional override for business context via `?override_economics=true`
- ✅ **Technical Rejection Workflow**: records rejection reason
- ✅ Architecture Package generation with components, integrations, risks

### Outputs
- ✅ Professional PDF with architecture, cost/value analysis, and ROI metrics
- ✅ Executive Dashboard with KPIs: pipeline ideas, viability, ROI, adoption rate
- ✅ Admin Panel with performance metrics and Business Rules configuration

---

## 👥 Roles & Permissions

| Role | Responsibilities | Main Views |
|-----|------------------|------------------|
| **Business Analyst** | Intake, business validation, context answers | Home, My Ideas, Clarification Queue |
| **Technical Reviewer** | Technical validation, economic decision, rejection with reason | Technical Queue (economic), Architecture Package Review |
| **Admin** | Context management, business rules configuration, executive dashboard | Admin Panel, Executive Dashboard, Context Manager |

---

## Microsoft Fabric Integration
- Semantic provider enabled for executive dashboard via Power BI / Fabric.
- Support scripts:
	- `scripts/fabric-provision-semantic.ps1`
	- `scripts/fabric-sync-semantic.ps1`
- Setup reference: `docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md`

## MVP1 Implemented ✅
- ✅ Idea intake with context capture
- ✅ Per-tenant Context Engine for viability evaluation
- ✅ Business validation with dynamic questionnaire + initial technical filter
- ✅ Use case status with rejection reason (business or technical phase)
- ✅ UI with login demo flow, context capture, and "My Ideas" view
- ✅ Owner-scoped access for business users and tenant-scoped review access for technical/admin roles
- ✅ Multi-language support (ES/EN/PT)
- ✅ Seven reusable demo ideas across ES, EN, and PT, available through the demo seed endpoint

## MVP2 Implemented ✅
- ✅ Persistence in SQLite DB (evolvable to PostgreSQL)
- ✅ Context file metadata in DB + content in Blob storage
- ✅ Technical validation via dedicated endpoint
- ✅ Professional Architecture Package generation (9 sections, PDF exportable)
- ✅ Response Composer with executive summary and recommendations

## 🎯 Latest Updates (v2.1) - Robust Validation & Economic Gating

### Heuristic Duplicate Gate
- **Scope**: Compares a new intake request with active initiatives in the same tenant.
- **Signals**: Normalized exact titles, title containment, and Jaccard token overlap for title, problem statement, and their combined text.
- **Thresholds**: Requires strong title and problem overlap together, or strong combined overlap.
- **Outcome**: Returns HTTP `409 Conflict` with the likely duplicate and owner details. The gate is heuristic and does not claim embedding-based semantic equivalence.

### Technical Queue with Automatic Value Economics
- **Role**: Technical Reviewer accesses queue of business_viable ideas
- **Automatic analysis**: System calculates value economics:
  - Extracts expected value from description (confidence: high/medium/low)
  - Resolves period (annual → monthly, etc.)
  - Calculates monthly infrastructure consumption cost
  - Computes value-to-cost ratio and payback period
  - Generates verdict: favorable/acceptable/marginal/unfavorable

### Economic Viability Gate
- **Blocks funding** if ratio < 1.0x (economically unfeasible)
- **Requires override** if ratio marginal (1.0x-1.5x) or needs_quantification
- **Permits approval** if ratio favorable (>=3.0x) or acceptable (1.5x-3.0x)
- **Objective**: Avoid investing in technically viable but economically unfeasible ideas

### Technical Rejection Workflow
- Technical Reviewer can reject ideas with structured reason
- Rejection history by phase (business vs technical)
- Insights to improve Business Validation rules

### PDF Architecture Package
- 9 sections: Executive Summary, Architecture Diagram, Components, Integrations, Risks, Deployment Steps, Cost Analysis, ROI Metrics, Contact
- Exportable in professional format for stakeholders
- Includes monthly consumption analysis and payback period

### UI/UX Improvements
- Removed emojis, replaced with text labels
- Dashboard metric tooltips document how each metric is calculated
- Admin Panel metric help texts (14+ in ES/EN/PT)
- Real-time polling every 10s for state synchronization

---

## 🔮 Roadmap - Not Yet Implemented

### Phase 3: Production Deployment & Monitoring (Q3-Q4 2026)
- [ ] **Entra ID Integration** - Replace auth mock with Azure Entra
- [ ] **Production Database** - PostgreSQL + connection pooling
- [ ] **Blob Storage** - Azure Blob Storage for context files (fallback: local)
- [ ] **Observability** - Application Insights logging + alerts
- [ ] **API Rate Limiting** - Protection against abuse
- [ ] **Audit Logging** - Complete change trail for compliance

### Phase 4: Advanced Analytics & ML (Q1 2027)
- [ ] **Collaborative Filtering** - Idea recommendations based on adoption patterns
- [ ] **Semantic Search** - Search ideas by meaning (not just keywords)
- [ ] **Predictive Scoring** - ML model to predict viability based on historical features
- [ ] **Anomaly Detection** - Flag unusual patterns in valuations
- [ ] **Custom ML Models** - Allow model upload per tenant

### Phase 5: Ecosystem & Integration (H2 2027)
- [ ] **Salesforce Integration** - Sync opportunities → ideas
- [ ] **Dynamics 365 CRM** - Sales pipeline integration
- [ ] **Teams/Slack Notifications** - Alerts in communication channels
- [ ] **Power Automate Workflows** - RPA triggering
- [ ] **OpenAPI/GraphQL** - Public API for partners
- [ ] **Webhooks** - Event-driven architecture

### Phase 6: Governance & Scale (2028+)
- [ ] **Role-Based Access Control (RBAC)** - Granular permissions (not just 3 roles)
- [ ] **Workflow Customization** - Tenant admins define custom validation phases
- [ ] **Approval Routing** - Multi-level approval chains
- [ ] **Compliance Modules** - Templates for SOX, GDPR, etc.
- [ ] **Multi-tenant Isolation** - Ensure zero data leakage
- [ ] **High Availability** - Active-active deployment in multi-regions

### Future Marketplace-Oriented Capabilities (Under Evaluation)
See the [project roadmap](#roadmap---not-yet-implemented) for the broader delivery sequence:
- [ ] **Community Voting / Upvoting** - Crowdsourced validation of ideas
- [ ] **Download / Adoption Metrics** - Track usage and deployment success
- [ ] **User Comments and Reviews** - Community feedback on initiatives
- [ ] **Publication Workflow** - Draft → Published → Versioned lifecycle
- [ ] **Admin Center** - Token/Cost/ROI governance and monitoring
- [ ] **Multi-tenant IaC** - Packaged deployment per client with Infrastructure as Code

## Authentication (Demo Current, Microsoft Entra ID Target)

### Active Provider
- Default: `AIHUB_AUTH_PROVIDER=demo` (local test users)
- Planned: `AIHUB_AUTH_PROVIDER=entra` for Microsoft Entra ID integration. The API returns `501 Not Implemented` when this provider is selected until token validation is completed.

### Demo Users
| User | Password | Role | Access |
|------|----------|------|--------|
| `analista.finanzas` | `Demo1234!` | Business Analyst | Intake, My Ideas, Validation Queue |
| `analista.riesgo` | `Demo1234!` | Business Analyst | Intake, My Ideas, Validation Queue |
| `analista.tecnologia` | `Demo1234!` | **Technical Reviewer** | Technical Queue, Economic Gate, Rejection |
| `admin.valuehub` | `Demo1234!` | Admin | Admin Panel, Context Manager, Executive Dashboard |

### Authentication Endpoints
- `POST /auth/login` - Obtain a demo bearer session token
- `GET /auth/me` - Get current user profile
- `GET /ideas/mine` - Get user's ideas

### Authentication Flow
1. Login with user/password
2. Backend validates the demo account and returns an opaque bearer session token
3. Frontend stores token in localStorage
4. All subsequent requests include token in Authorization header
5. Session syncs every 10s with polling for status updates

## 📁 Project Structure

```
AI-VALUE-HUB/
├── api/                           # Backend FastAPI
│   ├── app/
│   │   ├── main.py               # REST API with 48 application endpoints
│   │   ├── models.py             # Pydantic models for request/response
│   │   ├── matching_service.py   # Related-initiative scoring utilities
│   │   ├── value_economics.py    # Economic viability analysis
│   │   ├── pdf_service.py        # Architecture package PDF generation
│   │   ├── store.py              # SQLite persistence layer
│   │   └── ...
│   └── requirements.txt
├── frontend/                      # React + Vite SPA
│   ├── src/
│   │   ├── App.jsx               # Main component (3600+ lines)
│   │   ├── pages/
│   │   │   └── ExecutiveDashboard.tsx  # KPI metrics & monitoring
│   │   ├── styles/               # CSS modules + global styles
│   │   └── components/           # Reusable UI components
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── aihub.db                  # SQLite database (local dev)
├── docs/                          # Architecture & deployment guides
├── infra/                         # IaC templates (future)
├── scripts/                       # Setup & automation scripts
├── test_*.py                      # Test files for validation
└── README.md
```

### Key Components

| Component | Responsibility | Tech Stack |
|-----------|----------------|-----------|
| **REST API** | 48 application endpoints, demo bearer auth, business logic | FastAPI, Pydantic, SQLite |
| **Intake Duplicate Gate** | Exact, containment, and Jaccard token-overlap checks | Python normalization + set similarity |
| **Value Economics** | Cost analysis, ROI calculation, economic viability | Python numerical analysis |
| **Frontend SPA** | Multi-role UI, real-time polling, i18n | React 18, Vite, CSS modules |
| **Auth Layer** | Opaque demo bearer sessions; Entra token validation is planned | FastAPI HTTPBearer, localStorage |
| **Database** | Tenant-scoped idea persistence and workflow history | SQLite (current) → PostgreSQL (target) |

---

## Partner Quick Start (Docker)

Run the same frontend and API shown in this repository with Docker Desktop or Docker Engine with Compose:

```bash
git clone https://github.com/makanto32/AI-VALUE-HUB.git
cd AI-VALUE-HUB
docker compose up --build
```

Open `http://localhost:8080`, select a language, and sign in with `admin.valuehub / Demo1234!`. API documentation is available at `http://localhost:8000/docs`. Application data and uploaded context files persist in the named Docker volume `ai-value-hub_aihub-data`.

To use different ports or a browser-accessible API URL, copy `.env.example` to `.env`, edit the values, and rebuild with `docker compose up --build`. See [Partner deployment guide](docs/PARTNER_DEPLOYMENT_GUIDE.md) for architecture, verification, and production hardening.

> [!WARNING]
> Docker Compose starts an evaluation environment with demo authentication and SQLite. It is not a production security or availability configuration.

## Local Development Setup

### Requirements
- Python 3.11+ with pip
- Node.js 18+ with npm
- PowerShell (Windows) or bash (Mac/Linux)

### Setup Steps

**1. Clone Repository**
```bash
git clone https://github.com/makanto32/AI-VALUE-HUB.git
cd AI-VALUE-HUB
```

**2. Configure Python Environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
& .\.venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
cd api
pip install -r requirements.txt
```

**3. Run Backend (FastAPI)**
```bash
# From api folder
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# In another terminal:
# Backend running at http://127.0.0.1:8000
# Swagger API docs at http://127.0.0.1:8000/docs
```

**4. Run Frontend (React + Vite)**
```bash
# From frontend folder
npm install
npm run dev

# Frontend running at http://localhost:5174
# Or use .env.local for remote API:
# VITE_API_URL=http://127.0.0.1:8000
```

**5. Access Application**
- **Frontend**: http://localhost:5174/
- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **Demo Users**:
  - Business: `analista.finanzas / Demo1234!`
  - Technical: `analista.tecnologia / Demo1234!`
  - Admin: `admin.valuehub / Demo1234!`

### Troubleshooting

| Problem | Solution |
|---------|----------|
| **API not responding** | Verify `uvicorn` is running on port 8000 |
| **Frontend connects to Azure API** | Verify `.env.local` has `VITE_API_URL=http://127.0.0.1:8000` |
| **Login fails** | Verify user/password matches table above (case-sensitive) |
| **CORS errors** | Verify CORS middleware in `api/app/main.py` allows the frontend origin |

---

## 📚 Documentation

### Reference Guides
- **[CLIENT_ARCHITECTURE_REFERENCE.md](docs/CLIENT_ARCHITECTURE_REFERENCE.md)** - Architectural diagram and description for development teams
- **[FABRIC_MEDALLION_SEMANTIC_SETUP.md](docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md)** - Microsoft Fabric setup for Executive Dashboard
- **[AZURE_DEPLOYMENT_PLAN.md](docs/AZURE_DEPLOYMENT_PLAN.md)** - Deployment plan for Azure Container Apps
- **[ACR_PRODUCTION_DEPLOYMENT.md](docs/ACR_PRODUCTION_DEPLOYMENT.md)** - Versioned OCI images, ACR promotion, Container Apps, and production security gates
- **[PARTNER_DEPLOYMENT_GUIDE.md](docs/PARTNER_DEPLOYMENT_GUIDE.md)** - Fast local evaluation and production readiness overview

---

## 🤝 Contribution & Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution requirements, [SECURITY.md](SECURITY.md) for vulnerability reporting, and [SUPPORT.md](SUPPORT.md) for the support scope.

### For Development Teams
This repository is designed to be:
1. **Clean and Clear**: Modular code, documented endpoints, consistent naming conventions
2. **Extensible**: SOLID architecture, decoupled services, easy to add new phases/roles
3. **Deployment-Oriented**: A deployed API manifest, container definitions, and Azure foundation templates are included for evaluation and extension
4. **Well-Tested**: Test cases included for matching service, economics engine, and critical workflows

### To Add Features
1. Review the [Roadmap](#-roadmap---not-yet-implemented) for priorities
2. Create branch: `git checkout -b feature/feature-name`
3. Implement in backend (`api/app/`) and frontend (`frontend/src/`) as needed
4. Validate with test cases
5. Push to GitHub and create Pull Request with clear description

### Naming Structure
- **Files**: snake_case (e.g., `matching_service.py`)
- **Functions**: snake_case (e.g., `find_related_initiatives()`)
- **Classes**: PascalCase (e.g., `IdeaCase`, `ValueEconomics`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SEMANTIC_SYNONYMS`)

---

## 📄 License
This project is licensed under **MIT License**. See [LICENSE](LICENSE) for full details.

## 👥 Contact & Support
For technical questions, issues, or feature proposals:
1. Create a [GitHub Issue](https://github.com/makanto32/AI-VALUE-HUB/issues)
2. Describe the problem/feature with clear context
3. Include reproduction steps (if bug) or use cases (if feature)

---

**Last Updated**: August 2026  
**Status**: Reference MVP operational | Production controls in progress
**Maintainers**: Development Team
