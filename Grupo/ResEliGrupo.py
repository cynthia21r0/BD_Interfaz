"""
ResEliGrupo.py – Eliminar todos o Restaurar todos los grupos usando mongorestore.
"""

import subprocess
import os
from tkinter import messagebox, filedialog


MONGORESTORE_PATH = r"C:\Program Files\MongoDB\Tools\100\bin\mongorestore.exe"
DB_NAME = "BD_GrupoAlumno"


def eliminar_todos(collection) -> int:
    """Elimina todos los documentos de la colección."""
    resultado = collection.delete_many({})
    return resultado.deleted_count


def restaurar_todos(collection=None) -> bool:
    """
    Pide al usuario la carpeta del backup y ejecuta mongorestore.
    La carpeta debe contener la subcarpeta BD_GrupoAlumno generada por mongodump.
    """
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta raíz del Backup")
    if not carpeta:
        return False

    carpeta = os.path.normpath(carpeta)
    ruta_db = os.path.join(carpeta, DB_NAME)

    if not os.path.exists(ruta_db):
        messagebox.showerror(
            "Restaurar - Error",
            f"No se encontró la carpeta del backup:\n{ruta_db}\n\n"
            "Asegúrate de seleccionar la carpeta raíz donde mongodump guardó el backup."
        )
        return False

    cmd = [
        MONGORESTORE_PATH,
        f"--db={DB_NAME}",
        "--collection=Grupo",
        f"--dir={ruta_db}"
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True)

        if resultado.returncode == 0:
            messagebox.showinfo(
                "Restaurar",
                f"Base de datos restaurada correctamente desde:\n{ruta_db}"
            )
            return True
        else:
            messagebox.showerror(
                "Restaurar - Error",
                f"mongorestore falló:\n\n{resultado.stderr}"
            )
            return False

    except FileNotFoundError:
        messagebox.showerror(
            "Restaurar - Error",
            f"No se encontró mongorestore en:\n{MONGORESTORE_PATH}\n\n"
            "Verifica la ruta en ResEliGrupo.py"
        )
        return False