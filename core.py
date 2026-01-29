import asyncio
import datetime
import os

import pytz

from BOTmodules import *
from BOTmodules.commands.infocommand import InfoCommand
from BOTmodules.commands.rasp_tommorov import TommorowCommand
from BOTmodules.commands.raspcommand import RaspCommand
from BOTmodules.commands.unknowncommandhandler import UnknownCommandHandler
from BOTmodules.commands.weekcommand import WeekCommand
from BOTmodules.commands.weekscommand import WeeksCommand
from BOTmodules.configuration import ConfigurationOvermind
from BOTmodules.database import NarfuAPIOperator
from BOTmodules.telegram_interface import TelegramBotInterface

DEFAULT_TZ = pytz.timezone('Europe/Moscow')

TOKEN = ConfigurationOvermind().getBotToken()




TGI = TelegramBotInterface(ConfigurationOvermind().getBotToken())
TGI.AddHandlerToList(InfoCommand().GetHandler())
TGI.AddHandlerToList(RaspCommand().GetHandler())
TGI.AddHandlerToList(TommorowCommand().GetHandler())
TGI.AddHandlers(WeekCommand().GetHandler())
# TGI.AddHandlerToList(RegMonumentConverstation().getHandler()) 
# TGI.AddHandlerToList(MonumentInfoCommand().GetHandler())
# TGI.AddHandlers(EditMonumentInfo().GetHandler())
# TGI.AddHandlerToList(RandomMonument().GetHandler())
# TGI.AddHandlers(MonumentsByLocation().GetHandler())
TGI.AddHandlerToList(UnknownCommandHandler().GetHandler())



TGI.Run()
