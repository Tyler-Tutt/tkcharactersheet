import tkinter as tk
from tkinter import ttk

# --- Main Window ---
root = tk.Tk()
root.title("Scrollable Frame with Mouse Wheel")
root.geometry("300x250")

# --- Create a main frame to hold the canvas and scrollbar ---
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=1)

# --- Create a Canvas ---
my_canvas = tk.Canvas(main_frame)
my_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# --- Add a Scrollbar to the Canvas ---
my_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# --- Configure the Canvas ---
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# --- Create ANOTHER Frame INSIDE the Canvas ---
content_frame = ttk.Frame(my_canvas)
my_canvas.create_window((0, 0), window=content_frame, anchor="nw")

# --- Mouse Wheel Scrolling Function ---
def _on_mousewheel(event):
    # For Windows/macOS, event.delta is a value around +/-120
    # For Linux, event.num is 4 (up) or 5 (down)
    if event.num == 4 or event.delta > 0:
        my_canvas.yview_scroll(-1, "units")
    elif event.num == 5 or event.delta < 0:
        my_canvas.yview_scroll(1, "units")

# --- Bind the mouse wheel events ---
# Bind to the canvas itself
my_canvas.bind_all("<MouseWheel>", _on_mousewheel) # Windows/macOS
my_canvas.bind_all("<Button-4>", _on_mousewheel)   # Linux scroll up
my_canvas.bind_all("<Button-5>", _on_mousewheel)   # Linux scroll down


# --- Add Content to the 'content_frame' ---
for i in range(50):
    ttk.Label(content_frame, text=f"My Label Number {i+1}").pack(padx=10, pady=2)


root.mainloop()