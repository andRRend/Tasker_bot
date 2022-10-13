from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.files import JSONStorage

import logging

from bot.config import config


# --->
# TASKer telegram bot v0.0.1a
#
# andRRend
#
# --->

storage = JSONStorage(path='bot/config/states.json')

bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger.info("Starting bot")


async def main(dispatcher):
    from bot.exception.exception import register_exception
    from bot.handlers.command import register_handlers_commands
    from bot.handlers.new_task import register_handlers_new_task
    from bot.handlers.task_list import register_handlers_task_list

    register_exception(dispatcher)
    register_handlers_new_task(dispatcher, config.users)
    register_handlers_task_list(dispatcher, config.users)
    register_handlers_commands(dispatcher, config.users)

    await set_commands(bot)


async def set_commands(bot_obj):
    commands = [
        BotCommand(command="/list", description="Просмотреть все даты с активностями"),
        BotCommand(command="/new_task", description="Добавить новую задачу")
    ]
    await bot_obj.set_my_commands(commands)


async def shutdown(dispatcher):
    logger.debug(f"Shutdowning...")
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=main, on_shutdown=shutdown)

