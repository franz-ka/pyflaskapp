#FLASK
SECRET_KEY='dev'
TEMPLATES_AUTO_RELOAD = True
#MIAS
DEBUG_SQL = False
DEBUG_FLASK = True
APP_HOST = '127.0.0.1'
APP_PORT = 5000
#APP_HOST = '192.168.1.17'
#APP_PORT = 61220
MAIL_SERVER="smtp.gmail.com"
MAIL_PORT=587
MAIL_USU="xxx@xxx"
# para contraseña de gmail usar "App Passwords", no la contraseña directa
# https://support.google.com/accounts/answer/185833#app-passwords
MAIL_PASS="xxx"
MAIL_FROM="xxx@xxx"
# para alarmas de stock y backups de BBDD
MAIL_TO="xxx@xxx"
# para reporte de errores
MAIL_TO_ERRORS="xxx@xxx"
