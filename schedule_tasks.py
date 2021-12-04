from datetime import datetime as dt
from datetime import timedelta
from dateutil import parser as datetimeparser
class PendingTaskActions():
   

    def make_new_task(PendingTasks, current_user, usr_run_at_time, run_action):
        parsed_usr_run_at_time = datetimeparser.parse(usr_run_at_time) # user gave time in local but this converts it to UTC time not properly localized
        # print(parsed_usr_run_at_time)
        # print(dt.utcnow()) # should be in UTC but on my local system it is not
        offset = current_user.time_zone_offset
        # need to shift offset
        run_at_time = parsed_usr_run_at_time - timedelta(hours=offset) # this should properly normalize the user provided time to UTC so -8 seattle would be increased by 8 hours

        PendingTasks(
            phone_number=current_user.phone_number,
            run_at_time=run_at_time,
            run_action=run_action
            ).save()
        print(f"adding task for {current_user.phone_number} at {run_at_time} of {run_action}")
        return run_at_time - dt.utcnow()

    def find_and_run_over_due_tasks(PendingTasks):
        pending_tasks = PendingTasks.objects(run_at_time__lte=dt.utcnow())
        print("checking pending tasks")
        for task in pending_tasks:
            #this will run tasks someday probably call another function
            print(f"{task.run_action} - {task.phone_number} -------------------------------------------------")
            task.delete()
        print("done checking pending tasks")

    

if __name__ == "__main__":
    pass