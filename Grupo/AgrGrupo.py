"""
AgrGrupo.py – Lógica para AGREGAR un grupo en la colección MongoDB.
"""


def agregar_grupo(collection, cve_gru: str, nom_gru: str) -> bool:
    """
    Inserta un nuevo documento {cveGru, nomGru} en la colección.

    Returns:
        True  → inserción exitosa.
        False → ya existe un documento con esa clave.
    """
    if collection.find_one({"cveGru": cve_gru}):
        return False

    collection.insert_one({"cveGru": cve_gru, "nomGru": nom_gru})
    return True