// Показать анимацию загрузки
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

// Скрыть анимацию загрузки
function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

document.addEventListener('DOMContentLoaded', function() {
    // ========== УПРАВЛЕНИЕ БОКОВОЙ ПАНЕЛЬЮ ==========
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');
    
    // Заголовки для разделов
    const pageTitles = {
        'reports': {
            'ru': 'Отчеты платформы',
            'uz': 'Platforma hisobotlari'
        },
        'violations': {
            'ru': 'Анализ нарушений',
            'uz': 'Qoidabuzarliklar tahlili'
        }
    };
    
    const pageSubtitles = {
        'reports': {
            'ru': 'Консолидация недельных отчетов',
            'uz': 'Haftalik hisobotlarni birlashtirish'
        },
        'violations': {
            'ru': 'Анализ и статистика нарушений',
            'uz': 'Qoidabuzarliklar tahlili va statistikasi'
        }
    };
    
    navItems.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Убираем активный класс со всех элементов
            navItems.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Активируем выбранный раздел
            this.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
            
            // Обновляем заголовок страницы
            if (pageTitles[targetTab]) {
                pageTitle.textContent = pageTitles[targetTab][currentLang];
                pageTitle.setAttribute('data-i18n', targetTab === 'reports' ? 'tabReports' : 'tabViolations');
            }
            
            if (pageSubtitles[targetTab]) {
                pageSubtitle.textContent = pageSubtitles[targetTab][currentLang];
            }
            
            // Загружаем данные для вкладки
            if (targetTab === 'violations') {
                loadViolationsReports();
            } else {
                loadReports();
            }
        });
    });
    
    // ========== ВКЛАДКА: МЕСЯЧНЫЕ ОТЧЁТЫ ==========
    const uploadForm = document.getElementById('uploadForm');
    const monthSelect = document.getElementById('month');
    const yearInput = document.getElementById('year');
    const fileInput = document.getElementById('fileInput');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const message = document.getElementById('message');
    const reportsContainer = document.getElementById('reportsContainer');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Устанавливаем текущий год и месяц
    const now = new Date();
    yearInput.value = now.getFullYear();
    monthSelect.value = now.getMonth() + 1;
    
    // Загружаем список отчётов
    loadReports();
    
    // ========== ВКЛАДКА: НАРУШЕНИЯ ==========
    const uploadViolationsForm = document.getElementById('uploadViolationsForm');
    const violationsFileInput = document.getElementById('violationsFileInput');
    const reportNameInput = document.getElementById('reportName');
    const submitViolationsBtn = document.getElementById('submitViolationsBtn');
    const btnViolationsText = document.getElementById('btnViolationsText');
    const btnViolationsLoader = document.getElementById('btnViolationsLoader');
    const violationsMessage = document.getElementById('violationsMessage');
    const violationsReportsContainer = document.getElementById('violationsReportsContainer');
    const refreshViolationsBtn = document.getElementById('refreshViolationsBtn');
    const violationsResultSection = document.getElementById('violationsResultSection');
    const downloadViolationsTextBtn = document.getElementById('downloadViolationsTextBtn');
    
    let currentViolationsReportId = null;
    
    // Обработчик загрузки нарушений
    uploadViolationsForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = violationsFileInput.files[0];
        const reportName = reportNameInput.value.trim();
        
        if (!file) {
            showViolationsMessage('Выберите файл', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        if (reportName) {
            formData.append('report_name', reportName);
        }
        
        // Блокируем форму и показываем анимацию
        submitViolationsBtn.disabled = true;
        btnViolationsText.style.display = 'none';
        btnViolationsLoader.style.display = 'inline-block';
        showLoading();
        
        try {
            const response = await fetch('/violations/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                const msg = currentLang === 'uz' ? data.message_uz : data.message_ru;
                showViolationsMessage(msg || data.message, 'success');
                uploadViolationsForm.reset();
                
                // Показываем результаты
                currentViolationsReportId = data.report_id;
                displayViolationsResults(data);
                
                // Обновляем список отчетов
                loadViolationsReports();
            } else {
                const errorMsg = currentLang === 'uz' ? 'Yuklashda xatolik' : 'Ошибка загрузки';
                showViolationsMessage(data.error || errorMsg, 'error');
            }
        } catch (error) {
            showViolationsMessage('Ошибка соединения с сервером', 'error');
        } finally {
            submitViolationsBtn.disabled = false;
            btnViolationsText.style.display = 'inline';
            btnViolationsLoader.style.display = 'none';
            hideLoading();
        }
    });
    
    // Обновление списка отчетов по нарушениям
    refreshViolationsBtn.addEventListener('click', loadViolationsReports);
    
    // Скачивание текстового отчета
    downloadViolationsTextBtn.addEventListener('click', function() {
        if (currentViolationsReportId) {
            window.location.href = `/violations/download/${currentViolationsReportId}?lang=${currentLang}`;
        }
    });
    
    // ========== СРАВНЕНИЕ ФАЙЛОВ ==========
    const compareFilesForm = document.getElementById('compareFilesForm');
    const compareFile1 = document.getElementById('compareFile1');
    const compareFile2 = document.getElementById('compareFile2');
    const file1Name = document.getElementById('file1Name');
    const file2Name = document.getElementById('file2Name');
    const monthNameCompare = document.getElementById('monthNameCompare');
    const compareBtn = document.getElementById('compareBtn');
    const compareBtnText = document.getElementById('compareBtnText');
    const compareBtnLoader = document.getElementById('compareBtnLoader');
    const compareMessage = document.getElementById('compareMessage');
    const comparisonResultSection = document.getElementById('comparisonResultSection');
    const downloadDiff1Btn = document.getElementById('downloadDiff1Btn');
    const downloadDiff2Btn = document.getElementById('downloadDiff2Btn');
    
    let currentComparisonData = null;
    
    compareFilesForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const f1 = compareFile1.files[0];
        const f2 = compareFile2.files[0];
        
        if (!f1 || !f2) {
            showCompareMessage('Выберите оба файла', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file1', f1);
        formData.append('file2', f2);
        formData.append('file1_name', file1Name.value || 'Файл 1');
        formData.append('file2_name', file2Name.value || 'Файл 2');
        formData.append('month_name', monthNameCompare.value);
        formData.append('language', currentLang);
        
        // Блокируем форму
        compareBtn.disabled = true;
        compareBtnText.style.display = 'none';
        compareBtnLoader.style.display = 'inline-block';
        showLoading();
        
        try {
            const response = await fetch('/comparison/compare', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showCompareMessage('Файлы успешно сравнены', 'success');
                currentComparisonData = data.result;
                displayComparisonResults(data.result);
            } else {
                showCompareMessage(data.error || 'Ошибка сравнения', 'error');
            }
        } catch (error) {
            showCompareMessage('Ошибка соединения с сервером', 'error');
        } finally {
            compareBtn.disabled = false;
            compareBtnText.style.display = 'inline';
            compareBtnLoader.style.display = 'none';
            hideLoading();
        }
    });
    
    // ========== ОБЪЕДИНЕНИЕ ФАЙЛОВ ==========
    const mergeFilesForm = document.getElementById('mergeFilesForm');
    const mergeFiles = document.getElementById('mergeFiles');
    const columnNames = document.getElementById('columnNames');
    const selectedFilesList = document.getElementById('selectedFilesList');
    const mergeBtn = document.getElementById('mergeBtn');
    const mergeBtnText = document.getElementById('mergeBtnText');
    const mergeBtnLoader = document.getElementById('mergeBtnLoader');
    const mergeMessage = document.getElementById('mergeMessage');
    const mergeResultSection = document.getElementById('mergeResultSection');
    const downloadMergedTextBtn = document.getElementById('downloadMergedTextBtn');
    const downloadMergedExcelBtn = document.getElementById('downloadMergedExcelBtn');
    
    let currentMergedData = null;
    
    // Показываем выбранные файлы
    mergeFiles.addEventListener('change', function() {
        const files = Array.from(this.files);
        if (files.length > 0) {
            selectedFilesList.classList.add('has-files');
            selectedFilesList.innerHTML = files.map(file => `
                <div class="selected-file-item">
                    <svg class="selected-file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <span class="selected-file-name">${file.name}</span>
                    <span class="selected-file-size">${formatFileSize(file.size)}</span>
                </div>
            `).join('');
        } else {
            selectedFilesList.classList.remove('has-files');
            selectedFilesList.innerHTML = '';
        }
    });
    
    mergeFilesForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const files = Array.from(mergeFiles.files);
        
        if (files.length < 2) {
            showMergeMessage('Выберите минимум 2 файла', 'error');
            return;
        }
        
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files[]', file);
        });
        formData.append('column_names', columnNames.value);
        formData.append('language', currentLang);
        
        // Блокируем форму
        mergeBtn.disabled = true;
        mergeBtnText.style.display = 'none';
        mergeBtnLoader.style.display = 'inline-block';
        showLoading();
        
        try {
            const response = await fetch('/merge/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showMergeMessage('Файлы успешно объединены', 'success');
                currentMergedData = data.result;
                displayMergeResults(data.result);
            } else {
                showMergeMessage(data.error || 'Ошибка объединения', 'error');
            }
        } catch (error) {
            showMergeMessage('Ошибка соединения с сервером', 'error');
        } finally {
            mergeBtn.disabled = false;
            mergeBtnText.style.display = 'inline';
            mergeBtnLoader.style.display = 'none';
            hideLoading();
        }
    });
    
    // Скачивание результатов
    downloadMergedTextBtn.addEventListener('click', async function() {
        if (!currentMergedData) return;
        
        try {
            const response = await fetch('/merge/download-txt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    merged_data: currentMergedData,
                    language: currentLang
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `merged_${Date.now()}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            showMergeMessage('Ошибка скачивания', 'error');
        }
    });
    
    downloadMergedExcelBtn.addEventListener('click', async function() {
        if (!currentMergedData) return;
        
        try {
            const response = await fetch('/merge/download-excel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    merged_data: currentMergedData
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `merged_${Date.now()}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            showMergeMessage('Ошибка скачивания', 'error');
        }
    });
    
    // Скачивание файлов с различиями
    downloadDiff1Btn.addEventListener('click', async function() {
        if (!currentComparisonData) return;
        
        try {
            const response = await fetch('/comparison/download-differences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    comparison_data: currentComparisonData,
                    file_type: 'file1'
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${currentComparisonData.file1_name}_minus_${currentComparisonData.file2_name}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            showCompareMessage('Ошибка скачивания', 'error');
        }
    });
    
    downloadDiff2Btn.addEventListener('click', async function() {
        if (!currentComparisonData) return;
        
        try {
            const response = await fetch('/comparison/download-differences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    comparison_data: currentComparisonData,
                    file_type: 'file2'
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${currentComparisonData.file2_name}_minus_${currentComparisonData.file1_name}.txt`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }
        } catch (error) {
            showCompareMessage('Ошибка скачивания', 'error');
        }
    });
    
    // Обработчик загрузки
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        const month = monthSelect.value;
        const year = yearInput.value;
        
        if (!file || !month || !year) {
            showMessage('Заполните все поля', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('month', month);
        formData.append('year', year);
        
        // Блокируем форму и показываем анимацию
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        showLoading();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                const msg = currentLang === 'uz' ? data.message_uz : data.message_ru;
                showMessage(msg || data.message, 'success');
                uploadForm.reset();
                yearInput.value = now.getFullYear();
                monthSelect.value = now.getMonth() + 1;
                loadReports();
            } else {
                const errorMsg = currentLang === 'uz' ? 'Yuklashda xatolik' : 'Ошибка загрузки';
                showMessage(data.error || errorMsg, 'error');
            }
        } catch (error) {
            showMessage('Ошибка соединения с сервером', 'error');
        } finally {
            submitBtn.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            hideLoading();
        }
    });
    
    // Обновление списка
    refreshBtn.addEventListener('click', loadReports);
    
    // Функции
    async function loadReports() {
        reportsContainer.innerHTML = '<div class="loading">Загрузка...</div>';
        
        try {
            const response = await fetch('/monthly-reports');
            const data = await response.json();
            
            if (response.ok && data.files && data.files.length > 0) {
                const reportsHTML = data.files.map(file => `
                    <div class="report-item">
                        <div class="excel-icon">
                            <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect width="40" height="40" rx="4" fill="#217346"/>
                                <path d="M24 10H12C11.4477 10 11 10.4477 11 11V29C11 29.5523 11.4477 30 12 30H28C28.5523 30 29 29.5523 29 29V15L24 10Z" fill="#185C37"/>
                                <path d="M24 10V14C24 14.5523 24.4477 15 25 15H29L24 10Z" fill="#21A366"/>
                                <path d="M17 18L20 22L17 26M23 18L20 22L23 26" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </div>
                        <div class="report-info">
                            <div class="report-name">${file.display_name}</div>
                            <div class="report-meta">
                                <span data-i18n="dataRows">${t('dataRows')}</span>: ${file.total_rows} | 
                                <span data-i18n="updated">${t('updated')}</span>: ${formatDate(file.updated)}
                            </div>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-download btn-small" onclick="downloadFile(${file.month}, ${file.year})">
                                <span data-i18n="download">${t('download')}</span>
                            </button>
                            <button class="btn btn-danger btn-small" onclick="confirmDelete(${file.month}, ${file.year}, '${file.display_name}')">
                                <span data-i18n="delete">${t('delete')}</span>
                            </button>
                        </div>
                    </div>
                `).join('');
                
                reportsContainer.innerHTML = `<div class="reports-list">${reportsHTML}</div>`;
            } else {
                reportsContainer.innerHTML = `
                    <div class="empty-state">
                        <span data-i18n="noReports">${t('noReports')}</span><br>
                        <span data-i18n="uploadFirst">${t('uploadFirst')}</span>
                    </div>
                `;
            }
        } catch (error) {
            reportsContainer.innerHTML = `
                <div class="empty-state">
                    ${currentLang === 'uz' ? 'Xatolik' : 'Ошибка загрузки списка отчётов'}
                </div>
            `;
        }
    }
    
    function showMessage(text, type) {
        message.textContent = text;
        message.className = `message ${type}`;
        
        setTimeout(() => {
            message.className = 'message';
        }, 5000);
    }
    
    function formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleString('ru-RU', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // Глобальные функции
    window.downloadFile = function(month, year) {
        window.location.href = `/download/${month}/${year}`;
    };
    
    let fileToDelete = null;
    
    window.confirmDelete = function(month, year, displayName) {
        fileToDelete = {month, year};
        document.getElementById('deleteFileName').textContent = displayName;
        document.getElementById('confirmModal').style.display = 'block';
    };
    
    window.closeConfirmModal = function() {
        document.getElementById('confirmModal').style.display = 'none';
        fileToDelete = null;
    };
    
    document.getElementById('confirmDeleteBtn').addEventListener('click', async function() {
        if (!fileToDelete) return;
        
        try {
            const response = await fetch(`/delete/${fileToDelete.month}/${fileToDelete.year}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showMessage(data.message, 'success');
                closeConfirmModal();
                loadReports();
            } else {
                showMessage(data.error || 'Ошибка удаления', 'error');
            }
        } catch (error) {
            showMessage('Ошибка соединения с сервером', 'error');
        }
    });
    
    // Закрытие модального окна по клику вне него
    window.onclick = function(event) {
        const confirmModal = document.getElementById('confirmModal');
        
        if (event.target === confirmModal) {
            closeConfirmModal();
        }
    };
    
    // ========== ФУНКЦИИ ДЛЯ НАРУШЕНИЙ ==========
    
    async function loadViolationsReports() {
        violationsReportsContainer.innerHTML = '<div class="loading">Загрузка...</div>';
        
        try {
            const response = await fetch('/violations/reports');
            const data = await response.json();
            
            if (response.ok && data.reports && data.reports.length > 0) {
                const reportsHTML = data.reports.map(report => `
                    <div class="violation-report-item">
                        <div class="violation-icon">
                            ⚠
                        </div>
                        <div class="violation-info">
                            <div class="violation-name">${report.report_name}</div>
                            <div class="violation-meta">
                                ${report.filename} | ${formatDate(report.processed_at)}
                            </div>
                            <div class="violation-stats">
                                <div class="violation-stat">
                                    <span>Всего:</span> <strong>${report.total_violations}</strong>
                                </div>
                                <div class="violation-stat">
                                    <span>Типов:</span> <strong>${report.unique_types}</strong>
                                </div>
                            </div>
                        </div>
                        <div class="report-actions">
                            <button class="btn btn-download btn-small" onclick="viewViolationsReport(${report.id})">
                                <span>Просмотр</span>
                            </button>
                            <button class="btn btn-success btn-small" onclick="downloadViolationsText(${report.id})">
                                <span>TXT</span>
                            </button>
                            <button class="btn btn-danger btn-small" onclick="deleteViolationsReport(${report.id}, '${report.report_name}')">
                                <span data-i18n="delete">${t('delete')}</span>
                            </button>
                        </div>
                    </div>
                `).join('');
                
                violationsReportsContainer.innerHTML = `<div class="reports-list">${reportsHTML}</div>`;
            } else {
                violationsReportsContainer.innerHTML = `
                    <div class="empty-state">
                        <span>Нет отчётов по нарушениям</span><br>
                        <span>Загрузите первый файл для анализа</span>
                    </div>
                `;
            }
        } catch (error) {
            violationsReportsContainer.innerHTML = `
                <div class="empty-state">
                    ${currentLang === 'uz' ? 'Xatolik' : 'Ошибка загрузки списка отчётов'}
                </div>
            `;
        }
    }
    
    function displayViolationsResults(data) {
        // Показываем секцию результатов
        violationsResultSection.style.display = 'block';
        
        // Убираем collapsed класс если есть
        violationsResultSection.classList.remove('collapsed');
        
        // Функция форматирования с пробелами
        function formatWithSpaces(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        }
        
        // Обновляем статистику
        document.getElementById('totalViolations').textContent = formatWithSpaces(data.stats.total_violations);
        document.getElementById('uniqueTypes').textContent = data.stats.unique_types;
        
        // Обновляем "Самое частое" с полным текстом в title
        const mostCommonEl = document.getElementById('mostCommon');
        if (data.stats.most_common) {
            const mostCommonText = data.stats.most_common.violation_text;
            mostCommonEl.textContent = mostCommonText;
            mostCommonEl.setAttribute('title', mostCommonText); // Полный текст при наведении
        } else {
            mostCommonEl.textContent = '-';
            mostCommonEl.removeAttribute('title');
        }
        
        // Показываем текстовый вывод
        document.getElementById('textOutput').textContent = data.text_output;
        
        // Прокручиваем к результатам
        violationsResultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function showViolationsMessage(text, type) {
        violationsMessage.textContent = text;
        violationsMessage.className = `message ${type}`;
        
        setTimeout(() => {
            violationsMessage.className = 'message';
        }, 5000);
    }
    
    function showCompareMessage(text, type) {
        compareMessage.textContent = text;
        compareMessage.className = `message ${type}`;
        
        setTimeout(() => {
            compareMessage.className = 'message';
        }, 5000);
    }
    
    function displayComparisonResults(result) {
        // Показываем секцию результатов
        comparisonResultSection.style.display = 'block';
        
        // Убираем collapsed класс если есть
        comparisonResultSection.classList.remove('collapsed');
        
        // Функция форматирования с пробелами (как в примере: 1 070 812)
        function formatWithSpaces(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        }
        
        // Обновляем названия файлов и статистику
        document.getElementById('file1NameLabel').textContent = result.file1_name;
        document.getElementById('file2NameLabel').textContent = result.file2_name;
        document.getElementById('file1Total').textContent = formatWithSpaces(result.file1_total);
        document.getElementById('file2Total').textContent = formatWithSpaces(result.file2_total);
        document.getElementById('inBoth').textContent = formatWithSpaces(result.in_both);
        
        // Обновляем подписи на кнопках скачивания
        const downloadDiff1Span = downloadDiff1Btn.querySelector('span');
        const downloadDiff2Span = downloadDiff2Btn.querySelector('span');
        if (downloadDiff1Span) {
            downloadDiff1Span.textContent = result.file1_name;
        }
        if (downloadDiff2Span) {
            downloadDiff2Span.textContent = result.file2_name;
        }
        
        // Обновляем tooltips
        downloadDiff1Btn.setAttribute('title', `Скачать: ${result.file1_name} minus ${result.file2_name} (${formatWithSpaces(result.only_in_file1)} записей)`);
        downloadDiff2Btn.setAttribute('title', `Скачать: ${result.file2_name} minus ${result.file1_name} (${formatWithSpaces(result.only_in_file2)} записей)`);
        
        // Показываем текстовый вывод
        document.getElementById('comparisonOutput').textContent = result.text_output;
        
        // Прокручиваем к результатам
        comparisonResultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function showMergeMessage(text, type) {
        mergeMessage.textContent = text;
        mergeMessage.className = `message ${type}`;
        
        setTimeout(() => {
            mergeMessage.className = 'message';
        }, 5000);
    }
    
    function displayMergeResults(result) {
        // Показываем секцию результатов
        mergeResultSection.style.display = 'block';
        
        // Убираем collapsed класс если есть
        mergeResultSection.classList.remove('collapsed');
        
        // Функция форматирования с пробелами
        function formatWithSpaces(num) {
            return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
        }
        
        // Создаем статистику по файлам
        const statsHTML = `
            <div class="stats-grid">
                ${result.file_stats.map((stat, index) => `
                    <div class="stat-card stat-${index % 3 === 0 ? 'primary' : index % 3 === 1 ? 'secondary' : 'accent'}">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                            </svg>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">${stat.name}</div>
                            <div class="stat-value">${formatWithSpaces(stat.total_rows)}</div>
                            <div class="stat-meta">${stat.columns_found.join(', ')}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="merge-summary">
                <h4>${currentLang === 'uz' ? 'Umumiy natijalar:' : 'Общие результаты:'}</h4>
                ${Object.entries(result.total_unique_records).map(([col, count]) => `
                    <div class="summary-item">
                        <span class="summary-label">${col}:</span>
                        <span class="summary-value">${formatWithSpaces(count)} ${currentLang === 'uz' ? 'noyob yozuv' : 'уникальных записей'}</span>
                    </div>
                `).join('')}
            </div>
        `;
        
        document.getElementById('mergeStatsContainer').innerHTML = statsHTML;
        
        // Показываем текстовый вывод
        document.getElementById('mergeOutput').textContent = result.text_output;
        
        // Прокручиваем к результатам
        mergeResultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Глобальные функции для нарушений
    window.viewViolationsReport = async function(reportId) {
        showLoading();
        try {
            const response = await fetch(`/violations/report/${reportId}`);
            const data = await response.json();
            
            if (response.ok) {
                currentViolationsReportId = reportId;
                
                // Формируем данные для отображения
                const displayData = {
                    stats: {
                        total_violations: data.total_violations,
                        unique_types: data.unique_types,
                        most_common: data.violations && data.violations.length > 0 
                            ? { violation_text: data.violations[0].violation_text }
                            : null
                    },
                    text_output: data.text_output
                };
                
                displayViolationsResults(displayData);
            }
        } catch (error) {
            showViolationsMessage('Ошибка загрузки отчета', 'error');
        } finally {
            hideLoading();
        }
    };
    
    window.downloadViolationsText = function(reportId) {
        window.location.href = `/violations/download/${reportId}?lang=${currentLang}`;
    };
    
    window.deleteViolationsReport = async function(reportId, reportName) {
        if (!confirm(`Удалить отчет "${reportName}"?`)) {
            return;
        }
        
        showLoading();
        try {
            const response = await fetch(`/violations/delete/${reportId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                showViolationsMessage(data.message, 'success');
                loadViolationsReports();
                
                // Скрываем результаты, если удален текущий отчет
                if (currentViolationsReportId === reportId) {
                    violationsResultSection.style.display = 'none';
                    currentViolationsReportId = null;
                }
            } else {
                showViolationsMessage(data.error || 'Ошибка удаления', 'error');
            }
        } catch (error) {
            showViolationsMessage('Ошибка соединения с сервером', 'error');
        } finally {
            hideLoading();
        }
    };
});
