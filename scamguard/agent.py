from .text_analyzer import analyze_text
from .url_tools import extract_urls, url_features, phishtank_lookup, urlhaus_lookup
from .ocr_tools import ocr_image
from .ollama_agent import run_local_agent


def _deterministic_risk(text_score, url_results, phish_results, urlhaus_results):
    score = float(text_score)
    for x in url_results:
        score += min(20, x.get("heuristic_score", 0) * 3)
    for x in phish_results:
        if x.get("found") and x.get("verified"):
            score += 45
        elif x.get("found"):
            score += 25
    for x in urlhaus_results:
        if x.get("found"):
            score += 40
    score = int(min(100, round(score)))
    if score >= 80:
        level = "HIGH"
    elif score >= 50:
        level = "MEDIUM"
    elif score >= 20:
        level = "LOW"
    else:
        level = "UNKNOWN"
    return score, level


def investigate(text="", image=None, audio_transcript="", audio_metadata=None, enable_reputation=True):
    text = text or ""
    audio_transcript = audio_transcript or ""
    audio_metadata = audio_metadata or {}

    ocr = {"available": False, "text": "", "error": None}
    if image is not None:
        ocr = ocr_image(image)

    combined_text = "\n".join(x for x in [text, ocr.get("text", ""), audio_transcript] if x)
    text_evidence = analyze_text(combined_text)
    urls = extract_urls(combined_text)
    url_results = [url_features(u) for u in urls]

    phish_results, urlhaus_results = [], []
    if enable_reputation:
        for u in urls[:5]:
            phish_results.append(phishtank_lookup(u))
            urlhaus_results.append(urlhaus_lookup(u))

    deterministic_score, deterministic_level = _deterministic_risk(
        text_evidence["heuristic_score"], url_results, phish_results, urlhaus_results
    )

    evidence = {
        "input_modalities": {
            "text": bool(text.strip()),
            "screenshot": image is not None,
            "audio": bool(audio_transcript.strip()),
            "url": bool(urls),
        },
        "audio": audio_metadata,
        "text_analysis": text_evidence,
        "ocr": {"used": image is not None, "text_extracted": bool(ocr.get("text")), "error": ocr.get("error")},
        "urls": url_results,
        "phishtank": phish_results,
        "urlhaus": urlhaus_results,
        "deterministic_assessment": {"risk_score": deterministic_score, "risk_level": deterministic_level},
    }

    return {
        "scamtrace_version": "1.0.0",
        "deterministic": {"risk_score": deterministic_score, "risk_level": deterministic_level},
        "agent_report": run_local_agent(evidence),
        "evidence": evidence,
    }
