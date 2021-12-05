from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser as datetimeparser
from affirmations import get_affirmation
from twilio_logic import make_call, make_text


class PendingTaskActions():
    def make_new_task(PendingTasks, current_user, usr_run_at_time, run_action:str, user_input_text:str):
        parsed_usr_run_at_time = datetimeparser.parse(usr_run_at_time) # user gave time in local but this converts it to UTC time not properly localized
        offset = current_user.time_zone_offset
        # need to shift offset
        run_at_time = parsed_usr_run_at_time - timedelta(hours=offset) # this should properly normalize the user provided time to UTC so -8 seattle would be increased by 8 hours
        if run_at_time < dt.utcnow():
            run_at_time = run_at_time + timedelta(days=1)
        PendingTasks(
            phone_number=current_user.phone_number,
            run_at_time=run_at_time,
            run_action=run_action,
            user_input=user_input_text
            ).save()
        print(f"adding task for {current_user.phone_number} at {usr_run_at_time} of {run_action}")
        return run_at_time - dt.utcnow()

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