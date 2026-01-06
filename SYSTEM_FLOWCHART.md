# Outfit Bundle API - System Flowchart

## Component Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                 │
└─────────────────────────────────────────────────────────────────────────┘

[User Browser/Mobile App]
         │
         │ (1) POST request with:
         │     - Outfit images (base64)
         │     - Context: age, gender, occasion, season, budget
         ↓
         
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                              │
└─────────────────────────────────────────────────────────────────────────┘

[API Gateway: OutfitBundleAPI]
    │ ID: cjrw1dwlx2
    │ Endpoint: /prod/outfit-bundles
    │
    ├──→ (2) CORS validation
    ├──→ (3) Request throttling
    ├──→ (4) Authentication (optional)
    │
    ↓
    
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPUTE LAYER                                    │
└─────────────────────────────────────────────────────────────────────────┘

[Lambda Function: OutfitBundleAPI]
    │ Runtime: Python 3.11
    │ Memory: 3GB
    │ Timeout: 5 minutes
    │
    ├──→ Uses [Lambda Layer: outfit-bundle-dependencies]
    │         │ Contains: boto3, AWS SDK
    │         └──→ Provides AWS service clients
    │
    ├──→ (5) Decode base64 images
    ├──→ (6) Save to temp files
    │
    ↓
    
┌─────────────────────────────────────────────────────────────────────────┐
│                            AI LAYER                                      │
└─────────────────────────────────────────────────────────────────────────┘

[AWS Bedrock: Claude 3.5 Sonnet]
    ↑ (7) Send outfit images + prompt
    │     "Analyze this outfit for a 25yo female
    │      attending a garden party in summer"
    │
    ↓ (8) Returns analysis:
          - Style description
          - Color palette
          - Formality level
          - Recommended accessories
          
[Lambda Function] ← receives AI analysis
    │
    ↓
    
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                      │
└─────────────────────────────────────────────────────────────────────────┘

[Lambda Function]
    │
    ├──→ (9) Query [DynamoDB: aldo-product-metadata]
    │         │ Scan for products within budget
    │         │ Filter by type: FOOTWEAR, BAG, JEWELRY, CLOTHING
    │         │ Limit: 200 items for performance
    │         │
    │         ↓ (10) Returns product data:
    │              - product_id, name, price
    │              - description, type
    │              - s3_image_key, product_url
    │
    ├──→ (11) Access [S3: aldo-images]
    │         │ Get product image URLs
    │         │ 154 product photos
    │         │
    │         ↓ (12) Returns image URLs
    │
    └──→ (13) Optional: [S3: aldo-embeddings]
              │ Vector embeddings for similarity search
              │ 370 embedding files
              │
              ↓ (14) Returns similar products

[Lambda Function] ← has all product data
    │
    ↓
    
┌─────────────────────────────────────────────────────────────────────────┐
│                      AI MATCHING LAYER                                   │
└─────────────────────────────────────────────────────────────────────────┘

[Lambda Function]
    │
    ├──→ (15) Send to [AWS Bedrock: Claude]
    │         │ Prompt: "Match these products with the outfit"
    │         │ Input: Outfit analysis + 40 products
    │         │        (20 shoes, 20 accessories)
    │         │
    │         ↓ (16) Returns 3 bundles:
    │              Bundle 1: Budget (under $200)
    │              Bundle 2: Mid-range (under $200)
    │              Bundle 3: Premium ($200-275)
    │              Each with: items, scores, reasons
    │
    └──→ (17) Enrich bundle data
          - Map product IDs to full details
          - Add image URLs
          - Calculate total costs
          - Format styling notes

[Lambda Function] ← has outfit analysis
    │
    ├──→ (18) 🆕 OPTIONAL: Trigger [Lambda: TrendComparison]
    │         │ (Only if user requested trend analysis)
    │         │ ⚠️ HAPPENS BEFORE PRODUCT MATCHING
    │         │
    │         ↓
    │    ┌─────────────────────────────────────────────────────────────┐
    │    │         SOCIAL MEDIA TREND COMPARISON LAYER (NEW)           │
    │    └─────────────────────────────────────────────────────────────┘
    │    
    │    [Lambda Function: TrendComparison]
    │         │ Runtime: Python 3.11
    │         │ Memory: 2GB
    │         │ Timeout: 2 minutes
    │         │
    │         ├──→ (19) Check [DynamoDB: trend-cache]
    │         │         │ Query: occasion + season + date
    │         │         │ TTL: 24 hours
    │         │         │
    │         │         ↓ If cached (< 24hrs old) - 95% of requests:
    │         │              Return cached trend data
    │         │              Cost: $0.00000025 (DynamoDB read)
    │         │              Time: ~100ms
    │         │         
    │         │         ↓ If not cached - 5% of requests:
    │         │
    │         ├──→ (20) Call [Pinterest API]
    │         │         │ Search: "{occasion} {season} outfit 2025"
    │         │         │ Example: "garden party summer outfit 2025"
    │         │         │ Returns: 20 trending pins
    │         │         │ Cost: $0.00 (free tier)
    │         │         │
    │         │         ↓ (21) Download top 5 trending images
    │         │
    │         ├──→ (22) Store in [S3: trend-images-cache]
    │         │         │ Bucket: temporary storage
    │         │         │ Lifecycle: Delete after 7 days
    │         │         │ Cost: $0.000005
    │         │         │
    │         │         ↓ (23) Returns S3 URLs
    │         │
    │         ├──→ (24) Send to [AWS Bedrock: Claude]
    │         │         │ Prompt: "Analyze these trending outfits"
    │         │         │ Input: 5 trending outfit images
    │         │         │ Cost: $0.015 (most expensive step)
    │         │         │
    │         │         ↓ (25) Returns trend analysis:
    │         │              - Common colors (coral, mint green)
    │         │              - Popular styles (flowy, bohemian)
    │         │              - Key accessories (straw bags, wedges)
    │         │              - Trending patterns (floral, polka dots)
    │         │
    │         ├──→ (26) Cache results in [DynamoDB: trend-cache]
    │         │         │ Write: occasion + season + analysis + timestamp
    │         │         │ TTL: 24 hours (auto-delete)
    │         │         │ Cost: $0.00000125
    │         │         │
    │         │         ↓ (27) Returns cached for next request
    │         │
    │         └──→ (28) Return trend context to main Lambda
    │              Returns: {
    │                "trending_colors": ["coral", "mint green"],
    │                "trending_styles": ["flowy", "bohemian"],
    │                "trending_accessories": ["straw bags", "wedges"]
    │              }
    │
    │    [Lambda: OutfitBundleAPI] ← receives trend context
    │         │
    │         └──→ (29) Query products WITH trend context
    │
    ↓
    
[Lambda Function] ← has outfit analysis + trend context
    │
    ├──→ (30) Query [DynamoDB: aldo-product-metadata]
    │         │ Now filters/prioritizes based on trends:
    │         │ - Boost products matching trending colors
    │         │ - Prioritize trending accessory types
    │         │ - Consider trending styles
    │         │
    │         ↓ (31) Returns trend-aware product list
    │
    ├──→ (32) Access [S3: aldo-images]
    │         │ Get product image URLs
    │         │
    │         ↓ (33) Returns image URLs
    │
    └──→ (34) Prepare product list for AI matching
          - 20 shoes (prioritized by trend alignment)
          - 20 accessories (prioritized by trend alignment)

[Lambda Function] ← has trend-aware product list
    │
    ├──→ (35) Send to [AWS Bedrock: Claude]
    │         │ Prompt: "Match these products with the outfit"
    │         │ Input: Outfit analysis + 40 products + TREND CONTEXT
    │         │ 
    │         │ Example prompt addition:
    │         │ "Current trends for summer garden parties:
    │         │  - Colors: coral, mint green, white
    │         │  - Styles: flowy, bohemian, romantic
    │         │  - Accessories: straw bags, wedge sandals
    │         │  Prioritize products that align with these trends."
    │         │
    │         │ Cost: $0.010 (vs $0.008 without trends)
    │         │
    │         ↓ (36) Returns 3 trend-aware bundles:
    │              Bundle 1: Budget with trending items
    │              Bundle 2: Mid-range with trending items
    │              Bundle 3: Premium with trending items
    │              Each bundle now includes trend-aligned products
    │
    └──→ (37) Enrich bundle data
          - Map product IDs to full details
          - Add image URLs
          - Calculate total costs
          - Format styling notes
          - 🆕 Add "trending" badges to relevant products
          - 🆕 Include trend alignment notes

[Lambda Function] ← has trend-aware bundles
    │
    ↓
    
┌─────────────────────────────────────────────────────────────────────────┐
│                        RESPONSE LAYER                                    │
└─────────────────────────────────────────────────────────────────────────┘

[Lambda Function]
    │
    ├──→ (34) Format JSON response
    │         │ Standard response +
    │         │ Optional trend_analysis section:
    │         │ {
    │         │   "trend_score": 82,
    │         │   "trend_insights": "Your outfit is 82% aligned...",
    │         │   "trending_colors": ["coral", "mint green"],
    │         │   "trending_styles": ["flowy", "bohemian"],
    │         │   "suggestions": ["Add a straw bag to boost score"]
    │         │ }
    │
    ↓ (35) Returns to [API Gateway]
    
[API Gateway]
    │
    ├──→ (36) Add CORS headers
    ├──→ (37) Log to [CloudWatch Logs]
    │
    ↓ (38) Returns JSON to [User Browser]

[User Browser] ← receives outfit bundles + trend insights
    │
    └──→ Displays 3 curated bundles with:
         - Product images
         - Prices and descriptions
         - Styling recommendations
         - Purchase links
         - 🆕 Trend alignment score (82%)
         - 🆕 Trend insights and suggestions
         - 🆕 "Trending" badges on products

┌─────────────────────────────────────────────────────────────────────────┐
│                      MONITORING & ANALYTICS LAYER                        │
└─────────────────────────────────────────────────────────────────────────┘

[CloudWatch Logs]
    ↑ Receives logs from:
    │ - API Gateway (all requests)
    │ - Lambda Function (execution logs)
    │ - Errors and exceptions
    │
    ↓ Feeds into:

[CloudWatch Metrics]
    │ Tracks:
    │ - API request count
    │ - Lambda invocations
    │ - Error rates
    │ - Response times (latency)
    │ - Concurrent executions
    │
    ↓ Visualized in:

[CloudWatch Dashboard: Outfit Bundle Analytics]
    │ Real-time metrics:
    │ ├─ Total API calls (hourly/daily)
    │ ├─ Average response time
    │ ├─ Success rate (200 vs errors)
    │ ├─ Lambda duration & memory usage
    │ ├─ DynamoDB read capacity
    │ ├─ Bedrock API calls & costs
    │ └─ Most requested occasions/seasons
    │
    ↓ Triggers:

[CloudWatch Alarms]
    │ Alert conditions:
    │ ├─ Error rate > 5%
    │ ├─ Response time > 30 seconds
    │ ├─ Lambda throttling
    │ └─ DynamoDB capacity exceeded
    │
    ↓ Sends notifications to:

[SNS Topic: API-Alerts]
    │
    └──→ Email/SMS to DevOps team

┌─────────────────────────────────────────────────────────────────────────┐
│                    ANALYTICS BACKEND DASHBOARD                           │
└─────────────────────────────────────────────────────────────────────────┘

[DynamoDB: api-usage-logs] (NEW)
    ↑ Lambda writes after each request:
    │ - timestamp
    │ - user_context (age, gender, occasion)
    │ - budget
    │ - selected_bundle
    │ - response_time
    │ - products_recommended
    │
    ↓ Queried by:

[Lambda Function: AnalyticsDashboard] (NEW)
    │ Aggregates data:
    │ ├─ Popular occasions (weddings, parties, casual)
    │ ├─ Average budget by age group
    │ ├─ Most recommended products
    │ ├─ Bundle selection rates (budget vs premium)
    │ ├─ Peak usage times
    │ └─ Conversion metrics
    │
    ↓ Serves data to:

[API Gateway: /analytics] (NEW)
    │ Endpoints:
    │ ├─ GET /analytics/overview
    │ ├─ GET /analytics/products/top
    │ ├─ GET /analytics/occasions
    │ └─ GET /analytics/revenue
    │
    ↓ Consumed by:

[Admin Dashboard UI] (NEW)
    │ React/Vue dashboard showing:
    │ ├─ 📊 Usage graphs (daily/weekly/monthly)
    │ ├─ 💰 Revenue projections
    │ ├─ 👗 Top product combinations
    │ ├─ 👥 User demographics
    │ ├─ ⏱️ Performance metrics
    │ └─ 🎯 Recommendation accuracy
    │
    └──→ Accessed by: Business analysts, Product managers

┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYER                                   │
└─────────────────────────────────────────────────────────────────────────┘

[IAM Role: OutfitBundleAPIRole]
    │ Permissions:
    │ ├─ Lambda execution → CloudWatch Logs
    │ ├─ DynamoDB read → aldo-product-metadata
    │ ├─ S3 read → aldo-images, aldo-embeddings
    │ ├─ Bedrock invoke → Claude models
    │ └─ DynamoDB write → api-usage-logs (analytics)
    │
    └──→ Attached to [Lambda Function]

[AWS Secrets Manager] (OPTIONAL)
    │ Stores:
    │ ├─ Pinterest API keys
    │ ├─ Third-party service tokens
    │ └─ Database credentials
    │
    └──→ Accessed by [Lambda Function]

┌─────────────────────────────────────────────────────────────────────────┐
│                      SUPPORTING SERVICES                                 │
└─────────────────────────────────────────────────────────────────────────┘

[S3: aldo-kb-documents]
    │ 370 product documents
    │ Used for: Knowledge Base semantic search
    │
    └──→ Indexed by [AWS Bedrock Knowledge Base]
         │
         └──→ Enables natural language queries:
              "Find comfortable summer sandals under $100"

[S3: aldo-gift-finder]
    │ Gift recommendation data
    │ Used for: Separate gift finder feature
    │
    └──→ Accessed by [Gift Finder Lambda] (separate service)

[DynamoDB: aldo-products]
    │ 154 items (backup table)
    │ Simplified product data
    │
    └──→ Fallback if main table unavailable

┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW SUMMARY                                │
└─────────────────────────────────────────────────────────────────────────┘

User Request (with include_trends=true)
    ↓
API Gateway (validate, throttle)
    ↓
Lambda Function (decode images)
    ↓
Bedrock Claude (analyze outfit) ←─────────────┐
    ↓                                          │
🆕 Lambda: TrendComparison (if trends enabled) │
    ↓                                          │
DynamoDB (check trend cache)                  │
    ↓ (if cached - 95% of time)               │
    └→ Return cached trend data               │
    ↓ (if not cached - 5% of time)            │
Pinterest API (fetch trending outfits)        │
    ↓                                          │
S3 (cache trend images)                       │
    ↓                                          │
Bedrock Claude (analyze trends) ──────────────┤
    ↓                                          │
DynamoDB (cache trend results, TTL=24hrs)     │
    ↓                                          │
Lambda (return trend context) ────────────────┘
    ↓
Lambda (query products with trend context)
    ↓
DynamoDB (get product catalog)
    ↓
S3 (get image URLs)
    ↓
Lambda (prepare product list)
    ↓
Bedrock Claude (match products WITH trend awareness)
    │ Prompt now includes:
    │ - Outfit analysis
    │ - Trending colors: ["coral", "mint green"]
    │ - Trending styles: ["flowy", "bohemian"]
    │ - Trending accessories: ["straw bags", "wedges"]
    ↓
Lambda (format response with trend-aligned bundles)
    ↓
API Gateway (add headers)
    ↓
User Browser (display trend-aware bundles)
    │ Bundles now feature:
    │ - Products that match current trends
    │ - "Trending" badges on popular items
    │ - Higher relevance to social media styles
    │
    └──→ CloudWatch (log metrics)
         └──→ Analytics Dashboard (track usage)

┌─────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT DEPENDENCIES                              │
└─────────────────────────────────────────────────────────────────────────┘

Critical Path (must work):
1. API Gateway → Lambda → Bedrock → DynamoDB → Response

Supporting Services:
- S3 (images) - enhances results but not critical
- CloudWatch - monitoring only
- Analytics - business intelligence only

Failure Handling:
- API Gateway timeout → 504 error to user
- Lambda error → 500 error + CloudWatch alert
- Bedrock throttle → Retry with exponential backoff
- DynamoDB unavailable → Use cached data or fail gracefully

┌─────────────────────────────────────────────────────────────────────────┐
│                    SCALABILITY & PERFORMANCE                             │
└─────────────────────────────────────────────────────────────────────────┘

Current Capacity:
- API Gateway: 10,000 requests/second
- Lambda: 1,000 concurrent executions
- DynamoDB: 40,000 read capacity units
- Bedrock: 100 requests/minute (quota)

Bottlenecks:
1. Bedrock API rate limit (100/min)
   Solution: Request quota increase or implement queuing
   
2. Lambda cold starts (~2-3 seconds)
   Solution: Provisioned concurrency or keep-warm pings
   
3. DynamoDB scan performance
   Solution: Add GSI (Global Secondary Index) for faster queries

Future Optimizations:
- Add ElastiCache for product catalog caching
- Use Step Functions for multi-image processing
- Implement SQS queue for async processing
- Add CloudFront CDN for global distribution
