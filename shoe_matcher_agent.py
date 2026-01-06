"""
Shoe Matcher Agent - Finds the best matching shoes from aldo-images bucket for any outfit
"""
import boto3
import json
import base64
import sys
import os

class ShoeMatcherAgent:
    def __init__(self):
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.bucket_name = 'aldo-images'
        
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
    
    def find_matching_shoes(self, outfit_description):
        """Find matching shoes from S3 bucket"""
        print(f"Searching {self.bucket_name} for matching shoes...\n")
        
        # List all objects in bucket
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        
        if 'Contents' not in response:
            print("No images found in bucket")
            return []
        
        shoe_scores = []
        total_shoes = len([obj for obj in response['Contents'] 
                          if obj['Key'].lower().endswith(('.jpg', '.jpeg', '.png'))])
        current = 0
        
        for obj in response['Contents']:
            key = obj['Key']
            
            # Skip non-image files
            if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            current += 1
            print(f"[{current}/{total_shoes}] Analyzing: {key}")
            
            try:
                # Download image from S3
                image_obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
                image_bytes = image_obj['Body'].read()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Determine media type
                media_type = 'image/jpeg' if key.lower().endswith(('.jpg', '.jpeg')) else 'image/png'
                
                # Create request for Claude
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 500,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": f"""Rate how well these shoes would match with this outfit on a scale of 1-10:

{outfit_description}

Respond ONLY with a JSON object in this exact format:
{{"score": <number 1-10>, "reason": "<brief explanation>"}}"""
                                }
                            ]
                        }
                    ]
                }
                
                # Call Bedrock
                bedrock_response = self.bedrock.invoke_model(
                    modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                    body=json.dumps(request_body)
                )
                
                # Parse response
                response_body = json.loads(bedrock_response['body'].read())
                analysis_text = response_body['content'][0]['text']
                
                # Extract JSON from response
                try:
                    start = analysis_text.find('{')
                    end = analysis_text.rfind('}') + 1
                    json_str = analysis_text[start:end]
                    analysis = json.loads(json_str)
                    
                    score = analysis.get('score', 0)
                    reason = analysis.get('reason', 'No reason provided')
                    
                    shoe_scores.append({
                        'image': key,
                        'score': score,
                        'reason': reason
                    })
                    
                    print(f"  Score: {score}/10 - {reason[:60]}...")
                    
                except json.JSONDecodeError:
                    print(f"  Could not parse response")
                    
            except Exception as e:
                print(f"  Error: {e}")
                continue
        
        # Sort by score
        shoe_scores.sort(key=lambda x: x['score'], reverse=True)
        return shoe_scores
    
    def display_results(self, shoe_scores):
        """Display the results"""
        print("\n" + "="*80)
        print("BEST MATCHING SHOES (Top 5)")
        print("="*80)
        
        for i, shoe in enumerate(shoe_scores[:5], 1):
            print(f"\n{i}. {shoe['image']}")
            print(f"   Score: {shoe['score']}/10")
            print(f"   Reason: {shoe['reason']}")
        
        if shoe_scores:
            print("\n" + "="*80)
            print(f"🏆 TOP RECOMMENDATION: {shoe_scores[0]['image']}")
            print(f"   Score: {shoe_scores[0]['score']}/10")
            print(f"   {shoe_scores[0]['reason']}")
            print("="*80)
    
    def run(self, outfit_image_path):
        """Main agent execution"""
        try:
            # Step 1: Analyze the outfit
            outfit_description = self.analyze_outfit(outfit_image_path)
            
            # Step 2: Find matching shoes
            shoe_scores = self.find_matching_shoes(outfit_description)
            
            # Step 3: Display results
            self.display_results(shoe_scores)
            
            return shoe_scores
            
        except Exception as e:
            print(f"Error running agent: {e}")
            return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python shoe_matcher_agent.py <outfit_image_path>")
        print("Example: python shoe_matcher_agent.py img/download.jpg")
        sys.exit(1)
    
    outfit_image = sys.argv[1]
    
    if not os.path.exists(outfit_image):
        print(f"Error: Image file not found: {outfit_image}")
        sys.exit(1)
    
    print("="*80)
    print("SHOE MATCHER AGENT")
    print("Finding the best matching shoes from Aldo collection")
    print("="*80 + "\n")
    
    agent = ShoeMatcherAgent()
    agent.run(outfit_image)


if __name__ == "__main__":
    main()
