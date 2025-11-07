#   Primær kode for projektet
#   Når en client tilslutter sig vores server, bruges dette script til at dirigerer dem rundt 
#   Se den nedereste del af programmet "if __name__ == "__main__"", for hvordan serveren starter, når den testes lokalt
#   Når serveren kører på den hjemmeside, hvor vi host'er den bruges gunicorn, der står for at uddele "jobs" og kører koden

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from dotenv import load_dotenv
import os, jwt, time

# Vores enge funktion kald
from modules.password_generator import pass_random
from modules.mail_sender import send_mail
import modules.password_manager as pass_manager
import modules.db_manager as db_manager


app = Flask(__name__) # Initialisere serveren
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24)) # Sætter en tilfældig sammensætning af tal som "hemmelig" kode


is_debug = False # Til at tjekke om programmet køres under test

load_dotenv() # Henter api keys værdier fra filen .env



# JWT configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(32)) # En client ukendt hemmelig kode, der bruges ved kryptering af data'ene
JWT_ALGORITHM = 'HS256' # HMAC SHA-256 til signering af jwt tokens
JWT_EXPIRATION_HOURS = 24 * 3600 # Så længe en JWT token gælder (10 timer)



#########################################################
#                                                       #
#   JWT Helper Functions                                #
#                                                       #
#########################################################


# Kode til at oprette jwt tokens, ud fra en given mail
def create_jwt_token(email):
    current_time = int(time.time()) # For oprettelse tidsstempel
    expiration_time = current_time + (JWT_EXPIRATION_HOURS) # Hvornår vores token udløber
    
    # Data som der gemmes i vores JWT token
    payload = {
        'email': email, # Data vi kommer til at hente fra denne token
        'exp': expiration_time, # bruges automatisk af programmet
        'iat': current_time # bruges automatisk af programmet
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM) # Kalder en funktion, der returner vores token som klartekst efter at krypterer den
    return token


# Tjekker om det gældne token kan dekrypteres (om de er valide) og tjekker om det er udløbet
def decode_jwt_token(token): 
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM) # Funktion der returnerer den "payload", der blev signeret
        return payload
    except:
        return None  # Token er udløbet eller ugyldig




#########################################################
#                                                       #
#   Modtagning og håndtering af kald med serveren      #
#                                                       #
#########################################################



# En form for joker, der sender en bruger til en aktuel side, hvis de ikke specificerer en
@app.route("/", methods=["GET"])
def home():
    # Tjekker om en bruger allerede er logget ind
    token = request.cookies.get('jwt_token') # Tjekker om cookie'en jwt_token findes og gemmer den, hvis den gør
    if token and decode_jwt_token(token): # Prøver at validere cookie'en
        return redirect(url_for("dashboard")) # Hvis det var en valid JWT token, sendes clienten til user_dashboard
    
    return redirect(url_for("login")) # Som standard sendes brugerer til log-ind skærmen




# Kode til at oprette en konto
@app.route("/create_acc", methods=["GET", "POST"])
def create_acc():
    # Tjekker om en bruger allerede er logget ind
    token = request.cookies.get('jwt_token') # Tjekker om cookie'en jwt_token findes og gemmer den, hvis den gør
    if token and decode_jwt_token(token): # Prøver at validere cookie'en
        return redirect(url_for("dashboard")) # Hvis det var en valid JWT token, sendes clienten til user_dashboard
    
    
    # Retunerer html siden, hvis GET request
    if request.method == "GET":
        return render_template("create_account.html")
    
    
    # ******   Resten af denne funktion er i tilfældet "POST", hvor brugeren giver data    ******

    
    # Henter data fra form requesten
    email = request.form.get("email")
    password = request.form.get("password")
    action_type = request.form.get("submit_action")
    
    # "if" er tekniskset ligegyldigt, men er der for at være 100% sikker på at vi gør det rigtige
    if action_type == "account_creation":
        
        # Ens adgangskode skal være mellem 8 og 32 tegn
        if not (len(password) >= 8 and len(password) <= 32): 
            flash("Password must be 8-32 characthers !!", "danger") # Viser besked på html siden
            return render_template("create_account.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst
        
        # Tjekker om der findes en konto med den givne mail (scriptet db_manager.py bruges)
        if db_manager.account_exists(email):
            flash("An account with that email already exist !!", "danger") # Viser besked på html siden
            return render_template("create_account.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst
    
        # Resten af koden opretter kontoen med scriptet db_manager.py
    
        if db_manager.create_account(email, password):
            flash("Account succesfully created", "success") # Viser besked på html siden
            return render_template("create_account.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst
        else:
            flash("There was a problem creating your account !!", "danger") # Viser besked på html siden
            return render_template("create_account.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst




# Kode når en bruger prøver at logge ind med email og password
@app.route("/login", methods=["GET", "POST"])
def login():
    # Tjekker om en bruger allerede er logget ind
    token = request.cookies.get('jwt_token') # Tjekker om cookie'en jwt_token findes og gemmer den, hvis den gør
    if token and decode_jwt_token(token): # Prøver at validere cookie'en
        return redirect(url_for("dashboard")) # Hvis det var en valid JWT token, sendes clienten til user_dashboard

    # Retunerer html siden, hvis GET request
    if request.method == "GET":
        response = make_response(render_template("login.html")) # Klargør siden til at vi kan sende en cookie request med
        response.delete_cookie('sent_email') # sørger for at fjerne cookien "sent_mail", da clienten er væk fra authentications siden
        return response
    
    
    # ******   Resten af denne funktion er i tilfældet "POST", hvor brugeren giver data    ******


    # Henter data fra html siden
    email = request.form.get("email")
    password = request.form.get("password")
    action_type = request.form.get("submit_action")
    
    
    # "if" er tekniskset ligegyldigt, men er der for at være 100% sikker på at vi gør det rigtige
    if action_type == "login":
        # Sørger for at der faktisk findes en konto med den email clienten giver (scriptet db_manager.py bruges)
        if (not db_manager.account_exists(email)):
            flash("An account with that mail doesn't exist !!", "danger") # Viser besked på html siden
            return render_template("login.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst

        # Tjekker om email og password passer med dem gemt i databasen (krypterer det givne password som hash inden sammenligning)
        if (not db_manager.verify_pass(email, password)):
            flash("Wrong password !!", "danger") # Viser besked på html siden
            return render_template("login.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst
            
        
        # ******   Resten af koden klargør og sender en kode til ens mail    ******


        auth_pass = pass_random() # Bruger scriptet password_generator.py til at oprette en tilfældig kode
        
        if send_mail(auth_pass, email): # Hvis mailen sendes succesfuldt returnerers true
            flash(f"Authentication code sent to {email} !!", "success") # Viser besked på html siden

            pass_manager.add_auth_code(email, auth_pass) # Gemmer den oprettede authentication kode i password_manager.py scriptet
            
            response = make_response(render_template("authenticator.html")) # Klargør html siden til at sende med cookie
            response.set_cookie('sent_email', email) # Gemmer mailen authentication koden belv sendt til, som cookie, så den kan hentes på en anden side       
            return response
        
        else:
            flash("Email could not be sent.", "danger") # Viser besked på html siden
            return render_template("login.html", last_tried_email=email, last_password=password) # Indlæser html siden med det sidste password og email allerede indlæst
            




# Kode til at verificerer authentication kode sendt til en brugers email
@app.route("/auth", methods=["GET", "POST"])
def auth():
    # Tjekker om en bruger allerede er logget ind
    token = request.cookies.get('jwt_token') # Tjekker om cookie'en jwt_token findes og gemmer den, hvis den gør
    if token and decode_jwt_token(token): # Prøver at validere cookie'en
        return redirect(url_for("dashboard")) # Hvis det var en valid JWT token, sendes clienten til user_dashboard
    
    
    # Retunerer html siden, hvis GET request
    if request.method == "GET":
        if request.cookies.get('sent_email'): # Hvis der ikke er sendt en email til denne konto får brugeren ikke lov til at tilgå siden
            return render_template("authenticator.html")
        else:
            flash("Please begin log-in to access this page.", "danger") # Viser besked på html siden
            return render_template("login.html")
        
        
    # ******   Resten af denne funktion er i tilfældet "POST", hvor brugeren giver data    ******
        
    # Henter data fra html siden
    user_auth_pass = request.form.get("auth_pass")
    action_type = request.form.get("submit_action")
    
    # Henter data fra cookie
    email = request.cookies.get('sent_email')
    
    # "if" er tekniskset ligegyldigt, men er der for at være 100% sikker på at vi gør det rigtige
    if action_type == "check_auth":
        # Tjekker om brugeren har indskrevet en authentication kode, der passer med en gemt i scriptet passwor_manager.py
        if pass_manager.verify_auth_code(email, user_auth_pass):

            # Opret JWT token med brugerens mail som payload gemt i den
            token = create_jwt_token(email)
            
            # 
            response = make_response(render_template("user_dashboard.html")) # Klargør html siden til at sende med cookie
            response.set_cookie( # Gemmer den oprettede JWT token som cookie hos clienten
                'jwt_token', # Navn
                token, # Signeret payload 
                httponly=True, # Kan ikke røres af JavaScript
                secure=(not is_debug), # Skal være over https (Krypteret connection)
                samesite='Strict', # Andre åbne faner kan ikke tilgå cookien
                max_age=JWT_EXPIRATION_HOURS # Sætter cookie specifik maks levetid
            )

            return response
        
        else:
            flash("Invalid, expired, or already used authentication code!", "danger") # Viser besked på html siden
            return render_template("authenticator.html")
        



# Kode til at tilgå siden, man skal være logget ind for at tilgå
@app.route("/dashboard")
def dashboard():
    token = request.cookies.get('jwt_token') # Henter JWT token'en fra clientens cookies
    
    if not token: # Cookien kunne ikke findes
        flash("Please log in to access this page.", "danger") # Viser besked på html siden
        return redirect(url_for("login"))
    
    # Prøver at verificerer JWT token'ens signering og tjekke om den er udløbet
    payload = decode_jwt_token(token)
    
    if not payload: # Hvis den ikke kune verificeres
        flash("Session expired. Please log in again.", "danger") # Viser besked på html siden
        return redirect(url_for("login"))
    
    # Tilføjer clientens username til html siden så det kan vises på skærmen
    username = db_manager.get_username(payload['email'])
    
    
    response = make_response(render_template("user_dashboard.html", username=username)) # Klargør html siden med clientens username bagt ind
    response.delete_cookie('sent_email') # Sletter den mail der blev brugt til authentication
    return response


# Kode til at logge en bruger ud igen
@app.route("/logout")
def logout():
    flash("You have been logged out.", "info") # Viser besked på html siden
    
    response = make_response(redirect(url_for('login'))) # Klargør html siden login.html
    response.delete_cookie('jwt_token') # Sletter den adgangsgivne token (JWT token)
    response.delete_cookie('sent_email') # Sletter den mail der blev brugt til authentication (for sikkerhedsskyld burde ikke findes)
    return response


#########################################################
#                                                       #
#   Kode der tænder serveren, hvis den køres lokalt     #
#                                                       #
#########################################################

if __name__ == "__main__":
    is_debug = True # Sættes til, hvis koden køres lokalt
    app.run(debug=True) # Debug er sat til for at give mere information