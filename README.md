# Retail Outfit Matching System

This repository contains a collection of scripts and tools for analyzing outfits, matching shoes, searching Pinterest for fashion trends, and deploying related services to AWS. It also includes an MCP server for Pinterest integration.

---

## Project Structure

- analyze_outfit.py – Script for analyzing outfit data
- analyze-outfit.ps1 – PowerShell script for outfit analysis
- API_README.md – Documentation for API usage
- AWS_ARCHITECTURE_EXPLANATION.md – Explanation of AWS architecture
- check_dynamodb.py – Script to check DynamoDB resources
- check_product_types.py – Script to verify product types
- COST_BREAKDOWN.md – Cost analysis documentation
- create_layer.ps1 – PowerShell script to create AWS layers
- deploy_lambda.py – Script for deploying AWS Lambda functions
- deploy_to_aws.ps1 – PowerShell script for AWS deployment
- find_matching_shoes.py – Script for finding matching shoes
- list_aws_resources.py – Script to list AWS resources
- outfit_bundle_agent.py – Agent for outfit bundling
- outfit_bundle_api.py – API for outfit bundles
- request.json – Sample request JSON
- requirements.txt – Python dependencies
- run_shoe_matcher.bat – Batch script to run shoe matcher
- search_pinterest.py – Script for searching Pinterest
- serverless.yml – Serverless Framework configuration
- shoe_matcher_agent.py – Agent for shoe matching
- shoe_matcher_with_budget.py – Shoe matcher with budget constraints
- SOCIAL_MEDIA_TRENDS_SUMMARY.md – Summary of social media trends
- SYSTEM_FLOWCHART_HORIZONTAL.md – System flowchart documentation
- pinterest-mcp/ – Subdirectory containing the MCP server for Pinterest  
  - See README.md inside this directory for details

---

## Setup

### Clone the Repository

```
git clone <repository-url>  
cd retail
```
### Install Python Dependencies
```
pip install -r requirements.txt
```
### AWS Deployment Prerequisites

- AWS CLI configured
- Serverless Framework installed

### Pinterest Integration

Refer to the README.md inside the pinterest-mcp directory for setup instructions.

---

## Usage

### Run Outfit Analysis
```
python analyze_outfit.py
```
### Deploy to AWS
```
python deploy_lambda.py
```
or use the provided PowerShell scripts.

### Search Pinterest
```
python search_pinterest.py
```
### Match Shoes
```
python find_matching_shoes.py
```
See individual script files and documentation for detailed usage instructions.

---

## Contributing

Please follow standard Git practices. Ensure all changes are tested before committing.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

Note: The pinterest-mcp subdirectory has its own license as specified in its LICENSE file.
