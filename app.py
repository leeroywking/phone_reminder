from flask import Flask, send_file, request, Response
from datetime import datetime as dt
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from schedule_tasks import PendingTaskActions
from twilio_logic import make_call, make_text, make_play
from dateutil import parser as datetimeparser

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
    time_zone_offset = db.FloatField()
    daily_affirmation = db.BooleanField()

class PendingTasks(db.Document):
    run_at_time = db.DateTimeField()
    phone_number = db.StringField()
    run_action = db.StringField()
    user_input = db.StringField()
    simple_id = db.IntField()

@app.route("/")
def hello():
  return "Hello World!"

@app.route("/play_twiml", methods = ["POST","GET"])
def play_twiml():
    say_text = request.args.get("say_text") or " "
    file = request.args.get("file")
    return Response(make_play(file, say_text), content_type="text/xml")

@app.get("/static/<file_name>")
def send_static_file(file_name):
    print(file_name)
    return send_file(f"./static/{file_name}")


@app.post("/sms")
def reply_to_text():
    return sms_handler(Users=Users,PendingTasks=PendingTasks, request=request)

@app.post("/voice")
def reply_to_voice():
    return Response(make_play("phone_response", say_text=" "), content_type="text/xml")

@app.get("/time")
def get_time():
    return str(dt.utcnow())

@app.get("/time/<offset>")
def get_offset_time(offset):
    offset = float(offset)
    return str(dt.utcnow() + timedelta(hours=offset))

@app.get("/time/<offset>/<user_time_str>")
def get_offset_user_time(offset, user_time_str):
    offset = float(offset)
    parsed_usr_run_at_time = datetimeparser.parse(user_time_str, default=dt.utcnow() + timedelta(hours=offset)) # user gave time in local but this converts it to UTC time not properly localized
    parsed_usr_run_at_time = parsed_usr_run_at_time - timedelta(minutes = parsed_usr_run_at_time.minute, seconds = parsed_usr_run_at_time.second) # necessary to cancel out the default values written in the above line for minutes and seconds
    server_current_day = dt.utcnow().day
    user_current_day = (dt.utcnow() + timedelta(hours=offset)).day
    if server_current_day > user_current_day:
        parsed_usr_run_at_time + timedelta(days=-1)
    
    run_at_time = parsed_usr_run_at_time - timedelta(hours=offset)
    
    return str(f"parsed date{parsed_usr_run_at_time}    offset:{offset} server_current_day:{server_current_day} user_current_day:{user_current_day} run_at_time:{run_at_time}")


scheduler = BackgroundScheduler(timezone="UTC")
@scheduler.scheduled_job(IntervalTrigger(seconds=30, timezone="UTC"))
def check_pending_tasks():
    PendingTaskActions.find_and_run_over_due_tasks(PendingTasks=PendingTasks)
    pass

@scheduler.scheduled_job(IntervalTrigger(minutes=5, timezone="UTC")) # for daily affirmations
def schedule_affirmations():
    # print("This runs every minute------------------------------------------------------")
    users_to_affirm = Users.objects(daily_affirmation=True)
    for user in users_to_affirm:
        if not PendingTasks.objects(phone_number=user.phone_number, run_action="affirm"):
            PendingTaskActions.make_new_task(PendingTasks, current_user=user, usr_run_at_time="9:00am", run_action="affirm", user_input_text="Daily Affirmation")
        pass

scheduler.start()

if __name__ == "__main__":
  app.run(use_reloader=False)










