# Modelo operativo para partners

## RACI base

| Actividad | Producto | Partner | Cliente |
|---|---|---|---|
| Publicar imagenes y releases | Responsable | Informado | Informado |
| Desplegar infraestructura | Consultado | Responsable | Aprobador |
| Configurar Entra ID y red | Consultado | Responsable | Aprobador |
| Configurar integraciones | Consultado | Responsable | Responsable de datos |
| Operar plataforma | Soporte L3 | L1/L2 | Segun contrato |
| Aprobar produccion | Consultado | Consultado | Responsable |

## Reglas de distribucion

- Despliegue releases etiquetadas, nunca ramas de desarrollo.
- No modifique imagenes ni cree forks por cliente.
- Mantenga extensiones de infraestructura en un repositorio del cliente.
- Reporte vulnerabilidades por un canal privado, no mediante issues publicos.
- Adjunte version del kit, region, correlation ID y evidencia sanitizada al escalar.

## Ciclo de soporte

El partner realiza triage, verifica salud de Azure, reproduce el problema y elimina
datos sensibles. El equipo de producto atiende defectos reproducibles de imagenes o
contratos soportados. Cambios de red, identidad, datos o integraciones del cliente
permanecen bajo responsabilidad del partner y del cliente.

## Personalizacion

Configuracion, branding aprobado e integraciones se mantienen fuera del codigo del
producto. Una necesidad que cambie contratos compartidos debe entrar al roadmap del
producto y publicarse como nueva version compatible.
