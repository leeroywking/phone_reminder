from datetime import datetime, timedelta
from twilio_logic import make_call, make_text, helper_text_maker, timezone_help_text, reminder_help_text
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
            make_call(from_number, "completed_your_goal", " ")
    elif "affirm me" in body.lower():
        affirmation = get_affirmation()
        make_text(from_number, affirmation)

    elif "daily affirmation on" in body.lower() or "daily affirmations on" in body.lower():
        if not current_user.time_zone_offset:
            make_text(current_user.phone_number, timezone_help_text)
            return "Error: Time zone offset not set"
        current_user.daily_affirmation = True
        current_user.save()
        make_text(current_user.phone_number, "You subscribed to daily affirmations")

    elif "daily affirmation off" in body.lower() or "daily affirmations off" in body.lower():
        current_user.daily_affirmation = False
        current_user.save()
        pending_affirm = PendingTasks.objects(phone_number=current_user.phone_number, run_action="affirm")
        if pending_affirm:
            pending_affirm.delete()
        make_text(current_user.phone_number, "You unsubscribed from daily affirmations")

    elif "set timezone" in body.lower() or "set time zone" in body.lower():
        try:
            offset = re.search("[-+]\d{1,2}([\.\:][53])?", body)[0]
        except TypeError:
            make_text(current_user.phone_number, timezone_help_text)
            return "Error: malformed time zone offset"
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
        make_text(current_user.phone_number, f"You have set your time zone offset to {current_user.time_zone_offset}")
        current_user.save()

    elif "remind me" in body.lower():
        # Well formed text would look like "remind me to wash the dog at 16:00" or "remind me to drink water at 5pm"
        if not current_user.time_zone_offset:
            make_text(current_user.phone_number, timezone_help_text)
            return "Error: Time zone offset not set"
        if " on " in body.lower():
            body_list = body.lower().split(" on ")
        elif " at " in body.lower():
            body_list = body.lower().split(" at ")
        else:
            make_text(current_user.phone_number, reminder_help_text)
            return "Error: improper reminder format"

        usr_run_at_time = body_list[-1]
        try:
            reminder_body = body_list[0].split("remind me to ")[1]
        except IndexError:
            make_text(current_user.phone_number, reminder_help_text)
            return "Error: improper reminder format"
        # print(reminder_body)
        reminder_type = "reminder"
        if "phone-remind" in body.lower():
            reminder_type = "phone-reminder"
        time_till_event = PendingTaskActions.make_new_task(
            PendingTasks = PendingTasks, 
            current_user = current_user, 
            usr_run_at_time = usr_run_at_time, 
            run_action=reminder_type, 
            user_input_text=reminder_body
            )
        days = time_till_event.days
        hours = time_till_event.seconds // 3600
        minutes = (time_till_event.seconds //60)%60
        make_text(current_user.phone_number, f"You have made a reminder that will happen in {days} days, {hours} hours, and {minutes} minutes")

    elif "call me" in body.lower():
        print("received request for call")
        make_call(from_number, "wakeup",say_text=" ")
    
    elif "help" in body.lower():
        text = helper_text_maker(body.lower())
        make_text(from_number, text)

    elif "show pending" in body.lower():
        output = PendingTaskActions.make_pending_text(PendingTasks, current_user)
        make_text(from_number, output)
    elif "cancel pending" in body.lower():
        ids = [int(num) for num in re.findall("\d+", body)]
        for id in ids:
            task = PendingTasks.objects(phone_number = current_user.phone_number, simple_id=id)[0]
            print(f"removing id:{id} from database")
            text = f'Deleting Pending Task\n---------\nID:{task.simple_id} {task.run_action} {task.run_at_time + timedelta(hours = current_user.time_zone_offset)} "{task.user_input}"\n---------\n'
            task.delete()
        remaining_items = PendingTaskActions.make_pending_text(PendingTasks, current_user)
        make_text(current_user.phone_number, f"deleted IDs {ids} remaining pending items...\n{remaining_items}")
    else:
        make_text(from_number)

    return "blahblah"