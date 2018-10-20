import names
from random import randint,shuffle,sample

#Padrón
#Contraseña inicial (en el caso de que este usuario ya exista en el sistema, este campo puede dejarse en blanco)
#Nombre
#Apellido
#Prioridad
#Email
#Lista de carreras a las que está anotado, como enteros separados por guiones.

def generate_one(username):
    name = names.get_first_name()
    surname = names.get_last_name()
    all_degrees=list(range(1,12))
    shuffle(all_degrees)
    degrees="-".join([str(x) for x in all_degrees[:randint(1,3)]])
    return ",".join([str(x) for x in [
        username,
        username,
        name,
        surname,
        randint(1,200),
        "{}.{}@gmail.com".format(name,surname),
        degrees
    ]])
usernames=sample(list(range(10000,500000)),10000)
for u in usernames:
    print(generate_one(u))