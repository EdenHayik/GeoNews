#!/bin/bash

# Fix Railway Deployment - Commit and Push Script

cd /Users/edenhayik/GeoNews

echo "📦 Adding files..."
git add nixpacks.toml railway.json Procfile runtime.txt PUSH_COMPLETE.md RAILWAY_FIX.md push_railway_fix.sh

echo "💾 Committing changes..."
git commit -m "Fix Railway deployment: Use Python 3.11 (nixpacks compatible)

- Changed python313 to python311 in nixpacks.toml
- Updated runtime.txt to python-3.11.6
- Fixed uvicorn start command
- Fixes nixpacks 'undefined variable python313' error"

echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Done! Railway will now redeploy automatically."
echo ""
echo "Next steps:"
echo "1. Wait for Railway to rebuild (~2 minutes)"
echo "2. Add PostgreSQL database in Railway"
echo "3. Check logs for successful deployment"
