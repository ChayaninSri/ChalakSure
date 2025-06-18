import streamlit as st
import pandas as pd
import re

@st.cache_data
def load_ins_database():
    return pd.read_csv("ins_database.csv", encoding="utf-8-sig")

@st.cache_data
def load_warnings_database():
    return pd.read_csv("warnings_database.csv", encoding="utf-8-sig")

def normalize_ins(s):
    return re.sub(r"\s+", "", str(s)).lower()

def show():
    st.title("ตรวจสอบการแสดงข้อความของสูตรส่วนประกอบ")

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

    # Main ingredients section with button on the right
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("ส่วนประกอบหลัก")
    with col2:
        st.button("+ เพิ่มส่วนประกอบหลัก", on_click=add_main_ingredient)
    
    main_ingredients = []
    for i in range(st.session_state.main_ingredient_count):
        main_ing = st.text_input(f"ส่วนประกอบหลัก {i+1}", key=f"main_ing_{i}")
        if main_ing:
            main_ingredients.append(main_ing)
    
    # Add vertical spacing between sections
    st.write("")
    st.write("")
    
    # INS section with button on the right
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("วัตถุเจือปนอาหาร")
    with col2:
        st.button("+ เพิ่มวัตถุเจือปนอาหาร", on_click=add_ins)
    
    ins_list = []
    for i in range(st.session_state.ins_count):
        ins = st.text_input(f"เลข INS {i+1}", key=f"ins_{i}")
        if ins:
            ins_list.append(ins)
    
    st.markdown(
    "🔗 สามารถค้นหาเลข INS ได้ที่เว็ปไซต์ [กองอาหาร (อย.)](https://alimentum.fda.moph.go.th/FDA_FOOD_MVC/Additive/Main)"
    )

    if st.button("🔍 ตรวจสอบสูตรส่วนประกอบ"):
        ins_db = load_ins_database()
        warnings_db = load_warnings_database()

        # 🔍 ตรวจสอบคำเตือนจากส่วนประกอบหลัก
        if main_ingredients:
            st.markdown("### ผลการตรวจสอบคำเตือนจากส่วนประกอบหลัก")

            for ing in main_ingredients:
                matched = warnings_db[warnings_db["keyword"].str.strip().str.lower() == ing.lower()]
                if not matched.empty:
                    row = matched.iloc[0]
                    st.warning(f"⚠️ คำเตือนสำหรับ '{ing}': {row['warning']}")
                else:
                    st.success(f"✅ '{ing}' ไม่พบคำเตือนเฉพาะ")

        # 🔍 ตรวจสอบ INS
        if ins_list:
            st.markdown("### ผลการตรวจสอบวัตถุเจือปนอาหาร (INS)")

            ins_db["normalized"] = ins_db["ins_number"].astype(str).apply(normalize_ins)

            for ins in ins_list:
                ins_norm = normalize_ins(ins)
                matched = ins_db[ins_db["normalized"] == ins_norm]
                if not matched.empty:
                    row = matched.iloc[0]
                    st.warning(
                        f"⚠️ INS {row['ins_number']} คือ {row['name_th']} ({row['function_group']}) | 📋 ควรแสดงข้อความในฉลากว่า: {row['label_required_format']}"
                    )
                else:
                    st.success(f"✅ '{ins}' ไม่มีข้อความเฉพาะ สามารถแสดง 'วัตถุเจือปนอาหาร (INS {ins},...)' ร่วมกับวัตถุเจือปนตัวอื่นๆที่ไม่มีข้อความเฉพาะได้เลย")
