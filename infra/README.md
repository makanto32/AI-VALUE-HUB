# AI Value Hub Azure Foundation

Infraestructura base y artefactos operativos para desplegar AI Value Hub en Azure Container Apps.

## Recursos incluidos
- Azure Container Apps Environment.
- Azure Container Registry opcional.
- Azure Storage Account con contenedores `documents` y `artifacts`.
- Azure Key Vault con RBAC.
- Log Analytics Workspace.
- Application Insights.
- User Assigned Managed Identity.
- PostgreSQL Flexible Server opcional.

## Alcance del runtime
- La aplicacion actual ejecuta validaciones deterministicas y un orquestador local; no llama a Microsoft Foundry.
- Esta foundation prepara hosting, observabilidad, secretos y persistencia para una integracion futura si se valida su necesidad.
- La plantilla Bicep crea el Container Apps Environment, pero las aplicaciones se administran hoy mediante manifiestos y scripts separados.

## Despliegue rapido
```powershell
Set-Location infra
.\deploy-foundation.ps1
```

## Actualizar contenedores en Azure Container Apps
Para publicar una nueva imagen de API y/o frontend en Container Apps ya existentes:

```powershell
Set-Location infra
.\update-container-apps.ps1 `
	-ResourceGroupName "rg-ai-opportunity-hub-dev" `
	-ApiContainerAppName "aiopportunityhub-dev-api" `
	-ApiImage "<acr-login-server>/aihub/api:mvp2.1" `
	-FrontendContainerAppName "aiopportunityhub-dev-frontend" `
	-FrontendImage "<acr-login-server>/aihub/frontend:mvp2.1"
```

Notas:
- Puedes actualizar solo API o solo frontend enviando solo los parametros correspondientes.
- El script valida que la Container App exista antes de actualizar.
- Se crea una nueva revision con sufijo de timestamp para trazabilidad.

## Parametros
Edita `main.parameters.json` para cambiar:
- `location`
- `appName`
- `environmentName`
- `enablePostgres`
- `tags`

## Notas
- `enablePostgres` esta desactivado por defecto para evitar requerir un secreto en el primer despliegue.
- `enableAcr` esta desactivado por defecto porque la suscripcion actual no soporta ACR.
- Habilitar PostgreSQL solo crea el recurso. La API actual usa `sqlite3`; se requiere migrar driver, esquema y configuracion antes de conectarla.
- Cuando quieras aprovisionar PostgreSQL, agrega `postgresAdminLogin` y `postgresAdminPassword` en la llamada de despliegue.
- Este paquete crea la base para que luego publiquemos `frontend` y `api` como Container Apps usando imagenes versionadas por MVP.
- Los endpoints, claves o identificadores de una futura integracion con Foundry deben resolverse via identidad administrada, Key Vault o configuracion segura.