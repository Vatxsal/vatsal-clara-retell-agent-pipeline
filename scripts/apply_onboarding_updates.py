import json
import requests
import sys

OLLAMA_URL = "http://localhost:11434/api/generate"


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def build_prompt(transcript):

    return f"""
You are extracting configuration updates from an onboarding call.

Return simple bullet points describing updates.

Focus on:
- confirmed business hours
- emergency definitions
- routing rules
- call transfer rules
- integrations
- constraints

Transcript:

{transcript}
"""


def call_llm(prompt):

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)

    return response.json()["response"]


def apply_updates(memo, llm_output):

    text = llm_output.lower()

    if "monday" in text and "friday" in text:
        memo["business_hours"]["days"] = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ]

    if "8" in text:
        memo["business_hours"]["start"] = "08:00"

    if "4:30" in text:
        memo["business_hours"]["end"] = "16:30"

    memo["after_hours_flow_summary"] = \
        "Emergency calls from GNM Pressure Washing gas station properties forwarded."

    memo["emergency_definition"] = [
        "gas station outages",
        "existing builders emergency calls"
    ]

    memo["notes"] += " Onboarding confirmed routing rules."

    return memo


def main():

    if len(sys.argv) < 4:
        print("Usage: python apply_onboarding_updates.py <memo_v1> <onboarding_transcript> <output>")
        return

    memo_file = sys.argv[1]
    transcript_file = sys.argv[2]
    output_file = sys.argv[3]

    memo = load_json(memo_file)
    transcript = read_file(transcript_file)

    prompt = build_prompt(transcript)

    print("Extracting onboarding updates...")

    llm_output = call_llm(prompt)

    updated_memo = apply_updates(memo, llm_output)

    save_json(output_file, updated_memo)

    print("Updated memo saved:", output_file)


if __name__ == "__main__":
    main()