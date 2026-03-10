"""
ModGrupo.py – Lógica para MODIFICAR el nombre de un grupo existente.
"""


def modificar_grupo(collection, cve_gru: str, nuevo_nom: str) -> bool:
    """
    Actualiza el campo nomGru del documento cuya cveGru coincida.

    Returns:
        True  → actualización exitosa.
        False → no se encontró el documento.
    """
    resultado = collection.update_one(
        {"cveGru": cve_gru},
        {"$set": {"nomGru": nuevo_nom}}
    )
    return resultado.matched_count > 0