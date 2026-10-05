# CoCoa — Conversational Coach

CoCoa turns customer conversations into evidence-backed coaching. Upload a call recording, review the Gemini transcript, and generate a structured conversation-quality report.

## Workflow

`Audio / transcript → validation → Gemini transcription → human review → structured Gemini analysis → coaching dashboard`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

For live Gemini transcription and analysis, add `GEMINI_API_KEY` to `.streamlit/secrets.toml` or the environment. The app remains usable in demo mode without a key.

## Deploy

Push this repository to GitHub, then create a Streamlit Community Cloud app pointing at `app.py`. Add `GEMINI_API_KEY` under App settings → Secrets. Use only synthetic, anonymized, or permissioned recordings in a public deployment.

## Product decisions

- Staged workflow keeps transcription and analysis independently debuggable.
- Transcript editing makes the human the source-of-truth before coaching.
- Structured JSON output makes reports testable and UI-safe.
- The interface shows only counts derived from the current input, such as transcript words and speaker turns. It does not display invented benchmark or baseline numbers.
