from mailjet_rest import Client
from dotenv import load_dotenv
from datetime import datetime, timedelta



import os, re

load_dotenv() # Henter api keys værdier fra .env filen

# Henter specifikke værdier fra .env filen
api_key = os.getenv("MAILJET_PUBLIC")
api_secret = os.getenv("MAILJET_SECRET")
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
    
    current_time = (datetime.utcnow() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M UTC')
    
    
    # Formateret struktur for besked der sendes    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f4f4f4; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <!-- Header -->
            <div style="background-color: #0d6efd; padding: 20px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px;">AAU Login Verification</h1>
            </div>
            
            <!-- Body -->
            <div style="padding: 30px; text-align: center; color: #333333;">
                <p style="font-size: 16px; line-height: 1.5; margin-bottom: 30px;">
                    You requested a one-time login code for your AAU P1 project account <br>
                    Please use the code here, to login on the account tied to the e-mail: {reciever_mail}
                </p>
                
                <!-- OTP Code Box -->
                <div style="background-color: #f8f9fa; border: 2px dashed #000000; border-radius: 4px; padding: 15px; margin-bottom: 30px; display: inline-block;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #000000;">{auth_pass}</span>
                </div>
                
                <p style="font-size: 14px; color: #666666; margin-bottom: 0;">
                    The code is expires in 5 minutes
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #eeeeee; padding: 15px; text-align: center; font-size: 12px; color: #777777;">
                <p style="margin: 5px 0;">Koden blev anmodet: {current_time}</p>
                <p style="margin: 5px 0;">If this wasn't u please ignore this mail</p>
                <p style="margin: 10px 0 0 0;"><strong>AAU P1 Group-3 • Security System</strong></p>
            </div>
        </div>
    </div>
    """
    
    data_html = {
        'Messages': [
            {
                "From": {
                    "Email": sender_email, 
                    "Name": "AAU Security System"
                },
                "To": [
                    { 
                        "Email": reciever_mail,
                        "Name": "User"
                    }
                ],
                "Subject": "Din bekræftelseskode (OTP)", 
                "TextPart": f"Din kode er: {auth_pass}. Anmodet kl: {current_time}", # Vises hvis mail-klienten ikke kan vise HTML
                "HTMLPart": html_content # Vises som standard
            }
        ]
    }
    
    
    try:
        result = mailjet.send.create(data=data_html) # Prøver at sende mail og får værdien "result", som giver status'en for den sendte mail

        if result.status_code == 200: # 200 = standard kode for success
            return True
        else:
            print(f"Fejl ved sending: {result.status_code}") # Nyttig debug info
            return False 
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False
    