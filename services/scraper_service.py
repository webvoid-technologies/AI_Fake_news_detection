import re
from urllib.parse import urlparse

import requests
import trafilatura
from bs4 import BeautifulSoup

from config import MIN_CONTENT_LENGTH, REQUEST_TIMEOUT, SOCIAL_DOMAINS

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Selectors that commonly hold ads/nav/boilerplate
BOILERPLATE_TAGS = ["script", "style", "nav", "footer", "aside", "form", "iframe", "noscript"]


class ScraperError(Exception):
    pass


def validate_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        raise ScraperError("No URL provided.")
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url
    parsed = urlparse(url)
    if not parsed.netloc or "." not in parsed.netloc:
        raise ScraperError(f"'{url}' is not a valid URL.")
    return url


def detect_platform(url: str) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    for domain, name in SOCIAL_DOMAINS.items():
        if host == domain or host.endswith("." + domain):
            return name
    return "News Article"


def _meta(soup: BeautifulSoup, *names) -> str:
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find(
            "meta", attrs={"name": name}
        )
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""


def _fetch_html(url: str) -> str:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        raise ScraperError(f"Could not reach the URL: {exc}")
    if resp.status_code in (401, 403):
        raise ScraperError(
            f"Access denied (HTTP {resp.status_code}). This site may require login "
            "or blocks automated access — common for social media posts."
        )
    if resp.status_code >= 400:
        raise ScraperError(f"The URL returned HTTP {resp.status_code}.")
    return resp.text


def _fallback_extract(url: str, html: str) -> dict:
    """BeautifulSoup-based extraction, then newspaper3k as last resort."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(BOILERPLATE_TAGS):
        tag.decompose()

    text = ""
    for sel in ["article", "main", '[role="main"]', ".post", ".article-body"]:
        node = soup.select_one(sel)
        if node:
            text = node.get_text(" ", strip=True)
            if len(text) >= MIN_CONTENT_LENGTH:
                break
    if len(text) < MIN_CONTENT_LENGTH:
        text = soup.get_text(" ", strip=True)

    if len(text) < MIN_CONTENT_LENGTH:
        try:
            from newspaper import Article

            article = Article(url)
            article.download(input_html=html)
            article.parse()
            if len(article.text or "") > len(text):
                text = article.text
        except Exception:
            pass

    return {
        "headline": _meta(soup, "og:title", "twitter:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else ""),
        "author": _meta(soup, "author", "article:author", "og:site_name"),
        "published_date": _meta(
            soup, "article:published_time", "datePublished", "date", "pubdate"
        ),
        "text": re.sub(r"\s+", " ", text).strip(),
    }


def extract_content(url: str) -> dict:
    """Validate URL, fetch page, and return structured content."""
    url = validate_url(url)
    platform = detect_platform(url)
    html = _fetch_html(url)

    result = None
    extracted = trafilatura.extract(
        html, url=url, include_comments=False, include_tables=False, favor_precision=True
    )
    if extracted and len(extracted) >= MIN_CONTENT_LENGTH:
        meta = trafilatura.extract_metadata(html, default_url=url)
        result = {
            "headline": getattr(meta, "title", "") or "" if meta else "",
            "author": getattr(meta, "author", "") or "" if meta else "",
            "published_date": getattr(meta, "date", "") or "" if meta else "",
            "text": extracted,
        }
    else:
        result = _fallback_extract(url, html)

    if len(result["text"]) < MIN_CONTENT_LENGTH:
        raise ScraperError(
            "Could not extract enough readable text from this page. "
            "Social media posts often require login — try pasting the post text "
            "into a public source, or use a news article URL."
        )

    return {
        "url": url,
        "platform": platform,
        "headline": result["headline"],
        "author": result["author"],
        "published_date": result["published_date"],
        "content": result["text"][:15000],  # keep prompt size sane
    }
