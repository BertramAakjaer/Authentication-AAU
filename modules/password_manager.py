import time

auth_codes = [] # Formateret son [email, password, timestamp]

max_auth_time = 60 * 5 # Max tid for authentication password


# Til at tilføje nye auth koder
def add_auth_code(email, auth_pass):
    auth_codes.append([email, auth_pass, int(time.time())])
    print(f"Added password {auth_pass}")

# Selv-kaldt funktion til at fjerne udløbede adgangskoder
def remove_expired_passwords():
    
    for i in auth_codes:
        if (int(time.time()) - i[2]) >= max_auth_time:
            auth_codes.remove(i)
            print(f"removed {i} with the time difference {(int(time.time()) - i[2])}")
        else:
            break

# Checker om en kode findes i listen
def verify_auth_code(email, user_written_pass):
    remove_expired_passwords()
    
    for i in auth_codes:
        if i[0] == email and i[1] == user_written_pass:
            auth_codes.remove(i)
            return True
        
    return False