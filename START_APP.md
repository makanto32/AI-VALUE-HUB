# Iniciar AI Value Hub

## Evaluacion con Docker

Desde la raiz del repositorio:

```powershell
docker compose up --build
```

- Aplicacion: `http://localhost:8080`
- API y Swagger: `http://localhost:8000/docs`
- Usuario administrador: `admin.valuehub`
- Contrasena: `Demo1234!`

La primera pantalla permite seleccionar ES, EN o PT antes de continuar al inicio de sesion. Para detener los contenedores sin borrar los datos, ejecuta `docker compose down`. Para reiniciar completamente la evaluacion, ejecuta `docker compose down --volumes`.

## Desarrollo local en Windows

Después de crear `.venv`, instalar `api/requirements.txt` y ejecutar `npm install` en `frontend`, usa:

```powershell
.\start-local-session.ps1
```

El script inicia la API en `http://127.0.0.1:8000` y Vite en `http://127.0.0.1:5174`.

Consulta [README.md](README.md) para la instalacion completa y [docs/PARTNER_DEPLOYMENT_GUIDE.md](docs/PARTNER_DEPLOYMENT_GUIDE.md) para preparar un despliegue de cliente.
