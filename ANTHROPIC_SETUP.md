# Anthropic API Setup Guide

## Overview

The ITIL 4 Change Enablement App now uses **Anthropic's Claude AI** to generate intelligent, context-aware explanations for each change record. This provides much more detailed and relevant explanations compared to the basic template-based approach.

## What Changed

### Before (Template-based)
- Generic explanations based on category templates
- Limited context awareness
- Same phrasing for similar changes

### After (AI-powered)
- **Intelligent analysis** of each change record
- **Context-aware explanations** that reference specific details
- **Layman's terms** automatically generated
- Considers all fields: subject, reason, system, impact, regions, etc.

## Getting Your Anthropic API Key

### Step 1: Sign Up for Anthropic

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Click "Sign Up" (or "Sign In" if you have an account)
3. Complete the registration process

### Step 2: Get Your API Key

1. Once logged in, navigate to **Settings** → **API Keys**
2. Click "Create Key" or "New API Key"
3. Give it a name (e.g., "ITIL Change App")
4. **Copy the API key** - it will look like: `sk-ant-api03-...`
5. **Save it immediately** - you won't be able to see it again!

### Step 3: Add API Key to Your App

1. Open the `.env` file in the project root:
   ```
   \\wsl.localhost\Ubuntu\home\laurencesher\projects\changereport\.env
   ```

2. Add your API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   PORT=3000
   ```

3. Save the file

4. **Restart the server**:
   - Stop the current server (Ctrl+C in the terminal)
   - Or kill the process using Task Manager
   - Run: `npm start`

### Step 4: Verify It's Working

1. Start the app: `npm start`
2. You should see:
   ```
   ITIL 4 Change Enablement App running at http://localhost:3000
   Open your browser and navigate to http://localhost:3000
   ```

3. **No warning message** means the API key is configured correctly
4. If you see: `WARNING: ANTHROPIC_API_KEY not found...` - check your `.env` file

## How It Works

### AI Explanation Generation

When you upload an Excel file:

1. The app reads all change records
2. For each record, it sends the following information to Claude AI:
   - ID
   - Category
   - Type of Change
   - Subject
   - Reason/Benefit
   - System/Application
   - Impact Description
   - Regions Affected
   - Pre-checks
   - Start/End Date and Time

3. Claude analyzes the data and generates a 2-3 sentence explanation in layman's terms

4. The explanation is stored with each record

### Example AI-Generated Explanations

**Input Data:**
```
Category: Radio Network
Subject: 5G Cell Tower Firmware Update
System: Cell Tower Management System
Impact: No impact - maintenance window
```

**AI Output:**
```
The cell tower management system received a firmware update
to improve 5G network performance. This maintenance was
performed during a scheduled window and had no impact on
customer service or network availability.
```

## Cost Considerations

### Pricing (as of 2024)

- **Model Used**: Claude 3.5 Sonnet
- **Cost per request**: ~$0.003 per change explanation
- **For 200 changes**: ~$0.60
- **Monthly estimates**:
  - 1,000 changes/month: ~$3
  - 5,000 changes/month: ~$15
  - 10,000 changes/month: ~$30

### Tips to Minimize Costs

1. **Batch Processing**: The app already processes explanations in parallel for efficiency
2. **Cache Results**: Once processed, explanations are stored with the data
3. **Review Mode**: If you re-upload the same file, you'll need new explanations (consider exporting to PDF)

### Free Tier

Anthropic offers:
- **Free trial credits** for new accounts
- Typically $5-10 in free credits
- Enough for ~1,000-3,000 change explanations

## Fallback Mode

If the API key is not configured or there's an error:

- The app **continues to work** with basic template explanations
- You'll see: `WARNING: ANTHROPIC_API_KEY not found in .env file. AI explanations will use fallback mode.`
- Explanations will be simpler but functional

## Troubleshooting

### "WARNING: ANTHROPIC_API_KEY not found"

**Solution:**
1. Check that `.env` file exists in project root
2. Verify `ANTHROPIC_API_KEY=` is set correctly
3. No spaces around the `=` sign
4. No quotes around the key
5. Restart the server

### "API Key Invalid" Error

**Solution:**
1. Double-check the key from Anthropic Console
2. Make sure you copied the entire key (starts with `sk-ant-`)
3. Generate a new key if needed
4. Update `.env` and restart

### Slow Upload Processing

**Cause:** AI explanations are generated for each record

**Solutions:**
- This is normal for large files (200+ records may take 30-60 seconds)
- The app processes in parallel for maximum speed
- Progress is shown in server console

### Rate Limiting

If you hit rate limits:
- Wait a few minutes
- Anthropic has generous rate limits (typically 50+ requests/minute)
- Contact Anthropic support to increase limits if needed

## Security Best Practices

### Protecting Your API Key

1. ✅ **DO**: Store in `.env` file (already in `.gitignore`)
2. ✅ **DO**: Keep `.env` file on your local machine only
3. ❌ **DON'T**: Commit `.env` to version control
4. ❌ **DON'T**: Share your API key
5. ❌ **DON'T**: Hardcode the key in source files

### Key Rotation

Rotate your API key periodically:
1. Generate new key in Anthropic Console
2. Update `.env` file
3. Delete old key from Anthropic Console
4. Restart server

## Support

### Anthropic Support
- Documentation: [https://docs.anthropic.com/](https://docs.anthropic.com/)
- Support: [https://console.anthropic.com/](https://console.anthropic.com/) (Help section)

### App-Specific Issues
- Check server console for error messages
- Verify `.env` configuration
- Ensure all npm packages are installed: `npm install`

---

## Quick Reference

```bash
# Install dependencies
npm install

# Set up API key
# Edit .env file and add: ANTHROPIC_API_KEY=your-key-here

# Start server
npm start

# Expected output
# ITIL 4 Change Enablement App running at http://localhost:3000
# Open your browser and navigate to http://localhost:3000
```

**Your changes will now have AI-powered explanations! 🚀**
