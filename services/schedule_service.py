from services.section_service import get_all_sections
from services.classroom_service import get_all_classrooms
from services.student_section_service import get_all_student_section

from ortools.sat.python import cp_model
import pandas as pd

def load_schedule_data():
    student_section = get_all_student_section()
    sections = get_all_sections()
    creds = {sec.id: sec.period.course.credits for sec in sections}
    teachers = {sec.id: sec.teacher.name for sec in sections}
    students_in = {}
    for ss in student_section:
        students_in.setdefault(ss.section_id, []).append(ss.student_id)
    rooms = get_all_classrooms()
    capacity = {r.id: r.capacity for r in rooms}
    slots = [(d, h) for d in range(5) for h in [0,1,2,3,5,6,7,8]]
    return sections, creds, teachers, students_in, rooms, capacity, slots

def define_variables(model, sections, slots, rooms, capacity, students_in):
    x = {}
    for s in sections:
        for (d, h) in slots:
            for r in rooms:
                if capacity[r.id] >= len(students_in.get(s.id, [])):
                    x[s.id,d,h,r.id] = model.NewBoolVar(f"x_{s.id}_{d}_{h}_{r.id}")
    return x

def apply_constraints(model, x, sections, creds, teachers, students_in, slots, rooms):
    for s in sections:
        model.Add(sum(x[s.id,d,h,r.id] for (d,h) in slots for r in rooms if (s.id,d,h,r.id) in x) == 1)

    for s in sections:
        c = creds[s.id]
        for (d,h) in slots:
            valid = []
            for r in rooms:
                ok = all((d,h+offset) in slots for offset in range(c))
                if ok and (s.id,d,h,r.id) in x:
                    valid.append(x[s.id,d,h,r.id])
            model.Add(sum(valid) == sum(x[s.id,d,h,r.id] for r in rooms if (s.id,d,h,r.id) in x))

    for (d,h) in slots:
        for r in rooms:
            model.Add(
                sum(x[s.id,d,h0,r.id]
                    for s in sections
                    for h0 in range(h - creds[s.id] + 1, h+1)
                    if (d,h0) in slots and h0 + creds[s.id] > h and (s.id,d,h0,r.id) in x
                ) <= 1
            )

        for p in set(teachers.values()):
            model.Add(
                sum(x[s.id,d,h0,r.id]
                    for s in sections if teachers[s.id] == p
                    for r in rooms
                    for h0 in range(h - creds[s.id] + 1, h+1)
                    if (d,h0) in slots and h0 + creds[s.id] > h and (s.id,d,h0,r.id) in x
                ) <= 1
            )

        for stu in set(sum(students_in.values(), [])):
            secs = [s.id for s in sections if stu in students_in.get(s.id, [])]
            model.Add(
                sum(x[s,d,h0,r.id]
                    for s in secs
                    for r in rooms
                    for h0 in range(h - creds[s] + 1, h+1)
                    if (d,h0) in slots and h0 + creds[s] > h and (s,d,h0,r.id) in x
                ) <= 1
            )

def extract_schedule_result(solver, x, sections, creds, slots, rooms):
    assignments = []
    for s in sections:
        for (d,h) in slots:
            for r in rooms:
                if (s.id,d,h,r.id) in x and solver.Value(x[s.id,d,h,r.id]):
                    assignments.append({
                        "section": s,
                        "day": d,
                        "start": f"{9+h if h<4 else 9+(h-1)}:00",
                        "end": f"{9+h+creds[s.id] if h<4 else 9+(h-1)+creds[s.id]}:00",
                        "room": r
                    })
    return assignments

def solve_schedule(sections, creds, teachers, students_in, rooms, capacity, slots):
    model = cp_model.CpModel()
    x = define_variables(model, sections, slots, rooms, capacity, students_in)
    apply_constraints(model, x, sections, creds, teachers, students_in, slots, rooms)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    res = solver.Solve(model)
    if not (res == cp_model.OPTIMAL or res == cp_model.FEASIBLE):
        return None

    return extract_schedule_result(solver, x, sections, creds, slots, rooms)

def write_schedule_excel(assignments, creds):
    df = pd.DataFrame(assignments)
    df['day'] = df['day'].map({0:'Lunes',1:'Martes',2:'Miércoles',3:'Jueves',4:'Viernes'})
    df['section'] = df['section'].apply(lambda sec: f"{sec.period.course.name} (Sección {sec.section_number})")
    df['room'] = df['room'].apply(lambda room: room.name)

    days = ['Lunes','Martes','Miércoles','Jueves','Viernes']
    full_hours = [9,10,11,12,13,14,15,16,17]
    full_times = [f"{h}:00" for h in full_hours]
    schedule_map = {(day, t): [] for day in days for t in full_times}

    for entry in assignments:
        day = entry['day']
        start_hour = int(entry['start'].split(':')[0])
        duration = creds[entry['section'].id]
        for offset in range(duration):
            h = start_hour + offset
            if h == 13:
                continue
            t_str = f"{h}:00"
            key = (days[day], t_str)
            if key not in schedule_map:
                schedule_map[key] = []
            schedule_map[key].append(f"{entry['section'].period.course.name} ({entry['section'].section_number})\n{entry['room'].name}")

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
    return True

def generate_schedule():
    data = load_schedule_data()
    assignments = solve_schedule(*data)
    if assignments is None:
        return False
    write_schedule_excel(assignments, data[1])
    return True
