# PyWebForge ΩX — Hostinger (Frontend) + Render (Backend) Deployment Kit

This kit includes everything to wire your existing Web GUI on Hostinger to your backend on Render, with env-driven CORS, API base URL injection, and exact env vars.

## Contents
- `.env.render.final` – Environment variables for your Render service
- `config.js` – Frontend file to set `window.API_BASE` to your Render URL
- `server_cors.patch` – Patch to make Flask CORS env-driven
- `app_js_api_base.patch` – Patch to ensure all frontend fetches use `API_BASE`
- `README_DEPLOY.md` – This guide

---

## 1) Summary of what’s handled (no logic changes)
✅ Env-driven CORS in Flask so only your Hostinger origin is allowed (`ALLOWED_ORIGINS`)
✅ `flask-sock` added to `requirements.txt` so imports resolve
✅ Frontend `fetch` calls prepend `API_BASE` so Hostinger → Render works
✅ `config.js` snippet to set `window.API_BASE` to your Render URL
✅ Verified frontend routes match backend blueprints
✅ No syntax changes that affect logic; only configuration + missing dependency

Hostinger (Frontend): https://covenant-firm.com/
Render (Backend): https://pywebforgex.onrender.com/

---

## 2) Apply patches to your repository (recommended)

In your repo root:

```bash
# Apply CORS patch to backend
git apply server_cors.patch

# Apply API base patch to frontend
git apply app_js_api_base.patch

# Commit changes
git add -A
git commit -m "Configure env-driven CORS and API_BASE for Hostinger/Render"
```

> If you don’t use git, open the files shown in the patches and replicate the changes manually.

---

## 3) Render (Backend) Setup

**Root Directory:** leave blank (repo root)

**Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

**Start Command:**
```bash
PYTHONPATH=src_original/public/pywebforge_omegax \
gunicorn -w 2 -k gthread -b 0.0.0.0:$PORT 'app.server:create_app()'
```

**Environment Variables:** (from `.env.render.final`)
- `PYWEBFORGE_SECRET` – already provided
- `PWF_API_KEY` – already provided
- `PWF_CSRF_SECRET` – already provided
- `ALLOWED_ORIGINS = https://covenant-firm.com`
- `CORS_CREDENTIALS = false`
- Optional: `OPENAI_API_KEY`, `OLLAMA_HOST`
- Optional resource limits (defaulted already)

**Note:** Render sets `PORT` automatically.

---

## 4) Hostinger (Frontend) Setup

Upload the following into `public_html/` on Hostinger:
- Your GUI files:
  - `src_original/public/pywebforge_omegax/app/templates/index.html` → `public_html/index.html`
  - `src_original/public/pywebforge_omegax/app/templates/cli.html` → `public_html/cli.html`
  - `src_original/public/pywebforge_omegax/app/static/` → `public_html/static/`
- `config.js` (from this kit) → `public_html/config.js`

Edit `index.html` to include (before `app.js`):
```html
<script src="/config.js"></script>
<script src="/static/js/app.js"></script>
```

`config.js` sets:
```html
window.API_BASE="https://pywebforgex.onrender.com";
```

---

## 5) Smoke test

After deploying backend to Render:
```bash
curl -i https://pywebforgex.onrender.com/health
# Expect: HTTP/1.1 200 OK  +  {"status":"ok"}

curl -i -X POST https://pywebforgex.onrender.com/api/graphs/deps -H 'Content-Type: application/json' -d '{"path":"/tmp"}'
# Expect: JSON success (or validation error if path missing)
```

Then open https://covenant-firm.com/ in your browser and check that API calls go to `https://pywebforgex.onrender.com/...` and succeed (DevTools → Network).

---

## 6) Troubleshooting

- **CORS errors**: ensure `ALLOWED_ORIGINS` on Render exactly matches `https://covenant-firm.com` (protocol + hostname). If you later add `www`, include both origins comma-separated.
- **404 on assets**: verify `public_html/static/...` exists and index references `/static/...`.
- **WebSockets**: supported by Render. Point your client to `wss://pywebforgex.onrender.com/<ws-path>` if/when you add them.
- **Cold starts/timeouts**: free tiers can be slow; consider scaling concurrency/plan if needed.

---

## 7) Security

- Keep the provided secrets private. Rotate anytime in Render by updating env vars.
- If you enable cookies/auth, set `CORS_CREDENTIALS=true` and configure cookies properly (`SameSite=None; Secure`), and add exact origins to allowlist.

---

## 8) Need help?

If anything fails, share the exact error from browser DevTools (Console/Network) or Render logs. This guide ensures the frontend and backend “speak” correctly without altering your app logic.
