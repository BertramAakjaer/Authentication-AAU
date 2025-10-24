import random

def pass_random():
    letters = "abcdefghijklmnopqrstuvwxyzæøå"

    auth_pass = ""

    for i in range(8):
        temp = random.choice(letters)
        if random.randint(1, 100) > 50:
            temp = temp.upper()
        auth_pass += temp

    print(auth_pass)
    return auth_pass