#!/usr/bin/env python3
"""
Teste das proteções de segurança implementadas
"""

from security_config import is_ip_suspicious, is_path_blocked, is_user_agent_blocked

def test_security_functions():
    """Testa as funções de segurança"""
    print("🧪 Testando funções de segurança...\n")
    
    # Teste de IPs suspeitos
    print("1. Teste de IPs suspeitos:")
    test_ips = [
        ("95.214.55.246", True),   # IP dos logs de ataque
        ("127.0.0.1", False),     # Localhost
        ("192.168.1.1", False),   # IP privado
        ("35.203.210.168", True), # IP dos logs de ataque
    ]
    
    for ip, expected in test_ips:
        result = is_ip_suspicious(ip)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {ip:15s} -> {'Suspeito' if result else 'OK'}")
    
    # Teste de paths bloqueados
    print("\n2. Teste de paths bloqueados:")
    test_paths = [
        ("/admin", True),
        ("/wp-admin", True),
        ("/etc/passwd", True),
        ("/../../../etc/passwd", True),
        ("/topobitcoin", False),
        ("/trends", False),
        ("/", False),
    ]
    
    for path, expected in test_paths:
        result = is_path_blocked(path)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {path:25s} -> {'Bloqueado' if result else 'Permitido'}")
    
    # Teste de user agents bloqueados
    print("\n3. Teste de user agents bloqueados:")
    test_agents = [
        ("sqlmap/1.0", True),
        ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)", False),
        ("nikto", True),
        ("", True),  # User agent vazio
        ("curl/7.68.0", False),
    ]
    
    for agent, expected in test_agents:
        result = is_user_agent_blocked(agent)
        status = "✅" if result == expected else "❌"
        agent_display = agent if agent else "(vazio)"
        print(f"  {status} {agent_display:40s} -> {'Bloqueado' if result else 'Permitido'}")
    
    print("\n🎉 Testes de segurança concluídos!")

if __name__ == "__main__":
    test_security_functions()