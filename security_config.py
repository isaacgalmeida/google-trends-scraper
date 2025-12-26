#!/usr/bin/env python3
"""
Configurações de segurança para a API
"""

import ipaddress
from typing import Set, List

# IPs conhecidos de scanners/atacantes (exemplos dos seus logs)
KNOWN_MALICIOUS_IPS = {
    "35.203.210.168",
    "87.251.67.27", 
    "212.73.148.10",
    "147.185.133.248",
    "95.214.55.246",
    "204.76.203.215",
    "147.185.133.7",
    "45.79.172.21",
    "35.203.210.35",
    "185.247.137.236",
    "147.185.133.29",
    "212.73.148.6",
    "172.82.90.170",
    "162.216.149.31",
    "162.216.150.232",
    "35.203.211.135",
    "85.217.149.15"
}

# Ranges de IP suspeitos (clouds conhecidas por hospedar bots)
SUSPICIOUS_IP_RANGES = [
    "35.203.0.0/16",    # Google Cloud
    "147.185.0.0/16",   # DigitalOcean
    "95.214.0.0/16",    # Hetzner
    "162.216.0.0/16",   # DigitalOcean
    "185.247.0.0/16",   # Diversos provedores
]

# Paths que sempre devem retornar 404
BLOCKED_PATHS = {
    "/admin", "/wp-admin", "/wp-login.php", "/wp-content",
    "/phpmyadmin", "/pma", "/mysql", "/sql", "/database",
    "/config", "/env", "/.env", "/.git", "/backup",
    "/test", "/debug", "/api/v1", "/v1", "/v2",
    "/login", "/signin", "/auth", "/user", "/users",
    "/robots.txt", "/sitemap.xml", "/favicon.ico",
    "/.well-known", "/xmlrpc.php", "/wp-includes",
    "/cgi-bin", "/bin", "/etc/passwd", "/proc/version"
}

# User agents suspeitos
BLOCKED_USER_AGENTS = {
    "sqlmap", "nikto", "nmap", "masscan", "zap", "burp",
    "gobuster", "dirb", "dirbuster", "wfuzz", "ffuf",
    "nuclei", "httpx", "subfinder", "amass", "shodan"
}

def is_ip_suspicious(ip: str) -> bool:
    """Verifica se um IP é suspeito"""
    if ip in KNOWN_MALICIOUS_IPS:
        return True
    
    try:
        ip_obj = ipaddress.ip_address(ip)
        for range_str in SUSPICIOUS_IP_RANGES:
            if ip_obj in ipaddress.ip_network(range_str):
                return True
    except ValueError:
        return True  # IP inválido é suspeito
    
    return False

def is_path_blocked(path: str) -> bool:
    """Verifica se um path deve ser bloqueado"""
    path_lower = path.lower()
    
    # Verifica paths exatos
    if path_lower in BLOCKED_PATHS:
        return True
    
    # Verifica se contém algum path suspeito
    for blocked in BLOCKED_PATHS:
        if blocked in path_lower:
            return True
    
    return False

def is_user_agent_blocked(user_agent: str) -> bool:
    """Verifica se um user agent deve ser bloqueado"""
    if not user_agent:
        return True  # User agent vazio é suspeito
    
    ua_lower = user_agent.lower()
    return any(blocked in ua_lower for blocked in BLOCKED_USER_AGENTS)