import datetime
import sqlite3
from bot.config import config


def sqlquery(func):
    def wrapper(*args, **kwrags):
        connection = sqlite3.connect(config.database_name,
                                     detect_types=sqlite3.PARSE_DECLTYPES |
                                     sqlite3.PARSE_COLNAMES)
        cursor = connection.cursor()
        result = func(cursor, connection, *args, **kwrags)
        return result
    return wrapper


@sqlquery
def sql_create_tb_tasks(cursor, connection):
    with connection:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {config.tasks_table}
                            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            owner INTEGER,
                            date TEXT,
                            task TEXT,
                            comment TEXT,
                            members TEXT,
                            create_time timestamp)''').fetchall()
        connection.commit()
        print(f"Table {config.tasks_table} created")


@sqlquery
def sql_create_tb_user(cursor, connection):
    with connection:
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {config.username_table}
                            (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            user_id INTEGER,
                            first_name TEXT,
                            last_name TEXT,
                            username TEXT,
                            login TEXT,
                            joinDate timestamp)''')
        connection.commit()
        print(f"Table {config.username_table} created")


@sqlquery
def sql_insert_db(cursor, connection, **user_data):
    """
    Write new row in DB

    :param user_data: keys: id, user_id, date, task, comment
    :return: None
    """
    with connection:
        data = (user_data['user_id'], user_data['date'], user_data['task'],
                user_data['comment'], datetime.datetime.now())
        insert_query = f'''INSERT INTO {config.tasks_table} 
                       (owner, date, task, comment, create_time) 
                       VALUES (?,?,?,?,?);'''
        cursor.execute(insert_query, data)
        connection.commit()


@sqlquery
def sql_select_db(cursor, connection, dates_opt=False, sel_date=None, user_id=None, task=None, *args, **kwargs):
    """
    Select query by option from DB options:
    \t 1. task(arg) and user_id(arg) ---> return id from DB
    \t 2. dates(bool) True and user_id(arg) ---> return dates list by user(tuple)
    \t 3. sel_date(arg) and user_id(arg) ---> return list tasks on sel_date(tuple)
    :param dates_opt: (bool) True for options
    :param sel_date: (arg) select date
    :param user_id: (arg) user id
    :param task: (arg) task name
    :return: optionally
    """
    with connection:
        if task and user_id:
            id_from_db = cursor.execute(f'SELECT id FROM {config.tasks_table} '
                                        'WHERE owner = ? AND task = ?',
                                        (user_id, task)).fetchone()
            return id_from_db[0]

        elif dates_opt and user_id:
            try:
                all_dates = cursor.execute(f'SELECT date FROM {config.tasks_table} WHERE owner = ?',
                                                (user_id,)).fetchall()
                return set([el[0] for el in all_dates])
            except Exception as e:
                print(f'No tasks in DB {config.tasks_table}')
                return False

        elif sel_date and user_id:
            tasks = cursor.execute(f'SELECT task FROM {config.tasks_table} '
                                   'WHERE owner = ? AND date = ?',
                                   (user_id, sel_date)).fetchall()
            return [el[0] for el in tasks]


@sqlquery
def sql_select_by_id(cursor, connection, check_id_opt=False, comment_opt=False, task_opt=False, id_from_db=None):
    """
    Select query by option from DB by id options:
    \t 1. check_id_opt(bool) True ---> return last id(tuple) or 0
    \t 2. comment_opt(bool) True and id(arg) ---> return comment
    \t 3. task_opt(bool) True and id(arg) ---> return task
    :param check_id_opt: (bool) True for options
    :param comment_opt: (bool) True for options
    :param task_opt: (bool) True for options
    :param id_from_db: (arg) id from DB
    :return: optionally
    """
    with connection:
        if check_id_opt:
            try:
                ids = cursor.execute(f'SELECT id FROM {config.tasks_table}').fetchall()
                return max([el[0] for el in ids if len(ids) != 0])
            except Exception as e:
                print(e)
                return 0

        elif comment_opt and id_from_db:
            comment = cursor.execute(f'SELECT comment FROM {config.tasks_table} '
                                     'WHERE id = ?',
                                     (id_from_db, )).fetchone()
            return comment[0]

        elif task_opt and id_from_db:
            task = cursor.execute(f'SELECT task FROM {config.tasks_table} '
                                  'WHERE id = ?',
                                  (id_from_db, )).fetchone()
            return task[0]


@sqlquery
def sql_delete_row(cursor, connection, id_from_db):
    with connection:
        cursor.execute(f'DELETE FROM {config.tasks_table} '
                       'WHERE id = ?',
                       (id_from_db, ))
        connection.commit()


@sqlquery
def sql_update_comment(cursor, connection, id_from_db, new_comment):
    with connection:
        cursor.execute(f'UPDATE {config.tasks_table} set comment = ? '
                       'WHERE id = ?',
                       (new_comment, id_from_db))
        connection.commit()


@sqlquery
def sql_check_reg_user(cursor, connection, user_id):
    with connection:
        return cursor.execute(f'''SELECT user_id FROM {config.username_table} 
                              WHERE user_id = ?''',
                              (user_id, )).fetchone()


@sqlquery
def sql_insert_user(cursor, connection, **user_data):
    with connection:
        data = (user_data['user_id'], user_data['first_name'], user_data['last_name'],
                user_data['username'], user_data['login'], datetime.datetime.now())
        insert_query = f'''INSERT INTO {config.username_table} 
                       (user_id, first_name, last_name, username, login, joinDate) 
                       VALUES (?,?,?,?,?,?);'''
        cursor.execute(insert_query, data)
        connection.commit()


@sqlquery
def sql_select_datetime(cursor, connection, user_id):
    with connection:
        dt = cursor.execute(f'''SELECT joinDate FROM {config.username_table}
                                  WHERE user_id = ?''', (user_id, )).fetchone()
        return dt[0]
