import tkinter as tk
from tkinter import ttk

class PageBase(tk.Frame):
    """Base class for all pages to inherit from."""
    # master = App.main_content_frame, app_controller = App
    def __init__(self, master, app_controller, page_name, default_prefs=None):
        super().__init__(master)
        self.app_controller = app_controller
        self.page_name = page_name
        self.default_prefs = default_prefs if default_prefs is not None else {}

        self.build_ui()

    def build_ui(self):
        """Placeholder for UI building in subclasses."""
        label = ttk.Label(self, text=f"{self.page_name} - UI to be built")
        label.pack(padx=20, pady=20)