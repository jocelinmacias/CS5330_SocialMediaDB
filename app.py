import streamlit as st
import mysql.connector

def connect_to_db():
    try:
        with open("db_config.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user=lines[1],
            password=lines[2],
            database=lines[3],
            # On macOS, using the socket is often required for local terminal connections
            unix_socket="/tmp/mysql.sock" 
        )
        return conn
    except Exception as e:
        # If the socket above fails, try it without the socket line
        return mysql.connector.connect(host="127.0.0.1", user=lines[1], password=lines[2], database=lines[3])