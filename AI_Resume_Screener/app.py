from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

from flask import Flask, render_template, request

from nlp.parser import extract_text
from nlp.skill_extractor import extract_skills
from nlp.jobs import JOBS

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc"}

# Create uploads folder when app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

candidates = []


def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    try:
        print("=== Upload route reached ===")

        # Form fields
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name:
            return "Name is required", 400
        if not email:
            return "Email is required", 400

        print("Name:", name)
        print("Email:", email)

        # File upload
        file = request.files.get("resume")

        if not file:
            return "No file uploaded", 400

        filename = file.filename

        if filename == "":
            return "No file selected", 400

        if not allowed_file(filename):
            return (
                f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                400,
            )

        print("Creating uploads folder")
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        print("Saving file to:", filepath)
        file.save(filepath)
        print("File saved successfully")

        # Extract text
        print("Extracting text...")
        text = extract_text(filepath)

        if not text.strip():
            # Clean up the uploaded file if no text was extracted
            try:
                os.remove(filepath)
            except OSError:
                pass
            return "Could not extract any text from the uploaded file. Please try a different format.", 400

        print("Extracting skills...")
        skills = extract_skills(text)

        score = len(skills) * 10

        # Job recommendations
        job_recommendations = []

        resume_skill_set = set(skills)

        for job in JOBS:
            required = job.get("required_skills", [])
            required_set = set(required)

            matched = sorted(required_set.intersection(resume_skill_set))

            match_count = len(matched)
            required_count = len(required_set) if required_set else 1

            match_pct = int(round((match_count / required_count) * 100))

            job_recommendations.append(
                {
                    "title": job.get("title", "Job"),
                    "match_pct": match_pct,
                    "matched_skills": ", ".join(matched),
                    "required_skills": ", ".join(required),
                }
            )

        job_recommendations = sorted(
            job_recommendations,
            key=lambda x: x["match_pct"],
            reverse=True
        )[:3]

        candidates.append(
            {
                "name": name,
                "email": email,
                "skills": ", ".join(skills),
                "score": score,
                "job_recommendations": job_recommendations,
            }
        )

        print("Rendering dashboard")

        return render_template(
            "dashboard.html",
            candidates=candidates
        )

    except Exception as e:
        print("ERROR:", str(e))
        return f"An error occurred: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)