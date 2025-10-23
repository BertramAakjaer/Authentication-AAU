import streamlit as st

from modules.password_generator import pass_random
import modules.password_manager as pass_manager
from modules.mail_sender import send_mail

do_not_send_mail = False


st.title("OTP Login")

if st.checkbox("Use real mail service?"):
    do_not_send_mail = False
else:
    do_not_send_mail = True

    
mail = st.text_input("E-mail:")

if st.button("Send password"):
    auth_pass = pass_random()
    pass_manager.add_password(mail, auth_pass)
    
    if send_mail(auth_pass, mail, do_not_send_mail):
        st.success("Email sent to user")  
    else:
        st.error("Email couldn't send")
        st.stop()

user_written_pass = st.text_input("Password:")
if st.button("Check password"):
    if pass_manager.get_password(mail, user_written_pass):
        st.success("Correct code !!!")
    else:
        st.error("Incorrect code !!")