from flask import Flask, send_file, request
from twilio_logic import make_call, make_text
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
    # "username":DB_USER,
    # 'password':DB_PASS
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


@app.route("/")
def hello():
  return "Hello World!"

# @app.route("/static/<path:path>")
# def send_file(path):
#     return send_from_directory("static", path)

@app.post("/static/wakeup.xml")
def send_wakeup():
    return send_file("./static/wakeup.xml")

@app.route("/static/wakeup.mp3")
def send_wakeup_mp3():
    return send_file("./static/wakeup.mp3")

@app.post("/sms")
def reply_to_text():
    return sms_handler(Users=Users, request=request)


@app.get("/whats_been_texted")
def get_texts():
    return send_file("./whats_been_texted.txt")


if __name__ == "__main__":
  app.run()