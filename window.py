import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import queue

import ttkbootstrap as tb
from tkinter import ttk


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Generator")

        self.root.geometry("1400x900")
        self.minsize_width = 1000
        self.minsize_height = 700
        self.root.minsize(self.minsize_width, self.minsize_height)

        self.top_frame = ttk.Frame(root)
        self.top_frame.pack(fill="x", padx=10, pady=10)

        self.prompt_entry = ttk.Entry(self.top_frame, width=80)
        self.prompt_entry.grid(row=0, column=0, padx=5, sticky="ew")

        self.generate_button = ttk.Button(self.top_frame, text="Generate", width=12)
        self.generate_button.grid(row=0, column=1, padx=5)

        self.cancel_button = ttk.Button(self.top_frame, text="Cancel", width=12)
        self.cancel_button.grid(row=0, column=2, padx=5)

        self.safety_var = tk.BooleanVar(value=True)
        self.safety_check = ttk.Checkbutton(
            self.top_frame,
            text="Safety Checker",
            variable=self.safety_var
        )
        self.safety_check.grid(row=0, column=3, padx=10)

        self.top_frame.columnconfigure(0, weight=1)

        self.content_frame = ttk.Frame(root, padding=10)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.content_frame.columnconfigure(0, weight=3)
        self.content_frame.columnconfigure(1, weight=2)
        self.content_frame.rowconfigure(0, weight=1)

        self.image_frame = ttk.Frame(self.content_frame, bootstyle="secondary", padding=5)
        self.image_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        self.image_frame.columnconfigure(0, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(self.image_frame, text="", anchor="center")
        self.image_label.pack(fill="both", expand=True)

        self.console = ScrolledText(self.content_frame, font=("Consolas", 10))
        self.console.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        self.status_label = ttk.Label(root, text="Ready", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(0, 5))

        self.progress = ttk.Progressbar(
            root,
            orient="horizontal",
            mode="determinate",
            bootstyle="primary-striped"
        )
        self.progress.pack(fill="x", padx=10, pady=(0, 10))

        self.progress_queue = queue.Queue()
        self._poll_progress()

    def set_progress_queue(self, q):
        self.progress_queue = q

    def reset_progress(self, max_steps=40):
        self.progress["value"] = 0
        self.progress["maximum"] = max_steps
        self.progress.update_idletasks()

    def _poll_progress(self):
        try:
            while True:
                value = self.progress_queue.get_nowait()
                self.progress["value"] = value
                self.progress.update_idletasks()
        except queue.Empty:
            pass

        self.root.after(30, self._poll_progress)

    def display_image(self, image_path):
        try:
            image = Image.open(image_path)

            self.image_frame.update_idletasks()

            w = self.image_frame.winfo_width()
            h = self.image_frame.winfo_height()

            if w < 50:
                w = 800
            if h < 50:
                h = 600

            image.thumbnail((w, h))

            photo = ImageTk.PhotoImage(image)

            self.image_label.config(image=photo)
            self.image_label.image = photo

        except Exception as e:
            self.write_log(f"\nImage display error: {e}\n")

    def write_log(self, text):
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.update_idletasks()

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

    def set_generate_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.generate_button.config(state=state)