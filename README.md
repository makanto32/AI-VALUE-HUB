# AI-OPPORTUNIY-HUB

Base inicial del proyecto alineada al roadmap del documento de arquitectura.

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
