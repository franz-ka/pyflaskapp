from apscheduler.schedulers.background import BackgroundScheduler
from flask1.alarmas import check_alarmas
from flask1.backup_db import check_backup_db

from flask1 import create_app
app = create_app()

if not app.config['DEBUG_FLASK']:
    schedAlarmas = BackgroundScheduler(daemon=True)
    # add_job - https://apscheduler.readthedocs.io/en/stable/modules/schedulers/base.html#apscheduler.schedulers.base.BaseScheduler.add_job
    schedAlarmas.add_job(check_alarmas, 'interval', minutes=60, args=[app])
    schedAlarmas.start()

    schedBackupDB = BackgroundScheduler(daemon=True)
    schedBackupDB.add_job(check_backup_db, 'interval', hours=2, args=[app])
    schedBackupDB.start()

app.run(debug=app.config['DEBUG_FLASK'], host=app.config['APP_HOST'], port=app.config['APP_PORT'])
