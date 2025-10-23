#!/usr/bin/env python3
"""
Teste para o endpoint /topobitcoin
"""

import requests
import json

def test_topobitcoin_endpoint():
    """Testa o endpoint /topobitcoin"""
    base_url = "http://localhost:8052"
    endpoint = f"{base_url}/topobitcoin"
    
    print(f"🚀 Testando endpoint: {endpoint}")
    
    try:
        response = requests.get(endpoint, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sucesso! Dados recebidos:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verifica se os campos esperados estão presentes
            expected_fields = ["valor", "data", "descricao"]
            for field in expected_fields:
                if field in data:
                    print(f"✅ Campo '{field}': {data[field]}")
                else:
                    print(f"❌ Campo '{field}' não encontrado")
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor.")
        print("   Certifique-se de que o servidor está rodando com: python trends_api.py")
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição (30s)")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_topobitcoin_endpoint()