import re
import socket
from urllib.parse import urlparse
import requests
import tldextract
from .config import PHISHTANK_APP_KEY, URLHAUS_AUTH_KEY, USER_AGENT

URL_RE = re.compile(r"(?i)\b(?:https?://|www\.)[^\s<>'\"]+")
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy", "shorturl.at"}
SUSPICIOUS_WORDS = {"verify", "verification", "secure", "security", "login", "signin", "account", "update", "kyc", "otp", "wallet", "payment", "refund", "prize", "reward", "bonus", "urgent", "confirm", "bank"}

def extract_urls(text: str):
    if not text:
        return []
    urls = []
    for m in URL_RE.findall(text):
        u = m.rstrip(".,;:!?)]}")
        if u.startswith("www."):
            u = "http://" + u
        urls.append(u)
    return list(dict.fromkeys(urls))

def url_features(url: str):
    p = urlparse(url if "://" in url else "http://" + url)
    host = (p.hostname or "").lower()
    ext = tldextract.extract(host)
    registered = ext.registered_domain
    full = url.lower()
    features, score = [], 0

    if p.scheme != "https":
        features.append("URL does not use HTTPS"); score += 1
    if len(url) > 100:
        features.append("Unusually long URL"); score += 1
    if "@" in url:
        features.append("URL contains @, which can obscure destination"); score += 2
    if host.replace(".", "").isdigit():
        features.append("URL uses an IP address instead of a normal domain"); score += 2
    if host in SHORTENERS:
        features.append("URL uses a URL-shortening service"); score += 1
    if host.count(".") >= 3:
        features.append("URL contains many subdomain levels"); score += 1

    hits = sorted({w for w in SUSPICIOUS_WORDS if w in full})
    if hits:
        features.append("Suspicious URL terms: " + ", ".join(hits)); score += min(3, len(hits))

    try:
        socket.gethostbyname(host)
        dns_resolves = True
    except Exception:
        dns_resolves = False

    return {
        "url": url, "domain": registered or host, "hostname": host,
        "https": p.scheme == "https", "dns_resolves": dns_resolves,
        "heuristic_score": score, "indicators": features,
    }

def phishtank_lookup(url: str):
    data = {"checked": False, "found": False, "verified": False, "online": False, "target": None, "error": None}
    try:
        payload = {"url": url, "format": "json"}
        if PHISHTANK_APP_KEY:
            payload["app_key"] = PHISHTANK_APP_KEY
        r = requests.post(
            "https://checkurl.phishtank.com/checkurl/",
            data=payload,
            headers={"User-Agent": USER_AGENT},
            timeout=12,
        )
        r.raise_for_status()
        body = r.json()
        result = body.get("results", {})
        data.update({
            "checked": True,
            "found": bool(result.get("in_database")),
            "verified": bool(result.get("verified")),
            "online": bool(result.get("online")),
            "target": result.get("target"),
        })
    except Exception as e:
        data["error"] = str(e)
    return data

def urlhaus_lookup(url: str):
    data = {"checked": False, "found": False, "payload": None, "error": None}
    if not URLHAUS_AUTH_KEY:
        data["error"] = "URLHAUS_AUTH_KEY not configured"
        return data
    try:
        r = requests.post(
            "https://urlhaus-api.abuse.ch/v1/url/",
            data={"url": url},
            headers={"Auth-Key": URLHAUS_AUTH_KEY, "User-Agent": USER_AGENT},
            timeout=12,
        )
        r.raise_for_status()
        body = r.json()
        data["checked"] = True
        data["found"] = body.get("query_status") == "ok"
        data["payload"] = body
    except Exception as e:
        data["error"] = str(e)
    return data
