from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from functools import wraps
from dotenv import load_dotenv
import os, jwt, time

# Vores enge funktion kald
from modules.password_generator import pass_random
import modules.password_manager as pass_manager
from modules.mail_sender import send_mail



app = Flask(__name__)

load_dotenv() # Henter api keys


# JWT configuration
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.urandom(32))

JWT_ALGORITHM = 'HS256' # SHA-256
JWT_EXPIRATION_HOURS = 24 * 3600 # Så længe en token gælder (10 timer)





#########################################################
#                                                       #
#   JWT Helper Functions                                #
#                                                       #
#########################################################

def create_jwt_token(email):
    current_time = int(time.time())
    expiration_time = current_time + (JWT_EXPIRATION_HOURS)
    
    payload = {
        'email': email,
        'exp': expiration_time,
        'iat': current_time
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token): # Tjekker om det gældne token kan dekrypteres og tjekker om det er udløbet
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token er udløbet
    except jwt.InvalidTokenError:
        return None  # Ugyldigt token


def get_token_from_request():
    token = request.cookies.get('jwt_token')
    return token


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for("login"))
        
        payload = decode_jwt_token(token)
        if not payload:
            flash("Session expired. Please log in again.", "danger")
            return redirect(url_for("login"))
        
        # Tilføj ens email til request context så det kan vises på skærmen
        request.current_user = payload['email']
        return f(*args, **kwargs)
    
    return decorated_function





#########################################################
#                                                       #
#   Modtagning og håndtering af kald med serveren      #
#                                                       #
#########################################################



@app.route("/", methods=["GET"])
def home():
    token = get_token_from_request()
    if token and decode_jwt_token(token):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))



@app.route("/login", methods=["GET", "POST"])
def login():
    # Tjek om brugeren allerede er logget ind
    token = get_token_from_request()
    if token and decode_jwt_token(token):
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        return render_template("login.html")



    # ******   Resten af denne funktion er i tilfældet "POST", hvor brugeren giver data    ******


    # Henter data fra html siden
    email = request.form.get("email")
    action_type = request.form.get("submit_action")
    
    if action_type == "send_code":
        auth_pass = pass_random()
        pass_manager.add_auth_code(email, auth_pass)
        
        if send_mail(auth_pass, email):
            flash(f"Authentication code sent to {email} !!", "success")
        else:
            flash("Email could not be sent.", "danger")
        
        # Gem email i en midlertidig cookie (kun til UI-formål)
        response = make_response(render_template("login.html", last_sent_email=email))
        response.set_cookie('last_sent_email', email, max_age=600)  # 10 minutter max tid
        return response
    
    
    elif action_type == "login":
        user_auth_pass = request.form.get("auth_pass")
        
        if not user_auth_pass:
            flash("A code was not written !!", "danger")
            last_email = request.cookies.get('last_sent_email', email)
            return render_template("login.html", last_sent_email=last_email)
        
        if pass_manager.verify_auth_code(email, user_auth_pass):

            # Opret JWT token
            token = create_jwt_token(email)
            
            flash("Login Successful!", "success")
            
            # Opret response og sæt JWT token
            response = make_response(redirect(url_for("dashboard")))
            response.set_cookie(
                'jwt_token',
                token,
                httponly=True,
                secure=False,
                samesite='Strict',
                max_age=JWT_EXPIRATION_HOURS
            )

            # Fjern midlertidig email cookie
            response.delete_cookie('last_sent_email')
            return response
        
        else:
            flash("Invalid, expired, or already used authentication code!", "danger")
            last_email = request.cookies.get('last_sent_email', email)
            return render_template("login.html", last_sent_email=last_email)



@app.route("/dashboard")
@jwt_required
def dashboard():
    return render_template("user_dashboard.html", username=request.current_user)



@app.route("/logout")
def logout():
    flash("You have been logged out.", "info")
    response = make_response(redirect(url_for('login')))

    response.delete_cookie('jwt_token')
    response.delete_cookie('last_sent_email')

    return response



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)