"""
List all deployed AWS resources for the Outfit Bundle API
"""
import boto3
import json

def list_resources():
    print("="*80)
    print("AWS RESOURCES FOR OUTFIT BUNDLE API")
    print("="*80)
    
    # Lambda Functions
    print("\n📦 LAMBDA FUNCTIONS:")
    print("-" * 80)
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    try:
        functions = lambda_client.list_functions()
        for func in functions['Functions']:
            if 'Outfit' in func['FunctionName']:
                print(f"\nFunction: {func['FunctionName']}")
                print(f"  ARN: {func['FunctionArn']}")
                print(f"  Runtime: {func['Runtime']}")
                print(f"  Memory: {func['MemorySize']} MB")
                print(f"  Timeout: {func['Timeout']} seconds")
                print(f"  Last Modified: {func['LastModified']}")
                
                # Get layers
                if 'Layers' in func and func['Layers']:
                    print(f"  Layers:")
                    for layer in func['Layers']:
                        print(f"    - {layer['Arn']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Lambda Layers
    print("\n\n📚 LAMBDA LAYERS:")
    print("-" * 80)
    try:
        layers = lambda_client.list_layers()
        for layer in layers['Layers']:
            if 'outfit' in layer['LayerName'].lower():
                print(f"\nLayer: {layer['LayerName']}")
                print(f"  ARN: {layer['LatestMatchingVersion']['LayerVersionArn']}")
                print(f"  Version: {layer['LatestMatchingVersion']['Version']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # API Gateway
    print("\n\n🌐 API GATEWAY:")
    print("-" * 80)
    apigateway_client = boto3.client('apigateway', region_name='us-east-1')
    try:
        apis = apigateway_client.get_rest_apis()
        for api in apis['items']:
            if 'Outfit' in api['name']:
                print(f"\nAPI: {api['name']}")
                print(f"  ID: {api['id']}")
                print(f"  Endpoint: https://{api['id']}.execute-api.us-east-1.amazonaws.com/prod")
                print(f"  Created: {api['createdDate']}")
                
                # Get resources
                resources = apigateway_client.get_resources(restApiId=api['id'])
                print(f"  Resources:")
                for resource in resources['items']:
                    if resource['path'] != '/':
                        print(f"    - {resource['path']}")
                        if 'resourceMethods' in resource:
                            methods = ', '.join(resource['resourceMethods'].keys())
                            print(f"      Methods: {methods}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # IAM Roles
    print("\n\n🔐 IAM ROLES:")
    print("-" * 80)
    iam_client = boto3.client('iam', region_name='us-east-1')
    try:
        roles = iam_client.list_roles()
        for role in roles['Roles']:
            if 'Outfit' in role['RoleName']:
                print(f"\nRole: {role['RoleName']}")
                print(f"  ARN: {role['Arn']}")
                print(f"  Created: {role['CreateDate']}")
                
                # Get attached policies
                policies = iam_client.list_attached_role_policies(RoleName=role['RoleName'])
                if policies['AttachedPolicies']:
                    print(f"  Attached Policies:")
                    for policy in policies['AttachedPolicies']:
                        print(f"    - {policy['PolicyName']}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # DynamoDB Tables
    print("\n\n🗄️  DYNAMODB TABLES:")
    print("-" * 80)
    dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
    try:
        tables = dynamodb_client.list_tables()
        for table_name in tables['TableNames']:
            if 'aldo' in table_name.lower() or 'product' in table_name.lower():
                table = dynamodb_client.describe_table(TableName=table_name)['Table']
                print(f"\nTable: {table_name}")
                print(f"  ARN: {table['TableArn']}")
                print(f"  Status: {table['TableStatus']}")
                print(f"  Item Count: {table['ItemCount']}")
                print(f"  Size: {table['TableSizeBytes'] / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"  Error: {e}")
    
    # S3 Buckets
    print("\n\n🪣 S3 BUCKETS:")
    print("-" * 80)
    s3_client = boto3.client('s3', region_name='us-east-1')
    try:
        buckets = s3_client.list_buckets()
        for bucket in buckets['Buckets']:
            if 'aldo' in bucket['Name'].lower() or 'image' in bucket['Name'].lower():
                print(f"\nBucket: {bucket['Name']}")
                print(f"  Created: {bucket['CreationDate']}")
                
                # Get object count
                try:
                    objects = s3_client.list_objects_v2(Bucket=bucket['Name'], MaxKeys=1)
                    if 'KeyCount' in objects:
                        # Get approximate count
                        response = s3_client.list_objects_v2(Bucket=bucket['Name'])
                        count = response.get('KeyCount', 0)
                        print(f"  Objects: ~{count}")
                except:
                    pass
    except Exception as e:
        print(f"  Error: {e}")
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("\n✅ Deployed Components:")
    print("  - Lambda Function: OutfitBundleAPI")
    print("  - Lambda Layer: outfit-bundle-dependencies")
    print("  - API Gateway: OutfitBundleAPI")
    print("  - IAM Role: OutfitBundleAPIRole")
    print("  - DynamoDB Table: aldo-product-metadata")
    print("  - S3 Bucket: aldo-images")
    print("\n🌐 API Endpoint:")
    print("  https://cjrw1dwlx2.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles")
    print("\n" + "="*80)

if __name__ == '__main__':
    list_resources()
