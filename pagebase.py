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

    # def save_pref(self, key, value):
    #     """Convenience method to save a preference for this tool."""
    #     self.app_controller.user_prefs.set_preference(self.page_name, key, value)
    #     self.prefs[key] = value # Update local copy

    # def get_pref(self, key, default=None):
    #     """Convenience method to get a preference for this tool."""
    #     # This call is correct because 'key' will be a string.
    #     return self.app_controller.user_prefs.get_preference(self.page_name, key, default)

    # def on_show(self):
    #     """Called when the tool is shown. Override in subclasses if needed."""
    #     # Refresh preferences when shown, in case they were changed by another instance
    #     # or by direct file editing (less common for this app type)
    #     self.prefs = self.app_controller.user_prefs.get_tool_preferences(self.page_name, self.default_prefs)

    # def on_hide(self):
    #     """Called when the tool is hidden. Override in subclasses if needed."""
    #     pass
