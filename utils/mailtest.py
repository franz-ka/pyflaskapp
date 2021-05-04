import sys
import os
app_path = os.path.abspath(__file__ + "/../../instance/")
print('Usando path =', str(app_path))
sys.path.append(str(app_path))

import config
import smtplib

# igual qe en alarmas.py
s = smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT)
s.ehlo()
s.starttls()
s.ehlo()
print(f'Probando credenciales: {config.MAIL_USU}/{config.MAIL_PASS[:5]}*****')
s.login(config.MAIL_USU, config.MAIL_PASS)
message = 'hola\ntest'
s.sendmail(config.MAIL_FROM, config.MAIL_TO, message.encode('utf8'))
s.quit()
