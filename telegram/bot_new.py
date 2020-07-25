import datetime
import sqlite3
import json
import csv

import telebot

import config
import sql_code

bot = telebot.TeleBot(config.token)

user_data = {}

basic_categories = ["food", "healt", "transport and housing", "presents", "clothes"]

@bot.message_handler(commands = ['start'])
def start_message(message):
    start_menu(message)

@bot.callback_query_handler(func = lambda call: True)
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
        add_category()

    if call.data == "Delete all categories":
        delete_categories(call)

    if call.data == "Show all categories":
        show_all_categories(call)
@bot.message_handler(func=lambda message: True)
def default(message):
    print(message.from_user.id)
    print(user_data)
    if user_data[message.from_user.id]["step"] == "date":
        time_enter_date_second_step(message)

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
    user_data[call.message.from_user.id] = {'date': date}
    time_today = telebot.types.InlineKeyboardMarkup()
    time_today.add(create_button(date))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Selected date")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = time_today)
    bot.send_message(call.message.chat.id, text = "Enter your expenses")

def time_yesterday(call):
    date_temp = datetime.datetime.now()
    date = f'{date_temp.day - 1}.{date_temp.month}.{date_temp.year}'
    user_data[call.message.from_user.id] = {'date': date}
    time_yesterday = telebot.types.InlineKeyboardMarkup()
    time_yesterday.add(create_button(date))
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Selected date")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = time_yesterday)
    bot.send_message(call.message.chat.id, text = "Enter your expenses")

def time_enter_date_first_step(call):
    user_data[call.from_user.id] = {'step': 'date'}
    bot.send_message(call.message.chat.id, text = "Enter your date")
    print(user_data)

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

def add_category(call):
    pass

def delete_categories(call):
    sql_code.del_categories(call.from_user.id)
    settings = telebot.types.InlineKeyboardMarkup()
    settings.add(create_button("Add category"))
    settings.add(create_button("Delete all categories"))
    settings.add(create_button("Show all categories"))
    bot.send_message(call.message.chat.id, reply_markup = settings, text = "Your catigories have been deleted")

def show_all_categories(call):
    categories = sql_code.show_categories(call.from_user.id)
    print(categories)
    if categories == []:
        bot.send_message(call.message.chat.id, "You have not any categories")
    else:
        text = f'Categories: {categories[0][0]}'
        for y in range(1, len(categories)):
            text = f'{text}, {categories[y][0]}'
        bot.send_message(call.message.chat.id, text = text)
        settings = telebot.types.InlineKeyboardMarkup()
        settings.add(create_button("Add category"))
        settings.add(create_button("Delete all categories"))
        settings.add(create_button("Show all categories"))
        bot.send_message(call.message.chat.id, reply_markup = settings, text = "settings")

bot.polling()