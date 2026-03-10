"""
EjeBackup.py – Genera un backup de la colección Grupo en formato JSON.
El archivo se guarda como  backup_Grupo.json  en el directorio de trabajo.
"""

import json
import os
from datetime import datetime
from tkinter import messagebox


BACKUP_FILE = "backup_Grupo.json"


def ejecutar_backup(collection) -> None:
    """
    Exporta todos los documentos de la colección a un archivo JSON de backup.
    Muestra ventana emergente con el resultado.
    """
    docs = list(collection.find({}, {"_id": 0}))

    data = {
        "fecha_backup": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(docs),
        "grupos": docs
    }

    ruta = os.path.abspath(BACKUP_FILE)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    messagebox.showinfo(
        "Backup",
        f"Backup ejecutado correctamente.\n{len(docs)} registro(s) guardados en:\n{ruta}"
    )