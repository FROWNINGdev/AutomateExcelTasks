import os
import io
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
from excel_processor import ExcelProcessor
from violations_processor import ViolationsProcessor
from comparison_processor import ComparisonProcessor
from merge_processor import MergeProcessor
from database import Database

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['TEMPLATE_FILE'] = os.path.join('static', 'file', 'Шаблон.xlsx')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Создаем необходимые папки
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Инициализируем БД
db = Database()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не выбран'}), 400
        
        file = request.files['file']
        month = request.form.get('month')
        year = request.form.get('year')
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Разрешены только файлы Excel (.xlsx, .xls)'}), 400
        
        if not month or not year:
            return jsonify({'error': 'Укажите месяц и год'}), 400
        
        # Проверяем наличие шаблона
        if not os.path.exists(app.config['TEMPLATE_FILE']):
            return jsonify({'error': 'Шаблон месячного отчета не найден. Загрузите шаблон.'}), 400
        
        # Сохраняем загруженный файл временно
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        weekly_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{timestamp}_{filename}')
        file.save(weekly_file_path)
        
        # Проверяем, есть ли уже месячный отчет в БД
        existing_report = db.get_monthly_report_file(int(month), int(year))
        existing_data = existing_report['file_data'] if existing_report else None
        
        # Обрабатываем файл
        processor = ExcelProcessor(template_path=app.config['TEMPLATE_FILE'])
        monthly_filename, file_data, rows_added = processor.process_weekly_file(
            weekly_file_path, month, year, existing_data
        )
        
        # Сохраняем в БД
        monthly_report_id = db.get_or_create_monthly_report(
            int(month), int(year), monthly_filename, file_data
        )
        db.add_weekly_upload(monthly_report_id, filename, weekly_file_path, rows_added)
        
        # Обновляем статистику
        stats = processor.get_monthly_stats(file_data)
        db.update_monthly_report_rows(monthly_report_id, stats['total_rows'])
        
        # Получаем статистику из БД
        db_stats = db.get_monthly_report_stats(int(month), int(year))
        
        # Удаляем временный файл
        os.remove(weekly_file_path)
        
        return jsonify({
            'success': True,
            'message_ru': f'Файл успешно обработан. Обновлено {rows_added} строк.',
            'message_uz': f'Fayl muvaffaqiyatli qayta ishlandi. {rows_added} ta qator yangilandi.',
            'monthly_file': monthly_filename,
            'stats': {
                'rows_updated': rows_added,
                'total_rows': stats['total_rows'],
                'uploads_count': db_stats['uploads_count'] if db_stats else 1
            }
        })
    
    except Exception as e:
        # Удаляем временный файл при ошибке
        if 'weekly_file_path' in locals() and os.path.exists(weekly_file_path):
            os.remove(weekly_file_path)
        return jsonify({'error': f'Ошибка обработки файла: {str(e)}'}), 500

@app.route('/download/<int:month>/<int:year>')
def download_file(month, year):
    try:
        report = db.get_monthly_report_file(month, year)
        
        if not report:
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Создаем файл из БД
        file_stream = io.BytesIO(report['file_data'])
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=report['file_name'],
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка скачивания файла: {str(e)}'}), 500

@app.route('/monthly-reports')
def get_monthly_reports():
    try:
        reports = db.get_all_monthly_reports()
        
        # Названия месяцев для отображения
        month_names = {
            1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
            5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
            9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
        }
        
        files = []
        for report in reports:
            files.append({
                'month': report['month'],
                'year': report['year'],
                'display_name': f"{month_names.get(report['month'], report['month'])} {report['year']}",
                'size': report['file_size'],
                'created': report['created_at'],
                'updated': report['updated_at'],
                'total_rows': report['total_rows']
            })
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': f'Ошибка получения списка файлов: {str(e)}'}), 500

@app.route('/history/<int:month>/<int:year>')
def get_upload_history(month, year):
    try:
        uploads = db.get_weekly_uploads(month, year)
        return jsonify({'uploads': uploads})
    except Exception as e:
        return jsonify({'error': f'Ошибка получения истории: {str(e)}'}), 500

@app.route('/stats/<int:month>/<int:year>')
def get_stats(month, year):
    try:
        stats = db.get_monthly_report_stats(month, year)
        if stats:
            return jsonify({'stats': stats})
        else:
            return jsonify({'error': 'Отчет не найден'}), 404
    except Exception as e:
        return jsonify({'error': f'Ошибка получения статистики: {str(e)}'}), 500

@app.route('/delete/<int:month>/<int:year>', methods=['DELETE'])
def delete_report(month, year):
    try:
        # Проверяем существование
        report = db.get_monthly_report_file(month, year)
        if not report:
            return jsonify({'error': 'Файл не найден'}), 404
        
        # Удаляем из БД
        db.delete_monthly_report(month, year)
        
        return jsonify({'success': True, 'message': 'Файл успешно удалён'})
    except Exception as e:
        return jsonify({'error': f'Ошибка удаления файла: {str(e)}'}), 500

# ========== ENDPOINTS ДЛЯ РАБОТЫ С НАРУШЕНИЯМИ ==========

@app.route('/violations/upload', methods=['POST'])
def upload_violations():
    """Загрузка и обработка файла с нарушениями"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Файл не выбран'}), 400
        
        file = request.files['file']
        report_name = request.form.get('report_name', '').strip()
        
        if file.filename == '':
            return jsonify({'error': 'Файл не выбран'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Разрешены только файлы Excel (.xlsx, .xls)'}), 400
        
        if not report_name:
            # Генерируем имя отчета по дате
            report_name = f"Отчет {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        
        # Сохраняем файл временно
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'violations_{timestamp}_{filename}')
        file.save(file_path)
        
        # Обрабатываем файл
        processor = ViolationsProcessor()
        violations_data = processor.process_violations_file(file_path)
        
        # Сохраняем в БД
        report_id = db.save_violations_report(
            report_name=report_name,
            original_filename=filename,
            file_path=file_path,
            violations_data=violations_data,
            text_output=violations_data['text_output']
        )
        
        # Получаем статистику
        stats = processor.get_statistics(violations_data['violations'])
        
        # Удаляем временный файл
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'message_ru': f'Файл успешно обработан. Найдено {violations_data["total"]} нарушений.',
            'message_uz': f'Fayl muvaffaqiyatli qayta ishlandi. {violations_data["total"]} ta qoidabuzarlik topildi.',
            'report_id': report_id,
            'report_name': report_name,
            'stats': stats,
            'violations': violations_data['violations'][:10],  # Первые 10 для превью
            'text_output': violations_data['text_output']
        })
    
    except Exception as e:
        # Удаляем временный файл при ошибке
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'Ошибка обработки файла: {str(e)}'}), 500

@app.route('/violations/reports')
def get_violations_reports():
    """Получить список всех отчетов по нарушениям"""
    try:
        reports = db.get_all_violations_reports()
        return jsonify({'reports': reports})
    except Exception as e:
        return jsonify({'error': f'Ошибка получения списка отчетов: {str(e)}'}), 500

@app.route('/violations/report/<int:report_id>')
def get_violations_report_details(report_id):
    """Получить детали отчета по нарушениям"""
    try:
        report = db.get_violations_report(report_id)
        if not report:
            return jsonify({'error': 'Отчет не найден'}), 404
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': f'Ошибка получения отчета: {str(e)}'}), 500

@app.route('/violations/download/<int:report_id>')
def download_violations_report(report_id):
    """Скачать отчет по нарушениям в текстовом формате"""
    try:
        # Получаем язык из параметра запроса
        language = request.args.get('lang', 'ru')
        
        report = db.get_violations_report(report_id)
        if not report:
            return jsonify({'error': 'Отчет не найден'}), 404
        
        # Создаем текстовый файл
        processor = ViolationsProcessor()
        text_content, filename = processor.export_to_text({
            'violations': report['violations'],
            'total': report['total_violations'],
            'unique_violations': report['unique_types'],
            'text_output': report['text_output']
        }, language=language)
        
        # Отправляем файл
        file_stream = io.BytesIO(text_content)
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain; charset=utf-8'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка скачивания отчета: {str(e)}'}), 500

@app.route('/violations/delete/<int:report_id>', methods=['DELETE'])
def delete_violations_report(report_id):
    """Удалить отчет по нарушениям"""
    try:
        report = db.get_violations_report(report_id)
        if not report:
            return jsonify({'error': 'Отчет не найден'}), 404
        
        db.delete_violations_report(report_id)
        
        return jsonify({'success': True, 'message': 'Отчет успешно удалён'})
    except Exception as e:
        return jsonify({'error': f'Ошибка удаления отчета: {str(e)}'}), 500

# ========== СРАВНЕНИЕ ФАЙЛОВ ==========

@app.route('/comparison/compare', methods=['POST'])
def compare_files():
    """Сравнение двух файлов"""
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Необходимо загрузить оба файла'}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        file1_name = request.form.get('file1_name', 'Файл 1')
        file2_name = request.form.get('file2_name', 'Файл 2')
        month_name = request.form.get('month_name', '')
        language = request.form.get('language', 'uz')
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({'error': 'Выберите оба файла'}), 400
        
        # Сохраняем файлы временно
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file1_path = os.path.join(app.config['UPLOAD_FOLDER'], f'compare1_{timestamp}_{secure_filename(file1.filename)}')
        file2_path = os.path.join(app.config['UPLOAD_FOLDER'], f'compare2_{timestamp}_{secure_filename(file2.filename)}')
        
        file1.save(file1_path)
        file2.save(file2_path)
        
        # Сравниваем файлы
        processor = ComparisonProcessor()
        result = processor.compare_files(
            file1_path, 
            file2_path, 
            file1_name, 
            file2_name
        )
        
        # Форматируем вывод на нужном языке
        result['text_output'] = processor._format_comparison_output(result, language)
        
        # Добавляем название месяца
        if month_name:
            result['month_name'] = month_name
        
        # Удаляем временные файлы
        os.remove(file1_path)
        os.remove(file2_path)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        # Удаляем временные файлы при ошибке
        if 'file1_path' in locals() and os.path.exists(file1_path):
            os.remove(file1_path)
        if 'file2_path' in locals() and os.path.exists(file2_path):
            os.remove(file2_path)
        return jsonify({'error': f'Ошибка сравнения: {str(e)}'}), 500

@app.route('/comparison/download-differences', methods=['POST'])
def download_comparison_differences():
    """Скачать 2 файла с различиями (как в compare_month.py --export)"""
    try:
        comparison_data = request.json.get('comparison_data')
        file_type = request.json.get('file_type', 'file1')  # file1 или file2
        
        if not comparison_data:
            return jsonify({'error': 'Нет данных для экспорта'}), 400
        
        processor = ComparisonProcessor()
        file1_content, file1_name, file2_content, file2_name = processor.export_differences(comparison_data)
        
        # Отправляем нужный файл
        if file_type == 'file1':
            file_stream = io.BytesIO(file1_content)
            filename = file1_name
        else:
            file_stream = io.BytesIO(file2_content)
            filename = file2_name
        
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain; charset=utf-8'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка экспорта: {str(e)}'}), 500

# ========== ОБЪЕДИНЕНИЕ ФАЙЛОВ ==========

@app.route('/merge/process', methods=['POST'])
def merge_files_endpoint():
    """Объединение нескольких файлов по указанным столбцам"""
    try:
        # Получаем файлы
        files = request.files.getlist('files[]')
        if not files or len(files) < 2:
            return jsonify({'error': 'Необходимо загрузить минимум 2 файла'}), 400
        
        # Получаем названия столбцов
        column_names_str = request.form.get('column_names', 'doc_num')
        column_names = [col.strip() for col in column_names_str.split(',') if col.strip()]
        
        if not column_names:
            return jsonify({'error': 'Укажите хотя бы одно название столбца'}), 400
        
        language = request.form.get('language', 'ru')
        
        # Сохраняем файлы временно
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        files_data = []
        temp_files = []
        
        for i, file in enumerate(files):
            if file.filename == '':
                continue
            
            file_path = os.path.join(
                app.config['UPLOAD_FOLDER'], 
                f'merge_{timestamp}_{i}_{secure_filename(file.filename)}'
            )
            file.save(file_path)
            temp_files.append(file_path)
            
            files_data.append({
                'file': file_path,
                'name': file.filename
            })
        
        if len(files_data) < 2:
            # Удаляем временные файлы
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return jsonify({'error': 'Необходимо загрузить минимум 2 корректных файла'}), 400
        
        # Объединяем файлы
        processor = MergeProcessor()
        result = processor.merge_files(files_data, column_names)
        
        # Форматируем вывод на нужном языке
        # Для веб-интерфейса - ограничиваем предпросмотр до 1000 записей
        result['text_output'] = processor._format_merged_output(result, language, limit_preview=1000)
        # Для скачивания - сохраняем полный вывод
        result['text_output_full'] = processor._format_merged_output(result, language, limit_preview=0)
        
        # Удаляем временные файлы
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return jsonify({
            'success': True,
            'result': result
        })
    
    except Exception as e:
        # Удаляем временные файлы при ошибке
        if 'temp_files' in locals():
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        return jsonify({'error': f'Ошибка объединения: {str(e)}'}), 500

@app.route('/merge/download-txt', methods=['POST'])
def download_merged_txt():
    """Скачать объединенные данные как TXT"""
    try:
        merged_data = request.json.get('merged_data')
        language = request.json.get('language', 'ru')
        
        if not merged_data:
            return jsonify({'error': 'Нет данных для экспорта'}), 400
        
        processor = MergeProcessor()
        text_content, filename = processor.export_merged_data(merged_data, language=language)
        
        file_stream = io.BytesIO(text_content)
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain; charset=utf-8'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка экспорта: {str(e)}'}), 500

@app.route('/merge/download-excel', methods=['POST'])
def download_merged_excel():
    """Скачать объединенные данные как Excel"""
    try:
        merged_data = request.json.get('merged_data')
        
        if not merged_data:
            return jsonify({'error': 'Нет данных для экспорта'}), 400
        
        processor = MergeProcessor()
        excel_content, filename = processor.export_to_excel(merged_data)
        
        file_stream = io.BytesIO(excel_content)
        file_stream.seek(0)
        
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({'error': f'Ошибка экспорта: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    app.run(debug=True, host='0.0.0.0', port=port)
