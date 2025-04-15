# SGA - Sistema de Gestión Académica

Este proyecto utiliza Python, Flask y MySQL para gestionar cursos, periodos, profesores, alumnos, evaluaciones, etc.

## Requisitos Previos

- Tener **MySQL** instalado y en ejecución.
- Tener **Python 3.9** o superior instalado.

## Pasos para Configurar el Proyecto

### 1. Crear la Base de Datos

Abre la consola de MySQL y ejecuta lo siguiente para crear la base de datos `sga_db`:

```sql
CREATE DATABASE sga_db;
```

### 2. Crear y Activar un Entorno Virtual (venv)

Desde la raíz del proyecto, ejecuta:

**En Linux o macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

**En windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar las Dependencias

Con el entorno virtual activado, instala las dependencias definidas en el archivo requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación

Inicia la aplicación Flask con el siguiente comando:

```bash
flask run
```

La aplicación estará disponible en http://127.0.0.1:5000.