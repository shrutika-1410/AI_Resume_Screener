# Render deployment (Flask)

## 0) Stop local server
Local dev server (already running in your terminal):
- Stop with **CTRL+C**.

## 1) Ensure correct entrypoint
Your app currently lives at:
- `AI_Resume_Screener/app.py`

Render/Procfile expects the module `app` to be importable:
- Procfile: `web: gunicorn app:app`

Make sure Render’s **working directory** is `AI_Resume_Screener/`.

## 2) Files you should have committed
- `requirements.txt`
- `Procfile`
- `runtime.txt`

## 3) requirements.txt
This repo currently has no database code and (currently) no heavy NLP deps.
- Current `requirements.txt` contains:
  - Flask
  - gunicorn

If you later add MySQL / spacy / pdf/docx parsing, update `requirements.txt` accordingly.

## 4) Procfile
`Procfile`:
```
web: gunicorn app:app
```

## 5) runtime.txt
`runtime.txt`:
```
python-3.12.3
```

## 6) Create Render Web Service
1. Render Dashboard → **New** → **Web Service**
2. Connect GitHub repo
3. Service name: e.g. `ai-resume-screening`
4. Build Command:
   - `pip install -r requirements.txt`
5. Start Command:
   - `gunicorn app:app` (or rely on Procfile)
6. Choose region/runtime
7. Create Web Service

Render will provide URL like:
- `https://your-app-name.onrender.com`

## 7) Environment variables (optional)
If you later add MySQL or a secret key, add them in Render:
- `SECRET_KEY`
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

## 8) Notes about file uploads
This app writes uploads to local `uploads/`.
On Render, that filesystem is ephemeral.
For production, store uploads in S3/R2, or ensure that extracted data is persisted elsewhere.

