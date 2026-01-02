# 🔐 Secrets Configuration Guide

## ⚠️ Important: Never Commit Secrets to Git!

This guide shows you how to properly configure secrets for deployment without exposing them.

---

## 🏠 Local Development

Your secrets are stored in `/server/.env` (already in `.gitignore`):

```bash
# server/.env (NOT committed to Git)
OPENAI_API_KEY=sk-your-actual-key-here
PORT=8000
```

✅ This file is safe and stays on your computer only.

---

## 🚀 Production Deployment Secrets

### Railway (Backend)

**Step 1: Go to your Railway project**
1. Open [railway.app](https://railway.app)
2. Select your GeoNews project

**Step 2: Add PostgreSQL Database**
1. Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway will automatically create a PostgreSQL database
3. It will automatically set `DATABASE_URL` environment variable
4. ✅ **Free tier includes**: 512 MB storage, perfect for 30 days of news!

**Step 3: Add Environment Variables**
1. Click on your **backend service** (not the database)
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these secrets:

```
OPENAI_API_KEY=sk-your-actual-openai-key-here
PORT=8000
FRONTEND_URL=https://your-app.vercel.app
DATA_RETENTION_DAYS=30
```

**Note**: `DATABASE_URL` is automatically added by Railway when you add PostgreSQL!

**How to get OpenAI API Key:**
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click **"Create new secret key"**
3. Name it: `GeoNews Production`
4. Copy the key (starts with `sk-`)
5. Paste it into Railway as `OPENAI_API_KEY`

✅ Railway will:
- Keep your secrets encrypted
- Inject them as environment variables at runtime
- Never expose them in logs or code

---

### Vercel (Frontend)

**The frontend doesn't need the OpenAI key!** 

It only needs to know where the backend is:

1. Go to your Vercel project
2. **Settings** → **Environment Variables**
3. Add:

```
VITE_API_URL=https://your-railway-app.up.railway.app
```

Then update `client/vercel.json`:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-railway-app.up.railway.app/api/:path*"
    }
  ]
}
```

✅ Vercel proxies API requests to Railway, keeping secrets server-side only.

---

## 🔄 Updating Secrets

### Railway
1. Go to **Variables** tab
2. Click on the variable you want to change
3. Update the value
4. Railway will automatically redeploy

### Local Development
1. Edit `/server/.env`
2. Restart the server: `python run_server.py`

---

## ✅ Security Checklist

Before pushing to GitHub, verify:

- [ ] `.env` is in `.gitignore` ✓
- [ ] No `sk-` keys in any committed files ✓
- [ ] `geonews.db` is in `.gitignore` ✓
- [ ] Telegram session files are in `.gitignore` ✓
- [ ] `server/env.example` contains only placeholders ✓

**To verify:**
```bash
cd /Users/edenhayik/GeoNews
git status --ignored | grep -E "\.env|geonews\.db|session"
```

You should see them listed as ignored.

---

## 🚨 If You Accidentally Commit a Secret

**1. Revoke the key immediately:**
- OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → Delete the key

**2. Remove from Git history:**
```bash
# Remove the sensitive file from all commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch PATH/TO/FILE" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (be careful!)
git push origin --force --all
```

**3. Create a new key** and add it to Railway.

---

## 📖 Summary

| Location | How to Store Secrets |
|----------|---------------------|
| **Local Dev** | `/server/.env` (gitignored) |
| **Railway Backend** | Variables tab in Railway dashboard |
| **Vercel Frontend** | Environment Variables in Vercel settings |
| **GitHub Repo** | ❌ NEVER store secrets here |

Your secrets flow:
```
Local: .env file (your computer)
   ↓
Railway: Variables (Railway servers)
   ↓
App: Environment variables at runtime
```

✅ Secrets never leave secure environments!

---

## 🆘 Need Help?

- **Railway Docs**: [docs.railway.app/develop/variables](https://docs.railway.app/develop/variables)
- **Vercel Docs**: [vercel.com/docs/environment-variables](https://vercel.com/docs/environment-variables)
- **OpenAI Keys**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

