# AI-OPPORTUNIY-HUB

Base inicial del proyecto alineada al roadmap del documento de arquitectura.

## Licencia
Este repositorio está licenciado bajo MIT.
Consulta los términos completos en [LICENSE](LICENSE).

## 🚀 Vistas de Arquitectura (Live)

Accede directamente a las vistas visuales del proyecto en GitHub Pages:

- **📊 [Centro de Control](https://makanto32.github.io/AI-Opportunity-Hub/)** - Menú de navegación principal
- **💡 [AI Value Hub Demo](https://makanto32.github.io/AI-Opportunity-Hub/ai-value-hub-demo.html)** - Flujo visual del demo
- **🏗️ [Arquitectura (EN)](https://makanto32.github.io/AI-Opportunity-Hub/architecture-diagram.html)** - Diagrama técnico completo
- **🏗️ [Arquitectura (ES)](https://makanto32.github.io/AI-Opportunity-Hub/architecture-diagram.es.html)** - Versión en español
- **📈 [Arquitectura Fabric + Dashboard](https://makanto32.github.io/AI-Opportunity-Hub/architecture-fabric-live.html)** - Integración live de Microsoft Fabric para métricas ejecutivas
- **📖 [Use Case Factory](https://makanto32.github.io/AI-Opportunity-Hub/AI_Use_Case_Factory_Company_Context_Engine_EN.html)** - Documento de referencia ejecutivo

## Integracion Microsoft Fabric
- Provider semantico habilitado para dashboard ejecutivo via Power BI / Fabric.
- Scripts de soporte:
	- `scripts/fabric-provision-semantic.ps1`
	- `scripts/fabric-sync-semantic.ps1`
- Referencia de setup: `docs/FABRIC_MEDALLION_SEMANTIC_SETUP.md`

## MVP1 implementado
- Idea intake.
- Context Engine por tenant para evaluar viabilidad con linea base de negocio.
- Business validation + filtro tecnico inicial.
- Estado del caso de uso con motivo de rechazo (fase negocio o tecnica).
- UI con flujo de login demo, captura de contexto y vista separada de "Mis ideas".
- Aislamiento por usuario: cada sesion solo consulta sus ideas.
- Idioma canonico interno en espanol con base preparada para multilenguaje (es/en/pt).

## MVP2 en progreso (backend)
- Persistencia de estado y artefactos en DB local (SQLite) lista para evolucionar a PostgreSQL.
- Metadata de archivos de contexto persistida en DB y contenido en Blob (Azure o fallback local).
- Validacion tecnica explicita por endpoint dedicado.
- Generacion de Architecture Package por idea, con componentes, integraciones, riesgos y pasos de despliegue.
- Response Composer inicial para devolver resumen ejecutivo y siguientes acciones.

Endpoints MVP2 agregados:
- `POST /ideas/{idea_id}/technical-validate`
- `POST /ideas/{idea_id}/architecture-package`

## Autenticacion (demo + previsión Entra)
- Proveedor activo por defecto: `AIHUB_AUTH_PROVIDER=demo`.
- Usuarios de prueba:
	- `analista.finanzas / Demo1234!`
	- `analista.riesgo / Demo1234!`
- Endpoints:
	- `POST /auth/login`
	- `GET /auth/me`
	- `GET /ideas/mine`
- Prevision Entra ID incluida en codigo: si `AIHUB_AUTH_PROVIDER=entra`, la API responde `501` hasta completar la integracion productiva.

## Estructura
- `frontend`: React + Vite.
- `api`: FastAPI.
- `workers`: reservado para siguientes MVPs.
- `infra`: reservado para IaC en siguientes MVPs.
- `docs`: notas de alcance por MVP.

## Documentación de referencia para clientes
- Guía de arquitectura: [docs/CLIENT_ARCHITECTURE_REFERENCE.md](docs/CLIENT_ARCHITECTURE_REFERENCE.md)
- Diagrama profesional en PDF: [docs/AI_Opportunity_Hub_Architecture_Reference.pdf](docs/AI_Opportunity_Hub_Architecture_Reference.pdf)

## Ejecutar API
```bash
pip install -r requirements.txt
uvicorn api.app.main:app --reload --port 8000
```

## Ejecutar Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173
API: http://localhost:8000
