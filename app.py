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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        action_type = request.form.get('submit_action') # New way to distinguish action

        if action_type == 'send_code':
            # --- Code Sending Logic ---
            # 1. Check if the user/email is actually registered (if applicable)
            # if email not in USERS:
            #     flash("Email not found.", "danger")
            #     return render_template('login.html', request=request) # Pass request object to keep email

            auth_pass = pass_random() # Generates the code
            
            # Use the secure pass_manager functions
            try:
                pass_manager.add_password(email, auth_pass) # Stores hashed, with expiry
                send_mail(auth_pass, email)
                
                # Pass the email to the session or flash message to help the user
                flash(f"Authentication code sent to {email}. Please check your inbox.", "success")
                session['last_sent_email'] = email # Store email in session for potential pre-fill/display
            except Exception as e:
                # Log the error (e)
                flash("Email could not be sent. Please try again.", "danger")

            # Redirect with the email value to keep it in the form after flash
            return render_template('login.html', last_sent_email=email) 
            
        elif action_type == 'login':
            # --- Login Verification Logic ---
            user_auth_pass = request.form.get('auth_pass')
            
            if not user_auth_pass:
                 flash("Please enter the authentication code.", "danger")
                 return render_template('login.html', last_sent_email=email)
            
            # Use the secure pass_manager function: checks hash, checks expiry, and deletes on success
            if pass_manager.get_password(email, user_auth_pass):
                session['logged_in'] = True
                session['username'] = email
                session.pop('last_sent_email', None) # Clean up temporary session data
                flash("Login Successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid, expired, or already used authentication code!", "danger")
                # Keep the email for re-sending the code if they wish
                return render_template('login.html', last_sent_email=email)

    # For a GET request
    return render_template('login.html')


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