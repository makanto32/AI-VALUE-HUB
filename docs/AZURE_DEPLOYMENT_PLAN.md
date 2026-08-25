# AI Value Hub Azure Deployment Plan

## Objetivo
Provisionar la base cloud-native de AI Value Hub en Azure y publicar imagenes validadas en Azure Container Apps.

## Estado de arquitectura verificado
- La API FastAPI usa reglas deterministicas locales para validacion de negocio, revision tecnica automatica, matching y economia de valor.
- Microsoft Foundry no esta integrado en el runtime actual. Su uso para evaluaciones asistidas por modelos es una evolucion propuesta, no una dependencia del MVP.
- Existe un manifiesto de Azure Container Apps para la API con ingress HTTPS, identidad administrada asignada por el sistema, imagen en ACR y SQLite persistido en Azure Files.
- La plantilla Bicep crea el Container Apps Environment y recursos compartidos, pero no declara todavia las Container Apps de API y frontend.
- El frontend tiene Dockerfile y automatizacion de actualizacion, pero este repositorio no contiene evidencia equivalente de su manifiesto activo.

## Foundation actual
- IaC en Bicep para recursos compartidos.
- Dockerfile para API FastAPI.
- Dockerfile para frontend React/Vite servido con Nginx.
- Azure Blob Storage mediante identidad administrada o connection string, con fallback local en desarrollo.
- SQLite es la persistencia activa; PostgreSQL Flexible Server es opcional en la foundation y requiere adaptar la aplicacion antes de usarlo.
- Base de secretos y configuracion para una posible integracion futura con Foundry.
- Despliegue pensado para `az containerapp up --source` cuando ACR no este disponible en la suscripcion.

## Flujo de despliegue
1. Validar localmente frontend y API.
2. Construir imagenes versionadas por MVP.
3. Publicar imagenes en Azure Container Registry.
4. Crear o actualizar Container Apps apuntando al tag validado.
5. Repetir en cada MVP aprobado.

## Brechas antes de produccion
- Incorporar API y frontend al Bicep para conseguir un despliegue completo y repetible.
- Implementar validacion de tokens de Microsoft Entra ID; `AIHUB_AUTH_PROVIDER=entra` devuelve actualmente HTTP 501.
- Migrar el store basado en `sqlite3` a PostgreSQL antes de declarar PostgreSQL como sistema de registro.
- Completar RBAC de minimo privilegio, referencias de Key Vault, private networking, alertas, backups y pruebas de recuperacion.
- Agregar CI/CD para build, analisis, publicacion y promocion de imagenes inmutables.
- Integrar Microsoft Foundry solo si la evaluacion de calidad, costo y gobierno justifica sustituir o complementar las reglas deterministicas actuales.