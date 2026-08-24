# Lista de preparacion para produccion

## Plataforma

- [ ] Release y digests de imagen aprobados.
- [ ] `what-if` revisado por una persona distinta al implementador.
- [ ] Tags, presupuesto y alertas configurados.
- [ ] Escalamiento y prueba de carga aprobados.
- [ ] Dominio, certificados, DNS y red validados.

## Seguridad

- [ ] App Registrations separadas y con propietarios.
- [ ] Roles de aplicacion y admin consent revisados.
- [ ] RBAC de Azure revisado por minimo privilegio.
- [ ] Secretos en Key Vault y rotacion definida.
- [ ] Imagenes escaneadas; hallazgos criticos resueltos.
- [ ] Clasificacion, residencia y retencion de datos aprobadas.

## Operacion

- [ ] Logs, metricas, alertas y paneles operativos activos.
- [ ] SLO, soporte, escalamiento y contactos acordados.
- [ ] Backup, restauracion y continuidad probados.
- [ ] Runbooks de incidente, rollback y rotacion disponibles.
- [ ] `validate-deployment.ps1` completado sin errores.
- [ ] Pruebas de autenticacion, autorizacion e integraciones aprobadas.

## Entrega

- [ ] Arquitectura final y excepciones documentadas.
- [ ] Inventario de recursos, identidades e integraciones entregado.
- [ ] Evidencia de cambio almacenada segun politica del cliente.
- [ ] Aceptacion del cliente y transicion a operaciones completadas.
