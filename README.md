# ScamTrace AI — Multimodal Evidence-Fusion AI Agent

**Tagline:** Trace the Evidence. Detect the Scam. Explain the Risk.

ScamTrace AI is a **final-year/research prototype for explainable digital scam analysis**. It accepts:

- Suspicious text / email / chat
- Direct URLs
- Screenshots (OCR)
- Audio / voice notes in supported Indian languages

The system combines deterministic NLP indicators, URL analysis, optional PhishTank/URLhaus checks, local speech transcription with Faster-Whisper, and an evidence-grounded local Ollama LLM explanation layer.

## Key Features

- 📝 Text-based scam analysis
- 🔗 Suspicious URL analysis
- 🖼️ Screenshot OCR analysis
- 🎙️ Multilingual audio transcription
- 🌐 Indian-language audio support
- 🛡️ Optional PhishTank and URLhaus threat intelligence
- 📊 Evidence fusion and risk scoring
- 🤖 Local Ollama + Qwen3 explanation
- 🔍 Evidence-based scam reasoning
- ⚠️ Recommended safety actions

## Architecture

```text
Text ───────────────┐
URL ────────────────┤
Screenshot ── OCR ──┤──> Evidence Extraction
Audio ── Whisper ────┘             │
                                  ↓
                           Evidence Fusion
                                  │
                                  ↓
                             Risk Score
                                  │
                                  ↓
                         Local Ollama / Qwen3
                                  │
                                  ↓
                    Explainable Decision + Actions

## 1. Install Python Environment

Clone the repository:

git clone https://github.com/agrawaltina982-coder/ScamTrace-AI.git
cd ScamTrace-AI

Create and install the Python environment:

python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

If PowerShell does not allow virtual-environment activation, use:

.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

## 2. Ollama

Install Ollama separately and make sure qwen3:4b is available:

ollama list

If needed:

ollama pull qwen3:4b

The application communicates with http://localhost:11434 and does not require ollama run to be kept open manually.

## 3. Run
python -m streamlit run app\streamlit_app.py

Open http://localhost:8501.

## 4. Audio Support

The audio module uses Faster-Whisper, a local multilingual speech-to-text model. The first transcription downloads the selected model.

Supported languages include:

Hindi
Marathi
Bengali
Gujarati
Tamil
Telugu
Kannada
Malayalam
Punjabi
Urdu
Odia
Assamese
English
Auto Detect

Choose base for faster CPU transcription or small for better accuracy at higher compute cost.

The current audio feature performs speech-to-text + scam-text analysis. It does not claim to detect synthetic/deepfake audio. That is a separate research problem requiring an audio anti-spoofing model and dataset.

## 5. Optional Threat Intelligence

Copy .env.example to .env if you want to configure optional API credentials:

SCAMGUARD_OLLAMA_URL=http://localhost:11434
SCAMGUARD_OLLAMA_MODEL=qwen3:4b
PHISHTANK_APP_KEY=
URLHAUS_AUTH_KEY=

Do not commit .env or API keys to GitHub.

## 6. Windows OCR Note

The Python package pytesseract is included, but the Tesseract OCR engine must also be installed separately for screenshot OCR.

## 7. Research Notes

The heuristic score is an engineering risk indicator, not a calibrated probability.

The project is intended as a research/final-year prototype and should not be used to claim production-level accuracy without proper experimental evaluation.

For a research paper, evaluate the system on a sufficiently large and appropriately licensed dataset using:

Precision
Recall
F1-score
Accuracy
Confusion Matrix
Ablation Studies

Numerical results should only be reported after conducting the corresponding experiments.

## 8. Limitations
Heuristic risk scores are not calibrated probabilities.
OCR accuracy depends on image quality and language.
Speech transcription accuracy depends on language, accent, noise, and audio quality.
Threat-intelligence results depend on external services.
The local LLM may produce imperfect explanations.
The current audio module does not perform deepfake/voice-cloning detection.

## Disclaimer

ScamTrace AI is an academic/research prototype. Its automated risk scores and AI-generated explanations are not definitive cybersecurity verdicts. Users should independently verify suspicious messages, links, and requests before taking action.
