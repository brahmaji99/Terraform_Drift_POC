import json
import boto3
import sys
import os

# --- Configuration ---
DEFAULT_REGION = 'ap-southeast-2'
MODEL_ID = 'anthropic.claude-v2-2023-12-06'  # default model you want to use
MAX_PROMPT_LENGTH = 4000

# --- Read AWS region from environment ---
region = os.environ.get('AWS_DEFAULT_REGION', DEFAULT_REGION)

# --- Initialize Bedrock client ---
client = boto3.client('bedrock-runtime', region_name=region)

# --- Validate input argument ---
if len(sys.argv) < 2:
    print("Usage: python analyze_risk.py <json_file>")
    sys.exit(1)

file_path = sys.argv[1]

if not os.path.isfile(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

# --- Load JSON data ---
with open(file_path) as f:
    data = json.load(f)

# --- Verify if model exists ---
try:
    available_models = [m['modelId'] for m in client.list_models()['modelSummaries']]
except Exception as e:
    print(f"Error listing Bedrock models: {e}")
    sys.exit(1)

if MODEL_ID not in available_models:
    print(f"Warning: Model '{MODEL_ID}' not available in region '{region}'. Using first available model.")
    if len(available_models) == 0:
        print("No models available in this region/account.")
        sys.exit(1)
    MODEL_ID = available_models[0]

# --- Prepare prompt ---
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
{json.dumps(data)[:MAX_PROMPT_LENGTH]}
"""

# --- Invoke model ---
try:
    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": 50
        })
    )
except Exception as e:
    print(f"Error invoking Bedrock model: {e}")
    sys.exit(1)

# --- Parse response ---
try:
    result = json.loads(response['body'].read())
    output = result.get("completion", "").strip().upper()
    print(f"Model output: {output}")
except Exception as e:
    print(f"Error parsing response: {e}")
    sys.exit(1)

# --- Exit codes ---
if "LOW" in output:
    sys.exit(0)
elif "MEDIUM" in output:
    sys.exit(1)
elif "HIGH" in output:
    sys.exit(2)
else:
    print("Could not classify risk. Exiting with failure.")
    sys.exit(1)