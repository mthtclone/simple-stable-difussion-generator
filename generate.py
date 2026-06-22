import time
import uuid
import torch
from diffusers import StableDiffusionPipeline

model_id = "runwayml/stable-diffusion-v1-5"

print("Loading model...")


def pick_device_and_dtype():
    if torch.cuda.is_available():
        device = "cuda"
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU detected: {gpu_name}")

        # Conservative FP16 selection
        # GTX series and some older/laptop GPUs are more unstable in fp16
        if any(x in gpu_name for x in ["GTX", "MX", "1650", "1060"]):
            dtype = torch.float32
            print("Using FP32 (safer for this GPU)")
        else:
            dtype = torch.float16
            print("Using FP16")

        return device, dtype

    if torch.backends.mps.is_available():
        print("Using Apple MPS GPU")
        return "mps", torch.float16

    print("No GPU detected. Using CPU (FP32)")
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


def generate_image(prompt, controller=None, logger=print, safety_enabled=True):
    logger(f"Using device: {device.upper()}\n")
    logger("Starting generation...\n")

    start = time.perf_counter()
    cancelled = {"value": False}
    steps = 40

    def callback(step, timestep, latents):
        if controller and controller.is_cancelled():
            cancelled["value"] = True
            logger("\nCancel requested. Stopping early...\n")
            raise Exception("Generation cancelled")

        logger(f"Step {step + 1}/{steps}\n")

    try:
        if safety_enabled:
            safety_checker = pipe.components.get("safety_checker")
        else:
            safety_checker = None

        if safety_checker is None:
            logger("Safety checker: DISABLED\n")
        else:
            logger("Safety checker: ENABLED\n")

        result = pipe(
            prompt,
            num_inference_steps=steps,
            callback=callback,
            callback_steps=1,
            safety_checker=safety_checker
        )

        image = result.images[0]

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