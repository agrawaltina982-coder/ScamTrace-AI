import json
import requests
from .config import OLLAMA_URL, OLLAMA_MODEL

SYSTEM_PROMPT = r"""
You are ScamTrace AI, an evidence-grounded cybersecurity research assistant.

Your job is to explain a scam-risk assessment using ONLY the structured evidence supplied by the application.
Do not invent facts, do not browse the web, and do not claim that a URL is malicious unless the evidence supports it.
The deterministic risk score is an engineering indicator, not a probability.

Return ONLY valid JSON with this exact schema:
{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL|UNKNOWN",
  "scam_type": "string",
  "summary": "2-5 sentence explanation grounded in the evidence",
  "evidence": [
    {"source": "string", "finding": "string", "severity": "LOW|MEDIUM|HIGH"}
  ],
  "recommended_actions": ["string"],
  "limitations": ["string"]
}

Prefer the deterministic risk level unless the supplied evidence clearly justifies a more cautious interpretation.
For Indian-language or code-mixed inputs, explain the evidence in clear English unless the user language is obvious from the transcript.
"""


def _extract_json(text: str):
    text = (text or "").strip()
    if not text:
        raise ValueError("Ollama returned an empty message.")
    if "```" in text:
        text = text.replace("```json", "").replace("```", "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("Ollama did not return a JSON object.")
    return json.loads(text[start:end + 1])


def ollama_status():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m.get("name", "") for m in r.json().get("models", [])]
        return {"connected": True, "models": models, "error": None}
    except Exception as e:
        return {"connected": False, "models": [], "error": f"{type(e).__name__}: {e}"}


def _fallback_report(evidence: dict, error: Exception):
    det = evidence.get("deterministic_assessment", {})
    score = det.get("risk_score", 0)
    level = det.get("risk_level", "UNKNOWN")
    ta = evidence.get("text_analysis", {})
    category = ta.get("category_hint", "Suspicious digital communication")
    findings = []

    for item in ta.get("indicators", [])[:8]:
        findings.append({"source": "Text analysis", "finding": item, "severity": "HIGH" if level == "HIGH" else "MEDIUM"})
    for u in evidence.get("urls", [])[:5]:
        for item in u.get("indicators", [])[:5]:
            findings.append({"source": "URL analysis", "finding": item, "severity": "HIGH" if u.get("heuristic_score", 0) >= 4 else "MEDIUM"})
    for p in evidence.get("phishtank", []):
        if p.get("found"):
            findings.append({"source": "PhishTank", "finding": "URL appears in the PhishTank database.", "severity": "HIGH"})
    for u in evidence.get("urlhaus", []):
        if u.get("found"):
            findings.append({"source": "URLhaus", "finding": "URL appears in the URLhaus malicious-URL database.", "severity": "HIGH"})

    if level in {"HIGH", "CRITICAL"}:
        summary = f"The evidence indicates a high-risk {category.lower()}. The system detected multiple scam-related signals, producing a heuristic risk score of {score}/100. Treat the communication as suspicious and verify the sender through an independent official channel."
    elif level == "MEDIUM":
        summary = f"The communication contains several suspicious indicators associated with {category.lower()}. The heuristic score is {score}/100, so additional verification is recommended before taking any action."
    elif level == "LOW":
        summary = f"Some suspicious characteristics were detected, but the available evidence is limited. The heuristic score is {score}/100, so the message should be verified before sensitive information is shared."
    else:
        summary = "The available evidence is insufficient to make a confident classification."

    return {
        "risk_level": level,
        "scam_type": category,
        "summary": summary,
        "evidence": findings[:10],
        "recommended_actions": [
            "Do not click or open suspicious links.",
            "Never share OTPs, passwords, PINs, card details, or UPI credentials because a message asks for them.",
            "Verify the request through the organization's official website, app, or a trusted phone number.",
        ],
        "limitations": [f"Local Ollama explanation was unavailable: {type(error).__name__}: {error}", "The heuristic score is not a calibrated probability."],
        "llm_backend": "fallback",
        "llm_status": "error",
    }


def run_local_agent(evidence: dict):
    prompt = "Analyze the following ScamTrace AI evidence and return ONLY the required JSON.\n\n" + json.dumps(evidence, ensure_ascii=False, indent=2)
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "stream": False,
                "think": False,
                "format": "json",
                "keep_alive": "5m",
                "options": {"temperature": 0.1, "num_ctx": 4096},
            },
            timeout=180,
        )
        r.raise_for_status()
        payload = r.json()
        content = payload.get("message", {}).get("content", "")
        result = _extract_json(content)
        result["llm_backend"] = f"Ollama / {OLLAMA_MODEL}"
        result["llm_status"] = "connected"
        return result
    except Exception as e:
        return _fallback_report(evidence, e)
