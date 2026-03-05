import json
import sys


def load_memo(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(memo):

    company = memo["company_name"]
    hours = memo["business_hours"]
    services = memo["services_supported"]
    after_hours = memo["after_hours_flow_summary"]

    system_prompt = f"""
You are an AI receptionist for {company}.

Your job is to answer incoming customer calls, understand the purpose of the call,
and route or transfer appropriately.

Business hours:
{hours}

Services offered:
{services}

Office hours flow:
1. Greet caller
2. Ask purpose of call
3. Collect caller name and phone number
4. Route call or transfer if needed
5. If transfer fails, inform caller someone will follow up
6. Ask if anything else is needed
7. Close call politely

After hours flow:
1. Greet caller
2. Ask purpose
3. Confirm if emergency
4. If emergency → collect name, phone, address
5. Attempt transfer
6. If transfer fails → assure follow-up
7. If non-emergency → collect request and confirm next business day follow-up

Additional after hours rules:
{after_hours}
"""

    return system_prompt


def build_agent_spec(memo):

    agent_spec = {

        "agent_name": f"{memo['account_id']}_agent",

        "voice_style": "professional friendly",

        "system_prompt": build_prompt(memo),

        "key_variables": {
            "business_hours": memo["business_hours"],
            "office_address": memo["office_address"],
            "services_supported": memo["services_supported"]
        },

        "tool_invocation_placeholders": [
            "transfer_call",
            "send_sms_notification",
            "log_call_details"
        ],

        "call_transfer_protocol":
            memo["call_transfer_rules"],

        "fallback_protocol":
            "If call transfer fails, apologize and inform caller that a team member will return the call shortly.",

        "version": "v1"
    }

    return agent_spec


def main():

    if len(sys.argv) < 3:
        print("Usage: python generate_agent_spec.py <account_memo> <output>")
        return

    memo_file = sys.argv[1]
    output_file = sys.argv[2]

    memo = load_memo(memo_file)

    agent_spec = build_agent_spec(memo)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(agent_spec, f, indent=2)

    print("Agent spec generated:", output_file)


if __name__ == "__main__":
    main()