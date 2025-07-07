import streamlit as st

st.set_page_config(
    page_title="ฉลากชัวร์",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css(".streamlit/style.css")

def show_disclaimer():
    st.markdown("""
    <div class="disclaimer-box">
        <p>🚨 ข้อควรระวัง</p>
        <p>
            แอปพลิเคชันนี้เป็นตัวช่วยในการคำนวณและตรวจสอบฉลากอาหารเท่านั้น ไม่สามารถใช้เป็นเงื่อนไขการขออนุญาต หรืออ้างอิงทางกฎหมายได้ โปรดปฏิบัติตามกฎหมายอย่างเคร่งครัด
        </p>
    </div>
    """, unsafe_allow_html=True)

import main_page
# import ocr_check  # Commented out temporarily due to deployment issues
import ingredient_check
import nutrition_check


st.sidebar.title("เมนู")
page = st.sidebar.radio(
    "เลือกหมวดที่ต้องการตรวจสอบ",
    (
        "หน้าหลัก",
        # "ตรวจสอบองค์ประกอบฉลากจากภาพ",  # Commented out temporarily
        "ตรวจสอบข้อความจากสูตรส่วนประกอบ",
        "ตรวจสอบข้อความกล่าวอ้างโภชนาการ"
    )
)

# Show disclaimer on all pages
show_disclaimer()

if page == "หน้าหลัก":
    main_page.show()
# elif page == "ตรวจสอบองค์ประกอบฉลากจากภาพ":  # Commented out temporarily
#     ocr_check.show()
elif page == "ตรวจสอบข้อความจากสูตรส่วนประกอบ":
    ingredient_check.show()
elif page == "ตรวจสอบข้อความกล่าวอ้างโภชนาการ":
    nutrition_check.show()
