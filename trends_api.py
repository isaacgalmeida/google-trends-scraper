#!/usr/bin/env python3
"""
Extrai a coluna 'Tendências' do Google Trends BR via Selenium,
esperando o carregamento dinâmico da tabela.
"""

import time
import json
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configurações ---
URL          = "https://trends.google.com/trending?geo=BR"
COOKIES_FILE = Path(__file__).parent / "cookies.json"
TIMEOUT      = 20  # segundos

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def build_driver():
    opts = Options()
    # descomente para rodar sem abrir janela:
    # opts.add_argument("--headless")
    # Evita detecção de automação :contentReference[oaicite:4]{index=4}
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=opts)  # ChromeDriver no PATH :contentReference[oaicite:5]{index=5}
    return driver

def main():
    driver = build_driver()
    try:
        logging.info("Abrindo página…")
        driver.get(URL)

        # Injeta cookies salvos para reduzir bloqueios :contentReference[oaicite:6]{index=6}
        if COOKIES_FILE.exists():
            logging.info("Injetando cookies existentes…")
            cookies = json.loads(COOKIES_FILE.read_text())
            driver.delete_all_cookies()
            for c in cookies:
                driver.add_cookie(c)
            driver.refresh()

        # 1) Espera até o container da tabela estar no DOM :contentReference[oaicite:7]{index=7}
        table_css = "#trend-table > div.enOdEe-wZVHld-zg7Cn-haAclf > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_css))
        )
        logging.info("Tabela carregada com sucesso.")

        # 2) Rola ao fim para carregar todo o conteúdo lazy-loaded :contentReference[oaicite:8]{index=8}
        logging.info("Rolando até o fim da página…")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 3) Captura cada linha e extrai o texto do 2º <td> (coluna Tendências) :contentReference[oaicite:9]{index=9}
        rows = driver.find_elements(By.CSS_SELECTOR, f"{table_css} tbody tr")
        logging.info(f"{len(rows)} linhas encontradas na tabela.")
        trends = []
        for idx, row in enumerate(rows, start=1):
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                text = cells[1].text.strip()
                if text:
                    trends.append(text)
                    logging.debug(f"{idx:02d}: {text}")
            else:
                logging.warning(f"{idx:02d}: célula de tendência não encontrada.")

        # 4) Exibe resultado
        print("\n=== Tendências Google (BR) ===")
        for i, t in enumerate(trends, 1):
            print(f"{i:2d}. {t}")
        print(f"\nTotal de tendências extraídas: {len(trends)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
