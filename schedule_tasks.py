from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser as datetimeparser
from affirmations import get_affirmation
from twilio_logic import make_call, make_text


class PendingTaskActions():
    def make_new_task(PendingTasks, current_user, usr_run_at_time, run_action:str, user_input_text:str):
        offset = current_user.time_zone_offset
        now = dt.utcnow()
        default_time = now + timedelta(minutes=-1*now.minute, seconds=-1*now.second, microseconds=-1 * now.microsecond)
        parsed_usr_run_at_time = datetimeparser.parse(usr_run_at_time, default=(default_time) + timedelta(hours=offset)) # user gave time in local but this converts it to UTC time not properly localized
        server_current_day = now.day
        user_current_day = (now + timedelta(hours=offset)).day
        if server_current_day > user_current_day:
            parsed_usr_run_at_time + timedelta(days=-1)
        
        run_at_time = parsed_usr_run_at_time - timedelta(hours=offset) # this should properly normalize the user provided time to UTC so -8 seattle would be increased by 8 hours
        if run_at_time < now:
            print("shifting by one day so it doesn't land in the past")
            run_at_time = run_at_time + timedelta(days=1)
        PendingTasks(
            phone_number=current_user.phone_number,
            run_at_time=run_at_time,
            run_action=run_action,
            user_input=user_input_text
            ).save()
        print(f"adding task for {current_user.phone_number} at {usr_run_at_time} of {run_action}")
        return run_at_time - now

    def run_scheduled_task(task):
        if task.run_action == "affirm":
            affirmation = get_affirmation()
            make_text(task.phone_number, affirmation)
        elif task.run_action == "reminder":
            make_text(task.phone_number, f"You wanted to be reminded of this now:\n{task.user_input}")
        elif task.run_action == "phone-reminder":
            make_call(task.phone_number,"reminder",task.user_input)
        else:
            print("Error unknown scheduled action type")

    def make_pending_text(PendingTasks, current_user):
        pending_tasks_for_user = PendingTasks.objects(phone_number=current_user.phone_number)
        text = ""
        title = "Pending reminders\n--------------------\n"
        count = 1
        for task in pending_tasks_for_user:
            task.simple_id = count
            count += 1
            task.save()
            text += f'ID:{task.simple_id} {task.run_action} {task.run_at_time + timedelta(hours = current_user.time_zone_offset)} "{task.user_input}"\n---------\n'
        # print(text)
        if len(text) == 0:
            text = "No tasks pending at this time"
        return title+text

    def find_and_run_over_due_tasks(PendingTasks):
        pending_tasks = PendingTasks.objects(run_at_time__lte=dt.utcnow())
        # print("checking pending tasks")
        for task in pending_tasks:
            PendingTaskActions.run_scheduled_task(task)
            print(f"Scheduled action:{task.run_action} - {task.phone_number}")
            task.delete()
        # print("done checking pending tasks")

    
if __name__ == "__main__":
    pass