import os
import json
import tkinter as tk
from config_gui import ConfigGUI  # Import ConfigGUI

if __name__ == '__main__':
    root = tk.Tk()
    app = ConfigGUI(root)
    root.mainloop()
