"""
Test the deployed API Gateway endpoint
"""
import requests
import base64
import json

# Your deployed API URL
API_URL = "https://cjrw1dwlx2.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles"

def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_deployed_api():
    """Test the deployed API"""
    
    print("="*80)
    print("Testing Deployed API Gateway")
    print("="*80)
    print(f"\nAPI URL: {API_URL}\n")
    
    # Encode images
    print("Encoding images...")
    image1 = encode_image("img/download (1).jpg")
    image2 = encode_image("img/download (2).jpg")
    print(f"  Image 1: {len(image1)} bytes (base64)")
    print(f"  Image 2: {len(image2)} bytes (base64)")
    
    # Prepare request
    payload = {
        "images": [image1, image2],
        "age": "25",
        "gender": "female",
        "occasion": "garden party",
        "season": "summer",
        "budget": 200
    }
    
    print("\nSending request...")
    print(f"  Context: age={payload['age']}, gender={payload['gender']}")
    print(f"  Occasion: {payload['occasion']}, Season: {payload['season']}")
    print(f"  Budget: ${payload['budget']}")
    
    try:
        # Send request
        response = requests.post(
            API_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=300  # 5 minutes timeout
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "="*80)
            print("✅ SUCCESS! Received bundles:")
            print("="*80)
            print(json.dumps(result, indent=2))
            
            # Summary
            print("\n" + "="*80)
            print("SUMMARY")
            print("="*80)
            print(f"Outfits analyzed: {result['outfits_count']}")
            print(f"Bundles created: {len(result['bundles'])}")
            for bundle in result['bundles']:
                print(f"\n{bundle['bundle_number']}. {bundle['bundle_name']} ({bundle['bundle_type']})")
                print(f"   Total: ${bundle['total_cost']:.2f} | Score: {bundle['match_score']}/10")
                print(f"   Shoes: {bundle['shoes']['product_name']} (${bundle['shoes']['price']:.2f})")
                print(f"   Handbag: {bundle['handbag']['product_name']} (${bundle['handbag']['price']:.2f})")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (Lambda may need more time)")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_deployed_api()
