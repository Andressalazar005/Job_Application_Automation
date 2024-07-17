import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
import time
import re
import tkinter as tk

def start_applying(frame, config, log_text):
    def log(message):
        log_text.insert(tk.END, message + '\n')
        log_text.see(tk.END)
    
    # Log into LinkedIn
    linkedin_credentials = config.get("linkedin_credentials", {})
    username = linkedin_credentials.get("username")
    password = linkedin_credentials.get("password")

    if not username or not password:
        log("LinkedIn credentials are missing.")
        return

    options = webdriver.FirefoxOptions()
    options.add_argument("--start-maximized")

    try:
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    except Exception as e:
        log(f"Error: {e}\nPlease ensure Firefox is installed.")
        return

    try:
        driver.get("https://www.linkedin.com/login")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )

        username_field = driver.find_element(By.ID, "username")
        username_field.clear()
        username_field.send_keys(username)

        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "profile-nav-item"))
        )

        log("Successfully logged into LinkedIn.")

        # Add code to apply for jobs using the provided filters

    except Exception as e:
        log(f"An error occurred: {e}")
    finally:
        time.sleep(5)  # Optional: wait for a few seconds to see the result
        driver.quit()

def get_keywords_from_url(url):
    # Dummy implementation to simulate keyword extraction
    return ["developer", "engineer", "python"]

def load_client_config(file_path="credentials/credentials.json"):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_to_csv(data, filename="scraped_data.csv"):
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def extract_spreadsheet_id(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Google Sheets URL format")

def get_authenticated_session(client_config, token_file="credentials/token.json"):
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, ["https://www.googleapis.com/auth/spreadsheets"])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(client_config, ["https://www.googleapis.com/auth/spreadsheets"])
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    session = requests.Session()
    session.headers.update({'Authorization': f'Bearer {creds.token}'})
    return session

def upload_to_google_sheets(data, spreadsheet_url, range_name="Sheet1!A1", token_file="credentials/token.json"):
    client_config = load_client_config()

    try:
        spreadsheet_id = extract_spreadsheet_id(spreadsheet_url)
    except ValueError as e:
        print(f"Error: {e}")
        return False

    url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append?valueInputOption=RAW"
    headers = {"Content-Type": "application/json"}
    payload = {
        "range": range_name,
        "majorDimension": "ROWS",
        "values": data
    }

    try:
        session = get_authenticated_session(client_config, token_file)
        response = session.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as error:
        print(f"Error uploading to Google Sheets: {error}")
        return False
