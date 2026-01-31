from multiprocessing import context
from typing import override
from telegram import InlineKeyboardMarkup, Update, InlineKeyboardButton

from BOTmodules.commands.basebotcommand import BaseBotCommand
from telegram.ext import CallbackContext, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, filters, MessageHandler

from BOTmodules.commands.canceldialloge import CancelDialogCommand
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.scheldue import Lesson, ScheduleParser

class FilterCommand(BaseBotCommand):
    # AWAIT = range(1)
    # def __init__(self) -> None:
    #     super().__init__("filter")
    #     self.dialoge = ConversationHandler(entry_points=[
    #         CallbackQueryHandler(callback=self._registrate_filtration)
    #     ],
    #     states={
    #         FilterCommand.AWAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self._get_answer)],
    #     },
    #     fallbacks=[CancelDialogCommand().GetHandler()])

    # @override
    # async def _callback(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
    #     DB = NarfuAPIOperator()
    #     user_info = DB.LoadUserInfo(update.effective_user.id)
    #     if (user_info is None):
    #         await self._registrate_filtration(update, callback)
    #         return
    #     print(user_info)
    #     str_buffer = "Привет. У тебя фильтруются следующие предметы: "

    #     for key, value in user_info:
    #         str_buffer += f"{key} - {value} \n"



    #     await update.message.reply_text(str_buffer)

    # async def _registrate_filtration(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
    #     str_buffer = "Привет! Выбери из данного перечня предметы, которые тебе не нужны и выпиши их в виде: '1,2,3,4'\n"

    #     all_lessons = ScheduleParser(NarfuAPIOperator().DeserializeData()).get_all_lessons()

    #     lesson: Lesson

    #     lesson_buffer = []

    #     for lesson in all_lessons:
    #         lesson_buffer.append(lesson.discipline)

    #     filtered_list = list(set(lesson_buffer))

    #     dictonary = {}
    #     i = 0
    #     for lesson_name in filtered_list:
    #         dictonary[str(i)] = lesson_name
    #         str_buffer += f"\n{lesson_name}\n"

    #     callback.user_data["dictonary_of_lessons"] = dictonary

    #     await update.message.reply_text(str_buffer)

    #     return FilterCommand.AWAIT

    # async def _get_answer(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
    #     print(update.message.text)
    #     await update.message.reply_text("Z")

    # @override
    # def GetHandler(self):
    #     return [self.handler, self.dialoge]

    GETTING_INFO,AWAIT_ANSWER,ANALYZE_ANSWER = range(3)

    def __init__(self, args=None):
        self.dialogHandler = ConversationHandler(
            entry_points=[CommandHandler('filter', self._callback)], states={
                FilterCommand.AWAIT_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.__startRegistration)],
                FilterCommand.ANALYZE_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.__analyzeAsnwer)]
            }, fallbacks=[
                CancelDialogCommand().GetHandler()
            ]
        )
        self.queryhandler = CallbackQueryHandler(self._callback_query,pattern="^FILTER:")
        
    # async def _callback_query(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
    #     query = update.callback_query
    #     newContext = context
    #     newContext.args = [query.data.split(":")[1]] 
    #     await query.answer()
    #     await MonumentInfoCommand()._callback(update=update, context=newContext)      
        
    async def _callback(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        DB = NarfuAPIOperator()
        user_info = DB.LoadUserInfo(update.effective_user.id)
        if (user_info is None):
            return await self.__startRegistration(update,context)
        
        str_buffer = "Привет. У тебя фильтруются следующие предметы: \n"

        for key in user_info:
            str_buffer += f"{key} \n"

        keyboard = [
            [InlineKeyboardButton(f"Сбросить фильтр", callback_data=f"FILTER:RESET")]
        ]
        parsed_keyboard = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(str_buffer, reply_markup=parsed_keyboard)
    
    async def _callback_query(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        
        query_answer = query.data.split(":")[1]
        if (query_answer=="RESET"):
            NarfuAPIOperator().RemoveUserFromBase(update.effective_user.id)
            await query.answer("Фильтр сброшен")
            
        if (query_answer == str(1)):
            NarfuAPIOperator().SaveUserInfo(update.effective_user.id, context.user_data["CHOSE"])
            await query.answer("Фильтр обновлен")
        else:
            await query.answer("Для повторной выставки фильтра пропишите /filter")
        
    async def __startRegistration(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        DB = NarfuAPIOperator()
        user_info = DB.LoadUserInfo(update.effective_user.id)

        str_buffer = ""

        all_lessons = ScheduleParser(NarfuAPIOperator().DeserializeData()).get_all_lessons()

        lesson: Lesson

        lesson_buffer = []

        for lesson in all_lessons:
            lesson_buffer.append(lesson.discipline)

        filtered_list = sorted(list(set(lesson_buffer)))

        dictonary = {}
        i = 0
        for lesson_name in filtered_list:
            dictonary[str(i)] = lesson_name
            str_buffer += f"\n{i} - {lesson_name}\n"
            i+=1
        
        callback.user_data["dictonary_of_lessons"] = dictonary

        str_buffer += "\nПривет! Выбери из данного перечня предметы, которые тебе не нужны и выпиши их в виде: '1,2,3,4'. Для отмены - /cancel"

        await update.message.reply_text(str_buffer)

        return FilterCommand.ANALYZE_ANSWER
    
    async def __analyzeAsnwer(self, update: Update, callback: ContextTypes.DEFAULT_TYPE):
        message_stirng = update.message.text
        numbers = []
        try:
            # Разделяем строку по запятым и преобразуем в числа
            numbers = [int(num.strip()) for num in message_stirng.split(',')]
        except ValueError:
            await update.message.reply_text("Недопустимые символы. Попробуй еще раз (1,3,4) или /cancel")
            return FilterCommand.ANALYZE_ANSWER
        
        buffer = "Ты выбрал для показа следующие дисциплины: "

        dictionary = callback.user_data["dictonary_of_lessons"]
        choose_buffer = []
        print(dictionary)

        for number in numbers:
            buffer += f"\n {number} : {dictionary[str(number)]}"
            choose_buffer.append(dictionary[str(number)])

        buffer += "\n\n ВНИМАНИЕ. ЭТИ ПРЕДМЕТЫ НЕ БУДУТ ПОКАЗЫВАТЬСЯ В РАСПИСАНИИ. ПРОВЕРЬ ВСЕ 4 РАЗА!"
        callback.user_data["CHOSE"] = choose_buffer
        keyboard = [
            [InlineKeyboardButton(f"✅", callback_data=f"FILTER:1"), InlineKeyboardButton(f"❌", callback_data=f"FILTER:0")]
        ]
        parsed_keyboard = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(buffer,reply_markup=parsed_keyboard)
        return ConversationHandler.END
    # def __getNearestList(self, location: telegram.Location) -> dict[int: float]:
    #     ids = sorted(db.GetIDS())
    #     id_distance = {}
    #     for id in ids:
    #         id_distance[id] = self.__calculateDistance(location, db.ReadMonumentByID(id=id))
            
        
    #     id_distance = dict(sorted(id_distance.items(), key=lambda item: item[1]))
    #     return id_distance
    
    
    # def __calculateDistance(self, location: telegram.Location, monument: database.Monument) -> float:
    #     return distance.distance((location.latitude, location.longitude), monument.getGPSPosition).m
        
    @override
    def GetHandler(self):
        return [self.dialogHandler, self.queryhandler]