import streamlit as st
import mysql.connector

def connect_to_db():
    try:
        # Hardcoding for a quick demo test - switch back to file read after!
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="smu2026",
            database="SocialMediaDB",
            unix_socket="/tmp/mysql.sock" # This helps Mac Python find Mac Terminal MySQL
        )
        return conn
    except Exception as e:
        st.error(f"Try running 'brew services restart mysql' in terminal. Error: {e}")
        return None

if st.button("Test Connection"):
    c = connect_to_db()
    if c:
        st.success("Connected to Mac Terminal MySQL!")