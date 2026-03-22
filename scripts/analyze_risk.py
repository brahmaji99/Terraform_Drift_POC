import os
import json
import boto3
import sys

# Get region and Bedrock model/profile from environment
region = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-2')
model_id_or_profile = os.environ.get(
    'BEDROCK_MODEL_ID',
    'anthropic.claude-v2'  # fallback if not set
)

# Initialize Bedrock client
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

# Construct prompt
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

Return ONLY one word: LOW or MEDIUM or HIGH

DATA:
{json.dumps(data)[:4000]}
"""

# Call Bedrock using correct format (IMPORTANT FIX)
try:
    response = client.invoke_model(
        modelId=model_id_or_profile,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )
except client.exceptions.ValidationException as e:
    print(f"ValidationException: Model/Inference profile '{model_id_or_profile}' invalid or inaccessible in region {region}")
    sys.exit(1)
except Exception as e:
    print(f"Bedrock API error: {e}")
    sys.exit(1)

# Parse response safely
try:
    result = json.loads(response['body'].read())

    if "content" in result and len(result["content"]) > 0:
        output = result["content"][0]["text"].strip()
    else:
        output = str(result).strip()

except Exception as e:
    print(f"Error parsing Bedrock response: {e}")
    sys.exit(1)

print(f"Bedrock output: {output}")

# Normalize output
output_upper = output.upper()

# Exit codes for Jenkins
if "LOW" in output_upper:
    sys.exit(0)
elif "MEDIUM" in output_upper:
    sys.exit(1)
elif "HIGH" in output_upper:
    sys.exit(2)
else:
    print("Unexpected response from model")
    sys.exit(1)