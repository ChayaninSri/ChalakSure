import streamlit as st
import pandas as pd
import re
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION_START
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import io

@st.cache_data
def load_ins_database():
    return pd.read_csv("ins_database.csv", encoding="utf-8-sig")

@st.cache_data
def load_warnings_database():
    return pd.read_csv("warnings_database.csv", encoding="utf-8-sig")

# Define standard colors
COLOR_SUCCESS = RGBColor.from_string("006400")  # Dark Green
COLOR_FAILURE = RGBColor.from_string("8B0000")  # Dark Red
COLOR_WARNING = RGBColor.from_string("FF8C00")  # Dark Orange
COLOR_BLACK = RGBColor.from_string("000000")

TARGET_FONT_NAME = 'TH Sarabun New'
TARGET_FONT_SIZE = Pt(14)

# Helper function to add a styled heading with numbering
def add_styled_heading(document, text, level=1, numbered=True, section_number=""):
    prefix = f"{section_number} " if numbered and section_number else ""
    heading = document.add_heading(f"{prefix}{text}", level=level)
    for run in heading.runs:
        run.font.bold = True 
    heading.paragraph_format.space_after = Pt(6)
    return heading

# Helper function to add a paragraph with specific styling
def add_styled_paragraph(document, text, bold=False, italic=False, color=COLOR_BLACK, alignment=WD_ALIGN_PARAGRAPH.LEFT):
    p = document.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    p.alignment = alignment
    p.paragraph_format.space_after = Pt(4)
    return p

def add_page_numbers(document):
    for section in document.sections:
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fldChar1 = OxmlElement('w:fldChar')
        fldChar1.set(qn('w:fldCharType'), 'begin')
        instrText = OxmlElement('w:instrText')
        instrText.set(qn('xml:space'), 'preserve')
        instrText.text = "PAGE"
        fldChar2 = OxmlElement('w:fldChar')
        fldChar2.set(qn('w:fldCharType'), 'end')
        run = p.add_run()
        run.element.append(fldChar1)
        run.element.append(instrText)
        run.element.append(fldChar2)

def generate_label_word_report(report_data):
    """สร้างรายงาน Word สำหรับการตรวจสอบฉลากอาหาร"""
    document = Document()
    
    # Set default font for the document
    style = document.styles['Normal']
    font = style.font
    font.name = TARGET_FONT_NAME
    font.size = TARGET_FONT_SIZE
    style.paragraph_format.space_after = Pt(4)

    # Main Title
    title_p = document.add_paragraph()
    title_run = title_p.add_run("รายงานผลการตรวจสอบฉลากอาหาร")
    title_run.font.bold = True 
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_after = Pt(12)

    # Add disclaimer box
    disclaimer_p = document.add_paragraph()
    disclaimer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    disclaimer_run = disclaimer_p.add_run("⚠️ คำเตือน: แอปพลิเคชันนี้เป็นตัวช่วยในการคำนวณและตรวจสอบฉลากอาหารเท่านั้น \nไม่สามารถใช้เป็นเงื่อนไขการขออนุญาต หรืออ้างอิงทางกฎหมายได้ \nโปรดปฏิบัติตามกฎหมายอย่างเคร่งครัด")
    disclaimer_run.font.bold = True
    disclaimer_run.font.color.rgb = COLOR_WARNING
    disclaimer_p.paragraph_format.space_after = Pt(18)

    # 1. ข้อมูลพื้นฐาน
    add_styled_heading(document, "ข้อมูลพื้นฐาน", level=2, section_number="1.")
    
    add_styled_paragraph(document, f"ชื่ออาหาร: {report_data.get('food_name', 'ไม่ได้ระบุ')}")
    add_styled_paragraph(document, f"ประเภทอาหาร: {report_data.get('food_type', 'ไม่ได้ระบุ')}")
    add_styled_paragraph(document, f"ลักษณะอาหาร: {report_data.get('food_consistency', 'ไม่ได้ระบุ')}")
    add_styled_paragraph(document, f"เลขสารบบอาหาร: {report_data.get('food_registration_number', 'ไม่ได้ระบุ')}")
    add_styled_paragraph(document, f"อายุเก็บรักษา: {report_data.get('shelf_life_option', 'ไม่ได้ระบุ')}")
    
    if report_data.get('manufacturer_name'):
        add_styled_paragraph(document, f"ผู้ผลิต: {report_data.get('manufacturer_name')}")
    if report_data.get('manufacturer_address'):
        add_styled_paragraph(document, f"ที่ตั้งผู้ผลิต: {report_data.get('manufacturer_address')}")
    
    document.add_paragraph()

    # 2. ส่วนประกอบและวัตถุเจือปนอาหาร
    add_styled_heading(document, "ส่วนประกอบและวัตถุเจือปนอาหาร", level=2, section_number="2.")
    
    # ส่วนประกอบหลัก
    if report_data.get('main_ingredients'):
        add_styled_paragraph(document, "ส่วนประกอบหลัก:", bold=True)
        for i, ingredient in enumerate(report_data.get('main_ingredients', []), 1):
            add_styled_paragraph(document, f"{i}. {ingredient}")
    
    # คำเตือนจากส่วนประกอบหลัก
    if report_data.get('ingredient_warnings'):
        add_styled_paragraph(document, "คำเตือนจากส่วนประกอบหลัก:", bold=True)
        for warning in report_data.get('ingredient_warnings', []):
            add_styled_paragraph(document, f"⚠️ {warning}", color=COLOR_WARNING)
    
    # วัตถุเจือปนอาหาร
    if report_data.get('ins_results'):
        add_styled_paragraph(document, "วัตถุเจือปนอาหาร (INS):", bold=True)
        for ins_result in report_data.get('ins_results', []):
            if ins_result.get('has_special_label'):
                add_styled_paragraph(document, f"⚠️ {ins_result.get('message')}", color=COLOR_WARNING)
            else:
                add_styled_paragraph(document, f"✅ {ins_result.get('message')}", color=COLOR_SUCCESS)
    
    document.add_paragraph()

    # 3. สารก่อภูมิแพ้
    add_styled_heading(document, "สารก่อภูมิแพ้", level=2, section_number="3.")
    
    if report_data.get('has_allergen'):
        allergen_groups = report_data.get('allergen_groups', [])
        if allergen_groups:
            allergen_text = ", ".join(allergen_groups)
            add_styled_paragraph(document, f"มีสารก่อภูมิแพ้: {allergen_text}", color=COLOR_WARNING)
        else:
            add_styled_paragraph(document, "มีสารก่อภูมิแพ้ แต่ไม่ได้ระบุกลุ่ม", color=COLOR_WARNING)
    else:
        add_styled_paragraph(document, "ไม่มีสารก่อภูมิแพ้", color=COLOR_SUCCESS)
    
    document.add_paragraph()

    # 4. การกล่าวอ้างโภชนาการ
    add_styled_heading(document, "การกล่าวอ้างโภชนาการ", level=2, section_number="4.")
    
    if report_data.get('has_nutrition_claim'):
        add_styled_paragraph(document, "มีการกล่าวอ้างโภชนาการ", color=COLOR_WARNING)
        add_styled_paragraph(document, "หมายเหตุ: ฉลากต้องมีตารางโภชนาการด้วย")
    else:
        add_styled_paragraph(document, "ไม่มีการกล่าวอ้างโภชนาการ", color=COLOR_SUCCESS)
    
    document.add_paragraph()

    # 5. ข้อความที่ต้องมีในฉลาก
    add_styled_heading(document, "ข้อความที่ต้องมีในฉลาก", level=2, section_number="5.")
    
    required_labels = report_data.get('required_labels', [])
    if required_labels:
        for i, label in enumerate(required_labels, 1):
            add_styled_paragraph(document, f"{i}. {label}")
    else:
        add_styled_paragraph(document, "ไม่พบข้อความที่ต้องแสดงในฉลาก", italic=True)
    
    document.add_paragraph()

    # 6. สรุป
    add_styled_heading(document, "สรุป", level=2, section_number="6.")
    add_styled_paragraph(document, f"พบข้อความที่ต้องแสดงในฉลากทั้งหมด {len(required_labels)} รายการ", color=COLOR_SUCCESS)
    add_styled_paragraph(document, f"วันที่ตรวจสอบ: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    add_page_numbers(document)

    # Global Font Override
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            run.font.name = TARGET_FONT_NAME
            run.font.size = TARGET_FONT_SIZE
    
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.name = TARGET_FONT_NAME
                        run.font.size = TARGET_FONT_SIZE

    file_stream = io.BytesIO()
    document.save(file_stream)
    file_stream.seek(0)
    return file_stream

def normalize_ins(s):
    return re.sub(r"\s+", "", str(s)).lower()

def show():
    st.title("🔍 ตรวจสอบฉลากอาหาร")
    st.markdown("กรุณากรอกข้อมูลเพื่อตรวจสอบข้อความและคำเตือนที่ต้องแสดงในฉลากอาหาร")
    
    # Initialize session state for dynamic fields
    if "main_ingredient_count" not in st.session_state:
        st.session_state.main_ingredient_count = 5
    
    if "ins_count" not in st.session_state:
        st.session_state.ins_count = 3
    
    # Function to add more fields
    def add_main_ingredient():
        st.session_state.main_ingredient_count += 1
    
    def add_ins():
        st.session_state.ins_count += 1

    # 1. ชื่ออาหาร
    st.subheader("1. ชื่ออาหาร (ตามที่ขึ้นทะเบียน)")
    food_name = st.text_input("กรอกชื่ออาหาร", placeholder="เช่น ขนมปังโฮลวีท")
    
    # 2. ประเภทอาหาร/ชนิดอาหาร
    st.subheader("2. ประเภทอาหาร/ชนิดอาหาร")
    food_type = st.selectbox(
        "เลือกประเภทอาหาร",
        [
            "อื่นๆ",
            "อาหารขบเคี้ยว ตัวอย่างเช่น มันฝรั่งทอดกรอบ ข้าวโพดอบกรอบ ข้าวเกรียบชนิดต่างๆ ถั่วลิสงส์อบปรุงรส สาหร่ายทอดอบกรอบ ปลาหมึกแผ่นอบกรอบ หมูแผ่นอบกรอบ",
            "ช็อกโกแลต และขนมหวานรสช็อกโกแลต", 
            "ผลิตภัณฑ์ขนมอบ ตัวอย่างเช่น ขนมปังกรอบ ขนมขาไก่ เวเฟอร์สอดไส้ คุกกี้ เค้ก ขนมไหว้พระจันทร์ เอแคลร์ ครัวซองท์ พายไส้ต่างๆ",
            "อาหารกึ่งสำเร็จรูป",
            "อาหารมื้อหลักที่เป็นอาหารจานเดียว ซึ่งต้องเก็บรักษาไว้ในตู้เย็นหรือตู้แช่แข็งตลอดระยะเวลาจำหน่าย",
            "เครื่องดื่มในภาชนะบรรจุที่ปิดสนิท",
            "ชาปรุงสำเร็จ ทั้งชนิดเหลวและชนิดแห้ง",
            "กาแฟปรุงสำเร็จ ทั้งชนิดเหลวและชนิดแห้ง",
            "นมปรุงแต่ง",
            "นมเปรี้ยว",
            "ผลิตภัณฑ์ของนม",
            "น้ำนมถั่วเหลือง",
            "ไอศกรีมที่อยู่ในลักษณะพร้อมบริโภค",
            "วุ้นสำเร็จรูป",
            "ผลิตภัณฑ์เสริมอาหาร"
        ]
    )
    
    if food_type != "อื่นๆ" and food_type != "วุ้นสำเร็จรูป" and food_type != "ผลิตภัณฑ์เสริมอาหาร":
        st.info("📋 **หมายเหตุ**: อาหารประเภทนี้ต้องมีฉลาก GDA และตารางโภชนาการ")
    
    if food_type == "วุ้นสำเร็จรูป":
        st.warning("⚠️ **หมายเหตุ**: ต้องแสดง 'เด็กควรบริโภคแต่น้อย' ด้วยตัวอักษรสีแดงขนาด 5 มิลลิเมตร ในกรอบพื้นสีขาว")
    
    if food_type == "ผลิตภัณฑ์เสริมอาหาร":
        st.warning("⚠️ **หมายเหตุ**: ต้องแสดงคำเตือนดังต่อไปนี้:")
        st.warning("• 'คำเตือน' ด้วยตัวอักษรขนาดไม่เล็กกว่า 1.5 มม. ในกรอบสี่เหลี่ยมสีของตัวอักษรตัดกับสีของพื้นกรอบ และสีกรอบตัดกับสีของพื้นฉลาก")
        st.warning("• 'เด็กและสตรีมีครรภ์ ไม่ควรรับประทาน' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        st.warning("• 'ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        st.warning("• 'ไม่มีผลในการป้องกัน หรือรักษาโรค' ด้วยตัวอักษรหนาทึบ ในกรอบสี่เหลี่ยม สีของตัวอักษรตัดกับสีของพื้นกรอบ และสีของกรอบตัดกับสีของพื้นฉลาก")
    
    # 3. ลักษณะของอาหาร
    st.subheader("3. ลักษณะของอาหาร")
    
    # กำหนดตัวเลือกลักษณะอาหารตามประเภทอาหาร
    if food_type == "ผลิตภัณฑ์เสริมอาหาร":
        consistency_options = ["ของเหลว", "ของแข็ง", "เม็ดหรือแคปซูล"]
    else:
        consistency_options = ["ของเหลว", "ของแข็ง"]
    
    food_consistency = st.radio(
        "เลือกลักษณะของอาหาร",
        consistency_options
    )
    
    if food_consistency == "ของเหลว":
        st.info("📋 **หมายเหตุ**: อาหารของเหลวใช้ปริมาตรสุทธิ (เช่น มล., ลิตร)")
    elif food_consistency == "เม็ดหรือแคปซูล":
        st.info("📋 **หมายเหตุ**: ผลิตภัณฑ์เสริมอาหารเม็ดหรือแคปซูลใช้จำนวนบรรจุ (เช่น เม็ด, แคปซูล)")
    else:
        st.info("📋 **หมายเหตุ**: อาหารของแข็งใช้น้ำหนักสุทธิ (เช่น กรัม, กิโลกรัม)")
    
    # 4. ส่วนประกอบ และวัตถุเจือปนอาหาร
    st.subheader("4. ส่วนประกอบ และวัตถุเจือปนอาหาร")
    
    # Main ingredients section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**ส่วนประกอบหลัก**")
    with col2:
        st.button("+ เพิ่มส่วนประกอบหลัก", on_click=add_main_ingredient, key="add_main")
    
    main_ingredients = []
    for i in range(st.session_state.main_ingredient_count):
        main_ing = st.text_input(f"ส่วนประกอบหลัก {i+1}", key=f"main_ing_{i}")
        if main_ing:
            main_ingredients.append(main_ing)
    
    st.write("")
    
    # กำหนดค่าเริ่มต้นสำหรับตัวแปรกาเฟอีน
    caffeine_option = None
    container_type = None
    
    # เครื่องดื่มในภาชนะบรรจุที่ปิดสนิท - ตัวเลือกเพิ่มเติม
    if food_type == "เครื่องดื่มในภาชนะบรรจุที่ปิดสนิท":
        st.markdown("**ตัวเลือกเพิ่มเติมสำหรับเครื่องดื่ม**")
        
        caffeine_option = st.radio(
            "เลือกประเภทกาเฟอีน",
            ["ไม่มีกาเฟอีน", "ใช้วัตถุแต่งกลิ่นรสที่มีกาเฟอีนตามธรรมชาติ", "ผสมกาเฟอีนรูปแบบอื่น"],
            key="caffeine_option"
        )
        
        if caffeine_option == "ใช้วัตถุแต่งกลิ่นรสที่มีกาเฟอีนตามธรรมชาติ":
            st.warning("⚠️ **หมายเหตุ**: ต้องมีคำเตือนในฉลากว่า 'มีกาเฟอีน' ด้วยตัวอักษรขนาดความสูงไม่น้อยกว่า 2 มิลลิเมตร ที่อ่านได้ชัดเจน อยู่ในบริเวณเดียวกับชื่ออาหารหรือเครื่องหมายการค้า")
        
        elif caffeine_option == "ผสมกาเฟอีนรูปแบบอื่น":
            container_type = st.text_input("ระบุภาชนะที่ใช้บรรจุ", placeholder="เช่น กระป๋อง, ขวด", key="container_type")
            if container_type:
                st.warning(f"⚠️ **หมายเหตุ**: ต้องแสดงข้อความว่า 'ห้ามดื่มเกินวันละ 2 {container_type} เพราะอาจทำให้ใจสั่น นอนไม่หลับ เด็กและสตรีมีครรภ์ไม่ควรดื่ม ผู้มีโรคประจำตัวหรือผู้ป่วยปรึกษาแพทย์ก่อน' ด้วยตัวอักษรเส้นทึบสีแดง ขนาดความสูงไม่น้อยกว่า 2 มิลลิเมตร ในกรอบสี่เหลี่ยมพื้นขาว สีของกรอบตัดกับสีของพื้นฉลาก")
    
    # INS section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**วัตถุเจือปนอาหาร**")
    with col2:
        st.button("+ เพิ่มวัตถุเจือปนอาหาร", on_click=add_ins, key="add_ins")
    
    ins_list = []
    for i in range(st.session_state.ins_count):
        ins = st.text_input(f"เลข INS {i+1}", key=f"ins_{i}")
        if ins:
            ins_list.append(ins)
    
    st.markdown(
        "🔗 สามารถค้นหาเลข INS ได้ที่เว็ปไซต์ [กองอาหาร (อย.)](https://alimentum.fda.moph.go.th/FDA_FOOD_MVC/Additive/Main)"
    )
    
    # 5. สารก่อภูมิแพ้
    st.subheader("5. สารก่อภูมิแพ้")
    has_allergen = st.checkbox("มีสารก่อภูมิแพ้")
    
    allergen_groups = []
    if has_allergen:
        allergen_options = [
            "นม", "ไข่", "ถั่วเหลือง", "ถั่วลิสง", "ถั่วเปลือกแข็ง", 
            "ข้าวสาลี", "ปลา", "กุ้ง/ปู/หอย", "งา", "ซัลไฟต์"
        ]
        allergen_groups = st.multiselect(
            "เลือกกลุ่มสารก่อภูมิแพ้ที่มี",
            allergen_options
        )
    
    # 6. การกล่าวอ้างโภชนาการ
    st.subheader("6. การกล่าวอ้างโภชนาการ")
    has_nutrition_claim = st.checkbox("มีการกล่าวอ้างโภชนาการ")
    
    if has_nutrition_claim:
        st.info("📋 **หมายเหตุ**: กรุณาตรวจสอบเพิ่มเติมในเมนู 'ตรวจสอบการกล่าวอ้างโภชนาการ' และฉลากต้องมีตารางโภชนาการด้วย")
    
    # 7. เลขสารบบอาหาร
    st.subheader("7. เลขสารบบอาหาร")
    food_registration_number = st.text_input(
        "กรอกเลขสารบบอาหาร (ถ้ามี)", 
        placeholder="เช่น 12-1-12345-1-0001"
    )
    
    # 8. ชื่อและที่ตั้งผู้ผลิตหรือผู้นำเข้า
    st.subheader("8. ชื่อและที่ตั้งผู้ผลิตหรือผู้นำเข้า")
    manufacturer_name = st.text_input("ชื่อผู้ผลิตหรือผู้นำเข้า")
    manufacturer_address = st.text_area("ที่ตั้งผู้ผลิตหรือผู้นำเข้า")
    
    # 9. อายุของอาหาร
    st.subheader("9. อายุของอาหาร")
    shelf_life_option = st.radio(
        "เลือกอายุเก็บรักษา",
        ["ไม่เกิน 90 วัน", "เกิน 90 วัน"]
    )
    
    shelf_life_days = 90 if shelf_life_option == "ไม่เกิน 90 วัน" else 365
    
    if shelf_life_option == "ไม่เกิน 90 วัน":
        st.info("📋 **หมายเหตุ**: อายุเก็บไม่เกิน 90 วัน ต้องระบุ วัน เดือน ปี")
    else:
        st.info("📋 **หมายเหตุ**: อายุเก็บเกิน 90 วัน สามารถระบุ เดือนและปี หรือ วัน เดือน ปี")
    
    # 10. ซองวัตถุกันชื้น
    st.subheader("10. ซองวัตถุกันชื้น")
    has_desiccant = st.checkbox("มีซองวัตถุกันชื้น")
    
    if has_desiccant:
        st.warning("⚠️ **หมายเหตุ**: ต้องระบุ 'มีซองวัตถุกันชื้น' ด้วยตัวอักษรสีแดง ขนาดตัวอักษรไม่ต่ำกว่า ๓ มิลลิเมตร บนพื้นสีขาว")
    
    # ปุ่มตรวจสอบ
    st.write("")
    st.write("")
    
    if st.button("🔍 ตรวจสอบฉลากอาหาร", type="primary"):
        # สร้างรายงานผลการตรวจสอบ
        generate_label_report(
            food_name, food_type, food_consistency, main_ingredients, ins_list,
            has_allergen, allergen_groups, has_nutrition_claim, 
            food_registration_number, manufacturer_name, manufacturer_address,
            shelf_life_option, has_desiccant, caffeine_option, container_type
        )

def generate_label_report(food_name, food_type, food_consistency, main_ingredients, ins_list,
                         has_allergen, allergen_groups, has_nutrition_claim,
                         food_registration_number, manufacturer_name, manufacturer_address,
                         shelf_life_option, has_desiccant, caffeine_option=None, container_type=None):
    """สร้างรายงานผลการตรวจสอบฉลากอาหาร"""
    
    st.markdown("---")
    st.markdown("## 📋 รายงานผลการตรวจสอบฉลากอาหาร")
    
    # ข้อมูลพื้นฐาน
    st.markdown("### 📝 ข้อมูลพื้นฐาน")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**ชื่ออาหาร**: {food_name if food_name else 'ไม่ได้ระบุ'}")
        st.write(f"**ประเภทอาหาร**: {food_type if food_type else 'ไม่ได้ระบุ'}")
        st.write(f"**ลักษณะอาหาร**: {food_consistency}")
    
    with col2:
        st.write(f"**เลขสารบบอาหาร**: {food_registration_number if food_registration_number else 'ไม่ได้ระบุ'}")
        st.write(f"**อายุเก็บรักษา**: {shelf_life_option}")
    
    # ส่วนประกอบและวัตถุเจือปนอาหาร
    st.markdown("### 🧪 ส่วนประกอบและวัตถุเจือปนอาหาร")
    
    required_labels = []
    ins_results = []
    ingredient_warnings = []
    
    # ส่วนประกอบหลัก
    if main_ingredients:
        st.markdown("#### 📋 ส่วนประกอบหลัก")
        ingredients_text = ", ".join(main_ingredients)
        st.write(f"**ส่วนประกอบ**: {ingredients_text}")
        required_labels.append(f"ส่วนประกอบ: {ingredients_text}")
        
        # คำเตือนจากส่วนประกอบหลัก
        st.markdown("#### ⚠️ คำเตือนจากส่วนประกอบหลัก")
        warnings_db = load_warnings_database()
        
        for ing in main_ingredients:
            matched = warnings_db[warnings_db["keyword"].str.strip().str.lower() == ing.lower()]
            if not matched.empty:
                row = matched.iloc[0]
                warning_message = f"คำเตือนสำหรับ '{ing}': {row['warning']}"
                st.warning(f"⚠️ {warning_message}")
                required_labels.append(f"คำเตือน: {row['warning']}")
                ingredient_warnings.append(warning_message)
            else:
                st.success(f"✅ '{ing}' ไม่พบคำเตือนเฉพาะ")
    
    # วัตถุเจือปนอาหาร
    if ins_list:
        st.markdown("#### 🔍 ผลการตรวจสอบวัตถุเจือปนอาหาร (INS)")
        ins_db = load_ins_database()
        
        ins_db["normalized"] = ins_db["ins_number"].astype(str).apply(normalize_ins)
        
        for ins in ins_list:
            ins_norm = normalize_ins(ins)
            matched = ins_db[ins_db["normalized"] == ins_norm]
            if not matched.empty:
                row = matched.iloc[0]
                message = f"INS {row['ins_number']} คือ {row['name_th']} ({row['function_group']}) | 📋 ควรแสดงข้อความในฉลากว่า: {row['label_required_format']}"
                st.warning(f"⚠️ {message}")
                required_labels.append(f"วัตถุเจือปนอาหาร: {row['label_required_format']}")
                ins_results.append({
                    'has_special_label': True,
                    'message': message
                })
            else:
                message = f"'{ins}' ไม่มีข้อความเฉพาะ สามารถแสดง 'วัตถุเจือปนอาหาร (INS {ins},...)' ร่วมกับวัตถุเจือปนตัวอื่นๆที่ไม่มีข้อความเฉพาะได้เลย"
                st.success(f"✅ {message}")
                required_labels.append(f"วัตถุเจือปนอาหาร (INS {ins})")
                ins_results.append({
                    'has_special_label': False,
                    'message': message
                })
    
    # สารก่อภูมิแพ้
    st.markdown("### 🚨 สารก่อภูมิแพ้")
    if has_allergen and allergen_groups:
        allergen_text = ", ".join(allergen_groups)
        st.warning(f"⚠️ **มีสารก่อภูมิแพ้**: {allergen_text}")
        required_labels.append(f"ข้อมูลสำหรับผู้แพ้อาหาร: มี{allergen_text}")
    else:
        st.success("✅ **ไม่มีสารก่อภูมิแพ้**")
    
    # การกล่าวอ้างโภชนาการ
    st.markdown("### 📊 การกล่าวอ้างโภชนาการ")
    if has_nutrition_claim:
        st.warning("⚠️ **มีการกล่าวอ้างโภชนาการ**")
        st.info("📋 **หมายเหตุ**: ฉลากต้องมีตารางโภชนาการด้วย")
        required_labels.append("ตารางโภชนาการ")
        if food_type != "อื่นๆ" and food_type != "วุ้นสำเร็จรูป" and food_type != "ผลิตภัณฑ์เสริมอาหาร":
            required_labels.append("ฉลาก GDA")
    else:
        st.success("✅ **ไม่มีการกล่าวอ้างโภชนาการ**")
    
    # คำเตือนเฉพาะตามประเภทอาหาร
    st.markdown("### ⚠️ คำเตือนเฉพาะตามประเภทอาหาร")
    
    # วุ้นสำเร็จรูป
    if food_type == "วุ้นสำเร็จรูป":
        st.warning("⚠️ **วุ้นสำเร็จรูป**: ต้องแสดง 'เด็กควรบริโภคแต่น้อย' ด้วยตัวอักษรสีแดงขนาด 5 มิลลิเมตร ในกรอบพื้นสีขาว")
        required_labels.append("แสดง 'เด็กควรบริโภคแต่น้อย' ด้วยตัวอักษรสีแดงขนาด 5 มิลลิเมตร ในกรอบพื้นสีขาว")
    
    # ผลิตภัณฑ์เสริมอาหาร
    if food_type == "ผลิตภัณฑ์เสริมอาหาร":
        st.warning("⚠️ **ผลิตภัณฑ์เสริมอาหาร**: ต้องแสดงคำเตือนดังต่อไปนี้:")
        st.warning("• 'คำเตือน' ด้วยตัวอักษรขนาดไม่เล็กกว่า 1.5 มม. ในกรอบสี่เหลี่ยม")
        st.warning("• 'เด็กและสตรีมีครรภ์ ไม่ควรรับประทาน' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        st.warning("• 'ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        st.warning("• 'ไม่มีผลในการป้องกัน หรือรักษาโรค' ด้วยตัวอักษรหนาทึบ ในกรอบสี่เหลี่ยม")
        required_labels.append("แสดง 'คำเตือน' ด้วยตัวอักษรขนาดไม่เล็กกว่า 1.5 มม. ในกรอบสี่เหลี่ยมสีของตัวอักษรตัดกับสีของพื้นกรอบ และสีกรอบตัดกับสีของพื้นฉลาก")
        required_labels.append("แสดง 'เด็กและสตรีมีครรภ์ ไม่ควรรับประทาน' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        required_labels.append("แสดง 'ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ' ด้วยตัวอักษรที่มีขนาดเห็นได้ชัดเจน")
        required_labels.append("แสดง 'ไม่มีผลในการป้องกัน หรือรักษาโรค' ด้วยตัวอักษรหนาทึบ ในกรอบสี่เหลี่ยม สีของตัวอักษรตัดกับสีของพื้นกรอบ และสีของกรอบตัดกับสีของพื้นฉลาก")
    
    # อาหารขบเคี้ยว ช็อกโกแลต และผลิตภัณฑ์ขนมอบ
    if food_type in ["อาหารขบเคี้ยว ตัวอย่างเช่น มันฝรั่งทอดกรอบ ข้าวโพดอบกรอบ ข้าวเกรียบชนิดต่างๆ ถั่วลิสงส์อบปรุงรส สาหร่ายทอดอบกรอบ ปลาหมึกแผ่นอบกรอบ หมูแผ่นอบกรอบ", 
                     "ช็อกโกแลต และขนมหวานรสช็อกโกแลต", 
                     "ผลิตภัณฑ์ขนมอบ ตัวอย่างเช่น ขนมปังกรอบ ขนมขาไก่ เวเฟอร์สอดไส้ คุกกี้ เค้ก ขนมไหว้พระจันทร์ เอแคลร์ ครัวซองท์ พายไส้ต่างๆ"]:
        st.warning("⚠️ **อาหารขบเคี้ยว/ช็อกโกแลต/ขนมอบ**: ต้องแสดง 'บริโภคแต่น้อยและออกกำลังกายเพื่อสุขภาพ' ด้วยตัวอักษรหนาทึบ เห็นได้ชัดเจน")
        required_labels.append("ข้อความ 'บริโภคแต่น้อยและออกกำลังกายเพื่อสุขภาพ' ด้วยตัวอักษรหนาทึบ เห็นได้ชัดเจน สีของตัวอักษรตัดกับสีพื้นของกรอบ และสีของกรอบตัดกับสีพื้นฉลาก")
    
    # เครื่องดื่มในภาชนะบรรจุที่ปิดสนิท - กาเฟอีน
    if food_type == "เครื่องดื่มในภาชนะบรรจุที่ปิดสนิท":
        if caffeine_option == "ใช้วัตถุแต่งกลิ่นรสที่มีกาเฟอีนตามธรรมชาติ":
            st.warning("⚠️ **เครื่องดื่มกาเฟอีน**: ต้องมีคำเตือน 'มีกาเฟอีน' ด้วยตัวอักษรขนาดความสูงไม่น้อยกว่า 2 มิลลิเมตร")
            required_labels.append("คำเตือน 'มีกาเฟอีน' ด้วยตัวอักษรขนาดความสูงไม่น้อยกว่า 2 มิลลิเมตร ที่อ่านได้ชัดเจน อยู่ในบริเวณเดียวกับชื่ออาหารหรือเครื่องหมายการค้า")
        elif caffeine_option == "ผสมกาเฟอีนรูปแบบอื่น" and container_type:
            st.warning(f"⚠️ **เครื่องดื่มกาเฟอีน**: ต้องแสดงข้อความ 'ห้ามดื่มเกินวันละ 2 {container_type} เพราะอาจทำให้ใจสั่น นอนไม่หลับ เด็กและสตรีมีครรภ์ไม่ควรดื่ม ผู้มีโรคประจำตัวหรือผู้ป่วยปรึกษาแพทย์ก่อน'")
            required_labels.append(f"ข้อความ 'ห้ามดื่มเกินวันละ 2 {container_type} เพราะอาจทำให้ใจสั่น นอนไม่หลับ เด็กและสตรีมีครรภ์ไม่ควรดื่ม ผู้มีโรคประจำตัวหรือผู้ป่วยปรึกษาแพทย์ก่อน' ด้วยตัวอักษรเส้นทึบสีแดง ขนาดความสูงไม่น้อยกว่า 2 มิลลิเมตร ในกรอบสี่เหลี่ยมพื้นขาว สีของกรอบตัดกับสีของพื้นฉลาก")
    
    # จัดเรียงข้อความที่ต้องมีในฉลากตามลำดับที่ต้องการ
    ordered_labels = []
    
    # 1. ชื่ออาหาร
    ordered_labels.append(f"ชื่ออาหาร: {food_name if food_name else '[กรุณากรอกชื่ออาหาร]'}")
    
    # 2. เลขสารบบอาหาร
    ordered_labels.append("เลขสารบบอาหาร ในเครื่องหมายแสดงเลขสารบบอาหาร (ดาวน์โหลดได้ที่: https://food.fda.moph.go.th/media.php?id=629151820018753536&name=No-Color.png)")
    
    # 3. ส่วนประกอบที่สำคัญ
    if main_ingredients:
        ingredients_text = ", ".join(main_ingredients)
        ordered_labels.append(f"ส่วนประกอบ: {ingredients_text}")
    
    # 4. น้ำหนัก/ปริมาณ
    if food_consistency == "ของเหลว":
        ordered_labels.append("ปริมาตรสุทธิ ….. มล./ลิตร")
    elif food_consistency == "เม็ดหรือแคปซูล":
        ordered_labels.append("จำนวนบรรจุ ….. เม็ด/แคปซูล")
    else:
        ordered_labels.append("น้ำหนักสุทธิ ….. กรัม/กิโลกรัม")
    
    # 5. อื่นๆที่เหลือ (วัตถุเจือปนอาหาร, สารก่อภูมิแพ้, การกล่าวอ้างโภชนาการ, คำเตือน, ข้อมูลเพิ่มเติม)
    for label in required_labels:
        if label not in ordered_labels:
            ordered_labels.append(label)
    
    # เพิ่มข้อมูลที่ขาดหายไป
    # ผู้ผลิต
    if manufacturer_name:
        ordered_labels.append(f"ผู้ผลิต: {manufacturer_name}")
    if manufacturer_address:
        ordered_labels.append(f"ที่ตั้ง: {manufacturer_address}")
    
    # อายุของอาหาร
    if shelf_life_option == "ไม่เกิน 90 วัน":
        ordered_labels.append("ควรบริโภคก่อน (ระบุ วัน เดือน ปี)")
    else:
        ordered_labels.append("ควรบริโภคก่อน (ระบุ เดือน ปี หรือ วัน เดือน ปี)")
    
    # ซองวัตถุกันชื้น
    if has_desiccant:
        ordered_labels.append("ระบุ 'มีซองวัตถุกันชื้น' ด้วยตัวอักษรสีแดง ขนาดตัวอักษรไม่ต่ำกว่า ๓ มิลลิเมตร บนพื้นสีขาว")
    
    # เพิ่มข้อมูลอื่นๆที่เหลือ
    for label in required_labels:
        if label not in ordered_labels:
            ordered_labels.append(label)
    
    # ข้อความที่ต้องมีในฉลาก
    st.markdown("### ✅ ข้อความที่ต้องมีในฉลาก")
    for i, label in enumerate(ordered_labels, 1):
        st.write(f"{i}. {label}")
    
    # สรุป
    st.markdown("### 📊 สรุป")
    st.success(f"✅ พบข้อความที่ต้องแสดงในฉลากทั้งหมด {len(ordered_labels)} รายการ")

    # สร้างข้อมูลสำหรับรายงาน Word
    report_data = {
        'food_name': food_name,
        'food_type': food_type,
        'food_consistency': food_consistency,
        'food_registration_number': food_registration_number,
        'manufacturer_name': manufacturer_name,
        'manufacturer_address': manufacturer_address,
        'shelf_life_option': shelf_life_option,
        'has_allergen': has_allergen,
        'allergen_groups': allergen_groups,
        'has_nutrition_claim': has_nutrition_claim,
        'main_ingredients': main_ingredients,
        'ins_results': ins_results,
        'ingredient_warnings': ingredient_warnings,
        'required_labels': ordered_labels,
        'has_desiccant': has_desiccant,
        'caffeine_option': caffeine_option,
        'container_type': container_type
    }
    
    # ปุ่มดาวน์โหลดรายงาน
    st.markdown("### 📥 ดาวน์โหลดรายงาน")
    
    try:
        word_stream = generate_label_word_report(report_data)
        st.download_button(
            label="📥 ดาวน์โหลดรายงาน Word (.docx)",
            data=word_stream.getvalue(),
            file_name=f"label_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary"
        )
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการสร้างรายงาน Word: {str(e)}")
