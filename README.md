
```bash
    _            _    _                   _    _               _    _                            _        _     _   _
   / \    _   _ | |_ | |__    ___  _ __  | |_ (_)  ___   __ _ | |_ (_)  ___   _ __              / \      / \   | | | |
  / _ \  | | | || __|| '_ \  / _ \| '_ \ | __|| | / __| / _` || __|| | / _ \ | '_ \   _____    / _ \    / _ \  | | | |
 / ___ \ | |_| || |_ | | | ||  __/| | | || |_ | || (__ | (_| || |_ | || (_) || | | | |_____|  / ___ \  / ___ \ | |_| |
/_/   \_\ \__,_| \__||_| |_| \___||_| |_| \__||_| \___| \__,_| \__||_| \___/ |_| |_|         /_/   \_\/_/   \_\ \___/
```
> A custom, secure Two-Factor Authentication (2FA) service built with Flask for a cybersecurity project at AAU. It demonstrates secure user login using Email Time-based One-Time Passwords (TOTP).


## ✔️ Features

- **Two-Factor Authentication (2FA) via Email TOTP**: Secure login requires both a password and a time-sensitive, single-use code.
- **User Account Management**: Secure creation and validation of new user accounts.
- **Account Configuration**: Includes functionality for changing password, updating username, and permanent account deletion.


## ⏰ Installation & Setup
> [!Warning]
>  This project is made to be ran on a server using the [gunicorn](https://gunicorn.org/) python libary, but can be ran locally like showed firstly here.
> 

1. Clone the repository
```bash
# Clone this repository with git
git clone https://github.com/BertramAakjaer/Authentication-AAU.git

# Open the directory in terminal
cd Authentication-AAU/
```

2. Install requirements
```bash
python -m pip install -r requirements.txt
```

3. Setup a database with supabase using this SQL code
```sql
CREATE TABLE public.users (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT (now() AT TIME ZONE 'utc-1'::text),
  last_modified_at timestamp with time zone DEFAULT (now() AT TIME ZONE 'utc-1'::text),
  email text UNIQUE,
  username text,
  password text,
);
```

4. Setup a Mailjet account and get the API tokens

5. Configure your API tokens/secrets in a `.env` like the one showed here:
```bash
# Used by the Mailjet API for sending the authentication codes via email.
MAILJET_PUBLIC="<your_mailjet_api>"
MAILJET_SECRET="<your_mailjet_secret>"
EMAIL_SENDER="<an_email_to_send_mails_from>"

# API keys for Supabase, which is used as our database
SUPABASE_URL="https://<your_hidden_url>.supabase.co"
SUPABASE_KEY="<your_supabase_key>"

# A secret key used to sign and verify JWT tokens
JWT_SECRET="<a_randomly_generated_secret_key>"
```


## 💻 Usage
> [!NOTE]
>  Here is shown 2 different ways to run the program, `nr. 1` is for running the program locally in debug mode, and `nr. 2` is in a production enviroment, like on a server.

1. *Locally in debug mode*\
Run the app script:
```bash
python app.py
```

2. *In production (We use the serrvice [render](https://render.com/) which is free for limited use)*\
Run the app script, but with [gunicorn](https://gunicorn.org/):
```bash
gunicorn app:app
```



## 🔧 Technical Details
Will be added later

## 📚 Python Libaries

- [Flask](https://flask.palletsprojects.com/en/stable/) - Python webserver libary for hosting html content and handeling backend
- [bcrypt](https://github.com/pyca/bcrypt/) - Libary for secure hashing and hash validation
- [PyJWT](https://github.com/jpadilla/pyjwt) - Used for creating and validating JWT tokens



## 🥶 Development Team

- [Bertram Aakjær](https://github.com/BertramAakjaer)
- [Katrine Kloch](https://github.com/Kkloch)
- [Harun](https://github.com/Oxalo31)
- [Saba Idris](https://github.com/SabaIdris)
- [Tobias Petersen](https://github.com/Tuhu101)

---