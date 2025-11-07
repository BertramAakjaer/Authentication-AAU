import os
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
            
        return bool(response.data)

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










## Kan måske bruges \/


def get_data():
    # Select all
    response = supabase.table("users").select("*").execute()
    print("All Users:", response.data)

    # with a filter
    response = supabase.table("users").select("*").eq("email", "jan45@realmail.com").execute()
    print("Filtered Users:", response.data)

def update_password(email, new_pass):
    email = email.lower()
    new_pass = hash.hash_password(new_pass)

    update_data = {"password": new_pass}
    response = supabase.table("countries").update(update_data).eq("email", email).execute()
    print("Updated Data:", response.data)