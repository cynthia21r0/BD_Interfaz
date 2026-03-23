def agregar_alumno(collection_alumno, collection_grupo,
                   cve_alu: int, nom_alu: str, eda_alu: int, cve_gru: str) -> str:
    """
    Inserta un alumno nuevo.
    Retorna:
        "ok"          – insertado correctamente
        "duplicado"   – cveAlu ya existe
        "grupo"       – cveGru no existe en la colección Grupo
    """
    if collection_alumno.find_one({"cveAlu": cve_alu}):
        return "duplicado"

    if not collection_grupo.find_one({"cveGru": cve_gru}):
        return "grupo"

    collection_alumno.insert_one({
        "cveAlu": cve_alu,
        "nomAlu": nom_alu,
        "edaAlu": eda_alu,
        "cveGru": cve_gru
    })
    return "ok"