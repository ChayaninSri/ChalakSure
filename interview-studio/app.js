const STORAGE_KEY = "chalak-sure-interview-studio-v1";
const API_BASE_URL = (window.INTERVIEW_API_BASE_URL || "").replace(/\/$/, "");

const tags = [
  "กฎหมาย",
  "เวลา",
  "ต้นทุน",
  "ความรู้",
  "การตรวจฉลาก",
  "AI",
  "มือถือ",
  "ผู้เชี่ยวชาญ",
  "ข้อกังวล",
  "ข้อเสนอแนะ",
];

const guide = [
  {
    id: "q2-1",
    section: "ส่วนที่ 2 สภาพปัญหาในการจัดทำฉลากอาหาร",
    short: "กระบวนการจัดทำฉลาก",
    title:
      "โดยทั่วไปแล้ว กระบวนการจัดทำฉลากสินค้าของท่านเป็นอย่างไร? ท่านเริ่มต้นจากตรงไหน และมีขั้นตอนอะไรบ้าง?",
    probes: [
      "ใครเป็นคนรับผิดชอบหลักในการจัดทำฉลาก? ต้องประสานงานกับใครบ้าง?",
      "ข้อมูลที่ใช้ทำฉลาก เช่น สูตร ส่วนประกอบ วัตถุเจือปน สารก่อภูมิแพ้ โภชนาการ หรือคำเตือน มาจากแหล่งใด และใครเป็นคนยืนยันความถูกต้อง?",
      "ท่านรู้ได้อย่างไรว่าฉลากที่ทำออกมานั้น 'ถูกต้อง' แล้ว?",
      "ในขั้นตอนทั้งหมด จุดไหนที่ท่านคิดว่ามีโอกาสเกิดความผิดพลาดมากที่สุด เพราะอะไร?",
      "ปกติใช้เวลานานแค่ไหนกว่าจะได้ฉลากสำเร็จ 1 ฉบับ?",
    ],
  },
  {
    id: "q2-2",
    section: "ส่วนที่ 2 สภาพปัญหาในการจัดทำฉลากอาหาร",
    short: "ปัญหาที่เกิดขึ้นจริง",
    title:
      "ท่านเคยพบปัญหาหรืออุปสรรคอะไรบ้างในการจัดทำฉลาก ให้เล่าเป็นตัวอย่างที่เกิดขึ้นจริง?",
    note:
      "หากผู้ตอบเล่าปัญหาทั่ว ๆ ไป ให้กระตุ้นด้วย: มีเรื่องอะไรที่ท่านรู้สึกว่ายากที่สุดไหม?",
    probes: [
      "ปัญหานั้นเกิดขึ้นตอนไหน? ช่วงออกแบบ ช่วงรวบรวมข้อมูล หรือช่วงที่เจ้าหน้าที่ตรวจ?",
      "หากย้อนกลับไปดูกรณีนั้น ท่านคิดว่าสาเหตุที่แท้จริงมาจากอะไร เช่น ความรู้ กฎหมายเปลี่ยน การสื่อสารกับกราฟิก/OEM ข้อมูลสูตรไม่ครบ เวลาไม่พอ หรือไม่มีคนตรวจซ้ำ?",
      "ส่งผลกระทบกับธุรกิจอย่างไร? เช่น ต้องพิมพ์ใหม่ เสียเวลา ถูกปรับ",
      "ปัญหานี้เคยเกิดซ้ำหรือไม่ ถ้าเกิดซ้ำ ท่านคิดว่าอะไรทำให้ยังแก้ไม่หาย?",
      "ตอนนั้นท่านแก้ปัญหาอย่างไร? ได้ผลไหม?",
    ],
  },
  {
    id: "q2-3",
    section: "ส่วนที่ 2 สภาพปัญหาในการจัดทำฉลากอาหาร",
    short: "ความซับซ้อนของกฎระเบียบ",
    title:
      "ท่านรู้สึกอย่างไรกับความซับซ้อนของกฎระเบียบฉลากอาหาร โดยเฉพาะประกาศฉบับ 450 และ 445 ที่มีผลใช้บังคับใหม่?",
    probes: [
      "ส่วนไหนของกฎหมายที่ท่านพบว่ายากหรือสับสนที่สุด? ขอตัวอย่างได้ไหม?",
      "เวลาต้องตีความประกาศหรือข้อกฎหมาย ท่านติดตรงเนื้อหากฎหมายเอง การหาเอกสาร การแปลเป็นภาษาปฏิบัติ หรือการไม่แน่ใจว่าข้อไหนใช้กับสินค้าของท่าน?",
      "ท่านรู้ได้อย่างไรว่ากฎหมายเปลี่ยนแปลง? ต้องตามข่าวสารจากช่องทางไหน?",
      "เมื่อกฎหมายเปลี่ยน ท่านต้องทำอะไรบ้างกับฉลากที่มีอยู่แล้ว?",
    ],
  },
  {
    id: "q2-4",
    section: "ส่วนที่ 2 สภาพปัญหาในการจัดทำฉลากอาหาร",
    short: "วิธีตรวจสอบก่อนพิมพ์",
    title:
      "ในการตรวจสอบฉลากของสินค้าใหม่ ท่านมีวิธีการตรวจสอบอย่างไรบ้าง ก่อนส่งพิมพ์จริง?",
    note:
      "จุดนี้สำคัญมาก: เปิดโอกาสให้ผู้ตอบพูดถึงช่องว่างในกระบวนการตรวจสอบที่แอปฯ จะเข้ามาอุด",
    probes: [
      "ท่านตรวจเองทั้งหมด หรือให้ใครช่วยตรวจ?",
      "ก่อนพิมพ์จริงมี checklist หรือเกณฑ์ตรวจซ้ำที่เป็นลายลักษณ์อักษรหรือไม่ ถ้าไม่มี ปกติใช้วิธีจำ ประสบการณ์ หรือถามคนอื่นอย่างไร?",
      "เคยพลาดจุดใดไปหรือไม่ แล้วรู้ตอนไหน? ก่อนพิมพ์ หลังพิมพ์ หรือหลังวางจำหน่าย",
      "ถ้าฉลากผิดหลุดไปจนพิมพ์หรือวางขายแล้ว ปกติหลุดเพราะไม่มีใครตรวจ จุดตรวจไม่ครอบคลุม หรือข้อมูลที่ใช้ตรวจไม่ครบ?",
      "ถ้าไม่แน่ใจว่าฉลากถูกต้องไหม ท่านจะทำอย่างไร? ถามใคร?",
    ],
  },
  {
    id: "q3-1",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "รูปแบบนวัตกรรมที่ต้องการ",
    title:
      "หากมีนวัตกรรมที่จะสามารถช่วยให้ท่านตรวจสอบและจัดทำฉลากได้ถูกต้องและง่ายมากขึ้น ท่านต้องการอยากให้นวัตกรรมดังกล่าวออกมาเป็นรูปแบบใด",
    probes: [
      "เช่น สื่อการสอนที่ช่วยให้เข้าใจการจัดทำฉลากมากขึ้น หรือโปรแกรมสำเร็จรูปที่ช่วยตรวจสอบและออกแบบฉลากได้",
      "ท่านกังวลเรื่องความยากหรือง่ายในการใช้งานหรือไม่ อย่างไร?",
      "ท่านอยากให้นวัตกรรมดังกล่าวเป็นแบบเอกสาร หรือเป็นโปรแกรมสำเร็จรูป?",
    ],
  },
  {
    id: "q3-2",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "ฟังก์ชันที่ต้องการก่อน",
    title:
      "ถ้าท่านมีนวัตกรรมที่ช่วยตรวจสอบฉลากและจัดทำได้ ท่านอยากให้มันทำอะไรได้บ้างเป็นสิ่งแรก ๆ?",
    probes: [
      "ท่านอยากให้มันตรวจอะไร? แค่บอกว่าถูก/ผิด หรืออยากได้คำอธิบายด้วยว่าต้องแก้ตรงไหนอย่างไร?",
      "ท่านจะใช้งานตอนไหน? ก่อนออกแบบ ระหว่างออกแบบ หรือหลังออกแบบเสร็จแล้ว?",
      "ถ้ามีระบบ AI ที่อ่านฉลากจากภาพถ่ายแล้วแจ้งข้อผิดพลาดได้เลย ท่านคิดว่าจะเป็นประโยชน์ไหม? เพราะอะไร?",
      "ฟังก์ชันที่เลือกนี้จะช่วยแก้สาเหตุของฉลากผิดข้อใดที่ท่านพบจริง?",
    ],
  },
  {
    id: "q3-3",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "ร่างข้อความบนฉลากอัตโนมัติ",
    title:
      "ถ้ามีนวัตกรรมที่ช่วยร่างข้อความบนฉลากให้อัตโนมัติ เพียงแค่ท่านกรอกข้อมูลสินค้า ท่านคิดว่าจะช่วยประหยัดเวลาหรือลดปัญหาได้มากน้อยแค่ไหน?",
    probes: [
      "ข้อมูลอะไรที่ท่านคิดว่ายากที่สุดในการกรอก? เช่น ส่วนประกอบ วัตถุเจือปน คำเตือน",
      "ท่านอยากให้ระบบแนะนำ 'คำเตือนที่ต้องมี' ตามประเภทสินค้าของท่านได้เลยไหม?",
      "ท่านอยากได้ฟังก์ชันตรวจสอบโภชนาการเพื่อรองรับการกล่าวอ้าง เช่น ไขมันต่ำ หรือไม่เติมน้ำตาล หรือไม่?",
    ],
  },
  {
    id: "q3-4",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "อุปกรณ์และรูปแบบใช้งาน",
    title:
      "ในเชิงปฏิบัติจริง ถ้ามีนวัตกรรมที่ช่วยตรวจสอบฉลาก ท่านจะใช้งานผ่านอุปกรณ์อะไร?",
    probes: [
      "ท่านสะดวกใช้บนโทรศัพท์มือถือ แท็บเล็ต หรือคอมพิวเตอร์มากกว่ากัน?",
      "ท่านอยากใช้แบบออนไลน์ตลอดเวลา หรือต้องการให้ใช้แบบออฟไลน์ได้ด้วย?",
      "ความเร็วในการตอบสนองของระบบสำคัญแค่ไหน? ท่านรอได้นานสูงสุดกี่วินาที?",
    ],
  },
  {
    id: "q3-5",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "AI ถ่ายรูปฉลากและอ้างอิงกฎหมาย",
    title:
      "ถ้ามีระบบ AI ที่สามารถถ่ายรูปฉลากแล้วบอกข้อผิดพลาดได้ทันที รวมถึงระบุว่าต้องแก้ไขอะไร และอ้างอิงข้อกฎหมายด้วย ท่านคิดว่าระบบนี้จะเปลี่ยนวิธีทำงานของท่านได้ไหม อย่างไร?",
    probes: [
      "ท่านมั่นใจในความถูกต้องของ AI มากน้อยแค่ไหน? มีเงื่อนไขอะไรที่ทำให้ท่านมั่นใจมากขึ้น?",
      "ท่านยังต้องการให้มีผู้เชี่ยวชาญมนุษย์ยืนยันผลอีกครั้งไหม หรือเชื่อ AI ได้เลย?",
      "ถ้าระบบแจ้งว่าฉลากของท่านมีปัญหา ท่านต้องการคำอธิบายเพิ่มเติมหรือวิธีแก้ไขด้วยไหม?",
    ],
  },
  {
    id: "q3-6",
    section: "ส่วนที่ 3 ความต้องการรูปแบบ/นวัตกรรมเพื่อสนับสนุนการจัดทำฉลาก",
    short: "สิ่งที่ควรช่วยมากที่สุด",
    title:
      "ในบรรดาปัญหาและความต้องการทั้งหมดที่ท่านเล่ามา สิ่งใดที่ท่านอยากให้นวัตกรรมหรือแอปพลิเคชันช่วยแก้ไขได้มากที่สุดเป็นอันดับ 1?",
    probes: [
      "จากประสบการณ์ของท่าน หากต้องจัดอันดับ 3 สาเหตุหลักที่ทำให้ฉลากอาหารไม่ถูกต้อง ท่านคิดว่าเกิดจากอะไรบ้าง และข้อใดสำคัญที่สุด?",
      "ถ้าแอปฯ ทำสิ่งนั้นได้สำเร็จ ชีวิตการทำงานของท่านจะเปลี่ยนแปลงไปอย่างไร?",
      "มีอะไรที่ท่านคิดว่าแอปฯ ไม่ควรทำ หรือไม่ต้องการให้มีฟังก์ชันนั้นเลย?",
      "ท่านมีข้อเสนอแนะอื่น ๆ ที่อยากให้ผู้พัฒนาทราบหรือไม่?",
    ],
  },
];

const coverageGuide = {
  "q2-1": [
    {
      id: "process",
      label: "ขั้นตอนการทำฉลาก",
      keywords: ["เริ่ม", "รวบรวม", "ออกแบบ", "ส่ง", "ตรวจ", "พิมพ์", "ขั้นตอน", "กระบวนการ"],
      followup:
        "ช่วยเล่าขั้นตอนตั้งแต่เริ่มทำฉลากจนพร้อมพิมพ์จริงแบบคร่าว ๆ ได้ไหมครับ/คะ ว่าปกติผ่านขั้นไหนบ้าง?",
    },
    {
      id: "people",
      label: "ผู้เกี่ยวข้อง",
      keywords: ["เจ้าของ", "กราฟิก", "ร้าน", "oem", "โรงงาน", "เจ้าหน้าที่", "คน", "ประสาน", "รับผิดชอบ"],
      followup:
        "ในกระบวนการนั้นมีใครบ้างที่เกี่ยวข้อง และแต่ละคนช่วยตัดสินใจหรือตรวจอะไรเป็นหลักครับ/คะ?",
    },
    {
      id: "data-source",
      label: "แหล่งข้อมูลและผู้ยืนยัน",
      keywords: ["สูตร", "ส่วนประกอบ", "วัตถุเจือปน", "สารก่อภูมิแพ้", "โภชนาการ", "คำเตือน", "ยืนยัน", "แหล่งข้อมูล"],
      followup:
        "ข้อมูลที่ใช้ทำฉลากมาจากแหล่งใด และมีใครเป็นคนยืนยันความถูกต้องของข้อมูลเหล่านั้นก่อนนำไปออกแบบครับ/คะ?",
    },
    {
      id: "confidence",
      label: "วิธีมั่นใจว่าถูกต้อง",
      keywords: ["ถูกต้อง", "กฎหมาย", "ประกาศ", "ตรวจ", "เช็ก", "มั่นใจ", "อย.", "เอกสาร"],
      followup:
        "ตอนที่ตัดสินใจว่าฉลากนี้ถูกต้องแล้ว ท่านใช้อะไรเป็นหลักในการเช็กหรือสร้างความมั่นใจครับ/คะ?",
    },
    {
      id: "risk-point",
      label: "จุดเสี่ยงผิดพลาด",
      keywords: ["เสี่ยง", "ผิดพลาด", "พลาด", "หลุด", "จุด", "ขั้นตอน", "โอกาส"],
      followup:
        "ในขั้นตอนทั้งหมด จุดไหนที่ท่านคิดว่ามีโอกาสเกิดความผิดพลาดมากที่สุด และเพราะอะไรครับ/คะ?",
    },
    {
      id: "time",
      label: "เวลา/ความล่าช้า",
      keywords: ["เวลา", "วัน", "ชั่วโมง", "นาน", "ล่าช้า", "รอ"],
      followup:
        "โดยเฉลี่ยฉลากหนึ่งชิ้นใช้เวลาประมาณเท่าไร และช่วงไหนที่มักทำให้เสียเวลามากที่สุดครับ/คะ?",
    },
  ],
  "q2-2": [
    {
      id: "incident",
      label: "ตัวอย่างปัญหาจริง",
      keywords: ["เคย", "ตัวอย่าง", "ครั้ง", "กรณี", "ปัญหา", "ผิด", "พลาด"],
      followup:
        "ขอเป็นเหตุการณ์จริงสักหนึ่งกรณีได้ไหมครับ/คะ ว่าตอนนั้นเกิดปัญหาอะไรขึ้น?",
    },
    {
      id: "stage",
      label: "ช่วงที่เกิดปัญหา",
      keywords: ["ออกแบบ", "รวบรวม", "ตรวจ", "พิมพ์", "วางขาย", "ก่อน", "หลัง"],
      followup:
        "ปัญหานั้นมักเกิดช่วงไหนของงานฉลาก เช่น ตอนรวบรวมข้อมูล ออกแบบ ตรวจ หรือหลังพิมพ์ครับ/คะ?",
    },
    {
      id: "root-cause",
      label: "สาเหตุที่แท้จริง",
      keywords: ["สาเหตุ", "เพราะ", "จริง", "ความรู้", "สื่อสาร", "ข้อมูล", "เวลา", "ตรวจซ้ำ", "oem"],
      followup:
        "ถ้าย้อนกลับไปดูกรณีนั้น ท่านคิดว่าสาเหตุที่แท้จริงมาจากอะไร เช่น ความรู้ กฎหมายเปลี่ยน การสื่อสาร ข้อมูลไม่ครบ เวลาไม่พอ หรือไม่มีคนตรวจซ้ำครับ/คะ?",
    },
    {
      id: "impact",
      label: "ผลกระทบ",
      keywords: ["เสีย", "พิมพ์ใหม่", "ต้นทุน", "เงิน", "เวลา", "ปรับ", "ล่าช้า", "กระทบ"],
      followup:
        "ปัญหานั้นส่งผลต่อธุรกิจอย่างไรบ้าง เช่น เวลา ต้นทุน การขาย หรือความมั่นใจครับ/คะ?",
    },
    {
      id: "recurrence",
      label: "การเกิดซ้ำ",
      keywords: ["ซ้ำ", "อีก", "แก้ไม่หาย", "เหมือนเดิม", "บ่อย", "ประจำ"],
      followup:
        "ปัญหานี้เคยเกิดซ้ำหรือไม่ ถ้าเกิดซ้ำ ท่านคิดว่าอะไรทำให้ยังแก้ไม่หายครับ/คะ?",
    },
    {
      id: "solution",
      label: "วิธีแก้ปัญหา",
      keywords: ["แก้", "ปรึกษา", "ถาม", "ปรับ", "เปลี่ยน", "ทำใหม่"],
      followup:
        "ตอนนั้นท่านแก้ปัญหาอย่างไร และวิธีนั้นช่วยได้มากน้อยแค่ไหนครับ/คะ?",
    },
  ],
  "q2-3": [
    {
      id: "difficult-law",
      label: "จุดที่สับสน",
      keywords: ["สับสน", "ยาก", "ไม่เข้าใจ", "ประกาศ", "450", "445", "กฎหมาย"],
      followup:
        "ส่วนไหนของกฎระเบียบที่ทำให้สับสนหรือไม่แน่ใจมากที่สุดครับ/คะ?",
    },
    {
      id: "interpretation-barrier",
      label: "อุปสรรคการตีความ",
      keywords: ["ตีความ", "หาเอกสาร", "แปล", "ปฏิบัติ", "ใช้กับ", "สินค้า", "ไม่แน่ใจ"],
      followup:
        "เวลาต้องตีความประกาศ ท่านติดตรงเนื้อหากฎหมาย การหาเอกสาร การแปลเป็นภาษาปฏิบัติ หรือการไม่แน่ใจว่าข้อไหนใช้กับสินค้าของท่านครับ/คะ?",
    },
    {
      id: "source",
      label: "ช่องทางติดตามกฎหมาย",
      keywords: ["ข่าว", "ช่องทาง", "ไลน์", "เว็บ", "อบรม", "เจ้าหน้าที่", "อย.", "ติดตาม"],
      followup:
        "ปกติท่านรู้ข่าวว่ากฎหมายหรือประกาศเปลี่ยนจากช่องทางไหนครับ/คะ?",
    },
    {
      id: "change-action",
      label: "สิ่งที่ต้องทำเมื่อกฎหมายเปลี่ยน",
      keywords: ["แก้", "เปลี่ยน", "ฉลากเดิม", "พิมพ์ใหม่", "ปรับ", "ทำใหม่"],
      followup:
        "เมื่อกฎหมายเปลี่ยน ท่านต้องจัดการกับฉลากเดิมอย่างไรบ้างครับ/คะ?",
    },
  ],
  "q2-4": [
    {
      id: "check-method",
      label: "วิธีตรวจปัจจุบัน",
      keywords: ["ตรวจ", "เช็ก", "checklist", "เอกสาร", "เทียบ", "ดูเอง"],
      followup:
        "ก่อนส่งพิมพ์จริง ท่านตรวจฉลากด้วยวิธีไหนหรือใช้เอกสารอะไรช่วยครับ/คะ?",
    },
    {
      id: "checklist",
      label: "ระบบตรวจซ้ำ/checklist",
      keywords: ["checklist", "เช็กลิสต์", "เกณฑ์", "ลายลักษณ์", "เอกสาร", "จำ", "ประสบการณ์"],
      followup:
        "ก่อนพิมพ์จริงมี checklist หรือเกณฑ์ตรวจซ้ำที่เป็นลายลักษณ์อักษรหรือไม่ ถ้าไม่มี ปกติใช้วิธีจำ ประสบการณ์ หรือถามคนอื่นอย่างไรครับ/คะ?",
    },
    {
      id: "checker",
      label: "คนช่วยตรวจ",
      keywords: ["เอง", "เจ้าหน้าที่", "ผู้เชี่ยวชาญ", "กราฟิก", "โรงงาน", "ถาม", "ช่วย"],
      followup:
        "ปกติท่านตรวจเองทั้งหมด หรือมีใครช่วยตรวจ/ให้คำปรึกษาก่อนพิมพ์ครับ/คะ?",
    },
    {
      id: "missed",
      label: "จุดที่เคยพลาด",
      keywords: ["พลาด", "ผิด", "แก้", "หลังพิมพ์", "วางขาย", "ไม่แน่ใจ"],
      followup:
        "เคยมีจุดที่ตรวจไม่เจอจนต้องแก้ภายหลังไหมครับ/คะ ถ้ามี จุดนั้นคืออะไร?",
    },
    {
      id: "escape-cause",
      label: "สาเหตุที่หลุดก่อนพิมพ์/วางขาย",
      keywords: ["หลุด", "ไม่มีใคร", "ไม่ครอบคลุม", "ข้อมูลไม่ครบ", "ตรวจไม่เจอ", "วางขาย"],
      followup:
        "ถ้าฉลากผิดหลุดไปจนพิมพ์หรือวางขายแล้ว ปกติหลุดเพราะไม่มีใครตรวจ จุดตรวจไม่ครอบคลุม หรือข้อมูลที่ใช้ตรวจไม่ครบครับ/คะ?",
    },
  ],
  "q3-1": [
    {
      id: "format",
      label: "รูปแบบนวัตกรรม",
      keywords: ["เอกสาร", "แอป", "โปรแกรม", "เว็บ", "มือถือ", "สื่อ", "วิดีโอ", "คู่มือ"],
      followup:
        "ถ้าให้เลือกจริง ๆ ท่านอยากให้นวัตกรรมนี้อยู่ในรูปแบบไหนมากที่สุด เช่น แอป เว็บ คู่มือ หรือสื่อสอนครับ/คะ?",
    },
    {
      id: "ease",
      label: "ความง่ายในการใช้",
      keywords: ["ง่าย", "ยาก", "ไม่ถนัด", "ใช้ไม่เป็น", "สะดวก", "ซับซ้อน"],
      followup:
        "อะไรจะทำให้เครื่องมือนี้ใช้ง่ายสำหรับท่าน และอะไรที่กลัวว่าจะทำให้ใช้ยากครับ/คะ?",
    },
    {
      id: "support",
      label: "สิ่งสนับสนุนที่ต้องการ",
      keywords: ["สอน", "ตัวอย่าง", "คำแนะนำ", "อธิบาย", "เจ้าหน้าที่", "คู่มือ"],
      followup:
        "นอกจากตัวระบบแล้ว ท่านอยากได้คำแนะนำ ตัวอย่าง หรือการช่วยเหลือแบบใดเพิ่มไหมครับ/คะ?",
    },
  ],
  "q3-2": [
    {
      id: "first-feature",
      label: "ฟังก์ชันแรกที่อยากได้",
      keywords: ["ตรวจ", "บอก", "แจ้ง", "ออกแบบ", "ร่าง", "ฟังก์ชัน", "อันดับแรก"],
      followup:
        "ถ้าระบบทำได้เพียงหนึ่งอย่างก่อน ท่านอยากให้ช่วยเรื่องใดมากที่สุดครับ/คะ?",
    },
    {
      id: "explanation",
      label: "ระดับคำอธิบายที่ต้องการ",
      keywords: ["อธิบาย", "แก้", "ทำอย่างไร", "ถูก", "ผิด", "เหตุผล", "กฎหมาย"],
      followup:
        "เวลาระบบเจอปัญหา ท่านอยากให้บอกแค่ถูก/ผิด หรืออยากได้เหตุผลและวิธีแก้ด้วยครับ/คะ?",
    },
    {
      id: "timing",
      label: "ช่วงเวลาที่ใช้",
      keywords: ["ก่อน", "ระหว่าง", "หลัง", "ออกแบบ", "พิมพ์", "ส่ง"],
      followup:
        "ท่านคิดว่าจะใช้ระบบนี้ช่วงไหนของงานฉลากมากที่สุดครับ/คะ?",
    },
    {
      id: "cause-fit",
      label: "ฟังก์ชันเชื่อมกับสาเหตุจริง",
      keywords: ["สาเหตุ", "แก้", "ผิด", "จริง", "ช่วย", "ปัญหา"],
      followup:
        "ฟังก์ชันที่เลือกนี้จะช่วยแก้สาเหตุของฉลากผิดข้อใดที่ท่านพบจริงครับ/คะ?",
    },
  ],
  "q3-3": [
    {
      id: "time-saving",
      label: "ลดเวลา/ลดปัญหา",
      keywords: ["ประหยัด", "ลด", "เร็ว", "เวลา", "ปัญหา", "ช่วย"],
      followup:
        "ถ้าระบบช่วยร่างข้อความบนฉลากให้ ท่านคิดว่าจะลดเวลา หรือลดความผิดพลาดตรงไหนได้มากที่สุดครับ/คะ?",
    },
    {
      id: "hard-fields",
      label: "ข้อมูลที่กรอกยาก",
      keywords: ["ส่วนประกอบ", "วัตถุเจือปน", "คำเตือน", "โภชนาการ", "กรอก", "ยาก"],
      followup:
        "ข้อมูลส่วนไหนที่ท่านรู้สึกว่ากรอกหรือเขียนบนฉลากยากที่สุดครับ/คะ?",
    },
    {
      id: "claim-warning",
      label: "คำเตือน/โภชนาการ/กล่าวอ้าง",
      keywords: ["คำเตือน", "ถั่ว", "แพ้", "โภชนาการ", "ไขมันต่ำ", "น้ำตาล", "กล่าวอ้าง"],
      followup:
        "อยากให้ระบบช่วยแนะนำคำเตือน โภชนาการ หรือข้อความกล่าวอ้างแบบไหนเป็นพิเศษไหมครับ/คะ?",
    },
  ],
  "q3-4": [
    {
      id: "device",
      label: "อุปกรณ์ที่สะดวก",
      keywords: ["มือถือ", "โทรศัพท์", "แท็บเล็ต", "คอม", "คอมพิวเตอร์", "โน้ตบุ๊ก"],
      followup:
        "ท่านสะดวกใช้เครื่องมือนี้ผ่านอุปกรณ์ใดมากที่สุด และเพราะอะไรครับ/คะ?",
    },
    {
      id: "online",
      label: "ออนไลน์/ออฟไลน์",
      keywords: ["ออนไลน์", "ออฟไลน์", "อินเทอร์เน็ต", "เน็ต", "สัญญาณ"],
      followup:
        "การใช้งานออนไลน์ตลอดเวลามีปัญหาสำหรับท่านไหม หรือควรใช้บางส่วนแบบออฟไลน์ได้ครับ/คะ?",
    },
    {
      id: "speed",
      label: "ความเร็วที่ยอมรับได้",
      keywords: ["เร็ว", "ช้า", "รอ", "วินาที", "นาที", "ตอบสนอง"],
      followup:
        "ถ้าระบบต้องประมวลผล ท่านรอผลได้นานประมาณเท่าไรจึงจะยังรู้สึกว่าใช้งานได้ครับ/คะ?",
    },
  ],
  "q3-5": [
    {
      id: "workflow-change",
      label: "ผลต่อวิธีทำงาน",
      keywords: ["เปลี่ยน", "ทำงาน", "เร็ว", "ลด", "ช่วย", "ตรวจ"],
      followup:
        "ถ้าถ่ายรูปฉลากแล้วระบบแจ้งข้อผิดพลาดได้ทันที วิธีทำงานของท่านจะเปลี่ยนไปอย่างไรครับ/คะ?",
    },
    {
      id: "trust",
      label: "ความเชื่อมั่นต่อ AI",
      keywords: ["มั่นใจ", "เชื่อ", "ถูกต้อง", "กังวล", "ผิดพลาด", "ไว้ใจ"],
      followup:
        "อะไรจะทำให้ท่านมั่นใจผลจาก AI มากขึ้นครับ/คะ?",
    },
    {
      id: "human-confirm",
      label: "ต้องการผู้เชี่ยวชาญยืนยัน",
      keywords: ["เจ้าหน้าที่", "ผู้เชี่ยวชาญ", "ยืนยัน", "มนุษย์", "ตรวจซ้ำ", "อย."],
      followup:
        "ท่านยังอยากให้มีเจ้าหน้าที่หรือผู้เชี่ยวชาญยืนยันผลอีกครั้งไหมครับ/คะ?",
    },
  ],
  "q3-6": [
    {
      id: "top-priority",
      label: "สิ่งที่อยากให้แก้อันดับ 1",
      keywords: ["อันดับ", "สำคัญ", "ที่สุด", "อยาก", "ต้องการ", "แก้"],
      followup:
        "จากทั้งหมด ถ้าเลือกได้ข้อเดียว ท่านอยากให้แอปช่วยแก้ปัญหาอะไรมากที่สุดครับ/คะ?",
    },
    {
      id: "top-causes",
      label: "จัดอันดับสาเหตุฉลากผิด",
      keywords: ["สาเหตุ", "อันดับ", "หลัก", "ไม่ถูกต้อง", "สำคัญ", "เกิดจาก"],
      followup:
        "จากประสบการณ์ของท่าน หากต้องจัดอันดับ 3 สาเหตุหลักที่ทำให้ฉลากอาหารไม่ถูกต้อง ท่านคิดว่าเกิดจากอะไรบ้าง และข้อใดสำคัญที่สุดครับ/คะ?",
    },
    {
      id: "work-life-change",
      label: "ผลถ้าทำสำเร็จ",
      keywords: ["เปลี่ยน", "ช่วย", "ลด", "เร็ว", "มั่นใจ", "ทำงาน"],
      followup:
        "ถ้าแอปทำเรื่องนั้นได้จริง งานของท่านจะดีขึ้นหรือเปลี่ยนไปอย่างไรครับ/คะ?",
    },
    {
      id: "avoid",
      label: "สิ่งที่ไม่ควรทำ",
      keywords: ["ไม่ควร", "ไม่อยาก", "ไม่ต้องการ", "กังวล", "ข้อเสนอ", "เพิ่ม"],
      followup:
        "มีอะไรที่ท่านคิดว่าแอปไม่ควรทำ หรือมีข้อเสนอแนะที่อยากฝากให้ผู้พัฒนาระวังไหมครับ/คะ?",
    },
  ],
};

const participantNotice = [
  {
    title: "วัตถุประสงค์",
    text:
      "ศึกษาสถานการณ์ปัญหาการจัดทำฉลากอาหาร และความต้องการเครื่องมือหรือนวัตกรรมดิจิทัลที่ช่วยสนับสนุนผู้ประกอบการในจังหวัดสมุทรปราการ",
  },
  {
    title: "สิ่งที่จะขอให้ทำ",
    text:
      "ให้สัมภาษณ์เชิงลึกเกี่ยวกับประสบการณ์ ปัญหา และความต้องการในการจัดทำฉลากอาหาร ใช้เวลาประมาณ 10-15 นาที",
  },
  {
    title: "ความสมัครใจ",
    text:
      "การเข้าร่วมเป็นไปโดยสมัครใจ สามารถไม่ตอบบางคำถาม หรือถอนตัวจากการวิจัยได้ตลอดเวลา โดยไม่มีผลกระทบใด ๆ",
  },
  {
    title: "การเก็บข้อมูล",
    text:
      "ข้อมูลจะถูกปกปิดเป็นความลับ ใช้เพื่อการวิจัยและการพัฒนาแอปพลิเคชันเท่านั้น การรายงานผลจะไม่เปิดเผยชื่อหรือข้อมูลที่ระบุตัวตนได้",
  },
];

const businessTypeOptions = ["", "วิสาหกิจชุมชน / OTOP", "SME", "นิติบุคคล", "อื่น ๆ"];
const respondentMethodOptions = [
  "ออกแบบและทำเองทั้งหมด",
  "จ้างร้านกราฟิกออกแบบ",
  "จ้างโรงงาน OEM จัดทำให้",
  "ใช้ซอฟต์แวร์/เครื่องมือออนไลน์ช่วย",
];
const requiredRespondentFields = [
  ["code", "รหัส"],
  ["license", "ประเภทใบอนุญาต"],
  ["duration", "ระยะเวลากิจการ"],
  ["foodType", "ประเภทอาหารหลัก"],
  ["productCount", "จำนวนฉลาก"],
  ["role", "ตำแหน่งผู้รับผิดชอบ"],
  ["businessType", "ประเภทกิจการ"],
];

const blankState = {
  view: "manual",
  currentId: "q2-1",
  respondent: {
    code: "",
    license: "",
    duration: "",
    foodType: "",
    productCount: "",
    role: "",
    businessType: "",
    methods: [],
    methodOther: "",
  },
  consent: {
    informed: false,
    participation: false,
    audio: false,
    privacy: false,
    acceptedAt: null,
    declinedAt: null,
  },
  interviewer: "นายชญานิน ศรีชมภู",
  timer: {
    running: false,
    startedAt: null,
    elapsedMs: 0,
  },
  answers: {},
  ai: {
    currentId: "q2-1",
    started: false,
    completed: false,
    messages: [],
    isTyping: false,
  },
  isExtracting: false,
  helperText: "",
  updatedAt: null,
};

let state = loadState();
let toastTimer = null;

function icon(name) {
  const icons = {
    check:
      '<path d="M20 6 9 17l-5-5"></path>',
    clock:
      '<circle cx="12" cy="12" r="10"></circle><path d="M12 6v6l4 2"></path>',
    download:
      '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="M7 10l5 5 5-5"></path><path d="M12 15V3"></path>',
    file:
      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><path d="M14 2v6h6"></path><path d="M16 13H8"></path><path d="M16 17H8"></path>',
    mic:
      '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><path d="M12 19v3"></path>',
    pause:
      '<path d="M10 4H6v16h4V4Z"></path><path d="M18 4h-4v16h4V4Z"></path>',
    play:
      '<path d="m5 3 14 9-14 9V3Z"></path>',
    save:
      '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2Z"></path><path d="M17 21v-8H7v8"></path><path d="M7 3v5h8"></path>',
    spark:
      '<path d="M12 3l1.7 4.8L18 10l-4.3 2.2L12 17l-1.7-4.8L6 10l4.3-2.2L12 3Z"></path><path d="M19 3v4"></path><path d="M21 5h-4"></path><path d="M5 17v4"></path><path d="M7 19H3"></path>',
    message:
      '<path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"></path>',
    send:
      '<path d="m22 2-7 20-4-9-9-4Z"></path><path d="M22 2 11 13"></path>',
    trash:
      '<path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"></path>',
    user:
      '<path d="M20 21a8 8 0 0 0-16 0"></path><circle cx="12" cy="7" r="4"></circle>',
    arrowLeft:
      '<path d="M19 12H5"></path><path d="m12 19-7-7 7-7"></path>',
    arrowRight:
      '<path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path>',
  };
  return `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">${icons[name] || icons.file}</svg>`;
}

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    return normalizeState(saved || blankState);
  } catch {
    return normalizeState(blankState);
  }
}

function normalizeState(source) {
  const next = structuredClone(blankState);
  Object.assign(next, source || {});
  next.view = ["manual", "ai"].includes(source?.view) ? source.view : "manual";
  next.respondent = { ...blankState.respondent, ...(source?.respondent || {}) };
  if (!Array.isArray(next.respondent.methods)) next.respondent.methods = [];
  next.consent = { ...blankState.consent, ...(source?.consent || {}) };
  next.timer = { ...blankState.timer, ...(source?.timer || {}) };
  next.ai = { ...blankState.ai, ...(source?.ai || {}) };
  next.answers = source?.answers || {};

  guide.forEach((question) => {
    next.answers[question.id] = {
      answer: "",
      summary: "",
      probes: [],
      tags: [],
      coverage: [],
      aiFollowups: [],
      ...(next.answers[question.id] || {}),
    };
  });

  if (!guide.some((question) => question.id === next.currentId)) {
    next.currentId = guide[0].id;
  }
  if (!guide.some((question) => question.id === next.ai.currentId)) {
    next.ai.currentId = guide[0].id;
  }
  if (!Array.isArray(next.ai.messages)) next.ai.messages = [];

  return next;
}

function saveState(show = false) {
  state.updatedAt = new Date().toISOString();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  if (show) showToast("บันทึกฉบับร่างไว้ในเครื่องนี้แล้ว");
}

function currentQuestion() {
  return guide.find((question) => question.id === state.currentId) || guide[0];
}

function currentIndex() {
  return guide.findIndex((question) => question.id === state.currentId);
}

function answerFor(id) {
  return state.answers[id];
}

function isComplete(id) {
  const answer = answerFor(id);
  return Boolean(answer.answer.trim() || answer.summary.trim());
}

function progress() {
  const done = guide.filter((question) => isComplete(question.id)).length;
  return {
    done,
    total: guide.length,
    percent: Math.round((done / guide.length) * 100),
  };
}

function hasInterviewConsent() {
  return Boolean(
    state.consent.informed &&
    state.consent.participation &&
    state.consent.privacy,
  );
}

function missingRespondentFields() {
  const missing = requiredRespondentFields
    .filter(([key]) => !String(state.respondent[key] || "").trim())
    .map(([, label]) => label);

  if (!state.respondent.methods.length) {
    missing.push("วิธีจัดทำฉลาก");
  }

  return missing;
}

function hasRespondentProfile() {
  return missingRespondentFields().length === 0;
}

function markConsentAccepted() {
  state.consent.informed = true;
  state.consent.participation = true;
  state.consent.privacy = true;
  state.consent.declinedAt = null;
  if (!state.consent.acceptedAt) {
    state.consent.acceptedAt = new Date().toISOString();
  }
}

function showConsentRequired() {
  showToast("กรุณาแจ้งข้อมูลการวิจัยและบันทึกความยินยอมก่อนเริ่มสัมภาษณ์");
}

function showRespondentRequired() {
  const missing = missingRespondentFields();
  const sample = missing.slice(0, 3).join(", ");
  showToast(`กรุณากรอกข้อมูลผู้ให้สัมภาษณ์ให้ครบก่อนเริ่ม: ${sample}${missing.length > 3 ? "..." : ""}`);
}

function elapsedMs() {
  const extra =
    state.timer.running && state.timer.startedAt
      ? Date.now() - state.timer.startedAt
      : 0;
  return state.timer.elapsedMs + extra;
}

function formatDuration(ms) {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function render() {
  const question = currentQuestion();
  const answer = answerFor(question.id);
  const stats = progress();
  const app = document.querySelector("#app");
  const consentReady = hasInterviewConsent();
  const respondentReady = hasRespondentProfile();
  const interviewReady = consentReady && respondentReady;
  const mainView = !consentReady
    ? renderConsentGate()
    : !respondentReady
      ? renderRespondentGate()
      : state.view === "ai"
        ? renderAIInterview(stats)
        : renderQuestion(question, answer);

  app.innerHTML = `
    <div class="app-shell ${interviewReady ? "" : "setup-mode"} ${consentReady ? "" : "consent-mode"}">
      ${renderTopbar(stats)}
      <main class="layout ${state.view === "ai" ? "ai-layout" : ""} ${interviewReady ? "" : "setup-layout"} ${consentReady ? "" : "consent-layout"}">
        ${interviewReady ? renderSidebar(stats) : ""}
        ${mainView}
        ${interviewReady ? renderInspector(stats) : ""}
      </main>
      <div id="toast" class="toast" role="status" aria-live="polite"></div>
    </div>
    ${state.isExtracting ? `
      <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-title">กำลังดึงข้อมูลด้วย AI...</div>
        <div class="loading-subtitle">กรุณารอประมาณ 10-15 วินาที ระบบกำลังวิเคราะห์บทสนทนาและกรอกข้อมูลฟอร์มอัตโนมัติ</div>
      </div>
    ` : ""}
  `;

  refreshTimer();
  syncChatViewport();
}

function renderTopbar(stats) {
  const timerAction = state.timer.running ? "pause-timer" : "start-timer";

  return `
    <header class="topbar">
      <div class="brand">
        <div class="brand-mark">${icon("mic")}</div>
        <div>
          <h1 class="brand-title">ฉลากชัวร์ Interview Studio</h1>
          <p class="brand-subtitle">แบบสัมภาษณ์เชิงลึก: สภาพปัญหาการจัดทำฉลากอาหารและความต้องการนวัตกรรม</p>
        </div>
      </div>
      <div class="top-actions">
        <div class="mode-switch" role="tablist" aria-label="โหมดสัมภาษณ์">
          <button class="mode-tab ${state.view === "manual" ? "active" : ""}" data-action="set-view" data-view="manual">ผู้สัมภาษณ์กรอกเอง</button>
          <button class="mode-tab ${state.view === "ai" ? "active" : ""}" data-action="set-view" data-view="ai">AI สัมภาษณ์ผ่านแชท</button>
        </div>
        <span class="status-chip ${stats.done ? "good" : ""}">${stats.done}/${stats.total} คำถาม</span>
        <button class="button accent" data-action="${timerAction}">${icon(state.timer.running ? "pause" : "play")}<span>${state.timer.running ? "หยุด" : "เริ่ม"}</span></button>
        <button class="button soft" data-action="save">${icon("save")}<span>บันทึกร่าง</span></button>
        <button class="button warning" data-action="reset">${icon("trash")}<span>ล้างข้อมูล</span></button>
        <button class="button primary" data-action="submit">${icon("send")}<span>ส่งข้อมูล</span></button>
      </div>
    </header>
  `;
}

function renderConsentSidebar(stats) {
  return `
    <aside class="sidebar consent-sidebar">
      <section class="panel progress-panel">
        <div class="progress-row">
          <div>
            <p class="tiny-label">ก่อนเริ่ม</p>
            <p class="progress-title">รอบันทึกความยินยอม</p>
          </div>
          <div class="progress-number" style="--progress-angle: ${stats.percent * 3.6}deg">${stats.percent}%</div>
        </div>
      </section>
    </aside>
  `;
}

function renderConsentGate() {
  return `
    <section class="workspace consent-workspace">
      <article class="panel consent-gate">
        <div class="consent-hero">
          <div class="brand-mark">${icon("check")}</div>
          <div>
            <p class="section-kicker">ก่อนเริ่มสัมภาษณ์</p>
            <h2 class="question-title">ข้อมูลการวิจัยและความยินยอม</h2>
            <p class="consent-intro">
              งานวิจัยเรื่อง การพัฒนารูปแบบการตรวจสอบและจัดทำฉลากอาหารสำหรับผู้ประกอบการ จังหวัดสมุทรปราการ โดยนายชญานิน ศรีชมภู
            </p>
          </div>
        </div>

        <div class="consent-grid">
          ${participantNotice
            .map(
              (item) => `
                <section class="consent-point">
                  <strong>${escapeHtml(item.title)}</strong>
                  <p>${escapeHtml(item.text)}</p>
                </section>
              `,
            )
            .join("")}
        </div>

        <div class="consent-confirm">
          <p>
            การกดปุ่มยินยอมหมายถึงผู้ให้สัมภาษณ์ได้รับทราบข้อมูลสำคัญ มีโอกาสซักถาม และสมัครใจให้ข้อมูลเพื่อการวิจัยนี้
          </p>
          ${renderToggle("audio", "ยินยอมให้บันทึกเสียงหรือถอดคำพูดเพื่อความถูกต้องของข้อมูล (เลือกได้)")}
          <div class="consent-actions">
            <button class="button" data-action="decline-consent">${icon("pause")}<span>ยังไม่ยินยอม</span></button>
            <button class="button accent" data-action="accept-consent">${icon("check")}<span>ยินยอม ไปกรอกข้อมูล</span></button>
          </div>
        </div>
      </article>
    </section>
  `;
}

function renderRespondentGate() {
  return `
    <section class="workspace setup-workspace respondent-workspace">
      <article class="panel respondent-gate">
        <div class="consent-hero">
          <div class="brand-mark">${icon("user")}</div>
          <div>
            <p class="section-kicker">ก่อนเริ่มสัมภาษณ์</p>
            <h2 class="question-title">ข้อมูลผู้ให้สัมภาษณ์</h2>
            <p class="consent-intro">
              กรุณากรอกข้อมูลพื้นฐานให้ครบก่อนเริ่มสัมภาษณ์ ระบบจะใช้ข้อมูลนี้ประกอบการบันทึกและส่งออกผลสัมภาษณ์
            </p>
          </div>
        </div>

        <div class="respondent-required-note">
          <p>ต้องกรอกทุกช่องหลัก และเลือกวิธีจัดทำฉลากอย่างน้อย 1 วิธี จึงจะเริ่มสัมภาษณ์ได้</p>
        </div>

        ${renderRespondentFields()}

        <div class="consent-actions">
          <button class="button soft" data-action="save">${icon("save")}<span>บันทึกร่าง</span></button>
          <button class="button accent" data-action="confirm-respondent">${icon("check")}<span>เริ่มสัมภาษณ์</span></button>
        </div>
      </article>
    </section>
  `;
}

function renderSidebar(stats) {
  const angle = `${stats.percent * 3.6}deg`;
  const sectionTwo = guide.filter((question) => question.id.startsWith("q2"));
  const sectionThree = guide.filter((question) => question.id.startsWith("q3"));

  return `
    <aside class="sidebar">
      <section class="panel progress-panel">
        <div class="progress-row">
          <div>
            <p class="tiny-label">ความคืบหน้า</p>
            <p class="progress-title">บันทึกแล้ว ${stats.done} จาก ${stats.total} คำถาม</p>
          </div>
          <div class="progress-number" style="--progress-angle: ${angle}">${stats.percent}%</div>
        </div>
      </section>
      <nav class="panel nav-list" aria-label="รายการคำถามสัมภาษณ์">
        ${renderNavSection("ส่วนที่ 2", sectionTwo)}
        ${renderNavSection("ส่วนที่ 3", sectionThree)}
      </nav>
    </aside>
  `;
}

function renderNavSection(title, items) {
  return `
    <p class="nav-section-title">${title}</p>
    ${items
      .map((question) => {
        const index = guide.findIndex((item) => item.id === question.id) + 1;
        const active = question.id === state.currentId ? "active" : "";
        const done = isComplete(question.id) ? "done" : "";
        return `
          <button class="nav-item ${active}" data-action="go" data-id="${question.id}">
            <span class="nav-index">${question.id.replace("q", "").replace("-", ".")}</span>
            <span class="nav-main">
              <span class="nav-title">${escapeHtml(question.short)}</span>
              <span class="nav-caption">คำถามที่ ${index}</span>
            </span>
            <span class="check-dot ${done}"></span>
          </button>
        `;
      })
      .join("")}
  `;
}

function renderQuestion(question, answer) {
  const index = currentIndex();
  const statusClass = isComplete(question.id) ? "good" : "warn";
  const statusText = isComplete(question.id) ? "มีบันทึกแล้ว" : "รอบันทึกคำตอบ";
  const probeCount = answer.probes.length;
  const helper = state.helperText || buildSuggestion(question, answer);

  return `
    <section class="workspace">
      <article class="panel question-panel">
        <div class="question-head">
          <div>
            <p class="section-kicker">${escapeHtml(question.section)}</p>
            <h2 class="question-title">คำถามหลัก ${question.id.replace("q", "").replace("-", ".")}</h2>
          </div>
          <div class="question-meta">
            <span class="status-chip ${statusClass}">${statusText}</span>
            <span class="status-chip">${probeCount}/${question.probes.length} probe</span>
          </div>
        </div>
        <div class="question-body">
          <div class="field-stack">
            <div class="field">
              <span class="field-label">คำถามหลัก</span>
              <div class="assistant-box">
                <p class="assistant-prompt">${escapeHtml(question.title)}</p>
                <button class="button soft" data-action="suggest">${icon("spark")}<span>ช่วยเลือกคำถามถามต่อ</span></button>
              </div>
            </div>

            <div class="field">
              <label for="answer">บันทึกคำตอบ</label>
              <textarea id="answer" class="textarea" data-answer="${question.id}" placeholder="จดคำตอบแบบเล่าเรื่อง เหตุการณ์จริง คำพูดสำคัญ หรือบริบทที่สังเกตได้">${escapeHtml(answer.answer)}</textarea>
            </div>

            <div class="field">
              <label for="summary">สรุปประเด็นสำคัญ</label>
              <textarea id="summary" class="textarea summary" data-summary="${question.id}" placeholder="สรุปเป็น bullet/ประเด็นสำหรับวิเคราะห์ภายหลัง">${escapeHtml(answer.summary)}</textarea>
            </div>

            <div class="field">
              <span class="field-label">แท็กประเด็น</span>
              <div class="tag-row">
                ${tags
                  .map(
                    (tag) => `
                      <button class="tag ${answer.tags.includes(tag) ? "active" : ""}" data-action="tag" data-id="${question.id}" data-tag="${tag}">
                        ${escapeHtml(tag)}
                      </button>
                    `,
                  )
                  .join("")}
              </div>
            </div>
          </div>

          <aside class="probe-box">
            <div>
              <p class="tiny-label">คำถามเพื่อเจาะลึก</p>
              <p class="empty-text">ติ๊กเมื่อถามแล้ว เพื่อเห็นช่องว่างระหว่างสัมภาษณ์</p>
            </div>
            <div class="probe-list">
              ${question.probes
                .map(
                  (probe, probeIndex) => `
                    <label class="probe-item">
                      <input type="checkbox" data-probe="${question.id}" data-probe-index="${probeIndex}" ${answer.probes.includes(probeIndex) ? "checked" : ""} />
                      <span>${escapeHtml(probe)}</span>
                    </label>
                  `,
                )
                .join("")}
            </div>
            ${question.note ? `<div class="note-callout">${escapeHtml(question.note)}</div>` : ""}
            <div class="assistant-box">
              <p class="tiny-label">คำถามถัดไปที่น่าถาม</p>
              <p class="assistant-prompt">${escapeHtml(helper)}</p>
            </div>
          </aside>
        </div>
        <footer class="question-footer">
          <button class="button" data-action="prev" ${index === 0 ? "disabled" : ""}>${icon("arrowLeft")}<span>คำถามก่อนหน้า</span></button>
          <div class="toolbar-group">
            <button class="button warning" data-action="clear-current">${icon("trash")}<span>ล้างคำตอบข้อนี้</span></button>
            <button class="button primary" data-action="next" ${index === guide.length - 1 ? "disabled" : ""}><span>คำถามถัดไป</span>${icon("arrowRight")}</button>
          </div>
        </footer>
      </article>
    </section>
  `;
}

function renderAIInterview(stats) {
  const question = aiCurrentQuestion();
  const answer = answerFor(question.id);
  const index = aiCurrentIndex() + 1;
  const coverage = coverageFor(question.id, answer);

  return `
    <section class="workspace ai-workspace">
      <article class="panel chat-panel">
        <div class="question-head">
          <div>
            <p class="section-kicker">${escapeHtml(question.section)}</p>
            <h2 class="question-title">AI สัมภาษณ์ผ่านแชท</h2>
          </div>
          <div class="question-meta">
            <span class="status-chip ${state.ai.started ? "good" : "warn"}">${state.ai.started ? "กำลังสัมภาษณ์" : "พร้อมเริ่ม"}</span>
            <span class="status-chip">ข้อ ${index}/${guide.length}</span>
            <span class="status-chip">${coverage.covered.length}/${coverage.plan.length} ประเด็น</span>
          </div>
        </div>

        <div class="ai-current-card">
          <div>
            <p class="tiny-label">คำถามหลักที่ AI กำลังเก็บข้อมูล</p>
            <h3>${question.id.replace("q", "").replace("-", ".")} ${escapeHtml(question.short)}</h3>
            <p>${escapeHtml(question.title)}</p>
          </div>
          <button class="button soft" data-action="ask-ai-probe">${icon("spark")}<span>ถามต่อจากคำตอบ</span></button>
        </div>

        <div class="chat-log" data-chat-log aria-live="polite">
          ${renderChatMessages()}
        </div>

        <div class="chat-compose">
          <textarea class="chat-input" data-chat-input placeholder="พิมพ์คำตอบของผู้ให้สัมภาษณ์ หรือถอดคำพูดจากการสนทนา... (หรือใช้ฟังก์ชันพูดแทนการพิมพ์)"></textarea>
          <div class="chat-actions">
            <div class="toolbar-group">
              <button class="button accent" data-action="start-ai">${icon("message")}<span>${state.ai.started ? "ช่วงใหม่" : "เริ่ม AI"}</span></button>
              <button class="button soft" data-action="ai-next">${icon("arrowRight")}<span>คำถามถัดไป</span></button>
              <button class="button warning" data-action="finish-ai">${icon("check")}<span>จบสัมภาษณ์</span></button>
              <button class="button soft" data-action="extract-ai">${icon("spark")}<span>ดึงข้อมูล</span></button>
            </div>
            <div class="toolbar-group">
              <button class="button soft" data-action="toggle-mic">
                ${icon("mic")}
                <span>พูดตอบ</span>
              </button>
              <button class="button primary" data-action="send-chat">${icon("send")}<span>ส่งคำตอบ</span></button>
            </div>
          </div>
        </div>
      </article>

      <section class="panel ai-data-panel">
        <div class="side-heading">
          <h3>ข้อมูลที่เก็บจากแชท</h3>
          <span class="status-chip">${stats.percent}%</span>
        </div>
        <div class="summary-list">
          ${renderRecentSummaries()}
        </div>
      </section>
    </section>
  `;
}

function renderChatMessages() {
  if (!state.ai.messages.length && !state.ai.isTyping) {
    return `
      <div class="chat-empty">
        <div class="brand-mark">${icon("message")}</div>
        <h3>พร้อมให้ AI เป็นผู้สัมภาษณ์</h3>
        <p>กดเริ่ม แล้ว AI จะใช้คำถามหลักเป็นเป้าหมาย ถามต่อจากคำตอบจริง และใช้คำถามเจาะลึกเดิมเป็นเพียงแนวทาง</p>
      </div>
    `;
  }

  let html = state.ai.messages
    .map((message) => {
      const question = guide.find((item) => item.id === message.questionId);
      const label = message.role === "assistant" ? "AI ผู้สัมภาษณ์" : "ผู้ให้สัมภาษณ์";
      return `
        <article class="chat-message ${message.role}">
          <div class="chat-avatar">${message.role === "assistant" ? icon("spark") : icon("user")}</div>
          <div class="chat-bubble">
            <div class="chat-meta">
              <strong>${label}</strong>
              <span>${question ? question.id.replace("q", "").replace("-", ".") : ""}</span>
            </div>
            <p>${escapeHtml(message.text)}</p>
          </div>
        </article>
      `;
    })
    .join("");

  if (state.ai.isTyping) {
    html += `
      <article class="chat-message assistant">
        <div class="chat-avatar">${icon("spark")}</div>
        <div class="chat-bubble">
          <div class="chat-meta">
            <strong>AI ผู้สัมภาษณ์</strong>
            <span>กำลังประมวลผล...</span>
          </div>
          <div class="typing-indicator" style="margin-top: 6px;">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </article>
    `;
  }

  return html;
}

function renderInspector(stats) {
  return `
    <aside class="inspector">
      <section class="timer-card">
        <div class="timer-top">
          <div>
            <p class="timer-caption">เวลาในการสัมภาษณ์</p>
            <p id="timerValue" class="timer-value">${formatDuration(elapsedMs())}</p>
          </div>
          <span class="status-chip ${state.timer.running ? "good" : ""}">${state.timer.running ? "กำลังจับเวลา" : "ยังไม่เริ่ม"}</span>
        </div>
        <p class="timer-caption">เป้าหมายเดิมของแบบสัมภาษณ์: ประมาณ 10-15 นาที</p>
      </section>

      <section class="panel side-panel">
        <div class="side-heading">
          <h2>ข้อมูลผู้ให้สัมภาษณ์</h2>
          ${icon("user")}
        </div>
        ${renderRespondentFields()}
      </section>

      <section class="panel side-panel">
        <div class="side-heading">
          <h3>สรุปสถานะบันทึก</h3>
          <span class="status-chip">${stats.percent}%</span>
        </div>
        <div class="summary-list">
          ${renderRecentSummaries()}
        </div>
      </section>
    </aside>
  `;
}

function renderRespondentFields() {
  const r = state.respondent;
  return `
    <div class="form-grid respondent-form-grid">
      ${renderInput("code", "รหัส *", r.code)}
      ${renderInput("license", "ประเภทใบอนุญาต *", r.license)}
      ${renderInput("duration", "ระยะเวลากิจการ *", r.duration)}
      ${renderInput("foodType", "ประเภทอาหารหลัก *", r.foodType)}
      ${renderInput("productCount", "จำนวนฉลาก *", r.productCount)}
      ${renderInput("role", "ตำแหน่งผู้รับผิดชอบ *", r.role)}
      <div class="field wide">
        <label for="businessType">ประเภทกิจการ *</label>
        <select id="businessType" class="select" data-respondent="businessType">
          ${businessTypeOptions
            .map((option) => `<option value="${escapeHtml(option)}" ${r.businessType === option ? "selected" : ""}>${option || "เลือกประเภทกิจการ"}</option>`)
            .join("")}
        </select>
      </div>
      <div class="field wide">
        <span class="field-label">วิธีจัดทำฉลาก *</span>
        ${respondentMethodOptions
          .map((method) => renderMethod(method))
          .join("")}
      </div>
      ${renderInput("methodOther", "ระบุเพิ่มเติม", r.methodOther, "wide")}
    </div>
  `;
}

function renderInput(key, label, value, className = "") {
  return `
    <div class="field ${className}">
      <label for="${key}">${label}</label>
      <input id="${key}" class="input" data-respondent="${key}" value="${escapeHtml(value)}" />
    </div>
  `;
}

function renderToggle(key, label) {
  return `
    <label class="toggle-row">
      <input type="checkbox" data-consent="${key}" ${state.consent[key] ? "checked" : ""} />
      <span>${label}</span>
    </label>
  `;
}

function renderMethod(method) {
  const checked = state.respondent.methods.includes(method) ? "checked" : "";
  return `
    <label class="check-row">
      <input type="checkbox" data-method="${escapeHtml(method)}" ${checked} />
      <span>${escapeHtml(method)}</span>
    </label>
  `;
}

function renderRecentSummaries() {
  const items = guide
    .filter((question) => isComplete(question.id))
    .slice(-4)
    .map((question) => {
      const answer = answerFor(question.id);
      const text = answer.summary || answer.answer;
      return `
        <div class="summary-item">
          <strong>${question.id.replace("q", "").replace("-", ".")} ${escapeHtml(question.short)}</strong>
          <span>${escapeHtml(text)}</span>
        </div>
      `;
    })
    .join("");

  return items || `<p class="empty-text">ยังไม่มีคำตอบที่บันทึกไว้</p>`;
}

function buildSuggestion(question, answer) {
  const textLength = answer.answer.trim().length;
  if (textLength < 40) {
    return "ช่วยเล่าเป็นเหตุการณ์จริงสักหนึ่งตัวอย่างได้ไหมครับ/คะ ว่าเกิดอะไรขึ้น ใครเกี่ยวข้อง และจบอย่างไร?";
  }

  const remainingProbe = question.probes.find(
    (_, probeIndex) => !answer.probes.includes(probeIndex),
  );
  if (remainingProbe) return remainingProbe;

  if (!answer.summary.trim()) {
    return "จากที่เล่ามา ถ้าให้สรุปเป็น 1-2 ประเด็นสำคัญ ท่านอยากให้ผู้พัฒนาเข้าใจอะไรที่สุด?";
  }

  return "มีประเด็นใดที่ยังไม่ได้เล่า แต่คิดว่าสำคัญต่อการพัฒนาแอปพลิเคชันตรวจสอบฉลากหรือไม่?";
}

function aiCurrentQuestion() {
  return guide.find((question) => question.id === state.ai.currentId) || guide[0];
}

function aiCurrentIndex() {
  return guide.findIndex((question) => question.id === aiCurrentQuestion().id);
}

function addAIMessage(role, text, questionId = state.ai.currentId) {
  state.ai.messages.push({
    role,
    text,
    questionId,
    createdAt: new Date().toISOString(),
  });
}

function aiOpeningText(question) {
  return `สวัสดีครับ/ค่ะ ผมจะช่วยสัมภาษณ์ตามแบบสัมภาษณ์เชิงลึกของงานวิจัยนี้ โดยจะถามทีละข้อและถามเจาะลึกเมื่อคำตอบยังไม่ชัดเจน ขอเริ่มที่ข้อ ${question.id.replace("q", "").replace("-", ".")} นะครับ/คะ: ${question.title}`;
}

function startAIInterview(forceNew = false) {
  if (!hasInterviewConsent()) {
    showConsentRequired();
    return;
  }
  if (!hasRespondentProfile()) {
    showRespondentRequired();
    return;
  }

  if (forceNew) {
    state.ai.messages = [];
    state.ai.currentId = guide[0].id;
    state.currentId = guide[0].id;
    state.ai.completed = false;
  }

  state.ai.started = true;
  state.ai.completed = false;
  state.view = "ai";
  state.currentId = state.ai.currentId;
  if (!state.ai.messages.length || forceNew) {
    addAIMessage("assistant", aiOpeningText(aiCurrentQuestion()));
  }
  startTimer();
  saveState();
  render();
}

function inferTags(text) {
  const lower = text.toLowerCase();
  const matched = [];
  const rules = [
    ["กฎหมาย", ["กฎหมาย", "ประกาศ", "อย.", "450", "445", "ข้อกำหนด"]],
    ["เวลา", ["เวลา", "นาน", "รอ", "ล่าช้า", "วัน", "ชั่วโมง"]],
    ["ต้นทุน", ["ต้นทุน", "ค่าใช้จ่าย", "พิมพ์ใหม่", "เสียเงิน", "ปรับ"]],
    ["ความรู้", ["ไม่รู้", "ไม่เข้าใจ", "สับสน", "อบรม", "ความรู้"]],
    ["การตรวจฉลาก", ["ตรวจ", "ฉลาก", "ถูกต้อง", "ผิด", "แก้"]],
    ["AI", ["ai", "เอไอ", "ถ่ายรูป", "ภาพ", "อัตโนมัติ"]],
    ["มือถือ", ["มือถือ", "โทรศัพท์", "แท็บเล็ต", "คอมพิวเตอร์", "ออนไลน์", "ออฟไลน์"]],
    ["ผู้เชี่ยวชาญ", ["เจ้าหน้าที่", "ผู้เชี่ยวชาญ", "เภสัช", "อย.", "ยืนยัน"]],
    ["ข้อกังวล", ["กังวล", "กลัว", "ไม่มั่นใจ", "เชื่อ", "ความถูกต้อง"]],
    ["ข้อเสนอแนะ", ["อยาก", "ต้องการ", "ควร", "เสนอ", "ฟังก์ชัน"]],
  ];

  rules.forEach(([tag, keywords]) => {
    if (keywords.some((keyword) => lower.includes(keyword))) matched.push(tag);
  });

  return matched;
}

function buildLocalSummary(text) {
  const cleaned = text
    .split(/\n+/)
    .map((part) => part.trim())
    .filter(Boolean)
    .join(" ");
  if (!cleaned) return "";
  const sentences = cleaned.split(/(?<=[.!?。])\s+|(?<=ครับ|ค่ะ|คะ)\s+/).filter(Boolean);
  return (sentences.slice(0, 2).join(" ") || cleaned).slice(0, 220);
}

function appendAnswerFromChat(questionId, text) {
  const answer = answerFor(questionId);
  answer.answer = [answer.answer.trim(), text.trim()].filter(Boolean).join("\n\n");
  answer.summary = buildLocalSummary(answer.answer);
  answer.tags = [...new Set([...answer.tags, ...inferTags(text)])];
  answer.coverage = coverageFor(questionId, answer).covered.map((item) => item.id);
}

function coveragePlanFor(questionId) {
  return coverageGuide[questionId] || [];
}

function coverageFor(questionId, answer) {
  const plan = coveragePlanFor(questionId);
  const text = `${answer.answer || ""} ${answer.summary || ""}`.toLowerCase();
  const explicit = new Set(answer.coverage || []);
  const covered = plan.filter(
    (item) =>
      explicit.has(item.id) ||
      item.keywords.some((keyword) => text.includes(keyword.toLowerCase())),
  );
  return { plan, covered, missing: plan.filter((item) => !covered.includes(item)) };
}

function answerExcerpt(text) {
  const cleaned = text.replace(/\s+/g, " ").trim();
  if (!cleaned) return "";
  return cleaned.length > 86 ? `${cleaned.slice(0, 86)}...` : cleaned;
}

function buildAdaptiveFollowup(question, answer, mode = "auto") {
  const coverage = coverageFor(question.id, answer);
  const asked = new Set(answer.aiFollowups || []);
  const missing = coverage.missing.find((item) => !asked.has(item.id));
  const excerpt = answerExcerpt(answer.answer);

  if (!answer.answer.trim() || answer.answer.trim().length < 36) {
    return {
      id: "concrete-example",
      text:
        "ช่วยเล่าเป็นเหตุการณ์จริงหรือสถานการณ์ที่เคยเจอสักตัวอย่างได้ไหมครับ/คะ เพื่อให้เข้าใจบริบทมากขึ้น?",
    };
  }

  if (missing) {
    const prefix = excerpt ? `จากที่เล่าว่า “${excerpt}” ` : "";
    return {
      id: missing.id,
      text: `${prefix}${missing.followup}`,
    };
  }

  if (mode === "manual") {
    return {
      id: "deeper-meaning",
      text:
        "ถ้าสรุปจากประสบการณ์นี้ ประเด็นไหนที่ท่านอยากให้ผู้พัฒนาแอปเข้าใจมากที่สุดครับ/คะ?",
    };
  }

  return null;
}

function recordFollowup(answer, followupId) {
  if (!followupId) return;
  answer.aiFollowups = [...new Set([...(answer.aiFollowups || []), followupId])];
}

function shouldAskAnotherFollowup(question, answer, latestText) {
  const coverage = coverageFor(question.id, answer);
  const askedCount = (answer.aiFollowups || []).length;
  const enoughText = answer.answer.trim().length >= 88;
  const enoughCoverage = coverage.covered.length >= Math.min(2, coverage.plan.length);
  const latestLooksThin = latestText.trim().length < 45;

  if (latestLooksThin) return true;
  if (coverage.covered.length === 0) return true;
  if (!enoughText && askedCount < 1) return true;
  if (!enoughCoverage && askedCount < 2) return true;
  return false;
}

function askAIProbe() {
  const question = aiCurrentQuestion();
  state.ai.isTyping = true;
  saveState();
  render();

  fetch(`${API_BASE_URL}/api/chat/followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: state.ai.messages,
      currentQuestion: question
    })
  })
  .then(res => {
    if (!res.ok) throw new Error("การเชื่อมต่อเซิร์ฟเวอร์ล้มเหลว");
    return res.json();
  })
  .then(data => {
    state.ai.isTyping = false;
    if (data.response) {
      addAIMessage("assistant", data.response, question.id);
    } else {
      addAIMessage("assistant", "มีประเด็นเพิ่มเติมที่อยากขยายความในข้อนี้ไหมครับ/คะ?", question.id);
    }
    saveState();
    render();
  })
  .catch(err => {
    console.error(err);
    state.ai.isTyping = false;
    const answer = answerFor(question.id);
    const followup = buildAdaptiveFollowup(question, answer, "manual");
    if (!followup) {
      addAIMessage(
        "assistant",
        "จากคำตอบตอนนี้ประเด็นหลักค่อนข้างครอบคลุมแล้วครับ/ค่ะ ถ้าไม่มีเรื่องอยากเล่าเพิ่ม ผมจะขยับไปคำถามถัดไปได้เลย",
        question.id
      );
    } else {
      recordFollowup(answer, followup.id);
      addAIMessage("assistant", followup.text, question.id);
    }
    saveState();
    render();
  });
}

function moveAINext(addMessage = true) {
  const index = aiCurrentIndex();
  if (index >= guide.length - 1) {
    state.ai.completed = true;
    state.ai.started = false;
    if (addMessage) {
      addAIMessage(
        "assistant",
        "ครบทุกข้อแล้วครับ/ค่ะ ขอบคุณสำหรับข้อมูลทั้งหมด ระบบได้เก็บคำตอบและบทสนทนาไว้แล้ว สามารถส่งข้อมูลเข้าเซอร์เวอร์ได้ทันที",
      );
    }
    pauseTimer();
    saveState();
    render();
    
    // Auto extract interview data when chat finishes naturally
    extractInterviewData();
    return;
  }

  const nextQuestion = guide[index + 1];
  state.ai.currentId = nextQuestion.id;
  state.currentId = nextQuestion.id;
  if (addMessage) {
    addAIMessage(
      "assistant",
      `ขอบคุณครับ/ค่ะ ต่อไปขอถามข้อ ${nextQuestion.id.replace("q", "").replace("-", ".")}: ${nextQuestion.title}`,
      nextQuestion.id,
    );
  }
  saveState();
  render();
}

function sendChatMessage() {
  if (!hasInterviewConsent()) {
    showConsentRequired();
    return;
  }
  if (!hasRespondentProfile()) {
    showRespondentRequired();
    return;
  }

  const input = document.querySelector("[data-chat-input]");
  const text = input?.value.trim();
  if (!text) return;

  if (input) input.value = "";

  if (!state.ai.started) {
    state.ai.started = true;
    startTimer();
  }

  const question = aiCurrentQuestion();
  addAIMessage("user", text, question.id);
  appendAnswerFromChat(question.id, text);

  state.ai.isTyping = true;
  saveState();
  render();

  fetch(`${API_BASE_URL}/api/chat/followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      messages: state.ai.messages,
      currentQuestion: question
    })
  })
  .then(res => {
    if (!res.ok) throw new Error("การเชื่อมต่อเซิร์ฟเวอร์ล้มเหลว");
    return res.json();
  })
  .then(data => {
    state.ai.isTyping = false;
    if (data.shouldMoveToNext) {
      if (data.response) {
        addAIMessage("assistant", data.response, question.id);
      }
      const idx = aiCurrentIndex();
      if (idx >= guide.length - 1) {
        state.ai.completed = true;
        state.ai.started = false;
        if (!data.response) {
          addAIMessage(
            "assistant",
            "ครบทุกข้อแล้วครับ/ค่ะ ขอบคุณสำหรับข้อมูลทั้งหมด ระบบได้เก็บคำตอบและบทสนทนาไว้แล้ว สามารถส่งข้อมูลเข้าเซอร์เวอร์ได้ทันที",
          );
        }
        pauseTimer();
        saveState();
        render();
        extractInterviewData();
      } else {
        const nextQuestion = guide[idx + 1];
        state.ai.currentId = nextQuestion.id;
        state.currentId = nextQuestion.id;
        if (data.response) {
          addAIMessage("assistant", data.response, nextQuestion.id);
        } else {
          addAIMessage(
            "assistant",
            `ขอบคุณครับ/ค่ะ ต่อไปขอถามข้อ ${nextQuestion.id.replace("q", "").replace("-", ".")}: ${nextQuestion.title}`,
            nextQuestion.id,
          );
        }
        saveState();
        render();
      }
    } else {
      if (data.response) {
        addAIMessage("assistant", data.response, question.id);
      } else {
        addAIMessage("assistant", "ช่วยเล่ารายละเอียดเพิ่มเติมในประเด็นนี้หน่อยได้ไหมครับ/คะ?", question.id);
      }
      saveState();
      render();
    }
  })
  .catch(err => {
    console.error(err);
    state.ai.isTyping = false;
    const answer = answerFor(question.id);
    const followup = buildAdaptiveFollowup(question, answer);

    if (followup && shouldAskAnotherFollowup(question, answer, text)) {
      recordFollowup(answer, followup.id);
      addAIMessage("assistant", followup.text, question.id);
    } else {
      moveAINext(true);
      return;
    }
    saveState();
    render();
  });
}

let recognition = null;
let isListening = false;

function toggleSpeechRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    showToast("เบราว์เซอร์นี้ไม่รองรับการพิมพ์ด้วยเสียง แนะนำให้ใช้แป้นพิมพ์ของระบบแทน");
    return;
  }

  const micButton = document.querySelector("[data-action='toggle-mic']");
  const input = document.querySelector("[data-chat-input]");

  if (isListening) {
    if (recognition) {
      recognition.stop();
    }
    return;
  }

  try {
    recognition = new SpeechRecognition();
    recognition.lang = "th-TH";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isListening = true;
      if (micButton) {
        micButton.classList.add("warning");
        const label = micButton.querySelector("span");
        if (label) label.textContent = "กำลังฟัง (คลิกเพื่อหยุด)";
      }
      showToast("เริ่มฟังเสียงพูดภาษาไทยแล้ว...");
    };

    recognition.onresult = (event) => {
      let textSegment = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          textSegment += event.results[i][0].transcript;
        }
      }

      if (textSegment && input) {
        const currentText = input.value.trim();
        input.value = currentText ? `${currentText} ${textSegment}` : textSegment;
        input.dispatchEvent(new Event("input", { bubbles: true }));
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      if (event.error === "not-allowed") {
        showToast("ไม่ได้รับอนุญาตให้ใช้ไมโครโฟน กรุณาเปิดสิทธิ์ไมโครโฟนในเบราว์เซอร์");
      } else {
        showToast("เกิดข้อผิดพลาดในการฟังเสียง: " + event.error);
      }
      stopListeningUI();
    };

    recognition.onend = () => {
      stopListeningUI();
    };

    recognition.start();
  } catch (e) {
    console.error("Speech recognition init failed:", e);
    showToast("ไม่สามารถเปิดใช้งานไมโครโฟนได้");
    stopListeningUI();
  }
}

function stopListeningUI() {
  isListening = false;
  const micButton = document.querySelector("[data-action='toggle-mic']");
  if (micButton) {
    micButton.classList.remove("warning");
    const label = micButton.querySelector("span");
    if (label) label.textContent = "พูดคำตอบ";
  }
}

function refreshTimer() {
  const timer = document.querySelector("#timerValue");
  if (timer) timer.textContent = formatDuration(elapsedMs());
}

function startTimer() {
  if (!hasInterviewConsent()) {
    showConsentRequired();
    return;
  }
  if (!hasRespondentProfile()) {
    showRespondentRequired();
    return;
  }

  if (!state.timer.running) {
    state.timer.running = true;
    state.timer.startedAt = Date.now();
    saveState();
    render();
  }
}

function pauseTimer() {
  if (state.timer.running) {
    state.timer.elapsedMs = elapsedMs();
    state.timer.running = false;
    state.timer.startedAt = null;
    saveState();
    render();
  }
}

function acceptConsent() {
  markConsentAccepted();
  saveState();
  render();
  showToast("บันทึกความยินยอมแล้ว กรุณากรอกข้อมูลผู้ให้สัมภาษณ์ก่อนเริ่ม");
}

function declineConsent() {
  state.consent.participation = false;
  state.consent.acceptedAt = null;
  state.consent.declinedAt = new Date().toISOString();
  state.ai.started = false;
  if (state.timer.running) {
    state.timer.elapsedMs = elapsedMs();
    state.timer.running = false;
    state.timer.startedAt = null;
  }
  saveState();
  render();
  showToast("ยังไม่เริ่มสัมภาษณ์ เพราะผู้เข้าร่วมยังไม่ยินยอม");
}

function navigate(direction) {
  const index = currentIndex();
  const nextIndex = index + direction;
  if (nextIndex >= 0 && nextIndex < guide.length) {
    state.currentId = guide[nextIndex].id;
    state.helperText = "";
    saveState();
    render();
  }
}

function showToast(message) {
  const toast = document.querySelector("#toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2400);
}

function syncChatViewport() {
  if (state.view !== "ai") return;
  const scrollToLatest = () => {
    const chatLog = document.querySelector("[data-chat-log]");
    if (!chatLog) return;
    chatLog.scrollTop = chatLog.scrollHeight;
  };

  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(scrollToLatest);
  } else {
    setTimeout(scrollToLatest, 0);
  }
}

function buildMarkdown() {
  const r = state.respondent;
  const consentText = [
    state.consent.informed ? "อธิบายวัตถุประสงค์แล้ว" : "ยังไม่ยืนยันการอธิบายวัตถุประสงค์",
    state.consent.participation ? "ยินยอมเข้าร่วมโดยสมัครใจ" : "ยังไม่ยืนยันความยินยอมเข้าร่วม",
    state.consent.privacy ? "แจ้งการเก็บข้อมูลเป็นความลับแล้ว" : "ยังไม่ยืนยันการแจ้งความลับ",
    state.consent.audio ? "อนุญาตบันทึกเสียง" : "ไม่ระบุ/ไม่อนุญาตบันทึกเสียง",
    state.consent.acceptedAt
      ? `บันทึกความยินยอมเมื่อ ${new Date(state.consent.acceptedAt).toLocaleString("th-TH")}`
      : "ยังไม่มีเวลาบันทึกความยินยอม",
  ].join("; ");

  const lines = [
    "# บันทึกการสัมภาษณ์เชิงลึก ฉลากชัวร์",
    "",
    `วันที่บันทึก/ส่งข้อมูล: ${new Date().toLocaleString("th-TH")}`,
    `ผู้สัมภาษณ์: ${state.interviewer || "-"}`,
    `ระยะเวลาสัมภาษณ์: ${formatDuration(elapsedMs())}`,
    `สถานะความยินยอม: ${consentText}`,
    "",
    "## ข้อมูลผู้ให้สัมภาษณ์",
    `- รหัสผู้ให้สัมภาษณ์: ${r.code || "-"}`,
    `- ประเภทใบอนุญาต: ${r.license || "-"}`,
    `- ระยะเวลาดำเนินกิจการ: ${r.duration || "-"}`,
    `- ประเภทอาหารที่ผลิต: ${r.foodType || "-"}`,
    `- จำนวนผลิตภัณฑ์ที่มีฉลาก: ${r.productCount || "-"}`,
    `- ตำแหน่งผู้รับผิดชอบในการทำฉลาก: ${r.role || "-"}`,
    `- ประเภทกิจการ: ${r.businessType || "-"}`,
    `- วิธีจัดทำฉลาก: ${r.methods.length ? r.methods.join(", ") : "-"}${r.methodOther ? ` (${r.methodOther})` : ""}`,
    "",
    "## คำตอบรายข้อ",
  ];

  guide.forEach((question) => {
    const answer = answerFor(question.id);
    lines.push("");
    lines.push(`### ${question.id.replace("q", "").replace("-", ".")} ${question.short}`);
    lines.push(`คำถามหลัก: ${question.title}`);
    lines.push("");
    lines.push("คำถามเพื่อเจาะลึกที่ถามแล้ว:");
    const asked = question.probes.filter((_, index) => answer.probes.includes(index));
    if (asked.length) {
      asked.forEach((probe) => lines.push(`- ${probe}`));
    } else {
      lines.push("- ยังไม่ได้ทำเครื่องหมาย");
    }
    lines.push("");
    lines.push("บันทึกคำตอบ:");
    lines.push(answer.answer.trim() || "-");
    lines.push("");
    lines.push("สรุปประเด็นสำคัญ:");
    lines.push(answer.summary.trim() || "-");
    lines.push("");
    const coverage = coverageFor(question.id, answer).covered.map((item) => item.label);
    lines.push(`ประเด็นที่ครอบคลุมจาก AI chat: ${coverage.length ? coverage.join(", ") : "-"}`);
    lines.push("");
    lines.push(`แท็ก: ${answer.tags.length ? answer.tags.join(", ") : "-"}`);
  });

  if (state.ai.messages.length) {
    lines.push("");
    lines.push("## บทสนทนา AI สัมภาษณ์ผ่านแชท");
    state.ai.messages.forEach((message) => {
      const question = guide.find((item) => item.id === message.questionId);
      const role = message.role === "assistant" ? "AI ผู้สัมภาษณ์" : "ผู้ให้สัมภาษณ์";
      const questionLabel = question ? `ข้อ ${question.id.replace("q", "").replace("-", ".")}` : "-";
      lines.push("");
      lines.push(`**${role} (${questionLabel})**`);
      lines.push(message.text);
    });
  }

  return lines.join("\n");
}

function buildSubmissionPayload() {
  const content = buildMarkdown();
  const code = state.respondent.code?.trim() || "interview";
  return {
    markdown: content,
    respondentCode: code,
    submittedAt: new Date().toISOString(),
    elapsedMs: elapsedMs(),
    respondent: state.respondent,
    consent: state.consent,
    interviewer: state.interviewer,
    answers: state.answers,
    ai: state.ai,
  };
}

async function submitInterview() {
  if (!hasInterviewConsent()) {
    showConsentRequired();
    return;
  }
  if (!hasRespondentProfile()) {
    showRespondentRequired();
    return;
  }

  const payload = buildSubmissionPayload();
  const isStaticGithubPages = window.location.hostname.endsWith("github.io");

  if (isStaticGithubPages && !API_BASE_URL) {
    showToast("GitHub Pages ต้องต่อ backend เพิ่มก่อน จึงจะบันทึกไฟล์ .md ได้");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/interviews`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.error || "บันทึกข้อมูลไม่สำเร็จ");
    }

    showToast(`บันทึกเข้าเซอร์เวอร์แล้ว: ${result.filename}`);
  } catch (error) {
    const isFileMode = window.location.protocol === "file:";
    showToast(
      isFileMode
        ? "ต้องเปิดแอปผ่าน server จึงจะส่งข้อมูลเข้าโฟลเดอร์กลางได้"
        : error.message || "ส่งข้อมูลไม่สำเร็จ",
    );
  }
}

async function extractInterviewData() {
  if (!state.ai.messages.length) {
    showToast("ไม่มีข้อความสนทนาที่จะดึงข้อมูล");
    return;
  }

  state.isExtracting = true;
  saveState();
  render();

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages: state.ai.messages
      })
    });

    const result = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(result.error || "ดึงข้อมูลจากบทสนทนาไม่สำเร็จ");
    }

    if (result.answers) {
      Object.keys(result.answers).forEach((questionId) => {
        if (state.answers[questionId]) {
          const extracted = result.answers[questionId];
          state.answers[questionId].answer = extracted.answer || "";
          state.answers[questionId].summary = extracted.summary || "";
          state.answers[questionId].tags = Array.isArray(extracted.tags) ? extracted.tags : [];
          state.answers[questionId].probes = Array.isArray(extracted.probes) ? extracted.probes : [];
        }
      });
      showToast("ดึงข้อมูลสำเร็จและกรอกฟอร์มแล้ว!");
    } else {
      throw new Error("รูปแบบข้อมูลที่ได้รับไม่ถูกต้อง");
    }
  } catch (error) {
    console.error(error);
    showToast(error.message || "เกิดข้อผิดพลาดในการดึงข้อมูล");
  } finally {
    state.isExtracting = false;
    saveState();
    render();
  }
}

function clearCurrent() {
  const question = currentQuestion();
  state.answers[question.id] = {
    answer: "",
    summary: "",
    probes: [],
    tags: [],
    coverage: [],
    aiFollowups: [],
  };
  state.helperText = "";
  saveState();
  render();
}

function resetAll() {
  const keepTimer = window.confirm("ต้องการล้างข้อมูลสัมภาษณ์ทั้งหมดในเครื่องนี้หรือไม่?");
  if (!keepTimer) return;
  state = normalizeState(blankState);
  localStorage.removeItem(STORAGE_KEY);
  render();
  showToast("ล้างข้อมูลเรียบร้อยแล้ว");
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;

  const action = button.dataset.action;
  const consentGuardedActions = new Set([
    "set-view",
    "start-timer",
    "start-ai",
    "ask-ai-probe",
    "ai-next",
    "finish-ai",
    "extract-ai",
    "toggle-mic",
    "send-chat",
    "submit",
  ]);

  if (action === "accept-consent") {
    acceptConsent();
    return;
  }

  if (action === "decline-consent") {
    declineConsent();
    return;
  }

  if (action === "confirm-respondent") {
    if (!hasInterviewConsent()) {
      showConsentRequired();
      return;
    }
    if (!hasRespondentProfile()) {
      showRespondentRequired();
      return;
    }
    saveState();
    if (state.timer.running) {
      render();
    } else {
      startTimer();
    }
    showToast("บันทึกข้อมูลผู้ให้สัมภาษณ์แล้ว เริ่มสัมภาษณ์ได้");
    return;
  }

  if (consentGuardedActions.has(action) && !hasInterviewConsent()) {
    showConsentRequired();
    return;
  }
  if (consentGuardedActions.has(action) && !hasRespondentProfile()) {
    showRespondentRequired();
    return;
  }

  const question = currentQuestion();
  const answer = answerFor(question.id);

  if (action === "set-view") {
    state.view = button.dataset.view;
    if (state.view === "ai") state.currentId = state.ai.currentId;
    saveState();
    render();
  }
  if (action === "start-timer") startTimer();
  if (action === "pause-timer") pauseTimer();
  if (action === "start-ai") startAIInterview(state.ai.completed);
  if (action === "ask-ai-probe") askAIProbe();
  if (action === "ai-next") moveAINext();
  if (action === "finish-ai") {
    state.ai.completed = true;
    state.ai.started = false;
    addAIMessage(
      "assistant",
      "ผมจะจบการสัมภาษณ์ไว้ตรงนี้ครับ/ค่ะ ระบบได้เก็บข้อมูลบทสนทนาและคำตอบรายข้อไว้แล้ว",
    );
    pauseTimer();
    saveState();
    render();
    
    // Auto extract interview data when finishing manually
    extractInterviewData();
  }
  if (action === "extract-ai") {
    extractInterviewData();
  }
  if (action === "toggle-mic") {
    toggleSpeechRecognition();
  }
  if (action === "send-chat") sendChatMessage();
  if (action === "save") saveState(true);
  if (action === "submit") submitInterview();
  if (action === "prev") navigate(-1);
  if (action === "next") navigate(1);
  if (action === "clear-current") clearCurrent();
  if (action === "suggest") {
    state.helperText = buildSuggestion(question, answer);
    saveState();
    render();
    showToast("เลือกคำถามถามต่อให้แล้ว");
  }
  if (action === "go") {
    state.currentId = button.dataset.id;
    if (state.view === "ai") state.ai.currentId = button.dataset.id;
    state.helperText = "";
    saveState();
    render();
  }
  if (action === "tag") {
    const target = answerFor(button.dataset.id);
    const tag = button.dataset.tag;
    target.tags = target.tags.includes(tag)
      ? target.tags.filter((item) => item !== tag)
      : [...target.tags, tag];
    saveState();
    render();
  }
  if (action === "reset") resetAll();
});

document.addEventListener("input", (event) => {
  const target = event.target;
  if (target.matches("[data-answer]")) {
    state.answers[target.dataset.answer].answer = target.value;
    state.helperText = "";
    saveState();
  }
  if (target.matches("[data-summary]")) {
    state.answers[target.dataset.summary].summary = target.value;
    saveState();
  }
  if (target.matches("[data-respondent]")) {
    state.respondent[target.dataset.respondent] = target.value;
    saveState();
  }
});

document.addEventListener("change", (event) => {
  const target = event.target;
  if (target.matches("[data-respondent]")) {
    state.respondent[target.dataset.respondent] = target.value;
    saveState();
  }
  if (target.matches("[data-consent]")) {
    const key = target.dataset.consent;
    state.consent[key] = target.checked;
    if (hasInterviewConsent()) {
      state.consent.declinedAt = null;
      if (!state.consent.acceptedAt) {
        state.consent.acceptedAt = new Date().toISOString();
      }
    } else if (["informed", "participation", "privacy"].includes(key)) {
      state.consent.acceptedAt = null;
      state.ai.started = false;
      if (state.timer.running) {
        state.timer.elapsedMs = elapsedMs();
        state.timer.running = false;
        state.timer.startedAt = null;
      }
    }
    saveState();
    render();
  }
  if (target.matches("[data-method]")) {
    const method = target.dataset.method;
    state.respondent.methods = target.checked
      ? [...new Set([...state.respondent.methods, method])]
      : state.respondent.methods.filter((item) => item !== method);
    saveState();
  }
  if (target.matches("[data-probe]")) {
    const questionId = target.dataset.probe;
    const probeIndex = Number(target.dataset.probeIndex);
    const answer = answerFor(questionId);
    answer.probes = target.checked
      ? [...new Set([...answer.probes, probeIndex])]
      : answer.probes.filter((index) => index !== probeIndex);
    saveState();
    render();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.target.matches?.("[data-chat-input]") && event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
    return;
  }

  const isTyping = ["TEXTAREA", "INPUT", "SELECT"].includes(document.activeElement?.tagName);
  if (isTyping) return;
  if (event.key === "ArrowLeft") navigate(-1);
  if (event.key === "ArrowRight") navigate(1);
});

setInterval(refreshTimer, 1000);
render();
