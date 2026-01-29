from ast import List
from typing import override
from datetime import date
from datetime import datetime
from telegram import PhotoSize, Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram
from telegram.ext import ContextTypes, CallbackQueryHandler

from BOTmodules.commands.basebotcommand import BaseBotCommand
from BOTmodules.stringgenerator import GetStringForDate, GetStringForToday
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import ScheduleParser, Week

class WeeksCommand(BaseBotCommand):
    def __init__(self) -> None:
        super().__init__("weeks")
        self.queryhandler = CallbackQueryHandler(self._callback_weeks,pattern="^DATE:")

    @override
    async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        keyboard = [
        ]
        db = ScheduleParser(NarfuAPIOperator().DeserializeData())
        week: Week
        for week in db.get_all_weeks():
            keyboard.append([InlineKeyboardButton(f"{week.span}", callback_data=f"WEEEK:{week.span}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выбери неделю",reply_markup=reply_markup)

    async def _callback_weeks(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
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

        await query.answer()
        for day in result.days:
            keyboard.append([InlineKeyboardButton(f"{str(day.date)}", callback_data=f"DATE:{str(day.date)}")])
        
        await query.edit_message_reply_markup(keyboard)

            