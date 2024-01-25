import json
import requests
#import glpi_api

base_url = 'https://servicedesk.jetmonsters.me/apirest.php/'
app_token = 'VdrRJ55LZfo82Fb6uMfOlhaozeFk5fNxqPFMNa12'
user_token = 'YwfZ2Nlr2KAd4umsLsSDGuDUb3VshZxUEltJswnI'

requesttypes_id = 8
type_1 = 1

init_uri = 'initSession'
response = requests.get(url="{}{}".format(base_url,init_uri), params={"Content-Type": "application/json","user_token": user_token})
session_token = response.json()
session_token = session_token['session_token']
print(session_token)

headers = {"Session-Token":session_token, "App-Token":app_token, "Content-Type": "application/json"}
   
ticket_input = {"input": {"name": "Bot-Ticket", "requesttypes_id": requesttypes_id, "type": type_1,"content": "Task"}}

ticket_uri = 'Ticket'
post_ticket = requests.post(url="{}{}".format(base_url,ticket_uri), headers=headers, data=json.dumps(ticket_input))
pt = post_ticket.json()
pt = pt['id']
print(pt)

kill_uri = 'killSession'
kill_headers = {'Content-Type': 'application/json','App-Token': app_token,'Session-Token': session_token}
kill_session = requests.get(url="{}{}".format(base_url,kill_uri), headers=kill_headers)
print(kill_session.text)

