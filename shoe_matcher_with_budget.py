"""
Shoe Matcher Agent with Budget - Finds the best matching shoes within budget from DynamoDB
"""
import boto3
import json
import base64
import sys
import os
from decimal import Decimal

class ShoeMatcherWithBudget:
    def __init__(self, budget=200):
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        self.table = self.dynamodb.Table('aldo-product-metadata')
        self.bucket_name = 'aldo-images'
        self.budget = budget
        
    def analyze_outfit(self, image_path):
        """Analyze the outfit image and get description"""
        print(f"Analyzing outfit from: {image_path}")
        
        with open(image_path, 'rb') as f:
            image_bytes = base64.b64encode(f.read()).decode('utf-8')
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
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
                            "text": "Describe this outfit in detail, focusing on colors, style, and formality. What type of shoes would complement this outfit best?"
                        }
                    ]
                }
            ]
        }
        
        response = self.bedrock.invoke_model(
            modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        outfit_description = response_body['content'][0]['text']
        
        print(f"\nOutfit Analysis:\n{outfit_description}\n")
        return outfit_description
    
    def get_products_from_dynamodb(self):
        """Get all products from DynamoDB within budget"""
        print(f"Fetching products from DynamoDB (Budget: ${self.budget})...")
        
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            
            # Continue scanning if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))
            
            # Filter by budget
            affordable_items = []
            for item in items:
                price_str = str(item.get('price', '0'))
                # Remove dollar sign and convert to float
                price = float(price_str.replace('$', '').replace(',', ''))
                item['price_float'] = price  # Store cleaned price
                if price <= self.budget:
                    affordable_items.append(item)
            
            print(f"Found {len(affordable_items)} products within budget (out of {len(items)} total)\n")
            return affordable_items
            
        except Exception as e:
            print(f"Error fetching from DynamoDB: {e}")
            return []
    
    def match_shoes_with_outfit(self, outfit_description, products):
        """Match shoes with outfit using Claude and product descriptions"""
        print(f"Analyzing {len(products)} products for outfit match...\n")
        
        # Prepare all product descriptions for batch analysis
        product_descriptions = []
        for product in products:
            product_id = product.get('product_id', 'unknown')
            name = product.get('product_name', 'Unknown Product')
            description = product.get('description', 'No description available')
            price = product.get('price_float', 0)
            
            product_descriptions.append({
                'product_id': product_id,
                'name': name,
                'description': description,
                'price': price,
                'image_key': product.get('s3_image_key', ''),
                'url': product.get('product_url', 'N/A')
            })
        
        # Create a single request to analyze all products
        products_text = "\n\n".join([
            f"{i+1}. {p['name']} (${p['price']:.2f})\n   Description: {p['description']}"
            for i, p in enumerate(product_descriptions)
        ])
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""I need to match shoes with this outfit:

{outfit_description}

Here are the available shoes:

{products_text}

Rate each shoe on how well it matches the outfit (1-10 scale). Respond with a JSON array where each object has:
- "number": the shoe number (1-{len(product_descriptions)})
- "score": match score (1-10)
- "reason": brief explanation (max 100 chars)

Format: [{{"number": 1, "score": 8, "reason": "..."}}]"""
                        }
                    ]
                }
            ]
        }
        
        try:
            print("Analyzing all products with Claude...")
            # Call Bedrock
            bedrock_response = self.bedrock.invoke_model(
                modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(bedrock_response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Extract JSON from response
            start = analysis_text.find('[')
            end = analysis_text.rfind(']') + 1
            json_str = analysis_text[start:end]
            ratings = json.loads(json_str)
            
            # Map ratings back to products
            shoe_scores = []
            for rating in ratings:
                idx = rating.get('number', 0) - 1
                if 0 <= idx < len(product_descriptions):
                    product = product_descriptions[idx]
                    shoe_scores.append({
                        'product_id': product['product_id'],
                        'name': product['name'],
                        'price': product['price'],
                        'image': product['image_key'],
                        'score': rating.get('score', 0),
                        'reason': rating.get('reason', 'No reason provided'),
                        'url': product['url']
                    })
                    print(f"  {product['name']}: {rating.get('score')}/10")
            
            # Sort by score (descending), then by price (ascending) for ties
            shoe_scores.sort(key=lambda x: (-x['score'], x['price']))
            return shoe_scores
            
        except Exception as e:
            print(f"Error analyzing products: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def display_results(self, shoe_scores, outfit_name):
        """Display the top 5 results"""
        print("\n" + "="*80)
        print(f"TOP 5 MATCHING SHOES FOR: {outfit_name}")
        print(f"Budget: ${self.budget}")
        print("="*80)
        
        for i, shoe in enumerate(shoe_scores[:5], 1):
            print(f"\n{i}. {shoe['name']}")
            print(f"   Product ID: {shoe['product_id']}")
            print(f"   Price: ${shoe['price']:.2f}")
            print(f"   Match Score: {shoe['score']}/10")
            print(f"   Reason: {shoe['reason']}")
            print(f"   Image: {shoe['image']}")
            if shoe['url'] != 'N/A':
                print(f"   URL: {shoe['url']}")
        
        if shoe_scores:
            print("\n" + "="*80)
            print(f"🏆 BEST MATCH: {shoe_scores[0]['name']}")
            print(f"   Price: ${shoe_scores[0]['price']:.2f}")
            print(f"   Score: {shoe_scores[0]['score']}/10")
            print(f"   {shoe_scores[0]['reason']}")
            print("="*80)
    
    def run(self, outfit_images):
        """Main agent execution for multiple outfit images"""
        try:
            all_results = {}
            
            for outfit_image in outfit_images:
                if not os.path.exists(outfit_image):
                    print(f"Error: Image file not found: {outfit_image}")
                    continue
                
                print("\n" + "="*80)
                print(f"PROCESSING: {outfit_image}")
                print("="*80 + "\n")
                
                # Step 1: Analyze the outfit
                outfit_description = self.analyze_outfit(outfit_image)
                
                # Step 2: Get products from DynamoDB
                products = self.get_products_from_dynamodb()
                
                if not products:
                    print("No products found within budget")
                    continue
                
                # Step 3: Match shoes with outfit
                shoe_scores = self.match_shoes_with_outfit(outfit_description, products)
                
                # Step 4: Display results
                outfit_name = os.path.basename(outfit_image)
                self.display_results(shoe_scores, outfit_name)
                
                all_results[outfit_image] = shoe_scores[:5]
            
            return all_results
            
        except Exception as e:
            print(f"Error running agent: {e}")
            import traceback
            traceback.print_exc()
            return {}


def main():
    if len(sys.argv) < 2:
        print("Usage: python shoe_matcher_with_budget.py <outfit_image1> [outfit_image2] ...")
        print("Example: python shoe_matcher_with_budget.py img/download.jpg img/outfit2.jpg")
        sys.exit(1)
    
    outfit_images = sys.argv[1:]
    budget = 200  # Default budget
    
    print("="*80)
    print("SHOE MATCHER AGENT WITH BUDGET")
    print(f"Finding the best matching shoes within ${budget} budget")
    print(f"Analyzing {len(outfit_images)} outfit(s)")
    print("="*80 + "\n")
    
    agent = ShoeMatcherWithBudget(budget=budget)
    agent.run(outfit_images)


if __name__ == "__main__":
    main()
