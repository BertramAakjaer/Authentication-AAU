from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

USERS = {
    "admin": "password123",
    "User": "guest"
}

def login_required(f):
    """Decorator to protect routes that require a logged-in user."""
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
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check credentials against the dummy database
        if username in USERS and USERS[username] == password:
            session['logged_in'] = True
            session['username'] = username
            flash(f"Welcome, {username}! You are logged in.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password. Try 'admin'/'password123'.", "danger")
            # Stay on the login page

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