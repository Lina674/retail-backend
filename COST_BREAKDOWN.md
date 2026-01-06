# Cost Per Request - Outfit Bundle API

## Single Request Cost Breakdown

### Step-by-Step Pricing (1 outfit image, 1 API call)

---

#### 1️⃣ **User Request → API Gateway**
**Cost:** $0.0000035 per request
- API Gateway charges $3.50 per million requests
- **Per request: $0.0000035**

---

#### 2️⃣ **API Gateway → Lambda Function (validate, throttle)**
**Cost:** $0 (included in API Gateway cost)
- Validation and throttling are built-in features
- No additional charge

---

#### 3️⃣ **Lambda Function (decode images)**
**Cost:** $0.0000002 (~0.1 seconds compute)
- Lambda pricing: $0.0000166667 per GB-second
- Memory: 3GB
- Time: ~0.1 seconds for decoding
- Calculation: 3GB × 0.1s × $0.0000166667 = $0.000005
- **Per request: $0.000005**

---

#### 4️⃣ **Bedrock Claude (analyze outfit) - FIRST CALL**
**Cost:** $0.012 per image
- Claude 3.5 Sonnet pricing:
  - Input: $3 per million tokens (~1,000 tokens for image + prompt)
  - Output: $15 per million tokens (~200 tokens for analysis)
- Image processing: ~$0.01 per image
- Text tokens: ~$0.002
- **Per request: $0.012**

---

#### 4️⃣A **🆕 Lambda (trigger trend analysis) - IF TRENDS ENABLED**
**Cost:** $0.0000005 (~0.1 seconds compute)
- Time: ~0.1 seconds to invoke TrendComparison Lambda
- Calculation: 3GB × 0.1s × $0.0000166667 = $0.000005
- **Per request: $0.000005**

---

#### 4️⃣B **🆕 DynamoDB (check trend cache) - IF TRENDS ENABLED**
**Cost:** $0.00000025 per read
- DynamoDB read: $0.25 per million read requests
- Query: occasion + season + date
- **Per request: $0.00000025**

---

#### 4️⃣C **🆕 Pinterest API (fetch trends) - IF CACHE MISS**
**Cost:** $0.00 (free tier)
- Pinterest API: Free for up to 1,000 requests/day
- Search query: "summer garden party outfit 2025"
- Returns: 20 trending pins
- **Per request: $0.00**
- **Note:** 95% cache hit rate means only 5% of requests hit Pinterest

---

#### 4️⃣D **🆕 S3 (cache trending images) - IF CACHE MISS**
**Cost:** $0.000005 per request
- S3 PUT request: $0.005 per 1,000 requests
- Store 5 trending outfit images temporarily
- Calculation: 5 × $0.000001 = $0.000005
- **Per request: $0.000005**

---

#### 4️⃣E **🆕 Bedrock Claude (analyze trends) - SECOND CALL - IF CACHE MISS**
**Cost:** $0.015 per trend analysis
- Input: ~1,500 tokens (5 trending images + prompt)
- Output: ~300 tokens (trend summary)
- Calculation:
  - Input: 1,500 × $3/1M = $0.0045
  - Output: 300 × $15/1M = $0.0045
  - Image processing: 5 images × $0.002 = $0.01
- **Per request: $0.015**
- **Note:** 95% cache hit rate means only 5% of requests pay this cost

---

#### 4️⃣F **🆕 DynamoDB (cache trend results) - IF CACHE MISS**
**Cost:** $0.00000125 per write
- DynamoDB write: $1.25 per million write requests
- Write 1 trend analysis record with 24hr TTL
- **Per request: $0.00000125**

---

#### 5️⃣ **Lambda (query products)**
**Cost:** $0.0000005 (~0.2 seconds compute)
- Time: ~0.2 seconds to prepare query
- 🆕 Now includes trend context if enabled
- Calculation: 3GB × 0.2s × $0.0000166667 = $0.00001
- **Per request: $0.00001**

---

#### 6️⃣ **DynamoDB (get product catalog)**
**Cost:** $0.000025 per scan
- DynamoDB pricing: $0.25 per million read requests
- Scan operation: ~100 items read
- Read capacity: 100 items = 100 RCUs
- Calculation: 100 × $0.00000025 = $0.000025
- **Per request: $0.000025**

---

#### 7️⃣ **S3 (get image URLs)**
**Cost:** $0.0000004 per request
- S3 GET request: $0.0004 per 1,000 requests
- We don't download images, just get URLs from DynamoDB
- Minimal S3 API calls: ~1 request
- **Per request: $0.0000004**

---

#### 8️⃣ **Lambda (prepare product list)**
**Cost:** $0.0000015 (~0.3 seconds compute)
- Time: ~0.3 seconds to format product data
- Calculation: 3GB × 0.3s × $0.0000166667 = $0.000015
- **Per request: $0.000015**

---

#### 9️⃣ **Bedrock Claude (match products) - THIRD CALL (or SECOND if no trends)**
**Cost:** $0.008 per matching request (WITHOUT trends)
**Cost:** $0.010 per matching request (WITH trends)
- Input WITHOUT trends: ~2,000 tokens (outfit description + 40 products)
- Input WITH trends: ~2,500 tokens (outfit + 40 products + trend context)
- Output: ~500 tokens (3 bundles with reasoning)
- Calculation WITHOUT trends:
  - Input: 2,000 × $3/1M = $0.006
  - Output: 500 × $15/1M = $0.0075
  - **Total: $0.008**
- Calculation WITH trends:
  - Input: 2,500 × $3/1M = $0.0075
  - Output: 500 × $15/1M = $0.0075
  - **Total: $0.010**
- 🆕 Now considers trending colors, styles, and accessories when matching

---

#### 🔟 **Lambda (format response)**
**Cost:** $0.0000005 (~0.1 seconds compute)
- Time: ~0.1 seconds to format JSON
- Calculation: 3GB × 0.1s × $0.0000166667 = $0.000005
- **Per request: $0.000005**

---

#### 1️⃣1️⃣ **API Gateway (add headers)**
**Cost:** $0 (included in initial API Gateway cost)
- Response processing included in request cost

---

#### 1️⃣2️⃣ **User Browser (display bundles)**
**Cost:** $0 (client-side)
- No AWS charges for client-side rendering

---

#### 1️⃣3️⃣ **CloudWatch (log metrics)**
**Cost:** $0.0000005 per request
- CloudWatch Logs: $0.50 per GB ingested
- Log size: ~1KB per request
- Calculation: 1KB × $0.50/GB = $0.0000005
- **Per request: $0.0000005**

---

#### 1️⃣4️⃣ **Analytics Dashboard (track usage)**
**Cost:** $0.0000003 per request
- DynamoDB write: $1.25 per million write requests
- Write 1 item per request
- Calculation: 1 × $0.00000125 = $0.00000125
- **Per request: $0.00000125**

---

## 💰 TOTAL COST PER REQUEST (WITHOUT SOCIAL MEDIA TRENDS)

| Component | Cost per Request |
|-----------|------------------|
| API Gateway | $0.0000035 |
| Lambda (total compute) | $0.0000075 |
| Bedrock Claude (2 calls) | $0.020 |
| DynamoDB (read) | $0.000025 |
| S3 (URLs) | $0.0000004 |
| CloudWatch (logs) | $0.0000005 |
| Analytics (write) | $0.00000125 |
| **TOTAL** | **$0.0201** |

---

## 🆕 NEW FEATURE: SOCIAL MEDIA TREND COMPARISON

### How It Works Now
Trend analysis happens BEFORE product matching (steps 4A-4F), so the AI can suggest trend-aligned products in the bundles.

### Cost Impact by Cache Status

#### CACHE HIT (95% of requests)
When trend data is already cached (< 24 hours old):
- Lambda (check cache): $0.000005
- DynamoDB (read cache): $0.00000025
- Lambda (apply trends): $0.000005
- Bedrock (match with trends): +$0.002 (larger prompt)
- **Additional cost: $0.00201**

#### CACHE MISS (5% of requests)
When trend data needs to be fetched:
- Lambda (trigger trend fetch): $0.000005
- DynamoDB (check cache): $0.00000025
- Pinterest API (fetch trends): $0.00
- S3 (cache images): $0.000005
- Bedrock (analyze trends): $0.015
- DynamoDB (write cache): $0.00000125
- Lambda (apply trends): $0.000005
- Bedrock (match with trends): +$0.002
- **Additional cost: $0.01702**

#### WEIGHTED AVERAGE COST
- 95% × $0.00201 = $0.0019095
- 5% × $0.01702 = $0.000851
- **Average additional cost: $0.00276**

---

## 💰 TOTAL COST PER REQUEST (WITH SOCIAL MEDIA TRENDS)

### Scenario 1: Cache Hit (95% of requests)

| Component | Cost per Request |
|-----------|------------------|
| **ORIGINAL FEATURES** | |
| API Gateway | $0.0000035 |
| Lambda (decode images) | $0.000005 |
| Bedrock Claude (analyze outfit) | $0.012 |
| **TREND FEATURES (CACHED)** | |
| Lambda (check cache) | $0.000005 |
| DynamoDB (read trend cache) | $0.00000025 |
| Lambda (apply trends) | $0.000005 |
| **PRODUCT MATCHING** | |
| Lambda (query products) | $0.00001 |
| DynamoDB (product read) | $0.000025 |
| S3 (product URLs) | $0.0000004 |
| Lambda (prepare products) | $0.000015 |
| Bedrock Claude (match with trends) | $0.010 |
| Lambda (format response) | $0.000005 |
| **MONITORING** | |
| CloudWatch (logs) | $0.0000005 |
| Analytics (write) | $0.00000125 |
| **TOTAL (CACHE HIT)** | **$0.0227** |

### Scenario 2: Cache Miss (5% of requests)

| Component | Cost per Request |
|-----------|------------------|
| **ORIGINAL FEATURES** | |
| API Gateway | $0.0000035 |
| Lambda (decode images) | $0.000005 |
| Bedrock Claude (analyze outfit) | $0.012 |
| **TREND FEATURES (FETCH NEW)** | |
| Lambda (trigger trend fetch) | $0.000005 |
| DynamoDB (check cache - miss) | $0.00000025 |
| Pinterest API (fetch trends) | $0.00 |
| S3 (cache trend images) | $0.000005 |
| Bedrock Claude (analyze trends) | $0.015 |
| DynamoDB (write cache) | $0.00000125 |
| Lambda (apply trends) | $0.000005 |
| **PRODUCT MATCHING** | |
| Lambda (query products) | $0.00001 |
| DynamoDB (product read) | $0.000025 |
| S3 (product URLs) | $0.0000004 |
| Lambda (prepare products) | $0.000015 |
| Bedrock Claude (match with trends) | $0.010 |
| Lambda (format response) | $0.000005 |
| **MONITORING** | |
| CloudWatch (logs) | $0.0000005 |
| Analytics (write) | $0.00000125 |
| **TOTAL (CACHE MISS)** | **$0.0377** |

### Weighted Average Cost (WITH TRENDS)

**Average cost = (95% × $0.0227) + (5% × $0.0377) = $0.0235**

---

## 📊 Cost Breakdown by Category (WITH TRENDS - WEIGHTED AVERAGE)

**AI Processing (Bedrock - 3 calls):** $0.0225 (96% of cost)
- Outfit analysis: $0.012
- Trend analysis (5% of time): $0.00075
- Product matching with trends: $0.010

**Infrastructure (Lambda, API Gateway, etc.):** $0.001 (4% of cost)

**Cost increase from trends:** $0.0034 (17% increase with caching)

---

## 📊 Cost Breakdown by Category

**AI Processing (Bedrock):** $0.020 (99% of cost)
**Infrastructure (Lambda, API Gateway, etc.):** $0.0001 (1% of cost)

---

## 💵 Volume Pricing Comparison

### WITHOUT Social Media Trends

| Monthly Requests | Total Cost | Cost per Request |
|-----------------|------------|------------------|
| 100 | $2.01 | $0.0201 |
| 1,000 | $20.10 | $0.0201 |
| 10,000 | $201.00 | $0.0201 |
| 100,000 | $2,010.00 | $0.0201 |
| 1,000,000 | $20,100.00 | $0.0201 |

### WITH Social Media Trends (Weighted Average with 95% Cache Hit Rate)

| Monthly Requests | Total Cost | Cost per Request | Cost Increase |
|-----------------|------------|------------------|---------------|
| 100 | $2.35 | $0.0235 | +$0.34 (17%) |
| 1,000 | $23.50 | $0.0235 | +$3.40 (17%) |
| 10,000 | $235.00 | $0.0235 | +$34.00 (17%) |
| 100,000 | $2,350.00 | $0.0235 | +$340.00 (17%) |
| 1,000,000 | $23,500.00 | $0.0235 | +$3,400.00 (17%) |

**Note:** Costs remain linear because Bedrock (AI) is the dominant cost factor. The 24-hour caching strategy reduces trend costs by 83%.

---

## 🎯 Cost Optimization Opportunities

### 1. **Reduce Bedrock Calls** (Save 50%)
- Cache outfit analyses for similar images
- Use cheaper models for initial screening
- **Potential savings:** $0.010 per request

### 2. **Batch Processing** (Save 30%)
- Process multiple images in single Bedrock call
- Reduce per-image overhead
- **Potential savings:** $0.006 per request

### 3. **Pre-compute Product Matches** (Save 40%)
- Create product embeddings offline
- Use vector similarity instead of AI matching
- **Potential savings:** $0.008 per request

### 4. **Use Bedrock Batch API** (Save 50% on AI)
- Process requests in batches with 50% discount
- Trade-off: Adds latency (24-hour processing)
- **Potential savings:** $0.010 per request

---

## 💡 Recommended Pricing Strategy

### For End Users:

**Free Tier:**
- 10 requests/month free
- Cost to you: $0.20/month

**Basic Plan: $9.99/month**
- 500 requests/month
- Cost to you: $10.05/month
- Profit margin: -$0.06 (break even)

**Pro Plan: $29.99/month**
- 2,000 requests/month
- Cost to you: $40.20/month
- Profit margin: -$10.21 (loss leader)

**Enterprise: Custom pricing**
- Volume discounts
- Dedicated support
- Custom integrations

### Alternative: Pay-per-use
- $0.10 per outfit analysis
- 5x markup on cost
- Profit: $0.08 per request

---

## 📈 Break-Even Analysis

**To break even at $0.10 per request:**
- Need 5x markup on $0.02 cost
- Covers: infrastructure, support, development

**To be profitable:**
- Charge $0.15-0.25 per request
- Or bundle into subscription with other features
- Or monetize through affiliate commissions (Aldo product sales)

---

## 🔮 Future Cost Considerations

**If scaling to 1M requests/month:**

**Current architecture:** $20,100/month

**Optimized architecture:**
- Caching layer: -$10,000
- Batch processing: -$6,000
- Reserved capacity: -$2,000
- **Optimized cost:** $2,100/month (90% savings)

---

## 🎁 Hidden Costs Not Included

- **Data transfer:** ~$0.0001 per request (negligible)
- **CloudWatch storage:** ~$5/month (fixed)
- **Developer time:** Maintenance and updates
- **AWS support plan:** $29-15,000/month (optional)
- **Domain/SSL:** ~$12/year (if using custom domain)

---

## 💰 Real-World Example

**Scenario:** Fashion blog with 5,000 monthly users, each analyzing 2 outfits

**Usage:** 10,000 requests/month

**Costs:**
- AWS infrastructure: $201/month
- Developer maintenance: $500/month (part-time)
- **Total:** $701/month

**Revenue options:**
1. Subscription: 5,000 users × $4.99 = $24,950/month
2. Affiliate: 10% conversion × $100 avg order × 10% commission = $5,000/month
3. Ads: 5,000 users × $2 CPM = $10/month

**Profit potential:** $4,299 - $24,249/month

---

## 🏆 Bottom Line

### WITHOUT Social Media Trends
**Cost per request: $0.02**
- 99% is AI processing (Bedrock - 2 calls)
- 1% is infrastructure (Lambda, API Gateway, DynamoDB, S3)

### WITH Social Media Trends (Weighted Average)
**Cost per request: $0.0235** (with 95% cache hit rate)
- 96% is AI processing (Bedrock - 3 calls)
- 4% is infrastructure (Lambda, API Gateway, DynamoDB, S3)

**Most expensive component:** AWS Bedrock Claude AI
**Cheapest component:** S3 storage
**Biggest cost driver:** Trend analysis on cache miss (+$0.015, but only 5% of time)
**Caching benefit:** Saves $0.015 per request on 95% of requests = $0.01425 average savings

**Recommendation:** 
- **Basic tier:** $0.10-0.15 per request (outfit matching only)
- **Premium tier:** $0.15-0.20 per request (outfit matching + trend-aware suggestions)
- Or bundle into subscription model with affiliate revenue from product sales

**Value proposition for trends:** Users pay 17% more but get:
- Trend-aware product recommendations
- Products matched to current fashion trends
- Higher likelihood of on-trend purchases
- Bundles that align with what's popular on social media
- Better social proof and confidence in purchases
