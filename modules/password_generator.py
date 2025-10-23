import random

def pass_random():
    letters = "abcdefghijklmnopqrstuvwxyzæøå"

    auth_pass = ""

    for i in range(6):
        auth_pass += random.choice(letters)

    print(auth_pass)
    return auth_pass