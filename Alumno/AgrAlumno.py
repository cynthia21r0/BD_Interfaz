from pymongo import MongoClient as MC

conexion = MC("mongodb://localhost:27017/")
BD_GrupoAlumno = conexion["BD_GrupoAlumno"]
Alumno = BD_GrupoAlumno["Alumno"]

#Usando inputs y listando
cveAlu = input("Introduce la clave del Alumno: ")
nomAlu = input("Introduce el nombre del Alumno: ")
edaAlu = input("Introduce la edad del Alumno: ")
cveGru = input("Introduce la clave del Grupo: ")

Alumno.insert_one({"cveAlu": cveAlu, "nomAlu": nomAlu, "edaAlu": edaAlu, "cveGru": cveGru})
print("Alumno Insertado")

print("Lista de Alumnos")
for doc in Alumno.find():
    print(doc)