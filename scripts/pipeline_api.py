from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route("/run-demo-pipeline", methods=["POST"])
def run_demo():

    subprocess.run([
        "python",
        "scripts/extract_account_data.py",
        "dataset/demo_calls/bens_electric/transcript_clean.txt",
        "outputs/account_memo.json"
    ])

    subprocess.run([
        "python",
        "scripts/generate_agent_spec.py",
        "outputs/account_memo.json",
        "outputs/accounts/bens_electric/v1/agent_spec.json"
    ])

    return jsonify({"status": "demo pipeline executed"})


@app.route("/run-onboarding-pipeline", methods=["POST"])
def run_onboarding():

    subprocess.run([
        "python",
        "scripts/apply_onboarding_updates.py",
        "outputs/account_memo.json",
        "dataset/onboarding_calls/bens_electric/transcript.txt",
        "outputs/accounts/bens_electric/v2/account_memo.json"
    ])

    subprocess.run([
        "python",
        "scripts/generate_agent_spec.py",
        "outputs/accounts/bens_electric/v2/account_memo.json",
        "outputs/accounts/bens_electric/v2/agent_spec.json"
    ])

    subprocess.run([
        "python",
        "scripts/generate_diff.py",
        "outputs/account_memo.json",
        "outputs/accounts/bens_electric/v2/account_memo.json",
        "outputs/accounts/bens_electric/changes.md"
    ])

    return jsonify({"status": "onboarding pipeline executed"})


if __name__ == "__main__":
    app.run(port=8000)