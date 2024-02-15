#test mail search

import requests
from dotenv import load_dotenv
import os
from html2text import html2text
import html

load_dotenv()

base_url = os.getenv('URL_API')
app_token = os.getenv('A_TOKEN')
user_token = os.getenv('U_TOKEN')
init_uri = 'initSession'
response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
session_token = response.json()
session_token = session_token['session_token']
headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}

ticket_id = 641

ticket_uri = 'Ticket/' + str(ticket_id) + '/ITILSolution/'
print(ticket_uri)
post_ticket = requests.get(url="{}{}".format(base_url,ticket_uri), headers=headers)
pt = post_ticket.json()
pt = pt[0]
pt = pt['content']
pt = html.unescape(pt)
pt = html2text(pt)
print(pt)

kill_uri = 'killSession'
kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
