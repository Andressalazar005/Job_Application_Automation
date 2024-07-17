def generate_config_template(jobs):
    key = load_key()
    
    # Example LinkedIn credentials
    linkedin_username = "your_linkedin_username"
    linkedin_password = "your_linkedin_password"
    
    encrypted_username, encrypted_password = encrypt_credentials(linkedin_username, linkedin_password, key)
    
    # Configuration template
    common_fields = {
        "job_site_url": "https://www.example.com/jobs",
        "personal_info": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "resume_path": "/path/to/your/resume.pdf"
        },
        "form_fields": {
            "name_field_id": "name",
            "email_field_id": "email",
            "resume_field_id": "resume",
            "submit_button_id": "submit"
        },
        "filters": {
            "keywords": ["remote", "engineer", "developer"]
        },
        "google_sheets": {
            "spreadsheet_id": "your_google_sheet_id"
        },
        "linkedin_credentials": {
            "username": encrypted_username,
            "password": encrypted_password
        }
    }
    
    # Save the configuration template to a JSON file
    with open('config.json', 'w') as config_file:
        json.dump(common_fields, config_file, indent=4)
        
    print("Configuration template generated and saved as config.json")

# Example usage
if __name__ == '__main__':
    generate_config_template([])
