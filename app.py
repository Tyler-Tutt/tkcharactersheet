import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import sys # Access system-specific parameters
import database # database.py file
from database import UserPreferences
from ttkthemes import ThemedTk

from charactersheet import CharacterSheet

# --- Configuration ---
USER_DATA_DIR = "user_data"
DEFAULT_USER = "default_user"
DEFAULT_TOOL = None

# --- Main Application ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Toolbox")

        self.root.set_theme("black")

        # This line tells Tkinter to call our custom quit_app function
        # whenever the user clicks the 'X' button on the window.
        # This ensures the database connection is always closed cleanly.
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # --- Set up the hotkey binding ---
        # The .bind() method links an event pattern to a callback function.
        # This is bound to the root window, so it works globally.
        self.root.bind('<Control-q>', self.quit_app)
        self.root.bind('<Control-r>', self.restart_app)

        self.current_user = DEFAULT_USER
        self.user_prefs = UserPreferences(self.current_user)

        self.current_tool_frame = None

        # --- Menu ---
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        #file_menu.add_command(label="Switch User", command=self.switch_user)
        #file_menu.add_separator()
        file_menu.add_command(label="Restart (Ctrl+R)", command=self.restart_app)
        file_menu.add_separator()
        file_menu.add_command(label="Exit (Ctrl+Q)", command=self.quit_app)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Character Sheet", command=lambda: self.show_tool(CharacterSheet))
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(root, text=f"Current User: {self.current_user}", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Main content area ---
        # padding & borderwidth on the *frame widget* control the 'padding' & 'border' (Box Model)
        style = ttk.Style()
        style.configure("maincontentframe.TFrame", background="#f6ff00")
        self.main_content_frame = ttk.Frame(root, borderwidth=3, relief="groove", style="maincontentframe.TFrame")
        # padx & pady on the *Geometry Manager for the widget* control the 'Margin'
        self.main_content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Show a default tool or welcome message
        self.show_tool(DEFAULT_TOOL) # Show's a default Tool on startup

    # The 'event=None' allows this method to be called by the keybinding 
    # (which sends an event object) and the menu (which doesn't).
    def quit_app(self, event=None):
        """Callback function to quit the application."""
        self.root.quit()

    def restart_app(self, event=None):
        """Destroys the current window and restarts the python script."""
        # First, cleanly destroy the current Tkinter window
        self.root.destroy()
        # Then, use os.execl to replace the current process with a new one.
        # sys.executable is the path to the current Python interpreter.
        # sys.argv is the list of original command line arguments.
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_tool(self, tool_class):
        if self.current_tool_frame:
            if hasattr(self.current_tool_frame, 'on_hide'):
                self.current_tool_frame.on_hide()
            self.current_tool_frame.destroy()
            self.current_tool_frame = None # Ensure it's cleared

        # Instantiate the new tool, passing the app_controller (self)
        self.current_tool_frame = tool_class(self.main_content_frame, self)
        self.current_tool_frame.pack(fill="both", expand=True)
        if hasattr(self.current_tool_frame, 'on_show'):
            self.current_tool_frame.on_show()
        
        # Update window title or other app-level things based on tool
        self.root.title(f"tkcharactersheet - {self.current_tool_frame.tool_name}")

# --- Initiate tk loop ---
if __name__ == "__main__":
    database.init_db()

    DEFAULT_TOOL = CharacterSheet

    root = ThemedTk()
    app = App(root)
    root.mainloop()