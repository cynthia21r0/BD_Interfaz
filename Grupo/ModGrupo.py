def modificar_grupo(collection, cve_gru: str, nuevo_nom: str) -> bool:
    resultado = collection.update_one(
        {"cveGru": cve_gru},
        {"$set": {"nomGru": nuevo_nom}}
    )
    return resultado.matched_count > 0