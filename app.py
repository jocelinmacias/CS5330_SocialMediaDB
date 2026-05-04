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
    except:
        return mysql.connector.connect(
            host="127.0.0.1", user="root", password="smu2026", database="SocialMediaDB",
            unix_socket="/tmp/mysql.sock"
        )

# --- PAGE CONFIG ---
st.set_page_config(page_title="Social Media Analysis DB", page_icon="📊", layout="wide")

# --- NAVIGATION ---
st.sidebar.title("🛠️ System Menu")
menu = st.sidebar.selectbox("Go to:", 
    ["Dashboard", "People & Accounts", "Projects & Fields", "Post Management", "Analysis", "Query Center"])

# --- 1. DASHBOARD ---
if menu == "Dashboard":
    st.title("🚀 Social Media Analysis Dashboard")
    st.info("Local GUI connected to MySQL / MariaDB")
    
    conn = connect_to_db()
    cursor = conn.cursor()
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    cursor.execute("SELECT COUNT(*) FROM People")
    c1.metric("People", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM Posters")
    c2.metric("Accounts", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM Posts")
    c3.metric("Posts", cursor.fetchone()[0])
    cursor.execute("SELECT COUNT(*) FROM Projects")
    c4.metric("Projects", cursor.fetchone()[0])

    st.divider()
    st.subheader("Suggested Demo Flow")
    st.write("1. Show MySQL backend | 2. Link 1 Person to Multiple Accounts | 3. Show Posts & Reposts | 4. Run Analysis")

# --- 2. PEOPLE & ACCOUNTS ---
elif menu == "People & Accounts":
    st.header("👤 People & Social Accounts")
    tab1, tab2 = st.tabs(["Add Person", "Link Account"])
    
    with tab1:
        with st.form("person_form"):
            f_name = st.text_input("First Name")
            l_name = st.text_input("Last Name")
            birth = st.text_input("Country of Birth")
            if st.form_submit_button("Save Person"):
                conn = connect_to_db()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO People (first_name, last_name, country_birth) VALUES (%s, %s, %s)", (f_name, l_name, birth))
                conn.commit()
                st.success("Person Added!")

    with tab2:
        st.subheader("Operation 49: Link Account to Person")
        # Fetch people for dropdown
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT person_id, first_name, last_name FROM People")
        people = {f"{r[1]} {r[2]}": r[0] for r in cursor.fetchall()}
        
        with st.form("account_form"):
            user = st.text_input("Username")
            media = st.selectbox("Platform", ["Instagram", "Twitter", "Facebook"])
            person = st.selectbox("Assign to Person", list(people.keys()))
            if st.form_submit_button("Link Account"):
                cursor.execute("INSERT INTO Posters (username, media_name, person_id) VALUES (%s, %s, %s)", 
                               (user, media, people[person]))
                conn.commit()
                st.success("Account Linked!")

# --- 3. PROJECTS & FIELDS ---
elif menu == "Projects & Fields":
    st.header("📂 Projects & Analysis Fields")
    with st.form("proj_form"):
        name = st.text_input("Project Name")
        manager = st.text_input("Manager Name")
        if st.form_submit_button("Create Project"):
            conn = connect_to_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Projects (project_name, manager_last) VALUES (%s, %s)", (name, manager))
            conn.commit()
            st.success("Project Live!")

# --- 4. POST MANAGEMENT ---
elif menu == "Post Management":
    st.header("📝 Post Entry")
    with st.form("post_entry"):
        txt = st.text_area("Content")
        user = st.text_input("Handle")
        plat = st.selectbox("Platform", ["Instagram", "Twitter"])
        if st.form_submit_button("Submit Post"):
            conn = connect_to_db()
            cursor = conn.cursor()
            # Op 47: Duplicate check
            cursor.execute("SELECT post_id FROM Posts WHERE post_text=%s", (txt,))
            if cursor.fetchone():
                st.warning("Post already exists!")
            else:
                cursor.execute("INSERT INTO Posts (post_text, username, media_name, post_time) VALUES (%s, %s, %s, NOW())", (txt, user, plat))
                conn.commit()
                st.success("Post Saved!")

# --- 5. ANALYSIS ---
elif menu == "Analysis":
    st.header("🧪 Enter Analysis Results")
    conn = connect_to_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT project_name FROM Projects")
    projs = [r[0] for r in cursor.fetchall()]
    selected_proj = st.selectbox("Select Project", projs)
    
    with st.form("analysis_form"):
        field = st.text_input("Field Name (e.g., Sentiment)")
        val = st.text_input("Value (e.g., Positive)")
        post_id = st.number_input("Post ID", step=1)
        if st.form_submit_button("Save Result"):
            cursor.execute("INSERT INTO ProjectAnalysis VALUES (%s, %s, %s, %s)", (selected_project, post_id, field, val))
            conn.commit()
            st.success("Analysis Recorded!")

# --- 6. QUERY CENTER ---
elif menu == "Query Center":
    st.header("🔍 Query Results")
    q_type = st.radio("Query by:", ["Username", "Platform", "Project Stats"])
    
    val = st.text_input("Search term")
    if st.button("Run Intelligence Query"):
        conn = connect_to_db()
        cursor = conn.cursor()
        if q_type == "Username":
            cursor.execute("SELECT * FROM Posts WHERE username = %s", (val,))
        elif q_type == "Platform":
            cursor.execute("SELECT * FROM Posts WHERE media_name = %s", (val,))
        
        df = pd.DataFrame(cursor.fetchall())
        st.dataframe(df)