-- =====================================================================
-- TechStore - Base de datos MySQL compatible con la sincronización en la nube
-- Tablas con los mismos nombres de columna que usa la app (UUID entre tablas).
-- Abrir en MySQL Workbench: File > Open SQL Script > ejecutar con el rayo.
-- Usuarios demo: admin / admin123 (administrador) y vendedor / ven123 (vendedor).
-- =====================================================================
CREATE DATABASE IF NOT EXISTS techstore CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE techstore;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `conflictos_sincronizacion`;
DROP TABLE IF EXISTS `movimientos_stock`;
DROP TABLE IF EXISTS `detalle_ventas`;
DROP TABLE IF EXISTS `ventas`;
DROP TABLE IF EXISTS `clientes`;
DROP TABLE IF EXISTS `productos`;
DROP TABLE IF EXISTS `proveedores`;
DROP TABLE IF EXISTS `categorias`;
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    rol VARCHAR(20) NOT NULL,
    activo INT NOT NULL DEFAULT 1,
    creado_en VARCHAR(30) NULL,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    ruc_dni VARCHAR(20) NOT NULL UNIQUE,
    razon_social VARCHAR(150) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(50),
    email VARCHAR(100),
    direccion TEXT,
    activo INT NOT NULL DEFAULT 1,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(200) NOT NULL,
    categoria_uuid VARCHAR(36),
    proveedor_uuid VARCHAR(36),
    marca VARCHAR(100),
    precio_compra DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    stock_minimo INT NOT NULL DEFAULT 3,
    descripcion TEXT,
    activo INT NOT NULL DEFAULT 1,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    tipo_documento VARCHAR(20) DEFAULT 'DNI',
    numero_documento VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    telefono VARCHAR(50),
    email VARCHAR(100),
    direccion TEXT,
    activo INT NOT NULL DEFAULT 1,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE movimientos_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    producto_uuid VARCHAR(36) NOT NULL,
    tipo_movimiento VARCHAR(20) NOT NULL,
    cantidad INT NOT NULL,
    motivo TEXT,
    referencia VARCHAR(100),
    fecha VARCHAR(30) NOT NULL,
    usuario_uuid VARCHAR(36),
    proveedor_uuid VARCHAR(36),
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    numero_comprobante VARCHAR(50) NOT NULL UNIQUE,
    tipo_comprobante VARCHAR(30) NOT NULL DEFAULT 'Boleta',
    fecha VARCHAR(30) NOT NULL,
    cliente_uuid VARCHAR(36),
    usuario_uuid VARCHAR(36),
    subtotal DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    descuento DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    impuesto DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    total DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    metodo_pago VARCHAR(50) NOT NULL DEFAULT 'Efectivo',
    estado VARCHAR(30) NOT NULL DEFAULT 'Completada',
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(36) NOT NULL UNIQUE,
    venta_uuid VARCHAR(36) NOT NULL,
    producto_uuid VARCHAR(36) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_modificacion VARCHAR(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
CREATE TABLE conflictos_sincronizacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabla VARCHAR(50) NOT NULL,
    registro_uuid VARCHAR(36) NOT NULL,
    campo VARCHAR(50),
    valor_local TEXT,
    valor_remoto TEXT,
    fecha_conflicto VARCHAR(30) NULL,
    resuelto INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO `usuarios` (`id`, `uuid`, `username`, `password_hash`, `salt`, `nombre_completo`, `rol`, `activo`, `creado_en`, `fecha_modificacion`) VALUES (1, '2deac9e4-6248-4c04-9018-7516f3de949e', 'admin', '9c4c15c96e681b7e109dc49b57f6536e73dfe57cfa0e38765e3421d31ca5a3b9', 'b3933cadced305d17ae787223e213970', 'Administrador del Sistema', 'administrador', 1, '2026-11-15 13:11:50', '2026-11-15 13:11:50');
INSERT INTO `usuarios` (`id`, `uuid`, `username`, `password_hash`, `salt`, `nombre_completo`, `rol`, `activo`, `creado_en`, `fecha_modificacion`) VALUES (2, '5b3a2353-f299-4b66-930e-94ccd0071601', 'vendedor', '4e6041ae98bb81fe11cf83f9d26af5fec22cc41af48ad183f011c74a3b52340a', '091ebea1e272248c5e4098ac10e539ff', 'Carlos Vendedor', 'vendedor', 1, '2026-11-15 13:11:50', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (1, '2a863186-1d20-4b03-9a7d-b599e548753b', 'Procesadores (CPU)', 'Intel Core, AMD Ryzen, etc.', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (2, '985eaf4c-b9f1-44cb-9fe7-f2431d7005e8', 'Tarjetas Gráficas (GPU)', 'NVIDIA GeForce, AMD Radeon', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (3, 'beb52611-2a34-400e-b65d-47015825acd3', 'Placas Madre (Motherboard)', 'Sockets AM4, AM5, LGA1700', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (4, '87618fe5-3142-4af0-b1bb-79db86f3ad3f', 'Memorias RAM', 'DDR4, DDR5 para PC y Laptops', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (5, 'eb548c57-e5f6-479c-a99c-ff0904584722', 'Almacenamiento (SSD/HDD)', 'M.2 NVMe, SSD SATA, Discos Duros', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (6, 'a8c72200-c34b-422d-ab70-11ab96c37760', 'Fuentes de Poder (PSU)', 'Fuentes certificadas 80 Plus', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (7, 'eb401cd8-f6dc-4e53-98e3-3dc1cfa9ad3d', 'Gabinetes / Cases', 'Mid-Tower, Micro-ATX, Mini-ITX', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (8, '34a93dc0-6f3e-4892-bcea-9e3141d9c15d', 'Monitores', 'Gaming, Oficina, Profesionales', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (9, 'cd8c44c8-6e53-4219-a569-14534a97a2d3', 'Periféricos', 'Teclados, mouse, auriculares, webcams', '2026-11-15 13:11:50');
INSERT INTO `categorias` (`id`, `uuid`, `nombre`, `descripcion`, `fecha_modificacion`) VALUES (10, '43152eb7-d4f9-4348-b745-f8c96848d854', 'Laptops y Equipos', 'Portátiles gamer, ultrabooks, PCs armadas', '2026-11-15 13:11:50');
INSERT INTO `proveedores` (`id`, `uuid`, `ruc_dni`, `razon_social`, `contacto`, `telefono`, `email`, `direccion`, `activo`, `fecha_modificacion`) VALUES (1, 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', '20100123456', 'Deltron Importaciones S.A.', 'Juan Distribución', '01-4113000', 'ventas@deltron.local', 'Av. Argentina 4050, Lima', 1, '2026-11-15 13:11:50');
INSERT INTO `proveedores` (`id`, `uuid`, `ruc_dni`, `razon_social`, `contacto`, `telefono`, `email`, `direccion`, `activo`, `fecha_modificacion`) VALUES (2, 'd3697431-e0f2-4ea8-9d3e-478112dc9d41', '20255443322', 'Ingram Micro Perú S.A.C.', 'Área Mayorista', '01-5128000', 'contacto@ingram.local', 'Av. Materiales 3045, Callao', 1, '2026-11-15 13:11:50');
INSERT INTO `proveedores` (`id`, `uuid`, `ruc_dni`, `razon_social`, `contacto`, `telefono`, `email`, `direccion`, `activo`, `fecha_modificacion`) VALUES (3, '061ee954-0cd7-4720-882f-ae07b5a06660', '20334455667', 'TechData Solutions E.I.R.L.', 'Soporte Comercial', '01-6204000', 'pedidos@techdata.local', 'Av. República de Panamá 3500, San Isidro', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (1, '921e099e-ab0d-4374-a9ff-233d08c57482', 'CPU-INT-001', 'Procesador Intel Core i5-13400F 2.5/4.6GHz', '2a863186-1d20-4b03-9a7d-b599e548753b', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', 'Intel', 720.0, 890.0, 12, 3, '10 núcleos, 16 hilos, LGA1700', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (2, '7d59ae49-5e65-42a1-b09e-5ee22ab67897', 'CPU-AMD-002', 'Procesador AMD Ryzen 7 5700X 3.4/4.6GHz', '2a863186-1d20-4b03-9a7d-b599e548753b', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', 'AMD', 680.0, 830.0, 8, 2, '8 núcleos, 16 hilos, AM4', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (3, '53967a59-ff8e-46a1-a2cb-e79f9fee9d44', 'GPU-NV-001', 'Tarjeta Gráfica ASUS Dual GeForce RTX 4060 OC 8GB', '985eaf4c-b9f1-44cb-9fe7-f2431d7005e8', 'd3697431-e0f2-4ea8-9d3e-478112dc9d41', 'ASUS', 1350.0, 1620.0, 5, 2, 'GDDR6, DLSS 3, Ray Tracing', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (4, '9a9e79f0-19ef-4a35-a90f-9cdc09e77e3d', 'RAM-KNG-001', 'Memoria RAM Kingston Fury Beast 16GB DDR4 3200MHz', '87618fe5-3142-4af0-b1bb-79db86f3ad3f', '061ee954-0cd7-4720-882f-ae07b5a06660', 'Kingston', 140.0, 185.0, 25, 5, 'Disipador negro, CL16', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (5, '8394020e-c8a5-44e1-ac20-95fed33c9da0', 'SSD-KNG-002', 'Disco Sólido SSD M.2 NVMe Kingston NV2 1TB PCIe 4.0', 'eb548c57-e5f6-479c-a99c-ff0904584722', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', 'Kingston', 210.0, 275.0, 15, 4, 'Lectura hasta 3500 MB/s', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (6, 'fbf281f9-97d6-4b3e-bd47-c9b0d9b1a80d', 'PSU-COR-001', 'Fuente de Poder Corsair CV650 650W 80 Plus Bronze', 'a8c72200-c34b-422d-ab70-11ab96c37760', 'd3697431-e0f2-4ea8-9d3e-478112dc9d41', 'Corsair', 240.0, 310.0, 7, 2, 'Certificación 80 Plus Bronze', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (7, 'ed2f8e52-ddbf-44f6-b073-c8a936238dac', 'PER-LOG-001', 'Mouse Gamer Logitech G502 HERO 25K', 'cd8c44c8-6e53-4219-a569-14534a97a2d3', '061ee954-0cd7-4720-882f-ae07b5a06660', 'Logitech', 150.0, 219.0, 10, 3, 'Sensor HERO 25K, 11 botones', 1, '2026-11-15 13:11:50');
INSERT INTO `productos` (`id`, `uuid`, `codigo`, `nombre`, `categoria_uuid`, `proveedor_uuid`, `marca`, `precio_compra`, `precio_venta`, `stock`, `stock_minimo`, `descripcion`, `activo`, `fecha_modificacion`) VALUES (8, 'f75f5ec1-8cc5-4d20-8080-2546eb0d105f', 'PER-RED-002', 'Teclado Mecánico Redragon Kumara K552 RGB', 'cd8c44c8-6e53-4219-a569-14534a97a2d3', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', 'Redragon', 120.0, 169.0, 2, 3, 'Switches Outemu Red (Alerta Stock Bajo)', 1, '2026-11-15 13:11:50');
INSERT INTO `clientes` (`id`, `uuid`, `tipo_documento`, `numero_documento`, `nombre`, `telefono`, `email`, `direccion`, `activo`, `fecha_modificacion`) VALUES (1, 'c32c210e-94b6-47bb-be0e-4b4d6274cfdb', 'DNI', '00000000', 'Público General / Venta Rápida', '-', '-', '-', 1, '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (1, 'f717cc84-4a64-4ebb-a12d-93cc72ec4faa', '921e099e-ab0d-4374-a9ff-233d08c57482', 'ENTRADA', 12, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (2, '75b47f4f-bc71-40ac-b8fc-fd73cafd4f4a', '7d59ae49-5e65-42a1-b09e-5ee22ab67897', 'ENTRADA', 8, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (3, '1a94b99f-3539-4006-9b6f-2bbe6109c187', '53967a59-ff8e-46a1-a2cb-e79f9fee9d44', 'ENTRADA', 5, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'd3697431-e0f2-4ea8-9d3e-478112dc9d41', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (4, '707204b3-36f9-46b0-8a57-e1e9f8941703', '9a9e79f0-19ef-4a35-a90f-9cdc09e77e3d', 'ENTRADA', 25, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', '061ee954-0cd7-4720-882f-ae07b5a06660', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (5, '2c519287-485e-4044-adce-b66abf048b92', '8394020e-c8a5-44e1-ac20-95fed33c9da0', 'ENTRADA', 15, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (6, '0008a6eb-5bc6-46fa-8bca-bce831c5699d', 'fbf281f9-97d6-4b3e-bd47-c9b0d9b1a80d', 'ENTRADA', 7, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'd3697431-e0f2-4ea8-9d3e-478112dc9d41', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (7, '79eae2c0-6c5a-430f-8739-b63c153b7c1e', 'ed2f8e52-ddbf-44f6-b073-c8a936238dac', 'ENTRADA', 10, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', '061ee954-0cd7-4720-882f-ae07b5a06660', '2026-11-15 13:11:50');
INSERT INTO `movimientos_stock` (`id`, `uuid`, `producto_uuid`, `tipo_movimiento`, `cantidad`, `motivo`, `referencia`, `fecha`, `usuario_uuid`, `proveedor_uuid`, `fecha_modificacion`) VALUES (8, '04c0d795-86c0-4ae2-af60-a5dbd031be3f', 'f75f5ec1-8cc5-4d20-8080-2546eb0d105f', 'ENTRADA', 2, 'Inventario inicial de apertura', 'Guía Inicial 001', '2026-11-15 13:11:50', '2deac9e4-6248-4c04-9018-7516f3de949e', 'ea19bd63-ff0b-4068-88f2-79515e03cf9b', '2026-11-15 13:11:50');
SET FOREIGN_KEY_CHECKS = 1;
