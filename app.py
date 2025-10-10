import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# from ttkthemes import ThemedTk # Third-party library that extends ttk
import os
import sys
import database
from views.main_view import MainView
from views.character_sheet import CharacterSheet

class AppController:
    """The main controller for the application."""
    def __init__(self, root):
        self.root = root
        self.current_page = None

        # Sets the theme and creates the main view
        self.style = ttk.Style()
        self.style.theme_use('classic')
        self.view = MainView(root, self)

        # Bindings are controller logic
        #TODO Ensure bindings work with both lowercase & uppercase (for case when capslock is on)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.bind('<Control-q>', self.quit_app)
        self.root.bind('<Control-r>', self.restart_app)
        self.root.bind('<Control-s>', self.save_current_character)
        
        # Bind events for scrolling and resizing to the view's components
        self.view.main_content_frame.bind('<Configure>', self._on_frame_configure)
        self.view.canvas.bind('<Configure>', self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Show the default page
        self.show_page(CharacterSheet)

    def show_page(self, page_class, **kwargs):
        """Creates and displays a page in the main content frame."""
        if self.current_page:
            self.current_page.destroy()
        
        content_frame = self.view.main_content_frame
        
        try:
            self.current_page = page_class(content_frame, self, **kwargs)
            self.current_page.pack(fill="both", expand=True)
            self.root.title(f"tkcharactersheet - {self.current_page.page_name}")
        except Exception as e:
            messagebox.showerror("Page Load Error", f"Failed to load page: {e}")
            import traceback
            traceback.print_exc()

    def show_character_sheet(self):
        """Convenience method for showing the character sheet."""
        self.show_page(CharacterSheet)

    def save_current_character(self, event=None):
        """Calls the save method on the current page if it's a CharacterSheet."""
        if isinstance(self.current_page, CharacterSheet) and hasattr(self.current_page, 'save_character'):
            self.current_page.save_character()
        else:
            messagebox.showinfo("Info", "No character sheet is open to save.")

    def load_character_prompt(self, event=None):
        """Shows a dialog to select a character to load."""
        character_list = database.get_character_list()
        if not character_list:
            messagebox.showinfo("Load Character", "There are no saved characters to load.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load Character")
        dialog.geometry("250x120")
        dialog.resizable(False, False)
        dialog.transient(self.root) # Keep dialog on top of the main window
        dialog.grab_set() # Modal dialog

        ttk.Label(dialog, text="Select a character:").pack(pady=(10,5))
        
        selected_char = tk.StringVar()
        char_picklist = ttk.Combobox(dialog, textvariable=selected_char, values=character_list, state="readonly")
        char_picklist.pack(pady=5, padx=10)
        if character_list:
            char_picklist.set(character_list[0])

        def on_load():
            char_name = selected_char.get()
            if char_name:
                self.show_page(CharacterSheet, character_to_load=char_name)
            dialog.destroy()

        load_button = ttk.Button(dialog, text="Load", command=on_load)
        load_button.pack(pady=10)

    def quit_app(self, event=None):
        """Callback function to quit the application."""
        self.root.quit()

    def restart_app(self, event=None):
        """Destroys the current window and restarts the python script."""
        self.root.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        self.view.canvas.itemconfig(self.view.canvas_window, width=event.width)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame."""
        self.view.canvas.configure(scrollregion=self.view.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.view.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# --- Application Entry Point ---
if __name__ == "__main__":
    database.init_db()
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()