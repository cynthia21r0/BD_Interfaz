import tkinter as tk
from tkinter import messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Grupo.AgrGrupo import agregar_grupo
from Grupo.ModGrupo import modificar_grupo
from Grupo.EliGrupo import eliminar_grupo
from Grupo.EjeBackup import ejecutar_backup
from Grupo.ResEliGrupo import restaurar_todos, eliminar_todos
from Grupo.Exportar import exportar_csv, exportar_json, exportar_xml
from Grupo.Importar import importar_csv, importar_json, importar_xml
from db.conexion import get_collection


class AdmonGrupo:
    def __init__(self, root):
        self.root = root
        self.root.title("Admon Grupo")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4e8")

        self.collection = get_collection("BD_GrupoAlumno", "Grupo")

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}

        # --- Clave ---
        tk.Label(self.root, text="Clave:", bg="#f0f4e8").grid(row=0, column=0, sticky="e", **pad)
        self.entry_clave = tk.Entry(self.root, width=28)
        self.entry_clave.grid(row=0, column=1, columnspan=2, sticky="w", **pad)

        tk.Button(self.root, text="Buscar", width=12, command=self.buscar).grid(row=0, column=3, **pad)

        # --- Nombre ---
        tk.Label(self.root, text="Nombre:", bg="#f0f4e8").grid(row=1, column=0, sticky="e", **pad)
        self.entry_nombre = tk.Entry(self.root, width=28)
        self.entry_nombre.grid(row=1, column=1, columnspan=2, sticky="w", **pad)

        tk.Button(self.root, text="Limpiar", width=12, command=self.limpiar).grid(row=1, column=3, **pad)

        # --- Agregar / Modificar / Eliminar ---
        tk.Button(self.root, text="Agregar", width=12, command=self.agregar).grid(row=2, column=0, **pad)
        tk.Button(self.root, text="Modificar", width=12, command=self.modificar).grid(row=2, column=1, **pad)
        tk.Button(self.root, text="Eliminar", width=12, command=self.eliminar).grid(row=2, column=3, **pad)

        # --- Exportar ---
        tk.Button(self.root, text="Exportar csv", width=12, command=lambda: exportar_csv(self.collection)).grid(row=3, column=0, **pad)
        tk.Button(self.root, text="Exportar json", width=12, command=lambda: exportar_json(self.collection)).grid(row=3, column=1, **pad)
        tk.Button(self.root, text="Exportar xml", width=12, command=lambda: exportar_xml(self.collection)).grid(row=3, column=3, **pad)

        # --- Importar ---
        tk.Button(self.root, text="Importar csv", width=12, command=lambda: importar_csv(self.collection)).grid(row=4, column=0, **pad)
        tk.Button(self.root, text="Importar json", width=12, command=lambda: importar_json(self.collection)).grid(row=4, column=1, **pad)
        tk.Button(self.root, text="Importar xml", width=12, command=lambda: importar_xml(self.collection)).grid(row=4, column=3, **pad)

        # --- Backup / Eliminar todos / Restaurar todos ---
        tk.Button(self.root, text="Ejecutar Backup", width=48, command=lambda: ejecutar_backup(self.collection)).grid(row=5, column=0, columnspan=4, **pad)
        tk.Button(self.root, text="Eliminar todos los Grupos", width=48, command=self.eliminar_todos).grid(row=6, column=0, columnspan=4, **pad)
        tk.Button(self.root, text="Restaurar todos los Grupos", width=48, command=self.restaurar_todos).grid(row=7, column=0, columnspan=4, **pad)

    # ------------------------------------------------------------------ helpers
    def _get_clave(self):
        return self.entry_clave.get().strip()

    def _get_nombre(self):
        return self.entry_nombre.get().strip()

    def limpiar(self):
        self.entry_clave.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)

    # ------------------------------------------------------------------ CRUD
    def buscar(self):
        clave = self._get_clave()
        if not clave:
            messagebox.showwarning("Buscar", "Ingrese una Clave para buscar.")
            return
        doc = self.collection.find_one({"cveGru": clave})
        if doc:
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, doc["nomGru"])
            messagebox.showinfo("Buscar", f"Grupo encontrado:\nClave: {doc['cveGru']}\nNombre: {doc['nomGru']}")
        else:
            messagebox.showwarning("Buscar", f"No se encontró ningún grupo con clave '{clave}'.")

    def agregar(self):
        clave = self._get_clave()
        nombre = self._get_nombre()
        if not clave or not nombre:
            messagebox.showwarning("Agregar", "Ingrese Clave y Nombre.")
            return
        resultado = agregar_grupo(self.collection, clave, nombre)
        if resultado:
            messagebox.showinfo("Agregar", f"Grupo '{clave}' agregado correctamente.")
            self.limpiar()
        else:
            messagebox.showerror("Agregar", f"Ya existe un grupo con clave '{clave}'.")

    def modificar(self):
        clave = self._get_clave()
        nombre = self._get_nombre()
        if not clave or not nombre:
            messagebox.showwarning("Modificar", "Ingrese Clave y nuevo Nombre.")
            return
        resultado = modificar_grupo(self.collection, clave, nombre)
        if resultado:
            messagebox.showinfo("Modificar", f"Grupo '{clave}' modificado correctamente.")
            self.limpiar()
        else:
            messagebox.showerror("Modificar", f"No se encontró ningún grupo con clave '{clave}'.")

    def eliminar(self):
        clave = self._get_clave()
        if not clave:
            messagebox.showwarning("Eliminar", "Ingrese una Clave para eliminar.")
            return
        confirmar = messagebox.askyesno("Eliminar", f"¿Desea eliminar el grupo '{clave}'?")
        if confirmar:
            resultado = eliminar_grupo(self.collection, clave)
            if resultado:
                messagebox.showinfo("Eliminar", f"Grupo '{clave}' eliminado correctamente.")
                self.limpiar()
            else:
                messagebox.showerror("Eliminar", f"No se encontró ningún grupo con clave '{clave}'.")

    def eliminar_todos(self):
        confirmar = messagebox.askyesno("Eliminar todos", "¿Está seguro de eliminar TODOS los grupos?\nEsta acción no se puede deshacer.")
        if confirmar:
            eliminar_todos(self.collection)
            messagebox.showinfo("Eliminar todos", "Todos los grupos han sido eliminados.")

    def restaurar_todos(self):
        confirmar = messagebox.askyesno("Restaurar todos", "¿Desea restaurar todos los grupos desde el backup?")
        if confirmar:
            ok = restaurar_todos(self.collection)
            if ok:
                messagebox.showinfo("Restaurar todos", "Grupos restaurados correctamente.")
            else:
                messagebox.showerror("Restaurar todos", "No se encontró archivo de backup para restaurar.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdmonGrupo(root)
    root.mainloop()