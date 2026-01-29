import asyncio
from mailbox import FormatError
import re
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, BaseHandler, ContextTypes

from BOTmodules.database import NarfuAPIOperator

class TelegramBotInterface:
    def __init__(self, token: str) -> None:
        self.app: Application = ApplicationBuilder().token(token).post_init(self.post_init).build()

    def AddHandlerToList(self, handler: BaseHandler):
        self.app.add_handler(handler)

    def getApplication(self) -> Application:
        return self.app

    def AddHandlers(self, handlers: list[BaseHandler]):
        self.app.add_handlers(handlers)

    def Run(self):
        print('BOT STARTING')
        self.app.run_polling()

    @staticmethod
    async def sendPhoto(url: str, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        
        if not TelegramBotInterface.is_url(url):
            raise FormatError
        
        await callback.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=url
            )
    async def background_hourly_task(self):
        DB = NarfuAPIOperator()
        print("UPDATED INFO FIRSTLY")
        DB.UpdateInfo()

        while True:
            # Ждем 1 час
            await asyncio.sleep(3600)
            print("UPDATED INFO")
            DB.UpdateInfo()
    async def post_init(self, application: Application):
        # Создаем фоновую задачу
        asyncio.create_task(self.background_hourly_task())
    @staticmethod
    def is_url(text: str) -> bool:
        pattern = re.compile(
            r"^https?://"  # http:// или https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # Домен
            r"localhost|"  # Локальный хост
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IPv4
            r"(?::\d+)?"  # Порт (опционально)
            r"(?:/?|[/?]\S+)$", 
            re.IGNORECASE
        )
        return re.match(pattern, text) is not None