import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os  # Import the os module
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
                    "keywords": []
                },
                "google_sheets": {
                    "spreadsheet_id": ""
                },
                "debug_mode": False
            }

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.master, text="Job Site URL:").grid(row=0, column=0, sticky=tk.W)
        self.job_site_url_entry = tk.Entry(self.master, width=50)
        self.job_site_url_entry.grid(row=0, column=1, columnspan=2)
        self.job_site_url_entry.insert(0, self.config.get('job_site_url', ''))
        self.job_site_url_entry.bind("<FocusOut>", self.update_keywords)

        tk.Label(self.master, text="Name:").grid(row=1, column=0, sticky=tk.W)
        self.name_entry = tk.Entry(self.master, width=50)
        self.name_entry.grid(row=1, column=1, columnspan=2)
        self.name_entry.insert(0, self.config['personal_info'].get('name', ''))

        tk.Label(self.master, text="Email:").grid(row=2, column=0, sticky=tk.W)
        self.email_entry = tk.Entry(self.master, width=50)
        self.email_entry.grid(row=2, column=1, columnspan=2)
        self.email_entry.insert(0, self.config['personal_info'].get('email', ''))

        tk.Label(self.master, text="Resume Path:").grid(row=3, column=0, sticky=tk.W)
        self.resume_path_entry = tk.Entry(self.master, width=50)
        self.resume_path_entry.grid(row=3, column=1)
        self.resume_path_entry.insert(0, self.config['personal_info'].get('resume_path', ''))
        self.browse_button = tk.Button(self.master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=3, column=2)

        tk.Label(self.master, text="Google Sheets ID:").grid(row=4, column=0, sticky=tk.W)
        self.sheets_id_entry = tk.Entry(self.master, width=50)
        self.sheets_id_entry.grid(row=4, column=1, columnspan=2)
        self.sheets_id_entry.insert(0, self.config['google_sheets'].get('spreadsheet_id', ''))

        tk.Label(self.master, text="Filters:").grid(row=5, column=0, sticky=tk.W)
        self.filters_frame = tk.Frame(self.master)
        self.filters_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W)

        self.filters_vars = {}

        self.debug_mode_var = tk.BooleanVar(value=self.config.get('debug_mode', False))
        self.debug_checkbox = tk.Checkbutton(self.master, text="Debug Mode", variable=self.debug_mode_var)
        self.debug_checkbox.grid(row=7, column=0, sticky=tk.W)

        self.start_button = tk.Button(self.master, text="Start Applying", command=self.start_applying)
        self.start_button.grid(row=7, column=2, sticky=tk.E)

        self.canvas_frame = tk.Frame(self.master)
        self.canvas_frame.grid(row=8, column=0, columnspan=3, sticky=tk.W+tk.E)

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

        self.refresh_filter_checkbuttons()

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.resume_path_entry.delete(0, tk.END)
            self.resume_path_entry.insert(0, filename)

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

    def start_applying(self):
        self.save_config()
        start_applying(self.scrollable_frame, self.config)

    def update_keywords(self, event):
        url = self.job_site_url_entry.get()
        if url:
            keywords = get_keywords_from_url(url)
            self.config['filters']['keywords'] = keywords
            self.refresh_filter_checkbuttons()

    def refresh_filter_checkbuttons(self):
        for widget in self.filters_frame.winfo_children():
            widget.destroy()

        self.filters_vars = {}
        col = 0
        for keyword in self.config['filters']['keywords']:
            var = tk.BooleanVar()
            self.filters_vars[keyword] = var
            tk.Checkbutton(self.filters_frame, text=keyword.capitalize(), variable=var).grid(row=0, column=col, sticky=tk.W)
            col += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
