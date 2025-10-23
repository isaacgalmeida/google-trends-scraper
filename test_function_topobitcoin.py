#!/usr/bin/env python3
"""
Teste direto da função scrape_bitcoin_top()
"""

from trends_api import scrape_bitcoin_top
import json

def test_scrape_bitcoin_top():
    """Testa diretamente a função scrape_bitcoin_top"""
    print("🚀 Testando função scrape_bitcoin_top()...")
    
    try:
        result = scrape_bitcoin_top()
        
        print("✅ Sucesso! Dados extraídos:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verifica se os campos esperados estão presentes
        expected_fields = ["valor", "data", "descricao"]
        for field in expected_fields:
            if field in result:
                print(f"✅ Campo '{field}': {result[field]}")
            else:
                print(f"❌ Campo '{field}' não encontrado")
                
        return result
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

if __name__ == "__main__":
    test_scrape_bitcoin_top()