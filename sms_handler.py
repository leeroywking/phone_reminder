from twilio_logic import make_call, make_text
import re
from affirmations import get_affirmation
from schedule_tasks import PendingTaskActions

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


def sms_handler(Users, PendingTasks, request):
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
            make_call(from_number, "completed_your_goal")
    elif "affirm me" in body.lower():
        affirmation = get_affirmation()
        make_text(from_number, affirmation)

    elif "set timezone" in body.lower():
        try:
            offset = re.search("[-+]\d{1,2}([\.\:][53])?", body)[0]
        except TypeError:
            make_text(current_user.phone_number, 'Oops looks like you used an invalid format to set your offset. Valid formats are as follows\nset timezone +10:30\nset timezone +10.5\nset timezone -8\nset timezone -8:00\noffsets must have a + or - and must either represent decimal hours (+10.5) or hours and minutes (+10:30). If you are still having trouble reach out in #oh-no-your-code-its-broken')
            return "Error: malformed timezone offset"
        if ":" in offset: # this will not catch weird behavior like 10.3 to represent 10:30 it only works in decimals and hours:minutes and it doesn't support minutes besides 30
            [hours, minutes] = [int(num) for num in offset.split(":")]
            print(hours, minutes)
            if minutes == 3:
                if hours < 0:
                    hours -= 0.5
                else:
                    hours += 0.5
            offset = hours
        current_user.time_zone_offset = float(offset)
        make_text(current_user.phone_number, f"You have set your timezone offset to {current_user.time_zone_offset}")
        current_user.save()

    elif "remind me" in body.lower():
        # Well formed text would look like "remind me to wash the dog at 16:00" or "remind me to drink water at 5pm"
        if not current_user.time_zone_offset:
            make_text(current_user.phone_number, 'Looks like you haven\'t set your timezone offset yet.\nPlease visit:\nhttps://www.timeanddate.com/time/zone/\nThis will help you identify your current offset.\nThen send a message in the following format \n"set timezone -8" where "-8" would be replaced by the offset for your timezone\n-8 is the offset for PST in the USA')
            return "Error: Timezone offset not set"
        body_list = body.lower().split("at")
        usr_run_at_time = body_list[-1]
        reminder = "reminder"
        # need to logic the timezone normalization here
        time_till_event = PendingTaskActions.make_new_task(PendingTasks, current_user, usr_run_at_time, run_action=reminder)
        days = time_till_event.days
        hours = time_till_event.seconds // 3600
        minutes = (time_till_event.seconds //60)%60
        # print(f"Days till event: {days}")
        # print(f"hours till event: {hours}")
        # print(f"minutes till event: {minutes}")
        make_text(current_user.phone_number, f"You have made a reminder that will happen in {days} days, {hours} hours, and {minutes} minutes")

    elif "call me" in body.lower():
        print("received request for call")
        make_call(from_number, "wakeup")
    else:
        make_text(from_number)

    return "blahblah"