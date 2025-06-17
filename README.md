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
flask --app run run
```

### 5. Ejecutar los test

Ejecuta los test

```bash
pytest --cov=services --cov-report=term
```

La aplicación estará disponible en http://127.0.0.1:5000.

## Consejos
- Para crear una sección, debo crear un perido. Para crear un periodo, debo crear un curso. Cada uno de estos hijos se crea desde la vista principal del padre. (símbolo de ojo verde)
- Para crear una sección debe haber, al menos, un profesor creado en la base de datos. Para crear un profesor se debe ingresar a la vista general de profesores accesible desde el sidebar.
- Solo se puede agregar nota a alumnos desde una tarea creada con fecha de entrega anterior a la fecha actual.

## Texto no necesario pero explicacion para ustedes

✅ Pruebas implementadas (Unit Testing)
Todas las pruebas están centradas en el directorio services/, donde reside la lógica de negocio de la aplicación.
No se testean ni views/, ni templates/, ni directamente models/, ya que no contienen reglas o decisiones de negocio relevantes.

🧪 Lista de tests implementados
1. test_calculate_final_grades.py
Objetivo: Verificar que el cálculo de nota final (final_grade) para cada alumno se realice correctamente.

    Qué se evalúa: Que se aplique bien la ponderación de cada tarea, según sus pesos relativos.

2. test_report_tasks.py
Objetivo: Validar la generación del reporte de notas por tarea.

    Qué se evalúa: Que se generen correctamente las notas individuales, junto con resumen de nota mínima, máxima y promedio para la tarea.

3. test_report_students.py
Objetivo: Verificar el contenido del certificado de notas de un estudiante.

    Qué se evalúa: Que se incluyan correctamente las evaluaciones, tareas y promedios para cada curso cerrado.

4. test_section_update.py
Objetivo: Asegurar que no se puedan editar secciones cerradas (open = False).

    Qué se evalúa: Que se arroje un error si se intenta actualizar una sección ya cerrada.

Los warnings son porque en cuando hacemos ```section = Section.query.get_or_404(section_id)``` se considera obsoleto para la ersion de flask  y se deberia cambiar por:

```bash
from flask import abort

section = db.session.get(Section, section_id)
if section is None:
    abort(404)
```

pero esto no causa error ni en el funcionamiento ni los test, me da alta paja cambiarlo la verdad, pero eso.