import time


passwords = [] # Formatted like [email, password, timestamp]

max_pass_time = 10


def add_password(email, auth_pass):
    passwords.append([email, auth_pass, int(time.time())])
    print(f"Added password {auth_pass}")

def remove_expired_passwords():
    for i in passwords:
        if (int(time.time()) - i[2]) >= max_pass_time:
            passwords.remove(i)
            print(f"removed {i} with the time difference {(int(time.time()) - i[2])}")
        else:
            break

def get_password(email, user_written_pass):
    remove_expired_passwords()
    
    for i in passwords:
        if i[0] == email and i[1] == user_written_pass:
            return True
        
    return False