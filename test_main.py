import unittest
import tkinter as tk
import sys
import os

# Agregar el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ReservaApp.main import SistemaReservas, ReservaApp, GestionAutorizaciones
import sqlite3
from datetime import datetime, timedelta

def crear_base_datos_prueba():
    """Crea una base de datos de prueba con la estructura necesaria"""
    db_path = 'test_BD_HacienditaEmyraf.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla EVENTOS
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
            FECHA_AUTORIZACION TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    return db_path

class TestSistemaReservas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = crear_base_datos_prueba()

    def setUp(self):
        self.root = tk.Tk()
        self.sistema = SistemaReservas(self.root)
        self.sistema.db_path = self.test_db

    def tearDown(self):
        self.root.destroy()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_calculos_y_disponibilidad(self):
        """Prueba los cálculos de totales y verificación de disponibilidad"""
        # Prueba 1: Cálculo en temporada alta
        self.sistema.mesas_reservadas.set(5)
        self.sistema.incluye_vajilla.set(True)
        self.sistema.incluye_cristaleria.set(True)
        self.sistema.permiso_alcoholes.set(True)
        self.sistema.meseros.set(2)
        self.sistema.fecha_reserva.set("2024-12-15")
        
        total = self.sistema.calcular_total()
        self.assertEqual(total, 10100)  # 3500 + 2500 + 1000 + 800 + 1500 + 800

        # Prueba 2: Cálculo en temporada baja
        self.sistema.mesas_reservadas.set(3)
        self.sistema.incluye_vajilla.set(False)
        self.sistema.incluye_cristaleria.set(False)
        self.sistema.permiso_alcoholes.set(False)
        self.sistema.meseros.set(1)
        self.sistema.fecha_reserva.set("2024-03-15")
        
        total = self.sistema.calcular_total()
        self.assertEqual(total, 4400)  # 2500 + 1500 + 400

        # Prueba 3: Verificación de disponibilidad
        self.sistema.nombre_cliente.set("Cliente Test")
        self.sistema.monto_pagado.set(5000)
        fecha_prueba = "2024-06-15"
        self.sistema.fecha_reserva.set(fecha_prueba)
        
        # Verificar fecha libre
        self.assertTrue(self.sistema.verificar_disponibilidad())
        
        # Insertar evento y verificar fecha ocupada
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO EVENTOS (NOMBRE_CLIENTE, FECHA_EVENTO, ESTADO_PAGO, 
                               MONTO_TOTAL, MONTO_PAGADO, CANTIDAD_PERSONAS)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Cliente Existente", fecha_prueba, "ANTICIPO", 10000, 3000, 50))
        conn.commit()
        conn.close()
        
        self.assertFalse(self.sistema.verificar_disponibilidad())

class TestReservaApp(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = ReservaApp(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_login(self):
        """Prueba las diferentes opciones de login"""
        # Login como admin
        self.app.username_entry.insert(0, "admin")
        self.app.password_entry.insert(0, "1234")
        self.app.verify_login()
        
        # Login como secretaria
        self.app.username_entry.delete(0, tk.END)
        self.app.password_entry.delete(0, tk.END)
        self.app.username_entry.insert(0, "secretaria")
        self.app.password_entry.insert(0, "5678")
        self.app.verify_login()
        
        # Login fallido
        self.app.username_entry.delete(0, tk.END)
        self.app.password_entry.delete(0, tk.END)
        self.app.username_entry.insert(0, "usuario_incorrecto")
        self.app.password_entry.insert(0, "contraseña_incorrecta")
        self.app.verify_login()

class TestGestionAutorizaciones(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = crear_base_datos_prueba()

    def setUp(self):
        self.root = tk.Tk()
        self.gestion = GestionAutorizaciones(self.root)
        self.gestion.db_path = self.test_db

    def tearDown(self):
        self.root.destroy()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_gestion_eventos(self):
        """Prueba la gestión de eventos (autorización y rechazo)"""
        # Insertar evento de prueba
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO EVENTOS (NOMBRE_CLIENTE, FECHA_EVENTO, ESTADO_PAGO, 
                               MONTO_TOTAL, MONTO_PAGADO, CANTIDAD_PERSONAS)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ("Cliente Test", "2024-07-15", "ANTICIPO", 10000, 5000, 50))
        conn.commit()
        conn.close()

        # Simular selección y autorización
        self.gestion.tabla_eventos.insert("", "end", values=(1, "Cliente Test", "2024-07-15", 10000, 5000, "PENDIENTE"))
        self.gestion.tabla_eventos.selection_set(self.gestion.tabla_eventos.get_children()[0])
        self.gestion.autorizar_evento()

        # Verificar autorización
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT ESTADO_AUTORIZACION FROM EVENTOS WHERE ID = 1')
        estado = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(estado, "AUTORIZADO")

if __name__ == '__main__':
    unittest.main() 