import os, base64, uuid, logging, time
from flask import Flask, request, render_template, jsonify, redirect, url_for, flash
import requests
from mimetypes import guess_type

logging.basicConfig(level=logging.INFO)

RUNWARE_API_KEY = "YOUR_AUTH_KEY"
RUNWARE_API_URL = "https://api.runware.ai/v1"
AUTH = {"taskType": "authentication", "apiKey": RUNWARE_API_KEY}
HEADERS = {'Content-Type': 'application/json'}
app = Flask(__name__, template_folder="templates")

def data_uri_from_file(file_storage) -> str:
    file_bytes = file_storage.read()
    file_storage.seek(0)
    mime = file_storage.mimetype or "image/png"
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"

def runware_request(tasks: dict) -> list[dict]:
    """
    Send a request to the Runware API. Returns a dict with keys:
      - ok (bool)
      - status (int or None)
      - data (parsed JSON on success)
      - error / body fields when failure
    """
    payload = [
        AUTH,
        tasks
    ]
    try:
        r = requests.post(RUNWARE_API_URL, json=payload, headers=HEADERS, timeout=60)
        r.raise_for_status()
        return r.json()

        # image_url = data["data"][0]["imageURL"]  # adjust if API shape differs
        # return image_url

    except requests.exceptions.RequestException as e:
        logging.exception(f"Runware API request: {payload} {resp} failed")  # logs stack trace + message to CLI
        return None

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/image_infer", methods=["GET", "POST"])
def image_infer():
    if request.method == "GET":
        
        return render_template("image_infer.html", images=None)

    # image inference form fields with defaults
    task = {
        "taskType": "imageInference",
        "taskUUID": str(uuid.uuid4()),
        "positivePrompt": request.form.get("prompt", "").strip() or "full-body fashion look, editorial, studio lighting, high detail",
        "width": int(request.form.get("width", 768)),
        "height": int(request.form.get("height", 1024)),
        "model": request.form.get("model", "civitai:102438@133677").strip() or "runware:101@1",
        "numberResults": int(request.form.get("numberResults", 1)),
        "outputType": request.form.get("outputType", "URL"),
        "outputFormat": "JPG"
    }

    # check if seed image is provided
    if "seedImage" in request.files and request.files["seedImage"].filename:
        seed_file = request.files["seedImage"]
        task["seedImage"] = data_uri_from_file(seed_file)
        strength = float(request.form.get("strength", "0.6"))
        task["strength"] = strength

    data = runware_request(task)
    image_url = data["data"][0]["imageURL"]

    return render_template("image_infer.html", image=image_url)

class RunwareError(Exception):
    pass

@app.get("/video_infer")
def video():
    return render_template("video_infer.html")

@app.post("/api/video_infer")
def api_video_infer():
    """
    Submit a videoInference task (async). Returns { ok, taskUUID }.
    """

    if request.method == "GET":

        return render_template("video_infer.html", video=None)

    try:
    
        # video inference form fields with defaults
        task = {
            "taskType": "videoInference",
            "taskUUID": str(uuid.uuid4()),
            "deliveryMethod": "async",   # async required for video
            "outputType": "URL",  # videos return a URL
            "outputFormat": "MP4",
            "includeCost": True,
            "positivePrompt": request.form.get("prompt", "").strip() or "full-body fashion look, editorial, studio lighting, high detail",
            "width": int(request.form.get("width") or 864),
            "height": int(request.form.get("height") or 480),
            "model": (request.form.get("model") or "bytedance:1@1").strip() or "bytedance:1@1",
            "duration": int(request.form.get("duration") or 5),
            "fps": int(request.form.get("fps") or 24),
            "numberResults": int(request.form.get("numberResults") or 1),
        }


        data = runware_request(task)

        # Echo pattern: {"data":[{"taskType":"videoInference","taskUUID":"..."}]}
        items = data.get("data", [])
        vi = next(x for x in items if x.get("taskType") == "videoInference")
        returned_uuid = vi["taskUUID"]

        return jsonify({"ok": True, "taskUUID": returned_uuid, "raw": data})

    except (requests.RequestException, ValueError) as e:
        return jsonify({"ok": False, "error": f"Request failed: {e}"}), 502
    except (StopIteration, KeyError) as e:
        return jsonify({"ok": False, "error": "Unexpected response shape", "raw": r.text if 'r' in locals() else None}), 500
    except RunwareError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500

@app.get("/api/status/<task_uuid>")
def api_status(task_uuid: str):
    """
    Poll for results using getResponse. Returns { ok, status, videoURL?, cost?, raw }.
    """
    try:
        payload = [
            {"taskType": "authentication", "apiKey": RUNWARE_API_KEY},
            {"taskType": "getResponse", "taskUUID": task_uuid},
        ]

        r = requests.post(RUNWARE_API_URL, json=payload, headers=HEADERS, timeout=60)
        r.raise_for_status()
        data = r.json()

        # Look for success in data array; errors (if any) will be under 'errors'
        items = data.get("data", [])
        status = "pending"
        video_url = None
        cost = None

        for it in items:
            if it.get("taskType") == "videoInference":
                st = it.get("status")
                if st == "success":
                    status = "success"
                    video_url = it.get("videoURL") or it.get("videoUrl")
                    cost = it.get("cost")
                    break
                elif st in ("pending", "processing"):
                    status = "processing"

        # If there are errors, surface the first one
        errs = data.get("errors") or []
        if errs and status != "success":
            status = errs[0].get("status", "error")

        return jsonify({"ok": True, "status": status, "videoURL": video_url, "cost": cost, "raw": data})

    except (requests.RequestException, ValueError) as e:
        return jsonify({"ok": False, "error": f"Request failed: {e}"}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
