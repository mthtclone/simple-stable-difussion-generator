import sys
import threading
import tkinter as tk

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TORCHINDUCTOR_DISABLE"] = "1"
os.environ["PYTORCH_DISABLE_NUMPY_COMPAT"] = "1"

import torch
torch.set_grad_enabled(False)

from window import MainWindow
from generate import generate_image
from console_redirect import ConsoleRedirect

class GenerationController:
    def __init__(self):
        self.cancel_flag = False

    def cancel(self):
        self.cancel_flag = True

    def reset(self):
        self.cancel_flag = False

    def is_cancelled(self):
        return self.cancel_flag


controller = GenerationController()
worker_thread = None

root = tk.Tk()
app = MainWindow(root)

def log(text):
    root.after(0, lambda: app.write_log(str(text)))

def set_status(text):
    root.after(0, lambda: app.set_status(text))

def add_log(text):
    root.after(0, lambda: app.write_log(text))

def set_ready():
    root.after(0, lambda: app.set_status("Ready"))

def run_generation(prompt, safety_enabled):
    controller.reset()

    set_status("Generating...")
    add_log(f"Prompt: {prompt}\n")

    def task():
        image_path, elapsed = generate_image(
            prompt,
            controller=controller,
            logger=add_log,
            safety_enabled=safety_enabled
        )

        def update_ui():
            if image_path:
                app.display_image(image_path)
                add_log(f"\nDone in {elapsed:.2f} seconds\n")
                set_status("Ready")
            else:
                add_log("\nGeneration cancelled or failed.\n")
                set_status("Idle")

        root.after(0, update_ui)

    global worker_thread
    worker_thread = threading.Thread(target=task, daemon=True)
    worker_thread.start()


def on_generate():

    prompt = app.get_prompt().strip()

    if not prompt:
        app.set_status("Please enter a prompt")
        return

    app.clear_log()
    app.set_status("Generating...")

    safety_enabled = app.is_safety_enabled()
    run_generation(prompt, safety_enabled)


def on_cancel():
    controller.cancel()
    add_log("\nCancel requested...\n")
    set_status("Cancelling...")

app.set_generate_callback(on_generate)
app.set_cancel_callback(on_cancel)

root.mainloop()