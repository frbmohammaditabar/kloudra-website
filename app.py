import os
import ssl
import smtplib
import logging
from datetime import datetime, timezone
from email.message import EmailMessage

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {".pdf", ".doc", ".docx"}
MAX_SIZE = 10 * 1024 * 1024  # 10 MB
app.config["MAX_CONTENT_LENGTH"] = MAX_SIZE + (1 * 1024 * 1024)  # small buffer for other fields

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
TO_EMAIL = os.environ.get("TO_EMAIL", SMTP_USER)


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/api/apply", methods=["POST"])
def apply():
    try:
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        role = request.form.get("role", "").strip()
        message = request.form.get("message", "").strip()

        if not (first_name and last_name and email and phone):
            return jsonify({"ok": False, "error": "Please fill in all required fields."}), 400

        resume = request.files.get("resume")
        if not resume or not resume.filename:
            return jsonify({"ok": False, "error": "A resume file is required."}), 400

        ext = os.path.splitext(resume.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            return jsonify({"ok": False, "error": "Resume must be a PDF or Word document."}), 400

        resume_bytes = resume.read()
        if len(resume_bytes) > MAX_SIZE:
            return jsonify({"ok": False, "error": "Resume file is too large (max 10MB)."}), 400

        safe_name = secure_filename(resume.filename)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        stored_name = f"{timestamp}_{safe_name}"
        with open(os.path.join(UPLOAD_DIR, stored_name), "wb") as f:
            f.write(resume_bytes)

        if SMTP_USER and SMTP_PASS:
            msg = EmailMessage()
            msg["Subject"] = f"New job application — {first_name} {last_name}"
            msg["From"] = SMTP_USER
            msg["To"] = TO_EMAIL
            msg.set_content(
                f"Name: {first_name} {last_name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"Role: {role}\n\n"
                f"Message:\n{message or '(none)'}\n"
            )
            subtype = "pdf" if ext == ".pdf" else "vnd.openxmlformats-officedocument.wordprocessingml.document"
            msg.add_attachment(resume_bytes, maintype="application", subtype=subtype, filename=safe_name)

            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            app.logger.warning("SMTP_USER/SMTP_PASS not set — email not sent, file saved only.")

        return jsonify({"ok": True})

    except Exception:
        app.logger.exception("Application submission failed")
        return jsonify({"ok": False, "error": "Server error — please try again or email us directly."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
