# Lumora 🌿 — Premium redesign of Lumora

A multilingual AI wellbeing companion built with Streamlit and Google Gemini.
The other design lives in [lumora-classic](https://github.com/harman-codes49/lumora-classic).

## Run locally

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo 'GEMINI_API_KEY=your-key' > .env
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

Main file: `app.py` · Python 3.11 · add the secret:

```toml
GEMINI_API_KEY = "your-key"
```

## Starter content

A fresh deploy (empty database) is filled with sample conversations, memories,
dates and reflections from `app/database/seed.py`. An existing database is never touched.
Sample photos: Carli Jean, Alejandro Escamilla, Vee O and Christian Joudrey via Unsplash (Unsplash License).
