import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import os
import sys
# Base de datos simulada
base_datos = {
    "mesas": 15,
    "sillas": 150,
    "cubremanteles": ["blanco", "negro", "rojo", "azul", "verde", "amarillo"],
    "reservas": []  # Aquí se almacenarán las reservas
}

class SistemaReservas:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas - Haciendita Emyraf")
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        # Definir el tamaño de la ventana
        ancho_ventana = 600
        alto_ventana = 600

        # Calcular la posición para centrar la ventana
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2

        # Establecer la geometría de la ventana
        root.geometry(f'{ancho_ventana}x{alto_ventana}+{x}+{y}')

        # Configuración de variables
        self.fecha_reserva = tk.StringVar()
        self.mesas_reservadas = tk.IntVar(value=1)
        self.incluye_vajilla = tk.BooleanVar()
        self.incluye_cristaleria = tk.BooleanVar()
        self.permiso_alcoholes = tk.BooleanVar()
        self.meseros = tk.IntVar(value=0)
        
        # Elementos de la interfaz
        self.crear_interfaz()

    def crear_interfaz(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Calendario para seleccionar fecha
        ttk.Label(self.root, text="Seleccione la fecha del evento:").pack(pady=10)
        self.calendario = Calendar(self.root, date_pattern="yyyy-mm-dd")
        self.calendario.pack(pady=10)

        # Selección de mesas
        ttk.Label(self.root, text="Número de mesas a reservar (Máximo 15):").pack(pady=5)
        ttk.Spinbox(self.root, from_=1, to=15, textvariable=self.mesas_reservadas, width=10).pack(pady=5)

        # Opciones de vajilla y cristalería
        ttk.Checkbutton(self.root, text="Incluir plato base y plato", variable=self.incluye_vajilla).pack(pady=5)
        ttk.Checkbutton(self.root, text="Incluir cristalería", variable=self.incluye_cristaleria).pack(pady=5)

        # Extras
        ttk.Checkbutton(self.root, text="Permiso de alcoholes ($1500)", variable=self.permiso_alcoholes).pack(pady=5)
        ttk.Label(self.root, text="Número de meseros ($400 cada uno):").pack(pady=5)
        ttk.Spinbox(self.root, from_=0, to=10, textvariable=self.meseros, width=10).pack(pady=5)

        # Botón para calcular y reservar
        ttk.Button(self.root, text="Calcular y Reservar", command=self.calcular_reserva).pack(pady=20)
        ttk.Button(self.root, text="Cerrar Sesión", command=self.cerrar_sesion).pack(pady=20)

    def calcular_reserva(self):
        # Obtener fecha
        fecha = self.calendario.get_date()

        # Calcular precio base según la temporada
        mes = int(fecha.split("-")[1])
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
    def cerrar_sesion(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        login = ReservaApp(self.root)

    def crear_apartado_eventos(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Apartar Evento", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(self.root, text="Nombre del Evento:").pack()
        self.event_name_entry = tk.Entry(self.root, width= 20, font=("Arial", 18))
        self.event_name_entry.pack()
        
        
        tk.Button(self.root, text="Guardar", command=self.crear_interfaz).pack(pady=10)
        tk.Button(self.root, text="Regresar", command=self.crear_interfaz).pack()
    
    def save_booking(self):
        event_name = self.event_name_entry.get()
        event_date = self.event_date_entry.get()
        
        if event_name and event_date:
            messagebox.showinfo("Éxito", f"Evento '{event_name}' registrado para {event_date}")
            self.create_main_screen()
        else:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
    

class ReservaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas - Haciendita Emyraf")
        ancho_pantalla = root.winfo_screenwidth()
        alto_pantalla = root.winfo_screenheight()
        # Definir el tamaño de la ventana
        ancho_ventana = 400
        alto_ventana = 350

        # Calcular la posición para centrar la ventana
        x = (ancho_pantalla - ancho_ventana) // 2
        y = (alto_pantalla - alto_ventana) // 2

        # Establecer la geometría de la ventana
        root.geometry(f'{ancho_ventana}x{alto_ventana}+{x}+{y}')
        self.configurar_icono_taskbar()
        self.configurar_icono()
        self.create_login_screen()
    
    def configurar_logo(self):
        try:
            # Ruta del logo (ajusta esta ruta según la ubicación de tu imagen)
            ruta_logo = "haciendo_logo.png"  # Cambia esto a la ruta de tu logo

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

            # Crear una etiqueta con el logo
            logo_label = tk.Label(self.root, image=self.logo)
            logo_label.pack(pady=10)

        except Exception as e:
            print(f"Error al cargar el logo: {e}")
    def configurar_icono(self):
        try:
            # Rutas de ícono (prueba múltiples formatos)
            rutas_iconos = [
                "icono_programadores.ico",      # Formato Windows
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
                "icono_programadores.ico",
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
    
    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.configurar_logo()

        tk.Label(self.root, text="Inicio de Sesión", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(self.root, text="Usuario:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        
        tk.Label(self.root, text="Contraseña:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        
        tk.Button(self.root, text="Ingresar", command=self.verify_login).pack(pady=10)
    
    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username == "admin" and password == "1234":
            for widget in self.root.winfo_children():
                widget.destroy()
            reservas = SistemaReservas(self.root)
            
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    
    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Menú Principal", font=("Arial", 14)).pack(pady=10)
        
        #tk.Button(self.root, text="Apartar Evento", command=self.crear_apartado_eventos).pack(pady=5)
        tk.Button(self.root, text="Gestionar Pagos", command=self.create_payment_screen).pack(pady=5)
        tk.Button(self.root, text="Cerrar Sesión", command=self.create_login_screen).pack(pady=5)
    
    def create_payment_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        tk.Label(self.root, text="Gestión de Pagos", font=("Arial", 14)).pack(pady=10)
        
        tk.Label(self.root, text="Ingrese el monto:").pack()
        self.payment_entry = tk.Entry(self.root)
        self.payment_entry.pack()
        
        tk.Button(self.root, text="Realizar Pago", command=self.process_payment).pack(pady=10)
        tk.Button(self.root, text="Regresar", command=self.create_main_screen).pack()
    
    def process_payment(self):
        amount = self.payment_entry.get()
        
        if amount.isdigit():
            messagebox.showinfo("Éxito", f"Pago de ${amount} realizado con éxito")
            self.create_main_screen()
        else:
            messagebox.showerror("Error", "Ingrese un monto válido")

if __name__ == "__main__":
    root = tk.Tk()
    app = ReservaApp(root)
    root.mainloop()