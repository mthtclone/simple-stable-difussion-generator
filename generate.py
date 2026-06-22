import time
import uuid
import torch
import threading
from diffusers import StableDiffusionPipeline
from pathlib import Path

IMAGE_DIR = Path("images")
IMAGE_DIR.mkdir(exist_ok=True)

model_id = "runwayml/stable-diffusion-v1-5"

pipe = None
device = None
dtype = None

_model_loaded = False
_model_loading = False


def pick_device_and_dtype():
    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU detected: {gpu_name}")

        if any(x in gpu_name for x in ["GTX", "MX", "1650", "1060"]):
            dtype = torch.float32
        else:
            dtype = torch.float16

        return device, dtype

    if torch.backends.mps.is_available():
        print("Using Apple MPS GPU")
        return "mps", torch.float16

    return "cpu", torch.float32


def is_model_loaded():
    return _model_loaded


def load_model(logger=print):
    global pipe
    global device
    global dtype
    global _model_loaded
    global _model_loading

    if _model_loaded:
        return

    if _model_loading:
        return

    _model_loading = True

    try:
        logger("Detecting hardware \n")

        device, dtype = pick_device_and_dtype()

        logger(f"Loading Stable Diffusion model \n")
        logger(f"Device: {device}\n")

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            requires_safety_checker=False,
            cache_dir="./models"
        )

        pipe = pipe.to(device)

        if device == "cuda":
            try:
                pipe.enable_attention_slicing()
            except Exception:
                pass

        logger("Model loaded successfully.\n")

        _model_loaded = True

    finally:
        _model_loading = False


def load_model_async(logger=print, callback=None):
    def worker():
        try:
            load_model(logger)

            if callback:
                callback(True)

        except Exception as e:
            logger(f"Model load failed: {e}\n")

            if callback:
                callback(False)

    threading.Thread(target=worker, daemon=True).start()


def generate_image(
    prompt,
    controller=None,
    logger=print,
    safety_enabled=True,
    progress_queue=None,
    result_queue=None,
    steps=40
):
    def worker():
        if not is_model_loaded():
            logger("Model not loaded.\n")

            if result_queue:
                result_queue.put((None, 0))

            return

        logger(f"Using device: {device.upper()}\n")
        logger("Starting generation...\n")

        start = time.perf_counter()
        cancelled = {"value": False}

        if progress_queue:
            progress_queue.put(0)

        def callback(step, timestep, latents):
            if controller and controller.is_cancelled():
                cancelled["value"] = True
                logger("\nCancel requested. Stopping early...\n")
                raise Exception("Generation cancelled")

            if progress_queue:
                progress_queue.put(step + 1)

        try:
            safety_checker = (
                pipe.components.get("safety_checker")
                if safety_enabled
                else None
            )

            logger(
                "Safety checker: ENABLED\n"
                if safety_checker
                else "Safety checker: DISABLED\n"
            )

            result = pipe(
                prompt,
                num_inference_steps=steps,
                callback=callback,
                callback_steps=1,
                safety_checker=safety_checker
            )

            image = result.images[0]

            if cancelled["value"]:
                if result_queue:
                    result_queue.put((None, 0))
                return
            
            filename = IMAGE_DIR / f"output_{uuid.uuid4().hex}.png"

            image.save(filename)

            elapsed = time.perf_counter() - start

            logger("\nDone generating image\n")

            if progress_queue:
                progress_queue.put(steps)

            if result_queue:
                result_queue.put((filename, elapsed))

        except Exception as e:
            logger(f"\nStopped: {str(e)}\n")

            if result_queue:
                result_queue.put((None, 0))

    threading.Thread(target=worker, daemon=True).start()