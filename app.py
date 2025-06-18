import streamlit as st

st.set_page_config(
    page_title="แอปตรวจสอบฉลากอาหาร",
    page_icon="🍱",
    layout="wide"
)

import main_page
import ocr_check
import ingredient_check
import nutrition_check


st.sidebar.title("เมนู")
page = st.sidebar.radio(
    "เลือกหมวดที่ต้องการตรวจสอบ",
    (
        "หน้าหลัก",
        "ตรวจสอบองค์ประกอบฉลากจากภาพ",
        "ตรวจสอบข้อความจากสูตรส่วนประกอบ",
        "ตรวจสอบข้อความกล่าวอ้างโภชนาการ"
    )
)

if page == "หน้าหลัก":
    main_page.show()
elif page == "ตรวจสอบองค์ประกอบฉลากจากภาพ":
    ocr_check.show()
elif page == "ตรวจสอบข้อความจากสูตรส่วนประกอบ":
    ingredient_check.show()
elif page == "ตรวจสอบข้อความกล่าวอ้างโภชนาการ":
    nutrition_check.show()
