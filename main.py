import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import os
import sys
import sqlite3
from BD_HacienditaEmyraf import (inicializar_base_datos, obtener_manteles, 
                                obtener_cubremanteles, obtener_precio_mantel, 
                                obtener_precio_cubremantel)


class SistemaReservas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas - Haciendita Emyraf")
        # Configurar tamaño de ventana
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        # Dejar espacio para la barra de tareas (aproximadamente 40 píxeles)
        ancho_ventana = ancho_pantalla - 40
        alto_ventana = alto_pantalla - 100
        x = 20  # Margen izquierdo
        y = 20  # Margen superior
        root.geometry(f'{ancho_ventana}x{alto_ventana}+{x}+{y}')
        # Configurar el estilo
        self.configurar_estilo()
        
        # Configuración de variables
        self.fecha_reserva = tk.StringVar()
        self.mesas_reservadas = tk.IntVar(value=1)
        self.incluye_vajilla = tk.BooleanVar()
        self.incluye_cristaleria = tk.BooleanVar()
        self.permiso_alcoholes = tk.BooleanVar()
        self.meseros = tk.IntVar(value=0)
        self.nombre_cliente = tk.StringVar()
        self.cantidad_personas = tk.IntVar(value=50)
        self.monto_pagado = tk.DoubleVar(value=0.0)
        self.mantel_seleccionado = tk.StringVar()
        self.cubremantel_seleccionado = tk.StringVar()
        
        # Inicializar la base de datos
        self.db_path = 'test_BD_HacienditaEmyraf.db'
        inicializar_base_datos(self.db_path)
        
        self.crear_interfaz()

    def configurar_estilo(self):
        # Configurar el estilo de ttk
        style = ttk.Style()
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TCheckbutton", background="white", font=("Arial", 10))
        style.configure("TSpinbox", font=("Arial", 10))
        style.configure("TFrame", background="white")
        
        # Configurar el fondo de la ventana principal
        self.root.configure(bg="white")

    def crear_interfaz(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configurar logo al inicio
        self.configurar_logo()
            
        # Frame principal con fondo blanco
        frame_principal = ttk.Frame(self.root, style="TFrame")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
            
        # Calendario para seleccionar fecha
        ttk.Label(frame_principal, text="Seleccione la fecha del evento:", 
                 style="TLabel").pack(pady=10)
        self.calendario = Calendar(frame_principal, 
                                 date_pattern="dd/mm/yyyy",
                                 background="white", 
                                 foreground="black",
                                 selectbackground="lightblue",
                                 locale='es_ES',
                                 firstweekday='monday')
        self.calendario.pack(pady=10)

        # Frame para los campos
        frame_campos = ttk.Frame(frame_principal, style="TFrame")
        frame_campos.pack(pady=10)

        # Selección de mesas
        ttk.Label(frame_campos, text="Número de mesas a reservar (Máximo 15, cada mesa tiene el valor de $500):",
                 style="TLabel").pack(pady=5)
        ttk.Spinbox(frame_campos, from_=1, to=15, textvariable=self.mesas_reservadas, 
                   width=10, style="TSpinbox").pack(pady=5)

        # Opciones de vajilla y cristalería
        ttk.Checkbutton(frame_campos, text="Incluir plato base y plato ($1000)", 
                       variable=self.incluye_vajilla, style="TCheckbutton").pack(pady=5)
        ttk.Checkbutton(frame_campos, text="Incluir cristalería ($800)", 
                       variable=self.incluye_cristaleria, style="TCheckbutton").pack(pady=5)

        # Extras
        ttk.Checkbutton(frame_campos, text="Permiso de alcoholes ($1500)", 
                       variable=self.permiso_alcoholes, style="TCheckbutton").pack(pady=5)
        ttk.Label(frame_campos, text="Número de meseros ($400 cada uno):",
                 style="TLabel").pack(pady=5)
        ttk.Spinbox(frame_campos, from_=0, to=10, textvariable=self.meseros, 
                   width=10, style="TSpinbox").pack(pady=5)

        # Frame para botones
        frame_botones = ttk.Frame(frame_principal, style="TFrame")
        frame_botones.pack(pady=20)

        # Botón para calcular y reservar
        ttk.Button(frame_botones, text="Calcular y Reservar", 
                  command=self.calcular_reserva, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Cerrar Sesión", 
                  command=self.cerrar_sesion, style="TButton").pack(side="left", padx=5)

    def cargar_manteles(self):
        manteles = obtener_manteles(self.db_path)
        self.combo_mantel['values'] = manteles
        if manteles:
            self.combo_mantel.set(manteles[0])

    def cargar_cubremanteles(self):
        cubremanteles = obtener_cubremanteles(self.db_path)
        self.combo_cubremantel['values'] = cubremanteles
        if cubremanteles:
            self.combo_cubremantel.set(cubremanteles[0])

    def calcular_reserva(self):
        # Obtener fecha
        fecha = self.calendario.get_date()
        # Convertir fecha de dd/mm/yyyy a yyyy-mm-dd para procesamiento
        dia, mes, anio = fecha.split('/')
        fecha_procesada = f"{anio}-{mes}-{dia}"

        # Calcular precio base según la temporada
        mes = int(mes)
        if mes in [12, 1, 2]:
            precio_base = 3500
        else:
            precio_base = 2500

        # Calcular costos adicionales
        costo_mesas = self.mesas_reservadas.get() * 500
        costo_vajilla = 1000 if self.incluye_vajilla.get() else 0
        costo_cristaleria = 800 if self.incluye_cristaleria.get() else 0
        costo_alcoholes = 1500 if self.permiso_alcoholes.get() else 0
        costo_meseros = self.meseros.get() * 400

        # Total
        total = precio_base + costo_mesas + costo_vajilla + costo_cristaleria + costo_alcoholes + costo_meseros

        # Mostrar confirmación
        resumen = (
            f"Fecha del evento: {fecha}\n"
            f"Mesas reservadas: {self.mesas_reservadas.get()}\n"
            f"Incluye vajilla: {'Sí' if self.incluye_vajilla.get() else 'No'}\n"
            f"Incluye cristalería: {'Sí' if self.incluye_cristaleria.get() else 'No'}\n"
            f"Permiso de alcoholes: {'Sí' if self.permiso_alcoholes.get() else 'No'}\n"
            f"Meseros contratados: {self.meseros.get()}\n"
            f"Precio total: ${total}"
        )

        messagebox.showinfo("Resumen de la Reserva", resumen)
        self.crear_apartado_eventos()

    def crear_apartado_eventos(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Configurar logo al inicio
        self.configurar_logo()
        
        # Frame principal con fondo blanco
        frame_principal = ttk.Frame(self.root, style="TFrame")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sección de información del cliente
        titulo = tk.Label(frame_principal, text="Apartar Evento", 
                         font=("Arial", 14, "bold"), bg="white", fg="black")
        titulo.pack(pady=10)
        
        # Frame para los campos de entrada
        frame_campos = ttk.Frame(frame_principal, style="TFrame")
        frame_campos.pack(pady=10)
        
        # Nombre del cliente
        ttk.Label(frame_campos, text="Nombre del Cliente:", 
                 style="TLabel").pack()
        self.entry_nombre = ttk.Entry(frame_campos, textvariable=self.nombre_cliente, 
                                    width=30, style="TEntry")
        self.entry_nombre.pack(pady=5)
        
        # Mostrar la fecha seleccionada (no editable)
        ttk.Label(frame_campos, text="Fecha del Evento:", 
                 style="TLabel").pack()
        fecha_label = ttk.Label(frame_campos, text=self.calendario.get_date(),
                              style="TLabel")
        fecha_label.pack(pady=5)
        
        # Cantidad de personas
        ttk.Label(frame_campos, text="Cantidad de Personas:", 
                 style="TLabel").pack()
        ttk.Spinbox(frame_campos, from_=50, to=200, 
                   textvariable=self.cantidad_personas, style="TSpinbox").pack(pady=5)
        
        # Selección de mantel
        ttk.Label(frame_campos, text="Seleccione el mantel:", 
                 style="TLabel").pack(pady=5)
        self.combo_mantel = ttk.Combobox(frame_campos, textvariable=self.mantel_seleccionado, 
                                       state="readonly", width=30)
        self.cargar_manteles()
        self.combo_mantel.pack(pady=5)

        # Selección de cubremantel
        ttk.Label(frame_campos, text="Seleccione el cubremantel:", 
                 style="TLabel").pack(pady=5)
        self.combo_cubremantel = ttk.Combobox(frame_campos, textvariable=self.cubremantel_seleccionado, 
                                            state="readonly", width=30)
        self.cargar_cubremanteles()
        self.combo_cubremantel.pack(pady=5)
        
        # Monto de anticipo
        ttk.Label(frame_campos, text="Monto de Anticipo ($):", 
                 style="TLabel").pack()
        ttk.Entry(frame_campos, textvariable=self.monto_pagado, 
                 style="TEntry").pack(pady=5)
        
        # Frame para botones
        frame_botones = ttk.Frame(frame_principal, style="TFrame")
        frame_botones.pack(pady=10)
        
        # Botones
        ttk.Button(frame_botones, text="Verificar Disponibilidad", 
                  command=self.verificar_disponibilidad, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Regresar", 
                  command=self.crear_interfaz, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Cerrar Sesión", 
                  command=self.cerrar_sesion, style="TButton").pack(side="left", padx=5)

    def verificar_disponibilidad(self):
        fecha_seleccionada = self.calendario.get_date()
        # Convertir fecha de dd/mm/yyyy a yyyy-mm-dd para la base de datos
        dia, mes, anio = fecha_seleccionada.split('/')
        fecha_procesada = f"{anio}-{mes}-{dia}"
        
        nombre = self.nombre_cliente.get()
        anticipo = self.monto_pagado.get()
        
        if not nombre:
            messagebox.showerror("Error", "Por favor ingrese el nombre del cliente")
            return False
            
        if anticipo <= 0:
            messagebox.showerror("Error", "Debe realizar un anticipo para apartar la fecha")
            return False
            
        # Verificar disponibilidad en la base de datos
        try:
            conexion = sqlite3.connect(self.db_path)
            cursor = conexion.cursor()
            
            cursor.execute('''SELECT COUNT(*) FROM EVENTOS WHERE FECHA_EVENTO = ?''', 
                          (fecha_procesada,))
            
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showerror("Error", "Esta fecha ya está reservada")
                return False
            
            # Calcular el total
            total = self.calcular_total()
            
            # Verificar anticipo mínimo
            if anticipo < (total * 0.30):
                messagebox.showerror("Error", 
                    f"El anticipo mínimo debe ser del 30% del total (${total * 0.30:.2f})")
                return False
            
            # Guardar la reserva
            cursor.execute('''
                INSERT INTO EVENTOS (
                    NOMBRE_CLIENTE, FECHA_EVENTO, ESTADO_PAGO,
                    MONTO_TOTAL, MONTO_PAGADO, CANTIDAD_PERSONAS,
                    MANTEL, CUBREMANTEL
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre, fecha_procesada, "ANTICIPO",
                total, anticipo, self.cantidad_personas.get(),
                self.mantel_seleccionado.get(), self.cubremantel_seleccionado.get()
            ))
            evento_id = cursor.lastrowid
            # Insertar la cantidad de meseros en la tabla MESEROS
            cursor.execute('''
                INSERT INTO MESEROS (EVENTO_ID, CANTIDAD) VALUES (?, ?)
            ''', (evento_id, self.meseros.get()))
            
            conexion.commit()
            messagebox.showinfo("Éxito", "Reserva realizada con éxito")
            self.crear_interfaz()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar disponibilidad: {e}")
            return False
        finally:
            conexion.close()

    def calcular_total(self):
        # Obtener fecha
        fecha = self.calendario.get_date()
        # Convertir fecha de dd/mm/yyyy a yyyy-mm-dd para procesamiento
        dia, mes, anio = fecha.split('/')
        mes = int(mes)

        # Calcular precio base según la temporada
        if mes in [12, 1, 2]:
            precio_base = 3500  # Temporada alta
        else:
            precio_base = 2500  # Temporada baja

        # Calcular costos adicionales
        costo_mesas = self.mesas_reservadas.get() * 500  # $500 por mesa
        costo_vajilla = 1000 if self.incluye_vajilla.get() else 0  # $1000 si incluye vajilla
        costo_cristaleria = 800 if self.incluye_cristaleria.get() else 0  # $800 si incluye cristalería
        costo_alcoholes = 1500 if self.permiso_alcoholes.get() else 0  # $1500 por permiso de alcoholes
        costo_meseros = self.meseros.get() * 400  # $400 por mesero

        # Obtener costo de mantel y cubremantel
        costo_mantel = obtener_precio_mantel(self.db_path, self.mantel_seleccionado.get())
        costo_cubremantel = obtener_precio_cubremantel(self.db_path, self.cubremantel_seleccionado.get())

        # Total base
        total = (precio_base + costo_mesas + costo_vajilla + costo_cristaleria + 
                costo_alcoholes + costo_meseros + costo_mantel + costo_cubremantel)
        
        # Aplicar recargo por temporada alta (solo si es temporada alta)
        if mes in [12, 1, 2]:
            total += 1000  # Recargo adicional por temporada alta
            
        return total

    def cerrar_sesion(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Restaurar tamaño original de la ventana
        self.root.geometry("450x450")
        login = ReservaApp(self.root)

    def configurar_logo(self):
        try:
            # Ruta del logo (ajusta esta ruta según la ubicación de tu imagen)
            ruta_logo = "ReservaApp/haciendo_logo.png"  # Ruta corregida

            # Verificar si el archivo existe
            if not os.path.exists(ruta_logo):
                print(f"Advertencia: No se encontró el archivo {ruta_logo}")
                return

            # Abrir la imagen con PIL
            imagen = Image.open(ruta_logo)

            # Redimensionar la imagen (opcional)
            # Ajusta el tamaño según tus necesidades
            imagen_redimensionada = imagen.resize((100, 100), Image.LANCZOS)

            # Convertir la imagen para Tkinter
            self.logo = ImageTk.PhotoImage(imagen_redimensionada)
            # Crear una etiqueta con el logo y fondo blanco
            logo_label = tk.Label(self.root, image=self.logo, bg="white")
            logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")

class ReservaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas - Haciendita Emyraf")
        # Definir el tamaño de la ventana
        ancho_ventana = 450
        alto_ventana = 450

        # Calcular la posición para centrar la ventana
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2

        # Establecer la geometría de la ventana y hacerla no redimensionable
        root.geometry(f'{ancho_ventana}x{alto_ventana}+{x}+{y}')
        root.resizable(False, False)  # No permitir redimensionar
        
        # Configurar el estilo y fondo
        self.configurar_estilo()
        self.configurar_icono_taskbar()
        self.configurar_icono()
        self.create_login_screen()

    def configurar_estilo(self):
        # Configurar el estilo de ttk
        style = ttk.Style()
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))
        style.configure("TFrame", background="white")
        
        # Configurar el fondo de la ventana principal
        self.root.configure(bg="white")

    def configurar_logo(self):
        try:
            # Ruta del logo (ajusta esta ruta según la ubicación de tu imagen)
            ruta_logo = "ReservaApp/haciendo_logo.png"  # Ruta corregida

            # Verificar si el archivo existe
            if not os.path.exists(ruta_logo):
                print(f"Advertencia: No se encontró el archivo {ruta_logo}")
                return

            # Abrir la imagen con PIL
            imagen = Image.open(ruta_logo)

            # Redimensionar la imagen (opcional)
            # Ajusta el tamaño según tus necesidades
            imagen_redimensionada = imagen.resize((100, 100), Image.LANCZOS)

            # Convertir la imagen para Tkinter
            self.logo = ImageTk.PhotoImage(imagen_redimensionada)
            # Crear una etiqueta con el logo y fondo blanco
            logo_label = tk.Label(self.root, image=self.logo, bg="white")
            logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Frame principal con fondo blanco
        frame_principal = ttk.Frame(self.root, style="TFrame")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.configurar_logo()

        # Título con fondo blanco
        titulo = tk.Label(frame_principal, text="Inicio de Sesión", 
                         font=("Arial", 14, "bold"), bg="white", fg="black")
        titulo.pack(pady=10)
        
        # Frame para los campos de entrada
        frame_campos = ttk.Frame(frame_principal, style="TFrame")
        frame_campos.pack(pady=10)
        
        # Usuario
        ttk.Label(frame_campos, text="Usuario:", style="TLabel").pack()
        self.username_entry = ttk.Entry(frame_campos, style="TEntry")
        self.username_entry.pack(pady=5)
        
        # Contraseña
        ttk.Label(frame_campos, text="Contraseña:", style="TLabel").pack()
        self.password_entry = ttk.Entry(frame_campos, show="*", style="TEntry")
        self.password_entry.pack(pady=5)
        
        # Frame para botones
        frame_botones = ttk.Frame(frame_principal, style="TFrame")
        frame_botones.pack(pady=10)
        
        # Botón de ingreso
        ttk.Button(frame_botones, text="Ingresar", 
                  command=self.verify_login, style="TButton").pack(pady=10)

    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == "admin" and password == "123":
            for widget in self.root.winfo_children():
                widget.destroy()
            sistema = SistemaReservas(self.root)
            sistema.db_path = 'test_BD_HacienditaEmyraf.db'  # Usar base de datos de prueba
        elif username == "secretaria" and password == "456":
            for widget in self.root.winfo_children():
                widget.destroy()
            gestion = GestionAutorizaciones(self.root)
            gestion.db_path = 'test_BD_HacienditaEmyraf.db'  # Usar base de datos de prueba
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def configurar_icono(self):
        try:
            # Rutas de ícono (prueba múltiples formatos)
            rutas_iconos = [
                "ReservaApp/icono_programadores.ico",      # Formato Windows
            ]

            # Intentar cargar el ícono
            for ruta in rutas_iconos:
                if os.path.exists(ruta):
                    # Para Windows y sistemas que usan .ico
                    if ruta.endswith('.ico'):
                        self.root.iconbitmap(ruta)
                        break
                    
                    # Para sistemas que usan PNG o XBM
                    imagen_icono = Image.open(ruta)
                    
                    # Redimensionar si es necesario (generalmente 16x16, 32x32 o 64x64)
                    imagen_icono = imagen_icono.resize((32, 32), Image.LANCZOS)
                    
                    # Convertir a PhotoImage
                    photo_icono = ImageTk.PhotoImage(imagen_icono)
                    
                    # Establecer ícono
                    self.root.iconphoto(True, photo_icono)
                    break
            else:
                print("No se encontró ningún ícono válido")

        except Exception as e:
            print(f"Error al cargar el ícono: {e}")

    def configurar_icono_taskbar(self):
        try:
            # Intentar cargar el ícono
            rutas_iconos = [
                "ReservaApp/icono_programadores.ico",
            ]

            for ruta in rutas_iconos:
                if os.path.exists(ruta):
                    # Para Windows
                    if sys.platform.startswith('win'):
                        # Método para Windows para establecer ícono de taskbar
                        self.root.iconbitmap(ruta)
                    
                    # Para otros sistemas (Linux, macOS)
                    else:
                        # Cargar imagen con PIL
                        imagen_icono = Image.open(ruta)
                        
                        # Redimensionar (tamaño típico para íconos de taskbar)
                        imagen_icono = imagen_icono.resize((256, 256), Image.LANCZOS)
                        
                        # Convertir a PhotoImage
                        photo_icono = ImageTk.PhotoImage(imagen_icono)
                        
                        # Establecer ícono para la ventana
                        self.root.iconphoto(True, photo_icono)
                    
                    break
            else:
                print("No se encontró ningún ícono para taskbar")

        except Exception as e:
            print(f"Error al configurar ícono de taskbar: {e}")

class GestionAutorizaciones:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Autorizaciones - Haciendita Emyraf")
        # Configurar tamaño de ventana
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        # Dejar espacio para la barra de tareas (aproximadamente 40 píxeles)
        ancho_ventana = ancho_pantalla - 40
        alto_ventana = alto_pantalla - 100
        x = 20  # Margen izquierdo
        y = 20  # Margen superior
        root.geometry(f'{ancho_ventana}x{alto_ventana}+{x}+{y}')
        self.db_path = 'test_BD_HacienditaEmyraf.db'
        # Inicializar la conexión a la base de datos
        self.conexion = sqlite3.connect(self.db_path)
        self.cursor = self.conexion.cursor()
        # Inicializar la base de datos
        self.inicializar_base_datos()
        # Configurar el estilo
        self.configurar_estilo()
        self.crear_interfaz_autorizaciones()
        
    def inicializar_base_datos(self):
        try:
            # Crear tabla EVENTOS si no existe
            self.cursor.execute('''
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
            self.cursor.execute('''
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
            
            self.conexion.commit()
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")

    def configurar_estilo(self):
        # Configurar el estilo de ttk
        style = ttk.Style()
        style.configure("TLabel", background="white", foreground="black", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Treeview", background="white", fieldbackground="white")
        style.configure("Treeview.Heading", background="white", foreground="black", font=("Arial", 10, "bold"))
        style.configure("TFrame", background="white")
        style.configure("TRadiobutton", background="white", font=("Arial", 10))
        
        # Configurar el fondo de la ventana principal
        self.root.configure(bg="white")
        
    def crear_interfaz_autorizaciones(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Configurar logo al inicio
        self.configurar_logo()
            
        # Frame principal con fondo blanco
        frame_principal = ttk.Frame(self.root, style="TFrame")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
            
        # Título
        titulo = tk.Label(frame_principal, text="Gestión de Autorizaciones", 
                font=("Arial", 14, "bold"), bg="white", fg="black")
        titulo.pack(pady=10)
        
        # Frame para la lista de eventos pendientes
        frame_eventos = ttk.Frame(frame_principal, style="TFrame")
        frame_eventos.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Crear Treeview para mostrar eventos pendientes
        self.tabla_eventos = ttk.Treeview(frame_eventos, columns=(
            "ID", "Cliente", "Fecha", "Monto_Total", "Monto_Pagado", "Estado"
        ), show="headings", style="Treeview")
        
        # Configurar columnas
        self.tabla_eventos.heading("ID", text="ID")
        self.tabla_eventos.heading("Cliente", text="Cliente")
        self.tabla_eventos.heading("Fecha", text="Fecha Evento")
        self.tabla_eventos.heading("Monto_Total", text="Total")
        self.tabla_eventos.heading("Monto_Pagado", text="Pagado")
        self.tabla_eventos.heading("Estado", text="Estado")
        
        # Configurar el ancho de las columnas
        self.tabla_eventos.column("ID", width=50)
        self.tabla_eventos.column("Cliente", width=150)
        self.tabla_eventos.column("Fecha", width=100)
        self.tabla_eventos.column("Monto_Total", width=100)
        self.tabla_eventos.column("Monto_Pagado", width=100)
        self.tabla_eventos.column("Estado", width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(frame_eventos, orient="vertical", 
                                command=self.tabla_eventos.yview)
        self.tabla_eventos.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar elementos
        self.tabla_eventos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para los botones con fondo blanco
        frame_botones = ttk.Frame(frame_principal, style="TFrame")
        frame_botones.pack(pady=10)
        
        # Botones con estilo mejorado
        ttk.Button(frame_botones, text="Ver Detalles del Evento", 
                  command=self.mostrar_detalles_evento, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Autorizar Evento", 
                  command=self.autorizar_evento, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Rechazar Evento", 
                  command=self.rechazar_evento, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Borrar Evento", 
                  command=self.borrar_evento, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Pagar Evento", 
                  command=self.pagar_evento, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Actualizar Lista", 
                  command=self.cargar_eventos_pendientes, style="TButton").pack(side="left", padx=5)
        ttk.Button(frame_botones, text="Cerrar Sesión", 
                  command=self.cerrar_sesion, style="TButton").pack(side="left", padx=5)
        
        # Cargar eventos pendientes
        self.cargar_eventos_pendientes()
        
    def cargar_eventos_pendientes(self):
        # Limpiar tabla
        for item in self.tabla_eventos.get_children():
            self.tabla_eventos.delete(item)
            
        try:
            self.cursor.execute('''
                SELECT ID, NOMBRE_CLIENTE, FECHA_EVENTO, MONTO_TOTAL, 
                       MONTO_PAGADO, ESTADO_AUTORIZACION 
                FROM EVENTOS 
                ORDER BY ID ASC
            ''')
            
            for evento in self.cursor.fetchall():
                # Convertir la fecha de yyyy-mm-dd a dd/mm/yyyy
                fecha_original = evento[2]
                anio, mes, dia = fecha_original.split('-')
                fecha_formateada = f"{dia}/{mes}/{anio}"
                
                # Crear una nueva tupla con la fecha formateada
                evento_formateado = (
                    evento[0],  # ID
                    evento[1],  # NOMBRE_CLIENTE
                    fecha_formateada,  # FECHA_EVENTO formateada
                    evento[3],  # MONTO_TOTAL
                    evento[4],  # MONTO_PAGADO
                    evento[5]   # ESTADO_AUTORIZACION
                )
                
                self.tabla_eventos.insert("", "end", values=evento_formateado)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar eventos: {str(e)}")
            
    def autorizar_evento(self):
        seleccion = self.tabla_eventos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un evento")
            return
            
        evento_id = self.tabla_eventos.item(seleccion[0])['values'][0]
        
        try:
            # Verificar pago mínimo
            self.cursor.execute('''
                SELECT MONTO_TOTAL, MONTO_PAGADO 
                FROM EVENTOS 
                WHERE ID = ?
            ''', (evento_id,))
            
            total, pagado = self.cursor.fetchone()
            if pagado < (total * 0.30):
                messagebox.showwarning(
                    "Advertencia", 
                    "No se puede autorizar: Pago mínimo no cumplido (30%)"
                )
                return
            
            # Actualizar estado
            self.cursor.execute('''
                UPDATE EVENTOS 
                SET ESTADO_AUTORIZACION = 'AUTORIZADO',
                    AUTORIZADO_POR = ?,
                    FECHA_AUTORIZACION = DATETIME('now', 'localtime')
                WHERE ID = ?
            ''', ("SECRETARIA", evento_id))
            
            self.conexion.commit()
            messagebox.showinfo("Éxito", "Evento autorizado correctamente")
            self.cargar_eventos_pendientes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al autorizar evento: {str(e)}")
            
    def rechazar_evento(self):
        seleccion = self.tabla_eventos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un evento")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de rechazar este evento?"):
            evento_id = self.tabla_eventos.item(seleccion[0])['values'][0]
            
            try:
                self.cursor.execute('''
                    UPDATE EVENTOS 
                    SET ESTADO_AUTORIZACION = 'RECHAZADO',
                        AUTORIZADO_POR = ?,
                        FECHA_AUTORIZACION = DATETIME('now', 'localtime')
                    WHERE ID = ?
                ''', ("SECRETARIA", evento_id))
                
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Evento rechazado correctamente")
                self.cargar_eventos_pendientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al rechazar evento: {str(e)}")

    def borrar_evento(self):
        seleccion = self.tabla_eventos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un evento")
            return
            
        if messagebox.askyesno("Confirmar", "¿Está seguro de borrar este evento? Esta acción no se puede deshacer."):
            evento_id = self.tabla_eventos.item(seleccion[0])['values'][0]
            
            try:
                self.cursor.execute('DELETE FROM EVENTOS WHERE ID = ?', (evento_id,))
                
                self.conexion.commit()
                messagebox.showinfo("Éxito", "Evento borrado correctamente")
                self.cargar_eventos_pendientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al borrar evento: {str(e)}")

    def pagar_evento(self):
        seleccion = self.tabla_eventos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un evento")
            return
            
        evento_id = self.tabla_eventos.item(seleccion[0])['values'][0]
        
        # Crear ventana de pago
        ventana_pago = tk.Toplevel(self.root)
        ventana_pago.title("Registrar Pago")
        ventana_pago.configure(bg="white")
        
        # Centrar la ventana
        ventana_pago.geometry("400x500")
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 500) // 2
        ventana_pago.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame_principal = ttk.Frame(ventana_pago, style="TFrame")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            # Obtener información del evento
            self.cursor.execute('''
                SELECT NOMBRE_CLIENTE, MONTO_TOTAL, MONTO_PAGADO 
                FROM EVENTOS 
                WHERE ID = ?
            ''', (evento_id,))
            
            cliente, total, pagado = self.cursor.fetchone()
            pendiente = total - pagado
            
            # Información del evento
            ttk.Label(frame_principal, text=f"Cliente: {cliente}", 
                     style="TLabel").pack(pady=5)
            ttk.Label(frame_principal, text=f"Total: ${total:.2f}", 
                     style="TLabel").pack(pady=5)
            ttk.Label(frame_principal, text=f"Pagado: ${pagado:.2f}", 
                     style="TLabel").pack(pady=5)
            ttk.Label(frame_principal, text=f"Pendiente: ${pendiente:.2f}", 
                     style="TLabel").pack(pady=5)
            
            # Variables para el pago
            monto_pago = tk.DoubleVar(value=pendiente)
            tipo_pago = tk.StringVar(value="efectivo")
            forma_pago = tk.StringVar(value="unico")
            
            # Frame para el monto
            frame_monto = ttk.Frame(frame_principal, style="TFrame")
            frame_monto.pack(pady=10)
            ttk.Label(frame_monto, text="Monto a pagar:", 
                     style="TLabel").pack(side="left", padx=5)
            ttk.Entry(frame_monto, textvariable=monto_pago, 
                     width=15).pack(side="left", padx=5)
            
            # Frame para tipo de pago
            frame_tipo = ttk.Frame(frame_principal, style="TFrame")
            frame_tipo.pack(pady=10)
            ttk.Label(frame_tipo, text="Tipo de pago:", 
                     style="TLabel").pack(pady=5)
            ttk.Radiobutton(frame_tipo, text="Efectivo", 
                           variable=tipo_pago, value="efectivo", 
                           style="TRadiobutton").pack()
            ttk.Radiobutton(frame_tipo, text="Transferencia", 
                           variable=tipo_pago, value="transferencia", 
                           style="TRadiobutton").pack()
            
            # Frame para forma de pago
            frame_forma = ttk.Frame(frame_principal, style="TFrame")
            frame_forma.pack(pady=10)
            ttk.Label(frame_forma, text="Forma de pago:", 
                     style="TLabel").pack(pady=5)
            ttk.Radiobutton(frame_forma, text="Pago único", 
                           variable=forma_pago, value="unico", 
                           style="TRadiobutton").pack()
            ttk.Radiobutton(frame_forma, text="Abonos", 
                           variable=forma_pago, value="abonos", 
                           style="TRadiobutton").pack()
            
            def registrar_pago():
                try:
                    monto = monto_pago.get()
                    if monto <= 0:
                        messagebox.showerror("Error", "El monto debe ser mayor a 0")
                        return
                        
                    if monto > pendiente:
                        messagebox.showerror("Error", "El monto no puede ser mayor al pendiente")
                        return
                    
                    # Actualizar el monto pagado
                    nuevo_pagado = pagado + monto
                    self.cursor.execute('''
                        UPDATE EVENTOS 
                        SET MONTO_PAGADO = ?,
                            ESTADO_PAGO = CASE 
                                WHEN ? >= MONTO_TOTAL THEN 'PAGADO'
                                ELSE 'ABONO'
                            END
                        WHERE ID = ?
                    ''', (nuevo_pagado, nuevo_pagado, evento_id))
                    
                    # Registrar el pago en la tabla de pagos
                    self.cursor.execute('''
                        INSERT INTO PAGOS (
                            EVENTO_ID, MONTO, TIPO_PAGO, FORMA_PAGO, FECHA_PAGO
                        ) VALUES (?, ?, ?, ?, DATETIME('now'))
                    ''', (evento_id, monto, tipo_pago.get(), forma_pago.get()))
                    
                    self.conexion.commit()
                    messagebox.showinfo("Éxito", "Pago registrado correctamente")
                    ventana_pago.destroy()
                    self.cargar_eventos_pendientes()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al registrar el pago: {str(e)}")
            
            # Botón para registrar pago
            ttk.Button(frame_principal, text="Registrar Pago", 
                      command=registrar_pago, style="TButton").pack(pady=20)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
            ventana_pago.destroy()

    def cerrar_sesion(self):
        # Cerrar la conexión a la base de datos
        if hasattr(self, 'conexion'):
            self.conexion.close()
        # Limpiar la interfaz
        for widget in self.root.winfo_children():
            widget.destroy()
        # Restaurar tamaño original de la ventana
        self.root.geometry("450x450")
        login = ReservaApp(self.root)

    def configurar_logo(self):
        try:
            # Ruta del logo (ajusta esta ruta según la ubicación de tu imagen)
            ruta_logo = "ReservaApp/haciendo_logo.png"  # Ruta corregida

            # Verificar si el archivo existe
            if not os.path.exists(ruta_logo):
                print(f"Advertencia: No se encontró el archivo {ruta_logo}")
                return

            # Abrir la imagen con PIL
            imagen = Image.open(ruta_logo)

            # Redimensionar la imagen (opcional)
            # Ajusta el tamaño según tus necesidades
            imagen_redimensionada = imagen.resize((100, 100), Image.LANCZOS)

            # Convertir la imagen para Tkinter
            self.logo = ImageTk.PhotoImage(imagen_redimensionada)
            # Crear una etiqueta con el logo y fondo blanco
            logo_label = tk.Label(self.root, image=self.logo, bg="white")
            logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")

    def mostrar_detalles_evento(self):
        seleccion = self.tabla_eventos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor seleccione un evento")
            return
            
        evento_id = self.tabla_eventos.item(seleccion[0])['values'][0]
        
        try:
            # Obtener información detallada del evento
            self.cursor.execute('''
                SELECT e.*, 
                       GROUP_CONCAT(p.MONTO || ' (' || p.TIPO_PAGO || ' - ' || p.FORMA_PAGO || ')') as pagos,
                       (SELECT IFNULL(SUM(CANTIDAD), 0) FROM MESEROS WHERE EVENTO_ID = e.ID) as num_meseros
                FROM EVENTOS e
                LEFT JOIN PAGOS p ON e.ID = p.EVENTO_ID
                WHERE e.ID = ?
                GROUP BY e.ID
            ''', (evento_id,))
            
            evento = self.cursor.fetchone()
            
            if evento:
                # Crear ventana de detalles
                ventana_detalles = tk.Toplevel(self.root)
                ventana_detalles.title("Detalles del Evento")
                ventana_detalles.configure(bg="white")
                
                # Centrar la ventana y hacerla no redimensionable
                ventana_detalles.geometry("600x700")
                ventana_detalles.resizable(False, False)  # No permitir redimensionar
                x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
                y = self.root.winfo_y() + (self.root.winfo_height() - 700) // 2
                ventana_detalles.geometry(f"+{x}+{y}")
                
                # Frame principal
                frame_principal = ttk.Frame(ventana_detalles, style="TFrame")
                frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Título
                titulo = tk.Label(frame_principal, text="Detalles del Evento", 
                                font=("Arial", 14, "bold"), bg="white", fg="black")
                titulo.pack(pady=10)
                
                # Información del evento
                info_frame = ttk.Frame(frame_principal, style="TFrame")
                info_frame.pack(fill="both", expand=True, pady=10)
                
                # Crear etiquetas con la información
                info = [
                    f"Cliente: {evento[1]}",
                    f"Fecha del Evento: {evento[2]}",
                    f"Estado de Pago: {evento[3]}",
                    f"Monto Total: ${evento[4]:.2f}",
                    f"Monto Pagado: ${evento[5]:.2f}",
                    f"Cantidad de Personas: {evento[6]}",
                    f"Estado de Autorización: {evento[7]}",
                    f"Autorizado por: {evento[8] if evento[8] else 'No autorizado'}",
                    f"Fecha de Autorización: {evento[9] if evento[9] else 'No autorizado'}",
                    f"Mantel Seleccionado: {evento[10]}",
                    f"Cubremantel Seleccionado: {evento[11]}",
                    f"Cantidad de Meseros: {evento[13] if evento[13] else 0}"
                ]
                
                for texto in info:
                    ttk.Label(info_frame, text=texto, style="TLabel").pack(pady=5, anchor="w")
                
                # Información de pagos
                if evento[12]:  # Si hay pagos registrados
                    ttk.Label(info_frame, text="\nHistorial de Pagos:", 
                             style="TLabel").pack(pady=5, anchor="w")
                    pagos = evento[12].split(',')
                    for pago in pagos:
                        ttk.Label(info_frame, text=f"- {pago}", 
                                 style="TLabel").pack(pady=2, anchor="w")
                
                # Botón para cerrar
                ttk.Button(frame_principal, text="Cerrar", 
                          command=ventana_detalles.destroy, 
                          style="TButton").pack(pady=20)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservaApp(root)
    root.mainloop()