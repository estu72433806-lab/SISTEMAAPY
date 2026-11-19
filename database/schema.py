"""
Definición de tablas e inicialización de datos para la tienda de computadoras.
Incluye soporte para usuarios con contraseñas hasheadas (PBKDF2-HMAC-SHA256),
roles (administrador, vendedor), inventario, proveedores y movimientos de stock.
"""
import os
import secrets
import hashlib
from datetime import datetime
from database.db import get_connection

# Opciones comunes de todas las tablas (motor InnoDB y acentos/ñ correctos)
_OPC = "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

# Columnas usadas por la sincronización con la nube (modo híbrido)
_SYNC = """
    uuid VARCHAR(36) NULL,
    sincronizado TINYINT(1) NOT NULL DEFAULT 0,
    fecha_modificacion DATETIME NULL,"""

DDL_STATEMENTS = [
f"""
-- 1. Tabla de Usuarios del Sistema
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    nombre_completo VARCHAR(120) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('administrador', 'vendedor')),
    activo TINYINT(1) NOT NULL DEFAULT 1,
    creado_en DATETIME NOT NULL,{_SYNC}
    UNIQUE KEY uq_usuarios_uuid (uuid)
) {_OPC};
""",
f"""
-- 2. Tabla de Categorías de Hardware / Cómputo
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),{_SYNC}
    UNIQUE KEY uq_categorias_uuid (uuid)
) {_OPC};
""",
f"""
-- 3. Tabla de Proveedores de Tecnología
CREATE TABLE IF NOT EXISTS proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruc_dni VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(30),
    email VARCHAR(100),
    direccion VARCHAR(200),
    activo TINYINT(1) NOT NULL DEFAULT 1,{_SYNC}
    UNIQUE KEY uq_proveedores_uuid (uuid)
) {_OPC};
""",
f"""
-- 4. Tabla de Productos y Componentes
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    categoria_id INT NULL,
    proveedor_id INT NULL,
    marca VARCHAR(80),
    precio_compra DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 3,
    descripcion TEXT,
    activo TINYINT(1) NOT NULL DEFAULT 1,{_SYNC}
    UNIQUE KEY uq_productos_uuid (uuid),
    CONSTRAINT fk_productos_categoria FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL,
    CONSTRAINT fk_productos_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
) {_OPC};
""",
f"""
-- 5. Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_documento VARCHAR(10) DEFAULT 'DNI',
    numero_documento VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(30),
    email VARCHAR(100),
    direccion VARCHAR(200),
    activo TINYINT(1) NOT NULL DEFAULT 1,{_SYNC}
    UNIQUE KEY uq_clientes_uuid (uuid)
) {_OPC};
""",
f"""
-- 6. Tabla de Movimientos de Stock (Kardex / Auditoría)
CREATE TABLE IF NOT EXISTS movimientos_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    tipo_movimiento VARCHAR(10) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA', 'SALIDA', 'AJUSTE')),
    cantidad INT NOT NULL,
    motivo VARCHAR(255),
    referencia VARCHAR(100),
    fecha DATETIME NOT NULL,
    usuario_id INT NULL,
    proveedor_id INT NULL,{_SYNC}
    UNIQUE KEY uq_movimientos_uuid (uuid),
    CONSTRAINT fk_mov_producto FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    CONSTRAINT fk_mov_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    CONSTRAINT fk_mov_proveedor FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL
) {_OPC};
""",
f"""
-- 7. Tabla de Ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_comprobante VARCHAR(30) NOT NULL UNIQUE,
    tipo_comprobante VARCHAR(20) NOT NULL DEFAULT 'Boleta',
    fecha DATETIME NOT NULL,
    cliente_id INT NULL,
    usuario_id INT NULL,
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    descuento DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    impuesto DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    metodo_pago VARCHAR(50) NOT NULL DEFAULT 'Efectivo',
    estado VARCHAR(20) NOT NULL DEFAULT 'Completada',{_SYNC}
    UNIQUE KEY uq_ventas_uuid (uuid),
    CONSTRAINT fk_ventas_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
    CONSTRAINT fk_ventas_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
) {_OPC};
""",
f"""
-- 8. Tabla de Detalle de Venta
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    venta_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,{_SYNC}
    UNIQUE KEY uq_detalle_uuid (uuid),
    CONSTRAINT fk_detalle_venta FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES productos(id)
) {_OPC};
""",
f"""
-- 9. Estado de la sincronización con la nube
CREATE TABLE IF NOT EXISTS sincronizacion_info (
    id INT PRIMARY KEY,
    ultima_sincronizacion VARCHAR(30),
    estado VARCHAR(30) DEFAULT 'DESCONECTADO',
    detalles TEXT
) {_OPC};
""",
f"""
-- 10. Conflictos detectados al sincronizar
CREATE TABLE IF NOT EXISTS conflictos_sincronizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL,
    registro_uuid VARCHAR(36) NOT NULL,
    campo VARCHAR(50),
    valor_local TEXT,
    valor_remoto TEXT,
    fecha_conflicto DATETIME NOT NULL,
    resuelto TINYINT(1) NOT NULL DEFAULT 0
) {_OPC};
"""
]

DEFAULT_CATEGORIAS = [
    ("Procesadores (CPU)", "Intel Core, AMD Ryzen, etc."),
    ("Tarjetas Gráficas (GPU)", "NVIDIA GeForce, AMD Radeon"),
    ("Placas Madre (Motherboard)", "Sockets AM4, AM5, LGA1700"),
    ("Memorias RAM", "DDR4, DDR5 para PC y Laptops"),
    ("Almacenamiento (SSD/HDD)", "M.2 NVMe, SSD SATA, Discos Duros"),
    ("Fuentes de Poder (PSU)", "Fuentes certificadas 80 Plus"),
    ("Gabinetes / Cases", "Mid-Tower, Micro-ATX, Mini-ITX"),
    ("Monitores", "Gaming, Oficina, Profesionales"),
    ("Periféricos", "Teclados, mouse, auriculares, webcams"),
    ("Laptops y Equipos", "Portátiles gamer, ultrabooks, PCs armadas")
]

DEFAULT_PROVEEDORES = [
    ("20100123456", "Deltron Importaciones S.A.", "Juan Distribución", "01-4113000", "ventas@deltron.local", "Av. Argentina 4050, Lima"),
    ("20255443322", "Ingram Micro Perú S.A.C.", "Área Mayorista", "01-5128000", "contacto@ingram.local", "Av. Materiales 3045, Callao"),
    ("20334455667", "TechData Solutions E.I.R.L.", "Soporte Comercial", "01-6204000", "pedidos@techdata.local", "Av. República de Panamá 3500, San Isidro")
]

def hash_password(password: str, salt: str = None):
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_bytes = password.encode('utf-8')
    salt_bytes = bytes.fromhex(salt)
    key = hashlib.pbkdf2_hmac('sha256', pwd_bytes, salt_bytes, 100000)
    return key.hex(), salt

def verificar_password(password: str, password_hash: str, salt: str) -> bool:
    try:
        nuevo_hash, _ = hash_password(password, salt)
        return secrets.compare_digest(nuevo_hash, password_hash)
    except Exception:
        return False

import uuid
from database.db import get_connection, crear_base_si_no_existe

def init_db():
    """Crea la base de datos MySQL y sus tablas (si no existen) e inserta datos iniciales."""
    crear_base_si_no_existe()
    conn = get_connection()
    cursor = conn.cursor()
    for sentencia in DDL_STATEMENTS:
        cursor.execute(sentencia)

    # Inicializar registro único de estado si no existe
    cursor.execute("SELECT COUNT(*) FROM sincronizacion_info WHERE id = 1;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO sincronizacion_info (id, ultima_sincronizacion, estado, detalles)
            VALUES (1, 'Nunca', 'MODO_LOCAL', 'Sistema iniciado en modo local.');
        """)

    # Asegurar que todos los registros tengan UUID y fecha de modificación (modo híbrido)
    tablas_sync = [
        "usuarios", "categorias", "proveedores", "productos",
        "clientes", "movimientos_stock", "ventas", "detalle_ventas"
    ]
    for tabla in tablas_sync:
        # Generar UUID único y fecha para registros existentes que no lo tengan
        cursor.execute(f"SELECT id FROM {tabla} WHERE uuid IS NULL OR uuid = '';")
        filas = cursor.fetchall()
        for f in filas:
            row_id = f[0]
            gen_uuid = str(uuid.uuid4())
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                f"UPDATE {tabla} SET uuid = ?, fecha_modificacion = COALESCE(fecha_modificacion, ?) WHERE id = ?;",
                (gen_uuid, ahora, row_id)
            )

    # 1. Crear el primer administrador si no existe
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'administrador';")
    if cursor.fetchone()[0] == 0:
        pwd_hash, salt = hash_password("admin123")
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        admin_uuid = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO usuarios (uuid, username, password_hash, salt, nombre_completo, rol, activo, creado_en, fecha_modificacion, sincronizado)
            VALUES (?, ?, ?, ?, ?, 'administrador', 1, ?, ?, 1);
        """, (admin_uuid, "admin", pwd_hash, salt, "Administrador del Sistema", fecha_creacion, fecha_creacion))

    # 2. Insertar categorías de cómputo por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM categorias;")
    if cursor.fetchone()[0] == 0:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for cat in DEFAULT_CATEGORIAS:
            cursor.execute(
                "INSERT INTO categorias (uuid, nombre, descripcion, fecha_modificacion, sincronizado) VALUES (?, ?, ?, ?, 1);",
                (str(uuid.uuid4()), cat[0], cat[1], ahora)
            )

    # 3. Proveedores iniciales si está vacía
    cursor.execute("SELECT COUNT(*) FROM proveedores;")
    if cursor.fetchone()[0] == 0:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for prov in DEFAULT_PROVEEDORES:
            cursor.execute("""
                INSERT INTO proveedores (uuid, ruc_dni, razon_social, contacto, telefono, email, direccion, activo, fecha_modificacion, sincronizado)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 1);
            """, (str(uuid.uuid4()), prov[0], prov[1], prov[2], prov[3], prov[4], prov[5], ahora))

    # 4. Cliente genérico para venta rápida / público en general
    cursor.execute("SELECT COUNT(*) FROM clientes WHERE numero_documento = '00000000';")
    if cursor.fetchone()[0] == 0:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO clientes (uuid, tipo_documento, numero_documento, nombre, telefono, email, direccion, activo, fecha_modificacion, sincronizado)
            VALUES (?, 'DNI', '00000000', 'Público General / Venta Rápida', '-', '-', '-', 1, ?, 1);
        """, (str(uuid.uuid4()), ahora))

    conn.commit()
    conn.close()
