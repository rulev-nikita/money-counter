import datetime
import sqlite3
import json
import csv
from pathlib import Path

import telebot

import config
import sql_code
from config import basic_categories

bot = telebot.TeleBot(config.token)

user_data = {}


def check_auth(f):
    def deco(message):
        if message.from_user.id not in user_data: 
            user_data[message.from_user.id] = {
                'step': 'default', 
                'date': '', 
                'categories': '', 
                'value': '', 
                'description': '',
            }
        f(message)
    return deco


@bot.message_handler(commands = ['start', 'home'])
@check_auth
def start_message(message):
    start_menu(message)

@bot.callback_query_handler(func = lambda call: True)
@check_auth
def query_handler(call):
    if call.data == "Settings":
        settings(call)

    if call.data == "Select a date and enter expenses":
        choose_time(call)
    
    if call.data == "Today":
        time_today(call)    

    if call.data == "Yesterday":
        time_yesterday(call)

    if call.data == "Enter date":
        time_enter_date_first_step(call)

    if call.data == "Add category":
        add_category_first_step(call)

    if call.data == "Delete all categories":
        delete_categories(call)

    if call.data == "Show all categories":
        show_all_categories(call)

    if call.data == "Export my data in csv":
        export_csv(call)

    if call.data in user_data[call.from_user.id]['categories']:
        choose_category(call)

@bot.message_handler(func=lambda message: True)
@check_auth
def default(message):
    if user_data[message.from_user.id]["step"] == "date":
        time_enter_date_second_step(message)

    elif  user_data[message.from_user.id]["step"] == "category":
        add_category_second_step(message)

    elif  user_data[message.from_user.id]["step"] == "expenses":
        expenses(message)

    else:
        bot.send_message(message.chat.id, text = "вы забрели куда-то не туда, нажмите /home")

def create_button(text):
    return telebot.types.InlineKeyboardButton(text = text, callback_data = text)

def start_menu(message):
    if sql_code.check_auth(message.from_user.id):
        text = "Welcome! Choose your next step"
    else:
        for i in basic_categories:
            sql_code.add_category(message.from_user.id, i)   
        text = "This is your first time. Now you use basic categorise. You can use settings to change them"
    start_menu = telebot.types.InlineKeyboardMarkup()
    start_menu.add(create_button("Select a date and enter expenses"))
    start_menu.add(create_button("Settings"))
    start_menu.add(create_button("Export my data in csv"))
    bot.send_message(message.chat.id, text = text, reply_markup = start_menu)

def settings(call):
    settings = telebot.types.InlineKeyboardMarkup()
    settings.add(create_button("Add category"))
    settings.add(create_button("Delete all categories"))
    settings.add(create_button("Show all categories"))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Settings")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = settings)

def choose_time(call):
    choose_time = telebot.types.InlineKeyboardMarkup()
    choose_time.add(create_button("Today"))
    choose_time.add(create_button("Yesterday"))
    choose_time.add(create_button("Enter date"))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Select a date")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = choose_time)

def time_today(call):
    date = datetime.datetime.now()
    date = f'{date.strftime("%d.%m.%Y")}'
    user_data[call.from_user.id]['date'] = date # потенциальный косяк
    time_today = telebot.types.InlineKeyboardMarkup()
    time_today.add(create_button(date))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Selected date")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = time_today)
    bot.send_message(call.message.chat.id, text = "Enter your expenses")
    user_data[call.from_user.id]["step"] = "expenses"

def time_yesterday(call):
    date_temp = datetime.datetime.now()
    date = f'{date_temp.day - 1}.{date_temp.month}.{date_temp.year}'
    user_data[call.from_user.id]['date'] = date
    time_yesterday = telebot.types.InlineKeyboardMarkup()
    time_yesterday.add(create_button(date))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Selected date")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = time_yesterday)
    bot.send_message(call.message.chat.id, text = "Enter your expenses")
    user_data[call.from_user.id]["step"] = "expenses"

def time_enter_date_first_step(call):
    user_data[call.from_user.id]["step"] = "date"
    bot.send_message(call.message.chat.id, text = "Enter your date")

def time_enter_date_second_step(message):
    date = message.text
    try: 
        datetime.datetime.strptime(date, "%d.%m.%Y").date()
    except ValueError:
        date = "error"
        bot.send_message(message.chat.id, "Enter correct date")
    else:
        user_data[message.from_user.id]["date"] = f'{date}'
        user_data[message.from_user.id]["step"] = "expenses"
        time_enter_date_first_step = telebot.types.InlineKeyboardMarkup()
        time_enter_date_first_step.add(create_button(f'{date}'))
        bot.send_message(message.chat.id, text = "Selected date", reply_markup = time_enter_date_first_step)
        bot.send_message(message.chat.id, text = "Enter your expenses")

def add_category_second_step(message):
    sql_code.add_category(message.from_user.id, message.text)
    settings = telebot.types.InlineKeyboardMarkup()
    settings.add(create_button("Add category"))
    settings.add(create_button("Delete all categories"))
    settings.add(create_button("Show all categories"))
    bot.send_message(message.chat.id, reply_markup = settings, text = "You added new category")

def add_category_first_step(call):
    bot.send_message(call.message.chat.id, text = "Send your category")
    user_data[call.from_user.id]["step"] = "category"

def delete_categories(call):
    sql_code.del_categories(call.from_user.id)
    settings = telebot.types.InlineKeyboardMarkup()
    settings.add(create_button("Add category"))
    settings.add(create_button("Delete all categories"))
    settings.add(create_button("Show all categories"))
    bot.send_message(call.message.chat.id, reply_markup = settings, text = "Your catigories have been deleted")

def show_all_categories(call):
    categories = sql_code.show_categories(call.from_user.id)
    if categories == []:
        bot.send_message(call.message.chat.id, "You don't have any categories")
    else:
        text = f'Categories: {categories[0][0]}'
        for i in range(1, len(categories)):
            text = f'{text}, {categories[i][0]}'
        bot.send_message(call.message.chat.id, text = text)
        settings = telebot.types.InlineKeyboardMarkup()
        settings.add(create_button("Add category"))
        settings.add(create_button("Delete all categories"))
        settings.add(create_button("Show all categories"))
        bot.send_message(call.message.chat.id, reply_markup = settings, text = "settings")

def expenses(message):
    categories = []
    text = message.text
    categories_temp = sql_code.show_categories(message.from_user.id)
    cat = telebot.types.InlineKeyboardMarkup()
    for i in range(len(categories_temp)):
        cat.add(create_button(categories_temp[i][0]))
        categories.append(categories_temp[i][0])
    user_data[message.from_user.id]['categories'] =  categories
    
    list_temp = message.text.split(None, maxsplit=1)
    
    try:
        value = float(list_temp[0].replace(",", "."))
    except ValueError:
        bot.send_message(message.chat.id, "Введи корректное значение")
        return
    
    user_data[message.from_user.id]["value"] = value
    if len(list_temp) == 1:
        user_data[message.from_user.id]["descrription"] = ""
    
    else:   
        user_data[message.from_user.id]["description"] = list_temp[1]

    bot.send_message(message.chat.id, reply_markup = cat, text = text) 


def choose_category(call):
    choose_category = telebot.types.InlineKeyboardMarkup()
    text = f'{user_data[call.from_user.id]["value"]} {user_data[call.from_user.id]["description"]}'
    for i in user_data[call.from_user.id]['categories']:
        if call.data == i:
            choose_category.add(create_button(i))
            sql_write(call)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = text)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = choose_category)

def sql_write(call):
    user_id = call.from_user.id
    name = call.data
    value = user_data[call.from_user.id]["value"]
    description = user_data[call.from_user.id]["description"]
    time = user_data[call.from_user.id]["date"]
    sql_code.add_expenses(user_id, name, value, description, time)

def export_csv(call):
    user_id = call.from_user.id
    data = sql_code.data_for_export(user_id)
    folder = Path('csv_files')

    if not folder.exists():
        folder = Path('csv_files').mkdir(parents=True, exist_ok=True)

    name = folder/f'{call.from_user.id}_{datetime.datetime.now().strftime("%d.%m.%Y")}.csv'
    with open(name, 'w', newline='') as fin:
        writer = csv.writer(fin, dialect='excel')
        writer.writerow(["Category", "Value", "Description", "Date"])
        writer.writerows(data)
            
    doc = open(name, 'r')
    bot.send_document(call.message.chat.id, doc)

bot.polling()