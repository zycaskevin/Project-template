# AWS Lambda MCP Server 部署指南

**版本**: 1.0
**成本**: **$0/月** (免費 tier: 1M 次請求/月)
**部署時間**: <10 分鐘
**適用場景**: 自動壓縮與 Agent 交接文檔生成

---

## 🎯 快速開始

### 前置需求

1. **AWS 帳號** - [註冊 AWS 免費帳號](https://aws.amazon.com/free/)
2. **Node.js** - 安裝 Node.js 18+ (Serverless Framework 需要)
3. **AWS CLI** - 配置 AWS 憑證

```bash
# 安裝 AWS CLI (Windows)
pip install awscli

# 配置 AWS 憑證
aws configure
# 輸入:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

---

## 📦 安裝 Serverless Framework

```bash
# 全域安裝 Serverless Framework
npm install -g serverless

# 安裝 Python Requirements Plugin
npm install --save-dev serverless-python-requirements

# 驗證安裝
serverless --version
```

---

## 🚀 部署步驟

### Step 1: 準備專案

```bash
# 進入部署目錄
cd project-template/cloud-deployment/aws-lambda

# 安裝 Python 依賴 (本地測試用)
pip install -r requirements.txt
```

### Step 2: 部署到 AWS

```bash
# 部署到開發環境
serverless deploy --stage dev

# 或部署到生產環境
serverless deploy --stage prod
```

**預期輸出**:

```
✔ Service deployed to stack mcp-auto-compression-dev (142s)

endpoints:
  POST - https://abc123.execute-api.us-east-1.amazonaws.com/mcp
  GET  - https://abc123.execute-api.us-east-1.amazonaws.com/mcp/health
  POST - https://abc123.execute-api.us-east-1.amazonaws.com/compress
  POST - https://abc123.execute-api.us-east-1.amazonaws.com/handoff

functions:
  mcpServer: mcp-auto-compression-dev-mcpServer
  compressContext: mcp-auto-compression-dev-compressContext
  generateHandoff: mcp-auto-compression-dev-generateHandoff
```

### Step 3: 測試部署

```bash
# 測試健康檢查
curl https://YOUR_API_URL/mcp/health

# 測試壓縮功能
curl -X POST https://YOUR_API_URL/compress \
  -H "Content-Type: application/json" \
  -d '{"conversation": "User: Implement feature X\nAssistant: Created file src/feature.py"}'

# 測試 Handoff 生成
curl -X POST https://YOUR_API_URL/handoff \
  -H "Content-Type: application/json" \
  -d '{
    "from_agent": "research",
    "to_agent": "product",
    "compressed_context": {
      "sessionIntent": ["Implement dynamic compression"],
      "playByPlay": ["Created MCP server", "Deployed to AWS Lambda"]
    }
  }'
```

---

## 🔧 配置選項

### 環境變數 (serverless.yml)

```yaml
environment:
  TOKEN_THRESHOLD: 70        # Token 閾值 (%)
  CONTEXT_WINDOW: 200000     # 上下文視窗大小
  LOG_LEVEL: INFO            # 日誌級別
```

### 修改記憶體與超時

```yaml
provider:
  memorySize: 512   # 記憶體 (MB): 128, 256, 512, 1024, 2048
  timeout: 30       # 超時 (秒): 最大 30 (API Gateway 限制)
```

### 自訂 S3 Bucket 名稱

```yaml
custom:
  bucketName: my-custom-bucket-name  # 必須全球唯一
```

---

## 💰 成本估算

### AWS 免費 Tier (12 個月)

| 服務 | 免費額度 | 超額費用 |
|------|---------|---------|
| **Lambda** | 1M 次請求/月<br>400,000 GB-秒運算 | $0.20/百萬次請求<br>$0.0000166667/GB-秒 |
| **API Gateway** | 1M 次 HTTP API 調用/月 | $1.00/百萬次調用 |
| **S3** | 5 GB 儲存<br>20,000 GET 請求<br>2,000 PUT 請求 | $0.023/GB/月<br>$0.0004/千次 GET<br>$0.005/千次 PUT |

### 實際成本範例

**低強度使用** (10,000 次壓縮/月):
- Lambda: $0 (在免費額度內)
- API Gateway: $0 (在免費額度內)
- S3: $0 (在免費額度內)
- **總計: $0/月**

**中強度使用** (500,000 次壓縮/月):
- Lambda: $0 (在免費額度內)
- API Gateway: $0 (在免費額度內)
- S3: ~$0.10/月 (1 GB 儲存)
- **總計: ~$0.10/月**

**高強度使用** (5,000,000 次壓縮/月):
- Lambda: $0.80/月 (超額 4M 次)
- API Gateway: $4.00/月 (超額 4M 次)
- S3: ~$0.50/月 (10 GB 儲存)
- **總計: ~$5.30/月**

---

## 📊 監控與日誌

### 查看 CloudWatch 日誌

```bash
# 查看最近 50 條日誌
serverless logs -f mcpServer --tail

# 查看特定時間範圍
serverless logs -f mcpServer --startTime 1h

# 即時監控
serverless logs -f mcpServer --tail --interval 1000
```

### 查看 Lambda 指標

```bash
# AWS Console
https://console.aws.amazon.com/lambda

# 或使用 AWS CLI
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=mcp-auto-compression-dev-mcpServer \
  --start-time 2025-01-01T00:00:00Z \
  --end-time 2025-01-31T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

---

## 🔒 安全性最佳實踐

### 1. 啟用 API Key (推薦)

```yaml
# serverless.yml
provider:
  apiGateway:
    apiKeys:
      - mcp-compression-api-key
    usagePlan:
      quota:
        limit: 10000
        period: MONTH
      throttle:
        rateLimit: 100
        burstLimit: 200
```

### 2. 限制 CORS

```yaml
# serverless.yml
functions:
  mcpServer:
    events:
      - httpApi:
          path: /mcp
          method: POST
          cors:
            allowedOrigins:
              - https://your-domain.com
```

### 3. 加密 S3 Bucket

```yaml
# serverless.yml (已包含在配置中)
resources:
  Resources:
    CompressionBucket:
      Properties:
        BucketEncryption:
          ServerSideEncryptionConfiguration:
            - ServerSideEncryptionByDefault:
                SSEAlgorithm: AES256
```

---

## 🧹 移除部署

```bash
# 移除所有資源 (包含 S3 Bucket)
serverless remove --stage dev

# 或僅移除 Lambda 函數 (保留 S3)
aws lambda delete-function --function-name mcp-auto-compression-dev-mcpServer
```

---

## 🆘 常見問題

### Q1: 部署失敗 - "Access Denied"

**解決方案**:
```bash
# 檢查 AWS 憑證
aws sts get-caller-identity

# 確保 IAM 角色有以下權限:
# - AWSLambdaFullAccess
# - AmazonS3FullAccess
# - CloudWatchLogsFullAccess
```

### Q2: Lambda 超時

**解決方案**:
```yaml
# 增加超時時間 (serverless.yml)
provider:
  timeout: 30  # 最大 30 秒 (API Gateway 限制)
```

### Q3: S3 Bucket 已存在

**解決方案**:
```yaml
# 修改 Bucket 名稱 (serverless.yml)
custom:
  bucketName: mcp-compression-${self:provider.stage}-YOUR_UNIQUE_ID
```

---

## 🎯 下一步

1. ✅ **整合到 CLI Wrapper** - 修改 `claude-auto.sh` 調用雲端 MCP Server
2. ✅ **設定 CI/CD** - 使用 GitHub Actions 自動部署
3. ✅ **監控告警** - 設定 CloudWatch Alarms
4. ✅ **升級到 Cloudflare** - 更低延遲與成本 (Phase 2)

---

## 📚 參考資源

- [AWS Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
- [Serverless Framework Docs](https://www.serverless.com/framework/docs)
- [MCP Streamable HTTP Protocol](https://spec.modelcontextprotocol.io/specification/2025-03-26/architecture/)
- [AWS Serverless MCP Server](https://github.com/awslabs/aws-serverless-mcp-server)

---

**🎉 恭喜！您的 MCP Auto-Compression Server 已部署到 AWS Lambda！**

**總成本**: **$0/月** (免費 tier 完全足夠)
**可靠性**: ⭐⭐⭐⭐⭐ (AWS 管理基礎設施)
**擴展性**: ⭐⭐⭐⭐⭐ (自動擴展到百萬次請求)
