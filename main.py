import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import settings
from handlers.user_private import user_router

from db.db import DBSession
from db.engine import async_session, create_db

from shop_parser import parser_main

'''
Точка входа, код запуска бота и инициализации всех остальных модулей
'''

ALLOWED_UPDATES = ['message, edited_message']

bot_commands = [
    BotCommand(command="/start", description="запуск")
    #BotCommand(command="/help", description="справка")
]

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
dp.update.middleware(DBSession(session_pool=async_session))

# Подключает к диспетчеру все обработчики, которые используют user_router
dp.include_router(user_router)

async def main():

    print('Start: create DB')
    await create_db()

    print('delete webhook')

    # Удаляет все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands(bot_commands)

    print('start polling')
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

    print('finished!')
    

if __name__ == "__main__":
    
    # Запуск парсера
    # Парсер заполняет БД товарами, с которыми работает телеграм-бот
    # TODO: запускать парсер в отдельном потоке Thread
    #parser_main.main()
    
    # Запуск бота
    asyncio.run(main())
