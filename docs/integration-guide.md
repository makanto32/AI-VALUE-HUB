# Guia de integraciones

## Patron

Las integraciones son configuracion del tenant, no forks del producto. Use Managed
Identity para Azure y OAuth 2.0 para sistemas externos. Almacene endpoints no secretos
en configuracion y credenciales en Key Vault.

## Contrato minimo

Cada integracion debe documentar:

- propietario, sistema y ambiente;
- autenticacion y permisos requeridos;
- esquema y version del contrato;
- limites, timeouts y politica de reintentos;
- idempotencia y correlacion;
- clasificacion, residencia y retencion de datos;
- monitoreo, runbook y criterio de desactivacion.

## Implementacion

1. Valide conectividad y DNS desde Container Apps.
2. Cree una identidad o credencial dedicada con minimo privilegio.
3. Configure secretos en Key Vault fuera del despliegue Bicep compartido.
4. Pruebe errores 401, 403, 429, timeout y datos invalidos.
5. Propague un correlation ID sin registrar tokens ni datos sensibles.
6. Defina una cola o proceso de recuperacion para operaciones asincronas.

No introduzca credenciales del cliente en issues, pipelines, archivos `.bicepparam` ni
paquetes de soporte.
