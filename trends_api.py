#!/usr/bin/env python3
"""
FastAPI + Selenium: extrai 'Tendências' do Google Trends (por país e categoria)
e adiciona endpoint para raspar Infogram.
"""

import os
import time
import json
import logging
import tempfile
from pathlib import Path
from typing import List
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from security_config import is_ip_suspicious, is_path_blocked, is_user_agent_blocked

# --- Carrega .env ---
load_dotenv()
API_HOST     = os.getenv("API_HOST", "0.0.0.0")
API_PORT     = int(os.getenv("API_PORT", "8052"))
TIMEOUT      = int(os.getenv("PAGE_TIMEOUT", "20"))
LOG_LEVEL    = os.getenv("LOG_LEVEL", "INFO").upper()
TRENDS_URL   = os.getenv("TRENDS_URL", "https://trends.google.com/trending?geo=BR")
COOKIES_FILE = Path(__file__).parent / os.getenv("COOKIES_FILE", "cookies.json")

logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s %(levelname)s %(message)s")

SUPPORTED_GEO_CODES = {
    "BR": "Brasil",
    "US": "Estados Unidos",
    "UK": "Reino Unido",
    "IN": "Índia",
    "CA": "Canadá",
    "AU": "Austrália",
    "DE": "Alemanha",
    "FR": "França",
    "JP": "Japão",
    "IT": "Itália"
}

CATEGORIES = {
    "0": "Todas as categorias",
    "3": "Artes e Entretenimento",
    "5": "Computadores e Eletrônicos",
    "7": "Finanças",
    "8": "Jogos",
    "11": "Casa e Jardim",
    "12": "Negócios e Indústria",
    "13": "Internet e Telecomunicações",
    "14": "Pessoas e Sociedade",
    "16": "Notícias",
    "18": "Compras",
    "19": "Leis e Governo",
    "20": "Esportes",
    "22": "Livros e Literatura",
    "23": "Artes Cênicas",
    "24": "Artes Visuais e Design",
    "25": "Publicidade e Marketing",
    "26": "Automóveis e Veículos",
    "27": "Beleza e Fitness",
    "28": "Alimentos e Bebidas",
    "29": "Saúde",
    "30": "Hobbies e Lazer",
    "31": "Empregos e Educação",
    "32": "Lei e Governo",
    "33": "Ciência",
    "34": "Viagens",
    "35": "Imóveis",
    "36": "Referência",
    "37": "Animais e Pets",
    "38": "Religião e Espiritualidade",
    "39": "Pessoas e Sociedade",
    "40": "Ciência",
    "41": "Viagens",
    "42": "Imóveis",
    "43": "Referência",
    "44": "Animais e Pets",
    "45": "Religião e Espiritualidade",
    "46": "Pessoas e Sociedade",
    "47": "Ciência",
    "48": "Viagens",
    "49": "Imóveis",
    "50": "Referência"
}

app = FastAPI(title="Google Trends & Infogram Scraper API")

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique domínios específicos
    allow_credentials=True,
    allow_methods=["GET"],  # Apenas métodos necessários
    allow_headers=["*"],
)

# Rate limiting simples em memória
request_counts = defaultdict(lambda: deque())
RATE_LIMIT_REQUESTS = 10  # máximo de requests
RATE_LIMIT_WINDOW = 60    # por minuto
BLOCKED_IPS = set()

def is_suspicious_request(path: str, user_agent: str = "", client_ip: str = "") -> bool:
    """Detecta requisições suspeitas"""
    # Verifica IP suspeito
    if client_ip and is_ip_suspicious(client_ip):
        return True
    
    # Verifica path bloqueado
    if is_path_blocked(path):
        return True
    
    # Verifica user agent bloqueado
    if is_user_agent_blocked(user_agent):
        return True
    
    # Verifica tentativas de path traversal
    if '../' in path or '..\\' in path:
        return True
    
    return False

def check_rate_limit(client_ip: str) -> bool:
    """Verifica rate limiting por IP"""
    if client_ip in BLOCKED_IPS:
        return False
    
    now = datetime.now()
    minute_ago = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    # Remove requests antigos
    while request_counts[client_ip] and request_counts[client_ip][0] < minute_ago:
        request_counts[client_ip].popleft()
    
    # Verifica se excedeu o limite
    if len(request_counts[client_ip]) >= RATE_LIMIT_REQUESTS:
        BLOCKED_IPS.add(client_ip)
        logging.warning(f"IP {client_ip} bloqueado por excesso de requests")
        return False
    
    # Adiciona request atual
    request_counts[client_ip].append(now)
    return True

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Middleware de segurança"""
    client_ip = request.client.host
    path = request.url.path
    user_agent = request.headers.get("user-agent", "")
    
    # Log de tentativas suspeitas
    if is_suspicious_request(path, user_agent, client_ip):
        logging.warning(f"🚨 BLOCKED: {client_ip} - {request.method} {path} - UA: {user_agent[:100]}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Not found"}
        )
    
    # Rate limiting
    if not check_rate_limit(client_ip):
        logging.warning(f"🚫 RATE LIMITED: {client_ip}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"}
        )
    
    # Bloqueia métodos não permitidos
    allowed_methods = ["GET", "OPTIONS"]
    if request.method not in allowed_methods:
        logging.warning(f"🚫 METHOD NOT ALLOWED: {client_ip} - {request.method} {path}")
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={"detail": "Method not allowed"}
        )
    
    # Log de requests legítimos
    if path in ["/trends", "/categories", "/infogram", "/topobitcoin"]:
        logging.info(f"✅ ALLOWED: {client_ip} - {request.method} {path}")
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    """Endpoint raiz com informações básicas"""
    return {
        "message": "Google Trends & Bitcoin Scraper API",
        "version": "1.0.0",
        "endpoints": [
            "/trends - Google Trends data",
            "/categories - Available categories",
            "/infogram - Infogram scraping",
            "/topobitcoin - Bitcoin top indicator",
            "/docs - API documentation"
        ]
    }

class TrendsResponse(BaseModel):
    trends: List[str]

class InfogramResponse(BaseModel):
    carteira: List[List[str]]
    movimentacao: List[List[str]]

class BitcoinTopResponse(BaseModel):
    valor: str
    data: str
    descricao: str

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

def scrape_trends(geo: str = None, category: str = None) -> List[str]:
    # Monta URL com base nos parâmetros ou usa fallback
    if geo:
        geo = geo.upper()
        if geo not in SUPPORTED_GEO_CODES:
            raise HTTPException(
                status_code=400,
                detail=f"Código de país '{geo}' não suportado. Use: {', '.join(SUPPORTED_GEO_CODES.keys())}"
            )
        url = f"https://trends.google.com/trending?geo={geo}"
        if category:
            url += f"&category={category}"
    else:
        url = TRENDS_URL

    driver = build_driver()
    try:
        logging.info(f"Abrindo Trends: {url}")
        driver.get(url)

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
        time.sleep(6)

        sel1 = "#tabpanel-chart-3 > div > div > div > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel1))
        )
        tbl1 = driver.find_element(By.CSS_SELECTOR, sel1)
        rows1 = tbl1.find_elements(By.CSS_SELECTOR, "tbody tr")
        carteira = [
            [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            for row in rows1
        ]

        sel2 = "#tabpanel-chart-2 > div > div > div > table"
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, sel2))
        )
        tbl2 = driver.find_element(By.CSS_SELECTOR, sel2)
        rows2 = tbl2.find_elements(By.CSS_SELECTOR, "tbody tr")
        movimentacao = [
            [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            for row in rows2
        ]

        return {"carteira": carteira, "movimentacao": movimentacao}
    finally:
        driver.quit()

def scrape_bitcoin_top() -> dict:
    """Extrai informações do Bitcoin da página https://ullqyiyh.manus.space/"""
    url = "https://ullqyiyh.manus.space/"
    driver = build_driver()
    try:
        logging.info(f"Abrindo página Bitcoin: {url}")
        driver.get(url)
        time.sleep(5)

        # Seletor principal para o valor
        valor_selector = "#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-6xl.font-bold.text-foreground.mb-2"
        
        # Aguarda o elemento carregar
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, valor_selector))
        )
        
        # Extrai o valor
        valor_element = driver.find_element(By.CSS_SELECTOR, valor_selector)
        valor = valor_element.text.strip()
        
        # Extrai a data (elemento seguinte)
        data_selector = "#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-sm.text-muted-foreground"
        try:
            data_element = driver.find_element(By.CSS_SELECTOR, data_selector)
            data = data_element.text.strip()
        except:
            data = "Data não disponível"
        
        # Extrai a descrição (título da seção)
        descricao_selector = "#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > h2.text-lg.font-medium.text-muted-foreground.mb-2"
        try:
            descricao_element = driver.find_element(By.CSS_SELECTOR, descricao_selector)
            descricao = descricao_element.text.strip()
        except:
            descricao = "CONFIANÇA DE ESTAR NO TOPO"
        
        return {
            "valor": valor,
            "data": data,
            "descricao": descricao
        }
        
    finally:
        driver.quit()

@app.get("/trends", response_model=TrendsResponse)
def get_trends(
    request: Request,
    geo: str = Query(None, description="Código do país (ex: BR, US, UK, IN...)"),
    category: str = Query(None, description="Código da categoria (ex: 20 para Esportes)")
):
    """
    Retorna tendências por país (geo) e opcionalmente por categoria.
    Se nada for passado, usa a URL padrão do .env (TRENDS_URL).
    """
    try:
        logging.info(f"Trends request from {request.client.host}")
        return {"trends": scrape_trends(geo, category)}
    except Exception as e:
        logging.exception("Erro ao raspar tendências")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
def get_categories(request: Request):
    """
    Retorna a lista de categorias disponíveis no Google Trends.
    """
    logging.info(f"Categories request from {request.client.host}")
    return JSONResponse(content=CATEGORIES)

@app.get("/infogram", response_model=InfogramResponse)
def get_infogram(
    request: Request,
    url: str = Query(..., description="URL da página do Infogram (ex: https://infogram.com/...)")
):
    """
    Recebe a URL de um Infogram e retorna as duas tabelas:
      - tabela1: selector '#tabpanel-chart-3 > div > div > div > table'
      - tabela2: selector '#tabpanel-chart-2 > div > div > div > table'
    """
    try:
        logging.info(f"Infogram request from {request.client.host}")
        return scrape_infogram(url)
    except Exception as e:
        logging.exception("Erro ao raspar Infogram")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/topobitcoin", response_model=BitcoinTopResponse)
def get_topo_bitcoin(request: Request):
    """
    Extrai informações do indicador CBBI (Confiança de Estar no Topo) do Bitcoin
    da página https://ullqyiyh.manus.space/
    
    Retorna:
    - valor: O valor atual do indicador
    - data: Data da última atualização
    - descricao: Descrição do indicador
    """
    try:
        logging.info(f"Bitcoin request from {request.client.host}")
        return scrape_bitcoin_top()
    except Exception as e:
        logging.exception("Erro ao raspar dados do Bitcoin")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("trends_api:app", host=API_HOST, port=API_PORT)
