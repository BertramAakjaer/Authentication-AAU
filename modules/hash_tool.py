import bcrypt

# Using the has type: EksBlowfish

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    encoded_bytes = hashed_password.decode('utf-8')
    
    return encoded_bytes


def verify_password(password, stored_hash):
    decoded_string = stored_hash.encode('utf-8')

    password_bytes = password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, decoded_string)