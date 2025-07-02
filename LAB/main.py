import subprocess
import sys
import json

# 🔧 Configuración
TODAS_CATEGORIAS =  [
  "/abarrotes/aceites"
  
]


MAX_CATEGORIAS = 85
CONCURRENCIA = 3

# Seleccionar solo las primeras N categorías
categorias_filtradas = TODAS_CATEGORIAS[:MAX_CATEGORIAS]

# Convertir el array a JSON como string para pasarlo como argumento
categorias_json = json.dumps(categorias_filtradas)

# Ejecutar el archivo y pasarle la lista de categorías y concurrencia como argumentos
subprocess.run([
    sys.executable,
    "ScraperPequenoMundo.py",
    categorias_json,
    str(CONCURRENCIA)
])
