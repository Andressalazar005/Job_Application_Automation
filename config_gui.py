import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import webbrowser
from application_runner import start_applying, get_keywords_from_url
from cryptography.fernet import Fernet
import re  # Import the re module

class ConfigGUI:
    def __init__(self, master):
        self.master = master
        master.title("Job Application Bot Configuration")

        self.key = self.load_key()
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
                if "linkedin_credentials" not in self.config:
                    self.config["linkedin_credentials"] = {"username": "", "password": ""}
        else:
            self.config = {
                "job_site_url": "",
                "personal_info": {
                    "name": "",
                    "email": "",
                    "resume_path": ""
                },
                "form_fields": {
                    "name_field_id": "name",
                    "email_field_id": "email",
                    "resume_field_id": "resume",
                    "submit_button_id": "submit"
                },
                "filters": {
                    "keywords": [],
                    "remote": False,
                    "full_time": False,
                    "salary_range": []
                },
                "google_sheets": {
                    "spreadsheet_id": ""
                },
                "linkedin_credentials": {
                    "username": "",
                    "password": ""
                },
                "debug_mode": False
            }

        self.create_widgets()
        self.log("Application started.")

        self.decrypt_credentials()

        if self.config['job_site_url']:
            self.update_keywords()

    def load_key(self):
        key_path = "secret.key"
        if os.path.exists(key_path):
            return open(key_path, "rb").read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as key_file:
                key_file.write(key)
            return key

    def encrypt_credentials(self):
        f = Fernet(self.key)
        credentials = self.config["linkedin_credentials"]
        credentials["username"] = f.encrypt(credentials["username"].encode()).decode()
        credentials["password"] = f.encrypt(credentials["password"].encode()).decode()

    def decrypt_credentials(self):
        f = Fernet(self.key)
        credentials = self.config["linkedin_credentials"]
        try:
            credentials["username"] = f.decrypt(credentials["username"].encode()).decode()
            credentials["password"] = f.decrypt(credentials["password"].encode()).decode()
            self.log(f"Decrypted username: {credentials['username']}")  # Log the decrypted username
            self.log(f"Decrypted password: {credentials['password']}")  # Log the decrypted password
        except Exception as e:
            self.log(f"Error decrypting credentials: {e}")

    def create_widgets(self):
        # Log Frame should be initialized first to capture all logs
        self.log_frame = tk.Frame(self.master)
        self.log_frame.grid(row=11, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        self.log_text = tk.Text(self.log_frame, wrap='word', height=10)
        self.log_text.pack(side='left', fill='both', expand=True)
        self.log_scroll = tk.Scrollbar(self.log_frame, orient='vertical', command=self.log_text.yview)
        self.log_scroll.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=self.log_scroll.set)

        tk.Label(self.master, text="Job Site URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.job_site_url_entry = tk.Entry(self.master, width=50)
        self.job_site_url_entry.grid(row=0, column=1, padx=5, pady=5)
        self.job_site_url_entry.insert(0, self.config.get('job_site_url', ''))
        self.job_site_url_entry.bind("<FocusOut>", self.update_keywords_event)
        self.job_site_url_entry.bind("<KeyRelease>", self.auto_save_config)

        tk.Label(self.master, text="Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(self.master, width=50)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_entry.insert(0, self.config['personal_info'].get('name', ''))
        self.name_entry.bind("<KeyRelease>", self.auto_save_config)

        tk.Label(self.master, text="Email:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.email_entry = tk.Entry(self.master, width=50)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        self.email_entry.insert(0, self.config['personal_info'].get('email', ''))
        self.email_entry.bind("<KeyRelease>", self.auto_save_config)

        tk.Label(self.master, text="Resume Path:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.resume_path_entry = tk.Entry(self.master, width=50)
        self.resume_path_entry.grid(row=3, column=1, padx=5, pady=5)
        self.resume_path_entry.insert(0, self.config['personal_info'].get('resume_path', ''))
        self.resume_path_entry.bind("<KeyRelease>", self.auto_save_config)
        self.browse_button = tk.Button(self.master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=3, column=2, padx=5, pady=5)

        tk.Label(self.master, text="Google Sheets URL:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.sheets_id_entry = tk.Entry(self.master, width=50)
        self.sheets_id_entry.grid(row=4, column=1, padx=5, pady=5)
        self.sheets_id_entry.insert(0, self.config['google_sheets'].get('spreadsheet_id', ''))
        self.sheets_id_entry.bind("<KeyRelease>", self.auto_save_config)
        self.open_sheets_button = tk.Button(self.master, text="Open Sheets", command=self.open_sheets)
        self.open_sheets_button.grid(row=4, column=2, padx=5, pady=5)

        tk.Label(self.master, text="LinkedIn Username:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.linkedin_username_entry = tk.Entry(self.master, width=50)
        self.linkedin_username_entry.grid(row=5, column=1, padx=5, pady=5)
        self.linkedin_username_entry.insert(0, self.config['linkedin_credentials'].get('username', ''))
        self.linkedin_username_entry.bind("<KeyRelease>", self.auto_save_config)

        tk.Label(self.master, text="LinkedIn Password:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.linkedin_password_entry = tk.Entry(self.master, width=50, show='*')
        self.linkedin_password_entry.grid(row=6, column=1, padx=5, pady=5)
        self.linkedin_password_entry.insert(0, self.config['linkedin_credentials'].get('password', ''))
        self.linkedin_password_entry.bind("<KeyRelease>", self.auto_save_config)

        tk.Label(self.master, text="Filters:").grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)

        # Scrollable area for filters
        self.filters_canvas = tk.Canvas(self.master, height=100)
        self.filters_scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.filters_canvas.yview)
        self.filters_frame = tk.Frame(self.filters_canvas)

        self.filters_frame.bind(
            "<Configure>",
            lambda e: self.filters_canvas.configure(
                scrollregion=self.filters_canvas.bbox("all")
            )
        )

        self.filters_canvas.create_window((0, 0), window=self.filters_frame, anchor="nw")
        self.filters_canvas.configure(yscrollcommand=self.filters_scrollbar.set)

        self.filters_canvas.grid(row=8, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        self.filters_scrollbar.grid(row=8, column=2, sticky=tk.N+tk.S)

        self.filters_vars = {}
        self.refresh_filter_checkbuttons()

        self.use_filters_var = tk.BooleanVar(value=True)
        self.use_filters_checkbox = tk.Checkbutton(self.master, text="Use Filters", variable=self.use_filters_var, command=self.auto_save_config)
        self.use_filters_checkbox.grid(row=9, column=0, sticky=tk.W, padx=5, pady=5)

        self.debug_mode_var = tk.BooleanVar(value=self.config.get('debug_mode', False))
        self.debug_checkbox = tk.Checkbutton(self.master, text="Debug Mode", variable=self.debug_mode_var, command=self.auto_save_config)
        self.debug_checkbox.grid(row=9, column=1, sticky=tk.W, padx=5, pady=5)

        self.start_button = tk.Button(self.master, text="Start Applying", command=self.start_applying)
        self.start_button.grid(row=9, column=2, sticky=tk.E, padx=5, pady=5)

        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.grid(row=10, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)

        self.canvas = tk.Canvas(self.canvas_frame, height=200)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.resume_path_entry.delete(0, tk.END)
            self.resume_path_entry.insert(0, filename)
            self.auto_save_config()

    def save_config(self):
        self.config['job_site_url'] = self.job_site_url_entry.get()
        self.config['personal_info']['name'] = self.name_entry.get()
        self.config['personal_info']['email'] = self.email_entry.get()
        self.config['personal_info']['resume_path'] = self.resume_path_entry.get()
        self.config['google_sheets']['spreadsheet_id'] = self.sheets_id_entry.get()

        # Encrypt LinkedIn credentials
        self.encrypt_credentials()

        keywords = [key for key, var in self.filters_vars.items() if var.get()]
        self.config['filters']['keywords'] = keywords
        self.config['debug_mode'] = self.debug_mode_var.get()

        with open('config.json', 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

        self.log("Config saved.")

    def auto_save_config(self, event=None):
        self.save_config()

    def start_applying(self):
        self.save_config()
        use_filters = self.use_filters_var.get()
        if not use_filters:
            self.config['filters']['keywords'] = []
        start_applying(self.scrollable_frame, self.config, self.log_text)

    def update_keywords_event(self, event):
        self.update_keywords()

    def update_keywords(self):
        url = self.job_site_url_entry.get()
        if url:
            self.log(f"Scraping keywords from {url}...")
            keywords = get_keywords_from_url(url)
            if not keywords:
                self.log("Error: No filters found. Please check the URL or try a different one.")
                messagebox.showerror("Error", "No filters found. Please check the URL or try a different one.")
            else:
                # Filter out duplicates and non-words
                unique_keywords = list(set(filter(lambda x: re.match(r'^\w+$', x), keywords)))
                self.config['filters']['keywords'] = unique_keywords
                self.refresh_filter_checkbuttons()
                self.log(f"Filters updated: {', '.join(unique_keywords)}")

    def refresh_filter_checkbuttons(self):
        for widget in self.filters_frame.winfo_children():
            widget.destroy()

        self.filters_vars = {}
        row = 0
        col = 0
        for keyword in self.config['filters']['keywords']:
            var = tk.BooleanVar()
            self.filters_vars[keyword] = var
            tk.Checkbutton(self.filters_frame, text=keyword.capitalize(), variable=var, command=self.auto_save_config).grid(row=row, column=col, sticky=tk.W, padx=5, pady=5)
            col += 1
            if col >= 3:  # Adjust the number of columns as needed
                col = 0
                row += 1

    def open_sheets(self):
        url = self.sheets_id_entry.get()
        if url:
            webbrowser.open(url)
        else:
            messagebox.showerror("Error", "Google Sheets URL is empty.")

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
