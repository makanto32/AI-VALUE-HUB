# Fabric Medallion + Semantic Model (Admin Dashboard)

## Objetivo
Conectar el dashboard ejecutivo de admin a un modelo semántico alimentado por registros actuales de la base de datos transaccional.

## Estado implementado en API
- Fuente de métricas configurable por variable de entorno:
  - `AIHUB_DASHBOARD_METRICS_SOURCE=local|semantic`
- Archivo semántico configurable:
  - `AIHUB_SEMANTIC_METRICS_FILE=/ruta/a/executive_dashboard_current.json`
- Endpoint para refrescar pipeline medallion:
  - `POST /admin/metrics/semantic/refresh`
- Pipeline medallion en backend:
  - Bronze: `ideas_raw.jsonl`
  - Silver: `ideas_clean.csv`
  - Gold: `executive_dashboard_current.json`, `fact_dashboard_kpis.csv`

## Flujo recomendado en Azure (desde versión ACR)
1. Desplegar la API con esta versión de imagen.
2. Configurar variables de entorno en Container App:
   - `AIHUB_DASHBOARD_METRICS_SOURCE=semantic`
   - `AIHUB_FABRIC_DATA_DIR=/mnt/data/fabric` (o ruta persistente equivalente)
   - `AIHUB_SEMANTIC_METRICS_FILE=/mnt/data/fabric/gold/executive_dashboard_current.json`
3. Ejecutar `POST /admin/metrics/semantic/refresh` para generar Bronze/Silver/Gold.
4. En Microsoft Fabric:
   - Ingerir Bronze/Silver/Gold desde la ruta persistida o Blob/Lakehouse.
   - Crear modelo semántico sobre tabla Gold y tablas de soporte.

## Observación importante
- En esta fase, el dashboard consume el artefacto Gold semántico (`executive_dashboard_current.json`) generado desde datos reales de BD.
- Para conexión nativa directa a un dataset de Fabric (XMLA/DAX), se requiere una capa adicional de conector autenticado a Power BI/Fabric APIs.
