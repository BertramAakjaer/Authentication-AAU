import bcrypt

# Using the hash type: EksBlowfish

# Returnerer hash af en given adgangskode
def hash_password(password):
    password_bytes = password.encode('utf-8') # Laver string fra python string til rå data
    
    salt = bcrypt.gensalt(rounds=12) # 12 runder bruges under hashing
    hashed_password = bcrypt.hashpw(password_bytes, salt) # Opretter den 

    encoded_hash = hashed_password.decode('utf-8') # For at kunne gemme i databasen laves de rå data til UTF-8
    return encoded_hash


def verify_password(password, stored_hash):
    decoded_hash = stored_hash.encode('utf-8') # Laver den gemte password hash til rå bytes
    
    password_bytes = password.encode('utf-8') # Laver det givne password fra streng til rå bytes
    
    return bcrypt.checkpw(password_bytes, decoded_hash) # Returnerer om adgangskoden og hash'en matcher