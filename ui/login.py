"""
Ventana de Inicio de Sesión (Login) con validación de credenciales y roles.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.usuario import UsuarioModel

class LoginWindow(tk.Tk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        self.title("TechStore - Inicio de Sesión")
        self.geometry("450x520")
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')

        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        self.configure(bg="#0f172a") # Fondo oscuro slate elegante
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.style.configure("Login.TEntry", fieldbackground="#ffffff", padding=6)
        self.style.configure("Login.TButton",
            font=("Segoe UI", 11, "bold"),
            background="#0284c7",
            foreground="#ffffff",
            padding=8
        )
        self.style.map("Login.TButton",
            background=[("active", "#0369a1")]
        )

    def _construir_ui(self):
        # Contenedor principal con margen
        frame_principal = tk.Frame(self, bg="#0f172a", padx=35, pady=25)
        frame_principal.pack(fill="both", expand=True)

        # 1. Logo / Ícono
        lbl_icono = tk.Label(
            frame_principal,
            text="💻",
            font=("Segoe UI Emoji", 40),
            bg="#0f172a",
            fg="#38bdf8"
        )
        lbl_icono.pack(pady=(0, 5))

        lbl_titulo = tk.Label(
            frame_principal,
            text="TECHSTORE",
            font=("Segoe UI", 18, "bold"),
            bg="#0f172a",
            fg="#f8fafc"
        )
        lbl_titulo.pack()

        lbl_subtitulo = tk.Label(
            frame_principal,
            text="Sistema de Inventario y Ventas",
            font=("Segoe UI", 10),
            bg="#0f172a",
            fg="#94a3b8"
        )
        lbl_subtitulo.pack(pady=(0, 20))

        # 2. Formulario de Credenciales
        frame_form = tk.Frame(frame_principal, bg="#1e293b", padx=20, pady=20, highlightbackground="#334155", highlightthickness=1)
        frame_form.pack(fill="x")

        # Campo Usuario
        lbl_user = tk.Label(frame_form, text="Nombre de Usuario:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#e2e8f0")
        lbl_user.pack(anchor="w", pady=(0, 4))

        self.entry_usuario = ttk.Entry(frame_form, font=("Segoe UI", 10), style="Login.TEntry")
        self.entry_usuario.pack(fill="x", pady=(0, 12))
        self.entry_usuario.focus_set()

        # Campo Contraseña
        lbl_pass = tk.Label(frame_form, text="Contraseña:", font=("Segoe UI", 9, "bold"), bg="#1e293b", fg="#e2e8f0")
        lbl_pass.pack(anchor="w", pady=(0, 4))

        self.entry_password = ttk.Entry(frame_form, font=("Segoe UI", 10), show="•", style="Login.TEntry")
        self.entry_password.pack(fill="x", pady=(0, 8))

        # Checkbox mostrar contraseña
        self.var_mostrar = tk.BooleanVar(value=False)
        chk_mostrar = tk.Checkbutton(
            frame_form,
            text="Mostrar contraseña",
            variable=self.var_mostrar,
            command=self._toggle_password,
            bg="#1e293b",
            fg="#94a3b8",
            activebackground="#1e293b",
            activeforeground="#f8fafc",
            selectcolor="#0f172a",
            font=("Segoe UI", 8)
        )
        chk_mostrar.pack(anchor="w", pady=(0, 15))

        # Botón Ingresar
        btn_ingresar = ttk.Button(
            frame_form,
            text="Iniciar Sesión",
            style="Login.TButton",
            command=self.iniciar_sesion
        )
        btn_ingresar.pack(fill="x")

        # Vincular tecla Enter en ambos campos
        self.entry_usuario.bind("<Return>", lambda e: self.iniciar_sesion())
        self.entry_password.bind("<Return>", lambda e: self.iniciar_sesion())

        # 3. Aviso Informativo de Administrador por defecto
        frame_info = tk.Frame(frame_principal, bg="#0f172a", pady=15)
        frame_info.pack(fill="x")

        lbl_info_tit = tk.Label(
            frame_info,
            text="Credenciales de acceso inicial:",
            font=("Segoe UI", 8, "bold"),
            bg="#0f172a",
            fg="#64748b"
        )
        lbl_info_tit.pack()

        lbl_info_cred = tk.Label(
            frame_info,
            text="Admin: admin / admin123\nVendedor: vendedor / ven123",
            font=("Segoe UI", 8),
            bg="#0f172a",
            fg="#94a3b8"
        )
        lbl_info_cred.pack(pady=(2, 0))

    def _toggle_password(self):
        if self.var_mostrar.get():
            self.entry_password.config(show="")
        else:
            self.entry_password.config(show="•")

    def iniciar_sesion(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get()

        if not usuario or not password:
            messagebox.showwarning("Atención", "Por favor complete todos los campos de acceso.", parent=self)
            return

        sesion, error = UsuarioModel.autenticar(usuario, password)
        if error:
            messagebox.showerror("Error de Autenticación", error, parent=self)
            self.entry_password.delete(0, tk.END)
            self.entry_password.focus_set()
            return

        # Login correcto: destruir ventana de login y abrir app principal
        self.destroy()
        self.on_login_success(sesion)
