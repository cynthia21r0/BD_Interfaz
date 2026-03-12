import subprocess
import os
from tkinter import messagebox, filedialog


MONGODUMP_PATH = r"C:\Program Files\MongoDB\Tools\100\bin\mongodump.exe"
DB_NAME = "BD_GrupoAlumno"


def ejecutar_backup(collection=None) -> None:
    """
    Pide al usuario la carpeta destino y ejecuta mongodump.
    """
    carpeta = filedialog.askdirectory(title="Selecciona carpeta destino del Backup")
    if not carpeta:
        return

    carpeta = os.path.normpath(carpeta)

    cmd = [
        MONGODUMP_PATH,
        f"--db={DB_NAME}",
        f"--out={carpeta}"
    ]

    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True)

        if resultado.returncode == 0:
            ruta_final = os.path.join(carpeta, DB_NAME)
            messagebox.showinfo(
                "Backup",
                f"Backup ejecutado correctamente.\n\nGuardado en:\n{ruta_final}"
            )
        else:
            messagebox.showerror(
                "Backup - Error",
                f"mongodump falló:\n\n{resultado.stderr}"
            )

    except FileNotFoundError:
        messagebox.showerror(
            "Backup - Error",
            f"No se encontró mongodump en:\n{MONGODUMP_PATH}\n\n"
            "Verifica la ruta en EjeBackup.py"
        )