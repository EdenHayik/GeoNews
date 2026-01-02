# 🚀 Deployment Guide - GeoNews

## Step-by-Step Instructions

### 1️⃣ Deploy Backend to Railway (5 minutes)

**A. Sign Up & Create Project**
1. Go to [railway.app](https://railway.app)
2. Click **"Login"** → Sign in with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Search and select `GeoNews`

**B. Add PostgreSQL Database**
1. In your project, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway automatically creates the database and sets `DATABASE_URL`
4. ✅ Free tier: 512 MB storage (perfect for 30 days of news!)

**C. Configure Environment Variables**
1. Click on your **backend service** (not the database)
2. Go to **Variables** tab
3. Add these variables:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   PORT=8000
   DATA_RETENTION_DAYS=30
   ```
   
   **⚠️ Security Note**: Never commit API keys to Git!
   
   **How to get your OpenAI key**:
   - Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Create a new secret key
   - Copy it and paste into Railway
   
   📖 See [SECRETS.md](SECRETS.md) for detailed security guide.

**D. Get Your Backend URL**
1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy your URL (e.g., `geonews-production.up.railway.app`)
4. ✅ Save this URL - you'll need it for frontend!

---

### 2️⃣ Deploy Frontend to Vercel (5 minutes)

**A. Sign Up & Import Project**
1. Go to [vercel.com](https://vercel.com)
2. Click **"Login"** → Sign in with GitHub
3. Click **"Add New..."** → **"Project"**
4. Find and import `GeoNews`

**B. Configure Build Settings**
1. **Root Directory**: Click **"Edit"** → type `client`
2. **Framework Preset**: Vite (auto-detected)
3. Leave other settings as default

**C. Add Environment Variable**
1. Expand **"Environment Variables"**
2. Add:
   - **Name**: `VITE_API_URL`
   - **Value**: Your Railway URL from step 1C (e.g., `https://geonews-production.up.railway.app`)
3. Click **"Deploy"**

**D. Get Your Frontend URL**
- After deployment completes, you'll see your URL
- Example: `geonews-xyz123.vercel.app`
- ✅ Save this URL!

---

### 3️⃣ Update Backend CORS (2 minutes)

**Go back to Railway:**
1. Open your Railway project
2. Go to **Variables** tab
3. Add one more variable:
   ```
   FRONTEND_URL=https://your-frontend-url.vercel.app
   ```
   (Use the URL from step 2D)
4. Railway will automatically redeploy

---

### 4️⃣ Update Vercel Proxy (2 minutes)

1. In your code editor, open `/client/vercel.json`
2. Replace the `destination` URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://YOUR-RAILWAY-URL.up.railway.app/api/:path*"
       }
     ]
   }
   ```
3. Commit and push to GitHub
4. Vercel will auto-redeploy

---

## ✅ Test Your Deployment

1. Open your Vercel URL in Chrome
2. You should see the GeoNews app loading!
3. Check if news are loading on the map
4. If you see connection errors, double-check the URLs in Railway and Vercel

---

## 📱 Install on Phone

1. Open your Vercel URL on Android Chrome
2. Wait 2-3 seconds
3. You'll see **"Install GeoNews"** prompt
4. Tap **"Install"**
5. App appears on home screen! 🎉

---

## 🆓 Free Tier Limits

**Railway:**
- $5/month free credit
- ~500 hours/month
- Perfect for personal use!

**Vercel:**
- 100GB bandwidth/month
- Unlimited deployments
- Perfect for personal use!

---

## 🔧 Troubleshooting

### "Connection Error" on Frontend
- Check Railway logs for errors
- Verify `FRONTEND_URL` in Railway matches your Vercel URL
- Verify `/client/vercel.json` has correct Railway URL

### "Module Not Found" in Railway
- Make sure all dependencies are in `requirements.txt`
- Check Railway build logs

### RSS Feeds Not Updating
- Railway free tier may sleep after inactivity
- First request might take 30 seconds to wake up
- After wake, RSS scraper runs every 5 minutes

---

## 🎉 You're Done!

Your app is now:
- ✅ Live on the internet
- ✅ Free for personal use
- ✅ Installable on any phone
- ✅ Auto-updates when you push to GitHub

Enjoy your GeoNews app! 🗺️📰

