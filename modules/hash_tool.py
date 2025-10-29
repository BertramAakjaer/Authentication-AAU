import bcrypt

# Using the has type: EksBlowfish

def hash_password(password):
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    encoded_hash = hashed_password.decode('utf-8') # For at kunne gemme i databasen
    
    return encoded_hash


def verify_password(password, stored_hash):
    decoded_hash = stored_hash.encode('utf-8') # Fjenere database encodingen

    password_bytes = password.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, decoded_hash)


if __name__ == "__main__":
    a = hash_password("testpass")
    
    print(a)
    
    b = verify_password("ikkerigtigpass", a)
    
    print(f"test 1: {b}")
    
    c = verify_password("testpass", a)
    
    print(f"test 2: {c}")