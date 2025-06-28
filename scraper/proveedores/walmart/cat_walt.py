import requests
from bs4 import BeautifulSoup

url_base = "https://www.walmart.co.cr"

res = requests.get(url_base)
soup = BeautifulSoup(res.text, "html.parser")

categorias = set()

for a in soup.select("nav a[href^='/']"):
    href = a.get("href", "")
    texto = a.get_text(strip=True)
    if (
        href.count("/") == 1 and
        not href.endswith(".html") and
        texto and len(texto) > 2 and
        "login" not in href and "carrito" not in href
    ):
        categorias.add(href)

print("📂 Categorías detectadas:")
for cat in sorted(categorias):
    print(cat)
