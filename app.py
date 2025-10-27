from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

# Vores enge funktion kald
from modules.password_generator import pass_random
import modules.password_manager as pass_manager
from modules.mail_sender import send_mail


app = Flask(__name__) # Starter serveren

app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24)) # "SECRET_KEY" findes ikke


#########################################################
#                                                       #
#   Modtagning og håndtering af kald med serveren \/    #
#                                                       #
#########################################################



@app.route("/", methods=["GET"]) # Default håndtering når folk besøger hjemmesiden
def home():
    if 'logged_in' in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))



@app.route("/login", methods=["GET", "POST"]) # Logind håndtering (Både at besøge siden "GET" og udfylde form "POST")
def login():
    if "logged_in" in session:
        return redirect(url_for("dashboard"))
    
    if request.method == "GET": # Hvis siden skulle besøges renders den bare
        return render_template("login.html")
    

    # ******   Resten af denne funktion er i tilfældet "POST", hvor brugeren giver data    ******


    # Henter data fra html siden
    email = request.form.get("email")
    action_type = request.form.get("submit_action")


    if action_type == "send_code": # Hvis form action-typen er "send_code", så sendes auth koden

        auth_pass = pass_random() # Tilfældigt authentication kodeord laves
        pass_manager.add_auth_code(email, auth_pass) # Koden sendes til adgangskode manageren


        if send_mail(auth_pass, email): # Hviser fejlkode, hvis emailen ikke kunne sendes
            flash(f"Authentication code sent to {email} !!", "success")
        else:
            flash("Email could not be sent.", "danger")


        session["last_sent_email"] = email
        return render_template("login.html", last_sent_email=email) 
        


    elif action_type == "login": # Hvis form action-typen er "login", så sendes testes koden brugeren skrev, med den lavet af password-manageren

        user_auth_pass = request.form.get("auth_pass") # Henter data fra html siden
        
        if not user_auth_pass:
                flash("A code was not written !!", "danger")
                return render_template("login.html", last_sent_email=email)
        
        if pass_manager.verify_auth_code(email, user_auth_pass): # Tester om den bruger indtastede kode er korrekt
            session["logged_in"] = True
            session["username"] = email
            session.pop('last_sent_email', None)

            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid, expired, or already used authentication code!", "danger")
            return render_template("login.html", last_sent_email=email)



@app.route("/dashboard") # Kode for dashboard siden, der smider en bruger ud, hvis de ikke er logget ind
def dashboard():
    if "logged_in" not in session:
        flash("Please log in to access this page.", "danger")
        return redirect(url_for("login"))
    return render_template("user_dashboard.html", username=session.get("username"))



@app.route("/logout") # Fjerner en brugers "credentials"
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)

    flash("You have been logged out.", "info")
    return redirect(url_for('login'))



if __name__ == "__main__": # Kører scriptet hvis denne fil køres og ikke importeres
    app.run(host="0.0.0.0", port=10000)