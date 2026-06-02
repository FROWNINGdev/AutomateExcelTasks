# 📊 AutomateExcelTasks

> A bilingual (RU/UZ) Flask web platform for automating Excel reporting tasks — consolidating weekly reports, analyzing violations, comparing data sources, and merging files.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-2.2-150458?logo=pandas&logoColor=white)
![openpyxl](https://img.shields.io/badge/openpyxl-3.1-1D6F42?logo=microsoftexcel&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Overview

AutomateExcelTasks is a Flask-based web application that automates repetitive Excel/CSV reporting workflows. It lets you consolidate weekly Excel reports into monthly ones (preserving formatting), analyze violation statistics, compare UID lists across different data sources (POCHTA / Telecom / ASBT), and merge data from multiple files by column. Uploads and generated monthly reports are persisted in a local SQLite database, and the interface is fully localized in Russian and Uzbek.

## ✨ Features

- **Report consolidation** — merge weekly Excel files into a single monthly report while preserving original formatting (uses `xlwings` locally, `openpyxl` in Docker).
- **Violations analysis** — count and rank violation types from the `qoidabuzarlik nomi` column, with TXT export.
- **File comparison** — compare UID lists across sources: TXT (POCHTA, one UID per line), CSV (ASBT, `;`-separated, `TV_SERIALNUMBER` column), and Excel (Telecom, `doc_num` column). Reports totals and intersection counts; differences can be exported to TXT.
- **File merging** — combine 2+ files by specified column names and export the result as TXT or Excel.
- **Upload history & persistence** — monthly reports, weekly uploads, and stats stored in SQLite.
- **Bilingual UI (RU / UZ)** — language toggle with persisted preference; JSON-based i18n on the frontend.
- **CLI comparison tool** — `compare_month.py` runs the comparison logic standalone from the command line.
- **Dockerized deployment** — multi-stage Dockerfile and `docker-compose.yml` with a Linux-friendly dependency set (no `xlwings`).

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Flask 3.0.3, Werkzeug 3.0.3
- **Excel / data:** openpyxl 3.1.5, pandas 2.2.0, xlwings 0.32.1 (local only)
- **Database:** SQLite (via the standard library `sqlite3`)
- **Frontend:** server-rendered Jinja2 templates, vanilla JavaScript, CSS3
- **Deployment:** Docker, Docker Compose, Gunicorn 21.2.0 (Docker image)

## 🚀 Getting Started

### Prerequisites

- Python 3.11 (3.8+ should work; the Docker image uses 3.11)
- For local report consolidation: Microsoft Excel installed (required by `xlwings`). The Docker build uses an `openpyxl`-only processor and does **not** need Excel.
- Optional: Docker & Docker Compose for containerized deployment

### Installation

```bash
pip install -r requirements.txt
```

### Running

```bash
python app.py
```

Then open http://localhost:5050

To run the standalone CLI comparison tool:

```bash
python compare_month.py --base-dir "Comparer/AUGUST" --month "Avgust" --export
```

Useful CLI flags: `--base-dir`, `--month`, `--export`, `--export-dir`, `--no-progress`.

### Running with Docker

```bash
docker-compose build
docker-compose up -d
```

The app will be available at http://localhost:5050.

## ⚙️ Configuration

The application reads the following environment variables (defaults shown):

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `5050` | Port the Flask app listens on |
| `DATABASE_PATH` | `uploads.db` (`/app/data/uploads.db` in Docker) | SQLite database file path |
| `FLASK_ENV` | — | Set to `production` in Docker |

Other notes:
- Max upload size is 50 MB; allowed extensions are `.xlsx` and `.xls`.
- The monthly-report template is expected at `static/file/Шаблон.xlsx`.

## 📁 Project Structure

```
AutomateExcelTasks/
├── app.py                    # Flask app & routes (consolidation, violations, comparison, merge)
├── app_optimized.py          # Alternative/optimized app entry point
├── compare_month.py          # Standalone CLI comparison tool (POCHTA / Telecom / ASBT)
├── comparison_processor.py   # Web wrapper around compare_month.py
├── violations_processor.py   # Violation-type analysis
├── merge_processor.py        # Multi-file merge by column
├── excel_processor.py        # Monthly report consolidation (xlwings)
├── excel_processor_docker.py # openpyxl-only processor for Docker
├── database.py               # SQLite persistence layer
├── requirements.txt          # Local dependencies (incl. xlwings)
├── requirements.docker.txt   # Docker dependencies (no xlwings, + gunicorn)
├── Dockerfile                # Multi-stage build
├── docker-compose.yml        # Compose deployment
├── templates/                # Jinja2 HTML templates
└── static/                   # CSS, JS (i18n), images, template file
```

---

## 🇷🇺 Описание (Russian)

**AutomateExcelTasks** — веб-платформа на Flask для автоматизации задач по работе с Excel-отчетами: консолидация недельных отчетов в месячные, анализ нарушений, сравнение данных из разных источников и объединение файлов. Загрузки и сформированные отчеты хранятся в локальной базе SQLite. Интерфейс полностью локализован на русском и узбекском языках.

### Возможности

- **Консолидация отчетов** — объединение недельных Excel-файлов в месячный отчет с сохранением форматирования (`xlwings` локально, `openpyxl` в Docker).
- **Анализ нарушений** — подсчет и сортировка типов нарушений из столбца `qoidabuzarlik nomi`, экспорт в TXT.
- **Сравнение файлов** — сравнение списков UID между источниками: TXT (POCHTA), CSV (ASBT, разделитель `;`, столбец `TV_SERIALNUMBER`), Excel (Telecom, столбец `doc_num`). Выводит итоги и число совпадений; различия можно выгрузить в TXT.
- **Объединение файлов** — объединение 2+ файлов по указанным столбцам с экспортом в TXT или Excel.
- **История загрузок** — месячные отчеты и статистика хранятся в SQLite.
- **Двуязычный интерфейс (RU / UZ)** — переключатель языка с сохранением выбора.
- **CLI-инструмент** — `compare_month.py` для сравнения из командной строки.
- **Docker** — многоступенчатый Dockerfile и `docker-compose.yml` (без `xlwings`).

### Технологии

- Backend: Python 3.11, Flask 3.0.3
- Excel / данные: openpyxl 3.1.5, pandas 2.2.0, xlwings 0.32.1 (локально)
- База данных: SQLite
- Frontend: Jinja2, ванильный JavaScript, CSS3
- Деплой: Docker, Docker Compose, Gunicorn

### Запуск

```bash
pip install -r requirements.txt
python app.py
```

Откройте http://localhost:5050

Docker:

```bash
docker-compose build
docker-compose up -d
```

CLI:

```bash
python compare_month.py --base-dir "Comparer/AUGUST" --month "Avgust" --export
```

---

Made by [FROWNINGdev](https://github.com/FROWNINGdev) · Licensed under the MIT License.
