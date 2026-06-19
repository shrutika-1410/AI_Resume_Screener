from flask import Flask, render_template, request
import os

from nlp.parser import extract_text
from nlp.skill_extractor import extract_skills
from nlp.jobs import JOBS

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

candidates = []

@app.route('/')
def home():
    return render_template("upload.html")


@app.route('/upload', methods=['POST'])
def upload():

    name = request.form['name']
    email = request.form['email']

    file = request.files['resume']

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    text = extract_text(filepath)

    skills = extract_skills(text)

    score = len(skills) * 10

    # Job recommendations based on skill overlap
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

    job_recommendations = sorted(job_recommendations, key=lambda x: x["match_pct"], reverse=True)[:3]

    candidates.append({
        "name": name,
        "email": email,
        "skills": ", ".join(skills),
        "score": score,
        "job_recommendations": job_recommendations,
    })

    return render_template(
        "dashboard.html",
        candidates=candidates
    )

if __name__ == "__main__":
    app.run(debug=True)