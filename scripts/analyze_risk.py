import os
import json
import boto3
import sys

# Get region and Bedrock model/profile from environment
region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
model_id_or_profile = os.environ.get(
    'BEDROCK_MODEL_ID',
    'anthropic.claude-v2'  # fallback if not set
)

# Initialize Bedrock client
client = boto3.client('bedrock-runtime', region_name=region)

# Load drift JSON file
if len(sys.argv) < 2:
    print("Usage: python3 analyze_risk.py <drift_json_file>")
    sys.exit(1)

file = sys.argv[1]
with open(file) as f:
    data = json.load(f)

# Construct prompt for risk classification
prompt = f"""
Classify Terraform risk:

HIGH:
- IAM * permissions
- 0.0.0.0/0 open access

MEDIUM:
- instance size change
- public S3

LOW:
- tags

Return ONLY LOW, MEDIUM, HIGH

DATA:
{json.dumps(data)[:4000]}
"""

# Attempt to invoke model
try:
    response = client.invoke_model(
        modelId=model_id_or_profile,
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 50
        })
    )
except client.exceptions.ValidationException as e:
    print(f"ValidationException: Model/Inference profile '{model_id_or_profile}' invalid or inaccessible in region {region}")
    sys.exit(1)
except Exception as e:
    print(f"Bedrock API error: {e}")
    sys.exit(1)

# Parse and print output
result = json.loads(response['body'].read())
output = result.get("completion", "").strip()
print(f"Bedrock output: {output}")

# Exit codes for Jenkins
if "LOW" in output:
    sys.exit(0)
elif "MEDIUM" in output:
    sys.exit(1)
else:  # HIGH or unknown
    sys.exit(2)