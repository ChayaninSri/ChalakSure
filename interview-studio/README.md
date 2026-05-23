# Chalak Sure Interview Studio

## Production: Vercel + Supabase

This app can run fully on Vercel with Supabase Free:

- Vercel serves the web app and `/api/*` serverless functions.
- Gemini API is called only from the serverless functions, so the API key is not exposed in browser JavaScript.
- Supabase Database stores interview metadata, consent, respondent data, answers, and AI transcript JSON.
- Supabase Storage stores the exported Markdown `.md` interview file.

### 1. Create Supabase tables and storage

In Supabase Dashboard, open **SQL Editor**, paste and run:

```sql
-- supabase/schema.sql
```

Use the full SQL in `supabase/schema.sql`.

### 2. Vercel project settings

When importing this GitHub repo into Vercel, set:

```text
Root Directory: interview-studio
Framework Preset: Other
Build Command: leave empty
Output Directory: leave empty
Install Command: leave empty
```

### 3. Environment variables

Add these in **Vercel Dashboard > Project > Settings > Environment Variables**:

```bash
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_BUCKET=interviews
SUPABASE_INTERVIEWS_TABLE=interviews
```

Never put `SUPABASE_SERVICE_ROLE_KEY` in browser code. It must stay only in Vercel environment variables or local `.env`.

### 4. Local `.env`

For local testing, copy `.env.example` to `.env` and fill the same values. If Supabase variables are present, submissions save to Supabase. If they are not present, local `server.js` saves files to `data/interviews`.

## Run on a server

Use Node.js to serve the app and save interview files:

```bash
node server.js
```

Then open:

```text
http://127.0.0.1:5173
```

When the user clicks `ส่งข้อมูล` without Supabase variables, the local server saves:

- Markdown transcript: `data/interviews/YYYY-MM/*.md`
- Metadata: `data/interviews/YYYY-MM/*.json`
- Append-only index: `data/interviews/index.jsonl`

Opening `index.html` directly still works for drafting, but server-side saving only works when opened through the server URL.

## GitHub Pages

GitHub Pages can host the chat interface as a static website, but it cannot run `server.js`, Vercel functions, Gemini API calls, or write new `.md` files by itself. For production data collection, use Vercel + Supabase.

If you keep GitHub Pages only as a preview and want it to talk to a deployed Vercel API, set:

```html
<script>
  window.INTERVIEW_API_BASE_URL = "https://your-vercel-app.vercel.app";
</script>
```

Place that script before `app.js`.

## Gemini API

For a real AI interviewer, call Gemini from the backend, not directly from browser JavaScript, so the API key stays secret. Recommended environment variables:

```bash
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.5-flash
```
