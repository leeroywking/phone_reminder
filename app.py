from flask import Flask, send_file, request
from twilio_logic import make_call, make_text
# from werkzeug.utils import send_file, send_from_directory
app = Flask(__name__, static_url_path="/static")

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
    from_number = request.values.get("From")
    body = request.values.get("Body")
    with open("whats_been_texted.txt", "a") as myfile:
        myfile.write(f"{from_number} - {body}\n")
    if "call me" in body.lower():
        make_call(from_number)
    else:
        make_text(from_number)
    return ""

@app.get("/whats_been_texted")
def get_texts():
    return send_file("./whats_been_texted.txt")


if __name__ == "__main__":
  app.run()