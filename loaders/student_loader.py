from models import db, Student

def import_students(data):
    alumnos = data.get('alumnos', [])
    inserted = 0
    ignored = 0

    for item in alumnos:
        name = item.get('nombre')
        email = item.get('correo')
        admission_date = item.get('anio_ingreso')

        print(f"→ Procesando: name={name}, email={email}, anio={admission_date}")

        if name and email and admission_date:
            if Student.query.filter_by(email=email).first():
                print(f"🔁 Estudiante ya existe: {email}")
                ignored += 1
                continue

            try:
                student = Student(name=name, email=email, admission_date=admission_date)
                db.session.add(student)
                inserted += 1
            except Exception as e:
                print(f"❌ Error al insertar estudiante {item}: {e}")
                ignored += 1
        else:
            print(f"⚠️ Datos incompletos: {item}")
            ignored += 1

    db.session.commit()
    print(f"✅ Importación terminada: {inserted} insertados, {ignored} ignorados.")
    return inserted, ignored
