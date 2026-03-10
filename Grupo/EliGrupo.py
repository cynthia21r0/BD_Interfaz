def eliminar_grupo(collection, cve_gru: str) -> bool:
    resultado = collection.delete_one({"cveGru": cve_gru})
    return resultado.deleted_count > 0