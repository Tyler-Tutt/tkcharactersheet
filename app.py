import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# from ttkthemes import ThemedTk # Third-party library that extends ttk
import os
import sys # Access system-specific parameters
import database # database.py file
from database import UserPreferences
from charactersheet import CharacterSheet

# --- Configuration ---
USER_DATA_DIR = "user_data"
DEFAULT_USER = "default_user"
DEFAULT_PAGE = None

# --- Main Application ---
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("TK Character Sheet")

        # --- Set theme globally during app startup ---
        self.style = ttk.Style()
        self.style.theme_use('classic')

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

        self.current_page = None

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

        # Pages Menu
        pages_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pages", menu=pages_menu)
        pages_menu.add_command(label="Character Sheet", command=lambda: self.show_page(CharacterSheet))
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(root, text=f"Current User: {self.current_user}", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Main content area ---
        self.style.configure("maincontentframe.TFrame", background="#f6ff00", borderwidth=3, relief='solid')
        # padding & borderwidth on the *frame widget/style* control the 'padding' & 'border' (Box Model)
        self.main_content_frame = ttk.Frame(root, padding=5, style="maincontentframe.TFrame")
        # padx & pady on the *Geometry Manager* FOR the widget control the 'Margin'
        self.main_content_frame.pack(fill="both", expand=True, padx=3, pady=3)

        # Show's a default Page on startup
        self.show_page(DEFAULT_PAGE)

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

    def show_page(self, page_class):
        """Ensures Page to be shown/displayed correctly triggers"""
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        if not page_class:
            print("Debug: show_page was called with a None page_class.")
            return

        try:
            # TRY to create the page.
            self.current_page = page_class(self.main_content_frame, self)
            self.current_page.pack(fill="both", expand=True)
            self.root.title(f"tkcharactersheet - {self.current_page.page_name}")

            print(f"Debug: Successfully displayed page: {page_class.__name__}")

        except Exception as e:
            # If ANYTHING goes wrong inside the try block, this code will run.
            messagebox.showerror(
                "Page Load Error",
                f"Failed to load the page: {page_class.__name__}\n\n"
                f"Error: {e}"
            )
            print(f"!!! FAILED TO LOAD PAGE: {page_class.__name__} !!!")
            import traceback
            traceback.print_exc() # This prints the full, detailed error message.

# --- Initiate tk loop ---
if __name__ == "__main__":
    database.init_db()

    DEFAULT_PAGE = CharacterSheet

    root = tk.Tk()
    root.state('zoomed')
    app = App(root)
    root.mainloop()