import pandas as pd
from collections import Counter
from datetime import datetime
import io

class ViolationsProcessor:
    """
    Процессор для анализа нарушений из Excel файлов
    Улучшенная логика с нормализацией данных
    """
    
    def __init__(self):
        self.violation_column = 'qoidabuzarlik nomi'
    
    @staticmethod
    def _normalize_value(value) -> str:
        """
        Нормализует значение: убирает BOM, кавычки, пробелы
        """
        if value is None or pd.isna(value):
            return None
        
        s = str(value)
        # Убираем BOM и окружающие символы
        s = s.lstrip('\ufeff').strip().strip('"').strip("'").strip()
        
        if not s or s.lower() in {'nan', 'none', ''}:
            return None
        
        return s
    
    def process_violations_file(self, file_path):
        """
        Обрабатывает Excel файл с нарушениями и возвращает статистику
        
        Args:
            file_path: путь к Excel файлу или file object
            
        Returns:
            dict: {
                'violations': list of dicts with violation stats,
                'total': int total count,
                'text_output': str formatted text output,
                'unique_violations': int count of unique violations
            }
        """
        try:
            # Читаем Excel файл
            if isinstance(file_path, str):
                df = pd.read_excel(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path, dtype=str)
            
            # Проверяем наличие нужного столбца (case-insensitive)
            col = None
            if self.violation_column in df.columns:
                col = self.violation_column
            else:
                # Case-insensitive поиск
                for c in df.columns:
                    if c.strip().lower() == self.violation_column.lower():
                        col = c
                        break
                
                # Поиск по части названия
                if col is None:
                    possible_columns = [c for c in df.columns if 'nomi' in c.lower() or 'название' in c.lower()]
                    if possible_columns:
                        col = possible_columns[0]
                
                if col is None:
                    raise ValueError(f'Столбец "{self.violation_column}" не найден в файле. Доступные столбцы: {list(df.columns)}')
            
            # Получаем все нарушения с нормализацией
            violations = []
            series = df[col].astype(str)
            for v in series:
                normalized = self._normalize_value(v)
                if normalized:
                    violations.append(normalized)
            
            # Подсчитываем количество каждого нарушения
            violation_counts = Counter(violations)
            
            # Сортируем по количеству (по убыванию)
            sorted_violations = sorted(
                violation_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Формируем результат
            violations_list = []
            for idx, (violation_name, count) in enumerate(sorted_violations, 1):
                violations_list.append({
                    'number': idx,
                    'count': count,
                    'violation_text': violation_name
                })
            
            total_count = sum(violation_counts.values())
            
            # Формируем текстовый вывод
            text_output = self._format_text_output(violations_list, total_count)
            
            return {
                'violations': violations_list,
                'total': total_count,
                'text_output': text_output,
                'unique_violations': len(violation_counts),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f'Ошибка обработки файла с нарушениями: {str(e)}')
    
    def _format_text_output(self, violations_list, total_count):
        """
        Форматирует вывод в текстовом формате
        
        Args:
            violations_list: список нарушений
            total_count: общее количество
            
        Returns:
            str: отформатированный текст
        """
        lines = []
        lines.append("№  count  notify_text")
        lines.append("")
        
        for violation in violations_list:
            line = f"{violation['number']}  {violation['count']}  {violation['violation_text']}"
            lines.append(line)
        
        lines.append("")
        lines.append(f"  {total_count}  TOTAL")
        
        return "\n".join(lines)
    
    def export_to_text(self, violations_data, filename=None, language='ru'):
        """
        Экспортирует результаты в текстовый файл
        
        Args:
            violations_data: данные о нарушениях
            filename: имя файла (опционально)
            language: язык отчета ('ru' или 'uz')
            
        Returns:
            bytes: содержимое текстового файла
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'violations_report_{timestamp}.txt'
        
        text_content = violations_data['text_output']
        
        # Заголовки на разных языках
        headers = {
            'ru': {
                'title': 'ОТЧЕТ ПО НАРУШЕНИЯМ',
                'date': 'Дата формирования',
                'total': 'Всего нарушений',
                'unique': 'Уникальных типов'
            },
            'uz': {
                'title': 'QOIDABUZARLIKLAR HISOBOTI',
                'date': 'Tuzilgan sana',
                'total': 'Jami qoidabuzarliklar',
                'unique': 'Unikal turlar'
            }
        }
        
        h = headers.get(language, headers['ru'])
        
        # Добавляем заголовок
        header = f"""
=================================================
{h['title']}
=================================================
{h['date']}: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
{h['total']}: {violations_data['total']}
{h['unique']}: {violations_data['unique_violations']}
=================================================

"""
        
        full_text = header + text_content
        
        return full_text.encode('utf-8'), filename
    
    def get_statistics(self, violations_list):
        """
        Получает расширенную статистику по нарушениям
        
        Args:
            violations_list: список нарушений
            
        Returns:
            dict: статистика
        """
        if not violations_list:
            return {}
        
        counts = [v['count'] for v in violations_list]
        
        return {
            'total_violations': sum(counts),
            'unique_types': len(violations_list),
            'most_common': violations_list[0] if violations_list else None,
            'least_common': violations_list[-1] if violations_list else None,
            'average_per_type': sum(counts) / len(counts) if counts else 0
        }

