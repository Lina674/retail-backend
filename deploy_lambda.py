"""
Deploy Outfit Bundle API to AWS Lambda with API Gateway
"""
import boto3
import zipfile
import os
import json
import time

def create_deployment_package():
    """Create a deployment package with all dependencies"""
    print("Creating deployment package...")
    
    # Files to include
    files = [
        'outfit_bundle_api.py',
        'outfit_bundle_agent.py'
    ]
    
    # Create zip file
    zip_path = 'lambda_deployment.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  Added {file}")
    
    print(f"Deployment package created: {zip_path}")
    return zip_path

def create_lambda_role(iam_client):
    """Create IAM role for Lambda"""
    role_name = 'OutfitBundleAPIRole'
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        print(f"Creating IAM role: {role_name}")
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Outfit Bundle API Lambda'
        )
        role_arn = response['Role']['Arn']
        
        # Attach policies
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess',
            'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
        ]
        
        for policy in policies:
            iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy)
            print(f"  Attached policy: {policy}")
        
        # Add Bedrock policy
        bedrock_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "bedrock:InvokeModel",
                    "Resource": "*"
                }
            ]
        }
        
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockAccess',
            PolicyDocument=json.dumps(bedrock_policy)
        )
        print("  Added Bedrock access policy")
        
        # Wait for role to be available
        print("  Waiting for role to be ready...")
        time.sleep(10)
        
        return role_arn
        
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"Role {role_name} already exists, using existing role")
        response = iam_client.get_role(RoleName=role_name)
        return response['Role']['Arn']

def create_or_update_lambda(lambda_client, role_arn, zip_path):
    """Create or update Lambda function"""
    function_name = 'OutfitBundleAPI'
    
    with open(zip_path, 'rb') as f:
        zip_content = f.read()
    
    try:
        print(f"Creating Lambda function: {function_name}")
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.11',
            Role=role_arn,
            Handler='outfit_bundle_api.lambda_handler',
            Code={'ZipFile': zip_content},
            Timeout=300,
            MemorySize=3008,
            Environment={
                'Variables': {}
            }
        )
        function_arn = response['FunctionArn']
        print(f"Lambda function created: {function_arn}")
        
    except lambda_client.exceptions.ResourceConflictException:
        print(f"Function {function_name} already exists, updating...")
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        function_arn = response['FunctionArn']
        print(f"Lambda function updated: {function_arn}")
    
    return function_arn

def create_api_gateway(apigateway_client, lambda_client, function_arn):
    """Create API Gateway REST API"""
    api_name = 'OutfitBundleAPI'
    
    # Create REST API
    print(f"Creating API Gateway: {api_name}")
    api_response = apigateway_client.create_rest_api(
        name=api_name,
        description='Outfit Bundle API',
        endpointConfiguration={'types': ['REGIONAL']}
    )
    api_id = api_response['id']
    print(f"API created: {api_id}")
    
    # Get root resource
    resources = apigateway_client.get_resources(restApiId=api_id)
    root_id = resources['items'][0]['id']
    
    # Create /outfit-bundles resource
    resource_response = apigateway_client.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='outfit-bundles'
    )
    resource_id = resource_response['id']
    
    # Create POST method
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        authorizationType='NONE'
    )
    
    # Set up Lambda integration
    region = 'us-east-1'
    account_id = boto3.client('sts').get_caller_identity()['Account']
    uri = f'arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{function_arn}/invocations'
    
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='POST',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=uri
    )
    
    # Enable CORS
    apigateway_client.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        authorizationType='NONE'
    )
    
    apigateway_client.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        type='MOCK',
        requestTemplates={'application/json': '{"statusCode": 200}'}
    )
    
    apigateway_client.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': True,
            'method.response.header.Access-Control-Allow-Methods': True,
            'method.response.header.Access-Control-Allow-Origin': True
        }
    )
    
    apigateway_client.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod='OPTIONS',
        statusCode='200',
        responseParameters={
            'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
            'method.response.header.Access-Control-Allow-Origin': "'*'"
        }
    )
    
    # Deploy API
    deployment = apigateway_client.create_deployment(
        restApiId=api_id,
        stageName='prod'
    )
    
    # Add Lambda permission for API Gateway
    lambda_client.add_permission(
        FunctionName='OutfitBundleAPI',
        StatementId='apigateway-invoke',
        Action='lambda:InvokeFunction',
        Principal='apigateway.amazonaws.com',
        SourceArn=f'arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*'
    )
    
    api_url = f'https://{api_id}.execute-api.{region}.amazonaws.com/prod/outfit-bundles'
    print(f"\n✅ API Gateway deployed!")
    print(f"API URL: {api_url}")
    
    return api_url

def main():
    print("="*80)
    print("Deploying Outfit Bundle API to AWS")
    print("="*80 + "\n")
    
    # Create clients
    iam_client = boto3.client('iam', region_name='us-east-1')
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    apigateway_client = boto3.client('apigateway', region_name='us-east-1')
    
    # Step 1: Create deployment package
    zip_path = create_deployment_package()
    
    # Step 2: Create IAM role
    role_arn = create_lambda_role(iam_client)
    
    # Step 3: Create/update Lambda function
    function_arn = create_or_update_lambda(lambda_client, role_arn, zip_path)
    
    # Step 4: Create API Gateway
    api_url = create_api_gateway(apigateway_client, lambda_client, function_arn)
    
    print("\n" + "="*80)
    print("Deployment Complete!")
    print("="*80)
    print(f"\nAPI Endpoint: {api_url}")
    print("\nTest with:")
    print(f'  curl -X POST {api_url} -H "Content-Type: application/json" -d @test_payload.json')
    
    # Clean up
    os.remove(zip_path)
    print(f"\nCleaned up: {zip_path}")

if __name__ == '__main__':
    main()
