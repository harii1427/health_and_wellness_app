import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File paths for user data, health records, and appointments
USER_DATA_FILE = 'users.csv'
HEALTH_RECORD_FILE = 'health_records.csv'
APPOINTMENTS_FILE = 'appointments.csv'

def initialize_files():
    """Ensure necessary files exist, otherwise create them."""
    if not os.path.exists(USER_DATA_FILE):
        pd.DataFrame(columns=['username', 'password', 'name', 'gender', 'age']).to_csv(USER_DATA_FILE, index=False)
    if not os.path.exists(HEALTH_RECORD_FILE):
        pd.DataFrame(columns=['username', 'name', 'age', 'gender', 'height', 'weight']).to_csv(HEALTH_RECORD_FILE, index=False)
    if not os.path.exists(APPOINTMENTS_FILE):
        pd.DataFrame(columns=['username', 'date', 'time', 'reason']).to_csv(APPOINTMENTS_FILE, index=False)

def save_user_data(username, password, name, gender, age):
    user_df = pd.read_csv(USER_DATA_FILE) if os.path.exists(USER_DATA_FILE) else pd.DataFrame(columns=['username', 'password', 'name', 'gender', 'age'])
    if username in user_df['username'].values:
        st.error("Username already exists. Please choose a different username.")
        return
    user_df = pd.concat([user_df, pd.DataFrame([{'username': username, 'password': password, 'name': name, 'gender': gender, 'age': age}])], ignore_index=True)
    user_df.to_csv(USER_DATA_FILE, index=False)
    st.success("Signup Successful!")

def check_user_credentials(username, password):
    if not os.path.exists(USER_DATA_FILE):
        st.error("User database not found. Please contact an administrator.")
        return False
    user_df = pd.read_csv(USER_DATA_FILE)
    if not user_df[user_df['username'] == username].empty:
        user_row = user_df[user_df['username'] == username].iloc[0]
        db_password = user_row['password']
        if str(db_password) == password:
            return True 
    return False

def schedule_appointment(username):
    st.title("Schedule a New Appointment")
    date = st.date_input("Date", min_value=datetime.today())
    time = st.time_input("Time")
    reason = st.text_area("Reason for the appointment")
    
    if st.button("Schedule"):
        appointments_df = pd.read_csv(APPOINTMENTS_FILE)
        new_appointment = {'username': username, 'date': date, 'time': time.strftime('%H:%M'), 'reason': reason}
        new_appointment_df = pd.DataFrame([new_appointment])  # Create a DataFrame from the new appointment
        appointments_df = pd.concat([appointments_df, new_appointment_df], ignore_index=True)
        appointments_df.to_csv(APPOINTMENTS_FILE, index=False)
        st.success("Appointment scheduled successfully.")


def view_appointments(username):
    st.title("Your Appointments")
    appointments_df = pd.read_csv(APPOINTMENTS_FILE)
    user_appointments = appointments_df[appointments_df['username'] == username]
    
    if user_appointments.empty:
        st.write("You have no appointments scheduled.")
    else:
        user_data = pd.read_csv(USER_DATA_FILE)  # Load user data file
        for i, appointment in user_appointments.iterrows():
            patient_name = user_data[user_data['username'] == appointment['username']]['name'].iloc[0]  # Get patient name from user data
            st.markdown(f"""
- **Date**: {appointment['date']}
- **Time**: {appointment['time']}
- **Reason**: {appointment['reason']}
- **Patient Name**: {patient_name}
""")

def login():
    st.title("Login")
    username = st.text_input("Username", placeholder="Enter Username")
    password = st.text_input("Password", type="password", placeholder="Enter Password")
    if st.button("Login"):
        if check_user_credentials(username, password):
            st.session_state['username'] = username
            st.success("Login Successful!")
            st.experimental_rerun()  # Rerun the app to reflect the login state
        else:
            st.error("Invalid username or password.")

def signup():
    st.title("Signup")
    name = st.text_input("Name", placeholder="Enter your name")
    username = st.text_input("Username", placeholder="Choose a username")
    password = st.text_input("Password", type="password", placeholder="Enter a password")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=0, max_value=150, step=1, value=18)
    if st.button("Sign Up"):
        save_user_data(username, password, name, gender, age)

def user_logged_in():
    st.sidebar.title(f"Welcome, {st.session_state['username']}")
    options = ["Logout", "View Appointments", "Schedule Appointment", "View & Update Health Record"]
    choice = st.sidebar.radio("Choose an option", options,index=None)
    
    if choice == "Logout":
        st.write("**Do You Really Want To Logout?**")
        yes =st.button("Yes")
        if yes:
            del st.session_state['username']
            st.experimental_rerun()
    elif choice == "View Appointments":
        view_appointments(st.session_state['username'])
    elif choice == "Schedule Appointment":
        schedule_appointment(st.session_state['username'])
    elif choice == "View & Update Health Record":
        view_update_health_record(st.session_state['username'])


def view_update_health_record(username):
    """Displays and provides an option to update the user's health record."""
    st.title("Your Health Record")
    # Initialize local variable 'user_record' to ensure it's defined
    user_record = pd.DataFrame()  # Empty DataFrame placeholder
    if os.path.exists(HEALTH_RECORD_FILE):
        health_df = pd.read_csv(HEALTH_RECORD_FILE)
        if 'username' in health_df.columns:
            user_record = health_df[health_df['username'] == username]
            if not user_record.empty:
                user_record = user_record.iloc[0]
                st.table(user_record.drop('username'))
            else:
                st.write("No health record found. Please add your health details.")
        else:
            st.error("Health record format error: 'username' column not found.")
    else:
        st.error("Health record data not found.")
    
    # Update Health Record Section
    st.write("## Update Health Record")
    with st.form("health_record_form"):
        name = st.text_input("Name", value="" if user_record.empty else user_record['name'])
        age = st.number_input("Age", min_value=0, max_value=130, value=0 if user_record.empty else int(user_record['age']))
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0 if user_record.empty else ["Male", "Female", "Other"].index(user_record['gender']))
        height = st.number_input("Height (cm)", min_value=0.0, max_value=300.0, value=0.0 if user_record.empty else float(user_record['height']))
        weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=0.0 if user_record.empty else float(user_record['weight']))
        submit_button = st.form_submit_button("Update")

    if submit_button:
        update_health_record(username, name, age, gender, height, weight)
        st.rerun()


def update_health_record(username, name, age, gender, height, weight):
    """Updates the health record for a given user."""
    health_df = pd.read_csv(HEALTH_RECORD_FILE) if os.path.exists(HEALTH_RECORD_FILE) else pd.DataFrame(columns=['username', 'name', 'age', 'gender', 'height', 'weight'])
    
    # Remove existing record for the given username, if it exists
    health_df = health_df[health_df['username'] != username]
    
    # Create a new record DataFrame from the provided data
    new_record = pd.DataFrame({'username': [username], 'name': [name], 'age': [age], 'gender': [gender], 'height': [height], 'weight': [weight]})
    
    # Concatenate the new_record DataFrame with the existing health_df DataFrame
    health_df = pd.concat([health_df, new_record], ignore_index=True)
    
    # Save the updated health record DataFrame to the file
    health_df.to_csv(HEALTH_RECORD_FILE, index=False)
    
    st.success("Health record updated successfully.")



def main():
    initialize_files()
    if 'username' in st.session_state:
        user_logged_in()
    else:
        choice = st.sidebar.radio("Choose action", ["Login", "Signup"])
        if choice == "Login":
            login()
        elif choice == "Signup":
            signup()

if __name__ == "__main__":
    main()
