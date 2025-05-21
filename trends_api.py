#!/usr/bin/env python3
"""
FastAPI + Selenium: extrai 'Tendências' do Google Trends BR
e adiciona endpoint para raspar Infogram.
"""

import os
import time
import json
import logging
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Carrega .env ---
load_dotenv()
API_HOST     = os.getenv("API_HOST", "0.0.0.0")
API_PORT     = int(os.getenv("API_PORT", "8052"))
TIMEOUT      = int(os.getenv("PAGE_TIMEOUT", "20"))
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO").upper()
URL          = os.getenv("TRENDS_URL", "https://trends.google.com/trending?geo=BR")
COOKIES_FILE = Path(__file__).parent / os.getenv("COOKIES_FILE", "cookies.json")

logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="Google Trends & Infogram Scraper API")

class TrendsResponse(BaseModel):
    trends: List[str]

class InfogramResponse(BaseModel):
    table1: List[List[str]]
    table2: List[List[str]]

def build_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--headless")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")
    opts.add_argument(f"--user-data-dir={profile_dir}")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=opts)

def scrape_trends() -> List[str]:
    driver = build_driver()
    try:
        logging.info("Abrindo Trends…")
        driver.get(URL)

        if COOKIES_FILE.exists():
            logging.info("Injetando cookies…")
            cookies = json.loads(COOKIES_FILE.read_text())
            driver.delete_all_cookies()
            for c in cookies:
                driver.add_cookie(c)
            driver.refresh()

        table_css = "#trend-table > div.enOdEe-wZVHld-zg7Cn-haAclf > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, table_css))
        )
        logging.info("Tabela carregada.")

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        rows = driver.find_elements(By.CSS_SELECTOR, f"{table_css} tbody tr")
        logging.info(f"{len(rows)} linhas encontradas.")
        trends = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2:
                text = cells[1].text.strip()
                if text:
                    trends.append(text)

        return trends

    finally:
        driver.quit()

def scrape_infogram(url: str) -> dict:
    driver = build_driver()
    try:
        logging.info(f"Abrindo Infogram: {url}")
        driver.get(url)
        # espera o conteúdo dinâmico carregar
        time.sleep(6)

        # tabela 1
        sel1 = "#tabpanel-chart-3 > div > div > div > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel1))
        )
        tbl1 = driver.find_element(By.CSS_SELECTOR, sel1)
        rows1 = tbl1.find_elements(By.CSS_SELECTOR, "tbody tr")
        table1 = [
            [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            for row in rows1
        ]

        # tabela 2
        sel2 = "#tabpanel-chart-2 > div > div > div > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel2))
        )
        tbl2 = driver.find_element(By.CSS_SELECTOR, sel2)
        rows2 = tbl2.find_elements(By.CSS_SELECTOR, "tbody tr")
        table2 = [
            [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            for row in rows2
        ]

        return {"table1": table1, "table2": table2}
    finally:
        driver.quit()

@app.get("/trends", response_model=TrendsResponse)
def get_trends():
    try:
        return {"trends": scrape_trends()}
    except Exception as e:
        logging.exception("Erro ao raspar tendências")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/infogram", response_model=InfogramResponse)
def get_infogram(
    url: str = Query(..., description="URL da página do Infogram (ex: https://infogram.com/...)")
):
    """
    Recebe a URL de um Infogram e retorna as duas tabelas:
      - tabela1: selector '#tabpanel-chart-3 > div > div > div > table'
      - tabela2: selector '#tabpanel-chart-2 > div > div > div > table'
    """
    try:
        return scrape_infogram(url)
    except Exception as e:
        logging.exception("Erro ao raspar Infogram")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("trends_api:app", host=API_HOST, port=API_PORT)
