import os
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

def make_call(outgoing_number):
    call = client.calls.create(
                            url=f'{os.environ.get("BASE_URL")}/static/wakeup.xml',
                            to=outgoing_number,
                            from_='+14252175622'
                        )
    print(call.sid)

#970-hi-0-a-lee
div = "\n----------\n"
default_text = (
    f'You can reply with the text "call me" to receive a call.'\
    f'{div}Water tracking commands{div}' \
    f'FIRST - to set your goal send\n'\
    f'"help me drink 10 glasses of water" or\n'\
    f'"help me drink 100oz of water"\n(can be any unit){div}'\
    f'THEN - update progress send\n'\
    f'"I drank 1 glass of water" or\n'\
    f'"I have drunk 2 glasses already"'
)

def make_text(outgoing_number, body=default_text): 
    message = client.messages.create(
                                body=body,  
                                to=outgoing_number,
                                messaging_service_sid='MGd95c1d83c6ddffdea9172ffbf68d2c30'
                            ) 
    print(message.sid)

if __name__ == "__main__":
    # make_call("+14253501717")
    make_text("+14253501717")

