# 🚨 Quick Fix for Railway Error

## The Problem
```
error: undefined variable 'python313'
```

Railway's nixpacks doesn't support Python 3.13 yet.

## The Fix
Changed to **Python 3.11** (fully supported).

---

## 🚀 Push This Fix Now

**Run in your terminal:**

```bash
cd /Users/edenhayik/GeoNews
chmod +x push_railway_fix.sh
./push_railway_fix.sh
```

**OR manually:**

```bash
cd /Users/edenhayik/GeoNews

git add nixpacks.toml runtime.txt railway.json Procfile
git commit -m "Fix: Use Python 3.11 for Railway compatibility"
git push origin main
```

---

## ✅ After Pushing

1. **Railway will auto-redeploy** (~2 min)
2. **Build should succeed** ✅
3. **Then add PostgreSQL:**
   - Railway → "+ New" → "Database" → "PostgreSQL"

---

## 📋 What Changed

| File | Change |
|------|--------|
| `nixpacks.toml` | `python313` → `python311` |
| `runtime.txt` | `3.13.0` → `3.11.6` |

---

## Expected Result

```
✅ Setting up Python 3.11
✅ Installing PostgreSQL client  
✅ pip install -r requirements.txt
✅ Starting uvicorn server
🚀 Deployed!
```

---

**Ready? Run the script and Railway will work!** 🎉

