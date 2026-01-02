# GeoNews - Real-time Geopolitical Intelligence Dashboard

A full-stack application that aggregates news from RSS feeds, processes them with AI, and visualizes them on an interactive map.

## 🚀 Quick Deploy (Free)

### Backend Deployment (Railway)

1. **Go to [Railway.app](https://railway.app)** and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select this repository
4. Railway will auto-detect the configuration
5. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `PORT`: 8000
6. Click **"Deploy"**
7. Copy your Railway app URL (e.g., `https://your-app.up.railway.app`)

### Frontend Deployment (Vercel)

1. **Go to [Vercel.com](https://vercel.com)** and sign up with GitHub
2. Click **"Add New Project"**
3. Import this repository
4. Configure:
   - **Root Directory**: `client`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add environment variable:
   - `VITE_API_URL`: Your Railway backend URL (e.g., `https://your-app.up.railway.app`)
6. Click **"Deploy"**
7. Your app will be live at `https://your-project.vercel.app`

### Update Backend CORS

After deploying frontend, go back to Railway:
1. Add environment variable:
   - `FRONTEND_URL`: Your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Redeploy

✅ Done! Your app is now live and accessible from anywhere!

## 📱 Install on Phone

1. Open your Vercel URL in Chrome on Android
2. Wait for the "Install app" prompt
3. Tap **Install**
4. App icon will appear on your home screen!

## 🛠️ Local Development

### Backend
```bash
cd server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python run_server.py
```

### Frontend
```bash
cd client
npm install
npm run dev
```

## 📦 Tech Stack

**Backend:**
- Python, FastAPI
- SQLite (SQLAlchemy)
- OpenAI API (gpt-4o-mini)
- RSS Feed Parser
- APScheduler

**Frontend:**
- React + TypeScript + Vite
- Tailwind CSS
- Leaflet (OpenStreetMap)
- PWA Support

## 🔑 Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key
PORT=8000
FRONTEND_URL=https://your-frontend-url.vercel.app
```

### Frontend (.env)
```
VITE_API_URL=https://your-backend-url.up.railway.app
```

## 📰 News Sources

- **Israel Mainstream**: Ynet, Haaretz, Israel Defense, ITIC
- **Israel OSINT**: Abu Ali Express, Rotter, Nziv
- **International**: WSJ, The War Zone, ISW, Bellingcat, Al-Monitor

## 🌟 Features

- Real-time news aggregation (every 5 minutes)
- AI-powered geolocation and summarization
- Interactive map with clustering
- News list view with filters
- Daily recap by source
- Hebrew UI with RTL support
- Mobile-responsive PWA

## 📄 License

Personal use only
