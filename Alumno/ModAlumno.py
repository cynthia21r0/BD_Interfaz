def modificar_alumno(collection_alumno, collection_grupo,
                     cve_alu: int, nuevo_nom: str, nueva_eda: int, nueva_cve_gru: str) -> str:
    """
    Modifica nombre, edad y/o grupo de un alumno.
    Retorna:
        "ok"        – actualizado correctamente
        "noexiste"  – cveAlu no encontrado
        "grupo"     – nueva cveGru no existe en la colección Grupo
    """
    if not collection_alumno.find_one({"cveAlu": cve_alu}):
        return "noexiste"

    if not collection_grupo.find_one({"cveGru": nueva_cve_gru}):
        return "grupo"

    collection_alumno.update_one(
        {"cveAlu": cve_alu},
        {"$set": {
            "nomAlu": nuevo_nom,
            "edaAlu": nueva_eda,
            "cveGru": nueva_cve_gru
        }}
    )
    return "ok"