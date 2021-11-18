import config
import telebot
from telebot import types
from datetime import datetime
import sqlite3
import emoji

bot = telebot.TeleBot(config.token)

conn = sqlite3.connect('db/database', check_same_thread=False)
cursor = conn.cursor()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    user_login = message.from_user.username
    db_upsert_user(message.from_user.id, user_login, user_name)

    bot.send_message(message.from_user.id, user_name + config.startTest)

    show_list(message, False)


@bot.message_handler(commands=['help', 'menu', 'info', 'feedback'])
def help_actions(message):
    if message.text == '/menu':
        bot.send_message(message.from_user.id, "Отобразить тест с кнопками")
    elif message.text == '/info':
        bot.send_message(message.from_user.id, "Приветственный текст бота")
    elif message.text == '/feedback':
        bot.send_message(message.from_user.id, "Добавить возможность оставить фитбэк")
    elif message.text == '/help':
        bot.send_message(message.from_user.id, config.helpText)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    data = call.data
    if data == 'back':
        bot.send_message(call.message.chat.id, "Вы вернулись в меню")
    elif data.startswith('list_callback_'):
        list_id = data.split('_')[-1]
        list_worker(call, list_id)
    elif data.startswith('item_callback_'):
        item_id = data.split('_')[-1]
        item_worker(call, item_id)


def show_list(message, is_edit_mode):
    send_divider_for_message(message)
    list_of_list = db_get_list_all(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    final_text = "Выбери список мой друг"

    if is_edit_mode:
        final_text = "Или выбери существующий список"
        new_list_markup = types.InlineKeyboardMarkup()
        button_new_list = types.InlineKeyboardButton(text='Добавить', callback_data='list_callback_add_new')
        new_list_markup.add(button_new_list)
        bot.send_message(message.chat.id,
                         'Для того что бы добавить новый список, жмякни на кнопке "Добавить"',
                         reply_markup=new_list_markup)

    for val in list_of_list:
        button_list = types.InlineKeyboardButton(text=val[1], callback_data='list_callback_select_' + str(val[0]))
        if is_edit_mode:
            button_edit = types.InlineKeyboardButton(text='Переименовать',
                                                     callback_data='list_callback_rename_' + str(val[0]))
            button_delete = types.InlineKeyboardButton(text='Удалить',
                                                       callback_data='list_callback_delete_' + str(val[0]))
            markup.row(button_list, button_edit, button_delete)
        else:
            markup.add(button_list)
    bot.send_message(message.chat.id, final_text, reply_markup=markup)

    if not is_edit_mode:
        edit_mode_markup = types.InlineKeyboardMarkup()
        button_edit_mode = types.InlineKeyboardButton(text='Переключиться',
                                                      callback_data='list_callback_turn_on_edit_mode')
        edit_mode_markup.add(button_edit_mode)
        bot.send_message(message.chat.id, config.editModeTurnOnText, reply_markup=edit_mode_markup)


def show_list_items(call, list_id, is_edit_mode):#Доставать списки джоинами что бы можно было имя группы достать
    send_divider_for_call(call)
    list_of_items = db_get_item_by_list_id(list_id)
    # list_name = db_get_list_by_id(list_id)[0][1]
    markup = types.InlineKeyboardMarkup()
    final_text = "Открыт список"

    if is_edit_mode:
        final_text = "Или выбери существующий список"
        new_list_markup = types.InlineKeyboardMarkup()
        button_new_list = types.InlineKeyboardButton(text='Добавить', callback_data='item_callback_add_new_' + str(list_of_items[0][2]))
        new_list_markup.add(button_new_list)
        bot.send_message(call.message.chat.id,
                         'Для того что бы добавить новый пункт, жмякни на кнопке "Добавить"',
                         reply_markup=new_list_markup)

    for val in list_of_items:
        button_list = types.InlineKeyboardButton(text=val[1], callback_data='item_callback_select_' + str(val[0]))
        if is_edit_mode:
            button_edit = types.InlineKeyboardButton(text='Переименовать',
                                                     callback_data='item_callback_rename_' + str(val[0]))
            button_delete = types.InlineKeyboardButton(text='Удалить',
                                                       callback_data='item_callback_delete_' + str(val[0]))
            markup.row(button_list, button_edit, button_delete)
        else:
            markup.add(button_list)
    bot.send_message(call.message.chat.id, final_text, reply_markup=markup)

    if not is_edit_mode:
        edit_mode_markup = types.InlineKeyboardMarkup()
        button_edit_mode = types.InlineKeyboardButton(text='Переключиться',
                                                      callback_data='item_callback_turn_on_edit_mode_' + str(list_id))
        edit_mode_markup.add(button_edit_mode)
        bot.send_message(call.message.chat.id, config.editModeTurnOnText, reply_markup=edit_mode_markup)


# Ловит все, что начинается с list_callback
def list_worker(call, list_id):
    data = call.data
    if data.startswith('list_callback_select_'):
        show_list_items(call, list_id, False)
    if data.startswith('list_callback_rename_'):
        send_divider_for_call(call)
        bot.send_message(call.message.chat.id, 'Введите новое название списка')
        bot.register_next_step_handler(call.message, list_rename_list, list_id)
    if data.startswith('list_callback_delete_'):
        send_divider_for_call(call)
        db_delete_list(list_id)
        bot.send_message(call.message.chat.id, 'Список удален')
        show_list(call.message, False)
        # Добавить подтверждение удаления
    if data.startswith('list_callback_add_new'):
        send_divider_for_call(call)
        bot.send_message(call.message.chat.id, 'Введите название нового списка')
        bot.register_next_step_handler(call.message, list_add_new_list)
    if data.startswith('list_callback_turn_on_edit_mode'):
        show_list(call.message, True)


# Ловит все, что начинается с item_callback
def item_worker(call, item_id):
    data = call.data

    if data.startswith('item_callback_rename_'):
        # send_divider_for_call(call)
        bot.send_message(call.message.chat.id, 'Введите новое название списка')
        # bot.register_next_step_handler(call.message, list_rename_list, list_id)
    if data.startswith('item_callback_delete_'):
        send_divider_for_call(call)
        db_delete_item(item_id)
        bot.send_message(call.message.chat.id, 'Пункт удален')
        show_list(call.message, False)
        # Добавить подтверждение удаления
    if data.startswith('item_callback_add_new'):
        send_divider_for_call(call)
        bot.send_message(call.message.chat.id, 'Введите название нового элемента')
        bot.register_next_step_handler(call.message, item_add_new_item, item_id)
    if data.startswith('item_callback_turn_on_edit_mode'):
        list_id = db_get_list_by_item_id(item_id)[0][2]
        show_list_items(call, list_id, True)


def item_add_new_item(message, list_id):
    item_text = message.text
    db_add_new_item(item_text, list_id)
    bot.send_message(message.chat.id, 'Новый пункт добавлен.')
    show_list_items(message, False)


def list_add_new_list(message):
    new_list_name = message.text
    db_add_new_list(new_list_name, message.from_user.id)
    bot.send_message(message.chat.id, 'Новый список с названием "' + new_list_name + '" добавлен.')
    show_list(message, False)


def list_rename_list(message, list_id):
    new_list_name = message.text
    db_rename_list(new_list_name, list_id)
    bot.send_message(message.chat.id, 'Список переименован в ' + new_list_name)
    show_list(message, False)


def send_divider_for_message(message):
    bot.send_message(message.chat.id, emoji.emojize(':fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:', use_aliases=True))


def send_divider_for_call(call):
    bot.send_message(call.message.chat.id, emoji.emojize(':fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire::fire:', use_aliases=True))


# Создать пользователя
def db_upsert_user(user_id, user_login, user_name):
    row = cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,)).fetchone()
    if row is None:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        cursor.execute('INSERT INTO user (login, name, date, user_id) VALUES (?, ?, ?, ?)',
                       (user_login, user_name, dt_string, user_id))
    conn.commit()


# Получить списки
def db_get_list_all(user_id):
    row = cursor.execute('SELECT * FROM lists WHERE user_id = ?', (user_id,)).fetchall()
    conn.commit()
    return row


# Получить список по ид
def db_get_list_by_id(list_id):
    row = cursor.execute('SELECT * FROM lists WHERE id = ?', (list_id,)).fetchall()
    conn.commit()
    return row


# Добавить новый список
def db_add_new_list(list_name, user_id):
    cursor.execute('INSERT INTO lists (name, user_id) VALUES (?, ?)', (list_name, user_id)).fetchall()
    conn.commit()


# Удалить список
def db_delete_list(list_id):
    cursor.execute('DELETE FROM lists WHERE id = ?', (list_id,)).fetchall()
    conn.commit()


# Переименовать список
def db_rename_list(list_name, list_id):
    cursor.execute('UPDATE lists SET name = ? WHERE id = ?', (list_name, list_id)).fetchall()
    conn.commit()


# Получить список по ИД элемента
def db_get_list_by_item_id(item_id):
    row = cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchall()
    conn.commit()
    return row


# Получить элементы списка
def db_get_item_by_list_id(list_id):
    row = cursor.execute('SELECT * FROM items WHERE list_id = ?', (list_id,)).fetchall()
    conn.commit()
    return row


# Добавить новый элемент списка
def db_add_new_item(text, list_id):
    cursor.execute('INSERT INTO items (text, list_id) VALUES (?, ?)', (text, list_id)).fetchall()
    conn.commit()


# Удалить элемент
def db_delete_item(item_id):
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,)).fetchall()
    conn.commit()


bot.polling()