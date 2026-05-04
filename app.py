import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime

# --- DATABASE CONNECTION ---
def connect_to_db():
    try:
        with open("db_config.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        return mysql.connector.connect(
            host=lines[0], user=lines[1], password=lines[2], database=lines[3],
            unix_socket="/tmp/mysql.sock"
        )
    except Exception:
        return mysql.connector.connect(
            host="127.0.0.1", user="root", password="smu2026", database="SocialMediaDB",
            unix_socket="/tmp/mysql.sock"
        )

# --- PAGE CONFIG ---
st.set_page_config(page_title="SMU Social Media DB", page_icon="🐎", layout="wide")

# --- CUSTOM CSS FOR THE "CUTE" FACTOR ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #3498db; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    .header-style { color: #3498db; font-family: 'Helvetica'; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR BRANDING ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/f/f0/SMU_Mustangs_logo.svg", width=100)
st.sidebar.title("Navigation")
menu = st.sidebar.pills("Choose Action:", ["Project Setup", "Data Entry", "Analytics"])

# --- PROJECT SETUP (Op 0) ---
if menu == "Project Setup":
    st.markdown("<h1 class='header-style'>📁 Project Initialization</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.container(border=True):
            st.subheader("Operation 0: New Project")
            with st.form("project_form", clear_on_submit=True):
                p_name = st.text_input("Project Name (Unique ID)")
                c1, c2 = st.columns(2)
                m_f = c1.text_input("Manager First Name")
                m_l = c2.text_input("Manager Last Name")
                inst = st.text_input("Institute Name", value="Southern Methodist University")
                d1, d2 = st.columns(2)
                s_date = d1.date_input("Start Date")
                e_date = d2.date_input("End Date")
                
                if st.form_submit_button("✨ Initialize Project"):
                    try:
                        conn = connect_to_db()
                        cursor = conn.cursor()
                        query = "INSERT INTO Projects VALUES (%s, %s, %s, %s, %s, %s)"
                        cursor.execute(query, (p_name, m_f, m_l, inst, s_date, e_date))
                        conn.commit()
                        st.balloons()
                        st.success(f"Project '{p_name}' is ready!")
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- DATA ENTRY (Op 46) ---
elif menu == "Data Entry":
    st.markdown("<h1 class='header-style'>📝 Social Media Data Entry</h1>", unsafe_allow_html=True)
    
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM Projects")
    project_list = [row[0] for row in cursor.fetchall()]
    
    tab1, tab2 = st.tabs(["Add Single Post", "Bulk Upload (Coming Soon)"])
    
    with tab1:
        target_project = st.selectbox("Select Project for Association", project_list)
        with st.container(border=True):
            with st.form("post_form", clear_on_submit=True):
                p_text = st.text_area("What was posted?")
                c1, c2 = st.columns(2)
                p_user = c1.text_input("User Handle")
                p_media = c2.selectbox("Platform", ["Instagram", "Facebook", "Twitter", "TikTok"])
                
                if st.form_submit_button("🚀 Submit to Database"):
                    # Duplication Check (Op 47)
                    cursor.execute("SELECT post_id FROM Posts WHERE post_text=%s AND username=%s", (p_text, p_user))
                    result = cursor.fetchone()
                    
                    if result:
                        st.warning("⚠️ Duplicate detected! Linking existing record.")
                        post_id = result[0]
                    else:
                        cursor.execute("INSERT INTO Posts (post_text, media_name, username, post_time) VALUES (%s, %s, %s, NOW())", 
                                       (p_text, p_media, p_user))
                        post_id = cursor.lastrowid
                    
                    cursor.execute("INSERT IGNORE INTO ProjectAnalysis (project_name, post_id) VALUES (%s, %s)", (target_project, post_id))
                    conn.commit()
                    st.toast(f"Post linked to {target_project}!")

# --- ANALYTICS/QUERIES (Op 50-54) ---
elif menu == "Analytics":
    st.markdown("<h1 class='header-style'>🔍 Database Insights</h1>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.divider()
        q_choice = st.selectbox("Search By:", ["Platform", "Username", "Project"])
        val = st.text_input(f"Enter {q_choice}")

    if val:
        conn = connect_to_db()
        cursor = conn.cursor()
        sql = """
            SELECT p.post_text, p.username, p.media_name, p.post_time, GROUP_CONCAT(pa.project_name)
            FROM Posts p
            LEFT JOIN ProjectAnalysis pa ON p.post_id = pa.post_id
            WHERE p.media_name LIKE %s OR p.username LIKE %s
            GROUP BY p.post_id
        """
        cursor.execute(sql, (f"%{val}%", f"%{val}%"))
        df = pd.DataFrame(cursor.fetchall(), columns=["Post Content", "User", "Platform", "Timestamp", "Linked Projects"])
        
        st.dataframe(df, use_container_width=True)
        st.metric("Total Results Found", len(df))