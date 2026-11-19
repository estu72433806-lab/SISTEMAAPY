"""
Punto de Entrada del Sistema de Inventario y Ventas - Tienda de Computadoras.
Desarrollado en Python 3 con Tkinter, MySQL (phpMyAdmin), ReportLab y openpyxl.
"""
import sys
import uuid
from database.schema import init_db
from database.db import get_connection
from models.usuario import UsuarioModel
from models.movimiento_stock import MovimientoStockModel
from ui.login import LoginWindow
from ui.app import MainApplication

def insertar_datos_demo():
    """Inserta productos y vendedor de demostración si la base de datos es nueva."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Crear vendedor de prueba si no existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'vendedor';")
    if cursor.fetchone()[0] == 0:
        UsuarioModel.crear_usuario(
            username="vendedor",
            password="ven123",
            nombre_completo="Carlos Vendedor",
            rol="vendedor"
        )

    # 2. Productos de hardware de muestra (solo si la tabla productos está vacía)
    cursor.execute("SELECT COUNT(*) FROM productos;")
    if cursor.fetchone()[0] == 0:
        productos_demo = [
            ("CPU-INT-001", "Procesador Intel Core i5-13400F 2.5/4.6GHz", 1, 1, "Intel", 720.00, 890.00, 12, 3, "10 núcleos, 16 hilos, LGA1700"),
            ("CPU-AMD-002", "Procesador AMD Ryzen 7 5700X 3.4/4.6GHz", 1, 1, "AMD", 680.00, 830.00, 8, 2, "8 núcleos, 16 hilos, AM4"),
            ("GPU-NV-001", "Tarjeta Gráfica ASUS Dual GeForce RTX 4060 OC 8GB", 2, 2, "ASUS", 1350.00, 1620.00, 5, 2, "GDDR6, DLSS 3, Ray Tracing"),
            ("RAM-KNG-001", "Memoria RAM Kingston Fury Beast 16GB DDR4 3200MHz", 4, 3, "Kingston", 140.00, 185.00, 25, 5, "Disipador negro, CL16"),
            ("SSD-KNG-002", "Disco Sólido SSD M.2 NVMe Kingston NV2 1TB PCIe 4.0", 5, 1, "Kingston", 210.00, 275.00, 15, 4, "Lectura hasta 3500 MB/s"),
            ("PSU-COR-001", "Fuente de Poder Corsair CV650 650W 80 Plus Bronze", 6, 2, "Corsair", 240.00, 310.00, 7, 2, "Certificación 80 Plus Bronze"),
            ("PER-LOG-001", "Mouse Gamer Logitech G502 HERO 25K", 9, 3, "Logitech", 150.00, 219.00, 10, 3, "Sensor HERO 25K, 11 botones"),
            ("PER-RED-002", "Teclado Mecánico Redragon Kumara K552 RGB", 9, 1, "Redragon", 120.00, 169.00, 2, 3, "Switches Outemu Red (Alerta Stock Bajo)")
        ]
        
        for p in productos_demo:
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, categoria_id, proveedor_id, marca, precio_compra, precio_venta, stock, stock_minimo, descripcion, activo,
                                       uuid, fecha_modificacion, sincronizado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, NOW(), 0);
            """, p + (str(uuid.uuid4()),))
            prod_id = cursor.lastrowid

            # Registrar movimiento de entrada de apertura en movimientos_stock
            cursor.execute("""
                INSERT INTO movimientos_stock (producto_id, tipo_movimiento, cantidad, motivo, referencia, fecha, usuario_id, proveedor_id,
                                               uuid, fecha_modificacion, sincronizado)
                VALUES (?, 'ENTRADA', ?, 'Inventario inicial de apertura', 'Guía Inicial 001', NOW(), 1, ?, ?, NOW(), 0);
            """, (prod_id, p[7], p[3], str(uuid.uuid4())))

        conn.commit()

    conn.close()

def iniciar_login():
    """Inicia la ventana de login."""
    def on_login_exitoso(usuario_sesion):
        app = MainApplication(usuario_sesion, on_logout=iniciar_login)
        app.mainloop()

    login_win = LoginWindow(on_login_success=on_login_exitoso)
    login_win.mainloop()

def mostrar_error_mysql(error):
    """Muestra una ventana explicando qué hacer si MySQL no está encendido."""
    import tkinter as tk
    from tkinter import messagebox
    from database.db import obtener_configuracion_mysql, get_config_path
    cfg = obtener_configuracion_mysql()
    raiz = tk.Tk()
    raiz.withdraw()
    messagebox.showerror(
        "No se pudo conectar a MySQL",
        "El sistema no pudo conectarse a la base de datos MySQL.\n\n"
        "Revisa lo siguiente:\n"
        "1. Abre XAMPP y presiona 'Start' en Apache y en MySQL.\n"
        "2. Verifica los datos de conexión en el archivo:\n"
        f"   {get_config_path()}\n"
        f"   (servidor: {cfg['host']}:{cfg['port']}, usuario: {cfg['user']}, base: {cfg['database']})\n\n"
        f"Detalle técnico: {error}"
    )
    raiz.destroy()

def main():
    # 1. Crear la base de datos y las tablas en MySQL automáticamente si no existen
    try:
        init_db()
    except Exception as e:
        mostrar_error_mysql(e)
        sys.exit(1)

    # 2. Cargar datos de demostración solo si es necesario para probar
    insertar_datos_demo()

    # 3. Lanzar flujo de inicio de sesión
    iniciar_login()

if __name__ == "__main__":
    main()
