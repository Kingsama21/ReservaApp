import os

DB_PATH = 'test_BD_HacienditaEmyraf.db'

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print(f"Base de datos '{DB_PATH}' eliminada correctamente.")
else:
    print(f"No se encontró la base de datos '{DB_PATH}'. Ya está limpia.") 