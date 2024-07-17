import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from data_handler import track_job_application
import time

def get_job_listings(url, log_text):
    log_message(log_text, f"Fetching job listings from {url}...")
    jobs = []
    page = 1

    while True:
        paginated_url = f"{url}&start={page * 25}"
        log_message(log_text, f"Fetching page {page}...")
        response = requests.get(paginated_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        job_elements = soup.find_all('div', class_='job-card-container')

        if not job_elements:
            log_message(log_text, "No more job listings found.")
            break

        for job_element in job_elements:
            title_element = job_element.find('h3', class_='job-card-list__title')
            company_element = job_element.find('h4', class_='job-card-container__company-name')
            location_element = job_element.find('span', class_='job-card-container__metadata-item')
            link_element = job_element.find('a', class_='job-card-container__link')
            description_element = job_element.find('p', class_='job-card-container__snippet')

            if title_element and company_element and location_element and link_element:
                title = title_element.text.strip()
                company = company_element.text.strip()
                location = location_element.text.strip()
                link = 'https://www.linkedin.com' + link_element['href']
                description = description_element.text.strip() if description_element else ""

                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': link,
                    'description': description
                })

        log_message(log_text, f"Found {len(job_elements)} jobs on page {page}.")
        page += 1
        time.sleep(1)  # To prevent rate limiting

    log_message(log_text, f"Total jobs found: {len(jobs)}")
    return jobs

def filter_jobs(jobs, filters, log_text):
    log_message(log_text, "Filtering jobs based on keywords and criteria...")
    filtered_jobs = []
    for job in jobs:
        match = True
        if 'keywords' in filters:
            match = all(keyword.lower() in job['title'].lower() for keyword in filters['keywords'])
        if match and 'remote' in filters and filters['remote']:
            match = match and ('remote' in job['location'].lower() or 'home' in job['location'].lower())
        if match and 'full_time' in filters and filters['full_time']:
            match = match and ('full-time' in job['description'].lower() or 'full time' in job['description'].lower())
        if match and 'salary_range' in filters:
            salary_match = False
            for salary in filters['salary_range']:
                if salary.lower() in job['description'].lower():
                    salary_match = True
                    break
            match = match and salary_match

        if match:
            filtered_jobs.append(job)

    log_message(log_text, f"{len(filtered_jobs)} jobs matched the filters.")
    return filtered_jobs

def apply_for_job(job, config, frame, log_text):
    try:
        if config.get('debug_mode', False):
            result = "Debug - No Application Sent"
        else:
            driver = webdriver.Chrome(ChromeDriverManager().install())
            driver.get(job['link'])

            # Fill out the application form
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
        job_label = tk.Label(frame, text=f"{job['title']} - {result}")
        job_label.pack()

        log_message(log_text, f"Applied to {job['title']} at {job['company']} - {result}")

        if not config.get('debug_mode', False):
            track_job_application(job, config['google_sheets']['spreadsheet_id'])

    except Exception as e:
        result = f"Failed: {str(e)}"
        log_message(log_text, f"Error applying to {job['title']} at {job['company']}: {result}")

        job_label = tk.Label(frame, text=f"{job['title']} - {result}")
        job_label.pack()

def start_applying(frame, config, log_text):
    url = config['job_site_url']
    jobs = get_job_listings(url, log_text)
    filtered_jobs = filter_jobs(jobs, config['filters'], log_text)

    for job in filtered_jobs:
        apply_for_job(job, config, frame, log_text)

def get_keywords_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    keywords = set()

    for job_element in soup.find_all('div', class_='job-card-container'):
        title = job_element.find('h3', class_='job-card-list__title').text.strip()
        for word in title.split():
            keywords.add(word.lower())

    return list(keywords)

def log_message(log_text, message):
    log_text.insert(tk.END, message + '\n')
    log_text.see(tk.END)
