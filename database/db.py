"""
Módulo de conexión a la base de datos MySQL / MariaDB local.

La base de datos se administra con phpMyAdmin (por ejemplo, con XAMPP o WAMP):
    http://localhost/phpmyadmin  ->  base de datos "techstore_db"

Los datos de conexión se leen del archivo "config_mysql.json" que está en la
raíz del proyecto. Si no existe, se crea automáticamente con los valores por
defecto de XAMPP (usuario "root" sin contraseña, puerto 3306).

Para no tener que reescribir todas las consultas del sistema, la conexión
devuelta acepta los marcadores "?" (estilo SQLite) y los convierte a "%s"
(estilo MySQL) de forma automática. También permite leer las filas por nombre
de columna (fila["nombre"]) o por posición (fila[0]), igual que antes.
"""
import os
import json
import datetime
from decimal import Decimal

import pymysql

CONFIG_FILENAME = "config_mysql.json"

CONFIG_POR_DEFECTO = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "techstore_db"
}


# ----------------------------------------------------------------------------
# Configuración
# ----------------------------------------------------------------------------
def get_config_path():
    """Ruta absoluta del archivo de configuración MySQL en la raíz del proyecto."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, CONFIG_FILENAME)


def obtener_configuracion_mysql():
    """Lee config_mysql.json. Si no existe, lo crea con los valores de XAMPP."""
    ruta = get_config_path()
    if not os.path.exists(ruta):
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(CONFIG_POR_DEFECTO, f, indent=4)
        except Exception:
            pass
        return dict(CONFIG_POR_DEFECTO)

    try:
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
    except Exception:
        datos = {}
    config = dict(CONFIG_POR_DEFECTO)
    config.update({k: v for k, v in datos.items() if k in CONFIG_POR_DEFECTO})
    config["port"] = int(config.get("port") or 3306)
    return config


# ----------------------------------------------------------------------------
# Adaptadores: hacen que MySQL se use igual que antes se usaba SQLite
# ----------------------------------------------------------------------------
def _convertir_valor(valor):
    """Convierte tipos propios de MySQL a tipos simples de Python."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, datetime.datetime):
        return valor.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(valor, datetime.date):
        return valor.strftime("%Y-%m-%d")
    if isinstance(valor, (bytes, bytearray)):
        try:
            return valor.decode("utf-8")
        except Exception:
            return valor
    return valor


class Fila:
    """Fila que se puede leer por posición (fila[0]) o por nombre (fila['id'])."""
    __slots__ = ("_columnas", "_valores", "_indice")

    def __init__(self, columnas, valores):
        self._columnas = columnas
        self._valores = tuple(_convertir_valor(v) for v in valores)
        self._indice = {c: i for i, c in enumerate(columnas)}

    def __getitem__(self, clave):
        if isinstance(clave, (int, slice)):
            return self._valores[clave]
        return self._valores[self._indice[clave]]

    def keys(self):
        return list(self._columnas)

    def get(self, clave, defecto=None):
        i = self._indice.get(clave)
        return defecto if i is None else self._valores[i]

    def __iter__(self):
        return iter(self._valores)

    def __len__(self):
        return len(self._valores)

    def __repr__(self):
        return "Fila(" + ", ".join(f"{c}={v!r}" for c, v in zip(self._columnas, self._valores)) + ")"


def _adaptar_sql(sql, hay_parametros):
    """
    Traduce detalles de sintaxis SQLite a MySQL:
      - Marcadores "?" -> "%s" (solo fuera de textos entre comillas)
      - datetime('now', 'localtime') -> NOW()
      - DATE('now', 'localtime')     -> CURDATE()
    """
    reemplazos = [
        ("datetime('now', 'localtime')", "NOW()"),
        ("datetime('now','localtime')", "NOW()"),
        ("DATE('now', 'localtime')", "CURDATE()"),
        ("DATE('now','localtime')", "CURDATE()"),
        ("date('now', 'localtime')", "CURDATE()"),
    ]
    for viejo, nuevo in reemplazos:
        sql = sql.replace(viejo, nuevo)

    if not hay_parametros:
        return sql

    resultado = []
    comilla = None
    for ch in sql:
        if comilla:
            if ch == "%":
                resultado.append("%%")
                continue
            if ch == comilla:
                comilla = None
            resultado.append(ch)
        else:
            if ch in ("'", '"'):
                comilla = ch
                resultado.append(ch)
            elif ch == "?":
                resultado.append("%s")
            elif ch == "%":
                resultado.append("%%")
            else:
                resultado.append(ch)
    return "".join(resultado)


class CursorMySQL:
    """Cursor que acepta consultas escritas con '?' y devuelve objetos Fila."""

    def __init__(self, cursor_real):
        self._cur = cursor_real

    def execute(self, sql, parametros=None):
        if parametros is not None and not isinstance(parametros, (list, tuple, dict)):
            parametros = (parametros,)
        hay = bool(parametros)
        self._cur.execute(_adaptar_sql(sql, hay), parametros if hay else None)
        return self

    def executemany(self, sql, lista_parametros):
        self._cur.executemany(_adaptar_sql(sql, True), lista_parametros)
        return self

    def _columnas(self):
        return [d[0] for d in (self._cur.description or [])]

    def fetchone(self):
        fila = self._cur.fetchone()
        return Fila(self._columnas(), fila) if fila is not None else None

    def fetchall(self):
        cols = self._columnas()
        return [Fila(cols, f) for f in self._cur.fetchall()]

    def fetchmany(self, size=1):
        cols = self._columnas()
        return [Fila(cols, f) for f in self._cur.fetchmany(size)]

    def __iter__(self):
        return iter(self.fetchall())

    @property
    def lastrowid(self):
        return self._cur.lastrowid

    @property
    def rowcount(self):
        return self._cur.rowcount

    @property
    def description(self):
        return self._cur.description

    def close(self):
        self._cur.close()


class ConexionMySQL:
    """Conexión con la misma forma de uso que tenía la conexión SQLite."""

    def __init__(self, conexion_real):
        self._conn = conexion_real
        self.row_factory = None  # Se mantiene solo por compatibilidad

    def cursor(self):
        return CursorMySQL(self._conn.cursor())

    def execute(self, sql, parametros=None):
        cur = self.cursor()
        cur.execute(sql, parametros)
        return cur

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, tipo, valor, traza):
        if tipo is None:
            self.commit()
        else:
            self.rollback()
        return False


# ----------------------------------------------------------------------------
# Funciones públicas
# ----------------------------------------------------------------------------
def crear_base_si_no_existe():
    """Crea la base de datos (por ejemplo 'techstore_db') si todavía no existe."""
    cfg = obtener_configuracion_mysql()
    conn = pymysql.connect(
        host=cfg["host"], port=cfg["port"], user=cfg["user"], password=cfg["password"],
        charset="utf8mb4", connect_timeout=5
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{cfg['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
    finally:
        conn.close()


def get_connection():
    """Crea y retorna una conexión a la base de datos MySQL configurada."""
    cfg = obtener_configuracion_mysql()
    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        charset="utf8mb4",
        autocommit=False,
        connect_timeout=5
    )
    with conn.cursor() as cur:
        # Hora local de la PC y modo compatible con las consultas del sistema
        cur.execute("SET time_zone = %s;", (_zona_horaria_local(),))
        cur.execute("SET SESSION sql_mode = REPLACE(@@sql_mode, 'ONLY_FULL_GROUP_BY', '');")
    return ConexionMySQL(conn)


def probar_conexion_mysql():
    """Devuelve (True, mensaje) si MySQL responde, o (False, mensaje de error)."""
    try:
        crear_base_si_no_existe()
        conn = get_connection()
        conn.close()
        return True, "Conexión exitosa a MySQL."
    except Exception as e:
        return False, str(e)


def _zona_horaria_local():
    """Calcula el desfase horario de la PC (ej: Perú = '-05:00')."""
    desfase = datetime.datetime.now() - datetime.datetime.utcnow()
    minutos = round(desfase.total_seconds() / 60)
    signo = "+" if minutos >= 0 else "-"
    minutos = abs(minutos)
    return f"{signo}{minutos // 60:02d}:{minutos % 60:02d}"
