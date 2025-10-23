# Endpoint TopoBitcoin

## Descrição

Novo endpoint `/topobitcoin` adicionado ao `trends_api.py` que extrai informações do indicador CBBI (Confiança de Estar no Topo) do Bitcoin da página https://ullqyiyh.manus.space/

## Funcionalidade

O endpoint extrai as seguintes informações:

- **valor**: O valor atual do indicador CBBI
- **data**: Data da última atualização
- **descricao**: Descrição do indicador

## Uso

```bash
GET http://localhost:8052/topobitcoin
```

### Resposta de exemplo:

```json
{
  "valor": "69",
  "data": "23 de outubro de 2025",
  "descricao": "CONFIANÇA DE ESTAR NO TOPO"
}
```

## Arquivos criados/modificados

### 1. `trends_api.py` (modificado)

- Adicionado modelo `BitcoinTopResponse`
- Adicionada função `scrape_bitcoin_top()`
- Adicionado endpoint `/topobitcoin`

### 2. `test.py` (criado)

- Teste inicial para verificar a extração de dados da página
- Testa diferentes seletores CSS e XPath

### 3. `test_function_topobitcoin.py` (criado)

- Teste direto da função `scrape_bitcoin_top()`
- Não requer servidor rodando

### 4. `test_topobitcoin.py` (criado)

- Teste do endpoint via HTTP
- Requer servidor rodando

## Seletores utilizados

- **Valor principal**: `#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-6xl.font-bold.text-foreground.mb-2`
- **Data**: `#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > div.text-sm.text-muted-foreground`
- **Descrição**: `#root > div > main > section.text-center.mb-12 > div > div.text-center.mb-6 > h2.text-lg.font-medium.text-muted-foreground.mb-2`

## Como testar

### 1. Teste da função diretamente:

```bash
python test_function_topobitcoin.py
```

### 2. Teste do endpoint (requer servidor rodando):

```bash
# Terminal 1: Iniciar servidor
python trends_api.py

# Terminal 2: Testar endpoint
python test_topobitcoin.py
```

### 3. Teste manual via curl:

```bash
curl http://localhost:8052/topobitcoin
```

## Status

✅ Implementado e testado com sucesso
✅ Extração de dados funcionando
✅ Endpoint integrado ao trends_api.py
✅ Testes criados e validados
