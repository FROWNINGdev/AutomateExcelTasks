// Переводы
const translations = {
    ru: {
        title: 'Платформа отчетности',
        systemTitle: 'Платформа отчетности',
        systemSubtitle: 'Автоматизация документооборота',
        uploadWeekly: 'Загрузка недельного отчёта',
        month: 'Месяц:',
        year: 'Год:',
        file: 'Файл:',
        selectMonth: 'Выберите',
        january: 'Январь',
        february: 'Февраль',
        march: 'Март',
        april: 'Апрель',
        may: 'Май',
        june: 'Июнь',
        july: 'Июль',
        august: 'Август',
        september: 'Сентябрь',
        october: 'Октябрь',
        november: 'Ноябрь',
        december: 'Декабрь',
        supportedFormats: 'Поддерживаются форматы: .xlsx, .xls',
        upload: 'Загрузить',
        monthlyReports: 'Отчеты платформы',
        refresh: 'Обновить',
        loading: 'Загрузка...',
        download: 'Скачать',
        delete: 'Удалить',
        confirmDelete: 'Подтверждение удаления',
        deleteConfirmText: 'Вы уверены, что хотите удалить этот отчёт?',
        cancel: 'Отмена',
        footerText: 'Система учёта отчётов',
        pleaseWait: 'Пожалуйста, подождите...',
        dataRows: 'Строк данных',
        updated: 'Обновлён',
        noReports: 'Нет созданных отчётов.',
        uploadFirst: 'Загрузите первый недельный файл.',
        tabReports: 'Отчеты платформы',
        tabViolations: 'Анализ нарушений',
        uploadViolations: 'Загрузка файла с нарушениями',
        violationsDescription: 'Загрузите Excel файл с данными о нарушениях. Система автоматически подсчитает количество каждого типа нарушения из столбца "qoidabuzarlik nomi".',
        reportName: 'Название отчета:',
        reportNameHint: 'Необязательно. Если не указано, будет создано автоматически',
        analyze: 'Анализировать',
        analysisResults: 'Результаты анализа',
        downloadText: 'Скачать TXT',
        totalViolations: 'Всего нарушений',
        uniqueTypes: 'Типов нарушений',
        mostCommon: 'Самое частое нарушение',
        textFormat: 'Текстовый отчет',
        savedViolationsReports: 'Сохранённые отчёты по нарушениям',
        violationsSubtitle: 'Анализ и статистика нарушений',
        compareFiles: 'Сравнение файлов',
        compareDescription: 'Загрузите два файла (Excel или текстовые) для сравнения. Система найдет записи, присутствующие в обоих файлах и уникальные для каждого.',
        file1Name: 'Название источника 1:',
        file2Name: 'Название источника 2:',
        file1: 'Файл 1:',
        file2: 'Файл 2:',
        monthName: 'Название месяца (необязательно):',
        compare: 'Сравнить',
        comparisonResults: 'Результаты сравнения',
        comparisonReport: 'Отчет сравнения',
        inBoth: 'В обоих файлах',
        mergeFiles: 'Объединение файлов',
        mergeDescription: 'Загрузите несколько файлов (Excel или текстовые) и укажите названия столбцов. Система соберет все данные из этих столбцов в один файл.',
        columnNames: 'Названия столбцов (через запятую):',
        columnNamesHint: 'Укажите названия столбцов, которые нужно извлечь из файлов',
        selectFiles: 'Выберите файлы (минимум 2):',
        mergeFilesHint: 'Можно выбрать несколько файлов одновременно',
        merge: 'Объединить',
        mergeResults: 'Результаты объединения',
        mergedData: 'Объединенные данные',
        downloadTXT: 'Скачать TXT',
        downloadExcel: 'Скачать Excel'
    },
    uz: {
        title: 'Hisobot platformasi',
        systemTitle: 'Hisobot platformasi',
        systemSubtitle: 'Hujjat aylanmasini avtomatlashtirish',
        uploadWeekly: 'Haftalik hisobotni yuklash',
        month: 'Oy:',
        year: 'Yil:',
        file: 'Fayl:',
        selectMonth: 'Tanlang',
        january: 'Yanvar',
        february: 'Fevral',
        march: 'Mart',
        april: 'Aprel',
        may: 'May',
        june: 'Iyun',
        july: 'Iyul',
        august: 'Avgust',
        september: 'Sentabr',
        october: 'Oktabr',
        november: 'Noyabr',
        december: 'Dekabr',
        supportedFormats: 'Qo\'llab-quvvatlanadigan formatlar: .xlsx, .xls',
        upload: 'Yuklash',
        monthlyReports: 'Platforma hisobotlari',
        refresh: 'Yangilash',
        loading: 'Yuklanmoqda...',
        download: 'Yuklab olish',
        delete: 'O\'chirish',
        confirmDelete: 'O\'chirishni tasdiqlash',
        deleteConfirmText: 'Ushbu hisobotni o\'chirishga ishonchingiz komilmi?',
        cancel: 'Bekor qilish',
        footerText: 'Hisobot tizimi',
        pleaseWait: 'Iltimos, kuting...',
        dataRows: 'Ma\'lumot qatorlari',
        updated: 'Yangilangan',
        noReports: 'Hisobotlar mavjud emas.',
        uploadFirst: 'Birinchi haftalik faylni yuklang.',
        tabReports: 'Platforma hisobotlari',
        tabViolations: 'Qoidabuzarliklar tahlili',
        uploadViolations: 'Qoidabuzarliklar faylini yuklash',
        violationsDescription: 'Qoidabuzarliklar ma\'lumotlari bilan Excel faylni yuklang. Tizim "qoidabuzarlik nomi" ustunidan har bir turdagi qoidabuzarliklar sonini avtomatik hisoblab chiqadi.',
        reportName: 'Hisobot nomi:',
        reportNameHint: 'Majburiy emas. Agar ko\'rsatilmagan bo\'lsa, avtomatik yaratiladi',
        analyze: 'Tahlil qilish',
        analysisResults: 'Tahlil natijalari',
        downloadText: 'TXT yuklab olish',
        totalViolations: 'Jami qoidabuzarliklar',
        uniqueTypes: 'Qoidabuzarlik turlari',
        mostCommon: 'Eng ko\'p qoidabuzarlik',
        textFormat: 'Matnli hisobot',
        savedViolationsReports: 'Saqlangan qoidabuzarliklar hisobotlari',
        violationsSubtitle: 'Qoidabuzarliklar tahlili va statistikasi',
        compareFiles: 'Fayllarni solishtirish',
        compareDescription: 'Solishtirish uchun ikkita fayl (Excel yoki matnli) yuklang. Tizim ikkala faylda ham mavjud bo\'lgan va har bir fayl uchun noyob yozuvlarni topadi.',
        file1Name: 'Manba 1 nomi:',
        file2Name: 'Manba 2 nomi:',
        file1: 'Fayl 1:',
        file2: 'Fayl 2:',
        monthName: 'Oy nomi (ixtiyoriy):',
        compare: 'Solishtirish',
        comparisonResults: 'Solishtirish natijalari',
        comparisonReport: 'Solishtirish hisoboti',
        inBoth: 'Ikkalasida ham',
        mergeFiles: 'Fayllarni birlashtirish',
        mergeDescription: 'Bir nechta fayllarni (Excel yoki matnli) yuklang va ustun nomlarini ko\'rsating. Tizim bu ustunlardagi barcha ma\'lumotlarni bitta faylga to\'playdi.',
        columnNames: 'Ustun nomlari (vergul bilan):',
        columnNamesHint: 'Fayllardan ajratib olinadigan ustun nomlarini ko\'rsating',
        selectFiles: 'Fayllarni tanlang (kamida 2 ta):',
        mergeFilesHint: 'Bir vaqtning o\'zida bir nechta faylni tanlash mumkin',
        merge: 'Birlashtirish',
        mergeResults: 'Birlashtirish natijalari',
        mergedData: 'Birlashtirilgan ma\'lumotlar',
        downloadTXT: 'TXT yuklab olish',
        downloadExcel: 'Excel yuklab olish'
    }
};

// Текущий язык
let currentLang = localStorage.getItem('lang') || 'ru';

// Функция смены языка
function setLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);
    document.documentElement.lang = lang;
    
    // Обновляем все элементы с data-i18n
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Обновляем активную кнопку языка
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });
    
    // Обновляем title страницы
    document.title = translations[lang].title;
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    // Устанавливаем язык
    setLanguage(currentLang);
    
    // Обработчики кнопок языка
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            setLanguage(this.getAttribute('data-lang'));
        });
    });
});

// Функция получения перевода
function t(key) {
    return translations[currentLang][key] || key;
}

