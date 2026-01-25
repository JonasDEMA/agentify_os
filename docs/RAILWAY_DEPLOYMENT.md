# 🚂 Railway Deployment Guide - CPA Server

## 📋 Schritt-für-Schritt Anleitung

### 1️⃣ Railway Account erstellen

1. Gehe zu https://railway.app
2. Klicke auf "Start a New Project"
3. Sign up mit GitHub

---

### 2️⃣ Neues Projekt erstellen

1. Klicke auf "New Project"
2. Wähle "Deploy from GitHub repo"
3. Autorisiere Railway für GitHub
4. Wähle dein Repository aus

---

### 3️⃣ Environment Variables setzen

Gehe zu **Settings → Variables** und füge hinzu:

```env
HOST=0.0.0.0
PORT=$PORT
DEBUG=false
DATABASE_URL=sqlite+aiosqlite:///./cpa_server.db
SECRET_KEY=cpa_server_secret_key_2025_change_in_production_xyz123
CORS_ORIGINS=["https://your-lovable-app.lovable.app","http://localhost:5173"]
UPLOAD_DIR=./uploads
SCREENSHOT_DIR=./uploads/screenshots
API_KEY_LENGTH=64
AGENT_TIMEOUT_SECONDS=300
```

⚠️ **Wichtig:**
- `PORT=$PORT` - Railway setzt automatisch den Port
- `CORS_ORIGINS` - Ersetze mit deiner Lovable URL
- `SECRET_KEY` - Generiere einen sicheren Random String

---

### 4️⃣ Build & Deploy

Railway erkennt automatisch:
- `railway.json` - Build & Deploy Konfiguration
- `pyproject.toml` - Poetry Dependencies

**Build Command:**
```bash
pip install poetry && poetry install --no-dev
```

**Start Command:**
```bash
poetry run python -m server.main
```

Klicke auf **Deploy** und warte auf den Build.

---

### 5️⃣ Datenbank seeden (Admin Token erstellen)

Nach dem ersten erfolgreichen Deploy:

1. Gehe zu **Deployments → Latest Deployment**
2. Klicke auf **Shell** (Terminal Icon)
3. Führe aus:
```bash
poetry run python server/db/seed.py
```

4. **Kopiere den Admin Token!** (wird nur einmal angezeigt)

**Beispiel Output:**
```
================================================================================
🔑 ADMIN TOKEN FOR LOVABLE UI
================================================================================

Agent ID: admin_lovable_ui

API Key:
cpa_admin_lovable_ui_2025_secure_token_zav2DtpZy2zTlaY-DSetzHr5jiHOfOKKo5_n-E_UkbA

================================================================================
```

---

### 6️⃣ Domain notieren

Railway generiert automatisch eine URL:

**Format:** `https://your-app-name.up.railway.app`

**Beispiel:** `https://cpa-server-production.up.railway.app`

Diese URL brauchst du für:
- Lovable UI (`VITE_CPA_API_URL`)
- Lokalen Agent (`server_url`)

---

### 7️⃣ API testen

Öffne im Browser:

**Health Check:**
```
https://your-app.railway.app/health
```

**Erwartete Antwort:**
```json
{"status": "healthy"}
```

**API Docs:**
```
https://your-app.railway.app/docs
```

**Agents Liste:**
```
https://your-app.railway.app/api/v1/agents/
```

**Erwartete Antwort:**
```json
[
  {
    "id": "admin_lovable_ui",
    "hostname": "lovable-ui",
    "os_name": "Web",
    "is_active": true,
    ...
  }
]
```

---

### 8️⃣ CORS konfigurieren

Nachdem du deine Lovable App erstellt hast:

1. Notiere die Lovable URL: `https://your-app.lovable.app`
2. Gehe zu Railway → **Settings → Variables**
3. Aktualisiere `CORS_ORIGINS`:
```env
CORS_ORIGINS=["https://your-app.lovable.app","http://localhost:5173"]
```
4. Railway deployed automatisch neu

---

### 9️⃣ Lokalen Agent verbinden

Auf deinem lokalen Rechner:

1. Öffne `.env` (oder erstelle sie)
2. Füge hinzu:
```env
CPA_SERVER_URL=https://your-app.railway.app
```

3. Oder direkt im Code:
```python
from agents.desktop_rpa.server_comm import AgentClient

client = AgentClient(server_url="https://your-app.railway.app")
await client.register(phone_number="+4915143233730")
```

4. Starte den Agent:
```bash
start.bat
```

5. Der Agent registriert sich automatisch beim Server

---

### 🔟 Monitoring

**Railway Dashboard:**
- **Deployments** - Siehe Build & Deploy Status
- **Logs** - Siehe Server Logs (API Requests, Errors)
- **Metrics** - Siehe CPU, Memory, Network Usage

**Nützliche Logs:**
```
INFO:     127.0.0.1:12345 - "GET /api/v1/agents/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:12345 - "POST /api/v1/logs/ HTTP/1.1" 200 OK
```

---

## ✅ Checklist

- [ ] Railway Account erstellt
- [ ] Projekt aus GitHub deployed
- [ ] Environment Variables gesetzt
- [ ] Build erfolgreich
- [ ] Datenbank geseeded (Admin Token kopiert)
- [ ] Domain notiert
- [ ] `/health` Endpoint funktioniert
- [ ] `/docs` Endpoint funktioniert
- [ ] `/api/v1/agents/` zeigt Admin Agent
- [ ] CORS mit Lovable URL konfiguriert
- [ ] Lokaler Agent verbunden
- [ ] Logs im Railway Dashboard sichtbar

---

## 🔒 Sicherheit

### Admin Token sicher speichern

**Für Lovable:**
```env
VITE_CPA_API_KEY=cpa_admin_lovable_ui_2025_secure_token_...
```

**Für lokale Entwicklung:**
- Speichere in `.admin_token.txt` (ist in `.gitignore`)
- Oder in Password Manager

### SECRET_KEY ändern

Generiere einen sicheren Random String:

**Python:**
```python
import secrets
print(secrets.token_urlsafe(64))
```

**Online:**
https://www.random.org/strings/

Setze in Railway → Variables:
```env
SECRET_KEY=<dein-random-string>
```

---

## 🐛 Troubleshooting

### Build schlägt fehl

**Problem:** `poetry install` schlägt fehl

**Lösung:**
1. Prüfe `pyproject.toml` - Alle Dependencies korrekt?
2. Railway Logs prüfen - Welcher Fehler?
3. Lokaler Test: `poetry install --no-dev`

### Server startet nicht

**Problem:** `poetry run python -m server.main` schlägt fehl

**Lösung:**
1. Railway Logs prüfen
2. Environment Variables prüfen (PORT, HOST)
3. Lokaler Test: `poetry run python -m server.main`

### CORS Fehler

**Problem:** Lovable UI kann nicht auf API zugreifen

**Lösung:**
1. Prüfe `CORS_ORIGINS` in Railway Variables
2. Füge Lovable URL hinzu: `["https://your-app.lovable.app"]`
3. Railway deployed automatisch neu

### Datenbank leer

**Problem:** Keine Agents in `/api/v1/agents/`

**Lösung:**
1. Railway Shell öffnen
2. `poetry run python server/db/seed.py` ausführen
3. Admin Token kopieren

---

## 📊 Kosten

**Railway Free Tier:**
- $5 Guthaben pro Monat
- Ausreichend für Development & Testing
- Automatisches Scaling

**Upgrade:**
- Hobby Plan: $5/Monat
- Pro Plan: $20/Monat

---

## 🎉 Fertig!

Dein CPA Server läuft jetzt auf Railway! 🚀

**Nächste Schritte:**
1. Lovable UI erstellen (siehe `LOVABLE_INTEGRATION_GUIDE.md`)
2. Lokalen Agent verbinden
3. Monitoring Dashboard nutzen

**URLs:**
- Server: `https://your-app.railway.app`
- Docs: `https://your-app.railway.app/docs`
- Health: `https://your-app.railway.app/health`

