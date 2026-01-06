import boto3
from collections import Counter

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('aldo-product-metadata')

response = table.scan()
items = response.get('Items', [])

while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items.extend(response.get('Items', []))

product_types = [item.get('product_type', 'UNKNOWN') for item in items]
type_counts = Counter(product_types)

print("Product types in database:")
for ptype, count in type_counts.most_common():
    print(f"  {ptype}: {count}")

print(f"\nTotal products: {len(items)}")
