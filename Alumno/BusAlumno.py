from pymongo import MongoClient as MC

conexion = MC("mongodb://localhost:27017/")
BD_GrupoAlumno = conexion["BD_GrupoAlumno"]
Alumno = BD_GrupoAlumno["Alumno"]

#Usando inputs y listando
cveAlu = input("Introduce la clave del Alumno: ")
resultado = list(Alumno.find({"cveAlu": cveAlu}))

if (len(resultado)==0):
    print("El Alumno no Existe")
else:
    for alumno in resultado:
        print(alumno)