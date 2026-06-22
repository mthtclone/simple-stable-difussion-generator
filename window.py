import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Generator")
        self.root.geometry("850x750")
        self.root.minsize(True, True)

        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill="x", pady=10)

        self.prompt_entry = tk.Entry(self.top_frame, width=50)
        self.prompt_entry.grid(row=0, column=0, padx=5)

        self.generate_button = tk.Button(self.top_frame, text="Generate")
        self.generate_button.grid(row=0, column=1, padx=5)

        self.cancel_button = tk.Button(self.top_frame, text="Cancel")
        self.cancel_button.grid(row=0, column=2, padx=5)
        self.image_frame = tk.Frame(root, width=600, height=450, bg="black")
        self.image_frame.pack(pady=10)

        self.image_frame.pack_propagate(False)

        self.image_label = tk.Label(self.image_frame, bg="black")
        self.image_label.pack(expand=True)

        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack(pady=5)

        self.safety_var = tk.BooleanVar(value=True)

        self.safety_check = tk.Checkbutton(
            self.top_frame,
            text="Safety Checker",
            variable=self.safety_var
        )
        self.safety_check.grid(row=0, column=3, padx=5)

        self.console = ScrolledText(
            root,
            height=12,
            width=90,
            font=("Consolas", 10)
        )
        self.console.pack(fill="both", expand=True, padx=10, pady=10)

    def write_log(self, text):
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.console.delete("1.0", tk.END)

    def get_prompt(self):
        return self.prompt_entry.get()

    def set_status(self, text):
        self.status_label.config(text=text)

    def set_generate_callback(self, callback):
        self.generate_button.config(command=callback)

    def set_cancel_callback(self, callback):
        self.cancel_button.config(command=callback)

    def is_safety_enabled(self):
        return self.safety_var.get()

    def display_image(self, image_path):
        image = Image.open(image_path)

        # fit image inside fixed box cleanly
        image.thumbnail((600, 450))

        photo = ImageTk.PhotoImage(image)

        self.image_label.config(image=photo)
        self.image_label.image = photo