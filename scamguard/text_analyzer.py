import re

SCAM_PATTERNS = {
    "urgency": [
        r"\bimmediately\b", r"\burgent\b", r"\bwithin\s+\d+\s*(minutes?|hours?)\b",
        r"\blast\s+warning\b", r"\bact\s+now\b", r"\btoday\b.*\bblocked\b",
        r"\babhi\b", r"\bturant\b", r"\bjaldi\b", r"\bfauran\b", r"\bjaldi\s+se\b",
        r"\bअभी\b", r"\bतुरंत\b", r"\bजल्दी\b", r"\bफौरन\b"
    ],
    "credential_request": [
        r"\botp\b", r"\bpassword\b", r"\bpin\b", r"\bpasscode\b", r"\bcard\s*(number|details)\b",
        r"\baccount\s*(number|details)\b", r"\bkyc\b.*\bverify\b", r"\bupi\s*pin\b",
        r"\bओटीपी\b", r"\bपासवर्ड\b", r"\bपिन\b", r"\bकेवाईसी\b"
    ],
    "financial_request": [
        r"\bpay\b", r"\bpayment\b", r"\btransfer\b", r"\bsend\s+money\b", r"\bupi\b",
        r"\brefund\b", r"\binvest\b", r"\bdeposit\b", r"\bfee\b", r"\bregistration\s+fee\b",
        r"\b₹\s?[\d,]+\b", r"\brs\.?\s?[\d,]+\b", r"\bपैसे\b", r"\bभुगतान\b"
    ],
    "reward_or_prize": [
        r"\bwon\b", r"\bwinner\b", r"\bprize\b", r"\breward\b", r"\blottery\b", r"\bcashback\b", r"\bbonus\b",
        r"\bइनाम\b", r"\bलॉटरी\b", r"\bपुरस्कार\b"
    ],
    "impersonation": [
        r"\bbank\b", r"\bsbi\b", r"\bhdfc\b", r"\bicici\b", r"\baxis\b", r"\bpaytm\b",
        r"\bgovernment\b", r"\bincome\s*tax\b", r"\bcourier\b", r"\bpolice\b", r"\bcustoms\b",
        r"\bhr\b", r"\brecruiter\b", r"\bआरबीआई\b", r"\bबैंक\b"
    ],
    "job_scam": [
        r"\bwork\s+from\s+home\b", r"\bpart[-\s]?time\s+job\b", r"\bjob\s+offer\b",
        r"\bregistration\s+fee\b", r"\btraining\s+fee\b", r"\bघर\s+से\s+काम\b", r"\bनौकरी\b"
    ],
}


def analyze_text(text: str):
    text = text or ""
    lower = text.lower()
    indicators = []
    counts = {}
    for category, patterns in SCAM_PATTERNS.items():
        hits = [p for p in patterns if re.search(p, lower, flags=re.IGNORECASE)]
        if hits:
            counts[category] = len(hits)
            indicators.append(category.replace("_", " ").title())

    url_count = len(re.findall(r"https?://|www\.", lower))
    if url_count:
        indicators.append(f"Contains {url_count} URL(s)")

    score = 0
    score += min(25, counts.get("urgency", 0) * 8)
    score += min(30, counts.get("credential_request", 0) * 12)
    score += min(25, counts.get("financial_request", 0) * 8)
    score += min(15, counts.get("reward_or_prize", 0) * 7)
    score += min(15, counts.get("impersonation", 0) * 5)
    score += min(15, counts.get("job_scam", 0) * 8)

    if counts.get("credential_request") and counts.get("impersonation"):
        category = "Banking/KYC or account phishing"
    elif counts.get("job_scam"):
        category = "Job/recruitment scam"
    elif counts.get("reward_or_prize"):
        category = "Prize/reward scam"
    elif counts.get("financial_request"):
        category = "Payment/financial scam"
    elif counts.get("impersonation"):
        category = "Impersonation scam"
    else:
        category = "General suspicious message"

    return {
        "heuristic_score": min(100, score),
        "categories_detected": list(counts.keys()),
        "indicators": indicators,
        "category_hint": category,
        "matched_pattern_counts": counts,
    }
