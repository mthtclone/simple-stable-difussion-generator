![Python](https://img.shields.io/badge/python-3.12-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-red)

The Stable Diffusion model will be downloaded automatically during the first run.

- Model: Stable Diffusion v1.5
- Source: runwayml/stable-diffusion-v1-5
- Framework: Hugging Face Diffusers
- Device Support: CPU / CUDA / Apple MPS (auto-detected)
- Precision: float32 (CPU / fallback GPUs) or float16 (supported NVIDIA / MPS)
- Inference Steps: 40
- Output Format: PNG

**Safety checker is disabled for local usage**

---

For Window, simply double-click the `run.bat` file and run the program.

On macOS/linux, run this command in the folder to turn the script into executable:

`chmod +x run.sh`

and run the file:

`./run.sh`

Some generated image of the sky:

![sky 1](/output_27ba9ad73f51402297254bf842d27d80.png)
![sky 2](/output_fa174b3882d54fdea09489675bdfa913.png)
![sky 3](/output_ef5ba789eedf4c77bdcc9144e0495d6e.png)