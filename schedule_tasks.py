from datetime import datetime as dt
# from datetime import datetime
from timezones import list_of_timezones
from pytz import timezone
import pytz
from mongoengine.fields import DateField


class PendingTaskActions():
    def make_new_task(PendingTasks, current_user, run_at_time, run_action):
        PendingTasks(
            phone_number=current_user.phone_number,
            run_at_time=run_at_time,
            run_action=run_action
            ).save()
        print("made a new task!")

    def find_and_run_over_due_tasks(PendingTasks):
        pending_tasks = PendingTasks.objects(run_at_time__lte=dt.now())
        print("checking pending tasks")
        for task in pending_tasks:
            #this will run tasks someday probably call another function
            print(f"{task.run_action} - {task.phone_number} -------------------------------------------------")
            task.delete()
        print("done checking pending tasks")

    def make_run_at_time(tz, user_run_at_time):
        pass

if __name__ == "__main__":
    next_event = PendingTaskActions.make_run_at_time("US/Pacific", "16:00")
    utc = timezone("UTC")
    now = utc.localize(dt.now())
    now_reg = dt.now()
    diff = next_event - now
    print(now_reg)
    print(next_event)