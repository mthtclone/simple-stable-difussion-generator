import time
import torch
from diffusers import StableDiffusionPipeline
import uuid

model_id = "runwayml/stable-diffusion-v1-5"

print("Loading model...")

if torch.cuda.is_available():
    device = "cuda"
    dtype = torch.float16
    print(f"GPU detected: {torch.cuda.get_device_name(0)}")
else:
    device = "cpu"
    dtype = torch.float32
    print("No GPU detected. Using CPU.")

pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=dtype,
    cache_dir="./models"
)

pipe = pipe.to(device)

print(f"Model loaded on {device.upper()}")

def generate_image(prompt, controller=None, logger=print):

    logger(f"Using device: {device.upper()}\n")
    logger("Starting generation...\n")

    start = time.perf_counter()

    cancelled = {"value": False}

    def callback(step, timestep, latents):

        if controller and controller.is_cancelled():
            cancelled["value"] = True
            logger("\nCancel requested. Stopping early...\n")
            raise Exception("Generation cancelled")

        logger(f"Step {step + 1}/80\n")

    try:
        image = pipe(
            prompt,
            num_inference_steps=40,
            callback=callback,
            callback_steps=1
        ).images[0]

        if cancelled["value"]:
            return None, 0

        filename = f"output_{uuid.uuid4().hex}.png"

        image.save(filename)

        elapsed = time.perf_counter() - start

        logger("\nDone generating image\n")

        return filename, elapsed

    except Exception as e:
        logger(f"\nStopped: {str(e)}\n")
        return None, 0