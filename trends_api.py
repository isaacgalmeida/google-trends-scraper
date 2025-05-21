#!/usr/bin/env python3
"""
FastAPI wrapper para extrair a coluna 'Tendências' do Google Trends BR
via Selenium, esperando o carregamento dinâmico da tabela.
"""

import os
import time
import json
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Carrega variáveis de ambiente do .env ---
load_dotenv()
API_HOST     = os.getenv("API_HOST", "127.0.0.1")
API_PORT     = int(os.getenv("API_PORT", "8052"))
TIMEOUT      = int(os.getenv("PAGE_TIMEOUT", "20"))  # em segundos
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Configurações ---
URL          = os.getenv("TRENDS_URL", "https://trends.google.com/trending?geo=BR")
COOKIES_FILE = Path(__file__).parent / os.getenv("COOKIES_FILE", "cookies.json")

# --- Logging ---
logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s %(levelname)s %(message)s")

# --- FastAPI app ---
app = FastAPI(title="Google Trends Scraper API")

class TrendsResponse(BaseModel):
    trends: list[str]

def build_driver() -> webdriver.Chrome:
    opts = Options()
    # descomente para rodar sem GUI:
    # opts.add_argument("--headless")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)

def scrape_trends() -> list[str]:
    driver = build_driver()
    try:
        logging.info("Abrindo página de Trends…")
        driver.get(URL)

        # injeta cookies, se existirem
        if COOKIES_FILE.exists():
            logging.info("Injetando cookies salvos…")
            cookies = json.loads(COOKIES_FILE.read_text())
            driver.delete_all_cookies()
            for c in cookies:
                driver.add_cookie(c)
            driver.refresh()

        # espera tabela dinâmica carregar
        table_css = "#trend-table > div.enOdEe-wZVHld-zg7Cn-haAclf > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_css))
        )
        logging.info("Tabela carregada.")

        # faz scroll para lazy-load
        logging.info("Rolando para carregar conteúdo…")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # extrai cada linha (td[2] = coluna Tendências)
        rows = driver.find_elements(By.CSS_SELECTOR, f"{table_css} tbody tr")
        logging.info(f"{len(rows)} linhas encontradas.")
        trends: list[str] = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                text = cells[1].text.strip()
                if text:
                    trends.append(text)

        return trends

    finally:
        driver.quit()

@app.get("/trends", response_model=TrendsResponse)
def get_trends():
    try:
        data = scrape_trends()
        return {"trends": data}
    except Exception as e:
        logging.exception("Erro ao raspar as tendências")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("trends_api:app", host=API_HOST, port=API_PORT)
