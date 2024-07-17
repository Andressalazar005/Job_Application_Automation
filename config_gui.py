import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
import webbrowser  # Import webbrowser module for opening URLs
from application_runner import start_applying, get_keywords_from_url

class ConfigGUI:
    def __init__(self, master):
        self.master = master
        master.title("Job Application Bot Configuration")

        # Load existing config if available
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                self.config = json.load(config_file)
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
                "debug_mode": False
            }

        self.create_widgets()
        self.log("Application started.")

        # Scrape keywords on startup if URL is present
        if self.config['job_site_url']:
            self.update_keywords()

    def create_widgets(self):
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

        tk.Label(self.master, text="Filters:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.filters_frame = tk.Frame(self.master)
        self.filters_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)

        self.filters_vars = {}
        self.refresh_filter_checkbuttons()

        self.debug_mode_var = tk.BooleanVar(value=self.config.get('debug_mode', False))
        self.debug_checkbox = tk.Checkbutton(self.master, text="Debug Mode", variable=self.debug_mode_var, command=self.auto_save_config)
        self.debug_checkbox.grid(row=7, column=0, sticky=tk.W, padx=5, pady=5)

        self.start_button = tk.Button(self.master, text="Start Applying", command=self.start_applying)
        self.start_button.grid(row=7, column=2, sticky=tk.E, padx=5, pady=5)

        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.grid(row=8, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)

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

        # Log Frame
        self.log_frame = tk.Frame(self.master)
        self.log_frame.grid(row=9, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        self.log_text = tk.Text(self.log_frame, wrap='word', height=10)
        self.log_text.pack(side='left', fill='both', expand=True)
        self.log_scroll = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_scroll.pack(side='right', fill='y')
        self.log_text.configure(yscrollcommand=self.log_scroll.set)

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
                self.config['filters']['keywords'] = keywords
                self.refresh_filter_checkbuttons()
                self.log(f"Filters updated: {', '.join(keywords)}")

    def refresh_filter_checkbuttons(self):
        for widget in self.filters_frame.winfo_children():
            widget.destroy()

        self.filters_vars = {}
        col = 0
        for keyword in self.config['filters']['keywords']:
            var = tk.BooleanVar()
            self.filters_vars[keyword] = var
            tk.Checkbutton(self.filters_frame, text=keyword.capitalize(), variable=var, command=self.auto_save_config).grid(row=0, column=col, sticky=tk.W, padx=5, pady=5)
            col += 1

    def log(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)

    def open_sheets(self):
        url = self.sheets_id_entry.get()
        if url:
            webbrowser.open(url)
        else:
            messagebox.showerror("Error", "Google Sheets URL is empty.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
