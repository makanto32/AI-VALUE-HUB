# Dimensionamiento y costos

## Variables principales

- replicas minimas y maximas de API y web;
- CPU, memoria, solicitudes y ejecucion en Container Apps;
- volumen, redundancia y transacciones de Storage;
- ingesta y retencion de Log Analytics;
- ACR, egress, WAF, Private Endpoints y red privada opcional;
- servicios de IA y Fabric integrados por el cliente.

## Perfiles iniciales

| Perfil | Replicas minimas | Storage | Logs | Uso |
|---|---:|---|---:|---|
| Dev | 0 | LRS | 30 dias | Pruebas y demos |
| Prod | 1 por app | GRS | 90 dias | Base de produccion |

Estos valores son puntos de partida, no una cotizacion. Antes de aprobar produccion,
use Azure Pricing Calculator con la region y trafico del cliente, defina presupuesto y
alertas, y ejecute una prueba de carga representativa. Revise costo real tras 14 y 30
dias y ajuste escalamiento y retencion.
