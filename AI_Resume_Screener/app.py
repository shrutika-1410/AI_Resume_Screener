from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

from flask import Flask, render_template, request

from nlp.parser import extract_text
from nlp.skill_extractor import extract_skills
from nlp.jobs import JOBS
from nlp.database import init_db, insert_candidate, get_all_candidates


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def compute_ats_breakdown(text: str, extracted_skills: list[str]) -> tuple[int, dict]:
    """Compute an ATS score out of 100 with a per-parameter breakdown.

    This is intentionally lightweight (keyword/heuristic based) to keep the app dependency-free.
    """
    t = (text or "").lower()
    skills_set = set(extracted_skills or [])

    # Targets (sum = 100)
    targets = {
        "skills_match": 30,
        "experience": 20,
        "education": 10,
        "projects": 15,
        "ats_formatting": 10,
        "keywords": 10,
        "certifications": 5,
    }

    # Skills match: scale by how many known skills we extracted.
    # Normalize by a fixed upper bound so score stays 0..30.
    skills_known_pool = 20  # heuristic normalization
    skills_match = _clamp(int(round(len(skills_set) / skills_known_pool * targets["skills_match"])), 0, targets["skills_match"])

    # Experience: look for years/tenure and experience-section keywords.
    years = 0
    for m in re.findall(r"(\d+)\+?\s*(?:years|yrs)", t):
        try:
            years = max(years, int(m))
        except ValueError:
            pass
    years = _clamp(years, 0, 10)
    exp_from_years = int(round((years / 10) * targets["experience"]))
    exp_flags = 1 if any(k in t for k in ["experience", "work experience", "professional experience", "employment", "internship"]) else 0
    experience = _clamp(exp_from_years + exp_flags, 0, targets["experience"])

    # Education: detect education/degree markers.
    edu = 0
    if any(k in t for k in ["education", "bachelor", "b.sc", "btech", "b.tech", "master", "m.sc", "m.tech", "phd", "ph.d", "degree"]):
        edu = 1
    education = _clamp(int(round(edu * targets["education"])), 0, targets["education"])

    # Projects: detect projects/portfolio + GitHub.
    proj = 0
    if "project" in t or "projects" in t or "portfolio" in t:
        proj += 1
    if "github" in t or "gitlab" in t:
        proj += 1
    projects = _clamp(int(round((proj / 2) * targets["projects"])), 0, targets["projects"])

    # ATS formatting: since we don't parse layout, do a best-effort heuristic.
    # Reward presence of common resume section headings.
    formatting_hits = 0
    for k in ["skills", "experience", "education", "projects", "certifications", "summary", "objective"]:
        if k in t:
            formatting_hits += 1
    # Map 0..7 hits -> 0..10
    ats_formatting = _clamp(int(round((formatting_hits / 7) * targets["ats_formatting"])), 0, targets["ats_formatting"])

    # Keywords: intersection of extracted skills with job skill keywords pool.
    # Use the JOBS dataset indirectly by looking for skill keywords already present.
    # Here we approximate by rewarding density of skill hits within the text.
    keyword_hits = 0
    for s in skills_set:
        if s and s in t:
            keyword_hits += 1
    keywords = _clamp(int(round((keyword_hits / max(1, len(skills_set))) * targets["keywords"])), 0, targets["keywords"])

    # Certifications: look for cert keywords.
    cert_flags = 0
    if any(k in t for k in ["certification", "certifications", "certificate", "aws certified", "azure certification", "gcp certification", "cisco", "oracle"]):
        cert_flags = 1
    certifications = _clamp(int(round(cert_flags * targets["certifications"])), 0, targets["certifications"])

    ats_breakdown = {
        "skills_match": skills_match,
        "experience": experience,
        "education": education,
        "projects": projects,
        "ats_formatting": ats_formatting,
        "keywords": keywords,
        "certifications": certifications,
        "targets": targets,
    }

    ats_score = sum(
        ats_breakdown[k] for k in [
            "skills_match",
            "experience",
            "education",
            "projects",
            "ats_formatting",
            "keywords",
            "certifications",
        ]
    )
    ats_score = _clamp(int(ats_score), 0, 100)
    return ats_score, ats_breakdown


app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

# Upload folder setup
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc"}

# Create folders when app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
init_db()


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

        # ATS score (0-100) + breakdown for the UI
        ats_score, ats_breakdown = compute_ats_breakdown(text, skills)

        # Keep legacy `score` for backward compatibility (optional UI uses it)
        score = ats_score

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

        insert_candidate(
            name=name,
            email=email,
            skills=", ".join(skills),
            score=score,
            ats_score=ats_score,
            ats_breakdown=ats_breakdown,
            job_recommendations=job_recommendations,
        )

        candidates = get_all_candidates()

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