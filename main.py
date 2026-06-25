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

from ttkbootstrap import Style
import ttkbootstrap as tb
from tkinter import ttk

from generate import (
    generate_image,
    load_model_async,
    is_model_loaded
)


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

root = tb.Window(themename="darkly")
app = MainWindow(root)

progress_queue = queue.Queue()
result_queue = queue.Queue()

app.set_progress_queue(progress_queue)

app.set_generate_enabled(False)

def log(text):
    root.after(0, lambda: app.write_log(str(text)))


def set_status(text):
    root.after(0, lambda: app.set_status(text))


def clear_log():
    root.after(0, app.clear_log)


def model_loaded(success):
    if success:
        root.after(0, lambda: app.set_generate_enabled(True))
        root.after(0, lambda: app.set_status("Ready"))
        root.after(
            0,
            lambda: app.write_log(
                "\nStable Diffusion model ready.\n"
            )
        )
    else:
        root.after(0, lambda: app.set_status("Model load failed"))
        root.after(
            0,
            lambda: app.write_log(
                "\nModel failed to load.\n"
            )
        )

def run_generation(prompt, safety_enabled):
    controller.reset()

    app.set_generate_enabled(False)

    set_status("Generating...")
    log(f"Prompt: {prompt}\n")

    app.reset_progress(40)

    generate_image(
        prompt,
        controller=controller,
        logger=log,
        safety_enabled=safety_enabled,
        progress_queue=progress_queue,
        result_queue=result_queue,
        steps=40
    )

def poll_results():
    try:
        while True:
            image_path, elapsed = result_queue.get_nowait()

            if image_path:
                app.display_image(image_path)

                log(
                    f"\nDone in {elapsed:.2f} seconds\n"
                )

                app.set_generate_enabled(True)

                set_status("Ready")

            else:
                log(
                    "\nGeneration cancelled or failed.\n"
                )

                app.set_generate_enabled(True)

                set_status("Idle")

    except queue.Empty:
        pass

    root.after(100, poll_results)

def on_generate():
    if not is_model_loaded():
        app.set_status("Model still loading...")
        return

    prompt = app.get_prompt().strip()

    if not prompt:
        app.set_status("Please enter a prompt")
        return

    clear_log()

    safety_enabled = app.is_safety_enabled()

    run_generation(
        prompt,
        safety_enabled
    )


def on_cancel():
    controller.cancel()

    log("\nCancel requested...\n")

    set_status("Cancelling...")

def on_close():
    controller.cancel()

    try:
        root.destroy()
    finally:
        root.quit()


root.protocol(
    "WM_DELETE_WINDOW",
    on_close
)

app.set_generate_callback(on_generate)
app.set_cancel_callback(on_cancel)

app.set_status("Loading model...")

log("Initializing Stable Diffusion\n")

load_model_async(
    logger=log,
    callback=model_loaded
)

poll_results()

root.mainloop()