import csv
import json
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox


# ─────────────────────────── helpers ────────────────────────────

def _open_dialog(title: str, filetypes: list) -> str | None:
    ruta = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return ruta if ruta else None


def _insertar_docs(collection_alumno, collection_grupo, docs: list) -> tuple[int, int, int]:
    """
    Inserta alumnos evitando duplicados y validando que el grupo exista.
    Retorna (insertados, omitidos_duplicado, omitidos_sin_grupo).
    """
    insertados = omitidos_dup = omitidos_gru = 0
    for doc in docs:
        cve_alu = int(doc["cveAlu"])
        eda_alu = int(doc["edaAlu"])
        cve_gru = doc["cveGru"]

        if collection_alumno.find_one({"cveAlu": cve_alu}):
            omitidos_dup += 1
            continue

        if not collection_grupo.find_one({"cveGru": cve_gru}):
            omitidos_gru += 1
            continue

        collection_alumno.insert_one({
            "cveAlu": cve_alu,
            "nomAlu": doc["nomAlu"],
            "edaAlu": eda_alu,
            "cveGru": cve_gru
        })
        insertados += 1

    return insertados, omitidos_dup, omitidos_gru


def _mostrar_resultado(formato: str, insertados: int, omitidos_dup: int, omitidos_gru: int) -> None:
    messagebox.showinfo(
        f"Importar {formato}",
        f"Importación completada.\n\n"
        f"Insertados:               {insertados}\n"
        f"Omitidos (duplicados):    {omitidos_dup}\n"
        f"Omitidos (grupo inexist): {omitidos_gru}"
    )


# ─────────────────────────── CSV ────────────────────────────────

def importar_csv(collection_alumno, collection_grupo) -> None:
    ruta = _open_dialog("Abrir CSV", [("CSV files", "*.csv")])
    if not ruta:
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            docs = [
                {
                    "cveAlu": row["cveAlu"],
                    "nomAlu": row["nomAlu"],
                    "edaAlu": row["edaAlu"],
                    "cveGru": row["cveGru"]
                }
                for row in reader
            ]
    except Exception as e:
        messagebox.showerror("Importar CSV", f"Error al leer el archivo:\n{e}")
        return

    ins, odup, ogru = _insertar_docs(collection_alumno, collection_grupo, docs)
    _mostrar_resultado("CSV", ins, odup, ogru)


# ─────────────────────────── JSON ───────────────────────────────

def importar_json(collection_alumno, collection_grupo) -> None:
    ruta = _open_dialog("Abrir JSON", [("JSON files", "*.json")])
    if not ruta:
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            docs = json.load(f)
        if not isinstance(docs, list):
            raise ValueError("El archivo JSON debe contener una lista de objetos.")
    except Exception as e:
        messagebox.showerror("Importar JSON", f"Error al leer el archivo:\n{e}")
        return

    ins, odup, ogru = _insertar_docs(collection_alumno, collection_grupo, docs)
    _mostrar_resultado("JSON", ins, odup, ogru)


# ─────────────────────────── XML ────────────────────────────────

def importar_xml(collection_alumno, collection_grupo) -> None:
    ruta = _open_dialog("Abrir XML", [("XML files", "*.xml")])
    if not ruta:
        return

    try:
        tree = ET.parse(ruta)
        raiz = tree.getroot()
        docs = [
            {
                "cveAlu": alumno.find("cveAlu").text,
                "nomAlu": alumno.find("nomAlu").text,
                "edaAlu": alumno.find("edaAlu").text,
                "cveGru": alumno.find("cveGru").text,
            }
            for alumno in raiz.findall("Alumno")
        ]
    except Exception as e:
        messagebox.showerror("Importar XML", f"Error al leer el archivo:\n{e}")
        return

    ins, odup, ogru = _insertar_docs(collection_alumno, collection_grupo, docs)
    _mostrar_resultado("XML", ins, odup, ogru)