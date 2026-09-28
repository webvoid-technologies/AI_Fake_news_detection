"""Shared helpers for the analysis blueprints."""
from flask import jsonify, request

from services.scraper_service import ScraperError, extract_content
from services.groq_service import GroqServiceError, analyze


def article_from_payload() -> dict:
    """Build the article dict from a JSON payload.

    The client may resend extracted content (to avoid re-scraping) or just
    send a URL, in which case we scrape it here.
    """
    data = request.get_json(silent=True) or {}
    url = data.get("url", "")
    content = (data.get("content") or "").strip()

    if content:
        return {
            "url": url,
            "platform": data.get("platform") or "News Article",
            "headline": data.get("headline") or "",
            "author": data.get("author") or "",
            "published_date": data.get("published_date") or "",
            "content": content[:15000],
        }
    return extract_content(url)


def prompt_kwargs(article: dict) -> dict:
    return {
        "url": article["url"],
        "platform": article["platform"],
        "headline": article["headline"],
        "author": article["author"] or "Unknown",
        "published_date": article["published_date"] or "Unknown",
        "content": article["content"],
    }


def run_module(module: str, prompt_file: str):
    """Shared endpoint logic: get article -> call Groq -> JSON response."""
    try:
        article = article_from_payload()
    except ScraperError as exc:
        return jsonify({"success": False, "module": module, "error": str(exc)}), 400

    try:
        result = analyze(prompt_file, **prompt_kwargs(article))
    except GroqServiceError as exc:
        return jsonify({"success": False, "module": module, "error": str(exc)}), 502

    return jsonify(
        {
            "success": True,
            "module": module,
            "result": result,
            "article": {
                "url": article["url"],
                "platform": article["platform"],
                "headline": article["headline"],
                "author": article["author"],
                "published_date": article["published_date"],
                "content": article["content"][:2000],
            },
        }
    )
