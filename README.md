# Runware Fashion Demo — Image & Video Inference (Flask)

## Overview
This project is a lightweight demo showcasing **Runware AI’s multimodal generation capabilities** across **text-to-image, image-to-image, text-to-video, and image-to-video**. Runware provides a unified, task-based API for creative workloads, enabling you to submit prompts (and optional seed images), tune parameters (size, FPS, duration, model), and retrieve results via URLs. The app uses a tiny Flask backend and simple W3.CSS templates to demonstrate end-to-end flows: submit a job with the required array payload (authentication + task), then poll asynchronously for the final media. It’s designed for **interested Runware users** to quickly validate capabilities and patterns with minimal setup.

## Motivation
We built this as a **quick, user-friendly onramp** to the Runware API so you can start generating content in minutes—no heavy scaffolding, just clear forms, sensible defaults, and working routes. A **fashion/outfit generator** makes an ideal demo because it’s visually rich, parameterizable (style, palette, silhouette), and maps directly to real product needs for **engineering leadership** across industries:

- **Retail & E-commerce:** Rapid concepting of collections, PDP imagery variants, seasonal refreshes.  
- **Marketing & AdTech:** Creative iteration at scale; audience or channel-specific assets (image/video).  
- **Media & Entertainment:** Pre-viz and social-ready clips from prompts or reference looks.  
- **Gaming & Virtual Worlds:** Fast exploration of character skins, cosmetics, and motion previews.  

The domain highlights how the same API patterns seamlessly cover **T2I, I2I, T2V, and I2V**, making it easy to plug Runware into design pipelines, experimentation frameworks, or production services.

## Tech / Framework Used
- **Python 3.10+**, **Flask**, **requests**
- **W3.CSS** (simple, clean UI)
- **Runware API** (image & video inference + `getResponse` for async status/results)

## Features
- **Text → Image (T2I)**
  - Enter a prompt, choose width/height/model, and generate an image. Returns a direct image URL. (Optional: negative prompt, number of results.)

- **Image → Image (I2I)**
  - Upload a seed image + prompt; control width/height/**strength**/model to guide the transformation. Displays the generated image URL.

- **Text → Video (T2V)**
  - Submit a `videoInference` task with `deliveryMethod: "async"`; configure **duration**, **FPS**, **resolution**, and **model**. The app polls `getResponse` until `status: "success"` and renders the returned `videoURL`.

- **Image → Video (I2V)**
  - Start from a seed/reference image to influence motion and style in the generated clip. Uses the same async submit + poll flow to retrieve a `videoURL`.

- **Configurable Parameters**
  - Resolution (width/height), duration, FPS, number of results, and model (e.g., `bytedance:1@1`).

- **Good Defaults & Errors**
  - Sensible defaults for quick starts, clear status messaging, and helpful error output (including cost display when available).

## Installation

### Prerequisites
- Python 3.10+  
- A Runware API key

### Steps

# 1) Clone
```git clone git@github.com:harrisjasmine/runware_fashion_generator.git```
```cd <your-repo>```

# 2) Create & activate a virtualenv
```python -m venv .venv```
```source .venv/bin/activate  # Windows: .venv\Scripts\activate```

# 3) Install dependencies
```pip install -r requirements.txt```

# 4) Run the app locally
```python app.py```

# 5) Access your app running locally on:
```http://127.0.0.1:5000```
