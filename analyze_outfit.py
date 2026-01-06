import base64
import json
import boto3

# Read and encode the image
with open('img/download.jpg', 'rb') as f:
    image_bytes = base64.b64encode(f.read()).decode('utf-8')

# Create the request body
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 2000,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_bytes
                    }
                },
                {
                    "type": "text",
                    "text": "Analyze this outfit image and suggest what type of shoes would go well with it. Be specific about style, color, and type of shoes. Provide a concise description suitable for a Pinterest search query."
                }
            ]
        }
    ]
}

# Call Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock.invoke_model(
    modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
    body=json.dumps(request_body)
)

# Parse and print the response
response_body = json.loads(response['body'].read())
print(response_body['content'][0]['text'])
