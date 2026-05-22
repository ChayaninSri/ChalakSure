# Chalak Sure Interview Studio

## Run on a server

Use Node.js to serve the app and save interview files:

```bash
node server.js
```

Then open:

```text
http://127.0.0.1:5173
```

When the user clicks `ส่งข้อมูล`, the server saves:

- Markdown transcript: `data/interviews/YYYY-MM/*.md`
- Metadata: `data/interviews/YYYY-MM/*.json`
- Append-only index: `data/interviews/index.jsonl`

Opening `index.html` directly still works for drafting, but server-side saving only works when opened through the server URL.

## GitHub Pages

GitHub Pages can host the chat interface as a static website, but it cannot run `server.js` or write new `.md` files by itself. For production data collection, connect the static site to a separate backend by setting:

```html
<script>
  window.INTERVIEW_API_BASE_URL = "https://your-backend.example.com";
</script>
```

Place that script before `app.js`. The backend should expose `POST /api/interviews`.

## Gemini API

For a real AI interviewer, call Gemini from the backend, not directly from browser JavaScript, so the API key stays secret. Recommended environment variables:

```bash
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-3.5-flash
```
