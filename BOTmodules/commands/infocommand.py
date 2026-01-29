from typing import override

from datetime import datetime
from telegram import PhotoSize, Update, InlineKeyboardMarkup, InlineKeyboardButton
import telegram
from telegram.ext import ContextTypes

from BOTmodules.commands.basebotcommand import BaseBotCommand

## КОСТЫЛЬ
BOT_NAME = "Гуманитарии все испортили"
BOT_DATA = datetime.now()

class InfoCommand(BaseBotCommand):
    def __init__(self) -> None:
        super().__init__("start")

    @override
    async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        
        await update.message.reply_text(
            f"""
            Привет! {BOT_NAME} - просто расписание. Гуманитарии забыли продлить модеус. Ну, спасибо что не MAX.
            \nВремя сборки - {str(BOT_DATA)}
            """,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("GitHub",url="https://github.com/NefteSas/UICMLL")]])
            )