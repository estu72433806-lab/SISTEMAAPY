# ⚙️ Base de datos MySQL (phpMyAdmin)

El sistema ahora guarda todo en **MySQL** (antes usaba SQLite) y se puede ver y administrar desde **phpMyAdmin**.

## Pasos para usarlo
1. Instala **XAMPP** y en su panel presiona **Start** en **Apache** y **MySQL**.
2. Instala las librerías: `pip install -r requirements.txt` (incluye **PyMySQL**).
3. (Opcional, para conservar los datos que ya tenías) Entra a `http://localhost/phpmyadmin`, pestaña **Importar**, elige `techstore_db.sql` y presiona **Importar**.
4. Ejecuta `python main.py`. Si la base `techstore_db` no existe, el sistema la crea sola con sus tablas y datos iniciales.

## Datos de conexión (`config_mysql.json`)
```json
{ "host": "localhost", "port": 3306, "user": "root", "password": "", "database": "techstore_db" }
```
Son los valores por defecto de XAMPP. Si tu MySQL tiene contraseña u otro puerto, cámbialo en ese archivo.

## Colores de los botones
- 🟩 Verde: guardar, registrar, confirmar
- 🟦 Azul: actualizar, buscar, consultar
- 🟥 Rojo: desactivar, quitar, vaciar
- 🟧 Naranja: asistentes y sugerencias automáticas
- Turquesa: exportar a Excel
- 🟪 Morado: ver PDF / historial
- ⬜ Gris: limpiar, ver todo, cerrar


---

# Sistema de Inventario y Ventas - TechStore Computadoras

Aplicación de escritorio para Windows desarrollada en **Python 3 con Tkinter, MySQL (phpMyAdmin) y PostgreSQL en la Nube (opcional)**.
Todos los datos se guardan en la base **MySQL `techstore_db`**. Si se configura PostgreSQL, el sistema puede enviar una copia a la nube con el botón **"🔄 Sincronizar"**.

---

## 🚀 1. Instalación y Ejecución

### Requisitos:
* Python 3.8 o superior instalado en Windows (marcar *"Add Python to PATH"* durante la instalación).
* XAMPP con **MySQL** encendido.

### Instalación de Dependencias:
Abre una terminal o PowerShell en la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```
*(Incluye `reportlab`, `openpyxl`, `pyinstaller`, `PyMySQL` y `psycopg2-binary`).*

### Ejecutar la Aplicación:
```bash
python main.py
```

---

## 🌐 2. Base de datos principal y copia en la nube

### 1. MySQL (base principal):
* Todo lo que se hace en el sistema (productos, clientes, proveedores, ventas, Kardex y usuarios) se guarda en **MySQL** (`techstore_db`).
* Se puede ver y administrar desde `http://localhost/phpmyadmin`.
* Cada registro tiene un identificador único global (**UUID**) y un estado `sincronizado` (0 = pendiente, 1 = enviado a la nube).

### 2. PostgreSQL en la nube (opcional):
* Si se configura, permite compartir catálogo, clientes y ventas entre varias computadoras.
* Si no se configura, el sistema funciona igual, solo con MySQL.

### 3. SINCRONIZACIÓN SIN DUPLICADOS:
* Al hacer clic en **"🔄 Sincronizar"** (la primera vez sube toda la base de MySQL a la nube):
  1. Envía los registros pendientes (`ventas`, `detalle_ventas`, `movimientos_stock`, `productos`, `clientes`, `proveedores`, `usuarios`) a PostgreSQL.
  2. **Sin duplicados**: cada registro tiene un `uuid` único. Si se repite la sincronización, PostgreSQL ignora los que ya existen.
  3. **Descarga de novedades**: trae a MySQL los cambios hechos desde otras computadoras.
  4. Al terminar, marca los registros como `sincronizado = 1`.
  5. **Si se corta la conexión**: se deshace la operación (`ROLLBACK`) y los datos quedan pendientes para el próximo intento.

### 4. DETECCIÓN DE CONFLICTOS:
* Si un producto o cliente se modificó en esta computadora y también en la nube:
  * El sistema **no sobreescribe a ciegas** ninguno de los dos.
  * Compara la `fecha_modificacion`.
  * Guarda el caso en la tabla `conflictos_sincronizacion`.
  * Avisa al usuario para que lo revise.

---

## 🔒 3. Configuración Segura de PostgreSQL (Nube / Servidor)

Las credenciales **nunca se guardan en el código fuente**. Se gestionan mediante:

### Opción A: Desde la Interfaz Gráfica (Recomendada)
1. Inicia el sistema y haz clic en el botón superior **"☁ Config Nube"**.
2. Completa los campos:
   * **Host:** Dirección del servidor (ej: `ep-xyz.us-east-2.aws.neon.tech` o `localhost`).
   * **Puerto:** `5432`
   * **Base de Datos:** Nombre de la base (ej: `techstore_db` o `neondb`).
   * **Usuario:** Usuario de PostgreSQL (ej: `postgres` o `neondb_owner`).
   * **Contraseña:** Contraseña segura (oculta con botón para visualizar).
   * **Modo SSL:** Selecciona `require` para servicios cloud (Neon, Supabase) o `prefer` para local.
3. Haz clic en **"🔍 Probar Conexión"** para verificar la comunicación.
4. Haz clic en **"💾 Guardar Parámetros"** (se almacenará en `config_db.json`, excluido automáticamente de Git).

### Opción B: Archivo de Configuración Local
Copia la plantilla `config_db.example.json` a `config_db.json` y edita los valores:
```json
{
    "pg_host": "ep-example.us-east-2.aws.neon.tech",
    "pg_port": 5432,
    "pg_database": "techstore_db",
    "pg_user": "postgres",
    "pg_password": "TU_PASSWORD_AQUI",
    "pg_sslmode": "require",
    "timeout_segundos": 4
}
```

### Opción C: Variables de Entorno del Sistema
Configura las variables estándar en Windows o en tu terminal:
```bash
set PG_HOST=ep-example.us-east-2.aws.neon.tech
set PG_PORT=5432
set PG_DATABASE=techstore_db
set PG_USER=postgres
set PG_PASSWORD=tu_password
set PG_SSLMODE=require
```

> **¿No tienes un servidor PostgreSQL todavía?**
> Puedes crear una base de datos PostgreSQL gratuita en la nube en menos de 2 minutos en servicios como **[Neon.tech](https://neon.tech)** o **[Supabase.com](https://supabase.com)** (ambos compatibles con SSL `require`). Si no configuras PostgreSQL, el sistema seguirá funcionando al 100% solo con **MySQL**.

---

## 🔑 4. Credenciales de Acceso al Sistema

Al iniciar por primera vez, el sistema crea automáticamente las cuentas de acceso:

* **Administrador:**
  * Usuario: `admin` | Contraseña: `admin123`
  * *Permisos:* Control total del sistema, configuración de usuarios, costos de compra y eliminación.
* **Vendedor:**
  * Usuario: `vendedor` | Contraseña: `ven123`
  * *Permisos:* Operación de ventas (POS), consulta de catálogo y clientes (precios de compra y eliminación bloqueados).

*(Las contraseñas se almacenan protegidas mediante hash criptográfico PBKDF2-HMAC-SHA256 con salt).*

---

## 📦 5. Generación del Ejecutable para Windows (.exe) con PyInstaller

Para compilar la aplicación en un archivo `.exe` independiente que funcione en cualquier computadora con Windows sin necesidad de instalar Python:

1. Asegúrate de tener las dependencias instaladas:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecuta el comando de compilación:
   ```bash
   pyinstaller --noconsole --onefile --name "TechStore_Sistema" main.py
   ```
   * `--noconsole`: Oculta la ventana de comandos negra de fondo para un acabado profesional.
   * `--onefile`: Empaqueta el intérprete de Python, Tkinter, ReportLab, openpyxl, psycopg2 y todos los módulos en un único archivo ejecutable.
   * `--name "TechStore_Sistema"`: Asigna el nombre al archivo ejecutable.
3. El archivo generado se ubicará en:
   ```
   dist/TechStore_Sistema.exe
   ```
4. Al hacer doble clic en `TechStore_Sistema.exe`, la aplicación se conecta a MySQL (XAMPP debe estar encendido) y, si está configurada, también a la nube.
