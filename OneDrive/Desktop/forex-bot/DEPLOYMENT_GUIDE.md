# Deploy Your Forex Bot to Railway (FREE!)

Follow these steps to deploy your trading bot to the cloud for FREE! 🚀

## Step 1: Create a GitHub Account (if you don't have one)

1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Create your account (it's free!)

## Step 2: Install Git on Your Computer

1. Download Git from: [git-scm.com/downloads](https://git-scm.com/downloads)
2. Install it (just click "Next" through everything)
3. Restart your command prompt after installation

## Step 3: Initialize Git in Your Project

Open your command prompt in the forex-bot folder and run:

```bash
git init
git add .
git commit -m "Initial commit - Forex Trading Bot"
```

## Step 4: Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `forex-trading-bot`
3. Make it **Private** (keep your code secret!)
4. Click "Create repository"

## Step 5: Push Your Code to GitHub

GitHub will show you commands - run these in your command prompt:

```bash
git remote add origin https://github.com/YOUR-USERNAME/forex-trading-bot.git
git branch -M main
git push -u origin main
```

(Replace YOUR-USERNAME with your actual GitHub username)

## Step 6: Sign Up for Railway

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with your GitHub account (easiest way!)
4. Give Railway permission to access your repositories

## Step 7: Deploy from GitHub

1. Click "New Project"
2. Choose "Deploy from GitHub repo"
3. Select your `forex-trading-bot` repository
4. Railway will automatically detect it's a Python app!
5. Click "Deploy Now"

Railway will start deploying... wait 2-3 minutes!

## Step 8: Add Environment Variables

Your bot needs the OANDA credentials! In Railway:

1. Click on your deployed project
2. Go to "Variables" tab
3. Click "Add Variable" and add these ONE BY ONE:

```
OANDA_ACCOUNT_ID = 101-001-29826722-001
OANDA_API_KEY = ababbd6259da598c47b012d1c09f39de-e362bdefee1df957b1ceab016a070d01
OANDA_ENVIRONMENT = practice
TRADINGVIEW_WEBHOOK_SECRET = your_secret_key_here
```

4. Click "Deploy" after adding all variables

## Step 9: Get Your Public URL

1. In Railway, go to "Settings" tab
2. Scroll to "Domains"
3. Click "Generate Domain"
4. You'll get a URL like: `forex-bot-production.up.railway.app`
5. **Copy this URL!**

## Step 10: Test Your Deployed Bot!

1. Open your browser
2. Go to: `https://your-railway-url.up.railway.app`
3. Your dashboard should appear!
4. Try making a trade!

## Step 11: Set Up TradingView Webhooks

Now you can use your Railway URL for TradingView alerts!

**Webhook URL:**
```
https://your-railway-url.up.railway.app/webhook
```

In TradingView:
1. Create an alert
2. Click "Webhook URL"
3. Paste your webhook URL
4. Set the message to:
```json
{
    "action": "buy",
    "instrument": "EUR_USD",
    "sl_pips": 20,
    "tp_pips": 40
}
```

## Step 12: Connect Your GoDaddy Domain (Optional)

Once it's working, you can point your GoDaddy domain to Railway:

1. In Railway, go to Settings → Domains
2. Click "Custom Domain"
3. Enter your domain (e.g., `trading.yourdomain.com`)
4. Railway will give you a CNAME record
5. Go to GoDaddy DNS settings
6. Add the CNAME record
7. Wait 10-60 minutes for DNS to update

## Troubleshooting

**If deployment fails:**
- Check the logs in Railway (click "Deployments" → "View Logs")
- Make sure all environment variables are set
- Make sure you pushed all your code to GitHub

**If you can't access the dashboard:**
- Make sure the deployment succeeded (green checkmark)
- Make sure the URL is correct
- Try adding `http://` or `https://` to the URL

**If trades don't execute:**
- Check that environment variables are correct
- Check the logs for errors
- Make sure EUR_USD is enabled in your config

---

## What You Get:

✅ FREE hosting forever (Railway free tier)
✅ Your bot runs 24/7
✅ Access from anywhere
✅ TradingView webhooks work!
✅ Professional deployment

## Limits on Free Tier:

- 500 hours/month runtime (plenty!)
- If you need more, upgrade for $5/month

---

**You're now a professional trader with a cloud-hosted trading bot!** 🎉
