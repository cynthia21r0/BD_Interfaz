"""
ResEliGrupo.py – Lógica para ELIMINAR TODOS o RESTAURAR TODOS los grupos.
La restauración se apoya en el archivo backup_Grupo.json generado por EjeBackup.
"""

import json
import os


BACKUP_FILE = "backup_Grupo.json"


def eliminar_todos(collection) -> int:
    """
    Elimina todos los documentos de la colección.

    Returns:
        Número de documentos eliminados.
    """
    resultado = collection.delete_many({})
    return resultado.deleted_count


def restaurar_todos(collection) -> bool:
    """
    Restaura los grupos desde el archivo de backup JSON.
    Si el backup no existe, retorna False.

    Returns:
        True  → restauración exitosa.
        False → no se encontró el archivo de backup.
    """
    ruta = os.path.abspath(BACKUP_FILE)
    if not os.path.exists(ruta):
        return False

    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    grupos = data.get("grupos", [])
    if not grupos:
        return False

    # Evitar duplicados: insertar solo los que no existan
    insertados = 0
    for grupo in grupos:
        if not collection.find_one({"cveGru": grupo["cveGru"]}):
            collection.insert_one(grupo)
            insertados += 1

    return True