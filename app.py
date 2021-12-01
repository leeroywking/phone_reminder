from flask import Flask, send_file, request, Response
from datetime import datetime as dt
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from schedule_tasks import PendingTaskActions
from twilio_logic import make_call, make_text, make_play

import os
from flask_mongoengine import MongoEngine
from sms_handler import sms_handler



# from werkzeug.utils import send_file, send_from_directory
app = Flask(__name__, static_url_path="/static")

DB_NAME = os.environ['DB_NAME']
DB_HOST = os.environ['DB_HOST']
DB_PORT = int(os.environ['DB_PORT'])
DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]

app.config['MONGODB_SETTINGS'] = {
    'db': DB_NAME,
    'host': DB_HOST,
    'port': DB_PORT,
}
db = MongoEngine()
db.init_app(app)


class Users(db.Document):
    phone_number = db.StringField()
    preferred_name = db.StringField()
    water_goal = db.IntField()
    water_drank = db.IntField()
    total_sms_received = db.IntField()
    total_sms_sent = db.IntField()
    total_calls_received = db.IntField()
    total_calls_sent = db.IntField()
    received_sms_messages = db.StringField()
    time_zone = db.StringField()

class PendingTasks(db.Document):
    run_at_time = db.DateTimeField()
    phone_number = db.StringField()
    run_action = db.StringField()

@app.route("/")
def hello():
  return "Hello World!"


@app.post("/play_twiml/<file>")
def send_twiml_post(file):
    return Response(make_play(file), content_type='text/xml')

@app.get("/play_twiml/<file>")
def send_twiml_get(file):
    return Response(make_play(file), content_type='text/xml')



@app.get("/static/<file_name>")
def send_static_file(file_name):
    print(file_name)
    return send_file(f"./static/{file_name}")


@app.post("/sms")
def reply_to_text():
    return sms_handler(Users=Users, request=request)

@app.post("/voice")
def reply_to_voice():
    return Response(make_play("phone_response"), content_type="text/xml")

@app.get("/testingtestingtesting/<tz>/<userrunattime>")
def reply_to_test(tz, userrunattime):
    out = PendingTaskActions.make_run_at_time(tz,userrunattime)
    return out


scheduler = BlockingScheduler()
@scheduler.scheduled_job(IntervalTrigger(seconds=5))
def check_pending_tasks():
    current_time = dt.now()
    seconds = 30
    minutes_added = datetime.timedelta(seconds = seconds)
    future_date_and_time = current_time + minutes_added
    # PendingTaskActions.make_new_task(PendingTasks=PendingTasks, phone_number="+14253501717",run_action="reminder_call",run_at_time=future_date_and_time)
    # PendingTaskActions.find_over_due_tasks(PendingTasks=PendingTasks)
scheduler.start()

if __name__ == "__main__":
  app.run()










