# Create Lambda Layer with dependencies
Write-Host "Creating Lambda Layer with dependencies..." -ForegroundColor Green

# Create layer directory
$layerDir = "python"
if (Test-Path $layerDir) {
    Remove-Item -Recurse -Force $layerDir
}
New-Item -ItemType Directory -Path $layerDir | Out-Null

# Install dependencies
Write-Host "Installing boto3..." -ForegroundColor Yellow
pip install boto3 -t $layerDir --upgrade

# Create zip
Write-Host "Creating layer zip..." -ForegroundColor Yellow
Compress-Archive -Path $layerDir -DestinationPath lambda_layer.zip -Force

# Upload layer
Write-Host "Uploading layer to AWS..." -ForegroundColor Yellow
$layerVersion = aws lambda publish-layer-version `
    --layer-name outfit-bundle-dependencies `
    --zip-file fileb://lambda_layer.zip `
    --compatible-runtimes python3.11 `
    --region us-east-1 | ConvertFrom-Json

$layerArn = $layerVersion.LayerVersionArn
Write-Host "Layer created: $layerArn" -ForegroundColor Green

# Update Lambda function to use layer
Write-Host "Updating Lambda function..." -ForegroundColor Yellow
aws lambda update-function-configuration `
    --function-name OutfitBundleAPI `
    --layers $layerArn `
    --region us-east-1

Write-Host "Done! Lambda function updated with dependencies layer." -ForegroundColor Green

# Cleanup
Remove-Item -Recurse -Force $layerDir
Remove-Item lambda_layer.zip
