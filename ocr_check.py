import base64
import json
import os
from typing import List, Dict, Any, Optional

import requests
import streamlit as st


# หมายเหตุสำคัญสำหรับการตั้งค่า
# - หากคุณใช้ Google AI Studio (Generative Language API / Gemini):
#   ใส่ค่า API Key ในช่องด้านซ้าย หรือกำหนดเป็นตัวแปรแวดล้อมชื่อ GOOGLE_API_KEY
#   รูปแบบปลายทาง (Endpoint) เริ่มต้นจะเป็น
#   https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}
# - หากคุณใช้ปลายทาง/โมเดลที่ปรับแต่งเอง ให้แก้ URL/Headers ในส่วน Config ด้านล่าง


# รายการโมเดลที่แนะนำให้ลอง (ไล่ลำดับจากตัวที่มีโอกาสเปิดใน Free Tier มากที่สุดไปน้อยที่สุด)
FALLBACK_MODELS = [
    "gemini-2.0-flash",       # รุ่นใหม่ล่าสุด
    "gemini-1.5-flash",       # รุ่น flash พื้นฐาน
    "gemini-2.5-flash",       # อาจจะโดนจำกัด
]

DEFAULT_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
LOCKED_PROMPT = "ตรวจสอบเบื้องต้นจากภาพฉลาก"


def _b64(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


def _extract_text_from_glm_response(data: Dict[str, Any]) -> str:
    try:
        parts = data.get("candidates", [])[0].get("content", {}).get("parts", [])
        texts = []
        for p in parts:
            if "text" in p:
                texts.append(p["text"])
        return "\n\n".join(texts).strip() or json.dumps(data, ensure_ascii=False)
    except Exception:
        return json.dumps(data, ensure_ascii=False)


def _build_glm_payload(user_text: str, images: Optional[List[tuple]]) -> Dict[str, Any]:
    parts: List[Dict[str, Any]] = []
    if user_text:
        parts.append({"text": user_text})
        
    if images:
        for image_bytes, image_mime in images:
            if image_bytes and image_mime:
                parts.append({
                    "inline_data": {
                        "mime_type": image_mime,
                        "data": _b64(image_bytes),
                    }
                })

    system_instruction = """{
  "instructions": "คุณคือ AI ผู้เชี่ยวชาญด้านกฎหมายอาหารของประเทศไทย หน้าที่ของคุณคือวิเคราะห์และตรวจสอบฉลากอาหารที่ผู้ใช้อัปโหลดว่าถูกต้องหรือไม่ โดยอ้างอิงตามประกาศกระทรวงสาธารณสุข ฉบับที่ 450 พ.ศ. 2567 และแนวทางปฏิบัติล่าสุดที่เกี่ยวข้อง คุณต้องระบุชัดเจนว่าฉลากมีข้อผิดพลาดหรือขาดข้อมูลใดบ้าง พร้อมอ้างข้อกฎหมายที่เกี่ยวข้อง",
  "input": "ฉลากอาหารที่ผู้ใช้อัปโหลด",
  "output": "รายงานผลการตรวจสอบฉลากอาหาร โดยแสดงเป็น bullet ว่า ✅ มีข้อมูลครบถ้วนข้อใด และ ❌ ขาดหรือผิดข้อใด พร้อมอ้างอิงประกาศที่เกี่ยวข้อง และสรุปว่าฉลากถูกต้องหรือไม่ตามกฎหมาย พร้อมทิ้งท้ายข้อความว่า 'การตรวจสอบนี้อาจมีความผิดพลาดได้จากความชัดเจนของรูปภาพ และไม่ถือเป็นการรับรองฉลากอย่างเป็นทางการ ผู้ใช้งานควรตรวจสอบประกาศกระทรวงสาธารณสุขที่เกี่ยวข้องเพิ่มเติมทุกครั้ง'",
  "criteria": [
    "1. ชื่ออาหาร: ต้องมีชื่อภาษาไทย (ชื่อเฉพาะ/ชื่อสามัญ) หากมีชื่อการค้า ต้องระบุคำว่า ตรา/เครื่องหมายการค้า/TM/Brand/(R) และต้องแสดงอย่างชัดเจน อ่านง่าย ตำแหน่งไม่ทำให้เข้าใจผิด",
    "2. เลขสารบบอาหาร (อย.): ต้องแสดงเลขสารบบอาหาร 13 หลักครบถ้วน ตรงตามระบบของ อย.",
    "3. ชื่อและที่ตั้งผู้ผลิต/ผู้นำเข้า/สำนักงานใหญ่: ต้องระบุพร้อมข้อความกำกับ เช่น 'ผู้ผลิต' 'ผลิตโดย' 'ผู้นำเข้า' 'สำนักงานใหญ่' หรือ 'สถานที่ผลิต' อย่างชัดเจน",
    "4. ปริมาณสุทธิ: ต้องระบุเป็นภาษาไทย เช่น 'น้ำหนักสุทธิ ... กรัม' หรือ 'ปริมาตรสุทธิ ... มิลลิลิตร' ห้ามใช้เฉพาะภาษาอังกฤษ เช่น 'Net Weight ... g' โดยไม่มีข้อความภาษาไทย",
    "5. วันผลิต/วันหมดอายุ/ควรบริโภคก่อน: ต้องแสดงคำภาษาไทยกำกับ เช่น 'ผลิต' 'หมดอายุ' หรือ 'ควรบริโภคก่อน' หากไม่พิมพ์บนฉลากตรง ๆ ต้องระบุว่าดูวันที่ได้ที่ส่วนใดของบรรจุภัณฑ์ การแสดงวัน เดือน ปี ต้องเรียงตามที่กฎหมายกำหนด",
    "6. ส่วนประกอบสำคัญ: ต้องระบุเป็นร้อยละของน้ำหนักโดยประมาณ ยกเว้นที่กฎหมายยกเว้น ต้องแสดงชื่อวัตถุเจือปนอาหารพร้อมกลุ่มหน้าที่และ INS code หรือชื่อเฉพาะ เช่น 'วัตถุกันเสีย (INS211)' หรือ 'วัตถุให้ความหวานแทนน้ำตาล (แอสพาร์เทม)'",
    "7. ข้อมูลสำหรับผู้แพ้อาหาร: หากมีสารก่อภูมิแพ้ 10 กลุ่ม ต้องแสดง 'ข้อมูลสำหรับผู้แพ้อาหาร : มี…' หรือ 'อาจมี…' ครบถ้วน ได้แก่ (1) ธัญพืชที่มีกลูเตน (ข้าวสาลี ข้าวไรย์ ข้าวบาร์เลย์ ข้าวโอ๊ต) (2) สัตว์น้ำที่มีเปลือกแข็ง (กุ้ง ปู หอย) (3) ไข่ (4) ปลา (5) ถั่วลิสง (6) ถั่วเหลือง (7) น้ำนมโค/ผลิตภัณฑ์นม (8) ถั่วเปลือกแข็ง (อัลมอนด์ มะม่วงหิมพานต์ วอลนัต เฮเซลนัท ฯลฯ) (9) งา (10) ซัลไฟต์ ≥ 10 มก./กก. หรือ มก./ลิตร ทั้งนี้ หากชื่ออาหารระบุสารก่อภูมิแพ้อย่างชัดเจนแล้ว (เช่น 'ปลาย่าง' 'น้ำนมโค') ถือว่าเข้าข้อยกเว้น ไม่ต้องแสดงซ้ำ และห้ามสันนิษฐานสารก่อภูมิแพ้อื่นที่ไม่อยู่ในบัญชี 10 กลุ่มนี้",
    "8. คำเตือนบนฉลากอาหาร:\n   แบ่งออกเป็น 2 กลุ่มหลักที่ต้องตรวจสอบอย่างละเอียด\n   \n   (ก) คำเตือนที่ขึ้นกับประเภทอาหาร:\n       • อาหารขบเคี้ยว (มันฝรั่งทอด/อบกรอบ, ข้าวโพดคั่ว/อบกรอบ, ข้าวเกรียบทอด/อบกรอบ/อบพอง, ถั่ว/นัต/เมล็ดพืชอบเกลือ/ทอด/อบกรอบ/เคลือบ, สาหร่ายทอด/อบกรอบ/ปรุงรส, เนื้อสัตว์อบกรอบ/ปรุงรส, อาหารผสมตามรายการ) → ต้องมีคำเตือน “บริโภคแต่น้อยและออกกำลังกายเพื่อสุขภาพ” ตัวอักษรหนาทึบ สีตัวอักษรต้องตัดกับสีพื้นกรอบ และสีกรอบต้องตัดกับพื้นฉลาก\n       • ช็อกโกแลตและขนมหวานรสช็อกโกแลต → ต้องมีคำเตือน “บริโภคแต่น้อยและออกกำลังกายเพื่อสุขภาพ” เช่นเดียวกัน\n       • ผลิตภัณฑ์ขนมอบ (ขนมปังกรอบ/แครกเกอร์/บิสกิต, เวเฟอร์สอดไส้, คุกกี้, เค้ก, เพสตรี/พาย) → ต้องมีคำเตือน “บริโภคแต่น้อยและออกกำลังกายเพื่อสุขภาพ” เช่นเดียวกัน\n       • ผลิตภัณฑ์เสริมอาหาร → ต้องมีคำเตือนครบชุด ได้แก่ “คำเตือน” ในกรอบ + “เด็กและสตรีมีครรภ์ไม่ควรรับประทาน” + “ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ” + “ไม่มีผลในการป้องกันหรือรักษาโรค” (จัดรูปแบบตามเกณฑ์: กรอบ, สีตัวอักษร, ขนาด)\n   • ผลิตภัณฑ์รอยัลเยลลี → ต้องมีคำเตือน \"“ผู้ที่เป็นโรคหอบหืดหรือโรคภูมิแพ้ ไม่ควรรับประทาน เพราะอาจเกิดอาการแพ้อย่างรุนแรง”  • วุ้นสำเร็จรูป/เยลลี่ → ต้องมีข้อความ “เด็กควรบริโภคแต่น้อย” ตัวอักษรสีแดง ขนาดไม่เล็กกว่า 5 มม. อยู่ในกรอบพื้นสีขาว\n\n   (ข) คำเตือนที่ขึ้นกับส่วนประกอบ:\n       • อาหารที่มีวัตถุรักษาคุณภาพ/ซองกันชื้น → ต้องมีข้อความ “มีซองกันชื้น” ตัวอักษรสีแดง ขนาด ≥ 3 มม. พื้นขาว\n       • อาหารที่ใช้แอสพาร์เทม → ต้องมีข้อความ “ผู้ที่มีสภาวะฟินิลคีโตนูเรีย ผลิตภัณฑ์นี้มีฟินิลอะลานีน”\n       • อาหารที่เติมไฟโตสเตอรอล/แพลนท์สตานอล → ต้องแสดงข้อความใกล้ชื่ออาหารเกี่ยวกับปริมาณที่เติม และต้องมีคำเตือนสีแดงในกรอบตามที่กำหนด\n       • เมล็ดเชีย → ต้องมีข้อความ “บริโภคไม่เกินวันละ 15 กรัม และดื่มน้ำตาม 1–2 แก้ว”\n       • ว่านหางจระเข้ → ต้องมีข้อความ “เด็กไม่ควรรับประทาน” + “ไม่ใช่อาหารทางการแพทย์” + “หยุดบริโภคเมื่อมีอาการผิดปกติ”\n       • ใบแป๊ะก๊วย/สารสกัดจากแป๊ะก๊วย → ต้องมีข้อความ “อาจมีผลให้เลือดแข็งตัวช้า” + “เด็กและสตรีมีครรภ์ไม่ควรรับประทาน”\n       • แก่นตะวัน → ต้องมีข้อความ “บริโภคปริมาณมากอาจทำให้ท้องอืด ท้องเฟ้อได้”\n       • ผักเชียงดาอบแห้ง/อาหารที่มีผักเชียงดาอบแห้ง → ต้องมีข้อความ “เด็กและสตรีมีครรภ์ไม่ควรรับประทาน” + “ผู้ป่วยเบาหวานควรปรึกษาแพทย์ก่อนรับประทาน” + “ไม่ควรรับประทานติดต่อกันเกิน 1 เดือน”\n\n   (ค) หากอาหารไม่เข้าข่ายข้อ (ก) หรือ (ข) ให้สรุปว่า “ไม่อยู่ในประเภทที่ต้องมีคำเตือนเฉพาะ”",
    "9. ข้อความแนะนำการเก็บรักษาและวิธีปรุง (ถ้ามี): หากอาหารต้องมีวิธีเก็บรักษาหรือวิธีปรุงเพื่อรับประทาน ต้องแสดงข้อความเหล่านี้ให้ครบถ้วนตามข้อ 5 (11)-(12) ของประกาศ 450",
    "10. การกล่าวอ้างสรรพคุณ: ห้ามใช้ข้อความที่สื่อถึงการป้องกัน บำบัด รักษา หรือบรรเทาโรค เช่น 'ลดน้ำตาลในเลือด' 'ป้องกันหวัด' หากพบถือว่าผิดตามข้อ 4 ของประกาศ 450 (ต้องลบออกทันที ไม่แนะนำข้อความทดแทน)",
    "11. การแสดงข้อมูลโภชนาการ (ถ้ามี): หากมีการแสดงโภชนาการ ต้องตรงตามประกาศกระทรวงสาธารณสุขที่เกี่ยวข้อง (เช่น ฉบับ 394, 445, 447) และต้องแสดงคำกล่าวอ้างเป็นาภาษาไทย (เช่น โปรตีนสูง) และกรณีที่มีการ Disclaim (เช่น มีไขมัน...กรัม ต่ออาหาร...กรัม) ต้องแสดงข้อความ Disclaim ไว้ควบคู่กับข้อความกล่าวอ้าง นอกจากนี้ให้แนะนำผู้ใช้ให้ตรวจสอบเพิ่มเติมในแอปฉลากชัวร์ เมนู'ตรวจสอบข้อความกล่าวอ้างโภชนาการ'",
    "12. การแสดงโภชนาการและฉลาก GDA: หากแสดง Nutrition Facts หรือฉลาก GDA (Guideline Daily Amounts) กรอบข้อมูลต้องมีพื้นเป็นสีขาวตามที่กฎหมายกำหนด ห้ามใช้สีพื้นอื่น",
    "13. การแสดงรูปภาพบนฉลาก: ต้องไม่แสดงรูปภาพสื่อถึงการป้องกัน บำบัด รักษา หรือบรรเทาโรค เช่น รูปลำไส้ รูปตับ รูปหัวใจ เป็นต้น"
  ],
  "rules": [
    "ห้ามสันนิษฐานสารก่อภูมิแพ้ที่ไม่ได้อยู่ในบัญชี 10 กลุ่มตามกฎหมาย",
    "ห้ามให้ความเห็นเชิงส่วนตัว เช่น 'ไม่ถือว่าผิด แต่ควรระวัง'",
    "ห้ามเสนอข้อความทดแทนในกรณีที่ข้อความกล่าวอ้างผิดกฎหมาย",
    "ใช้รูปแบบการตอบตามแนวทางตรวจฉลาก (เช็กลิสต์โครงสร้าง: ระบุสิ่งที่ครบ/ยังขาด พร้อมข้อกฎหมายกำกับ)",
    "ห้ามละเว้นข้อความเตือนพิเศษทั้งที่ขึ้นกับประเภทอาหารและที่ขึ้นกับส่วนประกอบ",
    "การตรวจสอบนี้อาจมีความผิดพลาดได้จากความชัดเจนของรูปภาพ และไม่ถือเป็นการรับรองฉลากอย่างเป็นทางการ ผู้ใช้งานควรตรวจสอบประกาศกระทรวงสาธารณสุขที่เกี่ยวข้องเพิ่มเติมทุกครั้ง"
  ]
}"""

    return {
        "system_instruction": {
            "role": "system",
            "parts": [{"text": system_instruction}],
        },
        "contents": [
            {
                "role": "user",
                "parts": parts or [{"text": "กรุณาวิเคราะห์ฉลากอาหารจากรูปภาพทั้งหมดนี้รวมกัน"}],
            }
        ],
    }


def _send_to_google_ai(model: str, api_key: str, api_base: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{api_base}/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    try:
        data = resp.json() if resp.content else {}
    except Exception:
        data = {"raw": resp.text}
    return {"status_code": resp.status_code, "data": data, "model": model}


def _ensure_state():
    if "ocr_chat" not in st.session_state:
        st.session_state["ocr_chat"] = []
    if "ocr_images" not in st.session_state:
        st.session_state["ocr_images"] = []  # เก็บเป็น list ของ (bytes, mime)


def show():
    st.title("ตรวจสอบฉลากจากภาพด้วย AI")
    st.info("กรุณากรอก API Key ในแถบด้านซ้ายให้เรียบร้อยก่อนใช้งานทุกครั้ง")

    _ensure_state()
    api_base = DEFAULT_API_BASE

    with st.sidebar:
        st.markdown("**การเชื่อมต่อ Google AI Studio**")
        api_key = st.text_input(
            "API Key (Google AI Studio)",
            value=os.environ.get("GOOGLE_API_KEY", ""),
            type="password",
            help="ใส่คีย์จาก Google AI Studio"
        )
        
        st.markdown("**ตั้งค่าโมเดล AI (ตัวเลือก)**")
        # ให้ผู้ใช้สามารถเลือกโมเดลเองได้ หรือให้ระบบสุ่มหาอัตโนมัติ
        user_selected_model = st.selectbox("เลือก Model (ปล่อย Auto เพื่อให้ระบบหาเอง)", ["Auto"] + FALLBACK_MODELS)

        if st.button("ล้างประวัติแชต"):
            st.session_state["ocr_chat"] = []
            st.success("ล้างประวัติแล้ว")

    uploaded_files = st.file_uploader("อัปโหลดภาพฉลาก (JPEG/PNG) - อัปโหลดได้หลายภาพ", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    
    if uploaded_files:
        st.session_state["ocr_images"] = []
        # แสดงภาพเป็นคอลัมน์เพื่อให้ดูสวยงาม
        cols = st.columns(min(len(uploaded_files), 3) if len(uploaded_files) > 0 else 1)
        
        for i, file in enumerate(uploaded_files):
            img_bytes = file.read()
            mime = file.type or "image/jpeg"
            st.session_state["ocr_images"].append((img_bytes, mime))
            
            with cols[i % len(cols)]:
                st.image(img_bytes, caption=f"ภาพที่ {i+1}", use_container_width=True)

    for msg in st.session_state["ocr_chat"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["text"])

    send_disabled = len(st.session_state.get("ocr_images", [])) == 0
    if send_disabled:
        st.info("อัปโหลดภาพฉลากก่อน แล้วกดปุ่มเพื่อส่งคำขอวิเคราะห์")
    send_request = st.button("ส่งคำขอวิเคราะห์", use_container_width=True, disabled=send_disabled)

    if send_request:
        user_prompt = LOCKED_PROMPT
        st.session_state["ocr_chat"].append({"role": "user", "text": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        images = st.session_state.get("ocr_images", [])
        payload = _build_glm_payload(user_prompt, images)

        if not api_key:
            assistant_text = "กรุณาใส่ API Key ในแถบด้านซ้ายก่อนที่จะส่งคำขอ"
            st.session_state["ocr_chat"].append({"role": "assistant", "text": assistant_text})
            with st.chat_message("assistant"):
                st.warning(assistant_text)
            return

        with st.spinner("กำลังวิเคราะห์และหาโมเดลที่ใช้งานได้..."):
            models_to_try = [user_selected_model] if user_selected_model != "Auto" else FALLBACK_MODELS
            
            success = False
            last_error = ""
            
            for model_name in models_to_try:
                try:
                    result = _send_to_google_ai(model=model_name, api_key=api_key, api_base=api_base, payload=payload)
                    status = result.get("status_code")
                    data = result.get("data", {})
                    
                    if status == 200:
                        success = True
                        assistant_text = _extract_text_from_glm_response(data)
                        assistant_text = f"*(วิเคราะห์ด้วย {model_name})*\n\n" + assistant_text
                        break
                    else:
                        error_msg = json.dumps(data, ensure_ascii=False)
                        last_error = f"API Error HTTP {status} from {model_name}:\n{error_msg}"
                        # หากเป็น 404 Not Found หรือ 429 Quota Exceeded ให้ลองโมเดลถัดไป
                except Exception as e:
                    last_error = f"Exception with {model_name}: {e}"

            if not success:
                assistant_text = f"ไม่สามารถหาโมเดลที่ใช้งานได้เลย หรือเกิดข้อผิดพลาดทั้งหมด\n\nรายละเอียดข้อผิดพลาดล่าสุด:\n```\n{last_error}\n```"

        st.session_state["ocr_chat"].append({"role": "assistant", "text": assistant_text})
        with st.chat_message("assistant"):
            st.markdown(assistant_text)
