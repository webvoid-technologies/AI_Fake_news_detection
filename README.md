<p align="center">
  <img src="https://www.webvoidtechnologies.com/webvoid_logo_tm.png" alt="Webvoid Technologies" width="200" />
</p>

# AI Fake News Detector

An AI-powered fake news detection POC built for **Webvoid Technologies** — Final Year CSE Project (2026).

Paste a social media post or news article URL and the app extracts the content, summarizes it, extracts factual claims, assesses credibility, flags misinformation indicators, analyzes the source, and suggests fact-check steps — powered by the **Groq API**.

## Tech Stack

- **Backend:** Flask (Blueprints), Jinja2, Requests, BeautifulSoup4, Trafilatura, Newspaper3k, python-dotenv
- **Frontend:** HTML5, Tailwind CSS, Vanilla JS (Fetch API), Lucide icons, marked.js
- **AI:** Groq API (`openai/gpt-oss-120b` by default)

No auth, no database, no Docker — runs fully locally.

## Verdicts

`Likely Credible` · `Likely Misleading` · `Likely False` · `Unverifiable`
The AI never declares claims true/false without supporting evidence in the extracted text.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # add your GROQ_API_KEY (https://console.groq.com)
```

## Run

```bash
python app.py
```

Open <http://localhost:5000>.

## Endpoints

| Method | Path | Body | Purpose |
|---|---|---|---|
| GET | `/` | — | Dashboard |
| POST | `/analyze-url` | `{ "url": str }` | Extract + credibility assessment |
| POST | `/summary` | `{ "url" }` or extracted article | Summary |
| POST | `/claims` | same | Factual claims & entities |
| POST | `/misinformation` | same | Misinformation indicators |
| POST | `/source-analysis` | same | Source credibility |
| POST | `/fact-check` | same | Verification suggestions |

All POST routes accept either `{ "url": "..." }` (server scrapes it) or the `article` object returned by `/analyze-url` (avoids re-scraping). Responses are JSON:
`{ "success": true, "module": "...", "result": "<markdown>", "article": {...} }`.

## Project Structure

```
AI_Fake_news_detection/
├── app.py                  # Flask entrypoint (python app.py → :5000)
├── config.py               # env loading, constants, validation
├── routes/                 # Blueprints: analyze / summary / claims / source
├── services/
│   ├── scraper_service.py  # URL validation + trafilatura/BS4/newspaper3k extraction
│   └── groq_service.py     # Groq client (timeout, retry on 429, model via env)
├── prompts/                # 6 prompt templates → structured Markdown
├── templates/index.html    # Single-page dashboard
├── static/css|js/          # Glassmorphism theme + fetch/render logic
├── requirements.txt
├── .env.example
├── README.md
└── PROJECT_DOC.md
```

## Notes & Limitations

- Social platforms (X, Instagram, Facebook, LinkedIn) often block scrapers or require login; extraction failures produce a clear error message. News article URLs work most reliably.
- This is a POC: the verdict is an AI assessment of the text, not a ground-truth fact check.

## Support

Webvoid Technologies — <studentprogram@webvoidtechnologies.com>
