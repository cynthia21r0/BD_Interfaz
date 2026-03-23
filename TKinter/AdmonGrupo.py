import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import re

# Permite importar módulos desde el directorio padre del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Grupo.AgrGrupo import agregar_grupo
from Grupo.ModGrupo import modificar_grupo
from Grupo.EliGrupo import eliminar_grupo
from Grupo.EjeBackup import ejecutar_backup
from Grupo.ResEliGrupo import restaurar_todos, eliminar_todos
from Grupo.Exportar import exportar_csv, exportar_json, exportar_xml
from Grupo.Importar import importar_csv, importar_json, importar_xml
from db.conexion import get_collection


# Colores
BG          = "#F7F6F3"   # Fondo general de la ventana
SURFACE     = "#FFFFFF"   # Fondo de tarjetas y entradas
BORDER      = "#E2DFD8"   # Color de bordes
TEXT_PRI    = "#2C2C2A"   # Texto principal
TEXT_SEC    = "#5F5E5A"   # Texto secundario (labels)
ACCENT      = "#1D9E75"   # Verde principal (botones agregar, buscar)
ACCENT_HOV  = "#0F6E56"   # Verde oscuro al pasar el mouse
ACCENT_LITE = "#E1F5EE"   # Verde muy claro (fondo del título)
DANGER      = "#E24B4A"   # Rojo (eliminar)
DANGER_HOV  = "#A32D2D"   # Rojo oscuro al pasar el mouse
NEUTRAL     = "#3A3A38"   # Gris oscuro (botones neutros)
BTN_BORDER  = "#B4B2A9"   # Borde de botones

INDIGO      = "#4F46E5"   # Azul índigo (modificar)
INDIGO_HOV  = "#3730A3"
AMBER       = "#D97706"   # Ámbar (limpiar, advertencias)
AMBER_HOV   = "#92400E"
VIOLET      = "#7C3AED"   # Violeta (exportar)
VIOLET_HOV  = "#5B21B6"
CYAN        = "#0891B2"   # Cian (importar)
CYAN_HOV    = "#0E7490"
BURNT       = "#C2410C"   # Naranja quemado (restaurar)
BURNT_HOV   = "#9A3412"

DISABLED_FG = "#C0BDB8"   # Texto de botones deshabilitados
DISABLED_BG = "#F0EEEA"   # Fondo de botones deshabilitados

# Fuentes
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_LABEL  = ("Segoe UI", 9)
FONT_ENTRY  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 9)
FONT_TITLE  = ("Segoe UI", 13, "bold")

# Validación de Entradas
#  VALID_CLAVE:  solo letras, números, guiones y guiones bajos,
#                máximo 20 caracteres, sin espacios
# VALID_NOMBRE: letras (con acentos y ñ), números, espacios y
#                algunos caracteres especiales, máximo 80 caracteres
VALID_CLAVE  = re.compile(r'^[A-Za-z0-9\-_]{1,20}$')
VALID_NOMBRE = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑ0-9 \-_.,()]{1,80}$')

# Rutas de Archivos Exportados
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_EXPORT_PATHS = {
    "csv":  os.path.join(_BASE_DIR, "ExpImp", "Grupo.csv"),
    "json": os.path.join(_BASE_DIR, "ExpImp", "Grupo.json"),
    "xml":  os.path.join(_BASE_DIR, "ExpImp", "Grupo.xml"),
}

# Funciones auxiliares de validación rápida
def _clave_valida(v):  return bool(v) and bool(VALID_CLAVE.match(v))
def _nombre_valido(v): return bool(v) and bool(VALID_NOMBRE.match(v))

# CLASE PRINCIPAL
class AdmonGrupo:
    def __init__(self, root):
        self.root = root
        self.root.title("Administración de Grupos")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Conexión a las colecciones de MongoDB
        self.collection = get_collection("BD_GrupoAlumno", "Grupo")
        self.col_alu    = get_collection("BD_GrupoAlumno", "Alumno")  # para eliminación en cascada

        # Variables enlazadas a los campos de texto
        self.var_clave  = tk.StringVar()
        self.var_nombre = tk.StringVar()

        # Cada vez que el usuario escribe, se re-evalúan los botones
        self.var_clave.trace_add("write",  lambda *_: self._actualizar_botones())
        self.var_nombre.trace_add("write", lambda *_: self._actualizar_botones())

        # Diccionario de botones: { nombre: (widget, función_que_devuelve_bool) }
        # La función determina si el botón debe estar habilitado o no.
        self._btns = {}

        self._build_ui()
        self._actualizar_botones()

    # CONSTRUCCIÓN DE LA INTERFAZ
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG, padx=20, pady=18)
        outer.pack(fill="both", expand=True)

        # Título con contador de grupos
        title_frame = tk.Frame(outer, bg=ACCENT_LITE, padx=12, pady=8,
                               relief="flat", bd=0)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        tk.Label(title_frame, text="Grupos", font=FONT_TITLE,
                 bg=ACCENT_LITE, fg=ACCENT_HOV).pack(side="left")
        self.lbl_count = tk.Label(title_frame, text="", font=FONT_LABEL,
                                  bg=ACCENT_LITE, fg=TEXT_SEC)
        self.lbl_count.pack(side="right")
        self._actualizar_contador()

        # Tarjeta con los campos Clave y Nombre ────────────────
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14,
                        relief="solid", bd=1, highlightthickness=0)
        card.configure(highlightbackground=BORDER)
        card.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Campo: Clave
        tk.Label(card, text="Clave", font=FONT_LABEL, bg=SURFACE,
                 fg=TEXT_SEC).grid(row=0, column=0, sticky="w", pady=(0, 2))
        entry_row = tk.Frame(card, bg=SURFACE)
        entry_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.entry_clave = tk.Entry(entry_row, font=FONT_ENTRY, width=22,
                                    textvariable=self.var_clave,
                                    bg=SURFACE, fg=TEXT_PRI,
                                    relief="solid", bd=1,
                                    highlightthickness=1,
                                    highlightbackground=BORDER,
                                    highlightcolor=ACCENT,
                                    insertbackground=TEXT_PRI)
        self.entry_clave.pack(side="left")

        btn_buscar = self._btn(entry_row, "Buscar", self.buscar,
                               color=ACCENT, hover=ACCENT_HOV)
        btn_buscar.pack(side="left", padx=(8, 0))
        # Habilitado solo si la clave ingresada es válida
        self._btns["buscar"] = (btn_buscar,
                                lambda: _clave_valida(self.var_clave.get().strip()))

        # Campo: Nombre
        tk.Label(card, text="Nombre", font=FONT_LABEL, bg=SURFACE,
                 fg=TEXT_SEC).grid(row=2, column=0, sticky="w", pady=(0, 2))
        nombre_row = tk.Frame(card, bg=SURFACE)
        nombre_row.grid(row=3, column=0, sticky="ew", pady=(0, 2))
        self.entry_nombre = tk.Entry(nombre_row, font=FONT_ENTRY, width=22,
                                     textvariable=self.var_nombre,
                                     bg=SURFACE, fg=TEXT_PRI,
                                     relief="solid", bd=1,
                                     highlightthickness=1,
                                     highlightbackground=BORDER,
                                     highlightcolor=ACCENT,
                                     insertbackground=TEXT_PRI)
        self.entry_nombre.pack(side="left")

        btn_limpiar = self._btn(nombre_row, "Limpiar", self.limpiar,
                                color=AMBER, hover=AMBER_HOV)
        btn_limpiar.pack(side="left", padx=(8, 0))
        # Habilitado si al menos uno de los campos tiene contenido
        self._btns["limpiar"] = (btn_limpiar,
                                 lambda: bool(self.var_clave.get() or self.var_nombre.get()))

        # Botones CRUD
        crud = tk.Frame(outer, bg=BG)
        crud.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        crud.columnconfigure((0, 1, 2), weight=1)

        btn_agregar = self._btn(crud, "Agregar", self.agregar,
                                color=ACCENT, hover=ACCENT_HOV)
        btn_agregar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        # Requiere clave Y nombre válidos
        self._btns["agregar"] = (btn_agregar,
                                 lambda: (_clave_valida(self.var_clave.get().strip()) and
                                          _nombre_valido(self.var_nombre.get().strip())))

        btn_modificar = self._btn(crud, "Modificar", self.modificar,
                                  color=INDIGO, hover=INDIGO_HOV)
        btn_modificar.grid(row=0, column=1, padx=5, sticky="ew")
        # Requiere clave Y nombre válidos
        self._btns["modificar"] = (btn_modificar,
                                   lambda: (_clave_valida(self.var_clave.get().strip()) and
                                            _nombre_valido(self.var_nombre.get().strip())))

        btn_eliminar = self._btn(crud, "Eliminar", self.eliminar,
                                 color=DANGER, hover=DANGER_HOV)
        btn_eliminar.grid(row=0, column=2, padx=(5, 0), sticky="ew")
        # Solo requiere clave válida
        self._btns["eliminar"] = (btn_eliminar,
                                  lambda: _clave_valida(self.var_clave.get().strip()))

        # Separador visual
        self._sep(outer, row=3)

        # Sección EXPORTAR
        tk.Label(outer, text="EXPORTAR", font=("Segoe UI", 8),
                 bg=BG, fg=TEXT_SEC).grid(row=4, column=0, sticky="w", pady=(10, 4))
        exp_frame = tk.Frame(outer, bg=BG)
        exp_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
        exp_frame.columnconfigure((0, 1, 2), weight=1)

        exp_configs = [
            ("CSV",  lambda: self._exportar_y_refrescar("csv",  exportar_csv)),
            ("JSON", lambda: self._exportar_y_refrescar("json", exportar_json)),
            ("XML",  lambda: self._exportar_y_refrescar("xml",  exportar_xml)),
        ]
        for i, (lbl, fn) in enumerate(exp_configs):
            b = self._btn(exp_frame, lbl, fn, color=VIOLET, hover=VIOLET_HOV)
            b.grid(row=0, column=i,
                   padx=(0 if i == 0 else 5, 5 if i < 2 else 0), sticky="ew")
            # Habilitado solo si hay datos en la colección
            self._btns[f"exp_{lbl.lower()}"] = (b, self._hay_datos)

        # Sección IMPORTAR
        # El label muestra dinámicamente qué formatos están disponibles
        self.lbl_importar = tk.Label(outer, font=("Segoe UI", 8), bg=BG)
        self.lbl_importar.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 4))
        self._actualizar_label_importar()

        imp_frame = tk.Frame(outer, bg=BG)
        imp_frame.grid(row=7, column=0, columnspan=2, sticky="ew")
        imp_frame.columnconfigure((0, 1, 2), weight=1)

        imp_configs = [
            ("CSV",  "csv",  lambda: self._importar_y_refrescar(importar_csv)),
            ("JSON", "json", lambda: self._importar_y_refrescar(importar_json)),
            ("XML",  "xml",  lambda: self._importar_y_refrescar(importar_xml)),
        ]
        for i, (lbl, fmt, fn) in enumerate(imp_configs):
            b = self._btn(imp_frame, lbl, fn, color=CYAN, hover=CYAN_HOV)
            b.grid(row=0, column=i,
                   padx=(0 if i == 0 else 5, 5 if i < 2 else 0), sticky="ew")
            
            # Verificamos si el archivo físico existe en disco
            fmt_capturado = fmt
            self._btns[f"imp_{lbl.lower()}"] = (
                b,
                lambda f=fmt_capturado: self._archivo_existe(f)
            )

        # Separador visual
        self._sep(outer, row=8)

        # Sección BACKUP / RESTAURAR / ELIMINAR TODOS
        ops = tk.Frame(outer, bg=BG)
        ops.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ops.columnconfigure(0, weight=1)

        btn_backup = self._btn(ops, "Ejecutar Backup",
                               lambda: self._backup_con_validacion(),
                               color="#185FA5", hover="#0C447C")
        btn_backup.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self._btns["backup"] = (btn_backup, self._hay_datos)

        btn_eli_todos = self._btn(ops, "Eliminar todos los Grupos",
                                  self.eliminar_todos,
                                  color=DANGER, hover=DANGER_HOV)
        btn_eli_todos.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self._btns["eli_todos"] = (btn_eli_todos, self._hay_datos)

        btn_restaurar = self._btn(ops, "Restaurar todos los Grupos",
                                  self.restaurar_todos,
                                  color=BURNT, hover=BURNT_HOV)
        btn_restaurar.grid(row=2, column=0, sticky="ew")

        outer.columnconfigure(0, weight=1)

    # VERIFICACIÓN DE ARCHIVOS EN DISCO
    def _archivo_existe(self, fmt: str) -> bool:
        ruta = _EXPORT_PATHS.get(fmt, "")
        return bool(ruta) and os.path.isfile(ruta)

    # Estado de los botones
    def _hay_datos(self) -> bool:
        """Retorna True si la colección tiene al menos un documento."""
        try:
            return self.collection.count_documents({}) > 0
        except Exception:
            return False

    def _actualizar_botones(self):
        """
        Recorre todos los botones registrados en self._btns y
        habilita o deshabilita cada uno según su regla asociada.
        Se llama automáticamente al escribir en los campos y
        después de cada operación CRUD / exportar / importar.
        """
        for key, (widget, regla) in self._btns.items():
            habilitado = regla()
            self._set_btn_state(widget, habilitado, key)

    def _set_btn_state(self, btn, habilitado: bool, key: str = ""):
        """Aplica visualmente el estado habilitado/deshabilitado a un botón."""
        if habilitado:
            btn.configure(state="normal", cursor="hand2",
                          bg=btn._bg_normal if hasattr(btn, "_bg_normal") else btn.cget("bg"),
                          fg=btn._fg_normal if hasattr(btn, "_fg_normal") else btn.cget("fg"))
        else:
            if not hasattr(btn, "_fg_normal"):
                btn._fg_normal = btn.cget("fg")
                btn._bg_normal = btn.cget("bg")
            btn.configure(state="disabled", cursor="",
                          fg=DISABLED_FG, bg=DISABLED_BG,
                          disabledforeground=DISABLED_FG)

    #  HELPERS DE WIDGETS
    def _btn(self, parent, text, command, color=NEUTRAL, hover="#111110", fill=False):
        bg_base = SURFACE
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                        fg=color, bg=bg_base,
                        activeforeground=hover,
                        activebackground=BORDER,
                        disabledforeground=DISABLED_FG,
                        relief="solid", bd=1,
                        highlightthickness=0,
                        cursor="hand2",
                        pady=5, padx=10,
                        command=command)
        btn._fg_normal = color
        btn._bg_normal = bg_base

        def on_enter(e):
            if btn["state"] == "normal":
                btn.configure(fg=hover, bg=BORDER)

        def on_leave(e):
            if btn["state"] == "normal":
                btn.configure(fg=btn._fg_normal, bg=btn._bg_normal)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _sep(self, parent, row):
        """Dibuja una línea horizontal separadora."""
        sep = tk.Frame(parent, height=1, bg=BORDER)
        sep.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    def _actualizar_contador(self):
        """Actualiza el texto del contador de grupos en el título."""
        try:
            n = self.collection.count_documents({})
            self.lbl_count.configure(text=f"{n} grupo{'s' if n != 1 else ''}")
        except Exception:
            self.lbl_count.configure(text="")

    def _actualizar_label_importar(self):
        """
        Actualiza el label de la sección IMPORTAR para indicar
        visualmente qué formatos están disponibles para importar,
        verificando la existencia real de los archivos en disco.
        """
        disponibles = [fmt.upper() for fmt in _EXPORT_PATHS if self._archivo_existe(fmt)]

        if not disponibles:
            # Ningún archivo exportado existe: advertencia en ámbar
            self.lbl_importar.configure(
                text="IMPORTAR  ⚠ Primero debes exportar el formato deseado",
                fg=AMBER
            )
        elif len(disponibles) == 3:
            # Los tres formatos disponibles: label simple
            self.lbl_importar.configure(text="IMPORTAR", fg=TEXT_SEC)
        else:
            # Algunos formatos disponibles: los lista en verde
            self.lbl_importar.configure(
                text=f"IMPORTAR  ✔ Disponible: {', '.join(disponibles)}",
                fg=ACCENT
            )

    def _refrescar(self):
        """Actualiza el contador y el estado de todos los botones."""
        self._actualizar_contador()
        self._actualizar_label_importar()
        self._actualizar_botones()

    # VALIDACIONES DE ENTRADA
    def _validar_clave(self, clave: str) -> bool:
        """
        Valida que la clave cumpla con el formato requerido.
        Muestra un mensaje de advertencia si no es válida.
        """
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
        """
        Valida que el nombre cumpla con el formato requerido.
        Muestra un mensaje de advertencia si no es válido.
        """
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

    #  HELPERS DE CAMPOS
    def _get_clave(self):
        return self.var_clave.get().strip()

    def _get_nombre(self):
        return self.var_nombre.get().strip()

    def limpiar(self):
        self.var_clave.set("")
        self.var_nombre.set("")
        self.entry_clave.focus()

    #  EXPORTAR / IMPORTAR
    def _exportar_y_refrescar(self, fmt: str, fn_exportar):
        fn_exportar(self.collection)
        self._refrescar()

    def _importar_y_refrescar(self, fn_importar):
        fn_importar(self.collection)
        self._refrescar()

    #  OPERACIONES CRUD
    def buscar(self):
        """Busca un grupo por clave y muestra sus datos en los campos."""
        clave = self._get_clave()
        if not self._validar_clave(clave):
            return
        doc = self.collection.find_one({"cveGru": clave})
        if doc:
            self.var_nombre.set(doc["nomGru"])
            messagebox.showinfo("Buscar",
                f"Grupo encontrado:\nClave: {doc['cveGru']}\nNombre: {doc['nomGru']}")
        else:
            messagebox.showwarning("Buscar",
                f"No se encontró ningún grupo con clave '{clave}'.")

    def agregar(self):
        """Agrega un nuevo grupo. Verifica que la clave no exista previamente."""
        clave  = self._get_clave()
        nombre = self._get_nombre()
        if not self._validar_clave(clave):   return
        if not self._validar_nombre(nombre): return
        if self.collection.find_one({"cveGru": clave}):
            messagebox.showwarning("Agregar",
                f"El grupo con clave '{clave}' ya se encuentra registrado.")
            return
        if agregar_grupo(self.collection, clave, nombre):
            messagebox.showinfo("Agregar", f"Grupo '{clave}' agregado correctamente.")
            self.limpiar()
            self._refrescar()
        else:
            messagebox.showerror("Agregar", "Ocurrió un error al intentar agregar el grupo.")

    def modificar(self):
        """Modifica el nombre de un grupo existente."""
        clave  = self._get_clave()
        nombre = self._get_nombre()
        if not self._validar_clave(clave):   return
        if not self._validar_nombre(nombre): return
        if not self.collection.find_one({"cveGru": clave}):
            messagebox.showwarning("Modificar",
                f"No se puede modificar. El grupo con clave '{clave}' no existe.")
            return
        if modificar_grupo(self.collection, clave, nombre):
            messagebox.showinfo("Modificar", f"Grupo '{clave}' modificado correctamente.")
            self.limpiar()
        else:
            messagebox.showerror("Modificar",
                "No se detectaron cambios o ocurrió un error al modificar.")

    def eliminar(self):
        """
        Elimina un grupo y en cascada todos sus alumnos vinculados.
        Solicita confirmación al usuario antes de proceder.
        """
        clave = self._get_clave()
        if not self._validar_clave(clave): return

        if not self.collection.find_one({"cveGru": clave}):
            messagebox.showwarning("Eliminar",
                f"No se puede eliminar. El grupo con clave '{clave}' no existe.")
            return

        # Cuenta los alumnos vinculados para informar al usuario
        n_alu = self.col_alu.count_documents({"cveGru": clave})
        msg = f"¿Desea eliminar definitivamente el grupo '{clave}'?"
        if n_alu > 0:
            msg += (f"\n\n⚠ Se eliminarán también {n_alu} "
                    f"alumno{'s' if n_alu != 1 else ''} vinculado{'s' if n_alu != 1 else ''} "
                    f"a este grupo.")

        if not messagebox.askyesno("Eliminar", msg):
            return

        # Eliminación en cascada: primero alumnos, luego el grupo
        if n_alu > 0:
            self.col_alu.delete_many({"cveGru": clave})

        if eliminar_grupo(self.collection, clave):
            detalle = f"Grupo '{clave}' eliminado correctamente."
            if n_alu > 0:
                detalle += (f"\n{n_alu} alumno{'s' if n_alu != 1 else ''} "
                            f"eliminado{'s' if n_alu != 1 else ''} en cascada.")
            messagebox.showinfo("Eliminar", detalle)
            self.limpiar()
            self._refrescar()
        else:
            messagebox.showerror("Eliminar",
                "Ocurrió un error interno al intentar eliminar el grupo.")

    def eliminar_todos(self):
        """
        Elimina todos los grupos y en cascada todos los alumnos.
        Solicita confirmación doble al usuario por ser una operación irreversible.
        """
        n_gru = self.collection.count_documents({})
        if n_gru == 0:
            messagebox.showwarning("Eliminar todos", "No hay grupos para eliminar.")
            return

        n_alu = self.col_alu.count_documents({})
        msg = (f"¿Está seguro de eliminar los {n_gru} grupos?\n"
               "Esta acción no se puede deshacer.")
        if n_alu > 0:
            msg += f"\n\n⚠ Se eliminarán también TODOS los alumnos ({n_alu})."

        if not messagebox.askyesno("Eliminar todos", msg):
            return

        # Cascada total: primero todos los alumnos, luego todos los grupos
        if n_alu > 0:
            self.col_alu.delete_many({})

        eliminar_todos(self.collection)
        detalle = "Todos los grupos han sido eliminados."
        if n_alu > 0:
            detalle += (f"\n{n_alu} alumno{'s' if n_alu != 1 else ''} "
                        f"eliminado{'s' if n_alu != 1 else ''} en cascada.")
        messagebox.showinfo("Eliminar todos", detalle)
        self._refrescar()

    def restaurar_todos(self):
        """Restaura todos los grupos desde el archivo de backup."""
        if messagebox.askyesno("Restaurar todos",
                "¿Desea restaurar todos los grupos desde el backup?"):
            ok = restaurar_todos(self.collection)
            if ok:
                messagebox.showinfo("Restaurar todos", "Grupos restaurados correctamente.")
                self._refrescar()
            else:
                messagebox.showerror("Restaurar todos",
                    "No se encontró archivo de backup para restaurar.")

    def _backup_con_validacion(self):
        """
        Ejecuta el backup solo si hay datos en la colección.
        Muestra advertencia si la colección está vacía.
        """
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