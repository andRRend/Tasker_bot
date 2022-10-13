from aiogram.dispatcher.filters import IDFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram_calendar import SimpleCalendar
from aiogram_calendar import simple_cal_callback

from bot.services.repository_ref import *
from tbot import dp as dispatcher


class NewTask(StatesGroup):
    task_date = State()
    task_name = State()
    task_desc = State()
    task_acc = State()


# callback_gen = CallbackData("date", "sel_date")


async def start_simple_calendar(m):
    await dispatcher.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    await m.answer("Выберите дату для задачи: ", reply_markup=await SimpleCalendar().start_calendar())


async def process_simple_calendar(callback_query, callback_data):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        markup = InlineKeyboardMarkup()
        buttons = [
            InlineKeyboardButton(text="Создать задачу", callback_data=f'select_date/{date.strftime("%d.%m.%Y")}'),
            InlineKeyboardButton(text="Отмена", callback_data="cancel")
        ]
        markup.row(*buttons)
        await NewTask.task_date.set()
        await callback_query.message.edit_text(
            text=f'Выбрана дата {date.strftime("%d.%m.%Y")}',
            reply_markup=markup
        )


async def select_date(call, state):
    await call.message.edit_text(f"Выбрана дата:{call.data.split('/')[1]}\nНазвание задачи:", reply_markup=None)
    await state.set_data(data={'date': call.data.split("/")[1], 'm_id': call.message.message_id})
    await NewTask.next()  # task_name state set


async def set_task_name(m, state):
    data = await state.get_data()
    await dispatcher.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    await dispatcher.bot.edit_message_text(text=f"Описание для задачи: '{m.text}'",
                                           chat_id=m.chat.id,
                                           message_id=data['m_id'])
    await state.update_data(task=m.text)
    await NewTask.next()  # task_desc state set


async def set_task_comment(m, state):
    await state.update_data(comment=m.text)
    await NewTask.next()  # task_acc state set
    data = await state.get_data()
    await dispatcher.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    markup = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton(text="Подтвердить", callback_data="new_task_complete"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ]
    markup.row(*buttons)
    await dispatcher.bot.edit_message_text(text=f"Дата:{data['date']}\n"
                                                f"\nНазвание задачи:{data['task']}\n"
                                                f"\nОписание:{data['comment']}",
                                           chat_id=m.chat.id,
                                           message_id=data['m_id'],
                                           reply_markup=markup)


async def access_task(call, state):
    data = await state.get_data()
    await dispatcher.bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    task_data = {"user_id": call.message.chat.id, "date": data["date"], "task": data["task"], "comment": data["comment"]}
    sql_insert_db(**task_data)
    await call.message.answer(f"Задача: <<{data['task']}>> добавлена на дату: <<{data['date']}>>", reply_markup=None)
    await state.finish()


async def access_task_m(m, state):
    if m.text == "/cancel":
        await state.finish()
        await m.answer("Действие отменено", reply_markup=None)
    else:
        await m.answer("Необходимо подтвердить или отменить задачу", reply_markup=None)


async def callback_cancel(call, state):
    if call.data in "cancel":
        await call.message.edit_text("Действие отменено", reply_markup=None)
        await state.finish()


def register_handlers_new_task(dp, users):
    dp.register_message_handler(start_simple_calendar, lambda m: m.chat.type in "private",
                                IDFilter(user_id=users), commands=["new_task"])
    dp.register_callback_query_handler(callback_cancel, lambda call: call.data in "cancel", state='*')
    dp.register_callback_query_handler(select_date, state=NewTask.task_date)
    dp.register_message_handler(set_task_name, state=NewTask.task_name)
    dp.register_message_handler(set_task_comment, state=NewTask.task_desc)
    dp.register_callback_query_handler(access_task, state=NewTask.task_acc)
    dp.register_message_handler(access_task_m, state=NewTask.task_acc)
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter())
