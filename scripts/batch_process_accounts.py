import os
import time
import subprocess
import json

DATASET_DIR = "dataset/demo_calls"
OUTPUT_SUMMARY = "outputs/batch_summary.json"


def process_account(account_id):

    transcript_path = f"{DATASET_DIR}/{account_id}/transcript_clean.txt"

    memo_output = f"outputs/accounts/{account_id}/v1/account_memo.json"

    agent_output = f"outputs/accounts/{account_id}/v1/agent_spec.json"

    os.makedirs(f"outputs/accounts/{account_id}/v1", exist_ok=True)

    try:

        subprocess.run([
            "python",
            "scripts/extract_account_data.py",
            transcript_path,
            memo_output
        ], check=True)

        subprocess.run([
            "python",
            "scripts/generate_agent_spec.py",
            memo_output,
            agent_output
        ], check=True)

        return True

    except Exception as e:

        print(f"Error processing {account_id}:", e)

        return False


def main():

    start_time = time.time()

    accounts = os.listdir(DATASET_DIR)

    success = 0
    failed = 0

    for account in accounts:

        print("Processing account:", account)

        result = process_account(account)

        if result:
            success += 1
        else:
            failed += 1

    end_time = time.time()

    summary = {
        "accounts_processed": len(accounts),
        "successful": success,
        "failed": failed,
        "processing_time_seconds": round(end_time - start_time, 2)
    }

    with open(OUTPUT_SUMMARY, "w") as f:
        json.dump(summary, f, indent=2)

    print("Batch summary saved:", OUTPUT_SUMMARY)


if __name__ == "__main__":
    main()