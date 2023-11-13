import api as ws
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog


# Function to handle file drop event
def drop(event):
    file_path = event.data
    ws.run(file_path)


# Function to handle file selection from file dialog
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if file_path:
        ws.run(file_path)


if __name__ == '__main__':
    # Create the main window
    root = TkinterDnD.Tk()
    root.geometry('800x400')
    root.title("Excel File Upload")

    # Create a Canvas widget for the drag-and-drop area with a background color
    canvas = tk.Canvas(root, bg="lightgray", width=500, height=200)
    canvas.pack(pady=10)

    # Get the canvas background color
    canvas_bg_color = canvas.cget("bg")

    # Create a label with the same background color as the canvas
    label_text = "Drag and drop .xlsx files or browse to upload."
    label = tk.Label(canvas, text=label_text, bg=canvas_bg_color)

    # Place the label at the top-center of the canvas
    label.place(relx=0.5, rely=0, anchor='n')

    # Create a drop target to handle file drops
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', drop)

    # Create a Browse button
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack(pady=10)

    # Run the Tkinter main loop
    root.mainloop()

