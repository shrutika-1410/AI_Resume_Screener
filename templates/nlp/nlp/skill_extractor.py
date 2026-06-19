skills_db = [
    "python",
    "flask",
    "mysql",
    "nlp",
    "django",
    "html",
    "css",
    "javascript",
    "java"
]

def extract_skills(text):

    text = text.lower()

    found = []

    for skill in skills_db:
        if skill in text:
            found.append(skill)

    return found