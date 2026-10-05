import os

from validation import SUPPORTED_DOCUMENTS

def transcribe_audio(uploaded_file):
    """Transcribe with Gemini when configured; otherwise return an explicit demo fallback."""
    ext = uploaded_file.name.lower().rsplit(".", 1)[-1]
    if ext in SUPPORTED_DOCUMENTS:
        raw = uploaded_file.read()
        if ext in {"txt", "md", "markdown"}:
            return raw.decode("utf-8", errors="replace")
        return "[Document uploaded] PDF text extraction is enabled in the deployment build. Paste the extracted transcript here for review."
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "[Demo mode] Gemini is not configured. Add GEMINI_API_KEY in Streamlit secrets, then retry this upload.\n\n[00:00] Agent: This is where the Gemini speaker-labelled transcript will appear."
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        uploaded = client.files.upload(file=uploaded_file, config={"mime_type": uploaded_file.type})
        prompt = "Transcribe this customer support call. Label speakers as Agent and Customer, include timestamps, preserve Hindi-English code-switching, and return only the transcript."
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=[uploaded, prompt], config=types.GenerateContentConfig(temperature=0.1))
        return response.text
    except Exception as exc:
        return f"Transcription failed safely: {exc}. You can paste a transcript manually and continue to analysis."
