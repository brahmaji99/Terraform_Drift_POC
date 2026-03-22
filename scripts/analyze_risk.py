import json
import boto3
import sys
import os  # <--- added

# Use AWS_DEFAULT_REGION from environment or default
region = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-2')
client = boto3.client('bedrock-runtime', region_name=region)

file = sys.argv[1]

with open(file) as f:
    data = json.load(f)

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

response = client.invoke_model(
    modelId="anthropic.claude-v2",
    body=json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 50
    })
)

result = json.loads(response['body'].read())
output = result.get("completion", "").strip()

print(output)

if "LOW" in output:
    sys.exit(0)
elif "MEDIUM" in output:
    sys.exit(1)
else:
    sys.exit(2)