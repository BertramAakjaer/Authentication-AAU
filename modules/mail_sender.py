from mailjet_rest import Client
from dotenv import load_dotenv
import os


def send_mail(auth_pass, reciever_mail, do_not_send=False):
    
    if (do_not_send):
        print("Did not send")
        return True
    
    load_dotenv()

    api_key = os.getenv("API_PUBLIC")
    api_secret = os.getenv("API_SECRET")
    sender_email = os.getenv("EMAIL_SENDER")


    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    
    data = {
        'Messages': [
            {
                "From": {
                    "Email": sender_email,
                    "Name": "OTP Authentication"
                },
                "To": [
                    {
                        "Email": reciever_mail,
                        "Name": "Recipient Name"
                    }
                ],
                "Subject": "P1 project, OTP code to login",
                "TextPart": f"Here is the OTP authentication code to login on the site: {auth_pass}"
            }
        ]
    }
    
    try:
        result = mailjet.send.create(data=data)
        
        ## Debug \/
        # print(f"Status: {result.status_code}")
        # print(f"Response JSON:{result.json()}")

        if result.status_code == 200:
            # print("\nEmail sent successfully!")
            return True
        else:
            # print("\nEmail sending failed. Check the response JSON for errors.")
            return False

    except Exception as e:
        print(f"An error occurred: {e}")
    