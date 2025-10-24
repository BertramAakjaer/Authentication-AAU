from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

from modules.password_generator import pass_random
import modules.password_manager as pass_manager
from modules.mail_sender import send_mail


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

USERS = {
    "admin": "password123",
    "User": "guest"
}

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function




@app.route("/")
def home():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/send_auth', methods=['POST'])
def send_auth():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    user_mail = request.form.get('email')
    
    auth_pass = pass_random()
    pass_manager.add_password(user_mail, auth_pass)

    if send_mail(auth_pass, user_mail):
        flash("Authentication code send to {user_mail}", "success")
    else:
        flash("Email could not be sent!", "danger")
            
    return render_template(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        user_mail = request.form.get('email')
        user_auth_pass = request.form.get('auth_pass')

        if pass_manager.get_password(user_mail, user_auth_pass):
            session['logged_in'] = True
            session['username'] = user_mail
            flash("Login Successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid or expired authentication password!", "danger")
    return render_template(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """The protected page accessible only after successful login."""
    return render_template('user_dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    """Handles user logout by clearing the session."""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)