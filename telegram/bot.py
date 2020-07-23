import datetime
import sqlite3
import json
import csv

import telebot

import config


bot = telebot.TeleBot(config.token)


user_data = {}


def check_auth(f):
	def deco(message):
		if message.from_user.id not in user_data: 
			user_data[message.from_user.id] = {
				'step': 'default', 
				'date': '', 
				'category': '', 
				'value': '', 
				'description': '',
			}
		f(message)
	return deco


@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет, этот бот поможет тебе быть в курсе о своих тратах')
	user_data[message.from_user.id] = {'step': 'default' , 'date': '', 'category': '', 'value': '', 'description': ''}


@bot.message_handler(commands=['today'])
@check_auth
def today_command(message):
	date = datetime.datetime.now()
	bot.send_message(message.chat.id, date.strftime("%d.%m.%Y"))
	user_data[message.from_user.id]["date"] = f'{date.strftime("%d.%m.%Y")}'
	user_data[message.from_user.id]["step"] = "expenses"


@bot.message_handler(commands=['yesterday'])
@check_auth
def yesterday_command(message):
	date_temp = datetime.datetime.now()
	date = f"{date_temp.day - 1}.{date_temp.month}.{date_temp.year}"
	bot.send_message(message.chat.id, date)
	user_data[message.from_user.id]["date"] = f'{date}'
	user_data[message.from_user.id]["step"] = "expenses"

@bot.message_handler(commands=['enter_date'])
@check_auth
def enter_date_command(message):
	user_data[message.from_user.id]["step"] = "enter_date"
	bot.send_message(message.chat.id, "enter your date")

@bot.message_handler(commands=['export_csv'])
@check_auth
def export_csv(message):
	connection = sqlite3.connect(config.my_db, isolation_level=None)
	cursor = connection.cursor()
	data = cursor.execute('SELECT * FROM expenses')

	name = f'csv_files\\{datetime.datetime.now().strftime("%d.%m.%Y")}.csv'

	with open(name, 'w', newline='') as fin:
		writer = csv.writer(fin, dialect='excel')
		writer.writerow(["id", "user_id", "date", "category", "value", "descrription"])
		writer.writerows(data)

	doc = open(name, 'r')
	bot.send_document(message.chat.id, doc)



@bot.message_handler(func=lambda message: True)
@check_auth
def default(message):
	if user_data[message.from_user.id]["step"] == "enter_date":
		enterring_date(message)
	
	elif user_data[message.from_user.id]["step"] == "expenses":
		expenses(message)

	else:
		bot.send_message(message.chat.id, "Введи корректную комманду")

@bot.callback_query_handler(func = lambda call: True)
def query_handler(call):
	if call.data == "skip":
		return

	callback_data = json.loads(call.data)
	user_id = callback_data["user_id"]
	category = callback_data["category"]
	text = name_by_category(category)
	user_data[user_id]["category"] = category
	
	categories = telebot.types.InlineKeyboardMarkup(row_width=1)
	categories.add(telebot.types.InlineKeyboardButton(text = text, callback_data="skip"))

	bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=categories)
	
	sql_write(user_id, user_data)


def enterring_date(message):
	date = message.text
	try: 
		datetime.datetime.strptime(date, "%d.%m.%Y").date()
	except ValueError:
		date = "error"
		bot.send_message(message.chat.id, "Введи норм дату")
	else:
		user_data[message.from_user.id]["date"] = f'{date}'
		user_data[message.from_user.id]["step"] = "expenses"
		bot.send_message(message.chat.id, date)


def name_by_category(category):
	if category == "good_food":
		return "Нормальная еда"
	elif category == "bad_food":
		return "Хотелка еда"
	elif category == "electronics":
		return "Электроника"
	elif category == "clothes":
		return "Одежда"
	elif category == "attractions":
		return "Развлечения"

def create_button(user_id, category):
	callback_data = {
		"user_id": user_id,
		"category": category, 
	}	
	return telebot.types.InlineKeyboardButton(text=name_by_category(category), callback_data=json.dumps(callback_data))

def expenses(message):
		user_id = message.from_user.id
		categories = telebot.types.InlineKeyboardMarkup()
		categories.add(create_button(user_id, "good_food"))
		categories.add(create_button(user_id, "bad_food"))
		categories.add(create_button(user_id, "electronics"))
		categories.add(create_button(user_id, "clothes"))
		categories.add(create_button(user_id, "attractions"))

		list_temp = message.text.split(None, maxsplit=1)
		
		try:
			value = float(list_temp[0].replace(",", "."))
		except ValueError:
			bot.send_message(message.chat.id, "Введи корректное значение")
			return


		bot.send_message(message.chat.id, message.text, reply_markup = categories)
		
		user_data[message.from_user.id]["value"] = value
		if len(list_temp) == 1:
			user_data[message.from_user.id]["descrription"] = ""
		
		else:	
			user_data[message.from_user.id]["description"] = list_temp[1]

def sql_write(user_id, user_data):

	connection = sqlite3.connect(config.my_db, isolation_level=None)
	cursor = connection.cursor()
	cursor.execute('''INSERT INTO expenses (user_id, "date", category, value, description) 
					VALUES(?, ?, ?, ?, ?)''', (user_id, user_data[user_id]["date"], user_data[user_id]["category"], \
					user_data[user_id]["value"], user_data[user_id]["description"]))

	cursor.execute('SELECT * FROM expenses')

	rows = cursor.fetchall()

	for row in rows:
		print(row)


bot.polling()
