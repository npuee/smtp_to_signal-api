import base64, binascii, json, requests, asyncio, logging, sys

from email import message_from_bytes
from email.policy import default
from aiosmtpd.controller import Controller
from datetime import datetime
import re

print("Starting email to signal server:")
print("Loading settings")

# Load settings:
file = open("settings.json", "r")
f = file.read()
settings = json.loads(f)
file.close()

# Signal empty collection
# Signal sender:
signal_post = {}
signal_post["number"] = settings["signal"]["number"]

#
#   Handles all email routes
#
class EmailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        # Allow only in sender list
        if( envelope.mail_from not in settings["senders"] ):
            print(f"Denied email from: {envelope.mail_from}, to: {address}")
            print("-----------------------------------")
            return '550 not relaying to/from that domain'

        # Allow only in recipients list
        if( address not in settings["recipients"] ):
            print(f"Denied email from: {envelope.mail_from}, to:{address} ")
            print("-----------------------------------")
            return '550 not relaying to/from that domain'
        # If all goor return OK
        envelope.rcpt_tos.append(address)
        return '250 OK'

    # Handle email data itself
    async def handle_DATA(self, server, session, envelope):
        # Decode email content
        message = message_from_bytes(envelope.content, policy=default)
        email_from = message['from']
        email_to = message['to']
        email_subject = message['Subject']
        email_body = message.get_body().get_content()
    
        #Remove name from email from
        if '<' in email_to and '>' in email_to:
            start = email_to.find('<') + 1
            end = email_to.find('>', start)
            if end > start:
                email_to = email_to[start:end].strip()

        #Format Signal rest api json
        numbers= []
        numbers.append(settings["recipients"][email_to])
        signal_post['recipients'] = numbers
        signal_post['message'] = email_subject + "\n----------\n" + email_subject
        signal_post["base64_attachments"] = []
        
        # Iterate over attachments and add to signal post json
        for x in message.iter_attachments():
            image = x.get_payload(decode=True)
            if len(image) > 1000:
                base_post = "data:image/jpeg;base64," + base64.b64encode(image).decode("ascii")
                signal_post.setdefault("base64_attachments", []).append(base_post)

        #Send request to backend
        signal_backend_url = settings["signal"]["backend"]
        signal_response = requests.post(signal_backend_url, data=json.dumps(signal_post))
        # In debug mode skip sending signal
        #signal_response = "No signal sent, debug mode active"

        # Generic debug
        date_and_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{date_and_time}, email from:{email_from}, to:{email_to}")
        print(signal_post['message'])
        print(f"Signal message sent to: {numbers}")
        print(f"Signal api respons: {signal_response}")
        print("")
        print("-----------------------------------")
        return '250 Message accepted for delivery'

#MAIN LOOP
async def amain(loop):
    cont = Controller(EmailHandler(), hostname='', port=8025)
    cont.start()

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(amain(loop=loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("User abort indicated")
