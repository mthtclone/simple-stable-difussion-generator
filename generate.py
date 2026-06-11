import time
import torch
from diffusers import StableDiffusionPipeline
import uuid

model_id = "runwayml/stable-diffusion-v1-5"

print("Loading model...")

pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float32,
    cache_dir="./models"
)

pipe = pipe.to("cpu")

print("Model loaded")

def generate_image(prompt, controller=None, logger=print):

    logger("Starting generation...\n")

    start = time.perf_counter()

    cancelled = {"value": False}

    def callback(step, timestep, latents):

        if controller and controller.is_cancelled():
            cancelled["value"] = True
            logger("\nCancel requested. Stopping early...\n")
            raise Exception("Generation cancelled")

        logger(f"Step {step + 1}/20\n")

    try:
        image = pipe(
            prompt,
            num_inference_steps=20,
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