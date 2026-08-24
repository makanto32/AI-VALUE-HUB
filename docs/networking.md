# Perfiles de red

## Baseline

El baseline usa ingress HTTPS publico en Container Apps y endpoints publicos de Azure
protegidos por identidad y RBAC. Es apropiado para sandbox y clientes sin requisito
de aislamiento de red.

## Perfil privado

Para produccion privada se requiere una extension de arquitectura que incluya:

- Container Apps Environment integrado a VNet;
- Private Endpoints y Private DNS para Storage, Key Vault y ACR;
- ingress mediante WAF, Application Gateway o Front Door segun el escenario;
- egress con Azure Firewall/NAT y allowlist de destinos;
- resolucion DNS hibrida y conectividad corporativa;
- deshabilitacion comprobada de acceso publico.

## Decisiones previas

Confirme rangos IP sin superposicion, ownership de DNS, inspeccion TLS, rutas forzadas,
dependencias SaaS, conectividad on-premises y responsabilidad del WAF. Documente
excepciones y pruebe recuperacion cuando una dependencia no este disponible.
