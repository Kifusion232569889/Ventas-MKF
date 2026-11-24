"""Utilidades comunes de scraping: robots.txt, delays corteses y extracción de contacto."""
import random
import re
import time
import unicodedata
import urllib.robotparser as robotparser
from urllib.parse import urlparse

import requests

USER_AGENT = "Mozilla/5.0 (compatible; MKF-ProspeccionBot/1.0; +https://metodokifusion.com)"
MIN_DELAY, MAX_DELAY = 2.0, 3.0

_robots_cache = {}


def _robots_for(url: str):
    parsed = urlparse(url)
    root = f"{parsed.scheme}://{parsed.netloc}"
    if root not in _robots_cache:
        rp = robotparser.RobotFileParser()
        rp.set_url(root + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None
        _robots_cache[root] = rp
    return _robots_cache[root]


def allowed(url: str) -> bool:
    rp = _robots_for(url)
    if rp is None:
        return True
    try:
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def polite_get(url: str, timeout: int = 20):
    """GET respetando robots.txt y con delay 2-3s. Devuelve el Response o None."""
    if not allowed(url):
        return None
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        if resp.status_code != 200:
            return None
        return resp
    except requests.RequestException:
        return None


PHONE_RE = re.compile(r"(?:\+34[\s.-]?)?\b[679]\d{2}[\s.-]?\d{3}[\s.-]?\d{3}\b")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
WHATSAPP_RE = re.compile(r"wa\.me/(\d+)")

_BAD_EMAIL_SUFFIX = (".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", "example.com", "sentry.io", "wixpress.com")


def extract_contacts(html: str) -> dict:
    phones = {p.strip() for p in PHONE_RE.findall(html)}
    emails = {e for e in EMAIL_RE.findall(html) if not e.lower().endswith(_BAD_EMAIL_SUFFIX)}
    whatsapp = set(WHATSAPP_RE.findall(html))
    return {
        "telefono": sorted(phones)[0] if phones else "",
        "email": sorted(emails)[0] if emails else "",
        "whatsapp": sorted(whatsapp)[0] if whatsapp else "",
    }


INSTAGRAM_RE = re.compile(r"https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.]+")
LINKEDIN_RE = re.compile(r"https?://(?:www\.)?linkedin\.com/(?:in|company)/[A-Za-z0-9_.\-]+")


def extract_social(html: str) -> dict:
    ig = INSTAGRAM_RE.search(html)
    li = LINKEDIN_RE.search(html)
    return {
        "instagram": ig.group(0) if ig else "",
        "linkedin": li.group(0) if li else "",
    }


def normalize(name: str) -> str:
    n = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore").decode()
    return " ".join(n.lower().split())
