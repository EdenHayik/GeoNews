# 🔧 Railway Deployment Fix

## Problem
Railway build failed with: `pip: command not found`

## Solution
I've created 3 files to fix this:

### 1. `nixpacks.toml` ✅ (NEW FILE)
Tells Railway how to build your Python app properly.

### 2. `railway.json` ✅ (UPDATED)
Uses `uvicorn` command directly instead of custom script.

### 3. `Procfile` ✅ (UPDATED)
Backup start command configuration.

---

## 🚀 How to Deploy

### Option 1: Push via Script (Easiest)
```bash
cd /Users/edenhayik/GeoNews
chmod +x push_railway_fix.sh
./push_railway_fix.sh
```

### Option 2: Manual Git Commands
```bash
cd /Users/edenhayik/GeoNews

git add nixpacks.toml railway.json Procfile PUSH_COMPLETE.md
git commit -m "Fix Railway deployment configuration"
git push origin main
```

---

## 📋 After Pushing

1. **Go to Railway** → Your project
2. **It will auto-redeploy** (within 1-2 minutes)
3. **Check the build logs** - should show:
   ```
   ✅ Installing Python dependencies...
   ✅ Starting uvicorn server...
   ```

4. **If it still fails**, check that you have these **Environment Variables** set:
   ```
   OPENAI_API_KEY=sk-your-key-here
   PORT=8000
   DATA_RETENTION_DAYS=30
   ```

---

## 🗄️ Don't Forget PostgreSQL!

After the app deploys successfully:

1. In Railway, click **"+ New"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically:
   - Create the database
   - Set `DATABASE_URL` environment variable
   - Connect it to your backend

Your app will automatically use PostgreSQL instead of SQLite!

---

## ✅ Expected Build Output

After pushing, you should see in Railway logs:

```
Using Nixpacks
==============
✅ Setting up Python 3.13
✅ Installing PostgreSQL client
✅ Installing requirements.txt
✅ Starting: uvicorn app.main:app --host 0.0.0.0 --port $PORT

🚀 Server running on port 8000
📅 Scheduler started: RSS scraper every 5 minutes
📊 Database initialized
```

---

## 🆘 Troubleshooting

### If build still fails:

**Check 1: Python version**
- `runtime.txt` should say `python-3.13.0`

**Check 2: Requirements file**
- Make sure `server/requirements.txt` exists
- Should include `fastapi`, `uvicorn`, `sqlalchemy`, etc.

**Check 3: Start command**
- Railway should use: `cd server && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### If deployment succeeds but crashes:

**Check logs for:**
1. Missing `OPENAI_API_KEY` → Add it in Variables
2. Database connection error → Add PostgreSQL database
3. Import errors → Check all dependencies in requirements.txt

---

## 📝 What Changed

| File | Change | Why |
|------|--------|-----|
| `nixpacks.toml` | Created | Tells Railway to use Python 3.13 + PostgreSQL |
| `railway.json` | Simplified | Uses uvicorn directly (no custom script) |
| `Procfile` | Updated | Backup start command |

---

## 🎯 Summary

**Current Status:**
- ✅ Code is on GitHub
- ✅ Railway configuration fixed
- ⏳ Waiting for you to push
- ⏳ Then Railway will auto-deploy

**Next Steps:**
1. Run `./push_railway_fix.sh` OR manually push
2. Wait for Railway to redeploy (~2 minutes)
3. Add PostgreSQL database
4. Test your app!

---

**Need help?** Check Railway logs for specific errors.

