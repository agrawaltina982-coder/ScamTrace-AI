import json
import time
import streamlit as st
from PIL import Image

from scamguard.agent import investigate
from scamguard.audio_tools import LANGUAGE_MAP, transcribe_audio
from scamguard.ollama_agent import ollama_status

st.set_page_config(
    page_title="ScamTrace AI | Multimodal Scam Investigator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
:root { --accent:#6d5dfc; --dark:#111827; --muted:#6b7280; --card:#ffffff; }
.main { background: #f6f7fb; }
.block-container { max-width: 1400px; padding-top: 1.2rem; }
.hero { padding: 28px 32px; border-radius: 24px; background: linear-gradient(135deg,#111827 0%,#312e81 55%,#6d5dfc 100%); color:white; box-shadow: 0 18px 45px rgba(17,24,39,.16); margin-bottom: 22px; }
.hero h1 { font-size: 42px; margin:0 0 6px 0; letter-spacing:-1px; }
.hero p { font-size: 16px; opacity:.9; margin:0; }
.badge { display:inline-block; padding:5px 11px; border-radius:999px; background:rgba(255,255,255,.15); margin-right:6px; font-size:12px; }
.card { background:white; border:1px solid #e7e9f2; border-radius:18px; padding:18px; box-shadow:0 7px 24px rgba(17,24,39,.05); }
.section-title { font-size: 21px; font-weight: 750; color:#111827; margin: 6px 0 12px; }
.small { color:#6b7280; font-size:13px; }
.metric-card { background:white; border:1px solid #e7e9f2; border-radius:18px; padding:16px 18px; min-height:105px; }
.metric-label { color:#6b7280; font-size:13px; text-transform:uppercase; letter-spacing:.08em; }
.metric-value { font-size:27px; font-weight:800; margin-top:8px; color:#111827; }
.status-ok { color:#047857; font-weight:700; }
.status-bad { color:#b91c1c; font-weight:700; }
.evidence { border-left:4px solid #6d5dfc; background:#f8f7ff; padding:10px 14px; border-radius:10px; margin:8px 0; }
.disclaimer { background:#fff7ed; border:1px solid #fed7aa; padding:12px 14px; border-radius:12px; color:#9a3412; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div><span class="badge">MULTIMODAL AI AGENT</span><span class="badge">LOCAL AI</span><span class="badge">INDIAN LANGUAGES</span></div>
  <h1>🛡️ ScamTrace AI</h1>
  <p>Trace the Evidence. Detect the Scam. Explain the Risk.</p>
  <p style="margin-top:10px;opacity:.78">Analyze suspicious text, URLs, screenshots, and voice messages using evidence fusion, OCR, local speech-to-text, threat intelligence, and an evidence-grounded Ollama explanation layer.</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Investigation Settings")
    enable_reputation = st.checkbox("Threat-intelligence checks", value=False, help="Optional PhishTank/URLhaus lookups. Turn on when internet access and API configuration are available.")
    audio_model = st.selectbox("Audio transcription model", ["base", "small"], index=0, help="base is faster on CPU; small is generally more accurate but slower.")
    st.markdown("---")
    st.markdown("### 🤖 Local AI Status")
    status = ollama_status()
    if status["connected"]:
        st.markdown('<span class="status-ok">● Ollama connected</span>', unsafe_allow_html=True)
        st.caption("Available models: " + (", ".join(status["models"]) if status["models"] else "none detected"))
    else:
        st.markdown('<span class="status-bad">● Ollama unavailable</span>', unsafe_allow_html=True)
        st.caption(status["error"])
    st.markdown("---")
    st.markdown("### 🔐 Privacy")
    st.caption("Audio transcription and LLM explanation are designed to run locally. Uploaded audio is processed temporarily and is not automatically sent to a third-party speech API.")

# ---------- Input tabs ----------
tab_text, tab_url, tab_image, tab_audio = st.tabs(["💬 Message / Chat", "🔗 URL", "🖼️ Screenshot", "🎙️ Audio"])

text_input = ""
url_input = ""
image = None
audio_transcript = ""
audio_metadata = {}

with tab_text:
    st.markdown('<div class="section-title">Suspicious message, email, SMS, or chat</div>', unsafe_allow_html=True)
    text_input = st.text_area("Message content", height=230, placeholder="Paste the suspicious message here. English, Hindi, Marathi, or mixed-language text is supported.")
    st.caption("Tip: include the complete message so the agent can trace urgency, credential requests, money requests, impersonation, and other indicators.")

with tab_url:
    st.markdown('<div class="section-title">Direct URL investigation</div>', unsafe_allow_html=True)
    url_input = st.text_input("Suspicious URL", placeholder="https://example.com/verify")
    st.info("ScamTrace AI analyzes URL structure and suspicious terms without opening the page. Optional reputation checks can be enabled from the sidebar.")

with tab_image:
    st.markdown('<div class="section-title">Screenshot / image evidence</div>', unsafe_allow_html=True)
    uploaded_image = st.file_uploader("Upload a scam screenshot", type=["png", "jpg", "jpeg", "webp"], key="image")
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded evidence", use_container_width=True)
        st.caption("OCR extracts visible text from the screenshot and sends it into the same scam-analysis pipeline.")

with tab_audio:
    st.markdown('<div class="section-title">🎙️ Voice / audio scam analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="small">Upload a voice note or call recording. ScamTrace AI transcribes it locally and analyzes the transcript for scam indicators.</div>', unsafe_allow_html=True)
    audio_language_name = st.selectbox("Audio language", list(LANGUAGE_MAP.keys()), index=0)
    uploaded_audio = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "flac", "ogg", "webm"], key="audio")
    if uploaded_audio:
        st.audio(uploaded_audio)
        if st.button("🎧 Transcribe audio locally", use_container_width=True):
            with st.spinner(f"Transcribing with faster-whisper ({audio_model})... The first run downloads the model."):
                tr = transcribe_audio(
                    uploaded_audio.getvalue(), uploaded_audio.name,
                    language=LANGUAGE_MAP[audio_language_name], model_size=audio_model
                )
            st.session_state["audio_transcription"] = tr

    tr = st.session_state.get("audio_transcription")
    if tr:
        if tr.get("available"):
            detected = tr.get("language") or "unknown"
            st.success(f"Transcription complete • detected language: {detected} • confidence: {tr.get('language_probability', 0):.0%}")
            st.text_area("Transcribed speech", value=tr.get("text", ""), height=180, key="transcript_display")
            audio_transcript = tr.get("text", "")
            audio_metadata = {k: v for k, v in tr.items() if k != "text"}
        else:
            st.error(tr.get("error", "Audio transcription failed."))

# ---------- Analyze ----------
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔎  ANALYZE WITH SCAMTRACE AI", type="primary", use_container_width=True):
    final_text = "\n".join(x for x in [text_input.strip(), url_input.strip()] if x)
    if not final_text and image is None and not audio_transcript:
        st.warning("Please provide at least one input: message, URL, screenshot, or audio transcription.")
        st.stop()

    with st.spinner("Collecting evidence → fusing signals → generating explanation..."):
        result = investigate(
            text=final_text,
            image=image,
            audio_transcript=audio_transcript,
            audio_metadata=audio_metadata,
            enable_reputation=enable_reputation,
        )

    report = result["agent_report"]
    det = result["deterministic"]
    risk = report.get("risk_level", det["risk_level"])
    score = det["risk_score"]

    st.markdown("## 📊 Investigation Result")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="metric-label">Risk level</div><div class="metric-value">{risk}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="metric-label">Heuristic score</div><div class="metric-value">{score}/100</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="metric-label">Scam type</div><div class="metric-value" style="font-size:20px">{report.get("scam_type", "Unknown")}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="metric-label">AI explanation</div><div class="metric-value" style="font-size:20px">{"Connected" if report.get("llm_status") == "connected" else "Evidence fallback"}</div></div>', unsafe_allow_html=True)

    if report.get("llm_status") == "connected":
        st.success(f"🤖 Evidence-grounded explanation generated locally by {report.get('llm_backend', 'Ollama')}")
    else:
        st.warning("⚠️ Ollama explanation was unavailable, so ScamTrace AI generated a deterministic evidence-based explanation. The detection pipeline is still usable.")

    st.markdown("### 🧠 Explanation")
    st.markdown(f'<div class="card">{report.get("summary", "No explanation available.")}</div>', unsafe_allow_html=True)

    st.markdown("### 🔍 Evidence Trace")
    evidence_items = report.get("evidence", [])
    if evidence_items:
        for item in evidence_items:
            st.markdown(f'<div class="evidence"><b>{item.get("source", "Evidence")}</b> · {item.get("severity", "UNKNOWN")}<br>{item.get("finding", "")}</div>', unsafe_allow_html=True)
    else:
        st.info("No structured evidence items were returned by the explanation layer.")

    st.markdown("### ✅ Recommended Actions")
    for action in report.get("recommended_actions", []):
        st.markdown(f"- {action}")

    with st.expander("🎙️ Audio transcription details", expanded=bool(audio_transcript)):
        if audio_transcript:
            st.write(audio_transcript)
            st.json(audio_metadata)
        else:
            st.caption("No audio was used in this investigation.")

    with st.expander("🧪 Full technical evidence", expanded=False):
        st.json(result["evidence"])

    report_json = json.dumps(result, ensure_ascii=False, indent=2)
    st.download_button("⬇️ Download investigation report (JSON)", report_json, "scamtrace_investigation.json", "application/json", use_container_width=True)

st.markdown('<div class="disclaimer">⚠️ Research prototype: ScamTrace AI provides preliminary decision support. It can produce false positives or false negatives. Never share OTPs, passwords, PINs, or payment credentials based on a message request, and independently verify important claims.</div>', unsafe_allow_html=True)
st.caption("ScamTrace AI v1.0 • Evidence-first multimodal research prototype • Text + URL + OCR + Indian-language audio transcription + local LLM explanation")
