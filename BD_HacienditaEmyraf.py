import sqlite3
from tkinter import messagebox

def inicializar_base_datos(db_path):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        
        # Crear tabla EVENTOS si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EVENTOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE_CLIENTE TEXT NOT NULL,
                FECHA_EVENTO TEXT NOT NULL,
                ESTADO_PAGO TEXT,
                MONTO_TOTAL REAL,
                MONTO_PAGADO REAL,
                CANTIDAD_PERSONAS INTEGER,
                ESTADO_AUTORIZACION TEXT DEFAULT 'PENDIENTE',
                AUTORIZADO_POR TEXT,
                FECHA_AUTORIZACION TEXT,
                MANTEL TEXT,
                CUBREMANTEL TEXT
            )
        ''')
        
        # Crear tabla PAGOS si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS PAGOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                EVENTO_ID INTEGER,
                MONTO REAL,
                TIPO_PAGO TEXT,
                FORMA_PAGO TEXT,
                FECHA_PAGO TEXT,
                FOREIGN KEY (EVENTO_ID) REFERENCES EVENTOS (ID)
            )
        ''')
        
        # Crear tabla MANTELES si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MANTELES (
                CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE TEXT,
                PRECIO REAL
            )
        ''')
        
        # Crear tabla CUBREMANTELES si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CUBREMANTELES (
                CODIGO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE TEXT,
                PRECIO REAL
            )
        ''')
        
        # Insertar datos de ejemplo si las tablas están vacías
        cursor.execute("SELECT COUNT(*) FROM MANTELES")
        if cursor.fetchone()[0] == 0:
            manteles = [
                ('Mantel Blanco', 100),
                ('Mantel Verde', 100),
                ('Mantel Azul', 100),
                ('Mantel Rojo', 100),
                ('Mantel Negro', 200)
            ]
            cursor.executemany('INSERT INTO MANTELES (NOMBRE, PRECIO) VALUES (?, ?)', manteles)
        
        cursor.execute("SELECT COUNT(*) FROM CUBREMANTELES")
        if cursor.fetchone()[0] == 0:
            cubremanteles = [
                ('CubreMantel Blanco', 100),
                ('CubreMantel Verde', 100),
                ('CubreMantel Azul', 100),
                ('CubreMantel Rojo', 100),
                ('CubreMantel Amarillo', 100)
            ]
            cursor.executemany('INSERT INTO CUBREMANTELES (NOMBRE, PRECIO) VALUES (?, ?)', cubremanteles)
        
        # Insertar algunos eventos de ejemplo si la tabla está vacía
        cursor.execute("SELECT COUNT(*) FROM EVENTOS")
        if cursor.fetchone()[0] == 0:
            eventos = [
                ('Juan Pérez', '2024-03-15', 'ANTICIPO', 5000, 1500, 100, 'PENDIENTE', None, None, 'Mantel Blanco', 'CubreMantel Verde'),
                ('María García', '2024-04-20', 'PAGADO', 6000, 6000, 120, 'AUTORIZADO', 'SECRETARIA', '2024-02-01', 'Mantel Negro', 'CubreMantel Rojo'),
                ('Carlos López', '2024-05-10', 'ABONO', 4500, 2000, 80, 'PENDIENTE', None, None, 'Mantel Azul', 'CubreMantel Blanco')
            ]
            cursor.executemany('''
                INSERT INTO EVENTOS (
                    NOMBRE_CLIENTE, FECHA_EVENTO, ESTADO_PAGO,
                    MONTO_TOTAL, MONTO_PAGADO, CANTIDAD_PERSONAS,
                    ESTADO_AUTORIZACION, AUTORIZADO_POR, FECHA_AUTORIZACION,
                    MANTEL, CUBREMANTEL
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', eventos)
        
        conexion.commit()
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        messagebox.showerror("Error", f"Error al inicializar la base de datos: {e}")
    finally:
        conexion.close()

def obtener_manteles(db_path):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT NOMBRE FROM MANTELES ORDER BY NOMBRE")
        manteles = [row[0] for row in cursor.fetchall()]
        return manteles
    except Exception as e:
        print(f"Error al obtener manteles: {e}")
        return []
    finally:
        conexion.close()

def obtener_cubremanteles(db_path):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT NOMBRE FROM CUBREMANTELES ORDER BY NOMBRE")
        cubremanteles = [row[0] for row in cursor.fetchall()]
        return cubremanteles
    except Exception as e:
        print(f"Error al obtener cubremanteles: {e}")
        return []
    finally:
        conexion.close()

def obtener_precio_mantel(db_path, nombre_mantel):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT PRECIO FROM MANTELES WHERE NOMBRE = ?", (nombre_mantel,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0
    except Exception as e:
        print(f"Error al obtener precio del mantel: {e}")
        return 0
    finally:
        conexion.close()

def obtener_precio_cubremantel(db_path, nombre_cubremantel):
    try:
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()
        cursor.execute("SELECT PRECIO FROM CUBREMANTELES WHERE NOMBRE = ?", (nombre_cubremantel,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0
    except Exception as e:
        print(f"Error al obtener precio del cubremantel: {e}")
        return 0
    finally:
        conexion.close()
