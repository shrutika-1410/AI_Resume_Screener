import re


# Lightweight, dependency-free keyword matcher.
SKILL_KEYWORDS = [
    # Languages
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",

    # Frameworks / libraries
    "flask",
    "django",
    "react",
    "node",
    "express",
    "pandas",
    "numpy",
    "scikit-learn",

    # Cloud / DevOps
    "aws",
    "gcp",
    "azure",
    "docker",
    "kubernetes",
    "ci/cd",
    "github actions",

    # General
    "machine learning",
    "deep learning",
    "nlp",
    "computer vision",
    "data analysis",
    "data visualization",
    "etl",
]


def extract_skills(text: str):
    """Return a list of detected skills from resume text."""

    if not text:
        return []

    lowered = text.lower()

    found = []
    # Normalize common variants to improve matching.
    normalized = lowered
    normalized = normalized.replace("csharp", "c#")
    normalized = normalized.replace("c sharp", "c#")
    normalized = normalized.replace("python3", "python")
    normalized = normalized.replace("java8", "java")

    for kw in SKILL_KEYWORDS:
        # Prefer phrase matching without fragile word-boundaries.
        # This intentionally allows matches like "Python3" -> "python" after normalization.
        if kw in ["machine learning", "deep learning", "data analysis", "github actions", "ci/cd"]:
            pattern = re.escape(kw)
        else:
            pattern = r"(^|[^a-z0-9_\+#])" + re.escape(kw) + r"([^a-z0-9_\+#]|$)"

        if re.search(pattern, normalized):
            found.append(kw)

    # De-duplicate while preserving order.
    deduped = []
    seen = set()
    for s in found:
        if s not in seen:
            deduped.append(s)
            seen.add(s)

    return deduped

