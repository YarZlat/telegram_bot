#version with storing data in json-file

import telebot
from telebot import types
import json
import requests
from validate_email import validate_email
from dotenv import load_dotenv
import os
from datetime import date

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

@bot.message_handler(commands=['start'])
def start(message):
    global markup
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('До сервісдеску', url=os.getenv('URL')))
    markup.add(types.InlineKeyboardButton('Звернення у техпідтримку', callback_data='send_task'))
    bot.send_message(message.chat.id, 'Вас вітає бот техпідтримки JetMonsters!', reply_markup = markup)

@bot.message_handler(commands=['servicedesk'])
def servicedesk(message):
    bot.send_message(message.from_user.id, os.getenv('URL'))

@bot.message_handler(commands=['task'])
def task(message):
    bot.send_message(message.from_user.id, 'Введіть робочий нік: ')
    bot.register_next_step_handler(message, nickname)

@bot.callback_query_handler(func=lambda callback: True)
def send_task(callback):
    if callback.data == 'send_task':
        bot.send_message(callback.message.chat.id, 'Введіть робочий нік: ')
        bot.register_next_step_handler(callback.message, nickname)
def nickname(message):
    global nick
    nick = message.text
    bot.send_message(message.from_user.id, 'Введіть робочу пошту:')
    bot.register_next_step_handler(message, mailbox)
def mailbox(message):
    global mail 
    mail = message.text
    print(validate_email(mail))
    if validate_email(mail):
        bot.send_message(message.from_user.id, 'Введіть телефон:')
        bot.register_next_step_handler(message, telephone)
    else:
        bot.send_message(message.from_user.id, 'Такої пошти не існує.', reply_markup = markup)
def telephone(message):
    global phone
    phone = message.text
    bot.send_message(message.from_user.id, 'Опишіть проблему:')
    bot.register_next_step_handler(message, get_problem)
def get_problem(message):
    global problem
    problem = message.text
    bot.send_message(message.from_user.id, 'Результат: ')
    bot.send_message(message.from_user.id, nick)
    bot.send_message(message.from_user.id, mail)
    bot.send_message(message.from_user.id, phone)
    bot.send_message(message.from_user.id, problem)

#creating json and writing it to file
    data_json = {'nick': nick, 'mail': mail, 'phone': phone, 'problem': problem}
    today = date.today()
    filename = str(nick)+str(today)+'.json'
    with open(filename, 'w') as f:
        json.dump(data_json, f)

#creating task
    base_url = os.getenv('URL_API')
    app_token = os.getenv('A_TOKEN')
    user_token = os.getenv('U_TOKEN')
    requesttypes_id = 8
    type_1 = 1

    init_uri = 'initSession'
    response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
    session_token = response.json()
    session_token = session_token['session_token']

    headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}

#reading from file
    with open(filename) as f:
        loaded_data = json.load(f)
        ticket_input = {"input": {"name": "Ticket from " + loaded_data['nick'], 
                                  "requesttypes_id": requesttypes_id,
                                  "_users_id_requester": 142,
                                  "type": type_1,
                                  "content": "Звернення з телеграму: \n"
                                  + "Робочий нік: " + loaded_data['nick'] + "\n"
                                  + "Контакт у телеграмі: " + str(message.from_user.first_name) + "\n"
                                  + "Пошта: " + loaded_data['mail'] + "\n"
                                  + "Телефон: " + loaded_data['phone'] + "\n"
                                  + "Опис проблеми: " + loaded_data['problem']}}

    ticket_uri = 'Ticket'
    post_ticket = requests.post(url="{}{}".format(base_url,ticket_uri), headers=headers, data=json.dumps(ticket_input))
    pt = post_ticket.json()
    pt = pt['id']
    bot.send_message(message.from_user.id, 'Тікет створено, номер: ' + str(pt) + '\n' + 'Очікуйте вирішення вашого звернення.' + '\n' + 'До побачення!', reply_markup = markup)
#killing session
    kill_uri = 'killSession'
    kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
    kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
#deleting file after ticket created
#    os.remove(filename)

bot.polling(non_stop=True, interval=0)