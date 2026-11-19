"""
Ventana Principal de la Aplicación TechStore con control de roles y permisos.
Integra:
- Panel Principal (Dashboard con datos reales de MySQL y accesos rápidos)
- Inventario de Productos
- Movimientos de Stock (Kardex)
- Clientes y Proveedores (Contactos unificados)
- Punto de Venta (POS) con ReportLab PDF
- Reportes con Rango de Fechas y Excel (.xlsx) con openpyxl
- Gestión de Usuarios (exclusivo para Administrador)
"""
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from ui.views.dashboard_view import DashboardView
from ui.views.productos_view import ProductosView
from ui.views.movimientos_view import MovimientosStockView
from ui.views.contactos_view import ContactosView
from ui.views.ventas_view import VentasView
from ui.views.reportes_view import ReportesView
from ui.views.usuarios_view import UsuariosView
from ui.views.config_nube_dialog import ConfigNubeDialog
from services.sync_service import SyncService
from models.usuario import UsuarioModel

class MainApplication(tk.Tk):
    def __init__(self, usuario_sesion, on_logout=None):
        super().__init__()
        self.usuario_sesion = usuario_sesion
        self.on_logout = on_logout

        self.title("TechStore - Sistema de Inventario y Ventas Para Tienda de Computadoras")
        self.geometry("1240x780")
        self.minsize(1080, 660)
        self._configurar_estilos()
        self._construir_interfaz()

    def _configurar_estilos(self):
        self.style = ttk.Style(self)
        disponibles = self.style.theme_names()
        if "clam" in disponibles:
            self.style.theme_use("clam")

        COLOR_PRIMARIO = "#1e293b"
        COLOR_SECUNDARIO = "#0284c7"
        COLOR_FONDO = "#f8fafc"
        COLOR_TEXTO = "#0f172a"

        self.configure(bg=COLOR_FONDO)
        self.style.configure(".", font=("Segoe UI", 9), background=COLOR_FONDO, foreground=COLOR_TEXTO)

        # Estilos Notebook
        self.style.configure("TNotebook", background=COLOR_FONDO, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 9, "bold"), padding=[12, 7], background="#e2e8f0", foreground="#475569")
        self.style.map("TNotebook.Tab",
            background=[("selected", "#ffffff")],
            foreground=[("selected", COLOR_SECUNDARIO)]
        )

        # Botones
        self.style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=[7, 5])
        self.style.map("TButton", background=[("active", "#e2e8f0")])

        # Botones con color según la acción (para que se entienda mejor qué hace cada uno)
        #   Verde   = Guardar / Registrar / Confirmar
        #   Azul    = Actualizar / Buscar / Consultar
        #   Rojo    = Desactivar / Quitar / Eliminar
        #   Naranja = Asistentes y sugerencias automáticas
        #   Turquesa= Exportar a Excel
        #   Morado  = Ver PDF / Historial
        #   Gris    = Limpiar / Ver todo / Cerrar
        colores_botones = {
            "Exito":       ("#16a34a", "#15803d"),
            "Primario":    ("#2563eb", "#1d4ed8"),
            "Peligro":     ("#dc2626", "#b91c1c"),
            "Advertencia": ("#d97706", "#b45309"),
            "Exportar":    ("#0d9488", "#0f766e"),
            "Documento":   ("#7c3aed", "#6d28d9"),
            "Neutro":      ("#64748b", "#475569"),
        }
        for nombre, (color, color_hover) in colores_botones.items():
            estilo = f"{nombre}.TButton"
            self.style.configure(estilo, font=("Segoe UI", 9, "bold"), padding=[7, 5],
                                 background=color, foreground="#ffffff",
                                 bordercolor=color, lightcolor=color, darkcolor=color,
                                 focuscolor=color)
            self.style.map(estilo,
                background=[("disabled", "#cbd5e1"), ("pressed", color_hover), ("active", color_hover)],
                foreground=[("disabled", "#f1f5f9")],
                bordercolor=[("active", color_hover)],
                lightcolor=[("active", color_hover)],
                darkcolor=[("active", color_hover)]
            )

        # Tablas (Treeview)
        self.style.configure("Treeview",
            font=("Segoe UI", 9),
            rowheight=25,
            background="#ffffff",
            fieldbackground="#ffffff"
        )
        self.style.configure("Treeview.Heading",
            font=("Segoe UI", 9, "bold"),
            background="#f1f5f9",
            foreground="#1e293b",
            relief="flat"
        )
        self.style.map("Treeview",
            background=[("selected", "#0284c7")],
            foreground=[("selected", "#ffffff")]
        )

        self.style.configure("TLabelframe", background=COLOR_FONDO)
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"), foreground="#1e293b", background=COLOR_FONDO)

    def _construir_interfaz(self):
        # 1. Barra de Encabezado Superior
        frame_header = tk.Frame(self, bg="#0f172a", height=60, padx=20, pady=10)
        frame_header.pack(fill="x", side="top")

        lbl_logo = tk.Label(
            frame_header,
            text="💻 TECHSTORE COMPUTADORAS",
            font=("Segoe UI", 14, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        lbl_logo.pack(side="left")

        # Indicador de Usuario y Rol
        rol_display = self.usuario_sesion.get("rol", "").upper()
        nombre_display = self.usuario_sesion.get("nombre_completo", "Usuario")
        color_badge = "#22c55e" if rol_display == "ADMINISTRADOR" else "#f59e0b"

        frame_user = tk.Frame(frame_header, bg="#1e293b", padx=10, pady=4)
        frame_user.pack(side="right", padx=(10, 0))

        lbl_user_icon = tk.Label(
            frame_user,
            text="👤",
            font=("Segoe UI Emoji", 11),
            bg="#1e293b",
            fg="#38bdf8"
        )
        lbl_user_icon.pack(side="left", padx=(0, 5))

        lbl_user_info = tk.Label(
            frame_user,
            text=f"{nombre_display}  [{rol_display}]",
            font=("Segoe UI", 9, "bold"),
            bg="#1e293b",
            fg=color_badge
        )
        lbl_user_info.pack(side="left")

        btn_logout = tk.Button(
            frame_user,
            text="Cerrar Sesión",
            command=self.cerrar_sesion,
            font=("Segoe UI", 8, "bold"),
            bg="#ef4444",
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2"
        )
        btn_logout.pack(side="left", padx=(10, 0))

        self.lbl_reloj = tk.Label(
            frame_header,
            text="",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#0f172a"
        )
        self.lbl_reloj.pack(side="right", padx=(10, 15))
        self._actualizar_reloj()

        # Botones de Sincronización y Configuración Nube
        self.btn_sync = tk.Button(
            frame_header,
            text="🔄 Sincronizar",
            command=self.sincronizar_ahora,
            font=("Segoe UI", 8, "bold"),
            bg="#10b981",
            fg="#ffffff",
            activebackground="#059669",
            activeforeground="#ffffff",
            disabledforeground="#d1fae5",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_sync.pack(side="right", padx=(0, 8))

        self.btn_config_nube = tk.Button(
            frame_header,
            text="☁ Config Nube",
            command=self.abrir_config_nube,
            font=("Segoe UI", 8, "bold"),
            bg="#0284c7",
            fg="#ffffff",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        self.btn_config_nube.pack(side="right", padx=(0, 6))

        btn_asistente_header = tk.Button(
            frame_header,
            text="💡 Reposición",
            command=self.abrir_asistente_reposicion,
            font=("Segoe UI", 8, "bold"),
            bg="#d97706",
            fg="#ffffff",
            activebackground="#b45309",
            activeforeground="#ffffff",
            bd=0,
            padx=10,
            pady=3,
            cursor="hand2"
        )
        btn_asistente_header.pack(side="right", padx=(0, 6))

        # 2. Contenedor de Pestañas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Vistas
        self.vista_dashboard = DashboardView(
            self.notebook,
            usuario_sesion=self.usuario_sesion,
            on_navegar=self.navegar_a_pestana,
            on_abrir_asistente=self.abrir_asistente_reposicion,
            on_abrir_config_nube=self.abrir_config_nube
        )
        self.vista_productos = ProductosView(
            self.notebook,
            usuario_sesion=self.usuario_sesion,
            on_registrar_entrada=self.transferir_a_entrada_reposicion
        )
        self.vista_movimientos = MovimientosStockView(
            self.notebook,
            usuario_sesion=self.usuario_sesion,
            callback_stock_actualizado=self._on_datos_actualizados
        )
        self.vista_contactos = ContactosView(self.notebook, usuario_sesion=self.usuario_sesion)
        self.vista_ventas = VentasView(self.notebook, usuario_sesion=self.usuario_sesion, callback_producto_actualizado=self._on_datos_actualizados)
        self.vista_reportes = ReportesView(self.notebook, usuario_sesion=self.usuario_sesion)

        # Pestañas principales
        self.notebook.add(self.vista_dashboard, text="🏠 Inicio")
        self.notebook.add(self.vista_productos, text="📦 Inventario de Productos")
        self.notebook.add(self.vista_movimientos, text="🔄 Movimientos de Stock (Kardex)")
        self.notebook.add(self.vista_contactos, text="👥 Clientes y Proveedores")
        self.notebook.add(self.vista_ventas, text="🛒 Punto de Venta (POS)")
        self.notebook.add(self.vista_reportes, text="📊 Reportes y Exportación")

        # Pestaña de usuarios solo para Administrador
        es_admin = (self.usuario_sesion.get("rol") == "administrador")
        if es_admin:
            self.vista_usuarios = UsuariosView(self.notebook, usuario_sesion=self.usuario_sesion)
            self.notebook.add(self.vista_usuarios, text="👤 Usuarios")

        self.notebook.bind("<<NotebookTabChanged>>", self._on_cambio_pestana)

        # 3. Barra de Estado Inferior Híbrida
        frame_status = tk.Frame(self, bg="#e2e8f0", height=26, padx=10)
        frame_status.pack(fill="x", side="bottom")

        self.lbl_status_modo = tk.Label(
            frame_status,
            text="🟡 Modo: MySQL Local (Offline)",
            font=("Segoe UI", 8, "bold"),
            bg="#e2e8f0",
            fg="#b45309"
        )
        self.lbl_status_modo.pack(side="left")

        lbl_sep1 = tk.Label(frame_status, text=" | ", font=("Segoe UI", 8), bg="#e2e8f0", fg="#94a3b8")
        lbl_sep1.pack(side="left")

        self.lbl_status_pendientes = tk.Label(
            frame_status,
            text="0 pendientes",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg="#475569"
        )
        self.lbl_status_pendientes.pack(side="left")

        lbl_sep2 = tk.Label(frame_status, text=" | ", font=("Segoe UI", 8), bg="#e2e8f0", fg="#94a3b8")
        lbl_sep2.pack(side="left")

        lbl_status_db = tk.Label(
            frame_status,
            text=f"Sesión: {self.usuario_sesion.get('username')}",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg="#334155"
        )
        lbl_status_db.pack(side="left")

        lbl_status_info = tk.Label(
            frame_status,
            text="Sistema Híbrido: MySQL Local + PostgreSQL Nube",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg="#64748b"
        )
        lbl_status_info.pack(side="right")

        self.actualizar_estado_sync()

    def _actualizar_reloj(self):
        ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.lbl_reloj.config(text=f"📅 {ahora}")
        self.after(1000, self._actualizar_reloj)

    def navegar_a_pestana(self, indice):
        """Permite a los accesos directos del dashboard saltar a la pestaña correspondiente."""
        try:
            self.notebook.select(indice)
        except Exception:
            pass

    def _on_cambio_pestana(self, event=None):
        """Sincroniza y recarga los datos al cambiar de pestaña."""
        indice = self.notebook.index(self.notebook.select())
        if indice == 0:
            self.vista_dashboard.actualizar_metricas()
        elif indice == 1:
            self.vista_productos.cargar_selectores()
            self.vista_productos.cargar_productos()
        elif indice == 2:
            self.vista_movimientos.recargar_datos()
        elif indice == 3:
            self.vista_contactos.recargar_datos()
        elif indice == 4:
            self.vista_ventas.actualizar_datos()
        elif indice == 5:
            self.vista_reportes.cargar_ventas()
            self.vista_reportes.actualizar_indicadores()
        elif indice == 6 and hasattr(self, 'vista_usuarios'):
            self.vista_usuarios.cargar_usuarios()

    def _on_datos_actualizados(self):
        """Notificación disparada tras registrar ventas o movimientos de inventario."""
        self.vista_dashboard.actualizar_metricas()
        self.vista_productos.cargar_productos()
        self.vista_movimientos.recargar_datos()
        self.vista_ventas.actualizar_datos()
        self.vista_reportes.cargar_ventas()
        self.vista_reportes.actualizar_indicadores()
        self.actualizar_estado_sync()

    def actualizar_estado_sync(self):
        """Actualiza los indicadores visuales del modo híbrido y los registros pendientes."""
        try:
            from database.pg_config import tiene_credenciales_pg
            pendientes = SyncService.obtener_conteo_pendientes()
            modo, detalle = SyncService.obtener_estado_conexion()
            tiene_cred = tiene_credenciales_pg()

            if modo == "EN_LINEA":
                self.lbl_status_modo.config(text="🟢 Modo: En Línea (PostgreSQL Nube)", fg="#15803d")
                if hasattr(self, 'btn_config_nube'):
                    self.btn_config_nube.config(text="☁ Nube: En Línea 🟢", bg="#059669")
            else:
                self.lbl_status_modo.config(text="🟡 Modo: MySQL Local (Offline)", fg="#b45309")
                if hasattr(self, 'btn_config_nube'):
                    if tiene_cred:
                        self.btn_config_nube.config(text="☁ Nube: Local 🟡", bg="#d97706")
                    else:
                        self.btn_config_nube.config(text="☁ Conectar Nube ⚙", bg="#0284c7")

            if pendientes == 0:
                self.lbl_status_pendientes.config(text="✔ Sincronizado (0 pendientes)", fg="#15803d")
            else:
                self.lbl_status_pendientes.config(text=f"⚠ {pendientes} pendiente(s) de sincronizar", fg="#b91c1c")
        except Exception:
            pass

    def sincronizar_ahora(self):
        """
        Sube a la nube (PostgreSQL) lo guardado en MySQL y descarga las novedades.
        Se ejecuta en segundo plano para que la ventana no se congele mientras espera a internet.
        """
        if getattr(self, "_sync_en_curso", False):
            return
        # Si la nube todavía no está configurada, no se intenta conectar (así no sale
        # el aviso de error); se abre directamente la ventana para configurarla.
        from database.pg_config import tiene_credenciales_pg
        if not tiene_credenciales_pg():
            self.abrir_config_nube()
            return
        self._sync_en_curso = True
        self.btn_sync.config(state="disabled", text="⏳ Sincronizando...")
        resultado = {}

        def tarea():
            try:
                resultado["res"] = SyncService.sincronizar_todo()
            except Exception as e:
                resultado["error"] = str(e)

        hilo = threading.Thread(target=tarea, daemon=True)
        hilo.start()

        def revisar():
            if hilo.is_alive():
                self.after(300, revisar)
                return
            self._sync_en_curso = False
            self.btn_sync.config(state="normal", text="🔄 Sincronizar")
            if "error" in resultado:
                messagebox.showerror("Error", f"Ocurrió un error al sincronizar: {resultado['error']}")
            elif resultado["res"]["exito"]:
                messagebox.showinfo("Sincronización Exitosa", resultado["res"]["mensaje"])
            else:
                messagebox.showwarning("Aviso de Sincronización", resultado["res"]["mensaje"])
            self._on_datos_actualizados()
            self.actualizar_estado_sync()

        self.after(300, revisar)

    def abrir_config_nube(self):
        """Abre la ventana modal para configurar la base de datos PostgreSQL en la nube."""
        ConfigNubeDialog(self, on_guardado=self.actualizar_estado_sync)

    def abrir_asistente_reposicion(self, producto_id_foco=None):
        """Abre la ventana interactiva del Asistente Inteligente de Reposición."""
        from ui.views.asistente_reposicion_dialog import AsistenteReposicionDialog
        AsistenteReposicionDialog(
            self,
            on_registrar_entrada=self.transferir_a_entrada_reposicion,
            producto_id_foco=producto_id_foco
        )

    def transferir_a_entrada_reposicion(self, producto_id, cantidad, proveedor_id=None):
        """Navega a Movimientos de Stock y pre-configura la entrada sugerida."""
        self.navegar_a_pestana(2)
        self.vista_movimientos.preparar_entrada_producto(producto_id, cantidad, proveedor_id)

    def cerrar_sesion(self):
        confirmar = messagebox.askyesno("Cerrar Sesión", "¿Está seguro de que desea cerrar la sesión actual?")
        if confirmar:
            self.destroy()
            if self.on_logout:
                self.on_logout()
