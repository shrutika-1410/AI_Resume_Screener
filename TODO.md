# TODO - ATS Score bifurcation (parameter breakdown)

- [ ] Update `AI_Resume_Screener/app.py` to compute ATS score out of 100 and a per-parameter breakdown (skills/experience/education/projects/ATS formatting/keywords/certifications).

- [x] Persist breakdown in `AI_Resume_Screener/nlp/database.py` (add `ats_breakdown` column + read/write logic).

- [x] Update `AI_Resume_Screener/templates/dashboard.html` to render `ATS SCORE X / 100` and the 7 breakdown rows (✓ label and value/target).

- [ ] Run the app / quick smoke test by rendering a sample candidate from DB (ensure template doesn’t crash for older rows).

