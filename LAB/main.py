import subprocess
import sys
import json

# 🔧 Configuración
TODAS_CATEGORIAS =  [
  "/abarrotes/aceites",
  "/abarrotes/articulos-de-papel",
  "/abarrotes/bebidas",
  "/abarrotes/cafe-y-te",
  "/abarrotes/cereales",
  "/abarrotes/chocolates",
  "/abarrotes/condimentos",
  "/abarrotes/confites",
  "/abarrotes/cuidado-personal",
  "/abarrotes/desechables",
  "/abarrotes/enlatados",
  "/abarrotes/envolturas",
  "/abarrotes/galletas",
  "/abarrotes/granos",
  "/abarrotes/harinas",
  "/abarrotes/jaleas",
  "/abarrotes/lacteo",
  "/abarrotes/libre-de-gluten",
  "/abarrotes/licores",
  "/abarrotes/limpieza",
  "/abarrotes/pastas",
  "/abarrotes/salsas",
  "/abarrotes/siropes",
  "/abarrotes/snacks",
  "/abarrotes/sopas-y-consomes",
  "/abarrotes/suplementos",
  "/ferreteria/acabados",
  "/ferreteria/accesorios-de-ferreteria",
  "/ferreteria/articulos-carro",
  "/ferreteria/articulos-electricos",
  "/ferreteria/articulos-para-motocicletas",
  "/ferreteria/construccion",
  "/ferreteria/herramientas",
  "/ferreteria/iluminacion",
  "/ferreteria/jardineria",
  "/ferreteria/seguridad",
  "/hogar/adornos-decoracion",
  "/hogar/alfombras",
  "/hogar/articulos-deportivos",
  "/hogar/ba-o",
  "/hogar/bebes-y-damas",
  "/hogar/camping-e-inflables",
  "/hogar/canastas",
  "/hogar/candelas-y-candelabros",
  "/hogar/ceramica",
  "/hogar/cocina",
  "/hogar/cortinas",
  "/hogar/cristaleria",
  "/hogar/dormitorio",
  "/hogar/electrodomesticos",
  "/hogar/equipo-medico",
  "/hogar/escolar-y-oficina",
  "/hogar/espejos",
  "/hogar/fiesta",
  "/hogar/juguetes-1",
  "/hogar/lavanderia",
  "/hogar/maletas",
  "/hogar/navidad",
  "/hogar/plastico",
  "/hogar/portarretratos",
  "/hogar/temporada-lluviosa",
  "/mascotas-varias/gatos",
  "/mascotas-varias/perros",
  "/muebles/bancos",
  "/muebles/camas-camarotes-y-colchones",
  "/muebles/estantes",
  "/muebles/mesas-decorativas",
  "/muebles/mesas-industriales",
  "/muebles/muebles-de-cocina",
  "/muebles/muebles-de-dormitorio",
  "/muebles/muebles-de-jardin",
  "/muebles/muebles-de-tv",
  "/muebles/muebles-infantiles",
  "/muebles/muebles-plegables",
  "/muebles/oficina",
  "/muebles/ottoman",
  "/muebles/repisas",
  "/muebles/sillas-basicas",
  "/muebles/sillon",
  "/muebles/zapateras",
  "/vacaciones",
  "/liquidaciones",
  "/mi-negocio-limpio",
  "/electrodomesticos",
  "/mallas-construccion"
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
