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
    email = email.lower()

    try:
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
        email = email.lower()
        password = hash.hash_password(password)

        response = supabase.table("users").insert({"email": email, "password": password, "username": email}).execute()
        print("Inserted Data:", response.data)
        
        return True
    except:
        return False


# Tjekker om en given adgangskode og email passer med det der ligge i databasen
def verify_pass(email, password):    
    email = email.lower()
    try:
        response = supabase.table("users")\
            .select("password")\
            .eq('email', email)\
            .single()\
            .execute()
        
        row_data = response.data 
        
    except:
        print(f"Error fetching data")
        row_data = None
        
    if row_data:
        user_pass_hash = row_data.get("password")
    else:
        return False
    
    return hash.verify_password(password, user_pass_hash)
    

# Henter username ud fra email
def get_username(email):    
    email = email.lower()
    
    username = ""
    
    try:
        response = supabase.table("users")\
            .select("username")\
            .eq('email', email)\
            .single()\
            .execute()
        
        row_data = response.data 
        
        if row_data:
            username = row_data.get("username")
        else:
            return False
        
    except:
        print(f"Error fetching data")
        return False
        
    return username



# Ændrer password
def update_password(email, new_pass):
    email = email.lower()
    new_pass = hash.hash_password(new_pass)

    update_data = {"password": new_pass}
    try:
        response = supabase.table("users").update(update_data).eq("email", email).execute()
        update_last_login(email)
        return True if (response.data) else False

    except:
        return False
    

# Ændre det felt i databasen, hvor der står hvornår kontoen sidst er opdateret
def update_last_login(email):
    email = email.lower()

    utc_plus_one = timezone(timedelta(hours=1))

    current_utc_plus_one_datetime = datetime.now(utc_plus_one)

    current_timestamp = current_utc_plus_one_datetime.isoformat().split('+')[0]
    
    update_data = {"last_modified_at": current_timestamp}
    
    try:

        response = supabase.table("users")\
            .update(update_data)\
            .eq("email", email)\
            .execute()
        
        return True if (response.data) else False
    
    except:
        return False
    

# Ændrer username
def update_username(email, new_username):
    email = email.lower()
    update_data = {"username": new_username}
    
    try:
        response = supabase.table("users").update(update_data).eq("email", email).execute()
        return True if (response.data) else False

    except:
        return False


# Sletter en konto ud fra email
def delete_account(email):
    email = email.lower()

    try:
        # Udfører sletningen, hvor emailen matcher
        response = supabase.table("users")\
            .delete()\
            .eq("email", email)\
            .execute()
        
        # Tjekker om sletningen havde data (dvs. at en række blev slettet)
        # Hvis response.data er en tom liste [], betyder det at ingen række matchede og blev slettet.
        return True if response.data else False

    except:
        # Håndterer eventuelle fejl under sletningen
        return False




def get_readable_timestamps(email):
    email = email.lower()
    last_modified_at = None
    created_at = None
    
    formatted_last_modfied_at = None
    formatted_created_at = None
    

    response = supabase.table("users")\
        .select("last_modified_at")\
        .eq('email', email)\
        .single()\
        .execute()

    row_data = response.data
    
    if row_data and row_data.get("last_modified_at"):
        last_modified_at = row_data.get("last_modified_at")
    
    response = supabase.table("users")\
        .select("created_at")\
        .eq('email', email)\
        .single()\
        .execute()

    row_data = response.data
    
    if row_data and row_data.get("created_at"):
        created_at = row_data.get("created_at")
        

    if last_modified_at:
        dt_object = datetime.fromisoformat(last_modified_at)
        format_string = "%H:%M %d/%m/%Y"

        formatted_last_modfied_at = dt_object.strftime(format_string)
            
    if created_at:
        dt_object = datetime.fromisoformat(created_at)
        format_string = "%H:%M %d/%m/%Y"

        formatted_created_at = dt_object.strftime(format_string)
    
    return (formatted_created_at, formatted_last_modfied_at)
            



## Kan måske bruges \/


def get_data():
    # Select all
    response = supabase.table("users").select("*").execute()
    print("All Users:", response.data)

    # with a filter
    response = supabase.table("users").select("*").eq("email", "jan45@realmail.com").execute()
    print("Filtered Users:", response.data)

