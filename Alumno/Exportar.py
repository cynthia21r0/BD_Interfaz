import csv
import json
import os
import xml.etree.ElementTree as ET
from tkinter import filedialog, messagebox


# ─────────────────────────── helpers ────────────────────────────

def _obtener_docs(collection) -> list:
    """Obtiene todos los alumnos sin el campo _id."""
    return list(collection.find({}, {"_id": 0}))


def _save_dialog(title: str, filetypes: list, defaultext: str) -> str | None:
    ruta = filedialog.asksaveasfilename(
        title=title,
        filetypes=filetypes,
        defaultextension=defaultext,
        initialfile=f"Alumno{defaultext}"
    )
    return ruta if ruta else None


# ─────────────────────────── CSV ────────────────────────────────

def exportar_csv(collection) -> None:
    docs = _obtener_docs(collection)
    if not docs:
        messagebox.showwarning("Exportar CSV", "No hay datos para exportar.")
        return

    ruta = _save_dialog("Guardar CSV", [("CSV files", "*.csv")], ".csv")
    if not ruta:
        return

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["cveAlu", "nomAlu", "edaAlu", "cveGru"])
        writer.writeheader()
        writer.writerows(docs)

    messagebox.showinfo("Exportar CSV", f"Exportado correctamente:\n{ruta}")


# ─────────────────────────── JSON ───────────────────────────────

def exportar_json(collection) -> None:
    docs = _obtener_docs(collection)
    if not docs:
        messagebox.showwarning("Exportar JSON", "No hay datos para exportar.")
        return

    ruta = _save_dialog("Guardar JSON", [("JSON files", "*.json")], ".json")
    if not ruta:
        return

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=4)

    messagebox.showinfo("Exportar JSON", f"Exportado correctamente:\n{ruta}")


# ─────────────────────────── XML ────────────────────────────────

def exportar_xml(collection) -> None:
    docs = _obtener_docs(collection)
    if not docs:
        messagebox.showwarning("Exportar XML", "No hay datos para exportar.")
        return

    ruta = _save_dialog("Guardar XML", [("XML files", "*.xml")], ".xml")
    if not ruta:
        return

    raiz = ET.Element("Alumnos")
    for doc in docs:
        alumno = ET.SubElement(raiz, "Alumno")
        ET.SubElement(alumno, "cveAlu").text = str(doc["cveAlu"])
        ET.SubElement(alumno, "nomAlu").text = doc["nomAlu"]
        ET.SubElement(alumno, "edaAlu").text = str(doc["edaAlu"])
        ET.SubElement(alumno, "cveGru").text = doc["cveGru"]

    tree = ET.ElementTree(raiz)
    ET.indent(tree, space="    ")
    tree.write(ruta, encoding="utf-8", xml_declaration=True)

    messagebox.showinfo("Exportar XML", f"Exportado correctamente:\n{ruta}")