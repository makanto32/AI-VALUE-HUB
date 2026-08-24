# Onboarding de Microsoft Entra ID

## Registros recomendados

Use dos App Registrations por ambiente:

- **Web:** cliente publico/confidencial segun la implementacion; redirect URI exacta.
- **API:** expone un Application ID URI y roles de aplicacion.

El script `configure-entra.ps1` crea una base de registro unico para pruebas. Para
produccion, aplique la separacion anterior mediante el proceso corporativo y revision
de seguridad.

## Secuencia

1. Cree los registros en el tenant del cliente.
2. Configure redirect y logout URIs HTTPS exactas; no use comodines.
3. Exponga el scope delegado de acceso a la API.
4. Defina roles `Reader`, `Contributor`, `Approver` y `Administrator`.
5. Conceda permisos minimos y obtenga admin consent cuando sea necesario.
6. Asigne usuarios o grupos a roles en la Enterprise Application.
7. Establezca `entraTenantId`, `entraClientId` y `entraAudience` en Bicep.
8. Pruebe usuario autorizado, usuario sin rol, token expirado y audience incorrecta.

## Checklist de validacion

- La API rechaza tokens de otros tenants.
- No hay secretos de cliente en el navegador.
- Los redirect URI coinciden con el dominio productivo.
- El rol administrativo no se asigna por defecto.
- Conditional Access y MFA se validan con el equipo de identidad del cliente.
- Existe propietario tecnico y propietario de negocio para cada registro.
