from pymongo import MongoClient as MC

conexion = MC("mongodb://localhost:27017/")
BD_GrupoAlumno = conexion["BD_GrupoAlumno"]
Grupo = BD_GrupoAlumno["Grupo"]

#Usando inputs y listando
cveGru = input("Introduce la clave del Grupo: ")
nomGru = input("Introduce el nombre del Grupo: ")

Grupo.insert_one({"cveGru": cveGru, "nomGru": nomGru})
print("Grupo Insertado")

print("Lista de Grupos")
for doc in Grupo.find():
    print(doc)