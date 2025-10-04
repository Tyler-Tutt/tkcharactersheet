import tkinter as tk
from tkinter import ttk

class MainView(ttk.Frame):
    """
    The main user interface shell for the application.
    This class is responsible for building the static UI components like the
    menu, status bar, and the main content area, but it delegates all
    actions and logic to the controller (app.py).
    """
    # master = root, controller = AppController
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master
        self.controller = controller

        self.master.title("TK Character Sheet")
        self.master.state('zoomed') # Maximize the window on start

        self.pack(fill="both", expand=True)

        self._build_widgets()

    def _build_widgets(self):
        # --- Menu ---
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        # Commands are now delegated to the controller
        file_menu.add_command(label="Save Character (Ctrl+S)", command=self.controller.save_current_character)
        file_menu.add_separator()
        file_menu.add_command(label="Load Character", command=self.controller.load_character_prompt)
        file_menu.add_separator()
        file_menu.add_command(label="Restart (Ctrl+R)", command=self.controller.restart_app)
        file_menu.add_separator()
        file_menu.add_command(label="Exit (Ctrl+Q)", command=self.controller.quit_app)

        # Pages Menu
        pages_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pages", menu=pages_menu)
        pages_menu.add_command(label="Character Sheet", command=self.controller.show_character_sheet)
        
        # --- Status Bar ---
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Main content area (Scrollable Canvas) ---
        canvas_container = ttk.Frame(self)
        canvas_container.pack(fill="both", expand=True, padx=5, pady=5)
        canvas_container.rowconfigure(0, weight=1)
        canvas_container.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_container)
        self.scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # This is the frame that will hold the actual page content. It lives inside the canvas.
        self.main_content_frame = ttk.Frame(self.canvas)
        
        # Create canvas window to hold the main_content_frame
        self.canvas_window = self.canvas.create_window(
            (0, 0), 
            window=self.main_content_frame, 
            anchor="nw"
        )
