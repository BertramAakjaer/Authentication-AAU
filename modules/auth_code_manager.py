import time

auth_codes = [] # Formateret son [email, password, timestamp]
max_auth_time = 60 * 5 # Max tid for authentication password


# Til at tilføje nye auth koder
def add_auth_code(email, auth_pass):
    auth_codes.append([email, auth_pass, int(time.time())])
    print(f"Added password {auth_pass}")

# Selv-kaldt funktion til at fjerne udløbede adgangskoder
def remove_expired_auth_codes():
    
    for i in auth_codes: # Går igennem alle gemte koder
        if (int(time.time()) - i[2]) >= max_auth_time: # Tjekker om koden er udløbet
            auth_codes.remove(i) # Fjerner koden
            print(f"removed {i} with the time difference {(int(time.time()) - i[2])}")
        else:
            # Da koderne er oprettet i samme rækkefølge som de ligger (fifo),
            # så ved vi at alle efter en kode der ikke er udløbet, heller ikke
            # er udløbet og vi kan derfor sparer tid ved bare at kalde "break"
            break 

# Checker om en kode findes i listen
def verify_auth_code(email, user_written_pass):
    remove_expired_auth_codes() # Fjerner udløbede koder
    
    for i in auth_codes: # Tjekker alle koder igennem
        if i[0] == email and i[1] == user_written_pass: # Tjekker om mail og den givne authentication kode passer
            auth_codes.remove(i) # Fjerner koden efter brug
            
            return True
        
    return False