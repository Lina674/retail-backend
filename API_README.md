# Outfit Bundle API

REST API for generating outfit bundles with shoes and handbags based on outfit images and context.

## Features

- Accepts multiple outfit images (base64 encoded)
- Considers age, gender, occasion, and season
- Returns 3 curated bundles (budget, mid-range, premium)
- Powered by AWS Bedrock (Claude) and DynamoDB

## API Endpoint

### POST /outfit-bundles

Generate outfit bundles based on images and context.

**Request Body:**
```json
{
  "images": ["base64_encoded_image1", "base64_encoded_image2"],
  "age": "25",
  "gender": "female",
  "occasion": "garden party",
  "season": "summer",
  "budget": 200
}
```

**Parameters:**
- `images` (required): Array of base64-encoded images
- `age` (optional): Age or age range (e.g., "25" or "20-30")
- `gender` (optional): Gender (e.g., "female", "male", "unisex")
- `occasion` (optional): Occasion (e.g., "wedding", "birthday", "casual")
- `season` (optional): Season (e.g., "summer", "winter", "spring", "fall")
- `budget` (optional): Budget in dollars (default: 200)

**Response:**
```json
{
  "outfits_count": 2,
  "context": {
    "age": "25",
    "gender": "female",
    "occasion": "garden party",
    "season": "summer",
    "budget": 200
  },
  "bundles": [
    {
      "bundle_number": 1,
      "bundle_name": "Garden Party Essential",
      "bundle_type": "budget",
      "match_score": 8,
      "total_cost": 119.94,
      "shoes": {
        "product_name": "Efemina",
        "price": 39.97,
        "product_id": "aldo_10021228282155",
        "product_url": "https://...",
        "image_url": "https://...",
        "reason": "Why it works..."
      },
      "handbag": {
        "product_name": "Aubrielax",
        "price": 34.97,
        "product_id": "aldo_10021727568171",
        "product_url": "https://...",
        "image_url": "https://...",
        "reason": "Why it works..."
      },
      "styling_note": "How to wear this bundle..."
    }
  ]
}
```

## Local Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Locally
```bash
python outfit_bundle_api.py
```

The API will start on `http://localhost:5000`

### Test Locally
```bash
python test_api.py
```

## Deployment to AWS

### Prerequisites
- AWS CLI configured
- Serverless Framework installed: `npm install -g serverless`
- Serverless Python Requirements plugin: `serverless plugin install -n serverless-python-requirements`

### Deploy
```bash
serverless deploy --stage prod
```

This will:
1. Package the Python code
2. Create Lambda function
3. Set up API Gateway
4. Configure IAM roles for DynamoDB, S3, and Bedrock access

### Get API URL
After deployment, Serverless will output the API Gateway URL:
```
endpoints:
  POST - https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/outfit-bundles
```

## Frontend Integration

### JavaScript/React Example
```javascript
async function getOutfitBundles(images, context) {
  const response = await fetch('https://your-api-url/outfit-bundles', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      images: images, // Array of base64 strings
      age: context.age,
      gender: context.gender,
      occasion: context.occasion,
      season: context.season,
      budget: context.budget
    })
  });
  
  return await response.json();
}

// Usage
const images = [base64Image1, base64Image2];
const context = {
  age: "25",
  gender: "female",
  occasion: "garden party",
  season: "summer",
  budget: 200
};

const bundles = await getOutfitBundles(images, context);
console.log(bundles);
```

### Convert Image to Base64 (Frontend)
```javascript
function imageToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Usage with file input
const fileInput = document.getElementById('imageInput');
const base64 = await imageToBase64(fileInput.files[0]);
```

## Architecture

```
Frontend (React/Vue/etc)
    ↓ POST /outfit-bundles
API Gateway
    ↓
AWS Lambda (Python)
    ↓
    ├→ AWS Bedrock (Claude) - Image analysis
    ├→ DynamoDB - Product metadata
    └→ S3 - Product images
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (missing images)
- `500`: Server error

Error response format:
```json
{
  "error": "Error message",
  "trace": "Stack trace (in development)"
}
```

## Rate Limiting

Consider implementing rate limiting on API Gateway for production use.

## CORS

CORS is enabled for all origins (`*`). Update in production to restrict to your frontend domain.
