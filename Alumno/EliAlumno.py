def eliminar_alumno(collection_alumno, cve_alu: int) -> bool:
    """
    Elimina un alumno por su cveAlu.
    Retorna True si se eliminó, False si no existía.
    """
    resultado = collection_alumno.delete_one({"cveAlu": cve_alu})
    return resultado.deleted_count > 0