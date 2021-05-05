import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import os
from datetime import datetime
import zipfile
try:
    import zlib
    _zcompression = zipfile.ZIP_DEFLATED
except:
    _zcompression = zipfile.ZIP_STORED

_bkup_fname ='/last-backup-sent.txt'
_backup_db_dias_intervalo = 1
app_path = os.path.abspath(__file__ + "/../../")
instance_path = app_path + '/instance'

def days_between(d1, d2):
    return abs((d2 - d1).days)

def check_backup_db(app):
    try:
        last_sent_str = open(instance_path + _bkup_fname,"r").readline().strip()
        last_sent = datetime.strptime(last_sent_str, "%Y-%m-%d %H:%M:%S.%f")
    except (FileNotFoundError, ValueError):
        last_sent = datetime.min

    dtnow = datetime.now()
    #print(dtnow, last_sent)
    #print(days_between(last_sent, dtnow), _backup_db_dias_intervalo)
    if days_between(last_sent, dtnow) >= _backup_db_dias_intervalo:
        try: send_backup_db(app)
        except Exception as e:
            print('Error: Backup de la BBDD no pudo ser envíado')
            raise(e)
    else:
        print('Backup de la BBDD al día')

def send_backup_db(app):
    msg = MIMEMultipart()
    msg['From'] = app.config["MAIL_FROM"]
    msg['To'] = app.config["MAIL_TO"]
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Cogosys - Backup de la BBDD"

    msg.attach(MIMEText("Se ha generado el backup del día de la BBDD."))

    zf = zipfile.ZipFile(instance_path + '/flask1.db.zip', mode='w')
    zf.write(instance_path + '/flask1.db', arcname='flask1.db', compress_type=_zcompression)
    zf.close()
    part = MIMEApplication(open(instance_path + '/flask1.db.zip', 'rb').read())
    part['Content-Disposition'] = 'attachment; filename="flask1.db.zip"'
    msg.attach(part)

    s = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(app.config["MAIL_USU"], app.config["MAIL_PASS"])
    s.sendmail(app.config["MAIL_FROM"], app.config["MAIL_TO"], msg.as_string())
    print('Mail - Backup de la BBDD envíado')
    s.quit()

    dtnow = datetime.now()
    open(instance_path + _bkup_fname,"w+").write(str(dtnow))
