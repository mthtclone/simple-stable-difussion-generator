<div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:12px;">
  <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python Badge">
  <img src="https://img.shields.io/badge/PyTorch-red" alt="PyTorch Badge">
</div>

The Stable Diffusion model will be downloaded automatically during the first run.

- Model: Stable Diffusion v1.5
- Source: runwayml/stable-diffusion-v1-5
- Framework: Hugging Face Diffusers
- Device Support: CPU / CUDA / Apple MPS (auto-detected)
- Precision: float32 (CPU / fallback GPUs) or float16 (supported NVIDIA / MPS)
- Inference Steps: 40
- Output Format: PNG

---

For Window, simply double-click the `run.bat` file and run the program.

On macOS/linux, run this command in the folder to turn the script into executable:

`chmod +x run.sh`

and run the file:

`./run.sh`

Some generated image of the sky:

<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:12px; margin-top:10px;">
  <figure style="margin:0;">
    <img src="/output_27ba9ad73f51402297254bf842d27d80.png" alt="sky 1" style="width:100%; border-radius:8px;">
  </figure>

  <figure style="margin:0;">
    <img src="/output_fa174b3882d54fdea09489675bdfa913.png" alt="sky 2" style="width:100%; border-radius:8px;">
  </figure>

  <figure style="margin:0;">
    <img src="/output_ef5ba789eedf4c77bdcc9144e0495d6e.png" alt="sky 3" style="width:100%; border-radius:8px;">
  </figure>
</div>