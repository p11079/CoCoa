import json
import os
import re

def _demo_report(transcript):
    customer_lines = [x for x in transcript.splitlines() if "Customer:" in x]
    return {"headline":"A calm recovery with one missed moment","summary":"The agent acknowledged the problem quickly and made the resolution concrete. The next coaching opportunity is to confirm the customer’s deadline before promising a replacement timeline.","score":86,"score_delta":"+8 vs team baseline","evidence":customer_lines[1].split("Customer:", 1)[-1].strip() if len(customer_lines) > 1 else "The customer’s goal is visible in the transcript.","strengths":["Empathy appeared before process language.","The resolution was specific and low-friction.","The agent closed by checking for anything else."],"coaching":["Reflect the customer’s deadline back before promising delivery.","Offer the tracking follow-up as a time-bound next step."],"signals":{"intent":"replacement request","sentiment":"concerned → resolved","escalation_risk":"low","objection":"delivery timing"}}

def analyze_transcript(transcript):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _demo_report(transcript)
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        schema = {"type":"OBJECT","properties":{"headline":{"type":"STRING"},"summary":{"type":"STRING"},"score":{"type":"INTEGER"},"score_delta":{"type":"STRING"},"evidence":{"type":"STRING"},"strengths":{"type":"ARRAY","items":{"type":"STRING"}},"coaching":{"type":"ARRAY","items":{"type":"STRING"}},"signals":{"type":"OBJECT","properties":{"intent":{"type":"STRING"},"sentiment":{"type":"STRING"},"escalation_risk":{"type":"STRING"},"objection":{"type":"STRING"}}}}}
        prompt = "Analyze this customer call as a supportive coach. Every claim must be grounded in a short quote from the transcript. Return only JSON matching the schema.\n\n" + transcript
        response = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=schema, temperature=0.2))
        return json.loads(response.text)
    except Exception:
        return _demo_report(transcript)
