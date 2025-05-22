# Google Trends Scraper API

Este projeto fornece uma API que extrai a coluna **Tendências** do Google Trends Brasil utilizando Selenium.

## 📋 Descrição

- Abre um navegador Chrome/Chromium automatizado
- Espera o carregamento dinâmico da tabela de tendências
- Extrai o texto da segunda coluna (`td:nth-child(2)`) de cada linha
- Expõe um endpoint **GET /trends** que retorna JSON com a lista de tendências

---

## 🔧 Requisitos

- Python 3.8+
- Chrome ou Chromium instalado
- [ChromeDriver](https://sites.google.com/chromium.org/driver/) compatível no seu `PATH`

---

## 📦 Instalação

1. Clone este repositório ou copie os arquivos para sua máquina.
2. Crie e ative um ambiente virtual (opcional, mas recomendado):

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

```env
# Host e porta onde a API irá rodar
API_HOST=127.0.0.1
API_PORT=8052

# URL do Google Trends (Brasil)
TRENDS_URL=https://trends.google.com/trending?geo=BR

# Timeout para carregamento da página em segundos
PAGE_TIMEOUT=20

# Nome do arquivo de cookies (opcional)
COOKIES_FILE=cookies.json

# Nível de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

---

## 🚀 Uso

1. Garanta que o `chromedriver` está disponível no seu `PATH`.
2. Execute a API:

   ```bash
   python trends_api.py
   ```

3. Acesse o endpoint:

   ```bash
   curl http://127.0.0.1:8052/trends
   
   Trends do BRasil apenas
   curl http://127.0.0.1:8052/trends?geo=BR
   
   Trends do BRasil e categoria 18 - Tecnologia
   curl http://127.0.0.1:8052/trends?geo=BR&category=18
   
   Trends dos EUA e categoria 18 - Tecnologia
   curl http://127.0.0.1:8052/trends?geo=US&category=18
   
   Lista de categorias
   curl http://127.0.0.1:8052/categories
   ```

Você deverá receber uma resposta em JSON assim:

```json
{
  "trends": [
    "vasco da gama x operário",
    "náutico x são paulo",
    "grêmio x csa",
    "...",
    "última tendência"
  ]
}
```

---

## 📝 Exemplo de código principal

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ...
def scrape_trends():
    driver = webdriver.Chrome(options=chrome_opts)
    driver.get(TRENDS_URL)
    WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, table_css))
    )
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    rows = driver.find_elements(By.CSS_SELECTOR, f"{table_css} tbody tr")
    trends = [r.find_elements(By.TAG_NAME, "td")[1].text.strip() for r in rows]
    driver.quit()
    return trends
```

---

## 📄 Licença

Este projeto está sob a [MIT License](LICENSE). Feel free to use and modify!

```

```

```

```
