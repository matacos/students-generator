import psycopg2
from random import random
from random import choice
from random import sample
from random import triangular
from math import floor
import names
import sys
import lorem

conn_string ="postgresql://postgres@127.0.0.1:5444/postgres"
try:
    conn_string=sys.argv[1]
except Exception:
    pass

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

def nuevo_profesor():
    dni="".join([str(floor(random()*10)) for x in range(8)])
    email=dni+"@gmail.com"
    name = names.get_first_name()
    surname = names.get_last_name()
    cursor.execute("""insert into users(
        username,
        password,
        email,
        name,
        surname,
        token,
        token_expiration
    ) values (%s,%s,%s,%s,%s,%s,NOW());""",(dni,dni,email,name,surname,dni,))
    conn.commit()
    cursor.execute("""
    insert into professors(username) values (%s);
    """,(dni,))
    conn.commit()
    return dni

def nuevo_estudiante():
    padron="".join([str(floor(random()*10)) for x in range(5)])
    email=padron+"@gmail.com"
    name = names.get_first_name()
    surname = names.get_last_name()
    cursor.execute("""insert into users(
        username,
        password,
        email,
        name,
        surname,
        token,
        token_expiration
    ) values (%s,%s,%s,%s,%s,%s,NOW())  on conflict do nothing;""",(padron,padron,email,name,surname,padron,))
    prioridad=random()*100
    conn.commit()
    cursor.execute("""
    insert into students(username,priority) values (%s,%s) on conflict do nothing;
    """,(padron,prioridad,))
    conn.commit()
    cursor.execute("""
    insert into degree_enrollments values (10,%s)
    """,(padron,))
    return padron

def materia_de_depto(depto):
    cursor.execute("""select code from subjects where department_code = %s""",(depto,))
    got=cursor.fetchall()
    codes=[x[0] for x in got]
    return choice(codes)



def asignar_profesor(course,role):
    professor_id=nuevo_profesor()
    cursor.execute("""
    insert into professors_roles(professor,course,role)
    values (%s,%s,%s)
    """,(professor_id,course,role,))
    conn.commit()

def asignar_profesores(course):
    asignar_profesor(course,"Jefe de Cátedra")
    asignar_profesor(course,"JTP")
    for x in range(floor(random()*3)):
        asignar_profesor(course,"Ayudante de cátedra")

def nuevo_curso_de_materia(department_code,subject_code,semester):
    r=str(floor(random()*10))
    name=department_code+"."+subject_code+" "+semester+" - "+r
    total_slots=100+floor(random()*50)
    cursor.execute("""
    insert into courses (
        department_code,
        subject_code,
        semester,
        name,
        total_slots
    ) values (%s,%s,%s,%s,%s)
    returning *;
    """,(department_code,subject_code,semester,name,total_slots,))
    inserted=cursor.fetchone()
    conn.commit()
    return inserted[5]

cursor.execute("select * from classrooms;")
aulas=cursor.fetchall()
def asignar_aula_a_curso(course_id,description):
    def horario():
        h=str(floor(random()*24))
        if len(h)==1:
            h = "0" + h
        m=str(floor(random()*60))
        if len(h)==1:
            m = "0" + m
        return h+":"+m+":00"
    classroom=choice(aulas)
    classroom_code=classroom[0]
    classroom_campus=classroom[1]
    beginning=horario()
    ending=horario()
    day_of_week=choice(["dom","lun","mar","mie","jue","vie","sab"])

    cursor.execute("""
    insert into classroom_uses(
        course,
        classroom_code,
        classroom_campus,
        beginning,
        ending,
        day_of_week,
        description
    ) values
    (%s,%s,%s,%s,%s,%s,%s)
    """,(course_id,classroom_code,classroom_campus,beginning,ending,day_of_week,description))
    conn.commit()

def asignar_todas_aulas_a_curso(course_id):
    asignar_aula_a_curso(course_id,"Teórica Obligatoria")
    asignar_aula_a_curso(course_id,"Práctica Obligatoria")

def inscribir_estudiante_a_curso(course_id,student_id):
    cursor.execute("""
    insert into course_enrollments(course,student,creation,accepted,grade,grade_date)
    values (%s,%s,NOW(),'t',-1,NOW()) on conflict do nothing;
    """,(course_id,student_id,))
    conn.commit()
def agregar_encuesta(course,student):
    feedback=lorem.sentence()
    if random()>0.5:
        feedback = ""
    if random()<0.1:
        feedback = lorem.paragraph()
    if random()<0.01:
        feedback = lorem.text()
    def genq():
        centro = (course % 10) + 1
        val = min(max(floor(triangular(centro-3,centro+3,centro)),1),10)
        if val <1:
            val=1
        return val

    cursor.execute("""
        insert into polls(course,student,q1,q2,q3,q4,q5,q6,q7,passed,feedback)
        values (%s,%s,%s,%s,%s,%s,%s,%s,%s,'t',%s) on conflict do nothing;
    """,(
        course,
        student,
        genq(),genq(),genq(),genq(),genq(),genq(),genq(),
        feedback
        )
    )
    conn.commit()

def inscribir_estudiantes(course_id):
    for x in range(floor(20+random()*50)):
        padron=nuevo_estudiante()
        inscribir_estudiante_a_curso(course_id,padron)
        agregar_encuesta(course_id,padron)

def nuevo_curso_de_materia_completo(department_code,subject_code,semester):
    course_id=nuevo_curso_de_materia(department_code,subject_code,semester)
    asignar_profesores(course_id)
    asignar_todas_aulas_a_curso(course_id)
    inscribir_estudiantes(course_id)

def crear_cursos_de_materia(department_code,subject_code,semester):
    for x in range(floor(random()*4)+1):
        nuevo_curso_de_materia_completo(department_code,subject_code,semester)

def crear_cursos_de_depto(department_code,semester):
    cursor.execute("select code from subjects where department_code=%s",(department_code,))

    cursos=list([x[0] for x in cursor.fetchall()])
    materias=sample(cursos,min(floor(random()*10+5),len(cursos)))
    for m in materias:
        crear_cursos_de_materia(department_code,m,semester)

#inscribir_estudiantes(2)
for s in ["1c2018","2c2018"]:
    print("agregando a 75 ",s)
    crear_cursos_de_depto("75",s)
    crear_cursos_de_depto("66",s)
    crear_cursos_de_depto("68",s)
    

