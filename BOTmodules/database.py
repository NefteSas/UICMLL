import json
import os
import re
import json
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from bs4 import BeautifulSoup
import pytz
import requests

from BOTmodules import timecontroller

DATABASE_PATH = "database"

URL = "https://ruz.narfu.ru/?timetable&group=19396"
LAST_UPDATE = None
class NarfuAPIOperator():
    def __init__(self):
        self.LAST_UPDATE = timecontroller.now()
        if (os.path.exists(DATABASE_PATH)):
            print('VIEWED DATABASEPATH')
        else:
            print('DATABASE PATH IS NULL. GENERATING.')
            os.mkdir(DATABASE_PATH) 

    def DownloadHTM(self):

        # Загружаем с правильными заголовками
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        response = requests.get(URL, headers=headers)
        
        # Вариант A: Сохраняем как БИНАРНЫЙ файл (рекомендуется)
        with open(DATABASE_PATH+'/schedule_correct.htm', 'wb') as file:
            file.write(response.content)
        
    def ReadHTML(self) -> str:
        with open(DATABASE_PATH+'/schedule_correct.htm', 'rb') as f:
            html_content = f.read()

        return html_content
    
    #Боже, храни нейронку
    def parse_safu_schedule(self, html_content):
        """
        Парсит расписание группы САФУ из HTML
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Извлекаем информацию о группе из заголовка
        group_info = ""
        navbar_brand = soup.find('a', class_='navbar-brand')
        if navbar_brand:
            spans = navbar_brand.find_all('span')
            if len(spans) > 1:
                group_info = spans[1].text.strip()
        
        # Если не нашли там, ищем в h4
        if not group_info:
            h4 = soup.find('h4', class_=['visible-xs', 'visible-sm'])
            if h4:
                group_info = h4.text.strip()
        
        # Парсим статус обновления
        status = ""
        status_p = soup.find('p', class_='status')
        if status_p:
            status = status_p.text.strip()
        
        # Сначала парсим вкладки с неделями, чтобы получить даты
        week_tabs_info = {}
        nav_tabs = soup.find('ul', class_='nav nav-tabs')
        if nav_tabs:
            # Находим все вкладки недель
            week_tab_items = nav_tabs.find_all('li')
            for tab_item in week_tab_items:
                link = tab_item.find('a')
                if link and 'data-target' in link.attrs:
                    week_id = link['data-target'].replace('#', '')  # Извлекаем id недели (например, "week_1")
                    
                    # Извлекаем даты из трех вариантов отображения
                    date_xs = link.find('span', class_='visible-xs')
                    date_sm = link.find('span', class_='visible-sm visible-md')
                    date_lg = link.find('span', class_='visible-lg')
                    
                    week_tabs_info[week_id] = {
                        'id': week_id,
                        'is_active': 'active' in tab_item.get('class', []),
                        'date_xs': date_xs.text.strip() if date_xs else '',
                        'date_sm': date_sm.text.strip() if date_sm else '',
                        'date_lg': date_lg.text.strip() if date_lg else '',
                        # Для удобства также разделяем даты начала и конца недели
                        'date_range': date_lg.text.strip() if date_lg else '',
                        'start_date': '',
                        'end_date': ''
                    }
                    
                    # Парсим диапазон дат из visible-lg формата "26.01.2026&ndash;31.01.2026"
                    if date_lg:
                        date_text = date_lg.text.strip()
                        if '&ndash;' in date_text:
                            start_end = date_text.split('&ndash;')
                            week_tabs_info[week_id]['start_date'] = start_end[0].strip()
                            week_tabs_info[week_id]['end_date'] = start_end[1].strip()
        
        # Парсим недели
        weeks = []
        week_tabs = soup.find_all('div', class_='row tab-pane')
        
        for week_tab in week_tabs:
            week_id = week_tab.get('id', '')
            
            # Получаем информацию о неделе из вкладки
            week_info = week_tabs_info.get(week_id, {})
            
            week_data = {
                'week_id': week_id,
                'is_active': week_info.get('is_active', False),
                'date_xs': week_info.get('date_xs', ''),
                'date_sm': week_info.get('date_sm', ''),
                'date_lg': week_info.get('date_lg', ''),
                'date_range': week_info.get('date_range', ''),
                'start_date': week_info.get('start_date', ''),
                'end_date': week_info.get('end_date', ''),
                'days': []
            }
            
            # Парсим дни в неделе
            days = week_tab.find_all('div', class_='list')
            
            for day in days:
                day_info = {
                    'date': '',
                    'day_of_week': '',
                    'lessons': []
                }
                
                # Извлекаем дату и день недели
                dayofweek_div = day.find('div', class_='dayofweek')
                if dayofweek_div:
                    day_text = dayofweek_div.text.strip()
                    # Парсим день недели и дату
                    if ',' in day_text:
                        parts = day_text.split(',', 1)
                        day_info['day_of_week'] = parts[0].strip()
                        day_info['date'] = parts[1].strip()
                
                # Парсим занятия (для десктопной и мобильной версий)
                lessons_desktop = day.find_all('div', class_='timetable_sheet')
                lessons_mobile = day.find_all('div', class_='timetable_sheet_xs')
                
                # Объединяем все занятия
                all_lessons = []
                for lesson in lessons_desktop:
                    if 'transparent' not in lesson.get('class', []):
                        all_lessons.append(lesson)
                
                for lesson in all_lessons:
                    lesson_data = {}
                    
                    # Номер пары
                    num_para = lesson.find('span', class_='num_para')
                    if num_para:
                        lesson_data['number'] = num_para.text.strip()
                    
                    # Время
                    time_para = lesson.find('span', class_='time_para')
                    if time_para:
                        lesson_data['time'] = time_para.text.strip()
                    
                    # Тип занятия
                    kind = lesson.find('span', class_='kindOfWork')
                    if kind:
                        lesson_data['type'] = kind.text.strip()
                    
                    # Дисциплина
                    discipline = lesson.find('span', class_='discipline')
                    if discipline:
                        # Извлекаем название дисциплины и преподавателя
                        discipline_text = discipline.text.strip()
                        # Убираем теги <nobr> если есть
                        import re
                        discipline_text = re.sub(r'<nobr>.*?</nobr>', '', discipline_text)
                        lesson_data['discipline'] = discipline_text
                        
                        # Пытаемся извлечь преподавателя из дисциплины
                        nobr = discipline.find('nobr')
                        if nobr:
                            lesson_data['lecturer'] = nobr.text.strip()
                    
                    # Поток/группа
                    group = lesson.find('span', class_='group')
                    if group:
                        lesson_data['stream'] = group.text.strip()
                    
                    # Аудитория
                    auditorium = lesson.find('span', class_='auditorium')
                    if auditorium:
                        # Извлекаем текст аудитории, убирая HTML теги
                        auditorium_text = auditorium.get_text(strip=True, separator=' ')
                        if (" ,\n                               " in auditorium_text):
                            auditorium_text = auditorium_text.replace(" ,\n                               ", ' ')
                        if (" ," in auditorium_text):
                            auditorium_text = auditorium_text.replace(" ,", ' ')
                        if ("\n" in auditorium_text):
                            auditorium_text = auditorium_text.replace("\n", '')
                        lesson_data['auditorium'] = auditorium_text
                    
                    # Ссылки на курс (если есть)
                    link = lesson.find('a')
                    if link and link.get('href'):
                        lesson_data['course_link'] = link['href']
                        lesson_data['course_name'] = link.text.strip() if link.text else "Ссылка на курс"
                    
                    # Дополнительная информация
                    extra_spans = lesson.find_all('span', style="margin: 5px 0px 5px 0px")
                    if extra_spans:
                        for extra in extra_spans:
                            if 'Курс лекций' in extra.parent.text:
                                lesson_data['note'] = 'Курс лекций на платформе Sakai доступен для ознакомления'
                    
                    day_info['lessons'].append(lesson_data)
                
                week_data['days'].append(day_info)
            
            weeks.append(week_data)
        
        # Извлекаем ссылки iCal
        ical_links = {}
        ical_div = soup.find('div', class_='btn-group iCal')
        if ical_div:
            links = ical_div.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.text.strip()
                if 'Скачать' in text:
                    ical_links['download'] = href
                elif 'Подписаться' in text:
                    ical_links['subscribe'] = href
        
        result = {
            'group_info': group_info,
            'last_updated': status,
            'weeks_count': len(weeks),
            'weeks': weeks,
            'week_tabs_info': week_tabs_info,  # Дополнительная информация о вкладках
            'ical_links': ical_links
        }
        
        return result
    
    def SerializeParsed(self, schedule, filename=DATABASE_PATH+'\schedule.json'):
        """
        Сохраняет расписание в JSON файл
        """
        # Функция для сериализации объектов BeautifulSoup
        def clean_for_json(obj):
            if isinstance(obj, dict):
                return {k: clean_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_for_json(item) for item in obj]
            elif hasattr(obj, '__dict__'):
                return str(obj)
            else:
                return obj
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(clean_for_json(schedule), f, ensure_ascii=False, indent=2)
        print(f"\nРасписание сохранено в файл: {filename}")

    def DeserializeData(self, filename=DATABASE_PATH+'\schedule.json') -> dict:
        with open(filename, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        return json_data

    def UpdateInfo(self):
        self.DownloadHTM()
        content = self.ReadHTML()
        parsed = self.parse_safu_schedule(content)
        self.SerializeParsed(parsed)
        self.LAST_UPDATE = timecontroller.now()

    def GetTimeUpdate(self):
        return self.LAST_UPDATE
if (__name__ == '__main__'):
    DB = NarfuAPIOperator()
    DB.DownloadHTM()
    content = DB.ReadHTML()
    parsed = DB.parse_safu_schedule(content)
    DB.SerializeParsed(parsed)

