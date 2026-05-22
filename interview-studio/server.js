const http = require("node:http");
const https = require("node:https");
const fs = require("node:fs/promises");
const path = require("node:path");
const crypto = require("node:crypto");
const fsSync = require("node:fs");

// Load local .env file if it exists
try {
  const envPath = path.join(__dirname, ".env");
  if (fsSync.existsSync(envPath)) {
    const envContent = fsSync.readFileSync(envPath, "utf8");
    envContent.split(/\r?\n/).forEach((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) return;
      const index = trimmed.indexOf("=");
      if (index === -1) return;
      const key = trimmed.slice(0, index).trim();
      let val = trimmed.slice(index + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      process.env[key] = val;
    });
  }
} catch (err) {
  // Ignore env loading errors
}

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || "";
const GEMINI_MODEL = process.env.GEMINI_MODEL || "gemini-1.5-flash";

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

function normalizeGeminiContents(messages) {
  const contents = [];
  let lastRole = null;
  for (const m of messages) {
    if (!m.text || typeof m.text !== "string" || !m.text.trim()) continue;
    const role = m.role === "assistant" ? "model" : "user";
    if (role === lastRole) {
      if (contents.length > 0) {
        contents[contents.length - 1].parts[0].text += "\n" + m.text;
      }
    } else {
      contents.push({
        role: role,
        parts: [{ text: m.text }]
      });
      lastRole = role;
    }
  }
  
  if (contents.length > 0 && contents[0].role === "model") {
    contents.unshift({
      role: "user",
      parts: [{ text: "สวัสดีครับ/ค่ะ เริ่มบทสนทนา" }]
    });
  }
  return contents;
}

function callGeminiRaw(contents, systemInstruction = "", responseMimeType = "text/plain") {
  return new Promise((resolve, reject) => {
    if (!GEMINI_API_KEY) {
      return reject(new Error("กรุณาตั้งค่าสภาพแวดล้อม GEMINI_API_KEY ก่อนใช้งานฟังก์ชันนี้"));
    }

    const payload = {
      contents: contents,
      generationConfig: {
        temperature: 0.7,
      }
    };

    if (systemInstruction) {
      payload.systemInstruction = {
        parts: [{ text: systemInstruction }]
      };
    }

    if (responseMimeType === "application/json") {
      payload.generationConfig.responseMimeType = "application/json";
    }

    const postData = JSON.stringify(payload);

    const options = {
      hostname: "generativelanguage.googleapis.com",
      port: 443,
      path: `/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(postData)
      }
    };

    const req = https.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => body += chunk);
      res.on("end", () => {
        try {
          const json = JSON.parse(body);
          if (res.statusCode !== 200) {
            return reject(new Error(json.error?.message || `Gemini API returned status ${res.statusCode}`));
          }
          const text = json.candidates?.[0]?.content?.parts?.[0]?.text;
          if (!text) {
            return reject(new Error("ไม่ได้รับข้อความตอบกลับจาก Gemini API"));
          }
          resolve(text);
        } catch (e) {
          reject(new Error("การแปลงผลลัพธ์ของ Gemini ล้มเหลว: " + e.message));
        }
      });
    });

    req.on("error", (e) => reject(e));
    req.write(postData);
    req.end();
  });
}

async function handleChatFollowup(req, res) {
  try {
    const payload = await readJsonBody(req);
    const messages = payload.messages || [];
    const currentQuestion = payload.currentQuestion;

    if (!currentQuestion) {
      throw Object.assign(new Error("ไม่พบข้อมูลคำถามหลักที่กำลังใช้งาน"), { status: 400 });
    }

    const normalizedContents = normalizeGeminiContents(messages);

    const systemInstruction = `คุณเป็น AI ผู้สัมภาษณ์วิจัยของระบบ "ฉลากชัวร์" สัมภาษณ์เกี่ยวกับปัญหาและนวัตกรรมฉลากอาหารไทย
ให้วิเคราะห์บทสนทนาและตอบกลับในรูปแบบ JSON เสมอ:
{
  "response": "คำถามเจาะลึก 1 ข้อที่สั้น กระชับ สุภาพ (1-2 ประโยค) หรือข้อความกล่าวขอบคุณสั้นๆ เพื่อชวนย้ายไปข้อถัดไป",
  "shouldMoveToNext": true (เมื่อผู้สัมภาษณ์ตอบประเด็นครอบคลุมแล้ว หรือเมื่อผู้ใช้พิมพ์สั้นและแสดงเจตนาว่าไม่มีประเด็นเล่าเพิ่มแล้วในข้อนี้) หรือ false (ถ้าต้องการถามเจาะลึกเพิ่มในประเด็นย่อยที่ยังขาดหาย)
}

รายละเอียดหัวข้อปัจจุบัน:
รหัสข้อ: ${currentQuestion.id}
หัวข้อ: ${currentQuestion.title}
ประเด็นที่ควรเจาะลึก (Probes):
${(currentQuestion.probes || []).map((p, idx) => `[Probe ${idx}] ${p}`).join("\n")}
${currentQuestion.note ? `คำแนะนำเพิ่มเติม: ${currentQuestion.note}` : ""}

หลักการถามเจาะลึก:
- ถามทีละคำถามสั้นๆ เป็นกันเอง สุภาพ มีหางเสียง (ครับ/ค่ะ)
- ห้ามถามซ้ำในหัวข้อที่ผู้ให้สัมภาษณ์ตอบละเอียดแล้ว
- หากผู้ให้สัมภาษณ์ตอบครอบคลุม หรือแสดงเจตนาว่าไม่มีประเด็นอื่นแล้ว หรือต้องการข้าม ให้กำหนด shouldMoveToNext เป็น true`;

    const geminiResponseText = await callGeminiRaw(
      normalizedContents,
      systemInstruction,
      "application/json"
    );

    let result;
    try {
      result = JSON.parse(geminiResponseText.trim());
    } catch {
      result = {
        response: geminiResponseText.trim(),
        shouldMoveToNext: false
      };
    }

    sendJson(res, 200, result);
  } catch (error) {
    sendJson(res, error.status || 500, {
      error: error.message || "การเรียกใช้งาน Gemini API ล้มเหลว",
    });
  }
}

async function handleChatExtract(req, res) {
  try {
    const payload = await readJsonBody(req);
    const messages = payload.messages || [];

    if (messages.length === 0) {
      throw Object.assign(new Error("ไม่พบข้อความบันทึกบทสนทนาเพื่อทำการวิเคราะห์"), { status: 400 });
    }

    const transcript = messages
      .map(m => `${m.role === "assistant" ? "AI" : "Respondent"}: ${m.text}`)
      .join("\n");

    const prompt = `จากบทสนทนาการสัมภาษณ์เชิงลึกต่อไปนี้ ให้สกัดข้อมูลสำหรับแต่ละข้อคำถาม (q2-1 ถึง q3-6 ทั้งหมด 10 ข้อ) ออกมาในรูปแบบ JSON ตามโครงสร้างที่กำหนดเท่านั้น

บทสนทนาสัมภาษณ์:
"""
${transcript}
"""

---
โครงสร้างคำถามในโครงการวิจัย (มีทั้งหมด 10 ข้อ):
1. q2-1: กระบวนการจัดทำฉลากสินค้า ขั้นตอนใด ใครเกี่ยวข้อง มั่นใจได้อย่างไร
2. q2-2: ปัญหาอุปสรรคในการทำฉลากจริง (ตัวอย่างที่ยากที่สุด ผลกระทบ วิธีแก้)
3. q2-3: ความซับซ้อนของกฎหมาย (ประกาศ 445/450 จุดสับสน ช่องทางติดตาม การปรับตัว)
4. q2-4: วิธีตรวจฉลากก่อนพิมพ์ ( checklist คนช่วยตรวจ จุดที่เคยพลาด)
5. q3-1: รูปแบบนวัตกรรมที่ต้องการ (เอกสาร, แอป, เว็บ, ความง่าย, สื่อแนะนำ)
6. q3-2: ฟังก์ชันแรกที่อยากได้ ระดับคำอธิบายที่ต้องการ ช่วงเวลาที่นำมาใช้
7. q3-3: การร่างข้อความฉลากอัตโนมัติ (ช่วยลดเวลา/ปัญหาไหม จุดกรอกยาก โภชนาการ/คำเตือน)
8. q3-4: อุปกรณ์ที่สะดวก (คอม, มือถือ), การใช้งานออนไลน์/ออฟไลน์, ความเร็วที่ยอมรับได้
9. q3-5: AI ถ่ายรูปตรวจฉลากทันที (ผลต่อการทำงาน ความน่าเชื่อถือ/มั่นใจ การยืนยันโดยผู้เชี่ยวชาญ)
10. q3-6: ปัญหา/ความต้องการที่อยากให้ช่วยมากที่สุดเป็นอันดับ 1 และสิ่งที่ไม่ควรทำ

---
ให้ตอบกลับในรูปแบบ JSON ตามโครงสร้างนี้เท่านั้น (ห้ามมีข้อความเกริ่นหรือ markdown formatting อื่นๆ นอกเหนือจาก JSON ที่ถูกต้อง):
{
  "answers": {
    "q2-1": {
      "answer": "รายละเอียดคำตอบยาวที่เรียบเรียงและรวมคำตอบทุกเทิร์นเข้าด้วยกันให้อ่านเข้าใจง่ายและลึกซึ้ง (ถ้าไม่มีข้อมูลให้ปล่อยเป็นความว่าง \\"\\")",
      "summary": "สรุปประเด็นสำคัญเป็นข้อๆ (1-3 ข้อสั้นๆ เช่น \\"- ขั้นตอนออกแบบกราฟิกใช้เวลาค่อนข้างนาน\\")",
      "tags": ["กฎหมาย", "เวลา", "ต้นทุน", "ความรู้", "การตรวจฉลาก", "AI", "มือถือ", "ผู้เชี่ยวชาญ", "ข้อกังวล", "ข้อเสนอแนะ"], // เลือกเฉพาะแท็กที่เกี่ยวข้องตรงกับคำตอบในข้อนี้ (เว้นว่างได้เป็น [])
      "probes": [0, 2] // ดัชนีของประเด็นย่อย (Probes) ในข้อนั้นๆ ที่ตรวจพบว่าตอบแล้ว (0-indexed เช่น 0, 1, 2) โดยอิงตามรายการคำถามย่อยด้านล่าง
    },
    ...
  }
}

รายละเอียด Probes (ดัชนีคำถามย่อยสำหรับระบุใน probes array):
- q2-1: 0=ขั้นตอนทำฉลาก, 1=คนเกี่ยวข้อง/ประสานงาน, 2=วิธีมั่นใจว่าถูกต้อง, 3=เวลาหรือความล่าช้า
- q2-2: 0=ตัวอย่างปัญหาจริง, 1=ช่วงเวลาที่เกิดปัญหา, 2=ผลกระทบ, 3=วิธีแก้ปัญหา
- q2-3: 0=จุดสับสนในกฎหมาย, 1=ช่องทางการตามกฎหมาย, 2=การแก้ฉลากเดิมเมื่อกฎหมายเปลี่ยน
- q2-4: 0=วิธีตรวจสอบฉลากปัจจุบัน, 1=คนช่วยตรวจสอบ, 2=จุดที่เคยทำพลาด
- q3-1: 0=รูปแบบนวัตกรรม (เอกสาร/แอป/เว็บ), 1=ความยากง่ายที่กังวล, 2=สิ่งสนับสนุนเพิ่ม (คู่มือ/ตัวอย่าง)
- q3-2: 0=ฟังก์ชันแรกที่อยากได้, 1=ระดับอธิบาย (ถูก/ผิด หรือคำอธิบายการแก้), 2=ช่วงเวลาที่ใช้งาน
- q3-3: 0=ประหยัดเวลา/ลดปัญหาจากการร่าง, 1=จุดที่กรอกยากที่สุด, 2=อยากได้ระบบนำทางคำเตือน/กล่าวอ้างโภชนาการ
- q3-4: 0=อุปกรณ์ที่สะดวกใช้งาน, 1=การใช้ออนไลน์/ออฟไลน์, 2=ความเร็วตอบสนองที่ยอมรับได้
- q3-5: 0=ผลของ AI ถ่ายรูปต่อการทำงาน, 1=ความเชื่อมั่นใน AI, 2=ความต้องการคนตรวจเช็คซ้ำ
- q3-6: 0=ความต้องการแก้อันดับ 1, 1=ผลเมื่อระบบทำสำเร็จ, 2=สิ่งที่ไม่ควรมีในแอป/สิ่งกังวล`;

    const geminiResponseText = await callGeminiRaw(
      [{ role: "user", parts: [{ text: prompt }] }],
      "You are a helpful data extraction assistant that always outputs valid JSON.",
      "application/json"
    );

    let result;
    try {
      result = JSON.parse(geminiResponseText.trim());
    } catch (e) {
      throw new Error("การสกัดข้อมูลของ Gemini ไม่เป็นไปตามรูปแบบ JSON ที่คาดหวัง: " + e.message);
    }

    sendJson(res, 200, result);
  } catch (error) {
    sendJson(res, error.status || 500, {
      error: error.message || "การวิเคราะห์และดึงข้อมูลล้มเหลว",
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
    // Enable CORS for cross-origin requests (e.g. from GitHub Pages)
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS, HEAD");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

    if (req.method === "OPTIONS") {
      res.writeHead(204);
      res.end();
      return;
    }

    if (req.method === "POST" && req.url === "/api/chat/followup") {
      handleChatFollowup(req, res);
      return;
    }

    if (req.method === "POST" && req.url === "/api/chat/extract") {
      handleChatExtract(req, res);
      return;
    }

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
