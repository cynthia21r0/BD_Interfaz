import subprocess
import os
from tkinter import messagebox, filedialog


MONGORESTORE_PATH = r"C:\Program Files\MongoDB\Tools\100\bin\mongorestore.exe"
DB_NAME = "BD_GrupoAlumno"


def eliminar_todos(collection_alumno) -> int:
    """Elimina todos los alumnos. Retorna el número de documentos eliminados."""
    resultado = collection_alumno.delete_many({})
    return resultado.deleted_count


def restaurar_todos(collection_alumno=None) -> bool:
    """
    Pide al usuario la carpeta del backup y restaura la colección Alumno
    usando mongorestore.
    """
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta del Backup")
    if not carpeta:
        return False

    carpeta = os.path.normpath(carpeta)

    # Acepta tanto la carpeta raíz del backup como BD_GrupoAlumno directamente
    if os.path.basename(carpeta) == DB_NAME:
        ruta_db = carpeta
    else:
        ruta_db = os.path.join(carpeta, DB_NAME)

    bson_file = os.path.join(ruta_db, "Alumno.bson")

    if not os.path.exists(bson_file):
        messagebox.showerror(
            "Restaurar - Error",
            f"No se encontró el archivo:\n{bson_file}"
        )
        return False

    cmd = [
        MONGORESTORE_PATH,
        f"--nsInclude={DB_NAME}.Alumno",
        bson_file
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True)
        if resultado.returncode == 0:
            messagebox.showinfo(
                "Restaurar",
                f"Alumnos restaurados correctamente desde:\n{bson_file}"
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
            f"No se encontró mongorestore en:\n{MONGORESTORE_PATH}"
        )
        return False