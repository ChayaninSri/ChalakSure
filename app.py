import streamlit as st

def show_disclaimer():
    st.markdown("""
    <div style="background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border: 1px solid #ffeeba;">
        <p style="font-weight: bold; font-size: 1.1rem; margin: 0;">🚨 ข้อควรระวัง</p>
        <p style="margin: 0.5rem 0 0 0;">
            แอปพลิเคชันนี้เป็นตัวช่วยในการคำนวณและตรวจสอบฉลากอาหารเท่านั้น ไม่สามารถใช้เป็นเงื่อนไขการขออนุญาต หรืออ้างอิงทางกฎหมายได้ โปรดปฏิบัติตามกฎหมายอย่างเคร่งครัด
        </p>
    </div>
    """, unsafe_allow_html=True)

st.set_page_config(
    page_title="ฉลากชัวร์",
    page_icon="✅",
    layout="wide"
)

import main_page
# import ocr_check  # Commented out temporarily due to deployment issues
import Label_check
import nutrition_check


st.sidebar.title("เมนู")
page = st.sidebar.radio(
    "เลือกหมวดที่ต้องการตรวจสอบ",
    (
        "หน้าหลัก",
        # "ตรวจสอบองค์ประกอบฉลากจากภาพ",  # Commented out temporarily
        "ตรวจสอบฉลากอาหาร",
        "ตรวจสอบข้อความกล่าวอ้างโภชนาการ"
    )
)

# Show disclaimer on all pages
show_disclaimer()

if page == "หน้าหลัก":
    main_page.show()
# elif page == "ตรวจสอบองค์ประกอบฉลากจากภาพ":  # Commented out temporarily
#     ocr_check.show()
elif page == "ตรวจสอบฉลากอาหาร":
    Label_check.show()
elif page == "ตรวจสอบข้อความกล่าวอ้างโภชนาการ":
    nutrition_check.show()
