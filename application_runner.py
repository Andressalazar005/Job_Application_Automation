import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from data_handler import track_job_application

def get_job_listings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    jobs = []
    for job_element in soup.find_all('div', class_='job_listing'):
        title = job_element.find('h2').text.strip()
        company = job_element.find('div', class_='company').text.strip()
        location = job_element.find('div', class_='location').text.strip()
        link = job_element.find('a')['href']

        jobs.append({
            'title': title,
            'company': company,
            'location': location,
            'link': link
        })

    return jobs

def filter_jobs(jobs, filters):
    filtered_jobs = []
    for job in jobs:
        match = all(keyword.lower() in job['title'].lower() for keyword in filters.get('keywords', []))
        if match:
            filtered_jobs.append(job)
    return filtered_jobs

def apply_for_job(job, config, frame):
    if config.get('debug_mode', False):
        result = "Debug - No Application Sent"
    else:
        try:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(job['link'])

            name_field = driver.find_element_by_id(config['form_fields']['name_field_id'])
            email_field = driver.find_element_by_id(config['form_fields']['email_field_id'])
            resume_field = driver.find_element_by_id(config['form_fields']['resume_field_id'])

            name_field.send_keys(config['personal_info']['name'])
            email_field.send_keys(config['personal_info']['email'])
            resume_field.send_keys(config['personal_info']['resume_path'])

            submit_button = driver.find_element_by_id(config['form_fields']['submit_button_id'])
            submit_button.click()

            driver.quit()

            result = "Success"
        except Exception as e:
            result = f"Failed: {str(e)}"

    job_label = tk.Label(frame, text=f"{job['title']} - {result}")
    job_label.pack()

    if not config.get('debug_mode', False):
        track_job_application(job, config['google_sheets']['spreadsheet_id'])

def start_applying(frame, config):
    url = config['job_site_url']
    jobs = get_job_listings(url)
    filtered_jobs = filter_jobs(jobs, config['filters'])

    for job in filtered_jobs:
        apply_for_job(job, config, frame)

def get_keywords_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    keywords = set()

    for job_element in soup.find_all('div', class_='job_listing'):
        title = job_element.find('h2').text.strip()
        for word in title.split():
            keywords.add(word.lower())

    return list(keywords)
