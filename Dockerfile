# Multi-stage build для оптимизации размера
FROM python:3.11-slim as builder

# Установка зависимостей для сборки
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копирование и установка зависимостей
COPY requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

# Финальный образ
FROM python:3.11-slim

# Метаданные
LABEL maintainer="AutomateExcelTasks"
LABEL version="4.0"
LABEL description="Excel Report Automation System"

# Создание пользователя без прав root
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/uploads /app/static/file && \
    chown -R appuser:appuser /app

# Копирование виртуального окружения из builder
COPY --from=builder /opt/venv /opt/venv

# Установка рабочей директории
WORKDIR /app

# Копирование приложения
COPY --chown=appuser:appuser . .

# Установка переменных окружения
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP=app.py

# Переключение на непривилегированного пользователя
USER appuser

# Открытие порта
EXPOSE 5050

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5050')"

# Копирование Docker-версии процессора перед запуском
RUN cp excel_processor_docker.py excel_processor.py

# Запуск приложения
CMD ["python", "app.py"]

