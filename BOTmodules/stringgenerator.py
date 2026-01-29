from datetime import date

from BOTmodules import timecontroller
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import Lesson, ScheduleParser
d = { 0 : 'zero', 1 : '1️⃣', 2 : '2️⃣', 3 : '3️⃣', 4 : '4️⃣', 5 : '5️⃣', 6 : '6️⃣', 7 : '7️⃣', 8 : '8️⃣', 9 : '9️⃣'}
def GetStringForToday():
    today = timecontroller.today()
    return GetStringForDate(today)

def GetStringForDate(date: date) -> str:
    schedule = ScheduleParser(NarfuAPIOperator().DeserializeData()).get_schedule_by_date(date.strftime("%d.%m.%Y"))
    if (len(schedule) <= 0):
        return "Дата: " + date.strftime("%d.%m.%Y") + "\n\nСидим дома 🎉"
    else:
        string_buffer = "Дата: " + date.strftime("%d.%m.%Y")
        less: Lesson
        for less in schedule:
            if ((less.course_link is not None) or ('ауд. Дистанционное обучение' in str(less.auditorium))):
                string_buffer += f"\n{d[int(less.number)]} {less.time}\n❔{less.discipline}\n[🗺 Дистант]({less.course_link})\n"
                continue
            string_buffer += f"\n{d[int(less.number)]} {less.time}\n❔{less.discipline}\n🗺 {less.auditorium}\n"
        return string_buffer