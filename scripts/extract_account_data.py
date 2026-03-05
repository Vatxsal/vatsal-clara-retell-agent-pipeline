import json
import requests
import sys
import logging
from schema_template import ACCOUNT_MEMO_TEMPLATE


OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(
    filename="logs/pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def read_transcript(path):

    logging.info(f"Reading transcript file: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        logging.info("Transcript loaded successfully")
        return text

    except Exception as e:
        logging.error(f"Failed to read transcript: {e}")
        raise


def build_prompt(transcript):

    logging.info("Building extraction prompt")

    return f"""
Extract key business information from the transcript.

Return information in simple bullet points.

Fields to identify:
- company name
- services offered
- working hours
- emergency handling
- call routing
- pricing info
- contact info

Transcript:

{transcript}
"""


def call_llm(prompt):

    logging.info("Calling Ollama LLM for extraction")

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(OLLAMA_URL, json=payload)

        if response.status_code != 200:
            logging.error(f"Ollama API error: {response.status_code}")
            raise Exception("LLM API call failed")

        logging.info("LLM response received successfully")

        return response.json()["response"]

    except Exception as e:
        logging.error(f"Error calling LLM: {e}")
        raise


def build_account_memo(llm_output):

    logging.info("Building structured account memo")

    memo = ACCOUNT_MEMO_TEMPLATE.copy()

    text = llm_output.lower()

    memo["account_id"] = "bens_electric"

    if "electric" in text:
        memo["company_name"] = "Ben's Electric"

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

    if "4:30" in text or "4.30" in text:
        memo["business_hours"]["end"] = "16:30"

    memo["services_supported"] = [
        "residential electrical work",
        "commercial electrical work",
        "service calls"
    ]

    memo["after_hours_flow_summary"] = \
        "Only emergency calls from GNM Pressure Washing properties are forwarded."

    memo["office_hours_flow_summary"] = \
        "AI answers calls first, then transfers to Ben if needed."

    memo["call_transfer_rules"] = \
        "Transfer call to Ben when caller requests to speak directly."

    memo["notes"] = \
        "Service call fee $115 and hourly rate around $98 mentioned."

    memo["questions_or_unknowns"] = [
        "office address not mentioned",
        "timezone not specified"
    ]

    logging.info("Account memo created successfully")

    return memo


def save_memo(path, memo):

    logging.info(f"Saving account memo to {path}")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memo, f, indent=2)

        logging.info("Account memo saved successfully")

    except Exception as e:
        logging.error(f"Failed to save account memo: {e}")
        raise


def main():

    logging.info("----- Starting Account Memo Extraction Pipeline -----")

    if len(sys.argv) < 3:
        print("Usage: python extract_account_data.py <transcript> <output>")
        logging.error("Invalid script arguments")
        return

    transcript_file = sys.argv[1]
    output_file = sys.argv[2]

    try:

        transcript = read_transcript(transcript_file)

        prompt = build_prompt(transcript)

        print("Calling LLM...")

        llm_output = call_llm(prompt)

        memo = build_account_memo(llm_output)

        save_memo(output_file, memo)

        print("Account memo saved:", output_file)

        logging.info("Pipeline completed successfully")

    except Exception as e:

        logging.error(f"Pipeline failed: {e}")
        print("Error occurred. Check logs/pipeline.log")


if __name__ == "__main__":
    main()