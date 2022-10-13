from aiogram.dispatcher.filters import IDFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.services.repository_ref import *
from tbot import dp as dispather


class TaskList(StatesGroup):
    dates_list = State()
    tasks_list = State()
    task_edit = State()
    accept_task_edit = State()
    accept_comment_edit = State()


async def get_dates_list(m):
    if not sql_select_db(dates_opt=True, user_id=m.from_user.id):
        await dispather.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
        await m.answer("Записи еще не созданы")
    else:
        await dispather.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
        list_dates = sql_select_db(dates_opt=True, user_id=m.from_user.id)
        markup = InlineKeyboardMarkup()
        for date in sorted(list_dates):
            markup.add(InlineKeyboardButton(date, callback_data=date))
        markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
        await TaskList.dates_list.set()  # dates_list state set
        await m.answer("Даты на которые есть задачи:", reply_markup=markup)


async def get_tasks_list(call, state):
    markup = InlineKeyboardMarkup()
    list_tasks = sql_select_db(sel_date=call.data, user_id=call.from_user.id)
    for el in list_tasks:
        markup.add(InlineKeyboardButton(el, callback_data=el))
    markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    await state.set_data(data={'date': call.data})
    await TaskList.next()  # tasks_list state set
    await dispather.bot.edit_message_text(text=f"Список задач на дату: {call.data}",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=markup)


async def get_task_option(call, state):
    await state.update_data(task=call.data, m_id=call.message.message_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Переименовать задачу", callback_data="edit_task"))
    markup.add(InlineKeyboardButton("Изменить описание", callback_data="edit_comment"))
    markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    await dispather.bot.edit_message_text(text=f"Выберите действие для задачи: {call.data}",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=markup)
    await TaskList.next()  # task_edit state set


async def edit_task(call, state):
    data = await state.get_data()
    await dispather.bot.edit_message_text(text=f"Введите новое имя для задачи: {data['task']}",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=None)
    await TaskList.accept_task_edit.set()


async def accept_edit_task(m, state):
    data = await state.get_data()
    await state.update_data(edit_task=m.text)
    await dispather.bot.delete_message(chat_id=m.chat.id, message_id=data["m_id"])
    await dispather.bot.delete_message(chat_id=m.chat.id, message_id=m.message_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Подтвердить", callback_data="accept_edit_task"))
    markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
    # await dispather.bot.edit_message_text(text=f"Подтвердить переименование задачи: {data['task']} ?",
    #                                       chat_id=m.chat.id,
    #                                       message_id=m.message_id,
    #                                       reply_markup=markup)
    await m.answer(text=f"Подтвердить переименование задачи: {data['task']} в {data['edit_task']}?", reply_markup=markup)
    await state.finish()


async def complete_edit_task(call, state):
    pass
    await state.finish()



async def edit_comment(call, state):
    data = await state.get_data()
    await dispather.bot.edit_message_text(text=f"Введите новое описание для задачи: {data['task']}",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=None)
    await TaskList.accept_comment_edit.set()


async def accept_edit_comment(m, state):
    print('comment')
    await state.finish()


def register_handlers_task_list(dp, users):
    dp.register_message_handler(get_dates_list, lambda m: m.chat.type in "private",
                                IDFilter(user_id=users), commands=["list"])
    dp.register_callback_query_handler(get_tasks_list, state=TaskList.dates_list)
    dp.register_callback_query_handler(get_task_option, state=TaskList.tasks_list)
    dp.register_callback_query_handler(edit_task, lambda call: call.data in "edit_task", state=TaskList.task_edit)
    dp.register_callback_query_handler(edit_comment, lambda call: call.data in "edit_comment", state=TaskList.task_edit)
    dp.register_message_handler(accept_edit_task, state=TaskList.accept_task_edit)
    dp.register_message_handler(accept_edit_comment, state=TaskList.accept_comment_edit)
