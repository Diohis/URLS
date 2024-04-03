import os
import logging
import asyncio
import datetime as dt
from datetime import timedelta

from aiogram import Bot, Dispatcher
# from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from core.settings import settings
from core.settings import home
from core.handlers.basic import *
from core.handlers import main_router

if not os.path.exists(f"{home}/logging"):
    os.makedirs(f"{home}/logging")

# Для отладки локально разкоментить
# logging.basicConfig(level=logging.INFO)
#
# #Для отладки локально закоментить
logger = logging.getLogger()
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(f"{home}/logging/bot{dt.date.today()}.log", "a+", encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

logging.debug("Сообщения уровня DEBUG, необходимы при отладке ")
logging.info("Сообщения уровня INFO, полезная информация при работе программы")
logging.warning("Сообщения уровня WARNING, не критичны, но проблема может повторится")
logging.error("Сообщения уровня ERROR, программа не смогла выполнить какую-либо функцию")
logging.critical("Сообщения уровня CRITICAL, серьезная ошибка нарушающая дальнейшую работу")


async def start():
    bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
    dp = Dispatcher()
    dp.include_routers(main_router)
    dp.message.filter(F.chat.type == 'private')
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start())

