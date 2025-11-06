"""
Процессор для сравнения двух файлов
ИСПОЛЬЗУЕТ функции из compare_month.py напрямую (без дублирования!)
"""

import os
import tempfile
import io
from datetime import datetime
from compare_month import read_pochta_txts, read_asbt_csv, read_telecom_excels, _write_uids_txt

class ComparisonProcessor:
    """
    Обертка над compare_month.py для использования в веб-приложении
    Вся логика чтения и сравнения - из вашего скрипта!
    """
    
    def compare_files(self, file1, file2, file1_name, file2_name, column_name='doc_num'):
        """
        Сравнивает два файла используя функции из compare_month.py
        
        Args:
            file1: первый файл (file object из Flask)
            file2: второй файл (file object из Flask)
            file1_name: название источника (Pochta, Telecom, ASBT)
            file2_name: название источника
            column_name: не используется (определяется автоматически по типу файла)
            
        Returns:
            dict с результатами сравнения (точно как в compare_month.py)
        """
        try:
            # Создаем временные директории для каждого файла
            with tempfile.TemporaryDirectory() as tmpdir:
                dir1 = os.path.join(tmpdir, 'source1')
                dir2 = os.path.join(tmpdir, 'source2')
                os.makedirs(dir1, exist_ok=True)
                os.makedirs(dir2, exist_ok=True)
                
                # Сохраняем файлы с правильными расширениями
                file1_ext = os.path.splitext(file1.filename)[1].lower() if hasattr(file1, 'filename') else '.txt'
                file2_ext = os.path.splitext(file2.filename)[1].lower() if hasattr(file2, 'filename') else '.txt'
                
                file1_path = os.path.join(dir1, f'file1{file1_ext}')
                file2_path = os.path.join(dir2, f'file2{file2_ext}')
                
                if isinstance(file1, str):
                    import shutil
                    shutil.copy(file1, file1_path)
                else:
                    file1.save(file1_path)
                
                if isinstance(file2, str):
                    import shutil
                    shutil.copy(file2, file2_path)
                else:
                    file2.save(file2_path)
                
                # ИСПОЛЬЗУЕМ ФУНКЦИИ ИЗ compare_month.py
                set1 = self._read_as_set(dir1)
                set2 = self._read_as_set(dir2)
                
                # Сравниваем множества (как в compare_month.py: print_stats)
                in_both = set1 & set2
                only_in_file1 = set1 - set2
                only_in_file2 = set2 - set1
                
                # Формируем результат
                result = {
                    'file1_name': file1_name,
                    'file2_name': file2_name,
                    'file1_total': len(set1),
                    'file2_total': len(set2),
                    'in_both': len(in_both),
                    'only_in_file1': len(only_in_file1),
                    'only_in_file2': len(only_in_file2),
                    'comparison_date': datetime.now().isoformat(),
                    # Сохраняем сами списки для экспорта
                    'only_in_file1_list': sorted(only_in_file1),
                    'only_in_file2_list': sorted(only_in_file2)
                }
                
                # Формируем текстовый вывод
                result['text_output'] = self._format_comparison_output(result)
                
                return result
            
        except Exception as e:
            raise Exception(f'Ошибка сравнения файлов: {str(e)}')
    
    def _read_as_set(self, dir_path):
        """
        Читает файлы из директории используя функции compare_month.py
        
        Args:
            dir_path: путь к директории с файлами
            
        Returns:
            Set[str]: множество уникальных UID (ИЗ compare_month.py!)
        """
        files = os.listdir(dir_path)
        
        # TXT файлы → используем read_pochta_txts
        if any(f.lower().endswith('.txt') for f in files):
            return read_pochta_txts(dir_path, use_tqdm=False)
        
        # CSV файлы → используем read_asbt_csv
        elif any(f.lower().endswith('.csv') for f in files):
            return read_asbt_csv(dir_path, use_tqdm=False)
        
        # Excel файлы → используем read_telecom_excels
        elif any(f.lower().endswith(('.xlsx', '.xls')) for f in files):
            return read_telecom_excels(dir_path, use_tqdm=False)
        
        else:
            return set()
    
    def _format_comparison_output(self, result, language='uz'):
        """
        Форматирует результат (точный формат из compare_month.py::print_stats)
        
        Returns:
            str: отформатированный текст
        """
        def format_number(num):
            return f"{num:,}".replace(',', ' ')
        
        if language == 'uz':
            # ТОЧНЫЙ формат из print_stats
            lines = []
            lines.append("-" * 44)
            lines.append(f"{result['file1_name']} bergan faylda jami: {format_number(result['file1_total'])}")
            lines.append("")
            lines.append(f"{result['file2_name']} bergan faylda jami: {format_number(result['file2_total'])}")
            lines.append("")
            lines.append("-" * 44)
            lines.append("")
            lines.append(f"Ikkalasida ham mavjud bo'lganlar soni: {format_number(result['in_both'])}")
            lines.append("")
            lines.append(f"{result['file1_name']} bergan faylda mavjud, Telecom bergan faylda yo'q soni: {format_number(result['only_in_file1'])}")
            lines.append("")
            lines.append(f"{result['file2_name']} bergan faylda mavjud, Pochta bergan faylda yo'q soni: {format_number(result['only_in_file2'])}")
            lines.append("")
            lines.append("-" * 44)
            return "\n".join(lines)
        else:  # ru
            lines = []
            lines.append("-" * 44)
            lines.append(f"В файле от {result['file1_name']} всего: {format_number(result['file1_total'])}")
            lines.append("")
            lines.append(f"В файле от {result['file2_name']} всего: {format_number(result['file2_total'])}")
            lines.append("")
            lines.append("-" * 44)
            lines.append("")
            lines.append(f"Присутствуют в обоих файлах: {format_number(result['in_both'])}")
            lines.append("")
            lines.append(f"Есть в {result['file1_name']}, нет в {result['file2_name']}: {format_number(result['only_in_file1'])}")
            lines.append("")
            lines.append(f"Есть в {result['file2_name']}, нет в {result['file1_name']}: {format_number(result['only_in_file2'])}")
            lines.append("")
            lines.append("-" * 44)
            return "\n".join(lines)
    
    def export_comparison(self, comparison_data, month_name='', language='uz'):
        """
        Экспортирует результат сравнения в текстовый файл
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'comparison_{timestamp}.txt'
        
        if language == 'uz':
            if month_name:
                header = f"{month_name} uchun statistika ({comparison_data['file1_name']}-{comparison_data['file2_name']})"
            else:
                header = f"Solishtirish ({comparison_data['file1_name']}-{comparison_data['file2_name']})"
        else:
            if month_name:
                header = f"Статистика за {month_name} ({comparison_data['file1_name']}-{comparison_data['file2_name']})"
            else:
                header = f"Сравнение ({comparison_data['file1_name']}-{comparison_data['file2_name']})"
        
        full_text = f"{header}\n\n{comparison_data['text_output']}"
        
        return full_text.encode('utf-8'), filename
    
    def export_differences(self, comparison_data):
        """
        Экспортирует различия в 2 отдельных TXT файла
        БЕЗ заголовка "Uid" - только чистые данные
        
        Args:
            comparison_data: данные сравнения с только_в_файле1 и только_в_файле2
            
        Returns:
            tuple: (file1_content, file1_name, file2_content, file2_name)
        """
        # Создаем временную директорию для экспорта
        with tempfile.TemporaryDirectory() as tmpdir:
            # Файл 1: записи только в первом файле (БЕЗ заголовка!)
            file1_path = os.path.join(tmpdir, 'only_in_file1.txt')
            uids1 = comparison_data.get('only_in_file1_list', [])
            with open(file1_path, 'w', encoding='utf-8', newline='') as f:
                for uid in sorted(uids1):
                    f.write(f"{uid}\n")
            
            with open(file1_path, 'rb') as f:
                file1_content = f.read()
            
            # Файл 2: записи только во втором файле (БЕЗ заголовка!)
            file2_path = os.path.join(tmpdir, 'only_in_file2.txt')
            uids2 = comparison_data.get('only_in_file2_list', [])
            with open(file2_path, 'w', encoding='utf-8', newline='') as f:
                for uid in sorted(uids2):
                    f.write(f"{uid}\n")
            
            with open(file2_path, 'rb') as f:
                file2_content = f.read()
            
            # Генерируем имена файлов
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file1_name = f"{comparison_data['file1_name']}_minus_{comparison_data['file2_name']}_{timestamp}.txt"
            file2_name = f"{comparison_data['file2_name']}_minus_{comparison_data['file1_name']}_{timestamp}.txt"
            
            return file1_content, file1_name, file2_content, file2_name
