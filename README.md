# Sistema de Control Vehicular

Este proyecto es una aplicación web full-stack para el control y gestión de flotas de vehículos, diseñada para registrar recorridos, mantenimientos, y generar reportes.

## Características Principales

- **Gestión de Recorridos:** Inicio y fin de recorridos por parte de los choferes, registrando KM, estados del vehículo y consumo de combustible.
- **Control de Mantenimiento:** Módulo para que el personal de mantenimiento revise, apruebe o solicite ajustes en los informes de recorridos.
- **Roles de Usuario:** Sistema de autenticación y autorización con tres roles: `chofer`, `mantenimiento`, y `admin`.
- **API RESTful:** Backend robusto construido con Flask que expone una API para todas las operaciones.
- **Subida Segura de Archivos:** Integración con servicios compatibles con S3 (como Cloudinary, AWS S3, MinIO) para la subida de imágenes mediante URLs pre-firmadas.
- **Tareas en Segundo Plano:** Uso de Celery y Redis para procesar tareas pesadas como el análisis de imágenes o la generación de reportes.
- **Interfaz Web:** Frontend servido directamente desde Flask con plantillas Jinja2, utilizando TailwindCSS para estilos y Alpine.js para interactividad.
- **Containerización:** El proyecto está completamente containerizado con Docker y Docker Compose para un despliegue fácil y consistente.

## Stack Tecnológico

- **Backend:** Python, Flask, SQLAlchemy, Flask-JWT-Extended
- **Base de Datos:** PostgreSQL
- **Migraciones:** Alembic (integrado con Flask-Migrate)
- **Tareas Asíncronas:** Celery, Redis
- **Frontend:** Jinja2, TailwindCSS, Alpine.js
- **Containerización:** Docker, Docker Compose
- **Tests:** Pytest

## Configuración del Entorno

Sigue estos pasos para configurar tu entorno de desarrollo local.

### 1. Prerrequisitos

- Python 3.11+
- Docker y Docker Compose
- Git

### 2. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd control-vehicular
```

### 3. Configurar Variables de Entorno

Copia el archivo de ejemplo `.env.example` a un nuevo archivo llamado `.env`.

```bash
cp .env.example .env
```

Abre el archivo `.env` y ajusta las variables si es necesario. Las configuraciones por defecto deberían funcionar para el entorno de Docker.

### 4. Instalar Dependencias (para desarrollo local sin Docker)

Si deseas ejecutar la aplicación directamente con Python, necesitas instalar las dependencias. Es recomendable usar un entorno virtual.

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install -r backend/requirements.txt
```

## Ejecución de la Aplicación

Puedes ejecutar la aplicación de dos maneras:

### Método 1: Docker (Recomendado)

Este es el método preferido ya que levanta todos los servicios necesarios (web, base de datos, Redis, Celery) de forma automática.

Desde la raíz del proyecto, ejecuta:
```bash
docker compose up --build
```
La aplicación estará disponible en `http://localhost:5000`.

### Método 2: Python Directo (Desarrollo Local)

Este método es útil para un desarrollo rápido del backend sin levantar todo el stack de Docker. **Nota:** La base de datos y Redis no estarán disponibles a menos que los ejecutes por separado.

Desde la raíz del proyecto, ejecuta:
```bash
python backend/run.py
```
La aplicación se iniciará en modo de desarrollo en `http://localhost:5000`.

## Ejecución de los Tests

Para ejecutar la suite de tests, asegúrate de tener las dependencias instaladas y luego ejecuta el siguiente comando desde la raíz del proyecto:

```bash
PYTHONPATH=./backend pytest
```
