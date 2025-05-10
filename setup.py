import sys
import os
from cx_Freeze import setup, Executable

# Obtener la ruta del directorio actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Dependencias
build_exe_options = {
    "packages": ["tkinter", "tkcalendar", "PIL", "sqlite3"],
    "include_files": [
        (os.path.join(current_dir, "haciendo_logo.png"), "haciendo_logo.png"),
        (os.path.join(current_dir, "icono_programadores.ico"), "icono_programadores.ico"),
        (os.path.join(current_dir, "BD_HacienditaEmyraf.db"), "BD_HacienditaEmyraf.db")
    ],
    "excludes": ["test", "distutils"],
    "include_msvcr": True
}

# Configuración del ejecutable
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="Sistema de Reservas",
    version="1.0",
    description="Sistema de Reservas - Haciendita Emyraf",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            os.path.join(current_dir, "main.py"),
            base=base,
            icon=os.path.join(current_dir, "icono_programadores.ico"),
            target_name="SistemaReservas.exe"
        )
    ]
) 