# ScamTrace AI — Multimodal Evidence-Fusion AI Agent

**Tagline:** Trace the Evidence. Detect the Scam. Explain the Risk.

ScamTrace AI is a final-year/research prototype for explainable digital scam analysis. It accepts:

- suspicious text / email / chat
- direct URLs
- screenshots (OCR)
- audio / voice notes in supported Indian languages

The system combines deterministic NLP indicators, URL analysis, optional PhishTank/URLhaus checks, local speech transcription with faster-whisper, and an evidence-grounded local Ollama LLM explanation layer.

## Architecture

```text
Text ───────────────┐
URL ────────────────┤
Screenshot ── OCR ──┤──> Evidence Extraction ──> Evidence Fusion ──> Risk Score
Audio ── Whisper ───┘                                  │
                                                       ↓
                                               Local Ollama / Qwen3
                                                       ↓
                                      Explainable Decision + Actions
```

## 1. Install Python environment

```powershell
cd ScamGuard
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 2. Ollama

Install Ollama separately and make sure `qwen3:4b` is available:

```powershell
ollama list
```

If needed:

```powershell
ollama pull qwen3:4b
```

The application talks to Ollama through `http://localhost:11434` and does not require `ollama run` to be kept open manually.

## 3. Run

```powershell
python -m streamlit run app\streamlit_app.py
```

Open `http://localhost:8501`.

## 4. Audio support

The audio module uses `faster-whisper`, a local multilingual speech-to-text model. The first transcription downloads the selected model.

Supported UI choices include:

- Hindi
- Marathi
- Bengali
- Gujarati
- Tamil
- Telugu
- Kannada
- Malayalam
- Punjabi
- Urdu
- Odia
- Assamese
- English
- Auto detect

Choose **base** for faster CPU transcription or **small** for better accuracy at higher compute cost.

The current audio feature performs **speech-to-text + scam-text analysis**. It does not claim to detect synthetic/deepfake audio. That is a separate research problem requiring an audio anti-spoofing model and dataset.

## 5. Optional threat intelligence

Copy `.env.example` to `.env` if you want to configure optional API credentials:

```text
SCAMGUARD_OLLAMA_URL=http://localhost:11434
SCAMGUARD_OLLAMA_MODEL=qwen3:4b
PHISHTANK_APP_KEY=
URLHAUS_AUTH_KEY=
```

## 6. Windows OCR note

The Python package `pytesseract` is included, but the Tesseract OCR engine must also be installed separately for screenshot OCR.

## 7. Research notes

The heuristic score is an engineering risk indicator, not a calibrated probability. The starter project should not be used to claim production accuracy. For a research paper, evaluate on a sufficiently large licensed multilingual dataset with precision, recall, F1, confusion matrices, and ablations.
