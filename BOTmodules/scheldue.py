from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Lesson:
    number: str
    time: str
    type: str
    discipline: str
    lecturer: str
    auditorium: str
    stream: Optional[str] = None
    course_link: Optional[str] = None
    course_name: Optional[str] = None
    note: Optional[str] = None

@dataclass
class Day:
    date: str
    day_of_week: str
    lessons: List[Lesson]

@dataclass
class Week:
    week_id: str
    days: List[Day]
    span: str

@dataclass
class Schedule:
    group_info: str
    last_updated: str
    weeks_count: int
    weeks: List[Week]
    ical_links: dict

class ScheduleParser:
    def __init__(self, json_data: dict):
        self.schedule = self._parse_json(json_data)
    
    def _parse_json(self, data: dict) -> Schedule:
        """Парсит JSON и создает объект Schedule"""
        weeks = []
        
        for week_data in data.get('weeks', []):
            days = []
            
            for day_data in week_data.get('days', []):
                lessons = []
                
                for lesson_data in day_data.get('lessons', []):
                    lesson = Lesson(
                        number=lesson_data.get('number', ''),
                        time=lesson_data.get('time', ''),
                        type=lesson_data.get('type', ''),
                        discipline=lesson_data.get('discipline', ''),
                        lecturer=lesson_data.get('lecturer', ''),
                        auditorium=lesson_data.get('auditorium', ''),
                        stream=lesson_data.get('stream'),
                        course_link=lesson_data.get('course_link'),
                        course_name=lesson_data.get('course_name'),
                        note=lesson_data.get('note')
                    )
                    lessons.append(lesson)
                
                day = Day(
                    date=day_data.get('date', ''),
                    day_of_week=day_data.get('day_of_week', ''),
                    lessons=lessons
                )
                days.append(day)
            
            week = Week(
                week_id=week_data.get('week_id', ''),
                days=days,
                span=week_data.get("date_range")
            )
            weeks.append(week)
        
        return Schedule(
            group_info=data.get('group_info', ''),
            last_updated=data.get('last_updated', ''),
            weeks_count=data.get('weeks_count', 0),
            weeks=weeks,
            ical_links=data.get('ical_links', {})
        )
    
    def get_schedule_by_date(self, target_date: str) -> List[Lesson]:
        """Возвращает занятия на конкретную дату"""
        for week in self.schedule.weeks:
            for day in week.days:
                if day.date == target_date:
                    return day.lessons
        return []
    
    def get_schedule_by_week(self, week_id: str) -> List[Day]:
        """Возвращает расписание на неделю по ID"""
        for week in self.schedule.weeks:
            if week.week_id == week_id:
                return week.days
        return []
    
    def get_all_lessons(self) -> List[Lesson]:
        """Возвращает все занятия из расписания"""
        all_lessons = []
        for week in self.schedule.weeks:
            for day in week.days:
                all_lessons.extend(day.lessons)
        return all_lessons
    
    def get_days_with_lessons(self) -> List[Day]:
        """Возвращает только дни, в которых есть занятия"""
        days_with_lessons = []
        for week in self.schedule.weeks:
            for day in week.days:
                if day.lessons:
                    days_with_lessons.append(day)
        return days_with_lessons
    
    def filter_by_discipline(self, discipline: str) -> List[Lesson]:
        """Фильтрует занятия по названию дисциплины"""
        filtered = []
        for lesson in self.get_all_lessons():
            if discipline.lower() in lesson.discipline.lower():
                filtered.append(lesson)
        return filtered
    
    def filter_by_lecturer(self, lecturer: str) -> List[Lesson]:
        """Фильтрует занятия по преподавателю"""
        filtered = []
        for lesson in self.get_all_lessons():
            if lecturer.lower() in lesson.lecturer.lower():
                filtered.append(lesson)
        return filtered
    
    def get_distant_lessons(self) -> List[Lesson]:
        """Возвращает дистанционные занятия"""
        distant = []
        for lesson in self.get_all_lessons():
            if 'Дистанционное обучение' in lesson.auditorium:
                distant.append(lesson)
        return distant
    def get_all_weeks(self) -> List[Week]:
        return self.schedule.weeks