# 🚂 Railway Deployment Guide

## 📋 Voraussetzungen

1. **Railway Account:** https://railway.app
2. **GitHub Repository:** Code muss auf GitHub gepusht sein
3. **OpenAI API Key:** Für LLM-Extraktion

---

## 🚀 Backend auf Railway deployen

### **Schritt 1: Neues Projekt erstellen**

1. Gehe zu https://railway.app/dashboard
2. Klicke auf **"New Project"**
3. Wähle **"Deploy from GitHub repo"**
4. Wähle dein Repository: `JonasDEMA/agentify_os`
5. Railway erkennt automatisch das Python-Projekt

### **Schritt 2: Root Directory setzen**

1. Gehe zu **Settings** → **Service Settings**
2. Setze **Root Directory** auf: `agents/company_research`
3. Railway wird jetzt nur diesen Ordner deployen

### **Schritt 3: Umgebungsvariablen setzen**

Gehe zu **Variables** und füge hinzu:

```
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1
```

**Wichtig:** Ersetze `your_openai_api_key_here` mit deinem echten OpenAI API Key!

**Wichtig:** Railway setzt automatisch `PORT` - nicht manuell setzen!

### **Schritt 4: Deploy starten**

1. Railway startet automatisch das Deployment
2. Warte bis Status **"Success"** zeigt
3. Kopiere die **Public URL** (z.B. `https://your-app.railway.app`)

---

## 🎨 Frontend auf Vercel deployen

### **Schritt 1: Vercel Projekt erstellen**

1. Gehe zu https://vercel.com/dashboard
2. Klicke auf **"Add New"** → **"Project"**
3. Importiere dein GitHub Repository
4. Setze **Root Directory** auf: `agents/company_research/ui`

### **Schritt 2: Build Settings**

Vercel erkennt automatisch Vite. Prüfe:

- **Framework Preset:** Vite
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### **Schritt 3: Umgebungsvariablen**

Füge hinzu:

```
VITE_API_URL=https://your-backend.railway.app
```

Ersetze `your-backend.railway.app` mit deiner Railway-URL!

### **Schritt 4: Deploy**

1. Klicke auf **"Deploy"**
2. Warte bis Deployment fertig ist
3. Kopiere die **Production URL** (z.B. `https://your-app.vercel.app`)

---

## 🔧 Backend CORS anpassen

Nach dem Frontend-Deployment musst du die CORS-Origins im Backend aktualisieren:

1. Gehe zu Railway → **Variables**
2. Füge hinzu:
   ```
   CORS_ORIGINS=https://your-app.vercel.app
   ```
3. Railway deployed automatisch neu

---

## ✅ Testen

1. **Backend Health Check:**
   ```
   https://your-backend.railway.app/health
   ```
   Sollte `{"status": "healthy"}` zurückgeben

2. **Backend API Docs:**
   ```
   https://your-backend.railway.app/docs
   ```
   Sollte Swagger UI zeigen

3. **Frontend:**
   ```
   https://your-app.vercel.app
   ```
   Sollte die UI zeigen

---

## 🐛 Troubleshooting

### **Backend startet nicht:**
- Prüfe Logs in Railway Dashboard
- Stelle sicher, dass `OPENAI_API_KEY` gesetzt ist
- Prüfe ob `requirements.txt` alle Dependencies enthält

### **Frontend kann Backend nicht erreichen:**
- Prüfe `VITE_API_URL` in Vercel
- Prüfe `CORS_ORIGINS` in Railway
- Öffne Browser DevTools → Network Tab

### **Database Fehler:**
- Railway hat ephemeral storage
- Für Production: Railway Postgres hinzufügen
- Oder: Supabase für persistente Datenbank

---

## 📊 Monitoring

**Railway Dashboard:**
- CPU/Memory Usage
- Request Logs
- Error Logs
- Deployment History

**Vercel Dashboard:**
- Build Logs
- Function Logs
- Analytics
- Performance Metrics

---

## 💰 Kosten

**Railway:**
- $5/month Starter Plan
- Oder: $0.000463/GB-hour (Pay as you go)

**Vercel:**
- Hobby Plan: Kostenlos
- Pro Plan: $20/month (für Production)

---

## 🔄 Auto-Deploy

Beide Plattformen deployen automatisch bei Git Push:

```bash
git add .
git commit -m "Update agent"
git push origin main
```

Railway und Vercel deployen automatisch!

