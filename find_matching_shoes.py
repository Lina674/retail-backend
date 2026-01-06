import boto3
import json
import base64
from io import BytesIO

# Initialize AWS clients
s3 = boto3.client('s3', region_name='us-east-1')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

bucket_name = 'aldo-images'

# The outfit description from previous analysis
outfit_description = """
This image shows a classic beige/khaki trench coat with traditional details like epaulettes, 
storm flaps, and a belted waist. Looking for shoes that would pair well with this versatile 
trench coat. Best matches would be within the neutral family (tans, browns, blacks, whites) 
to complement the classic nature of the trench coat.
"""

print(f"Fetching images from S3 bucket: {bucket_name}...")

try:
    # List all objects in the bucket
    response = s3.list_objects_v2(Bucket=bucket_name)
    
    if 'Contents' not in response:
        print("No images found in bucket")
        exit(1)
    
    shoe_scores = []
    
    for obj in response['Contents']:
        key = obj['Key']
        
        # Skip non-image files
        if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue
        
        print(f"\nAnalyzing: {key}")
        
        try:
            # Download image from S3
            image_obj = s3.get_object(Bucket=bucket_name, Key=key)
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
            bedrock_response = bedrock.invoke_model(
                modelId='us.anthropic.claude-3-5-sonnet-20241022-v2:0',
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(bedrock_response['body'].read())
            analysis_text = response_body['content'][0]['text']
            
            # Extract JSON from response
            try:
                # Find JSON in the response
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
                
                print(f"  Score: {score}/10")
                print(f"  Reason: {reason}")
                
            except json.JSONDecodeError:
                print(f"  Could not parse response: {analysis_text}")
                
        except Exception as e:
            print(f"  Error analyzing {key}: {e}")
            continue
    
    # Sort by score
    shoe_scores.sort(key=lambda x: x['score'], reverse=True)
    
    # Display results
    print("\n" + "="*80)
    print("BEST MATCHING SHOES (Ranked)")
    print("="*80)
    
    for i, shoe in enumerate(shoe_scores, 1):
        print(f"\n{i}. {shoe['image']}")
        print(f"   Score: {shoe['score']}/10")
        print(f"   Reason: {shoe['reason']}")
    
    if shoe_scores:
        print("\n" + "="*80)
        print(f"TOP RECOMMENDATION: {shoe_scores[0]['image']}")
        print(f"Score: {shoe_scores[0]['score']}/10")
        print(f"Reason: {shoe_scores[0]['reason']}")
        print("="*80)
    
except Exception as e:
    print(f"Error: {e}")
