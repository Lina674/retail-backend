# Outfit Bundle API - AWS Architecture Explanation

## System Overview
An AI-powered outfit recommendation system that analyzes clothing images and suggests matching shoes, handbags, and accessories from Aldo's product catalog.

---

## Core Components

### 📦 **Lambda Function: OutfitBundleAPI**
**What it does:** The main application server that processes outfit images and generates product recommendations.

**How it works:**
1. Receives outfit images (base64 encoded) from frontend
2. Uses AWS Bedrock (Claude AI) to analyze the outfit style, colors, and context
3. Queries DynamoDB for matching products (shoes, handbags, jewelry, clothing)
4. Creates 3 curated bundles: budget, mid-range, and premium
5. Returns JSON with product details, prices, images, and styling notes

**Configuration:**
- 3GB memory for handling image processing
- 5-minute timeout for AI analysis
- Python 3.11 runtime

---

### 📚 **Lambda Layer: outfit-bundle-dependencies**
**What it does:** Contains Python libraries (boto3) needed by the Lambda function.

**Why separate:** Lambda has a 50MB deployment limit. Layers allow us to package dependencies separately, keeping the main code small and deployments fast.

---

### 🌐 **API Gateway: OutfitBundleAPI**
**What it does:** The public HTTPS endpoint that frontend applications call.

**How it works:**
- Receives POST requests with outfit images and context (age, gender, occasion, season, budget)
- Routes requests to Lambda function
- Handles CORS for cross-origin requests from web browsers
- Returns JSON responses to frontend

**Endpoint:** `https://cjrw1dwlx2.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles`

---

### 🔐 **IAM Role: OutfitBundleAPIRole**
**What it does:** Security permissions that define what the Lambda function can access.

**Permissions granted:**
- **Lambda execution:** Write logs to CloudWatch for debugging
- **DynamoDB read:** Query product catalog
- **S3 read:** Access product images
- **Bedrock invoke:** Use Claude AI for image analysis

**Why important:** Follows AWS security best practice of "least privilege" - only grants necessary permissions.

---

### 🗄️ **DynamoDB Tables**

#### **aldo-product-metadata (370 items)**
**What it stores:** Complete product catalog with details for each Aldo product.

**Data structure:**
```json
{
  "product_id": "aldo_10021228282155",
  "product_name": "Efemina",
  "price": "$39.97",
  "product_type": "FOOTWEAR",
  "description": "Wedge sandals...",
  "s3_image_key": "aldo_10021228282155.jpg",
  "product_url": "https://www.aldoshoes.com/...",
  "original_image_url": "https://cdn.shopify.com/..."
}
```

**Why DynamoDB:** Fast queries, scalable, serverless (no server management needed).

#### **aldo-products (154 items)**
**What it stores:** Simplified product data (backup/alternative table).

---

### 🪣 **S3 Buckets**

#### **aldo-images (154 images)**
**What it stores:** Product photos downloaded from Aldo's website.

**Usage:** Lambda downloads these images when analyzing products to match with outfits.

#### **aldo-embeddings (370 files)**
**What it stores:** AI-generated vector representations of products for similarity search.

**Purpose:** Enables "find similar products" functionality using machine learning.

#### **aldo-kb-documents (370 files)**
**What it stores:** Product descriptions and metadata for AWS Knowledge Base.

**Purpose:** Powers semantic search - find products by natural language queries like "comfortable summer sandals."

#### **Other buckets:**
- **aldo-product-images-retail-hack:** Duplicate image storage
- **aldo-gift-finder-1762463861:** Gift recommendation feature data
- **aldo-kb-docs-multimodal:** Multimodal search (text + images) - currently empty
- **aldo-pieces:** Reserved for future use - currently empty

---

## Data Flow

```
Frontend (React/Vue)
    ↓ POST /outfit-bundles
    ↓ {images: [...], age: 25, budget: 200}
    ↓
API Gateway
    ↓
Lambda Function
    ↓
    ├→ AWS Bedrock (Claude AI)
    │   └→ Analyzes outfit images
    │       Returns: style, colors, occasion fit
    │
    ├→ DynamoDB (aldo-product-metadata)
    │   └→ Queries matching products
    │       Returns: shoes, handbags, jewelry, clothing
    │
    ├→ S3 (aldo-images)
    │   └→ Gets product image URLs
    │
    └→ Returns JSON
        {
          bundles: [
            {items: [...], total_cost: 84.94},
            {items: [...], total_cost: 198.00},
            {items: [...], total_cost: 272.00}
          ]
        }
```

---

## Cost Breakdown (Estimated Monthly)

**For 10,000 API calls/month:**

- **Lambda:** ~$5 (compute time)
- **API Gateway:** ~$35 (API requests)
- **Bedrock (Claude):** ~$100-200 (AI image analysis)
- **DynamoDB:** ~$1 (read operations)
- **S3:** ~$1 (storage + data transfer)

**Total:** ~$142-242/month

**Scalability:** Can handle 100,000+ requests/month with minimal cost increase due to serverless architecture.

---

## Key Features

✅ **AI-Powered:** Uses Claude 3.5 Sonnet for intelligent outfit analysis
✅ **Context-Aware:** Considers age, gender, occasion, season, and budget
✅ **Flexible Bundles:** 1-3 items per bundle, always includes shoes
✅ **Budget-Conscious:** 2 bundles within budget, 1 premium option
✅ **Fast:** ~20-25 seconds response time for single image
✅ **Scalable:** Serverless architecture handles traffic spikes automatically
✅ **Secure:** IAM roles enforce least-privilege access

---

## Technical Decisions

**Why AWS Lambda?**
- No server management
- Pay only for actual usage
- Auto-scales with demand
- Integrates seamlessly with other AWS services

**Why DynamoDB?**
- Millisecond query latency
- Serverless (no capacity planning)
- Flexible schema for product data
- Cost-effective for read-heavy workloads

**Why Bedrock (Claude)?**
- State-of-the-art vision AI
- Understands fashion and styling
- Generates natural language explanations
- Managed service (no model hosting)

**Why API Gateway?**
- HTTPS endpoint with SSL
- Built-in CORS support
- Request throttling and rate limiting
- Monitoring and logging

---

## Future Enhancements

🔮 **Potential additions:**
- Caching layer (ElastiCache) for faster repeated queries
- Step Functions for multi-image processing
- EventBridge for async processing
- CloudFront CDN for global distribution
- Cognito for user authentication
- SQS queue for handling traffic spikes

---

## Monitoring & Debugging

**CloudWatch Logs:** All Lambda execution logs
**CloudWatch Metrics:** API latency, error rates, invocation counts
**X-Ray:** Distributed tracing for performance analysis

**Access logs:**
```bash
aws logs tail /aws/lambda/OutfitBundleAPI --follow
```

---

## Security

✅ **Encryption:** All data encrypted at rest (S3, DynamoDB)
✅ **HTTPS:** All API traffic encrypted in transit
✅ **IAM:** Role-based access control
✅ **VPC:** Can be deployed in private VPC if needed
✅ **Secrets:** API keys stored in environment variables (can use Secrets Manager)

---

## Deployment

**Current deployment:** Manual via Python script
**Recommended:** Use AWS SAM or Terraform for infrastructure-as-code

**Update Lambda:**
```bash
python deploy_lambda.py
```

**Test API:**
```bash
python test_simple.py
```

---

## Support & Maintenance

**Logs:** CloudWatch Logs (7-day retention)
**Alerts:** Can configure CloudWatch Alarms for errors
**Backup:** DynamoDB point-in-time recovery enabled
**Updates:** Lambda code can be updated without downtime
