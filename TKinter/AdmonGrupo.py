import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Grupo.AgrGrupo import agregar_grupo
from Grupo.ModGrupo import modificar_grupo
from Grupo.EliGrupo import eliminar_grupo
from Grupo.EjeBackup import ejecutar_backup
from Grupo.ResEliGrupo import restaurar_todos, eliminar_todos
from Grupo.Exportar import exportar_csv, exportar_json, exportar_xml
from Grupo.Importar import importar_csv, importar_json, importar_xml
from db.conexion import get_collection


# ── Paleta de colores ────────────────────────────────────────────
BG          = "#F7F6F3"
SURFACE     = "#FFFFFF"
BORDER      = "#E2DFD8"
TEXT_PRI    = "#2C2C2A"
TEXT_SEC    = "#5F5E5A"
ACCENT      = "#1D9E75"        # teal-400
ACCENT_HOV  = "#0F6E56"        # teal-600
ACCENT_LITE = "#E1F5EE"        # teal-50
DANGER      = "#E24B4A"
DANGER_HOV  = "#A32D2D"
NEUTRAL     = "#888780"        # gray-400
BTN_BORDER  = "#B4B2A9"        # gray-200

FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_LABEL  = ("Segoe UI", 9)
FONT_ENTRY  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 9)
FONT_TITLE  = ("Segoe UI", 13, "bold")

# Regex: sólo letras (incluye acentos/ñ), dígitos, espacios y guiones
VALID_CLAVE  = re.compile(r'^[A-Za-z0-9\-_]{1,20}$')
VALID_NOMBRE = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑ0-9 \-_.,()]{1,80}$')


class AdmonGrupo:
    def __init__(self, root):
        self.root = root
        self.root.title("Administración de Grupos")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.collection = get_collection("BD_GrupoAlumno", "Grupo")
        self._build_ui()

    # ─────────────────────────── UI ─────────────────────────────
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG, padx=20, pady=18)
        outer.pack(fill="both", expand=True)

        # ── Título ──────────────────────────────────────────────
        title_frame = tk.Frame(outer, bg=ACCENT_LITE, padx=12, pady=8,
                               relief="flat", bd=0)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        tk.Label(title_frame, text="Grupos", font=FONT_TITLE,
                 bg=ACCENT_LITE, fg=ACCENT_HOV).pack(side="left")
        self.lbl_count = tk.Label(title_frame, text="", font=FONT_LABEL,
                                  bg=ACCENT_LITE, fg=TEXT_SEC)
        self.lbl_count.pack(side="right")
        self._actualizar_contador()

        # ── Card principal ───────────────────────────────────────
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14,
                        relief="solid", bd=1, highlightthickness=0)
        card.configure(highlightbackground=BORDER)
        card.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Clave
        tk.Label(card, text="Clave", font=FONT_LABEL, bg=SURFACE,
                 fg=TEXT_SEC).grid(row=0, column=0, sticky="w", pady=(0, 2))
        entry_row = tk.Frame(card, bg=SURFACE)
        entry_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.entry_clave = tk.Entry(entry_row, font=FONT_ENTRY, width=22,
                                    bg=SURFACE, fg=TEXT_PRI,
                                    relief="solid", bd=1,
                                    highlightthickness=1,
                                    highlightbackground=BORDER,
                                    highlightcolor=ACCENT,
                                    insertbackground=TEXT_PRI)
        self.entry_clave.pack(side="left")
        self._btn(entry_row, "Buscar", self.buscar,
                  color=ACCENT, hover=ACCENT_HOV).pack(side="left", padx=(8, 0))

        # Nombre
        tk.Label(card, text="Nombre", font=FONT_LABEL, bg=SURFACE,
                 fg=TEXT_SEC).grid(row=2, column=0, sticky="w", pady=(0, 2))
        nombre_row = tk.Frame(card, bg=SURFACE)
        nombre_row.grid(row=3, column=0, sticky="ew", pady=(0, 2))
        self.entry_nombre = tk.Entry(nombre_row, font=FONT_ENTRY, width=22,
                                     bg=SURFACE, fg=TEXT_PRI,
                                     relief="solid", bd=1,
                                     highlightthickness=1,
                                     highlightbackground=BORDER,
                                     highlightcolor=ACCENT,
                                     insertbackground=TEXT_PRI)
        self.entry_nombre.pack(side="left")
        self._btn(nombre_row, "Limpiar", self.limpiar,
                  color=NEUTRAL, hover="#444441").pack(side="left", padx=(8, 0))

        # ── CRUD ─────────────────────────────────────────────────
        crud = tk.Frame(outer, bg=BG)
        crud.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        crud.columnconfigure((0, 1, 2), weight=1)
        self._btn(crud, "Agregar",   self.agregar,   color=ACCENT,  hover=ACCENT_HOV, fill=True).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self._btn(crud, "Modificar", self.modificar, color=NEUTRAL, hover="#444441",  fill=True).grid(row=0, column=1, padx=5,      sticky="ew")
        self._btn(crud, "Eliminar",  self.eliminar,  color=DANGER,  hover=DANGER_HOV, fill=True).grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # ── Separador ────────────────────────────────────────────
        self._sep(outer, row=3)

        # ── Exportar / Importar ──────────────────────────────────
        tk.Label(outer, text="EXPORTAR", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_SEC).grid(row=4, column=0, sticky="w", pady=(10, 4))
        exp_frame = tk.Frame(outer, bg=BG)
        exp_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
        exp_frame.columnconfigure((0, 1, 2), weight=1)
        for i, (lbl, fn) in enumerate([
            ("CSV",  lambda: exportar_csv(self.collection)),
            ("JSON", lambda: exportar_json(self.collection)),
            ("XML",  lambda: exportar_xml(self.collection)),
        ]):
            self._btn(exp_frame, lbl, fn, color=NEUTRAL, hover="#444441",
                      fill=True).grid(row=0, column=i, padx=(0 if i == 0 else 5, 5 if i < 2 else 0), sticky="ew")

        tk.Label(outer, text="IMPORTAR", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_SEC).grid(row=6, column=0, sticky="w", pady=(12, 4))
        imp_frame = tk.Frame(outer, bg=BG)
        imp_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        imp_frame.columnconfigure((0, 1, 2), weight=1)
        for i, (lbl, fn) in enumerate([
            ("CSV",  lambda: importar_csv(self.collection)),
            ("JSON", lambda: importar_json(self.collection)),
            ("XML",  lambda: importar_xml(self.collection)),
        ]):
            self._btn(imp_frame, lbl, fn, color=NEUTRAL, hover="#444441",
                      fill=True).grid(row=0, column=i, padx=(0 if i == 0 else 5, 5 if i < 2 else 0), sticky="ew")

        # ── Separador ────────────────────────────────────────────
        self._sep(outer, row=8)

        # ── Backup / Restaurar / Eliminar todos ──────────────────
        ops = tk.Frame(outer, bg=BG)
        ops.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ops.columnconfigure(0, weight=1)

        self._btn(ops, "Ejecutar Backup",
                  lambda: self._backup_con_validacion(),
                  color="#185FA5", hover="#0C447C", fill=True).grid(
                      row=0, column=0, sticky="ew", pady=(0, 6))

        self._btn(ops, "Eliminar todos los Grupos",
                  self.eliminar_todos,
                  color=DANGER, hover=DANGER_HOV, fill=True).grid(
                      row=1, column=0, sticky="ew", pady=(0, 6))

        self._btn(ops, "Restaurar todos los Grupos",
                  self.restaurar_todos,
                  color=NEUTRAL, hover="#444441", fill=True).grid(
                      row=2, column=0, sticky="ew")

        outer.columnconfigure(0, weight=1)

    # ─────────────────────────── Widget helpers ──────────────────
    def _btn(self, parent, text, command, color=NEUTRAL, hover="#444441",
             fill=False):
        """Botón plano con hover y bordes redondeados simulados."""
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                        fg=color, bg=SURFACE if not fill else BG,
                        activeforeground=hover,
                        activebackground=BORDER,
                        relief="solid", bd=1,
                        highlightthickness=0,
                        cursor="hand2",
                        pady=5, padx=10,
                        command=command)
        btn.bind("<Enter>", lambda e: btn.configure(fg=hover, bg=BORDER))
        btn.bind("<Leave>", lambda e: btn.configure(fg=color, bg=SURFACE if not fill else BG))
        return btn

    def _sep(self, parent, row):
        sep = tk.Frame(parent, height=1, bg=BORDER)
        sep.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def _actualizar_contador(self):
        try:
            n = self.collection.count_documents({})
            self.lbl_count.configure(text=f"{n} grupo{'s' if n != 1 else ''}")
        except Exception:
            self.lbl_count.configure(text="")

    # ─────────────────────────── Validaciones ────────────────────
    def _validar_clave(self, clave: str) -> bool:
        """Valida que la clave no esté vacía y solo tenga caracteres permitidos."""
        if not clave:
            messagebox.showwarning("Validación", "La Clave no puede estar vacía.")
            return False
        if not VALID_CLAVE.match(clave):
            messagebox.showwarning(
                "Validación",
                "La Clave solo puede contener letras, números, guiones y guiones\n"
                "bajos, sin espacios, y un máximo de 20 caracteres.\n\n"
                f"Valor ingresado: '{clave}'"
            )
            return False
        return True

    def _validar_nombre(self, nombre: str) -> bool:
        """Valida que el nombre no esté vacío y solo tenga caracteres permitidos."""
        if not nombre:
            messagebox.showwarning("Validación", "El Nombre no puede estar vacío.")
            return False
        if not VALID_NOMBRE.match(nombre):
            messagebox.showwarning(
                "Validación",
                "El Nombre contiene caracteres no válidos o supera 80 caracteres.\n"
                "Se permiten: letras (incluyendo acentos y ñ), números, espacios,\n"
                "guiones, puntos, comas y paréntesis.\n\n"
                f"Valor ingresado: '{nombre}'"
            )
            return False
        return True

    # ─────────────────────────── Helpers ─────────────────────────
    def _get_clave(self):
        return self.entry_clave.get().strip()

    def _get_nombre(self):
        return self.entry_nombre.get().strip()

    def limpiar(self):
        self.entry_clave.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_clave.focus()

    # ─────────────────────────── CRUD ────────────────────────────
    def buscar(self):
        clave = self._get_clave()
        if not self._validar_clave(clave):
            return
        doc = self.collection.find_one({"cveGru": clave})
        if doc:
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, doc["nomGru"])
            messagebox.showinfo("Buscar",
                f"Grupo encontrado:\nClave: {doc['cveGru']}\nNombre: {doc['nomGru']}")
        else:
            messagebox.showwarning("Buscar",
                f"No se encontró ningún grupo con clave '{clave}'.")

    def agregar(self):
        clave  = self._get_clave()
        nombre = self._get_nombre()
        if not self._validar_clave(clave):
            return
        if not self._validar_nombre(nombre):
            return
        if agregar_grupo(self.collection, clave, nombre):
            messagebox.showinfo("Agregar", f"Grupo '{clave}' agregado correctamente.")
            self.limpiar()
            self._actualizar_contador()
        else:
            messagebox.showerror("Agregar", f"Ya existe un grupo con clave '{clave}'.")

    def modificar(self):
        clave  = self._get_clave()
        nombre = self._get_nombre()
        if not self._validar_clave(clave):
            return
        if not self._validar_nombre(nombre):
            return
        if modificar_grupo(self.collection, clave, nombre):
            messagebox.showinfo("Modificar", f"Grupo '{clave}' modificado correctamente.")
            self.limpiar()
        else:
            messagebox.showerror("Modificar",
                f"No se encontró ningún grupo con clave '{clave}'.")

    def eliminar(self):
        clave = self._get_clave()
        if not self._validar_clave(clave):
            return
        if messagebox.askyesno("Eliminar", f"¿Desea eliminar el grupo '{clave}'?"):
            if eliminar_grupo(self.collection, clave):
                messagebox.showinfo("Eliminar",
                    f"Grupo '{clave}' eliminado correctamente.")
                self.limpiar()
                self._actualizar_contador()
            else:
                messagebox.showerror("Eliminar",
                    f"No se encontró ningún grupo con clave '{clave}'.")

    def eliminar_todos(self):
        # Validar que haya datos antes de proceder
        n = self.collection.count_documents({})
        if n == 0:
            messagebox.showwarning("Eliminar todos",
                "No hay grupos para eliminar.")
            return
        if messagebox.askyesno("Eliminar todos",
                f"¿Está seguro de eliminar los {n} grupos?\n"
                "Esta acción no se puede deshacer."):
            eliminar_todos(self.collection)
            messagebox.showinfo("Eliminar todos",
                "Todos los grupos han sido eliminados.")
            self._actualizar_contador()

    def restaurar_todos(self):
        if messagebox.askyesno("Restaurar todos",
                "¿Desea restaurar todos los grupos desde el backup?"):
            ok = restaurar_todos(self.collection)
            if ok:
                messagebox.showinfo("Restaurar todos",
                    "Grupos restaurados correctamente.")
                self._actualizar_contador()
            else:
                messagebox.showerror("Restaurar todos",
                    "No se encontró archivo de backup para restaurar.")

    # ── Backup con validación de colección no vacía ───────────────
    def _backup_con_validacion(self):
        n = self.collection.count_documents({})
        if n == 0:
            messagebox.showwarning("Ejecutar Backup",
                "No hay datos en la colección.\n"
                "El backup solo puede realizarse cuando existan grupos registrados.")
            return
        ejecutar_backup(self.collection)


if __name__ == "__main__":
    root = tk.Tk()
    app = AdmonGrupo(root)
    root.mainloop()