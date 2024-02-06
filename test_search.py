#version with dictionary handlers

import requests
from dotenv import load_dotenv
import os

load_dotenv()

base_url = os.getenv('URL_API')
app_token = os.getenv('A_TOKEN')
user_token = os.getenv('U_TOKEN')
init_uri = 'initSession'
response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
session_token = response.json()
session_token = session_token['session_token']
headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}

mail = 'cetan@jetmonsters.me'   
ticket_uri = 'User/10'
post_ticket = requests.get(url="{}{}".format(base_url,ticket_uri), headers=headers)
pt = post_ticket.json()
print(pt)

kill_uri = 'killSession'
kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
