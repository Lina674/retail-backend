$imageBytes = [Convert]::ToBase64String([IO.File]::ReadAllBytes("img\download.jpg"))

$requestBody = @{
    anthropic_version = "bedrock-2023-05-31"
    max_tokens = 2000
    messages = @(
        @{
            role = "user"
            content = @(
                @{
                    type = "image"
                    source = @{
                        type = "base64"
                        media_type = "image/jpeg"
                        data = $imageBytes
                    }
                }
                @{
                    type = "text"
                    text = "Analyze this outfit image and suggest what type of shoes would go well with it. Be specific about style, color, and type of shoes. Provide a concise description suitable for a Pinterest search query."
                }
            )
        }
    )
} | ConvertTo-Json -Depth 10

$requestBody | Out-File -FilePath "request.json" -Encoding utf8

aws bedrock-runtime invoke-model `
    --model-id anthropic.claude-3-5-sonnet-20241022-v2:0 `
    --body file://request.json `
    --region us-east-1 `
    output.json

$response = Get-Content output.json | ConvertFrom-Json
$response.content[0].text
