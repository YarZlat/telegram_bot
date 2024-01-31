#for testing file write-read

import json
import os
from datetime import date
 
today = date.today()
print("Today's date:", today)

nick = ['John', 'Mary']
mail = ['john@gmail.com', 'mary@gmail.com']
to_json = {'nick': nick, 'mail': mail}

filename = str(nick[0])+str(today)+'.json'
with open(filename, 'w') as f:
    json.dump(to_json, f)

with open(filename) as f:
    templates = json.load(f)
    print(type(templates['mail']))
    print(templates['mail'][0])

#os.remove(filename)