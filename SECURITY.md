# 🛡️ Medidas de Segurança Implementadas

## Proteções Ativas

### 1. **Rate Limiting**

- Máximo de 10 requests por minuto por IP
- IPs que excedem o limite são automaticamente bloqueados
- Bloqueio temporário em memória (reinicia com o servidor)

### 2. **Detecção de IPs Suspeitos**

- Lista de IPs maliciosos conhecidos (baseada nos seus logs)
- Bloqueio de ranges de IP suspeitos (clouds conhecidas por hospedar bots)
- Bloqueio automático de IPs com comportamento suspeito

### 3. **Filtragem de Paths**

- Bloqueio de paths comuns de ataques:
  - `/admin`, `/wp-admin`, `/phpmyadmin`
  - `/etc/passwd`, `/../`, path traversal
  - `/config`, `/.env`, `/backup`
  - `/login`, `/auth`, `/api/v1`
- Retorna 404 para paths bloqueados

### 4. **Detecção de User Agents Maliciosos**

- Bloqueia ferramentas de scanning conhecidas:
  - `sqlmap`, `nikto`, `nmap`, `masscan`
  - `gobuster`, `dirb`, `wfuzz`, `nuclei`
- Bloqueia requests sem User-Agent

### 5. **Controle de Métodos HTTP**

- Apenas métodos GET e OPTIONS são permitidos
- Outros métodos retornam 405 Method Not Allowed

### 6. **Logging Detalhado**

- Logs com emojis para fácil identificação:
  - 🚨 BLOCKED: Tentativas bloqueadas
  - 🚫 RATE LIMITED: Rate limiting
  - ✅ ALLOWED: Requests legítimos
- Inclui IP, método, path e User-Agent

## Arquivos de Segurança

### `security_config.py`

- Configurações centralizadas de segurança
- Listas de IPs, paths e user agents maliciosos
- Funções de validação reutilizáveis

### `monitor_security.py`

- Monitor em tempo real de tentativas de ataque
- Análise de logs para identificar padrões
- Relatórios de estatísticas de segurança

## Como Usar

### 1. Iniciar o servidor com proteções:

```bash
python trends_api.py
```

### 2. Monitorar ataques em tempo real:

```bash
python monitor_security.py
```

### 3. Analisar logs específicos:

```bash
python monitor_security.py caminho/para/arquivo.log
```

## Logs de Exemplo

```
2025-10-28 11:30:15,123 WARNING 🚨 BLOCKED: 95.214.55.246 - POST /admin - UA: Mozilla/5.0...
2025-10-28 11:30:16,456 WARNING 🚫 RATE LIMITED: 35.203.210.168
2025-10-28 11:30:17,789 INFO ✅ ALLOWED: 172.19.0.1 - GET /topobitcoin
```

## Configurações Recomendadas para Produção

### 1. **Proxy Reverso (Nginx)**

```nginx
# Rate limiting adicional no Nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=5r/m;

server {
    location / {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:8052;
    }
}
```

### 2. **Firewall (UFW)**

```bash
# Bloquear IPs específicos
sudo ufw deny from 95.214.55.246
sudo ufw deny from 35.203.210.168

# Permitir apenas portas necessárias
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 3. **Fail2Ban**

```ini
# /etc/fail2ban/jail.local
[trends-api]
enabled = true
port = 8052
filter = trends-api
logpath = /var/log/trends-api.log
maxretry = 5
bantime = 3600
```

## Estatísticas dos Ataques Bloqueados

Com base nos seus logs, os principais atacantes foram:

- `95.214.55.246` - 12+ tentativas (POST em vários endpoints)
- `35.203.210.168` - 3+ tentativas
- `147.185.133.248` - 2+ tentativas
- `204.76.203.215` - Path traversal (`/../../../../../../etc/passwd`)

## Próximos Passos

1. **Implementar logging em arquivo** para análise posterior
2. **Adicionar notificações** para ataques críticos
3. **Integrar com serviços de threat intelligence**
4. **Implementar CAPTCHA** para requests suspeitos
5. **Adicionar autenticação** para endpoints sensíveis
