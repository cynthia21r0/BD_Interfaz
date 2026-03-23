import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import re

# Permite importar módulos desde el directorio padre del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Alumno.AgrAlumno    import agregar_alumno
from Alumno.ModAlumno    import modificar_alumno
from Alumno.EliAlumno    import eliminar_alumno
from Alumno.EjeBackup    import ejecutar_backup
from Alumno.ResEliAlumno import restaurar_todos, eliminar_todos
from Alumno.Exportar     import exportar_csv, exportar_json, exportar_xml
from Alumno.Importar     import importar_csv, importar_json, importar_xml
from db.conexion         import get_collection

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
FONT_LABEL  = ("Segoe UI", 9)
FONT_ENTRY  = ("Segoe UI", 10)
FONT_BTN    = ("Segoe UI", 9)
FONT_TITLE  = ("Segoe UI", 13, "bold")

#  Validaciones de entradas
#  VALID_CLAVE:  solo dígitos, máximo 10
#  VALID_NOMBRE: letras (con acentos y ñ), números, espacios y
#                algunos caracteres especiales, máximo 80 caracteres
#  VALID_EDAD:   solo dígitos, máximo 3 (rango 1-120 se verifica aparte)
#  VALID_GRUPO:  letras, números, guiones y guiones bajos, máximo 20
VALID_CLAVE  = re.compile(r'^\d{1,10}$')
VALID_NOMBRE = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑ0-9 \-_.,()]{1,80}$')
VALID_EDAD   = re.compile(r'^\d{1,3}$')
VALID_GRUPO  = re.compile(r'^[A-Za-z0-9\-_]{1,20}$')

# Rutas de archivos importados
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_EXPORT_PATHS = {
    "csv":  os.path.join(_BASE_DIR, "ExpImp", "Alumno.csv"),
    "json": os.path.join(_BASE_DIR, "ExpImp", "Alumno.json"),
    "xml":  os.path.join(_BASE_DIR, "ExpImp", "Alumno.xml"),
}

# Funciones auxiliares de validación rápida
def _clave_valida(v):  return bool(v) and bool(VALID_CLAVE.match(v))
def _nombre_valido(v): return bool(v) and bool(VALID_NOMBRE.match(v))
def _edad_valida(v):   return bool(v) and bool(VALID_EDAD.match(v)) and 1 <= int(v) <= 120
def _grupo_valido(v):  return bool(v) and bool(VALID_GRUPO.match(v))

#  CLASE PRINCIPAL
class AdmonAlumno:
    def __init__(self, root):
        self.root = root
        self.root.title("Administración de Alumnos")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # Conexión a las colecciones de MongoDB
        self.col_alu = get_collection("BD_GrupoAlumno", "Alumno")
        self.col_gru = get_collection("BD_GrupoAlumno", "Grupo")

        # Variables enlazadas a los campos de texto
        self.var_clave  = tk.StringVar()
        self.var_nombre = tk.StringVar()
        self.var_edad   = tk.StringVar()
        self.var_grupo  = tk.StringVar()

        # Cada vez que el usuario escribe, se re-evalúan los botones
        for var in (self.var_clave, self.var_nombre, self.var_edad, self.var_grupo):
            var.trace_add("write", lambda *_: self._actualizar_botones())

        # Diccionario de botones: { nombre: (widget, función_que_devuelve_bool) }
        # La función determina si el botón debe estar habilitado o no.
        self._btns = {}

        self._build_ui()
        self._actualizar_botones()

    #  CONSTRUCCIÓN DE LA INTERFAZ
    def _build_ui(self):
        outer = tk.Frame(self.root, bg=BG, padx=20, pady=18)
        outer.pack(fill="both", expand=True)

        # Título con contador de alumnos
        title_frame = tk.Frame(outer, bg=ACCENT_LITE, padx=12, pady=8)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        tk.Label(title_frame, text="Alumnos", font=FONT_TITLE,
                 bg=ACCENT_LITE, fg=ACCENT_HOV).pack(side="left")
        self.lbl_count = tk.Label(title_frame, text="", font=FONT_LABEL,
                                  bg=ACCENT_LITE, fg=TEXT_SEC)
        self.lbl_count.pack(side="right")
        self._actualizar_contador()

        # Tarjeta con los campos del alumno
        card = tk.Frame(outer, bg=SURFACE, padx=16, pady=14,
                        relief="solid", bd=1)
        card.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Campo: Clave Alumno + Buscar
        tk.Label(card, text="Clave Alumno", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_SEC).grid(row=0, column=0, sticky="w", pady=(0, 2))
        row_clave = tk.Frame(card, bg=SURFACE)
        row_clave.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.entry_clave = self._entry(row_clave, self.var_clave)
        self.entry_clave.pack(side="left")
        btn_buscar = self._btn(row_clave, "Buscar", self.buscar,
                               color=ACCENT, hover=ACCENT_HOV)
        btn_buscar.pack(side="left", padx=(8, 0))
        # Habilitado solo si la clave ingresada es válida
        self._btns["buscar"] = (btn_buscar,
                                lambda: _clave_valida(self.var_clave.get().strip()))

        # Campo: Nombre + Limpiar
        tk.Label(card, text="Nombre", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_SEC).grid(row=2, column=0, sticky="w", pady=(0, 2))
        row_nom = tk.Frame(card, bg=SURFACE)
        row_nom.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        self.entry_nombre = self._entry(row_nom, self.var_nombre)
        self.entry_nombre.pack(side="left")
        btn_limpiar = self._btn(row_nom, "Limpiar", self.limpiar,
                                color=AMBER, hover=AMBER_HOV)
        btn_limpiar.pack(side="left", padx=(8, 0))
        # Habilitado si al menos uno de los campos tiene contenido
        self._btns["limpiar"] = (btn_limpiar,
                                 lambda: bool(self.var_clave.get() or self.var_nombre.get()
                                              or self.var_edad.get() or self.var_grupo.get()))

        # Campos: Edad y Clave Grupo en paralelo
        row_extra = tk.Frame(card, bg=SURFACE)
        row_extra.grid(row=4, column=0, sticky="ew", pady=(0, 4))

        col_eda = tk.Frame(row_extra, bg=SURFACE)
        col_eda.pack(side="left", padx=(0, 16))
        tk.Label(col_eda, text="Edad", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_SEC).pack(anchor="w")
        self.entry_edad = self._entry(col_eda, self.var_edad, width=8)
        self.entry_edad.pack(anchor="w")

        col_gru = tk.Frame(row_extra, bg=SURFACE)
        col_gru.pack(side="left")
        tk.Label(col_gru, text="Clave Grupo", font=FONT_LABEL,
                 bg=SURFACE, fg=TEXT_SEC).pack(anchor="w")
        self.entry_grupo = self._entry(col_gru, self.var_grupo, width=14)
        self.entry_grupo.pack(anchor="w")

        # Botones CRUD
        crud = tk.Frame(outer, bg=BG)
        crud.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        crud.columnconfigure((0, 1, 2), weight=1)

        # Agregar y Modificar requieren los 4 campos válidos
        def _campos_completos():
            return (_clave_valida(self.var_clave.get().strip()) and
                    _nombre_valido(self.var_nombre.get().strip()) and
                    _edad_valida(self.var_edad.get().strip()) and
                    _grupo_valido(self.var_grupo.get().strip()))

        btn_agregar = self._btn(crud, "Agregar", self.agregar,
                                color=ACCENT, hover=ACCENT_HOV)
        btn_agregar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self._btns["agregar"] = (btn_agregar, _campos_completos)

        btn_modificar = self._btn(crud, "Modificar", self.modificar,
                                  color=INDIGO, hover=INDIGO_HOV)
        btn_modificar.grid(row=0, column=1, padx=5, sticky="ew")
        self._btns["modificar"] = (btn_modificar, _campos_completos)

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
                               self._backup_con_validacion,
                               color="#185FA5", hover="#0C447C")
        btn_backup.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        self._btns["backup"] = (btn_backup, self._hay_datos)

        btn_eli_todos = self._btn(ops, "Eliminar todos los Alumnos",
                                  self.eliminar_todos,
                                  color=DANGER, hover=DANGER_HOV)
        btn_eli_todos.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self._btns["eli_todos"] = (btn_eli_todos, self._hay_datos)

        btn_restaurar = self._btn(ops, "Restaurar todos los Alumnos",
                                  self.restaurar_todos,
                                  color=BURNT, hover=BURNT_HOV)
        btn_restaurar.grid(row=2, column=0, sticky="ew")

        outer.columnconfigure(0, weight=1)

    #  VERIFICACIÓN DE ARCHIVOS EN DISCO
    def _archivo_existe(self, fmt: str) -> bool:
        ruta = _EXPORT_PATHS.get(fmt, "")
        return bool(ruta) and os.path.isfile(ruta)

    #  HELPERS DE WIDGETS
    def _entry(self, parent, textvariable, width=22):
        """Crea y retorna un campo de texto con estilo consistente."""
        return tk.Entry(parent, font=FONT_ENTRY, width=width,
                        textvariable=textvariable,
                        bg=SURFACE, fg=TEXT_PRI,
                        relief="solid", bd=1,
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=ACCENT,
                        insertbackground=TEXT_PRI)

    def _btn(self, parent, text, command, color=NEUTRAL, hover="#111110"):
        """
        Crea y retorna un botón con estilo consistente.
        Incluye efectos hover (cambio de color al pasar el mouse).
        """
        btn = tk.Button(parent, text=text, font=FONT_BTN,
                        fg=color, bg=SURFACE,
                        activeforeground=hover,
                        activebackground=BORDER,
                        disabledforeground=DISABLED_FG,
                        relief="solid", bd=1,
                        highlightthickness=0,
                        cursor="hand2",
                        pady=5, padx=10,
                        command=command)
        btn._fg_normal = color
        btn._bg_normal = SURFACE

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
        tk.Frame(parent, height=1, bg=BORDER).grid(
            row=row, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    #  ESTADO DE BOTONES
    def _hay_datos(self) -> bool:
        try:
            return self.col_alu.count_documents({}) > 0
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
            self._set_btn_state(widget, regla())

    def _set_btn_state(self, btn, habilitado: bool):
        """Aplica visualmente el estado habilitado/deshabilitado a un botón."""
        if habilitado:
            btn.configure(state="normal", cursor="hand2",
                          fg=btn._fg_normal, bg=btn._bg_normal)
        else:
            if not hasattr(btn, "_fg_normal"):
                btn._fg_normal = btn.cget("fg")
                btn._bg_normal = btn.cget("bg")
            btn.configure(state="disabled", cursor="",
                          fg=DISABLED_FG, bg=DISABLED_BG,
                          disabledforeground=DISABLED_FG)

    def _actualizar_contador(self):
        """Actualiza el texto del contador de alumnos en el título."""
        try:
            n = self.col_alu.count_documents({})
            self.lbl_count.configure(text=f"{n} alumno{'s' if n != 1 else ''}")
        except Exception:
            self.lbl_count.configure(text="")

    def _actualizar_label_importar(self):
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
        """Actualiza el contador, el label de importar y el estado de todos los botones."""
        self._actualizar_contador()
        self._actualizar_label_importar()
        self._actualizar_botones()

    #  VALIDACIONES DE ENTRADA
    def _validar_clave(self, clave: str) -> bool:
        """Valida que la clave sea un número entero positivo de máximo 10 dígitos."""
        if not clave:
            messagebox.showwarning("Validación", "La Clave del alumno no puede estar vacía.")
            return False
        if not VALID_CLAVE.match(clave):
            messagebox.showwarning(
                "Validación",
                "La Clave del alumno debe ser un número entero positivo "
                "(máximo 10 dígitos).\n\n"
                f"Valor ingresado: '{clave}'"
            )
            return False
        return True

    def _validar_nombre(self, nombre: str) -> bool:
        """Valida que el nombre cumpla con el formato requerido."""
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

    def _validar_edad(self, edad: str) -> bool:
        """Valida que la edad sea un número entero entre 1 y 120."""
        if not edad:
            messagebox.showwarning("Validación", "La Edad no puede estar vacía.")
            return False
        if not VALID_EDAD.match(edad) or not (1 <= int(edad) <= 120):
            messagebox.showwarning(
                "Validación",
                "La Edad debe ser un número entero entre 1 y 120.\n\n"
                f"Valor ingresado: '{edad}'"
            )
            return False
        return True

    def _validar_grupo(self, cve_gru: str) -> bool:
        """Valida que la clave de grupo cumpla con el formato requerido."""
        if not cve_gru:
            messagebox.showwarning("Validación", "La Clave del Grupo no puede estar vacía.")
            return False
        if not VALID_GRUPO.match(cve_gru):
            messagebox.showwarning(
                "Validación",
                "La Clave del Grupo solo puede contener letras, números, guiones\n"
                "y guiones bajos, sin espacios, máximo 20 caracteres.\n\n"
                f"Valor ingresado: '{cve_gru}'"
            )
            return False
        return True

    #  HELPERS DE CAMPOS
    def _get(self, var):
        """Retorna el valor de una variable sin espacios al inicio/fin."""
        return var.get().strip()

    def limpiar(self):
        """Limpia todos los campos y devuelve el foco al campo Clave."""
        for v in (self.var_clave, self.var_nombre, self.var_edad, self.var_grupo):
            v.set("")
        self.entry_clave.focus()

    #  EXPORTAR / IMPORTAR
    def _exportar_y_refrescar(self, fmt: str, fn_exportar):
        fn_exportar(self.col_alu)
        self._refrescar()

    def _importar_y_refrescar(self, fn_importar):
        fn_importar(self.col_alu, self.col_gru)
        self._refrescar()

    #  OPERACIONES CRUD
    def buscar(self):
        """Busca un alumno por clave y muestra sus datos en los campos."""
        clave = self._get(self.var_clave)
        if not self._validar_clave(clave):
            return
        doc = self.col_alu.find_one({"cveAlu": int(clave)})
        if doc:
            self.var_nombre.set(doc["nomAlu"])
            self.var_edad.set(str(doc["edaAlu"]))
            self.var_grupo.set(doc["cveGru"])
            messagebox.showinfo(
                "Buscar",
                f"Alumno encontrado:\n"
                f"Clave:  {doc['cveAlu']}\n"
                f"Nombre: {doc['nomAlu']}\n"
                f"Edad:   {doc['edaAlu']}\n"
                f"Grupo:  {doc['cveGru']}"
            )
        else:
            messagebox.showwarning("Buscar",
                f"No se encontró ningún alumno con clave '{clave}'.")

    def agregar(self):
        """Agrega un nuevo alumno. Verifica que la clave no exista y que el grupo sí."""
        clave  = self._get(self.var_clave)
        nombre = self._get(self.var_nombre)
        edad   = self._get(self.var_edad)
        grupo  = self._get(self.var_grupo)

        if not self._validar_clave(clave):   return
        if not self._validar_nombre(nombre): return
        if not self._validar_edad(edad):     return
        if not self._validar_grupo(grupo):   return

        resultado = agregar_alumno(
            self.col_alu, self.col_gru,
            int(clave), nombre, int(edad), grupo
        )

        if resultado == "ok":
            messagebox.showinfo("Agregar",
                f"Alumno '{clave}' agregado correctamente.")
            self.limpiar()
            self._refrescar()
        elif resultado == "duplicado":
            messagebox.showwarning("Agregar",
                f"El alumno con clave '{clave}' ya se encuentra registrado.")
        elif resultado == "grupo":
            messagebox.showwarning("Agregar",
                f"El grupo '{grupo}' no existe.\n"
                "Registra primero el grupo antes de asignar alumnos.")
        else:
            messagebox.showerror("Agregar",
                "Ocurrió un error al intentar agregar el alumno.")

    def modificar(self):
        """Modifica los datos de un alumno existente."""
        clave  = self._get(self.var_clave)
        nombre = self._get(self.var_nombre)
        edad   = self._get(self.var_edad)
        grupo  = self._get(self.var_grupo)

        if not self._validar_clave(clave):   return
        if not self._validar_nombre(nombre): return
        if not self._validar_edad(edad):     return
        if not self._validar_grupo(grupo):   return

        if not self.col_alu.find_one({"cveAlu": int(clave)}):
            messagebox.showwarning("Modificar",
                f"No se puede modificar. El alumno con clave '{clave}' no existe.")
            return

        resultado = modificar_alumno(
            self.col_alu, self.col_gru,
            int(clave), nombre, int(edad), grupo
        )

        if resultado == "ok":
            messagebox.showinfo("Modificar", "Alumno actualizado correctamente.")
            self.limpiar()
            self._refrescar()
        elif resultado == "grupo":
            messagebox.showwarning("Modificar",
                f"El grupo '{grupo}' no existe.\n"
                "Solo puedes asignar grupos ya registrados.")
        else:
            messagebox.showerror("Modificar",
                "No se detectaron cambios o ocurrió un error al modificar.")

    def eliminar(self):
        """
        Elimina un alumno por clave.
        Solicita confirmación al usuario antes de proceder.
        """
        clave = self._get(self.var_clave)
        if not self._validar_clave(clave):
            return
        if not self.col_alu.find_one({"cveAlu": int(clave)}):
            messagebox.showwarning("Eliminar",
                f"No se puede eliminar. El alumno con clave '{clave}' no existe.")
            return
        if messagebox.askyesno("Eliminar",
                f"¿Desea eliminar definitivamente al alumno con clave '{clave}'?"):
            if eliminar_alumno(self.col_alu, int(clave)):
                messagebox.showinfo("Eliminar",
                    f"Alumno '{clave}' eliminado correctamente.")
                self.limpiar()
                self._refrescar()
            else:
                messagebox.showerror("Eliminar",
                    "Ocurrió un error interno al intentar eliminar el alumno.")

    def eliminar_todos(self):
        """
        Elimina todos los alumnos de la colección.
        Solicita confirmación al usuario por ser una operación irreversible.
        """
        n = self.col_alu.count_documents({})
        if n == 0:
            messagebox.showwarning("Eliminar todos", "No hay alumnos para eliminar.")
            return
        if messagebox.askyesno("Eliminar todos",
                f"¿Está seguro de eliminar los {n} alumnos?\n"
                "Esta acción no se puede deshacer."):
            eliminar_todos(self.col_alu)
            messagebox.showinfo("Eliminar todos",
                "Todos los alumnos han sido eliminados.")
            self._refrescar()

    def restaurar_todos(self):
        """Restaura todos los alumnos desde el archivo de backup."""
        if messagebox.askyesno("Restaurar todos",
                "¿Desea restaurar todos los alumnos desde el backup?"):
            ok = restaurar_todos(self.col_alu)
            if ok:
                messagebox.showinfo("Restaurar todos",
                    "Alumnos restaurados correctamente.")
                self._refrescar()
            else:
                messagebox.showerror("Restaurar todos",
                    "No se encontró archivo de backup para restaurar.")

    def _backup_con_validacion(self):
        """
        Ejecuta el backup solo si hay datos en la colección.
        Muestra advertencia si la colección está vacía.
        """
        n = self.col_alu.count_documents({})
        if n == 0:
            messagebox.showwarning("Ejecutar Backup",
                "No hay datos en la colección.\n"
                "El backup solo puede realizarse cuando existan alumnos registrados.")
            return
        ejecutar_backup(self.col_alu)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdmonAlumno(root)
    root.mainloop()