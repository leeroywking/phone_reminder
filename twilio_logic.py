import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import urllib
from textwrap import wrap
from dotenv import load_dotenv
load_dotenv()


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)\

BASE_URL = os.environ.get("BASE_URL")

def make_call(outgoing_number, file_name, say_text=""):
    parsed_say_text = urllib.parse.quote(say_text)
    print(parsed_say_text)
    call = client.calls.create(
                            url=f'{BASE_URL}/play_twiml/{file_name}/{parsed_say_text}',
                            to=outgoing_number,
                            from_='+14252175622'
                        )
    print(call.sid)

def make_play(file_name, say_text = ""):
    response = VoiceResponse()
    response.play(f'{BASE_URL}/static/{file_name}.mp3')
    if len(say_text) > 0:
        response.pause(1)
        response.say(say_text)
        response.pause(1)
    return str(response)


#970-hi-0-a-lee
div = "\n----------\n"
small_div = "\n---\n"

water_text = (
    f'Water tracking commands{div}\n'
    f'FIRST - to set your goal send'
    f'{small_div}'
    f'"help me drink 10 glasses of water" or\n'
    f'"help me drink 100oz of water"\n(can be any unit)\n{div}\n'
    f'THEN - update progress send'
    f'{small_div}'
    f'"I drank 1 glass of water" or\n'
    f'"I have drunk 2 glasses already"'
)

help_misc = 'You can reply with the text "call me" to receive a call. "affirm me" to recieve a text affirmation'

intro_text = (
    f'Welcome to the lovebot we have a few features you can use right now. To learn more about them reply with one of the following options'
    f'{div}'
    f'"help affirmations"\n'
    f'"help reminders"\n'
    f'"help water tracking"\n'
    f'"help misc"\n'
    f'"help timezone"\n'
    f'"help all"\n'
    f'{div}'
    f'{help_misc}'
)

reminder_help_text = (
    "To set a reminder please send a message that follows one of these examples"\
    f"{div}"
    '"remind me to wash the dog at 5pm" (if its past 5pm it will use 5pm the next day)\n'
    '"remind me to call sam at 9am"\n'
    '"phone-remind me to do the dishes on friday dec 20th 10am\n'
    '"phone-remind me to fight god on sunday" (defaults to midnight)'
    f"{div}"
    'Things that don\'t work'
    f"{small_div}"
    "Remind me to call the doctor tomorrow at 10am\n"
    'If its a time in the future try using the date or day of week instead of words like "tomorrow" or "next week"\n'
    f"{div}"
    f'If you need to delete a reminder you\'ve made "help pending" will provide instructions'

)

daily_affirmation_text = (
    '"affirm me" gets you a single affirmation'
    f"{div}"
    'you may also sign up for daily affirmations at 9am by sending'
    f"{small_div}"
    '"daily affirmations on"\n and unsubscribe by sending\n'
    '"daily affirmations off"\n'
    "---\n"
    '(requires timezone to be set) send\n"help timezone"\nfor more info'
)

timezone_help_text = (
    'Setting your timezone is necessary for reminders and daily affirmations\n'
    'Please visit:\nhttps://www.timeanddate.com/time/zone/\n'
    'This will help you identify your current timezone offset.\n\n'
    'Then send a message in the following format'
    f'{div}'
    '"set timezone -8" where "-8" would be replaced by the offset for your timezone\n'
    '-8 is the offset for PST in the USA\n'
    f"{div}"
    'Example valid formats are as follows'
    f'{small_div}'
    'set timezone +10:30\n'
    'set timezone +10.5\n'
    'set timezone -8\n'
    'set timezone -5:00\n'
    'offsets must have a + or - and must either represent decimal hours (+10.5) or hours and minutes (+10:30).'
    f"{small_div}"
    'If you are still having trouble reach out in #oh-no-your-code-its-broken'
)

help_help_text = (
    "Valid help options are"
    f"{small_div}"
    f'"help affirmations"\n'
    f'"help reminders"\n'
    f'"help water tracking"\n'
    f'"help misc"\n'
    f'"help timezone"\n'
    f'"help pending"\n'
    f'"help all"\n'
)

example_pending = (
    'ID:1 reminder 2021-12-05 09:00:00 "fight god"\n'
    '---------\n'
    'ID:2 reminder 2021-12-04 20:00:00 "drink water"\n'
    '---------\n'
    'ID:3 reminder 2021-12-07 10:00:00 "buy presents"\n'
    '---------\n'
)

help_pending_management = (
    f'Reminders and daily affirmations both end up in "pending actions"\n'
    f'you can see your current pending actions by sending'
    f"{small_div}"
    f'"show pending"'
    f"{small_div}"
    f"example response"
    f"{div}"
    f"{example_pending}"
    f"If you want to cancel an upcoming reminder you can send"
    f"{small_div}"
    f'"cancel pending 3"\n'
    f'this would remove my pending reminder to "buy presents"\n'
    f"---\n"
    f'"cancel pending 1 2 3"\n'
    f'"this would remove all of the above pending reminders"'
)


help_all = (
    f"{help_misc}"
    f"{div}"
    f"{water_text}"
    f"{div}"
    f"{timezone_help_text}"
    f"{div}"
    f"{reminder_help_text}"
    f"{div}"
    f"{daily_affirmation_text}"
)
default_text = intro_text

helps = {
    "affirmations":daily_affirmation_text,
    "reminders": reminder_help_text,
    "water tracking":water_text, 
    "timezone":timezone_help_text,
    "misc":help_misc,
    "pending": help_pending_management
}


def helper_text_maker(help_request):
    output = ""
    if "all" in help_request:
        return help_all
    else:
        for help in helps:
            if help in help_request:
                output += f"{helps[help]}\n\n"
    if len(output) == 0:
        return help_help_text
    return output



def make_text(outgoing_number, body=default_text):
    bodies = wrap(body, 1600,replace_whitespace=False)
    for bodie in bodies:
        message = client.messages.create(
                                    body=bodie,  
                                    to=outgoing_number,
                                    messaging_service_sid='MGd95c1d83c6ddffdea9172ffbf68d2c30'
                                ) 
        print(message.sid)

if __name__ == "__main__":
    # make_call("+14253501717", "completed_your_goal")
    make_text("+14253501717", "You’ve survived every hardship that has come your way.\nKeep going.\n    -Jenna")

