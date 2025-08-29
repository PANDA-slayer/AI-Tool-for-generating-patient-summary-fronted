
import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # 👈 import this

from dotenv import load_dotenv

# Load .env
load_dotenv()

# Try to use new Google SDK
try:
    from google import genai
    USE_NEW_SDK = True
except ImportError:
    import google.generativeai as genai_old
    USE_NEW_SDK = False

# Flask app
app = Flask(__name__)
CORS(app) 

PROMPT = (
    "You are a clinical documentation assistant. "
    "Summarize this patient discharge report for a layperson in 150–250 words. "
    "Include: (1) primary diagnosis, (2) key treatments/procedures, "
    "(3) current condition, (4) medications at discharge, (5) follow-up plan & red flags."
)

# New SDK summarizer
def summarize_with_new_sdk(pdf_path: str) -> str:
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    uploaded = client.files.upload(file=pdf_path)

    result = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[uploaded, "\n\n", PROMPT],
    )
    return getattr(result, "text", "").strip()


# Old SDK summarizer
def summarize_with_old_sdk(pdf_path: str) -> str:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    genai_old.configure(api_key=api_key)
    uploaded = genai_old.upload_file(pdf_path)

    model = genai_old.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content([uploaded, "\n\n", PROMPT])
    return getattr(resp, "text", "").strip()


@app.route("/summarize", methods=["POST"])
def summarize():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400

    # Save temp file
    pdf_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(pdf_path)

    try:
        if USE_NEW_SDK:
            summary = summarize_with_new_sdk(pdf_path)
        else:
            summary = summarize_with_old_sdk(pdf_path)

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
