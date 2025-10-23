#!/usr/bin/env python3
"""
Teste para extrair informações do Bitcoin da página https://ullqyiyh.manus.space/
Seletor: #root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-6xl.font-bold.text-foreground.mb-2
XPath: //*[@id="root"]/div/main/section[1]/div/div[1]/div[1]
"""

import time
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def build_driver() -> webdriver.Chrome:
    """Cria uma instância do Chrome WebDriver com configurações otimizadas"""
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

def test_bitcoin_scraping():
    """Testa a extração das informações do Bitcoin"""
    url = "https://ullqyiyh.manus.space/"
    
    # Seletores para testar
    css_selector = "#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-6xl.font-bold.text-foreground.mb-2"
    xpath_selector = "//*[@id='root']/div/main/section[1]/div/div[1]/div[1]"
    
    driver = build_driver()
    try:
        print(f"Abrindo página: {url}")
        driver.get(url)
        
        # Aguarda a página carregar
        time.sleep(5)
        
        print("Tentando encontrar elemento com CSS Selector...")
        try:
            element_css = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            bitcoin_value_css = element_css.text.strip()
            print(f"✅ Valor encontrado com CSS Selector: {bitcoin_value_css}")
        except Exception as e:
            print(f"❌ Erro com CSS Selector: {e}")
            bitcoin_value_css = None
        
        print("\nTentando encontrar elemento com XPath...")
        try:
            element_xpath = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_selector))
            )
            bitcoin_value_xpath = element_xpath.text.strip()
            print(f"✅ Valor encontrado com XPath: {bitcoin_value_xpath}")
        except Exception as e:
            print(f"❌ Erro com XPath: {e}")
            bitcoin_value_xpath = None
        
        # Tenta seletores alternativos mais genéricos
        print("\nTentando seletores alternativos...")
        alternative_selectors = [
            "div.text-6xl.font-bold",
            ".text-6xl",
            "[class*='text-6xl']",
            "[class*='font-bold']"
        ]
        
        for selector in alternative_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, elem in enumerate(elements):
                        text = elem.text.strip()
                        if text:
                            print(f"✅ Alternativo '{selector}' [{i}]: {text}")
            except Exception as e:
                print(f"❌ Erro com seletor alternativo '{selector}': {e}")
        
        # Mostra o HTML da página para debug
        print("\n" + "="*50)
        print("HTML da seção principal (primeiros 1000 caracteres):")
        try:
            main_section = driver.find_element(By.TAG_NAME, "main")
            html_content = main_section.get_attribute("innerHTML")[:1000]
            print(html_content)
        except:
            print("Não foi possível obter o HTML da seção main")
        
        return bitcoin_value_css or bitcoin_value_xpath
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    print("🚀 Testando extração de dados do Bitcoin...")
    result = test_bitcoin_scraping()
    
    if result:
        print(f"\n✅ Sucesso! Valor extraído: {result}")
    else:
        print("\n❌ Não foi possível extrair o valor do Bitcoin")