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

        # This line tells Tkinter to call the custom quit_app function
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
        file_menu.add_command(label="Save Character", command=self._save_current_character)
        file_menu.add_separator()
        file_menu.add_command(label="Load Character", command=self._load_character_prompt)
        file_menu.add_separator()
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
        # This frame holds the canvas and the scrollbar
        self.style.configure("canvascontainer.TFrame", backgroundcolor="#EFEF13")
        canvas_container = ttk.Frame(root, padding=5, style="canvascontainer.TFrame")
        canvas_container.pack(fill="both", expand=True)
        canvas_container.rowconfigure(0, weight=1)
        canvas_container.columnconfigure(0, weight=1)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(canvas_container)
        scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        # Configure canvas
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # This is the frame that will hold the actual page content.
        # It lives inside the canvas.
        self.main_content_frame = ttk.Frame(self.canvas)
        
        # Place canvas and scrollbar using grid
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Create canvas window to hold the main_content_frame
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.main_content_frame, 
            anchor="nw"
        )
        
        # Bind events for scrolling and resizing
        self.main_content_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        # Use bind_all to catch the mousewheel event anywhere in the app
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

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

    # def switch_user(self, event=None):

    def _save_current_character(self):
        """Calls the save method on the current page if it's a CharacterSheet."""
        # Check if the current page is a CharacterSheet and has a save method
        if isinstance(self.current_page, CharacterSheet) and hasattr(self.current_page, 'save_character'):
            self.current_page.save_character()
        else:
            messagebox.showinfo("Info", "No character sheet is open to save.")

    def _load_character_prompt(self):
        """Shows a dialog to select a character to load."""
        character_list = database.get_character_list()
        if not character_list:
            messagebox.showinfo("Load Character", "There are no saved characters to load.")
            return

        # We need to create a simple dialog window.
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Character")
        dialog.geometry("250x120")
        dialog.resizable(False, False)

        ttk.Label(dialog, text="Select a character:").pack(pady=(10,5))
        
        selected_char = tk.StringVar()
        char_combo = ttk.Combobox(dialog, textvariable=selected_char, values=character_list, state="readonly")
        char_combo.pack(pady=5, padx=10)
        if character_list:
            char_combo.set(character_list[0])

        def on_load():
            # Get the selected name and show the page
            char_name = selected_char.get()
            if char_name:
                # Pass the selected name to the show_page method
                self.show_page(CharacterSheet, character_to_load=char_name)
            dialog.destroy()

        load_button = ttk.Button(dialog, text="Load", command=on_load)
        load_button.pack(pady=10)

    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update the width of the frame inside the canvas to match the canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        # print(f"Widget resized! New width: {event.width}, New height: {event.height}")

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        # Update scroll region to content size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        # The division by 120 is for Windows to normalize scroll speed
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def show_page(self, page_class, **kwargs):
        """Ensures Page to be shown/displayed correctly triggers"""
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None

        if not page_class:
            print("Debug: show_page was called with a None page_class.")
            return

        try:
            # TRY to create the page.
            self.current_page = page_class(self.main_content_frame, self, **kwargs)
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