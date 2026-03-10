from pymongo import MongoClient as MC

conexion = MC("mongodb://localhost:27017/")
BD_GrupoAlumno = conexion["BD_GrupoAlumno"]
Grupo = BD_GrupoAlumno["Grupo"]

#Usando inputs y listando para eliminar Grupos
cveGru = input("Introduce la clave del Grupo a eliminar: ")
resultado = list(Grupo.find({"cveGru": cveGru}))

if (len(resultado)==0):
    print("El Grupo no Existe")
else:
    Grupo.delete_one({"cveGru": cveGru})
    print("Grupo Eliminado")
