# SGA - Sistema de Gestión Académica

Este proyecto utiliza Python, Flask y MySQL para gestionar cursos, periodos, profesores, alumnos, evaluaciones, etc.

## Requisitos Previos

- Tener **MySQL** instalado y en ejecución.
- Tener **Python 3.9** o superior instalado.

## Pasos para Configurar el Proyecto

### 1. Crear la Base de Datos

Abre la consola de MySQL y ejecuta los siguientes comandos para crear la base de datos `sga_db` y un usuario con los permisos correspondientes:
```sql
CREATE USER 'sga_user'@'localhost' IDENTIFIED BY 'sga_user';
GRANT ALL PRIVILEGES ON sga_db.* TO 'sga_user'@'localhost';
FLUSH PRIVILEGES;
```
y luego
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

## Consejos
- Para crear una sección, debo crear un perido. Para crear un periodo, debo crear un curso. Cada uno de estos hijos se crea desde la vista principal del padre. (símbolo de ojo verde)
- Para crear una sección debe haber, al menos, un profesor creado en la base de datos. Para crear un profesor se debe ingresar a la vista general de profesores accesible desde el sidebar.
- Solo se puede agregar nota a alumnos desde una tarea creada con fecha de entrega anterior a la fecha actual.