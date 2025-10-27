import random

def pass_random():
    symbols = "abcdefghkmnopqrstuvwxyz0123456789"

    auth_pass = ""

    for i in range(6):
        temp = random.choice(symbols)
        if random.randint(1, 100) > 50:
            temp = temp.upper()
        auth_pass += temp

    print(auth_pass)
    return auth_pass