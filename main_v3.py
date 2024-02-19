#version with dictionary handlers

import telebot
from telebot import types
import json
import requests
from validate_email import validate_email
from dotenv import load_dotenv
import os
from datetime import date
from html2text import html2text
import html

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

user_dict = {}

class User:
    def __init__(self, nick):
        self.nick = nick
        self.mail = None
        self.phone = None
        self.tg_nick = None
        self.problem = None
        self.user_id = None

@bot.message_handler(commands=['start'])
def start(message):
    global markup
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('До сервісдеску', url=os.getenv('URL')))
    markup.add(types.InlineKeyboardButton('Звернення у техпідтримку', callback_data='send_task'))
    markup.add(types.InlineKeyboardButton('Перевірити рішення', callback_data='task_solution'))
    bot.send_message(message.chat.id, 'Вас вітає бот техпідтримки JetMonsters!', reply_markup = markup)

@bot.message_handler(commands=['servicedesk'])
def servicedesk(message):
    bot.send_message(message.chat.id, os.getenv('URL'))

@bot.message_handler(commands=['task'])
def task(message):
    bot.send_message(message.chat.id, 'Введіть робочий нік: ')
    bot.register_next_step_handler(message, nickname)

@bot.message_handler(commands=['solution'])
def solutionk(message):
    bot.send_message(message.chat.id, 'Введіть номер таска: ')
    bot.register_next_step_handler(message, task_id)

@bot.callback_query_handler(func=lambda callback: True)
def send_task(callback):
    if callback.data == 'send_task':
        bot.send_message(callback.message.chat.id, 'Введіть робочий нік: ')
        bot.register_next_step_handler(callback.message, nickname)
    if callback.data == 'task_solution':
        bot.send_message(callback.message.chat.id, 'Введіть номер таска: ')
        bot.register_next_step_handler(callback.message, task_id)
    
def nickname(message):
    chat_id = message.chat.id
    nick = message.text
    user = User(nick)
    user_dict[chat_id] = user
    bot.send_message(message.chat.id, 'Введіть робочу пошту:')
    bot.register_next_step_handler(message, mailbox)
def mailbox(message):
    chat_id = message.chat.id 
    mail = message.text
    user = user_dict[chat_id]
    user.mail = str(mail).lower()
    if validate_email(mail):
        bot.send_message(message.chat.id, 'Введіть телефон:')
        bot.register_next_step_handler(message, telephone)
    else:
        bot.send_message(message.chat.id, 'Такої пошти не існує.', reply_markup = markup)
def telephone(message):
    chat_id = message.chat.id 
    phone = message.text
    user = user_dict[chat_id]
    user.phone = phone
    bot.send_message(message.chat.id, 'Опишіть проблему:')
    bot.register_next_step_handler(message, get_problem)
def get_problem(message):
    chat_id = message.chat.id
    problem = message.text
    user = user_dict[chat_id]
    user.problem = problem
    user.tg_nick = message.from_user.first_name
    bot.send_message(message.chat.id, 'Результат: ')
    bot.send_message(message.chat.id, user.nick)
    bot.send_message(message.chat.id, user.mail)
    bot.send_message(message.chat.id, user.phone)
    bot.send_message(message.chat.id, user.tg_nick)
    bot.send_message(message.chat.id, user.problem)

#creating task
    base_url = os.getenv('URL_API')
    app_token = os.getenv('A_TOKEN')
    user_token = os.getenv('U_TOKEN')
    requesttypes_id = 8 #request type in GLPI = Bot
    type_1 = 1

    init_uri = 'initSession'
    response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
    session_token = response.json()
    session_token = session_token['session_token']

    headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}
   
    ticket_uri = '/search/User?criteria[0][field]=5&criteria[0][searchtype]=contains&criteria[0][value]=' + user.mail + '&forcedisplay[0]=1&forcedisplay[1]=2&forcedisplay[2]=5&forcedisplay[3]=9&forcedisplay[4]=14&forcedisplay[5]=80'
    post_ticket = requests.get(url="{}{}".format(base_url,ticket_uri), headers=headers)
    pt = post_ticket.json()
    if pt['totalcount'] > 0: 
        pt = pt['data']
        pt = pt[0]
        user.user_id = pt['2']
#        print('UserID = ', user.user_id)
    else:
        user.user_id = 142
#        print('Not found, setting UserID =', user_id)

    ticket_input = {"input": {"name": "Ticket from " + user.nick, 
                              "requesttypes_id": requesttypes_id,
                              "_users_id_requester": user.user_id, #request user in GLPI 
                              "type": type_1, #ticket type Incident in GLPI
                              "content": "Звернення з телеграму: \n" 
                              + "Робочий нік: " + user.nick + "\n" 
                              + "Контакт у телеграмі: " + user.tg_nick + "\n" 
                              + "Пошта: " + user.mail + "\n" 
                              + "Телефон: " + user.phone + "\n" 
                              + "Опис проблеми: " + user.problem}}

    ticket_uri = 'Ticket'
    post_ticket = requests.post(url="{}{}".format(base_url,ticket_uri), headers=headers, data=json.dumps(ticket_input))
    pt = post_ticket.json()
    pt = pt['id']
    bot.send_message(message.chat.id, 'Тікет створено, номер: ' + str(pt) + '\n' + 'Очікуйте вирішення вашого звернення.' + '\n' + 'До побачення!', reply_markup = markup)

    kill_uri = 'killSession'
    kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
    kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)

def task_id(message):
    base_url = os.getenv('URL_API')
    app_token = os.getenv('A_TOKEN')
    user_token = os.getenv('U_TOKEN')
    init_uri = 'initSession'
    response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
    session_token = response.json()
    session_token = session_token['session_token']
    headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}

    chat_id = message.chat.id
    ticket_id = message.text

    ticket_uri = 'Ticket/' + str(ticket_id) + '/ITILSolution/'
    print(ticket_uri)
    post_ticket = requests.get(url="{}{}".format(base_url,ticket_uri), headers=headers)
    if post_ticket:
        pt = post_ticket.json()
        if pt:
            pt = pt[0]
            pt = pt['content']
            pt = html.unescape(pt)
            pt = html2text(pt)
            bot.send_message(chat_id, pt, reply_markup = markup)
        else:
            bot.send_message(chat_id,'Ще не вирішено', reply_markup = markup)
    else:
        bot.send_message(chat_id,'Рішення немає', reply_markup = markup)

    kill_uri = 'killSession'
    kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
    kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
       

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.polling(non_stop=True, interval=0)