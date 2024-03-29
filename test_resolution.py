#test mail search

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

#ticket_uri = '/search/User?criteria[0][field]=5&criteria[0][searchtype]=contains&criteria[0][value]=' + mail + '&forcedisplay[0]=1&forcedisplay[1]=2&forcedisplay[2]=5&forcedisplay[3]=9'
ticket_uri = '//search/User?criteria[0][field]=5&criteria[0][searchtype]=contains&criteria[0][value]=' + mail + '&forcedisplay[0]=1&forcedisplay[1]=2&forcedisplay[2]=5&forcedisplay[3]=76676' 
post_ticket = requests.get(url="{}{}".format(base_url,ticket_uri), headers=headers)
pt = post_ticket.json()
print(pt)

if pt['totalcount'] > 0: 
    pt = pt['data']
    pt = pt[0]
    tg = pt['76676']
    print('TG =',tg)
else:
    print('Not found')

kill_uri = 'killSession'
kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
