import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('aldo-product-metadata')

response = table.scan(Limit=2)
items = response.get('Items', [])

print("Sample items from DynamoDB:")
print(json.dumps(items, indent=2, default=str))
