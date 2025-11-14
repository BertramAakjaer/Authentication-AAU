import random

def auth_code_random(): # Funktion der kan kaldes af andre scripts
    symbols = "abcdefghkmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" # Alle gyldige tegn der kan bruges

    auth_pass = "" # En tom klartekst, der bruges til at putte tegn i

    for i in range(6): # Tilføjer x antal tegn til klartekst strengen
        
        temp = random.choice(symbols) # Henter et tilfældigt symbol fra de "gyldige tegn" om gemmer den i en temporary variable
        if random.randint(1, 10) <= 5: # 50% chance for at lave bogstaver til store
            temp = temp.upper() # Laver bogstav til stort
            
        auth_pass += temp # Tilføjer det givne tegn til variablen

    print(f"Made auth pass: {auth_pass}")
    return auth_pass # Returnerer den endelige kode