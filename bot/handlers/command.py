from aiogram.dispatcher.filters import IDFilter

from bot.services.repository import SQLquery


async def commands(m):
    if m.text == '/dice':
        await m.answer_dice(emoji="🎲")
    elif m.text == "/cr_db":
        SQLquery().sql_create_tb_tasks()
        SQLquery().sql_create_tb_user()
        await m.answer("База данных создана!")


async def admin_commands(m):
    await m.answer("admin only")


async def text(m):
    await m.answer("I'am alive!")


async def cancel(m, state):
    await m.answer("Действие отменено", reply_markup=None)
    await state.finish()


def register_handlers_commands(dp, users):
    dp.register_message_handler(cancel, commands=["cancel"], state="*")
    dp.register_message_handler(commands, commands=["dice", "cr_db"])
    dp.register_message_handler(text, lambda m: m.chat.type in "private", IDFilter(user_id=users))


# tg://user?id={user_id}

