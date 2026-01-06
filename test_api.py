"""
Test script for Outfit Bundle API
"""
import requests
import base64
import json

# API endpoint (change to your deployed URL)
API_URL = "http://localhost:5000/outfit-bundles"

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_api():
    """Test the API with sample images"""
    
    # Encode images
    image1 = encode_image("img/download (1).jpg")
    image2 = encode_image("img/download (2).jpg")
    
    # Prepare request
    payload = {
        "images": [image1, image2],
        "age": "25",
        "gender": "female",
        "occasion": "garden party",
        "season": "summer",
        "budget": 200
    }
    
    print("Sending request to API...")
    print(f"URL: {API_URL}")
    print(f"Images: 2")
    print(f"Context: age={payload['age']}, gender={payload['gender']}, occasion={payload['occasion']}, season={payload['season']}")
    
    # Send request
    response = requests.post(API_URL, json=payload)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nSuccess! Received bundles:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\nError: {response.text}")

if __name__ == "__main__":
    test_api()
