"""
Процессор для объединения нескольких файлов по указанным столбцам
"""

import pandas as pd
from datetime import datetime
import io

class MergeProcessor:
    """
    Процессор для объединения данных из нескольких Excel или текстовых файлов
    Логика нормализации основана на compare_month.py
    """
    
    @staticmethod
    def _normalize_uid(value) -> str:
        """
        Нормализует UID: убирает BOM, кавычки, пробелы
        """
        if value is None or pd.isna(value):
            return None
        
        s = str(value)
        # Убираем BOM и окружающие символы
        s = s.lstrip('\ufeff').strip().strip('"').strip("'").strip()
        
        if not s or s.lower() in {'uid', 'id', 'doc_num', 'docnum', 'nan', 'none'}:
            return None
        
        return s
    
    def merge_files(self, files_data, column_names, merge_mode='union'):
        """
        Объединяет несколько файлов по указанным столбцам
        
        Args:
            files_data: список словарей [{file: путь или объект, name: название}]
            column_names: список названий столбцов для извлечения
            merge_mode: режим объединения ('union' - все уникальные, 'intersection' - только общие)
            
        Returns:
            dict с результатами объединения
        """
        try:
            all_data = {}
            file_stats = []
            
            # Читаем каждый файл
            for file_info in files_data:
                file_obj = file_info['file']
                file_name = file_info['name']
                
                # Извлекаем данные из файла
                extracted_data = self._extract_columns(file_obj, column_names)
                
                # Сохраняем статистику
                file_stats.append({
                    'name': file_name,
                    'total_rows': len(extracted_data),
                    'columns_found': list(extracted_data.keys())
                })
                
                # Объединяем данные
                for col_name, values in extracted_data.items():
                    if col_name not in all_data:
                        all_data[col_name] = []
                    all_data[col_name].extend(values)
            
            # Убираем дубликаты если нужно
            if merge_mode == 'union':
                for col_name in all_data:
                    all_data[col_name] = list(set(all_data[col_name]))
            
            # Формируем результат
            result = {
                'merged_data': all_data,
                'file_stats': file_stats,
                'total_unique_records': {col: len(vals) for col, vals in all_data.items()},
                'merge_date': datetime.now().isoformat()
            }
            
            # Формируем текстовый вывод
            result['text_output'] = self._format_merged_output(result)
            
            return result
            
        except Exception as e:
            raise Exception(f'Ошибка объединения файлов: {str(e)}')
    
    def _extract_columns(self, file, column_names):
        """
        Извлекает указанные столбцы из файла с улучшенной нормализацией
        
        Args:
            file: путь к файлу или file object
            column_names: список названий столбцов
            
        Returns:
            dict: {column_name: [values]} - с нормализованными значениями
        """
        result = {}
        
        # Определяем тип файла и читаем его
        if isinstance(file, str):
            file_path = file
            
            # Excel файл
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, dtype=str)
                for col_name in column_names:
                    result[col_name] = self._extract_column_from_df(df, col_name)
            
            # CSV файл
            elif file_path.endswith('.csv'):
                for sep in [';', ',', '\t']:
                    for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
                        try:
                            df = pd.read_csv(file_path, sep=sep, quotechar='"',
                                           engine='python', encoding=enc, dtype=str,
                                           on_bad_lines='skip')
                            if len(df.columns) > 0:
                                for col_name in column_names:
                                    result[col_name] = self._extract_column_from_df(df, col_name)
                                break
                        except:
                            continue
                    if result:
                        break
            
            # Текстовый файл (TXT)
            else:
                for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
                    try:
                        with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                            values = []
                            first_line = True
                            for line in f:
                                normalized = self._normalize_uid(line)
                                if normalized:
                                    # Пропускаем заголовок
                                    if first_line and normalized.lower() in {'uid', 'id', 'doc_num'}:
                                        first_line = False
                                        continue
                                    first_line = False
                                    values.append(normalized)
                        # Присваиваем всем запрошенным столбцам
                        for col_name in column_names:
                            result[col_name] = values
                        break
                    except:
                        continue
        
        else:
            # File object
            file.seek(0)
            content = file.read()
            
            # Пробуем как Excel
            try:
                df = pd.read_excel(io.BytesIO(content), dtype=str)
                for col_name in column_names:
                    result[col_name] = self._extract_column_from_df(df, col_name)
            except:
                pass
            
            # Если не получилось, пробуем CSV
            if not result:
                for sep in [';', ',', '\t']:
                    for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
                        try:
                            text = content.decode(enc)
                            df = pd.read_csv(io.StringIO(text), sep=sep, quotechar='"',
                                           engine='python', dtype=str, on_bad_lines='skip')
                            if len(df.columns) > 0:
                                for col_name in column_names:
                                    result[col_name] = self._extract_column_from_df(df, col_name)
                                break
                        except:
                            continue
                    if result:
                        break
            
            # Если все еще нет, пробуем как текстовый
            if not result:
                for enc in ['utf-8', 'utf-8-sig', 'cp1251', 'latin1']:
                    try:
                        text = content.decode(enc)
                        values = []
                        first_line = True
                        for line in text.split('\n'):
                            normalized = self._normalize_uid(line)
                            if normalized:
                                if first_line and normalized.lower() in {'uid', 'id', 'doc_num'}:
                                    first_line = False
                                    continue
                                first_line = False
                                values.append(normalized)
                        for col_name in column_names:
                            result[col_name] = values
                        break
                    except:
                        continue
        
        return result
    
    def _extract_column_from_df(self, df, column_name):
        """
        Извлекает столбец из DataFrame с нормализацией
        
        Args:
            df: pandas DataFrame
            column_name: название столбца
            
        Returns:
            list: нормализованные значения
        """
        values = []
        
        # Ищем столбец (case-insensitive)
        col = None
        
        # Точное совпадение
        if column_name in df.columns:
            col = column_name
        else:
            # Case-insensitive поиск
            for c in df.columns:
                if c.strip().lower() == column_name.lower():
                    col = c
                    break
            
            # Поиск по части названия (например, TV_SERIALNUMBER)
            if col is None:
                for c in df.columns:
                    if column_name.lower() in c.lower() or c.lower() in column_name.lower():
                        col = c
                        break
            
            # Если не нашли, используем первый столбец
            if col is None and len(df.columns) > 0:
                col = df.columns[0]
        
        if col is not None:
            series = df[col].astype(str)
            for v in series:
                normalized = self._normalize_uid(v)
                if normalized:
                    values.append(normalized)
        
        return values
    
    def _format_merged_output(self, result, language='ru', limit_preview=1000):
        """
        Форматирует результат объединения в текстовом виде
        
        Args:
            result: результаты объединения
            language: язык вывода
            limit_preview: ограничение для предпросмотра (0 = все записи)
            
        Returns:
            str: отформатированный текст
        """
        lines = []
        
        if language == 'uz':
            lines.append("=================================================")
            lines.append("FAYLLARNI BIRLASHTIRISH NATIJALARI")
            lines.append("=================================================")
            lines.append("")
            
            # Статистика по файлам
            for i, stat in enumerate(result['file_stats'], 1):
                lines.append(f"{i}. {stat['name']}")
                lines.append(f"   Qatorlar: {stat['total_rows']:,}")
                lines.append(f"   Topilgan ustunlar: {', '.join(stat['columns_found'])}")
                lines.append("")
            
            lines.append("-------------------------------------------------")
            lines.append("UMUMIY NATIJALAR:")
            lines.append("-------------------------------------------------")
            
            for col_name, count in result['total_unique_records'].items():
                lines.append(f"{col_name}: {count:,} noyob yozuv")
            
            lines.append("-------------------------------------------------")
            lines.append("")
            
            # Выводим данные (с ограничением для предпросмотра или все)
            for col_name, values in result['merged_data'].items():
                lines.append(f"=== {col_name} ===")
                lines.append("")
                sorted_values = sorted(values)
                
                if limit_preview > 0 and len(sorted_values) > limit_preview:
                    # Показываем только первые записи для предпросмотра
                    for value in sorted_values[:limit_preview]:
                        lines.append(value)
                    lines.append("")
                    lines.append(f"... va yana {len(sorted_values) - limit_preview:,} yozuv")
                    lines.append("")
                    lines.append(f"[TXT yoki Excel faylni yuklab oling - barcha yozuvlar uchun]")
                else:
                    # Выводим все
                    for value in sorted_values:
                        lines.append(value)
                
                lines.append("")
                lines.append(f"Jami: {len(values):,} yozuv")
                lines.append("")
        
        else:  # ru
            lines.append("=================================================")
            lines.append("РЕЗУЛЬТАТЫ ОБЪЕДИНЕНИЯ ФАЙЛОВ")
            lines.append("=================================================")
            lines.append("")
            
            # Статистика по файлам
            for i, stat in enumerate(result['file_stats'], 1):
                lines.append(f"{i}. {stat['name']}")
                lines.append(f"   Строк: {stat['total_rows']:,}")
                lines.append(f"   Найдено столбцов: {', '.join(stat['columns_found'])}")
                lines.append("")
            
            lines.append("-------------------------------------------------")
            lines.append("ОБЩИЕ РЕЗУЛЬТАТЫ:")
            lines.append("-------------------------------------------------")
            
            for col_name, count in result['total_unique_records'].items():
                lines.append(f"{col_name}: {count:,} уникальных записей")
            
            lines.append("-------------------------------------------------")
            lines.append("")
            
            # Выводим данные (с ограничением для предпросмотра или все)
            for col_name, values in result['merged_data'].items():
                lines.append(f"=== {col_name} ===")
                lines.append("")
                sorted_values = sorted(values)
                
                if limit_preview > 0 and len(sorted_values) > limit_preview:
                    # Показываем только первые записи для предпросмотра
                    for value in sorted_values[:limit_preview]:
                        lines.append(value)
                    lines.append("")
                    lines.append(f"... и еще {len(sorted_values) - limit_preview:,} записей")
                    lines.append("")
                    lines.append(f"[Скачайте TXT или Excel файл для просмотра всех записей]")
                else:
                    # Выводим все
                    for value in sorted_values:
                        lines.append(value)
                
                lines.append("")
                lines.append(f"Всего: {len(values):,} записей")
                lines.append("")
        
        return "\n".join(lines)
    
    def export_merged_data(self, merged_data, filename=None, language='ru'):
        """
        Экспортирует объединенные данные в текстовый файл
        
        Args:
            merged_data: данные объединения
            filename: имя файла
            language: язык
            
        Returns:
            bytes, filename
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'merged_data_{timestamp}.txt'
        
        # Используем ПОЛНЫЙ вывод для скачивания
        text_content = merged_data.get('text_output_full', merged_data['text_output'])
        
        return text_content.encode('utf-8'), filename
    
    def export_to_excel(self, merged_data, filename=None):
        """
        Экспортирует объединенные данные в Excel
        
        Args:
            merged_data: данные объединения
            filename: имя файла
            
        Returns:
            bytes, filename
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'merged_data_{timestamp}.xlsx'
        
        # Создаем DataFrame
        max_len = max(len(vals) for vals in merged_data['merged_data'].values())
        
        data_for_df = {}
        for col_name, values in merged_data['merged_data'].items():
            # Дополняем пустыми значениями до максимальной длины
            padded_values = values + [''] * (max_len - len(values))
            data_for_df[col_name] = padded_values
        
        df = pd.DataFrame(data_for_df)
        
        # Сохраняем в BytesIO
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Merged Data')
        
        output.seek(0)
        return output.getvalue(), filename

