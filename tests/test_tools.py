from scamguard.text_analyzer import analyze_text
from scamguard.url_tools import extract_urls, url_features

def test_url_extraction():
    assert extract_urls("Visit https://example.com now.") == ["https://example.com"]

def test_text_flags():
    result = analyze_text("Your KYC will be blocked. Send OTP immediately.")
    assert result["heuristic_score"] > 0
    assert "credential_request" in result["categories_detected"]

def test_url_features():
    result = url_features("http://example.com/verify/login")
    assert result["https"] is False
    assert result["heuristic_score"] > 0
