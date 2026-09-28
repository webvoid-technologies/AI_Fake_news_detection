# PROJECT DOCUMENTATION
## AI Fake News Detector (POC)
**Webvoid Technologies — Final Year CSE Project (2026)**

---

## 1. Abstract

The AI Fake News Detector is a Flask-based web application that accepts a social
media post URL or news article URL, extracts the readable content, and uses a
Large Language Model (via the Groq API) to produce a structured credibility
report: summary, verdict (Likely Credible / Likely Misleading / Likely False /
Unverifiable), confidence, extracted claims, misinformation indicators, source
analysis, and independent fact-check suggestions.

## 2. Objectives

- Automate first-pass credibility triage of online content.
- Surface *checkable* claims and manipulative rhetoric rather than issuing
  unsupported truth judgements.
- Demonstrate a full-stack AI pipeline: scraping → NLP prompting → structured
  reporting.

## 3. System Architecture

```
User URL
   │
   ▼
Flask Routes (routes/*.py — Blueprints)
   │
   ├──► ScraperService — validate URL → requests → trafilatura
   │                     → BeautifulSoup fallback → newspaper3k fallback
   │                     → {headline, author, date, text, platform}
   │
   └──► GroqService — load prompt template → Groq chat API
                      (timeout, 429 retry, JSON errors)
   │
   ▼
JSON {success, module, result(markdown), article}
   │
   ▼
Frontend — Fetch API → marked.js rendering → verdict badge,
           copy / download Markdown report
```

## 4. Module Descriptions

### 4.1 URL Content Extractor (`services/scraper_service.py`)
- URL validation & normalization (auto-prepends https).
- Platform detection: X/Twitter, Instagram, Facebook, LinkedIn, or News Article.
- Extraction chain: trafilatura → BeautifulSoup heuristics → newspaper3k.
- Strips ads/nav/scripts; returns headline, author, published date, text.
- Graceful errors for invalid URLs, HTTP errors, and login-walled content.

### 4.2 Fake News Analyzer (`POST /analyze-url`, `detect_prompt.txt`)
Returns credibility verdict, confidence % with justification, reasoning
quoting the text, and caveats about what cannot be determined.

### 4.3 Claim Extraction (`POST /claims`, `claims_prompt.txt`)
Structured bullets: factual claims, numbers/statistics, people,
organizations, locations, events/dates.

### 4.4 Misinformation Indicators (`POST /misinformation`)
Detects and explains: clickbait, emotional manipulation, fear-based wording,
unsupported claims, missing context, opinion-as-fact, and other indicators.

### 4.5 Fact-Check Suggestions (`POST /fact-check`)
Claims needing verification, reader questions, search keywords (incl.
fact-check sites), missing evidence, additional context. Explicitly avoids
declaring claims true/false.

### 4.6 Source Analysis (`POST /source-analysis`)
Source identification, domain reputation class (Recognized / Unknown /
User-Generated), transparency indicators, limitations, credibility signal.

### 4.7 News Summary (`POST /summary`)
3–5 sentence neutral summary, key topic, takeaways, entities.

## 5. Prompt Engineering

Six dedicated templates in `prompts/` enforce fixed Markdown section headings,
enabling consistent rendering and the verdict-badge regex in the frontend. A
shared system prompt sets an objective fact-checker persona and forbids
unsupported true/false declarations. Temperature 0.2 for consistency.

## 6. API Design

All POST endpoints accept `{ "url": "..." }` **or** a previously extracted
`article` object (the frontend passes the `/analyze-url` result onward, so the
page is scraped only once). Errors return `{ "success": false, "error": "..." }`
with HTTP 400 (input/scraping) or 502 (Groq/network).

## 7. Frontend

- Single-page glassmorphism dashboard, blue/white theme, Lucide icons.
- Sidebar navigation anchors to output cards; collapses to icons on mobile.
- Sequential-then-parallel fetch: `/analyze-url` first (scrapes + verdict),
  then five module calls in parallel.
- Per-card rendering with marked.js + highlight.js; verdict badge coloring.
- Copy analysis, download Markdown report, clear results, error banner.

## 8. Error Handling

| Case | Handling |
|---|---|
| Invalid/missing URL | ScraperError → 400 + UI banner |
| HTTP 401/403 (login wall) | Clear message explaining blocked access |
| Insufficient extracted text | 400 suggesting a news article URL |
| Missing GROQ_API_KEY | 502 + dashboard warning banner |
| Groq timeout/network | 502 with message |
| Groq 429 rate limit | Exponential-backoff retry (2 retries) |
| Frontend fetch failure | Per-module error card; global banner for analyze step |

## 9. Configuration

| Variable | Required | Default |
|---|---|---|
| `GROQ_API_KEY` | Yes | — |
| `GROQ_MODEL` | No | `openai/gpt-oss-120b` |

## 10. Limitations & Future Scope

- Social platforms may block scraping; POC works best with news URLs.
- No claim verification against external sources (by design — suggestions are
  provided instead).
- Future: fact-check API integration (Google Fact Check Tools), text paste
  mode, browser extension, batch analysis, credibility history.

## 11. Conclusion

The POC demonstrates a complete, modular AI-assisted misinformation triage
pipeline — web scraping, LLM prompt engineering, structured reporting and a
polished UI — suitable for final-year demonstration.

---
**Support:** studentprogram@webvoidtechnologies.com
