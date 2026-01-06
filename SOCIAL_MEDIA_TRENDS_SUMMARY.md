# Social Media Trend Comparison - Feature Summary

## Overview
New Lambda function that analyzes social media trends (Pinterest) and compares user outfits against current fashion trends, providing personalized insights and trend alignment scores.

---

## Cost Impact

### Per Request Cost Breakdown (CORRECTED)

#### CACHE HIT (95% of requests)

| Step | Component | Cost | Details |
|------|-----------|------|---------|
| **ORIGINAL FEATURES** | | | |
| 1-3 | API Gateway + Lambda decode | $0.0000085 | Standard overhead |
| 4 | Bedrock (analyze outfit) | $0.012 | First AI call |
| **TREND FEATURES (CACHED)** | | | |
| 4A | Lambda (trigger trends) | $0.000005 | Invoke TrendComparison |
| 4B | DynamoDB (read cache) | $0.00000025 | Cache hit |
| 4C | Lambda (apply trends) | $0.000005 | Process cached data |
| **PRODUCT MATCHING** | | | |
| 5-8 | Lambda + DynamoDB + S3 | $0.0000354 | Get products |
| 9 | Bedrock (match WITH trends) | $0.010 | Larger prompt (+$0.002) |
| 10-14 | Lambda + monitoring | $0.00001625 | Format response |
| **TOTAL (CACHE HIT)** | | **$0.0227** | **+13% vs no trends** |

#### CACHE MISS (5% of requests)

| Step | Component | Cost | Details |
|------|-----------|------|---------|
| **ORIGINAL FEATURES** | | | |
| 1-3 | API Gateway + Lambda decode | $0.0000085 | Standard overhead |
| 4 | Bedrock (analyze outfit) | $0.012 | First AI call |
| **TREND FEATURES (FETCH NEW)** | | | |
| 4A | Lambda (trigger trends) | $0.000005 | Invoke TrendComparison |
| 4B | DynamoDB (check cache - miss) | $0.00000025 | Cache miss |
| 4C | Pinterest API | $0.00 | Free tier |
| 4D | S3 (cache images) | $0.000005 | Store 5 images |
| 4E | Bedrock (analyze trends) | $0.015 | Most expensive |
| 4F | DynamoDB (write cache) | $0.00000125 | Save for 24hrs |
| 4G | Lambda (apply trends) | $0.000005 | Process new data |
| **PRODUCT MATCHING** | | | |
| 5-8 | Lambda + DynamoDB + S3 | $0.0000354 | Get products |
| 9 | Bedrock (match WITH trends) | $0.010 | Larger prompt (+$0.002) |
| 10-14 | Lambda + monitoring | $0.00001625 | Format response |
| **TOTAL (CACHE MISS)** | | **$0.0377** | **+88% vs no trends** |

#### WEIGHTED AVERAGE

**Average cost = (95% × $0.0227) + (5% × $0.0377) = $0.0235**

**Cost increase from trends: +$0.0034 (17% increase with caching)**

---

## Cost Comparison

### Monthly Volume Pricing (CORRECTED with 95% Cache Hit Rate)

| Requests/Month | Without Trends | With Trends | Increase |
|----------------|----------------|-------------|----------|
| 100 | $2.01 | $2.35 | +$0.34 (17%) |
| 1,000 | $20.10 | $23.50 | +$3.40 (17%) |
| 10,000 | $201.00 | $235.00 | +$34.00 (17%) |
| 100,000 | $2,010.00 | $2,350.00 | +$340.00 (17%) |

**Key insight:** With 95% cache hit rate, trend feature only adds 17% to cost, not 109%. The 24-hour caching strategy makes trends economically viable.

---

## Architecture Integration

### Where It Hooks Into Existing System

```
EXISTING FLOW:
User Request → API Gateway → Lambda → Bedrock (analyze outfit) 
→ DynamoDB (products) → Bedrock (match products) → Response

NEW FLOW WITH TRENDS (CORRECTED):
User Request (include_trends=true) → API Gateway → Lambda 
→ Bedrock (analyze outfit)
→ 🆕 Lambda: TrendComparison (BEFORE product matching)
    → 🆕 DynamoDB (check cache)
    → 🆕 Pinterest API (fetch trends) [if cache miss]
    → 🆕 S3 (cache images) [if cache miss]
    → 🆕 Bedrock (analyze trends) [if cache miss]
    → 🆕 DynamoDB (cache results) [if cache miss]
    → 🆕 Return trend context
→ DynamoDB (products with trend filtering)
→ Bedrock (match products WITH trend awareness)
→ Response (trend-aware bundles)
```

### Integration Points

**1. Trigger Point (Step 18)**
- ⚠️ AFTER outfit analysis, BEFORE product matching
- Main Lambda invokes TrendComparison Lambda
- Passes: outfit description, occasion, season
- **Critical change:** Trends inform product selection, not just insights

**2. Data Flow**
- TrendComparison runs synchronously (blocks until complete)
- Returns trend context: colors, styles, accessories
- Main Lambda uses trends to filter/prioritize products
- Bedrock receives trend context in matching prompt

**3. Caching Layer**
- DynamoDB table: `trend-cache`
- Key: `{occasion}#{season}#{date}`
- TTL: 24 hours
- Reduces Pinterest API calls by 95%
- Cache hit rate: 95% (same occasion/season within 24hrs)

---

## New AWS Components

### Lambda Function: TrendComparison
- **Runtime:** Python 3.11
- **Memory:** 2GB
- **Timeout:** 2 minutes
- **Trigger:** Invoked by OutfitBundleAPI Lambda
- **Purpose:** Fetch and analyze social media trends

### DynamoDB Table: trend-cache
- **Purpose:** Cache trend analysis results
- **TTL:** 24 hours (auto-delete stale data)
- **Keys:** 
  - Partition key: `occasion#season` (e.g., "garden_party#summer")
  - Sort key: `date` (e.g., "2025-11-07")
- **Attributes:**
  - `trending_colors`: ["coral", "mint green"]
  - `trending_styles`: ["flowy", "bohemian"]
  - `trending_accessories`: ["straw bags", "wedges"]
  - `analysis_timestamp`: ISO datetime
  - `pinterest_pins`: [pin_urls]

### S3 Bucket: trend-images-cache
- **Purpose:** Temporary storage for trending outfit images
- **Lifecycle:** Delete after 7 days
- **Size:** ~5 images per trend query (~2MB)
- **Access:** Private (Lambda only)

### IAM Role Updates
- **Add to OutfitBundleAPIRole:**
  - `lambda:InvokeFunction` (call TrendComparison)
  - `dynamodb:PutItem` (write to trend-cache)
  - `dynamodb:GetItem` (read from trend-cache)
  - `s3:PutObject` (cache trend images)

---

## API Changes

### Request Format (NEW PARAMETER)

```json
{
  "images": ["base64_image"],
  "age": "25",
  "gender": "female",
  "occasion": "garden party",
  "season": "summer",
  "budget": 200,
  "include_trends": true  // 🆕 NEW PARAMETER
}
```

### Response Format (UPDATED)

```json
{
  "outfits_count": 1,
  "context": {...},
  "bundles": [
    {
      "bundle_number": 1,
      "bundle_name": "Trendy Garden Party Essential",
      "bundle_type": "budget",
      "match_score": 8,
      "total_cost": 119.94,
      "items": [
        {
          "category": "shoes",
          "product_name": "Efemina Wedge Sandals",
          "price": 39.97,
          "trending": true,  // 🆕 Trend badge
          "trend_reason": "Wedge sandals are trending for summer 2025 garden parties",  // 🆕
          "reason": "These nude wedges complement the floral print..."
        },
        {
          "category": "handbag",
          "product_name": "Straw Tote Bag",
          "price": 34.97,
          "trending": true,  // 🆕 Trend badge
          "trend_reason": "Straw bags are the #1 trending accessory for summer events",  // 🆕
          "reason": "Natural straw texture adds bohemian vibe..."
        }
      ],
      "styling_note": "This budget-friendly bundle aligns with current summer 2025 trends...",
      "trend_alignment": 85  // 🆕 Bundle trend score
    }
  ],
  "trend_context": {  // 🆕 NEW SECTION (for reference)
    "trending_colors": ["coral", "mint green", "white"],
    "trending_styles": ["flowy", "bohemian", "romantic"],
    "trending_accessories": ["straw bags", "wedge sandals", "statement earrings"],
    "pinterest_inspiration": [
      "https://pinterest.com/pin/123...",
      "https://pinterest.com/pin/456..."
    ]
  }
}
```

**Key difference:** Trends are now INTEGRATED into bundles, not just added as insights afterward.

---

## Performance Impact

### Response Time
- **Without trends:** 20-25 seconds
- **With trends (first request):** 35-40 seconds (+15s)
- **With trends (cached):** 22-27 seconds (+2s)

### Caching Benefits
- **Cache hit rate:** ~95% (same occasion/season within 24hrs)
- **Pinterest API calls saved:** 95%
- **Cost savings from cache:** ~$0.015 per cached request

---

## Business Value

### User Benefits
1. **Trend-aware recommendations** - Get products that match current fashion trends
2. **Social confidence** - Know you're buying what's popular on social media
3. **Better product selection** - AI prioritizes trending items in bundles
4. **Inspiration** - Links to trending Pinterest pins for styling ideas

### Retailer Benefits
1. **Higher engagement** - Trend-aware bundles feel more relevant
2. **Increased conversions** - Trending products sell 30-40% better
3. **Premium pricing** - Justify 17% price increase for trend feature
4. **Competitive advantage** - Unique AI-powered trend integration
5. **Inventory optimization** - Push trending items that will sell faster

---

## Pricing Strategy (UPDATED)

### Tiered Pricing Model

**Basic Tier: $0.10-0.15 per request**
- Outfit analysis
- Product matching
- 3 curated bundles
- No trend awareness

**Premium Tier: $0.15-0.20 per request** (only 17% more expensive)
- Everything in Basic
- 🆕 Trend-aware product selection
- 🆕 Trending badges on products
- 🆕 Trend alignment scores per bundle
- 🆕 Pinterest inspiration links

**Subscription Model**
- **Basic Plan:** $9.99/month (100 requests, no trends)
- **Pro Plan:** $14.99/month (100 requests with trends) - only $5 more!
- **Enterprise:** Custom pricing

**Value proposition:** For just 17% more cost, users get significantly better product recommendations that align with current fashion trends.

---

## Implementation Checklist

### Phase 1: Infrastructure Setup
- [ ] Create Lambda function: TrendComparison
- [ ] Create DynamoDB table: trend-cache (with TTL)
- [ ] Create S3 bucket: trend-images-cache (with lifecycle)
- [ ] Update IAM roles with new permissions
- [ ] Set up Pinterest API credentials

### Phase 2: Code Development
- [ ] Write TrendComparison Lambda handler
- [ ] Implement Pinterest API integration
- [ ] Build trend analysis logic
- [ ] Create caching mechanism
- [ ] Update main Lambda to invoke TrendComparison

### Phase 3: Testing
- [ ] Unit tests for trend analysis
- [ ] Integration tests with Pinterest API
- [ ] Cache hit/miss testing
- [ ] Performance benchmarking
- [ ] Cost validation

### Phase 4: Deployment
- [ ] Deploy TrendComparison Lambda
- [ ] Update OutfitBundleAPI Lambda
- [ ] Configure API Gateway (no changes needed)
- [ ] Set up CloudWatch alarms
- [ ] Monitor costs and performance

---

## Risk Mitigation

### Pinterest API Limits
- **Risk:** Free tier limited to 1,000 requests/day
- **Mitigation:** 24-hour caching reduces calls by 95%
- **Fallback:** Return bundles without trend data if API fails

### Increased Latency
- **Risk:** +15 seconds response time on first request
- **Mitigation:** Caching reduces to +2 seconds on subsequent requests
- **Alternative:** Make trend analysis async (return immediately, send trends via webhook)

### Cost Overruns
- **Risk:** Bedrock costs double with trend feature
- **Mitigation:** Make trends opt-in (include_trends=true)
- **Monitoring:** CloudWatch alarms on Bedrock spend

---

## Future Enhancements

### Phase 2 Features
1. **Multi-platform trends** - Add Instagram, TikTok APIs
2. **Trend forecasting** - Predict upcoming trends using ML
3. **Personalized trends** - Filter by user's style preferences
4. **Trend history** - Track how trends evolve over time

### Optimization Opportunities
1. **Batch processing** - Analyze multiple outfits in single Bedrock call
2. **Vector embeddings** - Use embeddings for faster trend matching
3. **CDN caching** - Cache trend images on CloudFront
4. **Async processing** - Use SQS queue for non-blocking trend analysis

---

## Success Metrics

### Technical KPIs
- Cache hit rate: >90%
- Response time (cached): <30 seconds
- Error rate: <1%
- Pinterest API usage: <1,000/day

### Business KPIs
- Premium tier adoption: >20%
- Conversion rate increase: +15%
- Average order value increase: +25%
- User engagement time: +40%

---

## Conclusion

The social media trend comparison feature adds significant value for users while doubling the per-request cost. The 24-hour caching strategy makes it economically viable, and the opt-in design allows users to choose between basic (cheap) and premium (trend-aware) experiences.

**Recommended approach:** Launch as premium feature at 2x price point, monitor adoption, and optimize based on user feedback.
