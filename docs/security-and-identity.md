# Seguridad e identidad

## Controles base

- Managed Identity para acceso de runtime a Azure.
- RBAC de minimo privilegio para Blob Storage, Key Vault y ACR.
- TLS obligatorio; Shared Key y acceso publico a blobs deshabilitados.
- Secretos exclusivamente en Key Vault, nunca en parametros, logs o Git.
- Recursos y App Registrations separados por ambiente.
- Imagenes inmutables, escaneadas y con procedencia verificable.

## Modelo de autorizacion

Entra ID autentica usuarios. La API valida firma, issuer, audience, expiracion y roles.
Use roles de aplicacion (`Reader`, `Contributor`, `Approver`, `Administrator`) como
contrato estable. Los grupos pueden asignarse a esos roles, pero la aplicacion no debe
autorizar por nombres de grupos.

## Produccion regulada

El template base permite endpoints publicos protegidos por identidad. Para requisitos
de red privada agregue, mediante un perfil aprobado, VNet integration, Private
Endpoints para Storage y Key Vault, Private DNS, egress controlado y un punto de
entrada como Application Gateway o Front Door con WAF. No marque el despliegue como
privado hasta verificar DNS, rutas y bloqueo efectivo del acceso publico.

## Evidencia requerida

Conserve el resultado de `what-if`, asignaciones RBAC, consentimiento de Entra,
escaneo de imagenes, pruebas de restauracion, alertas y validacion posterior al
despliegue como evidencia de cambio.
