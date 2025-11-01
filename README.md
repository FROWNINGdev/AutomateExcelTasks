# 📊 AutomateExcelTasks - Excel Report Automation System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)

[English](#english) | [Русский](#russian)

---

## English

### 🎯 Project Purpose

This web application automates the consolidation of weekly Excel reports into monthly summaries with **automatic data aggregation**. 

**Problem it solves:**
- Manual consolidation of weekly reports takes hours
- Risk of calculation errors
- Formatting inconsistencies
- No tracking of upload history

**Solution:**
Upload weekly files → System automatically sums numerical data → Download formatted monthly report ✅

### ✨ Key Features

- ➕ **Automatic Data Summation** - numerical values accumulate across weeks
- 🎨 **Perfect Formatting** - colors, borders, merged cells preserved
- 💾 **Database Storage** - all files in SQLite for easy backup
- 🌐 **Bilingual** - Russian/Uzbek interface
- 🚀 **Two Deployment Options** - Native (xlwings) or Docker (openpyxl)
- 📊 **Upload History** - track all weekly uploads
- 🎭 **Custom Logo** support

### 🛠️ Technology Stack

**Backend:**
- Python 3.8+
- Flask 3.0.3
- SQLite3

**Excel Processing:**
- **Native (Windows):** xlwings 0.32.1 (COM API - 100% formatting)
- **Docker (Linux):** openpyxl 3.1.5 (Cross-platform)

**Frontend:**
- Vanilla JavaScript
- CSS3 with animations
- Custom i18n system

### 🚀 Quick Start

#### Option 1: Native (Windows with Excel)

```bash
# Clone repository
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks

# Install dependencies
pip install -r requirements.txt

# Run
start.bat
```

#### Option 2: Docker

```bash
# Clone repository
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks

# Build and run with Docker Compose
docker-compose up -d

# Access at http://localhost:5000
```

### 📖 How It Works

#### Data Aggregation Example

```
Week 1: Region KR → 5 cameras
Week 2: Region KR → 3 cameras
Monthly Result: Region KR → 8 cameras (5 + 3) ✅
```

#### Template Structure

- **Rows 1-7:** Headers (preserved from template)
- **Rows 8+:** Data area (updated from weekly files)

### 🐳 Docker Deployment

```bash
# Build image
docker build -t excel-automation .

# Run container
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/static/file:/app/static/file:ro \
  excel-automation

# Or use docker-compose
docker-compose up -d
```

### 📁 Project Structure

```
AutomateExcelTasks/
├── app.py                      # Main application (xlwings)
├── app_optimized.py            # Optimized app (auto-detect)
├── excel_processor.py          # Excel processing (xlwings)
├── excel_processor_docker.py   # Excel processing (openpyxl)
├── database.py                 # SQLite operations
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── requirements.txt            # Python deps (native)
├── requirements.docker.txt     # Python deps (Docker)
└── static/file/Шаблон.xlsx    # Monthly template
```

### 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

### 👨‍💻 Author

FROWNINGdev

### 📄 License

MIT License - see [LICENSE](LICENSE)

---

## Russian

### 🎯 Назначение проекта

Веб-приложение для автоматизации объединения еженедельных Excel отчётов в месячные с **автоматическим суммированием данных**.

**Решаемая проблема:**
- Ручное объединение недельных отчётов занимает часы
- Риск ошибок в расчётах
- Несоответствия в форматировании
- Нет учёта истории загрузок

**Решение:**
Загрузили недельные файлы → Система автоматически суммирует → Скачали готовый месячный отчёт ✅

### ✨ Основные возможности

- ➕ **Автоматическое суммирование** - числовые значения накапливаются по неделям
- 🎨 **Идеальное форматирование** - цвета, границы, объединённые ячейки
- 💾 **Хранение в БД** - все файлы в SQLite для простого бэкапа
- 🌐 **Двуязычный интерфейс** - русский/узбекский
- 🚀 **Два варианта развёртывания** - Native (xlwings) или Docker (openpyxl)
- 📊 **История загрузок** - учёт всех недельных файлов
- 🎭 **Поддержка логотипа** компании

### 🛠️ Технологии

**Backend:**
- Python 3.8+
- Flask 3.0.3
- SQLite3

**Обработка Excel:**
- **Native (Windows):** xlwings 0.32.1 (COM API - 100% форматирование)
- **Docker (Linux):** openpyxl 3.1.5 (Кросс-платформенный)

**Frontend:**
- Vanilla JavaScript
- CSS3 с анимациями
- Собственная система локализации

### 🚀 Быстрый старт

#### Вариант 1: Native (Windows с Excel)

```bash
# Клонирование
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks

# Установка зависимостей
pip install -r requirements.txt

# Запуск
start.bat
```

#### Вариант 2: Docker

```bash
# Клонирование
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks

# Сборка и запуск с Docker Compose
docker-compose up -d

# Доступ: http://localhost:5000
```

### 📖 Как работает

#### Пример агрегации данных

```
Неделя 1: Регион КР → 5 камер
Неделя 2: Регион КР → 3 камеры
Месячный результат: Регион КР → 8 камер (5 + 3) ✅
```

#### Структура шаблона

- **Строки 1-7:** Заголовки (сохраняются из шаблона)
- **Строки 8+:** Область данных (обновляется из недельных файлов)

### 🐳 Развёртывание в Docker

```bash
# Сборка образа
docker build -t excel-automation .

# Запуск контейнера
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/static/file:/app/static/file:ro \
  excel-automation

# Или через docker-compose
docker-compose up -d
```

### 🤝 Участие в проекте

См. [CONTRIBUTING.md](CONTRIBUTING.md)

### 👨‍💻 Автор

FROWNINGdev

### 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

---

**Version:** 4.0  
**Status:** Production Ready ✅
