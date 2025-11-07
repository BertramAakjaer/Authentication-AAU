from mailjet_rest import Client
from dotenv import load_dotenv
import os, re

load_dotenv() # Henter api keys værdier fra .env filen

# Henter specifikke værdier fra .env filen
api_key = os.getenv("API_PUBLIC")
api_secret = os.getenv("API_SECRET")
sender_email = os.getenv("EMAIL_SENDER")

# Starter mailjet klienten
mailjet = Client(auth=(api_key, api_secret), version='v3.1')



# Tjekker om den mail der er giver er formateret som "*@*.*", hvor * er tilføldige symboler
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+$", email) is not None


# Funktion der kan kaldes til at sende authentication koden til mail
def send_mail(auth_pass, reciever_mail, do_not_send=False):
    if (do_not_send): # Kan bruges til at teste uden at bruge API tokens
        print("Did not send mail")
        return True
    
    if not is_valid_email(reciever_mail): # Tjekker om mailen er valid formateret, hvilket burde vise om den kan bruges
        return False
    
    # Formateret struktur for besked der sendes
    data = {
        'Messages': [
            {
                "From": { # Hvor mailen sendes fra
                    "Email": sender_email, 
                    "Name": "OTP Authentication"
                },
                "To": { # Hvor mailen sendes til
                    "Email": reciever_mail,
                    "Name": "AAU Authentication client"
                }
                ,
                "Subject": "P1 project, OTP code to login", # Overskrift vist på mail
                "TextPart": f"Here is the OTP authentication code to login on the site: {auth_pass}" # Brødtekst af mail
            }
        ]
    }
    
    try:
        result = mailjet.send.create(data=data) # Prøver at sende mail og får værdien "result", som giver status'en for den sendte mail

        if result.status_code == 200: # 200 = standard kode for success
            return True
        else:
            return False # ellers ved vi der skete fejl
    except:
        return False
    