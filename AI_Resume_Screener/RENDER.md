# Deploy to Render (Flask)

## Prerequisites

- A [Render](https://render.com) account (free tier works)
- A [GitHub](https://github.com) account
- Git installed locally

---

## Step 1 — Initialize Git & push to GitHub

```bash
# From the project folder (AI_Resume_Screener/)
git init
git add .
git commit -m "Initial commit: AI Resume Screener"

# Create a repo on GitHub (don't add README/.gitignore), then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

> **Note:** The `.gitignore` already excludes `__pycache__/`, `uploads/`, `.env`, and test files.

---

## Step 2 — Create a Render Web Service

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. **Connect your GitHub repo** — grant access and select the repo you just pushed
4. Fill in the service details:

| Field | Value |
|-------|-------|
| **Name** | `ai-resume-screener` (or your choice) |
| **Region** | Pick closest to you (e.g. `Frankfurt` or `Oregon`) |
| **Branch** | `main` |
| **Runtime** | `Python 3` (auto-detected) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | **Free** (starts at $0/month) |

5. Click **Create Web Service**

---

## Step 3 — Set Environment Variables (optional)

The app works without any env vars (it falls back to `"dev-secret-key"`), but for production:

1. In your Render service dashboard, go to **Environment**
2. Add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | A secure random string (e.g. `openssl rand -hex 32`) |
| `PYTHON_VERSION` | `3.13.3` (optional — `runtime.txt` already sets this) |

---

## Step 4 — Deploy

- Render will automatically build and deploy your service
- First deploy takes ~2–3 minutes
- Once done, your app is live at:

```
https://ai-resume-screener.onrender.com
```

> **Free tier note:** The service spins down after 15 minutes of inactivity. The first request after idle will have a ~30–60 second delay while it wakes up.

---

## Important Notes

### File uploads are ephemeral
On Render's free tier, the filesystem is **ephemeral** — uploaded resume files and the in‑memory candidate list are lost on restart. This is fine for demos and interviews.

### Debug mode is OFF in production
When running under gunicorn (Render/Procfile), `app.run(debug=True)` is **not executed** — it only runs when you do `python app.py` locally.

### Updating after deploy
Push new commits to GitHub → Render auto‑deploys. Or use **Manual Deploy** → **Clear build cache & deploy** in the Render dashboard for a fresh build.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError` | Ensure the package is in `requirements.txt` and the build command is `pip install -r requirements.txt` |
| 500 errors on upload | Check **Render Dashboard → Logs** for the traceback |
| File uploads not working | Make sure `uploads/` dir is created (app does this on startup) |
```
