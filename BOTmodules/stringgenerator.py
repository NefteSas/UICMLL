from datetime import date

from BOTmodules import timecontroller
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import Lesson, ScheduleParser
d = { 0 : 'zero', 1 : '1️⃣', 2 : '2️⃣', 3 : '3️⃣', 4 : '4️⃣', 5 : '5️⃣', 6 : '6️⃣', 7 : '7️⃣', 8 : '8️⃣', 9 : '9️⃣'}
def GetStringForToday(user_id):
    today = timecontroller.today()
    return GetStringForDate(today, user_id)

def GetStringForDate(date: date, user_id) -> str:
    DB = NarfuAPIOperator()
    user_data = DB.LoadUserInfo(user_id)
    schedule = ScheduleParser(DB.DeserializeData()).get_schedule_by_date(date.strftime("%d.%m.%Y"))
    if (len(schedule) <= 0):
        return "Дата: " + date.strftime("%d.%m.%Y") + " | " + timecontroller.weekday_short(date.weekday()) + "\n\nСидим дома 🎉"
    else:
        string_buffer = ""
        less: Lesson
        i = 0
        for less in schedule:
            print(user_data)
            if (user_data is not None and len(user_data) != 0):
                if (less.discipline in user_data):
                    i+=1
                    continue
            if ((less.course_link is not None) or ('ауд. Дистанционное обучение' in str(less.auditorium))):
                string_buffer += f"\n{d[int(less.number)]} {less.time}\n{less.type}\n{less.discipline}\n[Дистант]({less.course_link})\n"
                continue
            string_buffer += f"\n{d[int(less.number)]} {less.time}\n{less.type}\n{less.discipline}\n{less.auditorium}\n"
        
        string_buffer = "Дата: " + date.strftime("%d.%m.%Y") + " | " + timecontroller.weekday_short(date.weekday()) + f" | Отфильтровано {i} \n"  + string_buffer
        return string_buffer