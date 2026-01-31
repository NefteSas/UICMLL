from ast import List
from typing import override
from datetime import date
from datetime import datetime
from telegram import PhotoSize, Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram
from telegram.ext import ContextTypes

from BOTmodules.commands.basebotcommand import BaseBotCommand
from BOTmodules.stringgenerator import GetStringForDate, GetStringForToday
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import ScheduleParser

class RaspCommand(BaseBotCommand):
    def __init__(self) -> None:
        super().__init__("rasp")

    @override
    async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(GetStringForToday(update.effective_user.id), parse_mode='Markdown')
            