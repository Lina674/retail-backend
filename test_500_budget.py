"""
Test with $500 budget
"""
import requests
import base64
import json

API_URL = "https://cjrw1dwlx2.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles"

def encode_image(image_path):
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

print("Testing with $500 budget...")
image1 = encode_image("img/download (1).jpg")

payload = {
    "images": [image1],
    "age": "25",
    "gender": "female",
    "occasion": "garden party",
    "season": "summer",
    "budget": 500
}

print(f"Sending request to {API_URL}")
print(f"Budget: ${payload['budget']}")
response = requests.post(API_URL, json=payload, timeout=300)

print(f"\nStatus: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
    
    # Summary
    print("\n" + "="*80)
    print("BUNDLE SUMMARY")
    print("="*80)
    for bundle in result['bundles']:
        print(f"\n{bundle['bundle_number']}. {bundle['bundle_name']} ({bundle['bundle_type']})")
        print(f"   Total: ${bundle['total_cost']:.2f} | Score: {bundle['match_score']}/10")
        print(f"   Items: {len(bundle['items'])}")
        for item in bundle['items']:
            print(f"     - {item['category']}: {item['product_name']} (${item['price']:.2f})")
else:
    print(response.text)
