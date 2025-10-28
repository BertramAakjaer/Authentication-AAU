import os
from supabase import create_client, Client
from dotenv import load_dotenv

import modules.hash_tool as hash


load_dotenv() # Henter api keys

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)



def create_user(email, username, password):
    email = email.lower()

    password = hash.hash_password(password)

    response = supabase.table("users").insert({"email": email, "password": password, "username": username}).execute()
    print("Inserted Data:", response.data)


def get_data():
    # Select all
    response = supabase.table("users").select("*").execute()
    print("All Users:", response.data)

    # with a filter
    response = supabase.table("users").select("*").eq("email", "jan45@realmail.com").execute()
    print("Filtered Users:", response.data)


def get_user_by_mail(email):
    email = email.lower()

    response = supabase.table("users").select("*").eq("email", email).execute()
    print("Filtered Users:", response.data)


def update_password(email, new_pass):
    email = email.lower()
    new_pass = hash.hash_password(new_pass)

    update_data = {"password": new_pass}
    response = supabase.table("countries").update(update_data).eq("email", email).execute()
    print("Updated Data:", response.data)


def get_pass(email):
    email = email.lower()

    try:
        response = supabase.table("users")\
            .select("password")\
            .eq('email', email)\
            .single()\
            .execute()
        
        row_data = response.data 
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        row_data = None
    
    if row_data:
        user_pass = row_data.get("password")
        return user_pass
    else:
        return ""



if __name__ == "__main__":
    email = "Jan45@realmail.com"
    username = "Jan"
    password = "123456"

    #create_user(email, username, password)

    #get_data()

    #get_user_by_mail(email)

    #update_password(email, "654321")

    #get_pass(email)
