from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re

def obtener_marca_con_renderizado(driver, url_producto):
    try:
        driver.get(url_producto)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'body')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for li in soup.find_all("li"):
            texto = li.get_text(separator=" ", strip=True)
            if "marca" in texto.lower():
                partes = texto.split(":")
                if len(partes) > 1:
                    return partes[1].strip()
        return "Marca no encontrada"
    except Exception as e:
        print(f"❌ Error renderizando marca desde {url_producto}: {e}")
        return "Error al renderizar"

def obtener_sku_renderizado(driver):
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        posibles = soup.find_all(string=re.compile("SKU", re.IGNORECASE))
        for texto in posibles:
            match = re.search(r"SKU[:\s]*([0-9]+)", texto)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        print(f"❌ Error extrayendo SKU: {e}")
        return None
