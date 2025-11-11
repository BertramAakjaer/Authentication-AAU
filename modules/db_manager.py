import os
from datetime import datetime, timezone, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Vores eget script til at lave hashes
import modules.hash_tool as hash


load_dotenv() # Henter api keys fra .env fil

# Gemme værdier i variabler
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Opretter client til at tale med databasen
supabase = create_client(supabase_url, supabase_key)



# Tjekker om en konto findes ud fra mailen
def account_exists(email):
    email = email.lower() # Sikrer at mailen er i små bogstaver

    try:
        # Returnere en værdi hvis en konto med emailen eksisterer 
        response = supabase.table("users")\
            .select("email")\
            .eq("email", email)\
            .limit(1)\
            .execute()
            
        return True if (response.data) else False

    except:
        return False


# Opretter en konto
def create_account(email, password):
    try:
        email = email.lower() # Sikrer at mailen er i små bogstaver
        password = hash.hash_password(password) # Hasher adgangskoden med bcrypt

        # Opretter konto med email og password
        response = supabase.table("users").insert({"email": email, "password": password, "username": email}).execute()
        
        return True if (response.data) else False
    except:
        return False


# Tjekker om en given adgangskode og email passer med det der ligge i databasen
def verify_pass(email, password):    
    email = email.lower() # Sikrer at mailen er i små bogstaver
    
    try:
        # Henter det hashede password, ud fra email
        response = supabase.table("users")\
            .select("password")\
            .eq('email', email)\
            .single()\
            .execute()
        
        row_data = response.data 
        
    except:
        row_data = None
    
    # Hvis dataen findes
    if row_data:
        user_pass_hash = row_data.get("password")
    else:
        return False
    
    # Returner om det bruger givne password passer med den gemte hash
    return hash.verify_password(password, user_pass_hash)
    

# Henter username ud fra email
def get_username(email):    
    email = email.lower() # Sikrer at mailen er i små bogstaver
    
    username = ""
    
    try:
        # Hente username ud fra email
        response = supabase.table("users")\
            .select("username")\
            .eq('email', email)\
            .single()\
            .execute()
        
        row_data = response.data 
        
        # Hvis dataen fandtes
        if row_data:
            username = row_data.get("username")
        else:
            return False
        
    except:
        return False
        
    return username



# Ændrer password
def update_password(email, new_pass):
    email = email.lower() # Sikrer at mailen er i små bogstaver
    new_pass = hash.hash_password(new_pass) # Hasher adgangskoden med bcrypt

    update_data = {"password": new_pass} # Data der opdateres i databasen
    try:
        # Opdatere password ud fra email
        response = supabase.table("users").update(update_data).eq("email", email).execute()
        update_last_login(email) # Ændrer last_updated_at til at reflekter at adgangskoden er opdaterer
        
        return True if (response.data) else False

    except:
        return False
    

# Ændre det felt i databasen, hvor der står hvornår kontoen sidst er opdateret
def update_last_login(email):
    email = email.lower() # Sikrer at mailen er i små bogstaver

    utc_plus_one = timezone(timedelta(hours=1)) # UTC+1 er det vi har i danmark som ogs er CET (Centralt Eastern Time)
    current_utc_plus_one_datetime = datetime.now(utc_plus_one) # Henter tidstampet
    current_timestamp = current_utc_plus_one_datetime.isoformat().split('+')[0] # Returner tidsstemplet uden +1 utc stilen
    
    update_data = {"last_modified_at": current_timestamp} # Gives til databasen og opdaterer "last_modified_at" med current_timestamp
    
    try:
        # Updatere tidsstemplet til kontoen med den givne email
        response = supabase.table("users")\
            .update(update_data)\
            .eq("email", email)\
            .execute()
        
        return True if (response.data) else False
    
    except:
        return False
    

# Ændrer username
def update_username(email, new_username):
    email = email.lower() # Sikrer at mailen er i små bogstaver
    update_data = {"username": new_username} # Gives til databasen og opdaterer "username" med new_username
    
    try:
        # Updatere username til kontoen med den givne email
        response = supabase.table("users").update(update_data).eq("email", email).execute()
        return True if (response.data) else False

    except:
        return False


# Sletter en konto ud fra email
def delete_account(email):
    email = email.lower() # Sikrer at mailen er i små bogstaver

    try:
        # Udfører sletningen, hvor emailen matcher
        response = supabase.table("users")\
            .delete()\
            .eq("email", email)\
            .execute()
        
        # Tjekker om sletningen havde data (at en række blev slettet)
        return True if response.data else False

    except:
        return False



# Function der returnerer de dataoer vi viser angående ændret og oprettet account
def get_readable_timestamps(email):
    email = email.lower() # Sikrer at mailen er i små bogstaver
    
    # Opretter tomme variabler til at gemme data i
    last_modified_at = None
    created_at = None
    
    formatted_last_modfied_at = None
    formatted_created_at = None
    
    # Tidspunkter data fra databasen
    response1 = supabase.table("users")\
        .select("last_modified_at")\
        .eq('email', email)\
        .single()\
        .execute()
        
    response2 = supabase.table("users")\
        .select("created_at")\
        .eq('email', email)\
        .single()\
        .execute()

    # Gemmer data rækkerne
    row_data1 = response1.data
    row_data2 = response2.data
    
    # Tjekker om værdierne findes og henter de specifikke værdier
    if row_data1 and row_data1.get("last_modified_at"):
        last_modified_at = row_data1.get("last_modified_at")
    
    if row_data2 and row_data2.get("created_at"):
        created_at = row_data2.get("created_at")

    # Hvis værdierne findes formateres de korrekt
    if last_modified_at:
        dt_object = datetime.fromisoformat(last_modified_at)
        format_string = "%H:%M %d/%m/%Y"

        formatted_last_modfied_at = dt_object.strftime(format_string)
            
    if created_at:
        dt_object = datetime.fromisoformat(created_at)
        format_string = "%H:%M %d/%m/%Y"

        formatted_created_at = dt_object.strftime(format_string)
        
    # Returnerer de formaterede værdier som en tuple til nem
    return (formatted_created_at, formatted_last_modfied_at)
            














## Kan måske bruges, men bruges ikke lige nu \/


def get_data():
    # Select all
    response = supabase.table("users").select("*").execute()
    print("All Users:", response.data)

    # with a filter
    response = supabase.table("users").select("*").eq("email", "jan45@realmail.com").execute()
    print("Filtered Users:", response.data)