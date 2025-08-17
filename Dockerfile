# Používame Python 3.11 slim image
FROM python:3.11-slim

# Nastavíme pracovný adresár
WORKDIR /app

# Nainštalujeme systémové závislosti
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Skopírujeme requirements.txt
COPY requirements.txt .

# Nainštalujeme Python závislosti
RUN pip install --no-cache-dir -r requirements.txt

# Skopírujeme celý projekt
COPY . .

# Vytvoríme adresár pre databázu
RUN mkdir -p /app/data

# Nastavíme environment premenné
ENV PYTHONPATH=/app
ENV LITESTAR_APP=app.main:app

# Vystavíme port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Spustíme aplikáciu pomocou uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
