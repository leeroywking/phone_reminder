from twilio_logic import make_call, make_text
import re

def make_new_user(from_number, Users):
    Users(phone_number=from_number,
        preferred_name = "",
        water_goal = 0,
        water_drank = 0,
        total_sms_received = 0,
        total_sms_sent = 0,
        total_calls_received = 0,
        total_calls_sent = 0,
        received_sms_messages = ""
        ).save()


def sms_handler(Users, request):
    from_number = request.values.get("From")
    body = request.values.get("Body")

    if not Users.objects(phone_number=from_number).first():
        make_new_user(from_number=from_number, Users=Users)

    current_user = Users.objects(phone_number=from_number).first()
    current_user.total_sms_received = current_user.total_sms_received +1
    current_user.received_sms_messages = current_user.received_sms_messages + f"{body}\n"

    current_user.save()

    if "help me drink" in body.lower():
        goal = re.search("\d+", body)[0]
        if goal:
            current_user.water_goal = int(goal)
            current_user.water_drank = 0
            current_user.save()
            make_text(from_number, f"You wanna drink {goal} today you have drank 0/{goal}")
    elif "drank" in body.lower() or "drunk" in body.lower():
        drank = re.search("\d+", body)[0]
        if drank:
            current_user.water_drank = current_user.water_drank + int(drank)
            current_user.save()
            make_text(from_number, f"You have drank {current_user.water_drank}/{current_user.water_goal} of your goal today")
        if current_user.water_goal <= current_user.water_drank:
            make_text(from_number, f"You completed your water goal for the day great job!")

    elif "call me" in body.lower():
        print("received request for call")
        make_call(from_number, "wakeup")
    else:
        make_text(from_number)

    return "blahblah"