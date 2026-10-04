import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("SCAMGUARD_OLLAMA_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("SCAMGUARD_OLLAMA_MODEL", "qwen3:4b")
PHISHTANK_APP_KEY = os.getenv("PHISHTANK_APP_KEY", "").strip()
URLHAUS_AUTH_KEY = os.getenv("URLHAUS_AUTH_KEY", "").strip()
USER_AGENT = "ScamGuard-Research-Agent/0.1 (student research prototype)"
