import subprocess
import sys
import json

 
TODAS_CATEGORIAS =  [
  "/abarrotes/aceites" 
]

MAX_CATEGORIAS = 85
CONCURRENCIA = 3

# S primeras N categorías
categorias_filtradas = TODAS_CATEGORIAS[:MAX_CATEGORIAS]

categorias_json = json.dumps(categorias_filtradas)

subprocess.run([
    sys.executable,
    "ScraperPequenoMundo.py",
    categorias_json,
    str(CONCURRENCIA)
])
