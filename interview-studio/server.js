const http = require("node:http");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");

const PORT = Number(process.env.PORT || 5173);
const HOST = process.env.HOST || "127.0.0.1";
const ROOT_DIR = __dirname;
const DATA_DIR = path.join(ROOT_DIR, "data", "interviews");
const MAX_BODY_BYTES = 8 * 1024 * 1024;

const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml; charset=utf-8",
};

function sendJson(res, status, payload) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
  });
  res.end(JSON.stringify(payload));
}

function safeSegment(value, fallback = "interview") {
  const cleaned = String(value || "")
    .normalize("NFKD")
    .replace(/[^\p{Letter}\p{Number}_-]+/gu, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80);
  return cleaned || fallback;
}

function timestampForFile(date = new Date()) {
  return date.toISOString().replace(/[:.]/g, "-");
}

function monthFolder(date = new Date()) {
  return date.toISOString().slice(0, 7);
}

async function readJsonBody(req) {
  const chunks = [];
  let size = 0;

  for await (const chunk of req) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) {
      throw Object.assign(new Error("ข้อมูลมีขนาดใหญ่เกินกำหนด"), { status: 413 });
    }
    chunks.push(chunk);
  }

  const raw = Buffer.concat(chunks).toString("utf8");
  try {
    return JSON.parse(raw || "{}");
  } catch {
    throw Object.assign(new Error("รูปแบบข้อมูลไม่ถูกต้อง"), { status: 400 });
  }
}

async function saveInterview(payload, options = {}) {
  if (!payload.markdown || typeof payload.markdown !== "string") {
    throw Object.assign(new Error("ไม่พบเนื้อหา Markdown สำหรับบันทึก"), { status: 400 });
  }

  const now = options.now || new Date();
  const dataDir = options.dataDir || DATA_DIR;
  const rootDir = options.rootDir || ROOT_DIR;
  const id = options.id || crypto.randomUUID();
  const respondentCode = safeSegment(payload.respondentCode);
  const folder = path.join(dataDir, monthFolder(now));
  const basename = `${timestampForFile(now)}-${respondentCode}-${id.slice(0, 8)}`;
  const markdownPath = path.join(folder, `${basename}.md`);
  const metadataPath = path.join(folder, `${basename}.json`);
  const indexPath = path.join(dataDir, "index.jsonl");

  await fs.mkdir(folder, { recursive: true });

  const metadata = {
    id,
    filename: `${basename}.md`,
    markdownPath,
    metadataPath,
    submittedAt: now.toISOString(),
    respondentCode: payload.respondentCode || "",
    elapsedMs: payload.elapsedMs || 0,
    respondent: payload.respondent || {},
    consent: payload.consent || {},
    interviewer: payload.interviewer || "",
    answerCount: payload.answers
      ? Object.values(payload.answers).filter(
          (answer) => answer?.answer?.trim() || answer?.summary?.trim(),
        ).length
      : 0,
    aiMessageCount: payload.ai?.messages?.length || 0,
  };

  await fs.writeFile(markdownPath, payload.markdown, "utf8");
  await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2), "utf8");
  await fs.appendFile(indexPath, `${JSON.stringify(metadata)}\n`, "utf8");

  return {
    ok: true,
    id,
    filename: metadata.filename,
    path: path.relative(rootDir, markdownPath),
    metadataPath: path.relative(rootDir, metadataPath),
    markdownPath,
    absoluteMetadataPath: metadataPath,
  };
}

async function handleInterviewSubmit(req, res) {
  try {
    const payload = await readJsonBody(req);
    const saved = await saveInterview(payload);

    sendJson(res, 201, {
      ok: true,
      id: saved.id,
      filename: saved.filename,
      path: saved.path,
      metadataPath: saved.metadataPath,
    });
  } catch (error) {
    sendJson(res, error.status || 500, {
      error: error.message || "บันทึกข้อมูลไม่สำเร็จ",
    });
  }
}

async function serveStatic(req, res) {
  const requestUrl = new URL(req.url, `http://${req.headers.host || "localhost"}`);
  let pathname;
  try {
    pathname = decodeURIComponent(requestUrl.pathname);
  } catch {
    res.writeHead(400, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Bad request");
    return;
  }

  const requested = pathname === "/" ? "/index.html" : pathname;
  const filePath = path.normalize(path.join(ROOT_DIR, requested));
  const rootBoundary = `${ROOT_DIR}${path.sep}`;

  if (filePath !== ROOT_DIR && !filePath.startsWith(rootBoundary)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  try {
    const content = await fs.readFile(filePath);
    const ext = path.extname(filePath).toLowerCase();
    res.writeHead(200, {
      "Content-Type": mimeTypes[ext] || "application/octet-stream",
      "Cache-Control": ext === ".html" ? "no-store" : "public, max-age=60",
    });
    res.end(content);
  } catch {
    res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    res.end("Not found");
  }
}

function createServer() {
  return http.createServer((req, res) => {
    if (req.method === "POST" && req.url?.startsWith("/api/interviews")) {
      handleInterviewSubmit(req, res);
      return;
    }

    if (req.method === "GET" || req.method === "HEAD") {
      serveStatic(req, res);
      return;
    }

    sendJson(res, 405, { error: "Method not allowed" });
  });
}

if (require.main === module) {
  const server = createServer();
  server.listen(PORT, HOST, () => {
    const address = server.address();
    const actualPort = typeof address === "object" && address ? address.port : PORT;
    console.log(`Interview Studio running at http://${HOST}:${actualPort}`);
    console.log(`Saved interviews folder: ${DATA_DIR}`);
  });
}

module.exports = {
  createServer,
  saveInterview,
  safeSegment,
};
