import json
import os
import time
import uuid
from pathlib import Path

import streamlit as st

from analysis import analyze_transcript
from transcription import transcribe_audio
from validation import SUPPORTED_DOCUMENTS, SUPPORTED_AUDIO, validate_upload


st.set_page_config(page_title="CoCoa · Conversational Coach", page_icon="◌", layout="wide", initial_sidebar_state="expanded")

# Streamlit Cloud exposes secrets through st.secrets; mirror the key into the
# environment so the provider modules stay framework-agnostic and testable.
if "GEMINI_API_KEY" not in os.environ:
    try:
        if st.secrets.get("GEMINI_API_KEY"):
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;1,600&display=swap');
:root { --ink:#18231f; --muted:#6d7972; --cream:#f6f4ed; --paper:#fffdf7; --mint:#d9f4e8; --green:#13795b; --coral:#e77052; --line:#dce4dd; }
.stApp { background: radial-gradient(circle at 78% 8%, #e5f2e4 0, transparent 25%), var(--cream); color:var(--ink); font-family:'Manrope',sans-serif; }
[data-testid="stSidebar"] { background:#19362c; border-right:0; }
[data-testid="stSidebar"] * { color:#eef8f1 !important; }
.brand { font-family:'Playfair Display',serif; font-size:2.25rem; letter-spacing:-.06em; color:#f6f4ed; margin: 1rem 0 0; }
.eyebrow { font:500 .72rem 'DM Mono',monospace; letter-spacing:.16em; text-transform:uppercase; color:var(--green); }
.hero { padding:2.5rem 0 1.5rem; max-width:900px; }
.hero h1 { font-family:'Playfair Display',serif; font-size:clamp(3rem,7vw,6.5rem); line-height:.9; letter-spacing:-.07em; margin:.45rem 0 1.2rem; color:var(--ink); }
.hero h1 em { color:var(--coral); font-weight:600; }
.hero p { max-width:650px; color:var(--muted); font-size:1.1rem; line-height:1.7; }
.signal { display:flex; align-items:center; gap:.6rem; font:500 .72rem 'DM Mono'; color:var(--green); }
.signal i { width:8px; height:8px; border-radius:50%; background:#4ec58a; box-shadow:0 0 0 5px #d9f4e8; }
.card { background:rgba(255,253,247,.78); border:1px solid var(--line); border-radius:22px; padding:1.35rem; box-shadow:0 14px 40px rgba(24,35,31,.05); }
.card h3 { margin:.25rem 0 .35rem; font-size:1.05rem; }
.kicker { color:var(--muted); font-size:.82rem; }
.metric { font:600 2rem 'DM Mono'; color:var(--green); }
.quote { border-left:3px solid var(--coral); padding:.6rem 1rem; margin:.6rem 0; font-family:'Playfair Display',serif; font-size:1.12rem; background:#fff8ef; border-radius:0 10px 10px 0; }
.stButton > button { border-radius:999px; border:1px solid #b7d6c6; background:var(--green); color:white; font-weight:700; padding:.55rem 1.2rem; }
.stButton > button:hover { background:#0d5d46; border-color:#0d5d46; }
.step { display:flex; gap:.65rem; align-items:center; font-size:.8rem; color:#b6d7c6; padding:.55rem 0; }
.step b { display:grid; place-items:center; width:22px; height:22px; border:1px solid #6d9a87; border-radius:50%; font:500 .7rem 'DM Mono'; }
div[data-testid="stFileUploader"] { background:#fffdf7; border:1.5px dashed #9dc8b0; border-radius:18px; padding:.6rem; }
.smallcaps { font:500 .7rem 'DM Mono'; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); }
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {"run_id": None, "status": "Upload received", "transcript": "", "report": None, "file_name": None, "started": None}
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def set_status(value):
    st.session_state.status = value


def sample_transcript():
    return """[00:00] Agent: Hi Maya, thanks for calling BrightCart support. How can I help today?
[00:08] Customer: My order arrived missing the blue kettle, and I need it before Friday.
[00:17] Agent: I’m sorry about that. I can see the rest of the order was delivered yesterday. I’ll ship a replacement today.
[00:28] Customer: Thank you. Will I be charged again?
[00:34] Agent: No, the replacement is free. I’ll email the tracking link as soon as it leaves our warehouse.
[00:43] Customer: Great, that works for me.
[00:47] Agent: Is there anything else I can help with?
[00:51] Customer: No, that’s all. Thanks."""


init_state()

with st.sidebar:
    st.markdown('<div class="brand">CoCoa</div><div style="color:#a6c9b7;font-size:.78rem;margin-bottom:2rem">CONVERSATIONAL COACH</div>', unsafe_allow_html=True)
    st.markdown('<div class="smallcaps" style="color:#a6c9b7">Workflow</div>', unsafe_allow_html=True)
    for n, label in [("01", "Bring in a conversation"), ("02", "Review the transcript"), ("03", "Coach the conversation")]:
        st.markdown(f'<div class="step"><b>{n}</b>{label}</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="smallcaps" style="color:#a6c9b7">Run status</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="signal" style="color:#d9f4e8;margin-top:.6rem"><i></i>{st.session_state.status}</div>', unsafe_allow_html=True)
    st.caption("A private-by-design demo. Use synthetic or permissioned recordings only.")

st.markdown('<div class="hero"><div class="eyebrow">Conversation intelligence, with a human in the loop</div><h1>Turn calls into<br><em>better conversations.</em></h1><p>CoCoa transcribes, listens for the moments that matter, and turns them into practical coaching—with every recommendation grounded in the transcript.</p></div>', unsafe_allow_html=True)

tab_coach, tab_about = st.tabs(["Coach a call", "How it works"])

with tab_coach:
    left, right = st.columns([1.2, .8], gap="large")
    with left:
        st.markdown('<div class="card"><div class="eyebrow">01 · Bring in a conversation</div><h3>Upload a call or transcript</h3><div class="kicker">Audio is transcribed with Gemini. PDF, TXT, and Markdown work as a fast fallback.<br><br>MP3 · WAV · M4A · AAC · OGG · FLAC · WebM · PDF · TXT · MD<br>Maximum 100 MB · Recommended call length about 60 minutes</div></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=sorted(SUPPORTED_AUDIO | SUPPORTED_DOCUMENTS), label_visibility="collapsed")
        c1, c2 = st.columns([1, 1])
        with c1:
            demo = st.button("Use a sample call", use_container_width=True)
        with c2:
            if uploaded:
                st.caption(f"{uploaded.name} · {uploaded.size / 1_000_000:.1f} MB")
        if demo:
            st.session_state.file_name = "sample_missing_kettle.wav"
            st.session_state.transcript = sample_transcript()
            st.session_state.run_id = "demo-" + uuid.uuid4().hex[:8]
            set_status("Transcript ready")
        if uploaded:
            error = validate_upload(uploaded.name, uploaded.size)
            if error:
                st.error(error)
            elif st.button("Transcribe with Gemini", type="primary"):
                st.session_state.run_id = uuid.uuid4().hex[:10]
                st.session_state.file_name = uploaded.name
                set_status("Transcription started")
                with st.spinner("Listening for speakers, timestamps, and intent…"):
                    result = transcribe_audio(uploaded)
                st.session_state.transcript = result
                set_status("Transcript ready")
        if st.session_state.transcript:
            st.markdown('<div class="card" style="margin-top:1rem"><div class="eyebrow">02 · Review before analysis</div><h3>Your transcript</h3><div class="kicker">Make corrections now. The coach will analyze exactly what you approve.</div></div>', unsafe_allow_html=True)
            st.session_state.transcript = st.text_area("Transcript", st.session_state.transcript, height=290, label_visibility="collapsed")
            st.download_button("Download transcript", st.session_state.transcript, file_name="cocoa-transcript.txt")
            if st.button("Analyze this conversation", type="primary"):
                set_status("Analysis started")
                with st.spinner("Finding signals and evidence…"):
                    st.session_state.report = analyze_transcript(st.session_state.transcript)
                set_status("Analysis complete")

    with right:
        st.markdown('<div class="card"><div class="eyebrow">What CoCoa looks for</div><h3>Signal, not surveillance.</h3><p class="kicker">A structured review of the conversation, with evidence attached to every meaningful conclusion.</p></div>', unsafe_allow_html=True)
        cols = st.columns(2)
        turns = len([line for line in st.session_state.transcript.splitlines() if ":" in line])
        words = len(st.session_state.transcript.split())
        for col, value, label in [(cols[0], turns, "speaker turns in this input"), (cols[1], words, "words in this transcript")]:
            with col:
                st.markdown(f'<div class="card"><div class="metric">{value}</div><div class="kicker">{label}</div></div>', unsafe_allow_html=True)
        if st.session_state.report:
            r = st.session_state.report
            st.markdown(f'<div class="card" style="margin-top:1rem"><div class="eyebrow">03 · Coaching report</div><h3>{r["headline"]}</h3><p>{r["summary"]}</p><div class="quote">“{r["evidence"]}”</div></div>', unsafe_allow_html=True)
            if r.get("score") is not None:
                st.metric("Conversation score", f'{r["score"]}/100')
            st.markdown("#### Keep doing")
            for item in r["strengths"]: st.success(item)
            st.markdown("#### Try next time")
            for item in r["coaching"]: st.warning(item)
            with st.expander("View structured output"):
                st.json(r)

with tab_about:
    st.markdown('<div class="hero" style="padding-top:1rem"><div class="eyebrow">A staged, inspectable AI workflow</div><h2 style="font-family:Playfair Display;font-size:3rem;letter-spacing:-.05em">The human stays in the loop.</h2><p>CoCoa separates transcription from analysis so you can correct the source of truth, retry one stage independently, and measure where the system is reliable.</p></div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    for col, num, title, desc in [(a,"01","Transcribe","Gemini identifies speakers and timestamps."),(b,"02","Review","You approve and edit the transcript."),(c,"03","Coach","A validated report cites its evidence.")]:
        with col: st.markdown(f'<div class="card"><div class="metric">{num}</div><h3>{title}</h3><p class="kicker">{desc}</p></div>', unsafe_allow_html=True)
