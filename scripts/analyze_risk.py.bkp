import os
import json
import boto3
import sys

# Config
region = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-2')
model_id_or_profile = os.environ.get(
    'BEDROCK_MODEL_ID',
    'anthropic.claude-v2'
)

client = boto3.client('bedrock-runtime', region_name=region)

# Validate input
if len(sys.argv) < 2:
    print("Usage: python3 analyze_risk.py <drift_json_file>")
    sys.exit(1)

file = sys.argv[1]

try:
    with open(file) as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading file: {e}")
    sys.exit(1)

# Enhanced prompt (AI explanation + fix)
prompt = f"""
You are a senior cloud security engineer.

Analyze the Terraform drift data and return structured JSON.

Return ONLY valid JSON in this format:
{{
  "risk": "LOW | MEDIUM | HIGH",
  "reason": "why this drift happened",
  "impact": "what could go wrong",
  "recommendation": "how to fix it"
}}

Classification rules:
- HIGH:
  - IAM wildcard permissions
  - 0.0.0.0/0 exposure
  - Public critical resources
- MEDIUM:
  - Public S3 bucket
  - Instance type or infra change
- LOW:
  - Tags, metadata changes

Keep answers short and practical.

DATA:
{json.dumps(data)[:4000]}
"""

# Call Bedrock
try:
    response = client.invoke_model(
        modelId=model_id_or_profile,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )
except client.exceptions.ValidationException:
    print(f"ValidationException: Model/Inference profile '{model_id_or_profile}' invalid or inaccessible in region {region}")
    sys.exit(1)
except Exception as e:
    print(f"Bedrock API error: {e}")
    sys.exit(1)

# Parse response
try:
    result = json.loads(response['body'].read())

    if "content" in result and len(result["content"]) > 0:
        raw_text = result["content"][0]["text"].strip()
    else:
        raw_text = str(result)

    # Try parsing AI JSON output
    try:
        ai_output = json.loads(raw_text)
    except:
        print("⚠️ Failed to parse AI JSON. Raw output:")
        print(raw_text)
        sys.exit(1)

except Exception as e:
    print(f"Error parsing Bedrock response: {e}")
    sys.exit(1)

# Extract values
risk = ai_output.get("risk", "UNKNOWN").upper()
reason = ai_output.get("reason", "")
impact = ai_output.get("impact", "")
recommendation = ai_output.get("recommendation", "")

# Print for Jenkins logs
print("\n===== AI Drift Analysis =====")
print(f"Risk          : {risk}")
print(f"Reason        : {reason}")
print(f"Impact        : {impact}")
print(f"Recommendation: {recommendation}")
print("================================\n")

# Save report for alerts
try:
    os.makedirs("reports/risk", exist_ok=True)
    report_file = f"reports/risk/{os.path.basename(file)}"

    with open(report_file, "w") as f:
        json.dump(ai_output, f, indent=2)

    print(f"Report saved to {report_file}")

except Exception as e:
    print(f"Error saving report: {e}")

# Exit codes for Jenkins
if risk == "LOW":
    sys.exit(0)
elif risk == "MEDIUM":
    sys.exit(1)
elif risk == "HIGH":
    sys.exit(2)
else:
    print("Unknown risk level")
    sys.exit(1)