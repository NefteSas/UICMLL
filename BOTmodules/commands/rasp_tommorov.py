from ast import List
from typing import override
from datetime import date, timedelta
from datetime import datetime
from telegram import PhotoSize, Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram
from telegram.ext import ContextTypes

from BOTmodules import timecontroller
from BOTmodules.commands.basebotcommand import BaseBotCommand
from BOTmodules.stringgenerator import GetStringForDate, GetStringForToday
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import ScheduleParser

class TommorowCommand(BaseBotCommand):
    def __init__(self) -> None:
        super().__init__("tomm")

    @override
    async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(GetStringForDate(timecontroller.today() + timedelta(days=1), update.effective_user.id), parse_mode='Markdown')