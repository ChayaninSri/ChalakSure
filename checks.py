# checks.py
import re

# ตรวจสอบข้อความเกี่ยวกับวันหมดอายุ
def check_expiry_phrases(ocr_text):
    keywords = ["หมดอายุ", "ควรบริโภคก่อน"]
    return not any(kw in ocr_text for kw in keywords)

# ตรวจสอบข้อความเกี่ยวกับปริมาณสุทธิ
def check_packsize_phrases(ocr_text):
    keywords = ["ปริมาตร", "น้ำหนัก"]
    return not any(kw in ocr_text for kw in keywords)

def check_registration_number(ocr_text):
    pattern = r"\d{2}\s*-\s*\d{1}\s*-\s*\d{5}\s*-\s*\d{1}\s*-\s*\d{4}"
    return not re.search(pattern, ocr_text)

def check_producer(ocr_text):
    keywords = ["ผลิตโดย", "ผู้ผลิต", "นำเข้า", "สำนักงานใหญ่"]
    return not any(kw in ocr_text for kw in keywords)

def check_ingredients(ocr_text):
    keywords = ["ประกอบด้วย", "ส่วนประกอบ", "โดยประมาณ"]
    return not any(kw in ocr_text for kw in keywords)

# ตรวจสอบคำเตือนสำหรับผู้แพ้อาหาร
def check_allergy_warning(ocr_text):
    keywords = ["แพ้อาหาร"]
    return not any(kw in ocr_text for kw in keywords)

# สามารถเพิ่มฟังก์ชันใหม่ๆ ได้ที่นี่ โดยใช้โครงสร้างเดียวกัน
