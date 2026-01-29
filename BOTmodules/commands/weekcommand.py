from ast import List
from itertools import count
from typing import override
from datetime import date, timedelta
from datetime import datetime
from telegram import CallbackQuery, PhotoSize, Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram
from telegram.ext import ContextTypes
from telegram.ext import CallbackQueryHandler, CommandHandler
from BOTmodules import stringgenerator
from BOTmodules.commands.basebotcommand import BaseBotCommand
from BOTmodules.stringgenerator import GetStringForDate, GetStringForToday
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import ScheduleParser, Week

class WeekCommand(BaseBotCommand):
    def __init__(self) -> None:
        super().__init__("week")
        self.queryhandler = CallbackQueryHandler(self._callback_query,pattern="^DATE:")
        self.another_command = CommandHandler("weeks", self._callback_weeks)
        self.weeks_handler = CallbackQueryHandler(self._callback_weeks_query,pattern="^WEEK:")

    @override
    async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        keyboard = [
        ]
        db = ScheduleParser(NarfuAPIOperator().DeserializeData())
        result: Week = None
        week: Week
        for week in db.get_all_weeks():
            spit = week.span.split("–")
            true_end_of_week = datetime.strptime(spit[1], '%d.%m.%Y') +  timedelta(days=1)

            if (datetime.strptime(spit[0], '%d.%m.%Y') <= datetime(2026,2,9) <= true_end_of_week):
                result = week
                break
        if (result is None):
            await update.message.reply_text(f"На этой неделе пар нет 🎉")
            return
        else:
            for day in result.days:
                keyboard.append([InlineKeyboardButton(f"{str(day.date)}", callback_data=f"DATE:{str(day.date)}")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выбери неделю",reply_markup=reply_markup)

    async def _callback_query(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        newContext = context
        newContext.args = [query.data.split(":")[1]] 
        await query.answer() 
        print(query.data.split(":")[1])
        await query.edit_message_text(stringgenerator.GetStringForDate(datetime.strptime(query.data.split(":")[1], '%d.%m.%Y')), parse_mode='Markdown')

    async def _callback_weeks(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        keyboard = [
        ]
        db = ScheduleParser(NarfuAPIOperator().DeserializeData())
        week: Week
        for week in db.get_all_weeks():
            has_any_lesson = False
            for day in week.days:
                if (len(day.lessons) > 0):
                    has_any_lesson = True
                    break
            
            if (not has_any_lesson):
                continue

            keyboard.append([InlineKeyboardButton(f"{week.span}", callback_data=f"WEEK:{week.span}")])
        if (len(keyboard) == 0):
            await update.message.reply_text("На этой неделе пар нет 🎉")
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выбери неделю",reply_markup=reply_markup)

    async def _callback_weeks_query(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        keyboard = [
        ]
        db = ScheduleParser(NarfuAPIOperator().DeserializeData())
        result: Week = None
        week: Week
        query = update.callback_query
        for week in db.get_all_weeks():
            if (week.span==query.data.split(":")[1]):
                result=week
                break

        query.answer()

        for day in result.days:
            if len(day.lessons) <= 0:
                continue
            keyboard.append([InlineKeyboardButton(f"{str(day.date)}", callback_data=f"DATE:{str(day.date)}")])
        
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    @override
    def GetHandler(self):
        return [self.handler,self.queryhandler, self.another_command, self.weeks_handler]

            