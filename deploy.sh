#!/bin/bash

echo "🚀 GeoNews Deployment Helper"
echo "=============================="
echo ""

# Check if git repo is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit - GeoNews app"
    echo "✅ Git repository initialized"
    echo ""
fi

# Check for GitHub remote
if ! git remote | grep -q "origin"; then
    echo "⚠️  No GitHub remote found!"
    echo "Please create a GitHub repository and run:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/GeoNews.git"
    echo "  git push -u origin main"
    echo ""
else
    echo "✅ GitHub remote configured"
    echo ""
    
    # Offer to push
    read -p "📤 Push to GitHub? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        echo "✅ Pushed to GitHub"
    fi
fi

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Deploy Backend (Railway):"
echo "   👉 https://railway.app"
echo "   - Sign in with GitHub"
echo "   - Deploy from GitHub repo"
echo "   - Add OPENAI_API_KEY and PORT=8000"
echo "   - Get your Railway URL"
echo ""
echo "2. Deploy Frontend (Vercel):"
echo "   👉 https://vercel.com"
echo "   - Sign in with GitHub"  
echo "   - Import project, set root to 'client'"
echo "   - Add VITE_API_URL (your Railway URL)"
echo "   - Get your Vercel URL"
echo ""
echo "3. Update CORS:"
echo "   - Go back to Railway"
echo "   - Add FRONTEND_URL (your Vercel URL)"
echo ""
echo "4. Update vercel.json:"
echo "   - Edit client/vercel.json"
echo "   - Replace destination with your Railway URL"
echo "   - Commit and push"
echo ""
echo "📱 Then install on your phone from the Vercel URL!"
echo ""
echo "📖 Full instructions: See DEPLOYMENT.md"
echo ""

