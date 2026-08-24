# AI VALUE HUB - Partner Deployment Kit

Repositorio de referencia para partners que implementan AI VALUE HUB en Azure.
Incluye arquitectura, seguridad, infraestructura como codigo y automatizacion para
llevar una instancia desde sandbox hasta produccion.

## Modelos soportados

| Modelo | Uso recomendado | Operacion |
|---|---|---|
| SaaS administrado | Clientes que priorizan rapidez y actualizaciones continuas | Plataforma multi-tenant operada por el proveedor |
| Instancia dedicada | Clientes regulados o con requisitos estrictos de aislamiento | Recursos desplegados en la suscripcion del cliente |

La primera version del kit implementa una **instancia dedicada por cliente** y
mantiene configuracion, identidad y datos separados por ambiente. Esta base permite
evolucionar posteriormente a un SaaS multi-tenant sin crear variantes del producto.

## Inicio rapido

1. Revise [la arquitectura](docs/architecture-overview.md) y
   [los prerrequisitos](docs/deployment-guide.md).
2. Ejecute `./scripts/preflight.ps1` para comprobar Azure CLI, permisos y parametros.
3. Despliegue un sandbox con `./scripts/deploy.ps1 -Environment dev`.
4. Configure Entra ID siguiendo [la guia de identidad](docs/entra-onboarding.md).
5. Ejecute `./scripts/validate-deployment.ps1` y complete
   [la lista de produccion](docs/production-readiness-checklist.md).

## Deploy to Azure

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmakanto32%2FAI-VALUE-HUB%2Fmain%2Finfra%2Fmain.json)

El boton es apropiado para sandbox y usa el artefacto compilado de `main`. Para
produccion use una release estable y el script o un pipeline con `what-if`, aprobacion
y validacion posterior.

## Principios del kit

- Managed Identity y Key Vault; ningun secreto se almacena en Git.
- App Registration y roles de aplicacion separados por ambiente.
- Configuracion del cliente fuera del codigo de la aplicacion.
- Observabilidad, respaldo, recuperacion y rollback incluidos en la preparacion.
- Releases versionadas y compatibles entre aplicacion e infraestructura.

Consulte [el modelo de soporte y gobierno](docs/partner-operating-model.md) antes de
iniciar una implementacion con un cliente.
