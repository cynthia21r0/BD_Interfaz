import csv
import json
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox


# ─────────────────────────── helpers ────────────────────────────

def _open_dialog(title: str, filetypes: list) -> str | None:
    ruta = filedialog.askopenfilename(title=title, filetypes=filetypes)
    return ruta if ruta else None


def _insertar_docs(collection, docs: list) -> tuple[int, int]:
    insertados = omitidos = 0
    for doc in docs:
        if not collection.find_one({"cveGru": doc["cveGru"]}):
            collection.insert_one({"cveGru": doc["cveGru"], "nomGru": doc["nomGru"]})
            insertados += 1
        else:
            omitidos += 1
    return insertados, omitidos


# ─────────────────────────── CSV ────────────────────────────────

def importar_csv(collection) -> None:
    ruta = _open_dialog("Abrir CSV", [("CSV files", "*.csv")])
    if not ruta:
        return

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            docs = [{"cveGru": row["cveGru"], "nomGru": row["nomGru"]} for row in reader]
    except Exception as e:
        messagebox.showerror("Importar CSV", f"Error al leer el archivo:\n{e}")
        return

    insertados, omitidos = _insertar_docs(collection, docs)
    messagebox.showinfo(
        "Importar CSV",
        f"Importación completada.\nInsertados: {insertados}  |  Omitidos (duplicados): {omitidos}"
    )


# ─────────────────────────── JSON ───────────────────────────────

def importar_json(collection) -> None:
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

    insertados, omitidos = _insertar_docs(collection, docs)
    messagebox.showinfo(
        "Importar JSON",
        f"Importación completada.\nInsertados: {insertados}  |  Omitidos (duplicados): {omitidos}"
    )


# ─────────────────────────── XML ────────────────────────────────

def importar_xml(collection) -> None:
    ruta = _open_dialog("Abrir XML", [("XML files", "*.xml")])
    if not ruta:
        return

    try:
        tree = ET.parse(ruta)
        raiz = tree.getroot()
        docs = [
            {
                "cveGru": grupo.find("cveGru").text,
                "nomGru": grupo.find("nomGru").text,
            }
            for grupo in raiz.findall("Grupo")
        ]
    except Exception as e:
        messagebox.showerror("Importar XML", f"Error al leer el archivo:\n{e}")
        return

    insertados, omitidos = _insertar_docs(collection, docs)
    messagebox.showinfo(
        "Importar XML",
        f"Importación completada.\nInsertados: {insertados}  |  Omitidos (duplicados): {omitidos}"
    )