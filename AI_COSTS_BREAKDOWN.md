# AI Analysis Costs & Model Breakdown

## Current Configuration

### Model Used
**Claude Sonnet 4 (claude-sonnet-4-20250514)**
- Latest generation model (released May 2025)
- Best balance of quality, speed, and cost
- Excellent for business analysis tasks

## Cost Breakdown

### Pricing (as of 2025)
**Claude Sonnet 4 Pricing:**
- **Input tokens**: $3.00 per million tokens
- **Output tokens**: $15.00 per million tokens

### Per-Change Analysis Cost

**Typical Input per Change:**
- Change context (5 columns): ~150-200 tokens
- System prompt: ~100 tokens
- **Total input per change**: ~250-300 tokens

**Typical Output per Change:**
- AI-generated explanation: ~80-120 tokens (2-3 sentences)
- **Total output per change**: ~100 tokens

**Cost per Change:**
- Input: 300 tokens × $3.00 / 1M = **$0.0009**
- Output: 100 tokens × $15.00 / 1M = **$0.0015**
- **Total per change: ~$0.0024** (approximately 0.24 cents)

### File Processing Costs

#### Small File (50 changes)
- Total API calls: 50
- Input tokens: ~15,000 (50 × 300)
- Output tokens: ~5,000 (50 × 100)
- **Total cost: ~$0.12**

#### Medium File (100 changes)
- Total API calls: 100
- Input tokens: ~30,000
- Output tokens: ~10,000
- **Total cost: ~$0.24**

#### Large File (200 changes)
- Total API calls: 200
- Input tokens: ~60,000
- Output tokens: ~20,000
- **Total cost: ~$0.48**

#### Very Large File (500 changes)
- Total API calls: 500
- Input tokens: ~150,000
- Output tokens: ~50,000
- **Total cost: ~$1.20**

## Batched Processing Implementation

### Rate Limits (Current Free/Starter Tier)
- **Concurrent connections**: 5-10 simultaneous requests
- **Requests per minute**: 50 (typical)
- **Tokens per minute**: ~40,000

### Our Batched Processing
```javascript
// Processing in batches of 5 to avoid rate limits
Batch size: 5 concurrent requests
Delay between batches: 500ms
```

**Processing Time Examples:**
- 50 changes: ~5-10 seconds (10 batches)
- 100 changes: ~15-20 seconds (20 batches)
- 200 changes: ~30-40 seconds (40 batches)
- 500 changes: ~60-90 seconds (100 batches)

## Monthly Cost Estimates

### Usage Scenarios

**Light Usage (10 reports/month, 100 changes each)**
- Total changes analyzed: 1,000
- Monthly cost: **~$2.40**

**Medium Usage (30 reports/month, 150 changes each)**
- Total changes analyzed: 4,500
- Monthly cost: **~$10.80**

**Heavy Usage (100 reports/month, 200 changes each)**
- Total changes analyzed: 20,000
- Monthly cost: **~$48.00**

**Enterprise Usage (500 reports/month, 200 changes each)**
- Total changes analyzed: 100,000
- Monthly cost: **~$240.00**

## API Key & Billing

### Current Setup
```
API Key: sk-ant-api03-[REDACTED]
Stored in: .env file
Account type: Anthropic Console account
```

### Monitoring Usage
1. Visit: https://console.anthropic.com/
2. Navigate to: **Settings → Usage**
3. View:
   - Current month spend
   - Token usage breakdown
   - Request counts
   - Rate limit status

### Setting Up Budget Alerts
1. Go to: https://console.anthropic.com/settings/limits
2. Set monthly spending limit
3. Configure email alerts at thresholds (e.g., 50%, 80%, 100%)

## Optimization Opportunities

### 1. Reduce Token Usage
**Current Implementation:**
```javascript
// We use 5 columns for analysis
Subject, Reason/Benefit, Category, System, MOP
```

**To Reduce Costs (if needed):**
- Use only 3 most important columns
- Shorten system prompts
- Limit output to 1-2 sentences instead of 2-3

**Potential savings: 20-30% reduction**

### 2. Cache System Prompts (Future Feature)
Anthropic supports prompt caching:
- Cache the system instruction
- Reuse for multiple changes
- **Save ~50% on input token costs**

### 3. Alternative Models

**Claude Haiku (cheaper, faster)**
- Input: $0.25 per million tokens
- Output: $1.25 per million tokens
- **Cost per change: ~$0.0002** (1/10th the cost)
- Trade-off: Slightly lower quality explanations

**Cost comparison for 200 changes:**
- Sonnet 4: $0.48
- Haiku: $0.04
- **Savings: 90%**

## Error Handling & Fallbacks

### When AI Fails
```javascript
// Fallback to basic template
return `A ${category} change was performed on ${system}: ${subject}`;
```
- No API cost
- Basic but functional explanation
- Happens only on API errors

## ROI Analysis

### Value Provided
**Per Report:**
- Manual explanation writing time: ~1-2 min per change
- For 200 changes: **6-7 hours of manual work**
- AI cost for 200 changes: **$0.48**

**Time Savings:**
- Human hourly rate: $50-100/hour
- Manual cost: $300-700
- AI cost: $0.48
- **ROI: 62,400% - 145,700%**

## API Key Security

### Current Protection
✅ Stored in `.env` file (not in git)
✅ Server-side only (not exposed to client)
✅ Not logged in console output
✅ File permissions protected

### Best Practices
⚠️ **Never commit .env to git**
⚠️ **Rotate API keys periodically**
⚠️ **Monitor usage for anomalies**
⚠️ **Set spending limits in Anthropic Console**

## Switching Models (If Needed)

### To Change Model
Edit `server.js` line 168:
```javascript
// Current
model: "claude-sonnet-4-20250514"

// Switch to Haiku (cheaper)
model: "claude-3-5-haiku-20241022"

// Switch to Opus (highest quality, most expensive)
model: "claude-opus-4-20250514"
```

### Model Comparison

| Model | Quality | Speed | Input Cost | Output Cost | Best For |
|-------|---------|-------|------------|-------------|----------|
| **Claude Sonnet 4** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | $3/M | $15/M | **Current choice** - Best balance |
| Claude Haiku 3.5 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | $0.25/M | $1.25/M | High volume, cost-sensitive |
| Claude Opus 4 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | $15/M | $75/M | Premium quality needed |

## Recommendations

### For Your Use Case (Change Management Reports)

✅ **Keep Claude Sonnet 4**
- Excellent quality for business audience
- Fast enough for real-time use
- Cost is very reasonable ($0.48 per 200 changes)
- ROI is exceptional

### Consider Haiku If:
- Processing >1000 changes per report regularly
- Budget is extremely tight
- Speed is more important than explanation quality

### Consider Opus If:
- Explanations for executive/board level
- Regulatory compliance requires highest accuracy
- Cost is not a concern

## Monthly Budget Planning

### Recommended Budget Tiers

**Starter Tier: $10/month**
- ~40 reports with 100 changes each
- Perfect for small teams

**Professional Tier: $50/month**
- ~200 reports with 100 changes each
- Suitable for medium teams

**Enterprise Tier: $200-500/month**
- Unlimited practical usage
- Large organizations, high volume

## Summary

**Current Cost per Analysis:**
- **$0.0024 per change** (0.24 cents)
- **$0.48 per 200 changes**
- Extremely cost-effective compared to manual work

**Annual Cost Estimate:**
- 100 reports/month × 150 changes = 15,000 changes/month
- Monthly: ~$36
- **Annual: ~$432**

**Value Delivered:**
- Saves 6-7 hours per report
- Consistent, professional explanations
- Scalable to any volume
- **ROI: 60,000%+**

---

*Last Updated: February 2026*
*Model: Claude Sonnet 4 (claude-sonnet-4-20250514)*
