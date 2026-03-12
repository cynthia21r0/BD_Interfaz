def agregar_grupo(collection, cve_gru: str, nom_gru: str) -> bool:

    if collection.find_one({"cveGru": cve_gru}):
        return False

    collection.insert_one({"cveGru": cve_gru, "nomGru": nom_gru})
    return True