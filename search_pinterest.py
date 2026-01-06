import os
import requests
import json

# Get Pinterest access token from environment
access_token = os.environ.get('PINTEREST_ACCESS_TOKEN')

if not access_token:
    print("Error: PINTEREST_ACCESS_TOKEN not set")
    print("Please get your token from https://developers.pinterest.com/")
    exit(1)

# Search queries from Claude's analysis
search_queries = [
    "Classic leather pumps cognac heel",
    "Minimal white leather sneakers",
    "Neutral suede ankle boots",
    "Professional block heel nude pumps"
]

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

print("Searching Pinterest for matching shoes...\n")

for query in search_queries:
    print(f"\n{'='*60}")
    print(f"Search: {query}")
    print('='*60)
    
    # Pinterest API v5 search endpoint
    url = f'https://api.pinterest.com/v5/search/pins?query={query}&limit=5'
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            if items:
                for i, pin in enumerate(items, 1):
                    print(f"\n{i}. {pin.get('title', 'No title')}")
                    print(f"   Link: {pin.get('link', 'N/A')}")
                    print(f"   Image: {pin.get('media', {}).get('images', {}).get('original', {}).get('url', 'N/A')}")
            else:
                print("No results found")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error searching: {e}")

print("\n" + "="*60)
print("Search complete!")
