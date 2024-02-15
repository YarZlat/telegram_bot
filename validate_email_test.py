#for testing mail validation

from validate_email import validate_email

mail = 'discipler7@gmail.com'
valid = validate_email(mail, verify=True)
print(valid)