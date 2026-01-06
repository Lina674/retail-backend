"""
Simple test with one image
"""
import requests
import base64
import json

API_URL = "https://cjrw1dwlx2.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles"

def encode_image(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

print("Testing with 1 image...")
image1 = encode_image("img/download (1).jpg")

payload = {
    "images": [image1],
    "age": "25",
    "gender": "female",
    "occasion": "garden party",
    "season": "summer",
    "budget": 200
}

print(f"Sending request to {API_URL}")
response = requests.post(API_URL, json=payload, timeout=300)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(response.text)
