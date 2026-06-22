import time
import uuid
import torch
import threading
import queue
from diffusers import StableDiffusionPipeline

model_id = "runwayml/stable-diffusion-v1-5"

print("Loading model...")


# =========================================================
# DEVICE SETUP
# =========================================================
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


device, dtype = pick_device_and_dtype()

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

print(f"Device selected: {device}")
print(f"Precision: {dtype}")
print("Model loaded successfully")


# =========================================================
# MAIN GENERATION ENGINE
# =========================================================
def generate_image(
    prompt,
    controller=None,
    logger=print,
    safety_enabled=True,
    progress_queue=None,
    result_queue=None,
    steps=40
):
    """
    Fully async-safe generation engine:
    - progress → progress_queue
    - result → result_queue
    """

    def worker():
        logger(f"Using device: {device.upper()}\n")
        logger("Starting generation...\n")

        start = time.perf_counter()
        cancelled = {"value": False}

        # reset progress
        if progress_queue:
            progress_queue.put(0)

        # -------------------------
        # PROGRESS CALLBACK (ACCURATE)
        # -------------------------
        def callback(step, timestep, latents):
            if controller and controller.is_cancelled():
                cancelled["value"] = True
                logger("\nCancel requested. Stopping early...\n")
                raise Exception("Generation cancelled")

            # EXACT step sync (no +1 drift)
            if progress_queue:
                progress_queue.put(step + 1)

        try:
            safety_checker = pipe.components.get("safety_checker") if safety_enabled else None

            logger("Safety checker: ENABLED\n" if safety_checker else "Safety checker: DISABLED\n")

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

            filename = f"output_{uuid.uuid4().hex}.png"
            image.save(filename)

            elapsed = time.perf_counter() - start

            logger("\nDone generating image\n")

            # FINAL STEP MUST BE EXACT 40
            if progress_queue:
                progress_queue.put(steps)

            # send result to UI
            if result_queue:
                result_queue.put((filename, elapsed))

        except Exception as e:
            logger(f"\nStopped: {str(e)}\n")

            if result_queue:
                result_queue.put((None, 0))

    # IMPORTANT: fire worker thread here
    t = threading.Thread(target=worker, daemon=True)
    t.start()