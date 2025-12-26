#!/usr/bin/env python3
"""
Monitor de segurança para acompanhar tentativas de ataque
"""

import re
import time
from collections import defaultdict, Counter
from datetime import datetime
import subprocess
import sys

def monitor_logs():
    """Monitora logs em tempo real"""
    print("🔍 Monitorando tentativas de ataque...")
    print("Pressione Ctrl+C para parar\n")
    
    blocked_ips = Counter()
    attack_patterns = Counter()
    
    try:
        # Se estiver rodando o servidor, monitore os logs
        # Aqui você pode adaptar para ler de um arquivo de log se necessário
        while True:
            # Simula monitoramento - em produção, leia de logs reais
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitorando...")
            
            if blocked_ips:
                print("\n📊 Top IPs bloqueados:")
                for ip, count in blocked_ips.most_common(5):
                    print(f"  {ip}: {count} tentativas")
            
            if attack_patterns:
                print("\n🎯 Padrões de ataque mais comuns:")
                for pattern, count in attack_patterns.most_common(5):
                    print(f"  {pattern}: {count} vezes")
            
            time.sleep(30)  # Atualiza a cada 30 segundos
            
    except KeyboardInterrupt:
        print("\n\n📈 Relatório final:")
        print(f"Total de IPs únicos bloqueados: {len(blocked_ips)}")
        print(f"Total de tentativas bloqueadas: {sum(blocked_ips.values())}")
        
        if blocked_ips:
            print("\n🥇 Top 10 atacantes:")
            for i, (ip, count) in enumerate(blocked_ips.most_common(10), 1):
                print(f"  {i:2d}. {ip:15s} - {count:3d} tentativas")

def analyze_log_file(log_file: str):
    """Analisa um arquivo de log específico"""
    print(f"📁 Analisando arquivo: {log_file}")
    
    blocked_ips = Counter()
    paths_attacked = Counter()
    user_agents = Counter()
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Procura por logs de bloqueio
                if "🚨 BLOCKED:" in line:
                    # Extrai IP
                    ip_match = re.search(r'BLOCKED: (\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        blocked_ips[ip_match.group(1)] += 1
                    
                    # Extrai path
                    path_match = re.search(r'(GET|POST) ([^\s]+)', line)
                    if path_match:
                        paths_attacked[path_match.group(2)] += 1
                
                # Procura por rate limiting
                elif "🚫 RATE LIMITED:" in line:
                    ip_match = re.search(r'RATE LIMITED: (\d+\.\d+\.\d+\.\d+)', line)
                    if ip_match:
                        blocked_ips[ip_match.group(1)] += 1
        
        print(f"\n📊 Estatísticas:")
        print(f"IPs únicos bloqueados: {len(blocked_ips)}")
        print(f"Total de tentativas: {sum(blocked_ips.values())}")
        
        if blocked_ips:
            print(f"\n🥇 Top 10 atacantes:")
            for i, (ip, count) in enumerate(blocked_ips.most_common(10), 1):
                print(f"  {i:2d}. {ip:15s} - {count:3d} tentativas")
        
        if paths_attacked:
            print(f"\n🎯 Paths mais atacados:")
            for i, (path, count) in enumerate(paths_attacked.most_common(10), 1):
                print(f"  {i:2d}. {path:30s} - {count:3d} tentativas")
                
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {log_file}")
    except Exception as e:
        print(f"❌ Erro ao analisar arquivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Analisa arquivo específico
        analyze_log_file(sys.argv[1])
    else:
        # Monitora em tempo real
        monitor_logs()