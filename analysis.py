import json
import os

def _demo_report(transcript):
    customer_lines = [x for x in transcript.splitlines() if "Customer:" in x]
    return {"headline":"A useful first-pass coaching review","summary":"This demo report is generated locally from the sample transcript. Add a Gemini API key for a live analysis of your own conversation.","score":None,"evidence":customer_lines[1].split("Customer:", 1)[-1].strip() if len(customer_lines) > 1 else "The customer’s goal is visible in the transcript.","strengths":["The conversation contains a clear customer need.","The transcript has explicit agent and customer turns."],"coaching":["Review the transcript and confirm the customer’s desired outcome.","Add a Gemini API key to generate model-based coaching."],"signals":{"intent":"sample conversation","sentiment":"not scored","escalation_risk":"not scored","objection":"not scored"}}

def analyze_transcript(transcript):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _demo_report(transcript)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        schema = {"type":"OBJECT","properties":{"headline":{"type":"STRING"},"summary":{"type":"STRING"},"score":{"type":"INTEGER"},"evidence":{"type":"STRING"},"strengths":{"type":"ARRAY","items":{"type":"STRING"}},"coaching":{"type":"ARRAY","items":{"type":"STRING"}},"signals":{"type":"OBJECT","properties":{"intent":{"type":"STRING"},"sentiment":{"type":"STRING"},"escalation_risk":{"type":"STRING"},"objection":{"type":"STRING"}}}}}
        prompt = "Analyze this customer call as a supportive coach. Every claim must be grounded in a short quote from the transcript. Return only JSON matching the schema.\n\n" + transcript
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"), contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0.2))
        return json.loads(response.text)
    except Exception:
        return _demo_report(transcript)
