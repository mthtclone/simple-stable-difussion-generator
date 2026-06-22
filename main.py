import sys
import threading
import tkinter as tk
import queue

import os
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TORCHINDUCTOR_DISABLE"] = "1"
os.environ["PYTORCH_DISABLE_NUMPY_COMPAT"] = "1"

import torch
torch.set_grad_enabled(False)

from window import MainWindow
from generate import generate_image

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

root = tk.Tk()
app = MainWindow(root)

progress_queue = queue.Queue()
result_queue = queue.Queue()

app.set_progress_queue(progress_queue)

def log(text):
    root.after(0, lambda: app.write_log(str(text)))


def set_status(text):
    root.after(0, lambda: app.set_status(text))


def clear_log():
    root.after(0, app.clear_log)

def run_generation(prompt, safety_enabled):
    controller.reset()

    set_status("Generating...")
    log(f"Prompt: {prompt}\n")

    app.reset_progress(40)

    def task():
        generate_image(
            prompt,
            controller=controller,
            logger=log,
            safety_enabled=safety_enabled,
            progress_queue=progress_queue,
            result_queue=result_queue,
            steps=40
        )

    threading.Thread(target=task, daemon=True).start()

def poll_results():
    try:
        while True:
            image_path, elapsed = result_queue.get_nowait()

            if image_path:
                app.display_image(image_path)
                log(f"\nDone in {elapsed:.2f} seconds\n")
                set_status("Ready")
            else:
                log("\nGeneration cancelled or failed.\n")
                set_status("Idle")

    except queue.Empty:
        pass

    root.after(100, poll_results)

def on_generate():
    prompt = app.get_prompt().strip()

    if not prompt:
        app.set_status("Please enter a prompt")
        return

    clear_log()
    set_status("Generating...")

    safety_enabled = app.is_safety_enabled()
    run_generation(prompt, safety_enabled)


def on_cancel():
    controller.cancel()
    log("\nCancel requested...\n")
    set_status("Cancelling...")

app.set_generate_callback(on_generate)
app.set_cancel_callback(on_cancel)

poll_results()

root.mainloop()