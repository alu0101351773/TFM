import os

# Obtener la ruta del directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta del archivo CSV relativo al directorio del script
csv_file_path = os.path.join(script_dir, 'inventario-1anio.csv')

# Ahora puedes abrir el archivo CSV usando la ruta absoluta
with open(csv_file_path, 'r') as csv_file:
    print('Esto funca!!')
    pass
