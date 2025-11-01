# 🔧 Полная инструкция по установке / Complete Setup Guide

[English](#english-version) | [Русский](#russian-version)

---

## English Version

### Prerequisites

- Python 3.8 or higher
- Microsoft Excel (required for xlwings)
- Windows OS
- Git (for cloning repository)

### Installation Steps

**1. Clone the repository:**
```bash
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Prepare your monthly template:**
- Create your monthly report template with desired formatting
- Save it as: `static/file/Шаблон.xlsx`
- Ensure it has headers in rows 1-7 and data area in rows 8+

**4. Run the application:**

Windows:
```bash
start.bat
```

Or manually:
```bash
python app.py
```

**5. Open in browser:**
```
http://localhost:5000
```

### First Time Setup

1. **Upload your first weekly file:**
   - Select month and year
   - Choose your weekly Excel file
   - Click "Upload" (Загрузить)
   - Wait for "Please wait..." animation
   - Success message appears

2. **Download monthly report:**
   - Find your month in "Monthly Reports" section
   - Click "Download" button
   - Open in Excel and verify formatting

### Troubleshooting

**xlwings not working?**
- Ensure Microsoft Excel is installed
- Run as Administrator if needed

**Formatting lost?**
- Verify template exists in `static/file/Шаблон.xlsx`
- Template must have all colors and borders

**Can't upload files?**
- Check file size (max 50MB)
- Ensure file format is .xlsx or .xls

---

## Russian Version

### Требования

- Python 3.8 или выше
- Microsoft Excel (требуется для xlwings)
- Windows
- Git (для клонирования репозитория)

### Шаги установки

**1. Клонируйте репозиторий:**
```bash
git clone https://github.com/YOURUSERNAME/AutomateExcelTasks.git
cd AutomateExcelTasks
```

**2. Установите зависимости Python:**
```bash
pip install -r requirements.txt
```

**3. Подготовьте шаблон месячного отчёта:**
- Создайте шаблон месячного отчёта с нужным форматированием
- Сохраните как: `static/file/Шаблон.xlsx`
- Убедитесь что заголовки в строках 1-7, а область данных в строках 8+

**4. Запустите приложение:**

Windows:
```bash
start.bat
```

Или вручную:
```bash
python app.py
```

**5. Откройте в браузере:**
```
http://localhost:5000
```

### Первый запуск

1. **Загрузите первый недельный файл:**
   - Выберите месяц и год
   - Выберите недельный Excel файл
   - Нажмите "Загрузить"
   - Дождитесь анимации "Пожалуйста, подождите..."
   - Появится сообщение об успехе

2. **Скачайте месячный отчёт:**
   - Найдите ваш месяц в разделе "Месячные отчёты"
   - Нажмите кнопку "Скачать"
   - Откройте в Excel и проверьте форматирование

### Решение проблем

**xlwings не работает?**
- Убедитесь что установлен Microsoft Excel
- Запустите от имени Администратора если нужно

**Форматирование потеряно?**
- Проверьте что шаблон существует в `static/file/Шаблон.xlsx`
- Шаблон должен содержать все цвета и границы

**Не загружаются файлы?**
- Проверьте размер файла (макс 50МБ)
- Убедитесь что формат файла .xlsx или .xls

---

**Дополнительная помощь:** См. [README.md](README.md) и [README.ru.md](README.ru.md)

