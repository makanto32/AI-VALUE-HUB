# AI Value Hub

Base proyecto alineada al roadmap del documento de arquitectura.

## Licencia
Este repositorio está licenciado bajo MIT.
Consulta los términos completos en [LICENSE](LICENSE).

## ⭐ Star Here - Quick Start

**AI Value Hub** es una plataforma de gestión y validación de iniciativas impulsadas por IA para organizaciones financieras. Implementa un workflow de 3 fases con gates económicos, validación técnica robusta y detección inteligente de duplicidad.

### 🎯 Valor Clave
- **Validación 3-Fases**: Intake → Business (context-aware) → Technical (with economic gate)
- **Detección Inteligente de Duplicidad**: 4-estrategia semántica detecta duplicados incluso con wording distinto
- **Gate Económico**: Valida viabilidad financiera (ratio cost-to-value) antes de financiación
- **Multi-rol**: Business Analyst, Technical Reviewer, Admin
- **Production-Ready Demo**: Datos de ejemplo, workflow completo, pronto para Entra ID

---

## 🚀 Live Views - Vistas Interactivas (GitHub Pages)

Accede directamente a las vistas visuales del proyecto. Las siguientes son solo para lectura y no requieren instalación local:

- **📊 [Centro de Control](https://makanto32.github.io/AI-Opportunity-Hub/)** - Dashboard de navegación principal
- **💡 [AI Value Hub Interactive Demo](https://makanto32.github.io/AI-Opportunity-Hub/ai-value-hub-demo.html)** - Flujo visual del workflow completo
- **🏗️ [Arquitectura Técnica (EN)](https://makanto32.github.io/AI-Opportunity-Hub/architecture-diagram.html)** - Diagrama de componentes y integraciones
- **🏗️ [Arquitectura Técnica (ES)](https://makanto32.github.io/AI-Opportunity-Hub/architecture-diagram.es.html)** - Versión localizada en español
- **📈 [Arquitectura Microsoft Fabric + Executive Dashboard](https://makanto32.github.io/AI-Opportunity-Hub/architecture-fabric-live.html)** - Integración live con Power BI/Fabric para métricas KPI
- **📖 [Use Case Factory & Company Context Engine](https://makanto32.github.io/AI-Opportunity-Hub/AI_Use_Case_Factory_Company_Context_Engine_EN.html)** - Documento de referencia arquitectónico y patrones

---

## 🎯 Core Capabilities

### Fase 1: Intake & Contexto
- ✅ Captura estructurada de idea con problem statement y expected value
- ✅ Context Engine por tenant: valúa viabilidad dentro de línea base empresarial
- ✅ Soporte multi-idioma (ES, EN, PT) con traducción automática vía i18n
- ✅ Aislamiento por usuario: cada sesión solo consulta sus ideas

### Fase 2: Business Validation (Context-Aware)
- ✅ Cuestionario de validación dinámico basado en contexto empresarial
- ✅ **Detección Inteligente de Duplicidad** con 4-estrategia semántica:
  - Keyword similarity (compatibilidad legado)
  - Structural string similarity (SequenceMatcher)
  - Semantic concept overlap (sinónimos del dominio financiero)
  - Intention analysis (título + problem statement combinados)
  - **Detecta duplicados incluso con wording distinto o descripción reducida**
- ✅ Scoring automático basado en respuestas
- ✅ Flujo de clarificación interactivo si scoring es bajo

### Fase 3: Technical Validation (Con Gate Económico)
- ✅ **Queue técnica dedicada** para revisores técnicos
- ✅ **Análisis de Value Economics** automático:
  - Extrae valor esperado de descripción (high/medium/low confidence)
  - Calcula costo mensual de consumo de infraestructura
  - Computa ratio value-to-cost y payback period
  - Period normalization (monthly/annual/quarterly/weekly/daily)
- ✅ **Economic Viability Gate**: bloquea fundación de ideas económicamente inviables
  - Verdicts: favorable (>=3.0x), acceptable (>=1.5x), marginal (>=1.0x), unfavorable (<1.0x)
  - Override opcional para contexto de negocio via `?override_economics=true`
- ✅ **Technical Rejection Workflow**: registra razón de rechazo
- ✅ Generación de Architecture Package con componentes, integraciones, riesgos

### Salidas
- ✅ PDF profesional con arquitectura, cost/value analysis y ROI metrics
- ✅ Executive Dashboard con KPIs: ideas en pipeline, viabilidad, ROI, adoption rate
- ✅ Admin Panel con métricas de rendimiento y configuración de Business Rules

---

## 👥 Roles & Permisos

| Rol | Responsabilidades | Vistas Principales |
|-----|------------------|------------------|
| **Business Analyst** | Intake, validación de negocio, respuestas de contexto | Home, My Ideas, Clarification Queue |
| **Technical Reviewer** | Validación técnica, decisión económica, rechazo con razón | Technical Queue (económica), Architecture Package Review |
| **Admin** | Gestión de contexto, configuración de reglas, dashboard ejecutivo | Admin Panel, Executive Dashboard, Context Manager |

---

## Integracion Microsoft Fabric
- Provider semantico habilitado para dashboard ejecutivo via Power BI / Fabric.
- Scripts de soporte:
	- `scripts/fabric-provision-semantic.ps1`
	- `scripts/fabric-sync-semantic.ps1`
- Referencia de setup: `docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md`

## MVP1 Implementado ✅
- ✅ Idea intake con captura de contexto
- ✅ Context Engine por tenant para evaluación de viabilidad
- ✅ Business validation con cuestionario dinámico + filtro técnico inicial
- ✅ Estado del caso de uso con motivo de rechazo (fase business o technical)
- ✅ UI con flujo de login demo, captura de contexto, y vista "Mis ideas"
- ✅ Aislamiento por usuario: cada sesión solo consulta sus ideas
- ✅ Soporte multi-idioma (ES/EN/PT)
- ✅ Demo con 13 ideas de ejemplo preargadas

## MVP2 Implementado ✅
- ✅ Persistencia en DB SQLite (evolucionable a PostgreSQL)
- ✅ Metadata de archivos de contexto en DB + contenido en Blob storage
- ✅ Validación técnica por endpoint dedicado
- ✅ Generación de Architecture Package profesional (9 secciones, PDF exportable)
- ✅ Response Composer con resumen ejecutivo y recomendaciones

## 🎯 Últimas Actualizaciones (v2.1) - Robust Validation & Economic Gating

### Detección Inteligente de Duplicidad (4-Estrategia Semántica)
- **Problema resuelto**: Las búsquedas de palabras clave simples no detectaban duplicados cuando el wording cambiaba
- **Solución**: Análisis combinado de 4 dimensiones:
  1. **Keyword Similarity** - Palabras compartidas directas
  2. **Structural String Similarity** - SequenceMatcher detecta similitud incluso con cambios de formato
  3. **Semantic Concept Overlap** - Mapeo de sinónimos del dominio (predicción ↔ predictor, rotación ↔ churn)
  4. **Intention Analysis** - Combina título + problem statement para detectar objetivo subyacente
- **Resultado**: Detecta duplicidad incluso cuando:
  - Cambias "Predicción" por "Predictor"
  - Reduces descripción significativamente
  - Usas sinónimos distintos para el mismo problema
  - Modificas wording pero objetivo es idéntico

### Technical Queue con Value Economics Automático
- **Rol**: Technical Reviewer accede a queue de ideas business_viable
- **Análisis automático**: Sistema calcula value economics:
  - Extrae valor esperado de descripción (confidence: high/medium/low)
  - Resuelve período (anual → mensual, etc.)
  - Calcula costo mensual de consumo de infraestructura
  - Computa ratio value-to-cost y payback period
  - Genera verdict: favorable/acceptable/marginal/unfavorable

### Economic Viability Gate
- **Bloquea fundación** si ratio < 1.0x (inviable económicamente)
- **Requiere override** si ratio marginal (1.0x-1.5x) o needs_quantification
- **Permite aprobación** si ratio favorable (>=3.0x) o acceptable (1.5x-3.0x)
- **Objetivo**: Evita invertir en ideas técnicamente viables pero económicamente inviables

### Technical Rejection Workflow
- Technical Reviewer puede rechazar ideas con razón estructurada
- Histórico de rechazos por phase (business vs technical)
- Insights para mejorar Business Validation rules

### PDF Architecture Package
- 9 secciones: Executive Summary, Architecture Diagram, Components, Integrations, Risks, Deployment Steps, Cost Analysis, ROI Metrics, Contact
- Exportable en formato profesional para stakeholders
- Incluye análisis de consumo mensual y payback period

### UI/UX Improvements
- Removidos emojis, reemplazados con text labels
- Dashboard metric tooltips documentan cómo se calcula cada métrica
- Admin Panel metric help texts (14+ en ES/EN/PT)
- Real-time polling cada 10s para sincronización de estado

---

## 🔮 Roadmap - Not Yet Implemented

### Phase 3: Production Deployment & Monitoring (Q3-Q4 2026)
- [ ] **Entra ID Integration** - Reemplazar auth mock con Azure Entra
- [ ] **Production Database** - PostgreSQL + connection pooling
- [ ] **Blob Storage** - Azure Blob Storage para contexto files (fallback: local)
- [ ] **Observability** - Application Insights logging + alerts
- [ ] **API Rate Limiting** - Protección contra abuse
- [ ] **Audit Logging** - Trail completo de cambios para compliance

### Phase 4: Advanced Analytics & ML (Q1 2027)
- [ ] **Collaborative Filtering** - Recomendaciones de ideas relacionadas basadas en adoption patterns
- [ ] **Semantic Search** - Búsqueda de ideas por significado (no solo keywords)
- [ ] **Predictive Scoring** - ML model para predecir viabilidad basado en features históricos
- [ ] **Anomaly Detection** - Flagear patrones inusuales en valuations
- [ ] **Custom ML Models** - Permitir upload de modelos por tenant

### Phase 5: Ecosystem & Integration (H2 2027)
- [ ] **Salesforce Integration** - Sync de opportunities → ideas
- [ ] **Dynamics 365 CRM** - Integración con pipeline de ventas
- [ ] **Teams/Slack Notifications** - Alertas en canales de comunicación
- [ ] **Power Automate Workflows** - Triggering de RPA
- [ ] **OpenAPI/GraphQL** - Public API para partners
- [ ] **Webhooks** - Event-driven architecture

### Phase 6: Governance & Scale (2028+)
- [ ] **Role-Based Access Control (RBAC)** - Granular permissions (not just 3 roles)
- [ ] **Workflow Customization** - Tenant admins definen custom validation phases
- [ ] **Approval Routing** - Multi-level approval chains
- [ ] **Compliance Modules** - Templates para SOX, GDPR, etc.
- [ ] **Multi-tenant Isolation** - Garantizar zero data leakage
- [ ] **High Availability** - Active-active deployment en multi-regions

## Autenticación (Demo + Entra-Ready)

### Proveedor Activo
- Por defecto: `AIHUB_AUTH_PROVIDER=demo` (usuarios de prueba locales)
- Previsión: `AIHUB_AUTH_PROVIDER=entra` para integración con Azure Entra ID (509 Not Implemented hasta completar)

### Usuarios de Demo
| Usuario | Contraseña | Rol | Acceso |
|---------|-----------|-----|--------|
| `analista.finanzas` | `Demo1234!` | Business Analyst | Intake, My Ideas, Validation Queue |
| `analista.riesgo` | `Demo1234!` | Business Analyst | Intake, My Ideas, Validation Queue |
| `analista.tecnologia` | `Demo1234!` | **Technical Reviewer** | Technical Queue, Economic Gate, Rejection |
| `admin.valuehub` | `Demo1234!` | Admin | Admin Panel, Context Manager, Executive Dashboard |

### Endpoints de Autenticación
- `POST /auth/login` - Obtain JWT token
- `GET /auth/me` - Get current user profile
- `GET /ideas/mine` - Get user's ideas

### Flujo de Autenticación
1. Login con usuario/contraseña
2. Backend valida y devuelve JWT token
3. Frontend almacena token en localStorage
4. Todas las peticiones subsecuentes incluyen token en Authorization header
5. Sesión se sincroniza cada 10s con polling para status updates

## 📁 Estructura del Proyecto

```
ai-opportunity-hub/
├── api/                           # Backend FastAPI
│   ├── app/
│   │   ├── main.py               # REST API con 30+ endpoints
│   │   ├── models.py             # Pydantic models para request/response
│   │   ├── matching_service.py   # Semantic duplicate detection engine
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

### Componentes Clave

| Componente | Responsabilidad | Tech Stack |
|-----------|----------------|-----------|
| **REST API** | 30+ endpoints, JWT auth, business logic | FastAPI, Pydantic, SQLite |
| **Semantic Matching** | 4-strategy duplicate detection with synonyms | Python regex + difflib |
| **Value Economics** | Cost analysis, ROI calculation, economic viability | Python numerical analysis |
| **Frontend SPA** | Multi-role UI, real-time polling, i18n | React 18, Vite, CSS modules |
| **Auth Layer** | JWT token + demo users (Entra-ready) | FastAPI HTTPBearer, localStorage |
| **Database** | Tenant isolation, idea persistence, audit trail | SQLite (dev) → PostgreSQL (prod) |

---

## 🚀 Ejecutar Localmente (Desarrollo)

### Requisitos
- Python 3.11+ con pip
- Node.js 18+ con npm
- Terminal PowerShell (Windows) o bash (Mac/Linux)

### Pasos de Setup

**1. Clonar repositorio**
```bash
git clone https://github.com/makanto32/AI-Opportunity-Hub.git
cd AI-Opportunity-Hub
```

**2. Configurar Python Environment**
```bash
# Crear virtual environment
python -m venv .venv

# Activar (Windows PowerShell)
& .\.venv\Scripts\Activate.ps1

# Activar (Mac/Linux)
source .venv/bin/activate

# Instalar dependencias
cd api
pip install -r requirements.txt
```

**3. Ejecutar Backend (FastAPI)**
```bash
# Desde carpeta api/
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# En otra terminal:
# Backend corriendo en http://127.0.0.1:8000
# Swagger API docs en http://127.0.0.1:8000/docs
```

**4. Ejecutar Frontend (React + Vite)**
```bash
# Desde carpeta frontend/
npm install
npm run dev

# Frontend corriendo en http://localhost:5173
# O usar .env.local para API remota:
# VITE_API_URL=http://127.0.0.1:8000
```

**5. Acceder a la Aplicación**
- **Frontend**: http://localhost:5173/
- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **Demo Users**:
  - Business: `analista.finanzas / Demo1234!`
  - Technical: `analista.tecnologia / Demo1234!`
  - Admin: `admin.valuehub / Demo1234!`

### Troubleshooting

| Problema | Solución |
|----------|----------|
| **API no responde** | Verificar `uvicorn` está corriendo en puerto 8000 |
| **Frontend conecta a Azure API** | Verificar `.env.local` tiene `VITE_API_URL=http://127.0.0.1:8000` |
| **Login falla** | Verificar usuario/contraseña coincide con tabla anterior (case-sensitive) |
| **CORS errors** | Verificar CORS middleware en `api/app/main.py` permite `http://localhost:5173` |

---

## 📚 Documentación

### Guías de Referencia
- **[CLIENT_ARCHITECTURE_REFERENCE.md](docs/CLIENT_ARCHITECTURE_REFERENCE.md)** - Diagrama y descripción arquitectónica para equipos de desarrollo
- **[FABRIC_MEDALLION_SEMANTIC_SETUP.md](docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md)** - Setup de Microsoft Fabric para Executive Dashboard
- **[INSTALLATION_GUIDE.md](docs/INSTALLATION_GUIDE.md)** - Guía de despliegue en Azure Container Apps
- **[MVP_IMPLEMENTATION_LOG.md](docs/MVP_IMPLEMENTATION_LOG.md)** - Changelog detallado de implementaciones

---

## 🤝 Contribución & Desarrollo

### Para Equipos de Desarrollo
Este repositorio está diseñado para ser:
1. **Claro y Limpio**: Código modular, endpoints documentados, naming conventions consistentes
2. **Extensible**: Arquitectura SOLID, services desacoplados, fácil agregar nuevas fases/roles
3. **Production-Ready**: Error handling robusto, logging, validación de entrada, CORS configurado
4. **Well-Tested**: Test cases incluidos para matching service, economics engine, y workflows críticos

### Para Agregar Funcionalidades
1. Revisar `docs/Roadmap (Not yet implemented)` para prioridades
2. Crear rama: `git checkout -b feature/nombre-funcionalidad`
3. Implementar en backend (`api/app/`) y frontend (`frontend/src/`) según corresponda
4. Validar con casos de prueba
5. Push a GitHub y crear Pull Request con descripción clara

### Estructura de Naming
- **Archivos**: snake_case (e.g., `matching_service.py`)
- **Funciones**: snake_case (e.g., `find_related_initiatives()`)
- **Clases**: PascalCase (e.g., `IdeaCase`, `ValueEconomics`)
- **Constantes**: UPPER_SNAKE_CASE (e.g., `SEMANTIC_SYNONYMS`)

---

## 📄 Licencia
Este proyecto está licenciado bajo **MIT License**. Consulta [LICENSE](LICENSE) para más detalles.

## 👥 Contacto & Soporte
Para preguntas técnicas, issues o propuestas de features:
1. Crea un [GitHub Issue](https://github.com/makanto32/AI-Opportunity-Hub/issues)
2. Describe el problema/funcionalidad con contexto claro
3. Incluye pasos para reproducir (si es bug) o use cases (si es feature)

---

**Last Updated**: August 2026  
**Status**: MVP2 Complete ✅ | Phase 3 (Production) In Progress  
**Maintainers**: Development Team
```bash
git clone https://github.com/makanto32/AI-Opportunity-Hub.git
cd AI-Opportunity-Hub
```

**2. Configurar Python Environment**
```bash
# Crear virtual environment
python -m venv .venv

# Activar (Windows PowerShell)
& .\.venv\Scripts\Activate.ps1

# Activar (Mac/Linux)
source .venv/bin/activate

# Instalar dependencias
cd api
pip install -r requirements.txt
```

**3. Ejecutar Backend (FastAPI)**
```bash
# Desde carpeta api/
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# En otra terminal:
# Backend corriendo en http://127.0.0.1:8000
# Swagger API docs en http://127.0.0.1:8000/docs
```

**4. Ejecutar Frontend (React + Vite)**
```bash
# Desde carpeta frontend/
npm install
npm run dev

# Frontend corriendo en http://localhost:5173
# O usar .env.local para API remota:
# VITE_API_URL=http://127.0.0.1:8000
```

**5. Acceder a la Aplicación**
- **Frontend**: http://localhost:5173/
- **API Docs (Swagger)**: http://127.0.0.1:8000/docs
- **Demo Users**:
  - Business: `analista.finanzas / Demo1234!`
  - Technical: `analista.tecnologia / Demo1234!`
  - Admin: `admin.valuehub / Demo1234!`

### Troubleshooting

| Problema | Solución |
|----------|----------|
| **API no responde** | Verificar `uvicorn` está corriendo en puerto 8000 |
| **Frontend conecta a Azure API** | Verificar `.env.local` tiene `VITE_API_URL=http://127.0.0.1:8000` |
| **Login falla** | Verificar usuario/contraseña coincide con tabla anterior (case-sensitive) |
| **CORS errors** | Verificar CORS middleware en `api/app/main.py` permite `http://localhost:5173` |

---

## 📚 Documentación
