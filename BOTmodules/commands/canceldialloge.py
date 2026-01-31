from typing import override
from telegram import ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, filters

from BOTmodules.commands.basebotcommand import BaseBotCommand

class CancelDialogCommand(BaseBotCommand):
    def __init__(self, command='cancel', args=None):
        super().__init__(command, args)
    
    @override    
    async def _callback(self, update, callback):
        await update.message.reply_text("🚫 Диалог прерван.", reply_markup=ReplyKeyboardRemove())
        callback.user_data.clear()
        return ConversationHandler.END
    