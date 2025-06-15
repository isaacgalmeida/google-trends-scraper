# Dockerfile
FROM python:3.12-slim-bookworm

# Instala dependências do sistema para Chrome/Chromium e drivers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      chromium chromium-driver curl \
 && rm -rf /var/lib/apt/lists/*

# Defina variáveis de ambiente para o Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_PATH=/usr/lib/chromium/

WORKDIR /app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da API
COPY . .

# Exponha a porta que a API vai usar
EXPOSE 8052

# Comando padrão para iniciar a API
CMD ["uvicorn", "trends_api:app", "--host", "0.0.0.0", "--port", "8052"]
