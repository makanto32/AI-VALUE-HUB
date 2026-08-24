# Guia de despliegue

## Prerrequisitos

- Suscripcion Azure y permisos para crear recursos y asignar roles.
- Azure CLI con Bicep y PowerShell 7.
- Tenant Entra ID con permiso para registrar aplicaciones o un administrador disponible.
- Imagenes OCI versionadas de API y frontend.
- ACR existente si las imagenes son privadas.

## Sandbox

1. Clone una release, no la rama `main`.
2. Edite `infra/environments/dev.bicepparam` y reemplace todos los valores `REPLACE`.
3. Ejecute:

```powershell
./scripts/preflight.ps1 -ParametersFile ./infra/environments/dev.bicepparam
./scripts/deploy.ps1 -Environment dev
```

El script ejecuta `what-if` antes de crear recursos. Revise eliminaciones, cambios de
SKU y cambios de identidad antes de aprobar.

## Produccion

1. Copie `prod.bicepparam.example` a un archivo no versionado.
2. Use tags inmutables o digests para ambas imagenes.
3. Ejecute el pipeline corporativo con federacion OIDC y aprobacion del ambiente.
4. Configure dominio, Entra ID e integraciones.
5. Ejecute `validate-deployment.ps1` y la lista de preparacion productiva.

```powershell
./scripts/deploy.ps1 `
  -Environment prod `
  -ParametersFile ./infra/environments/prod.bicepparam `
  -SubscriptionId <subscription-id>
```

## Rollback

Container Apps conserva revisiones. Antes de actualizar, registre la revision activa y
los tags de imagen. Si falla la validacion, reactive la revision anterior y revierta
cualquier migracion de datos mediante el procedimiento publicado con esa release.
Nunca use un tag mutable como `latest` en produccion.
