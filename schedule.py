from services.student_service import get_all_students
from services.section_service import get_all_sections
from services.teacher_service import get_all_teachers
from services.classroom_service import get_all_classrooms
from services.student_section_service import get_all_student_section

from flask import Blueprint, send_file, current_app
from ortools.sat.python import cp_model

schedule_bp = Blueprint('schedule', __name__)

def generate_schedule():
    model = cp_model.CpModel()

    student_section = get_all_student_section()
    teachers_temp = get_all_teachers()

    sections = get_all_sections()
    creds = {}
    teachers = {}
    students_in = {}
    rooms = get_all_classrooms()
    capacity = {}

    for section in sections:
        creds[section.id] = section.period.course.credits
        teachers[section.id] = section.teacher.name

    for room in rooms:
        capacity[room.id] = room.capacity
    
    for ss in student_section:
        if ss.section_id in students_in.keys():
            students_in[ss.section_id].append(ss.student_id)
        else:
            students_in[ss.section_id] = [ss.student_id]

    slots = [(d, h) for d in range(5) for h in [0,1,2,3,5,6,7,8]]

    x = {}
    for s in sections:
        for (d, h) in slots:
            for r in rooms:
                if capacity[r.id] >= len(students_in.get(s.id, [])):
                    x[s.id,d,h,r.id] = model.NewBoolVar(f"x_{s.id}_{d}_{h}_{r.id}")
    
    for s in sections:
        model.Add(sum(x[s.id,d,h,r.id] for (d,h) in slots for r in rooms) == 1)

    for s in sections:
        c = creds[s.id]
        for (d,h) in slots:
            valid = []
            for r in rooms:
                ok = True
                for offset in range(c):
                    next_h = h + offset
                    if (d,next_h) not in slots:
                        ok = False
                if ok:
                    valid.append(x[s.id,d,h,r.id])
            model.Add(sum(valid) == sum(x[s.id,d,h,r.id] for r in rooms))
            
    for (d,h) in slots:
        for r in rooms:
            model.Add(
                sum(x[s.id,d,h0,r.id] 
                    for s in sections 
                    for h0 in range(h - creds[s.id] + 1, h+1) 
                    if (d,h0) in slots and h0 + creds[s.id] > h
                ) <= 1
            )
        for p in set(teachers.values()):
            model.Add(
                sum(x[s.id,d,h0,r.id] 
                    for s in sections if teachers[s.id]==p
                    for r in rooms
                    for h0 in range(h - creds[s.id] + 1, h+1)
                    if (d,h0) in slots and h0 + creds[s.id] > h
                ) <= 1
            )
        for stu in set(sum(students_in.values(), [])):
            secs = [s.id for s in sections if stu in students_in.get(s.id, [])]
            model.Add(
                sum(x[s,d,h0,r.id] 
                    for s in secs
                    for r in rooms
                    for h0 in range(h - creds[s] + 1, h+1)
                    if (d,h0) in slots and h0 + creds[s] > h
                ) <= 1
            )
            
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    res = solver.Solve(model)
    if res == cp_model.OPTIMAL or res == cp_model.FEASIBLE:
        assignments = []
        for s in sections:
            for (d,h) in slots:
                for r in rooms:
                    if solver.Value(x[s.id,d,h,r.id]):
                        assignments.append({
                            "section": s,
                            "day": d,
                            "start": f"{9+h if h<4 else 9+(h-1)}:00",
                            "end":   f"{9+h+creds[s.id] if h<4 else 9+(h-1)+creds[s.id]}:00",
                            "room": r
                        })
    
    else:
        print("No hay solución factible con estas restricciones.")
        
    import pandas as pd

    df = pd.DataFrame(assignments)
    # mapea días 0–4 a nombres
    df['day'] = df['day'].map({0:'Lunes',1:'Martes',2:'Miércoles',3:'Jueves',4:'Viernes'})
    df['section'] = df['section'].apply(lambda sec: f"{sec.period.course.name} (Sección {sec.section_number})")
    df['room']    = df['room'].apply(lambda room: room.name)
    day_map = {0:'Lunes',1:'Martes',2:'Miércoles',3:'Jueves',4:'Viernes'}
    for entry in assignments:
        entry['day'] = day_map.get(entry['day'], entry['day'])

    with pd.ExcelWriter('horario_semestre.xlsx', engine='xlsxwriter') as writer:
        workbook  = writer.book
        worksheet = workbook.add_worksheet('Horario')
        writer.sheets['Horario'] = worksheet

        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        time_format   = workbook.add_format({'align': 'center', 'border': 1})
        class_format  = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
        lunch_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'italic': True,
            'border': 1,
            'bg_color': '#D3D3D3'
        })

        days = ['Lunes','Martes','Miércoles','Jueves','Viernes']
        full_hours = [9,10,11,12,13,14,15,16,17]
        full_times = [f"{h}:00" for h in full_hours]
        schedule_map = {(day, t): [] for day in days for t in full_times}
        for entry in assignments:
            print(entry['section'].section_number)
            day = entry['day']
            start_hour = int(entry['start'].split(':')[0])
            duration = creds[entry['section'].id]
            for offset in range(duration):
                h = start_hour + offset
                if h == 13:
                    continue
                t_str = f"{h}:00"
                schedule_map[(day, t_str)].append(f"{entry['section'].period.course.name} ({entry['section'].section_number})\n{entry['room'].name}")

        worksheet.write(0, 0, '', header_format)
        for col, day in enumerate(days, start=1):
            worksheet.write(0, col, day, header_format)

        worksheet.set_column(0, 0, 12)
        for row, t in enumerate(full_times, start=1):
            worksheet.write(row, 0, t, time_format)
            if t == '13:00':
                worksheet.merge_range(row, 1, row, len(days), 'ALMUERZO', lunch_format)
                continue
            for col, day in enumerate(days, start=1):
                cell_text = '\n'.join(schedule_map[(day, t)])
                worksheet.write(row, col, cell_text, class_format)
        for col in range(1, len(days) + 1):
            worksheet.set_column(col, col, 20)

        df.to_excel(writer, index=False, sheet_name='Tabla')

    print("Calendario generado: horario_semestre.xlsx")

@schedule_bp.route('/download_schedule')
def download_schedule():
    # Genera el archivo en memoria/disco
    generate_schedule()
    # Devuelve el Excel
    return send_file(
        'horario_semestre.xlsx',
        as_attachment=True,
        download_name='horario_semestre.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )