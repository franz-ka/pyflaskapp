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

def check_backup_db():    
    try:
        last_sent_str = open(instance_path + _bkup_fname,"r").readline().strip()
        last_sent = datetime.strptime(last_sent_str, "%Y-%m-%d %H:%M:%S.%f")
    except (FileNotFoundError, ValueError):
        last_sent = datetime.min

    dtnow = datetime.now()
    #print(dtnow, last_sent)
    #print(days_between(last_sent, dtnow), _backup_db_dias_intervalo)
    if days_between(last_sent, dtnow) >= _backup_db_dias_intervalo:
        try: send_backup_db()
        except Exception as e:
            print('Error: Backup de la BBDD no pudo ser envíado')
            raise(e)
    else:
        print('Backup de la BBDD al día')

def send_backup_db():    
    msg = MIMEMultipart()
    msg['From'] = "stockcogonauts@gmail.com"
    msg['To'] = "bungew@gmail.com"
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Backup de la BBDD"

    msg.attach(MIMEText("Backup de la BBDD al día de la fecha adjunto."))

    zf = zipfile.ZipFile(instance_path + '/flask1.db.zip', mode='w')
    zf.write(instance_path + '/flask1.db', arcname='flask1.db', compress_type=_zcompression)
    zf.close()
    part = MIMEApplication(open(instance_path + '/flask1.db.zip', 'rb').read())
    part['Content-Disposition'] = 'attachment; filename="flask1.db.zip"'
    msg.attach(part)
        
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login("stockcogonauts@gmail.com", "Markdijono1375$")
    s.sendmail("stockcogonauts@gmail.com", "bungew@gmail.com", msg.as_string())
    s.quit()
    
    print('Backup de la BBDD envíado')
    
    dtnow = datetime.now()
    open(instance_path + _bkup_fname,"w+").write(str(dtnow))
    
