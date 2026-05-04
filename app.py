import streamlit as st
import mysql.connector

def connect_to_db():
    try:
        with open("db_config.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        # Ensure we have all 4 required pieces of info
        if len(lines) < 4:
            st.error("db_config.txt must have 4 lines: host, user, password, database")
            return None

        conn = mysql.connector.connect(
            host=lines[0],
            user=lines[1],
            password=lines[2],
            database=lines[3],
            port=3306 # Force standard port
        )
        return conn
    except Exception as e:
        st.error(f"Connection Failed: {e}")
        return None

# Test the connection immediately
connection = connect_to_db()
if connection and connection.is_connected():
    st.sidebar.success("Database Connected!")
else:
    st.sidebar.error("Database Offline")