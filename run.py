from apscheduler.schedulers.background import BackgroundScheduler
from flask1.alarmas import check_alarmas

sched = BackgroundScheduler(daemon=True)
sched.add_job(check_alarmas, 'interval', minutes=60)
sched.start()


from flask1 import create_app
app = create_app()
app.run(debug=app.config['DEBUG_FLASK'], host=app.config['APP_HOST'], port=app.config['APP_PORT'])