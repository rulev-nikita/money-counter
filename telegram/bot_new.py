import datetime
import sqlite3
import json
import csv

import telebot

import config

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands = ['start'])
def start_message(message):
    start_menu(message)

@bot.callback_query_handler(func = lambda call: True)
def query_handler(call):
    if call.data == "Settings":
        settings(call)

    if call.data == "Enter expenses":
        pass

def create_button(text):
    return telebot.types.InlineKeyboardButton(text = text, callback_data = text)

def start_menu(message):
    if True:
        text = "Welcome! Choose your next step"
    else:    
        text = "This is your first time. Now you use basic categorise. You can use settings to change them"

    start_menu = telebot.types.InlineKeyboardMarkup()
    start_menu.add(create_button("Choose time and enter expenses"))
    start_menu.add(create_button("Settings"))
    bot.send_message(message.chat.id, text = text, reply_markup = start_menu)

def settings(call):
     settings = telebot.types.InlineKeyboardMarkup()
     settings.add(create_button("Add category"))
     settings.add(create_button("Remove category"))
     bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Settings")
     bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = settings)

bot.polling()