import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from math import isnan
from typing import Dict, List, Any
import io # Added for BytesIO for file download
from nutrition_report import generate_nutrition_report # Added for report generation
from disclaim_check import check_disclaimers
from nutrition_cal import adjust_per_100_to_serving, round_nutrition_value, calculate_per_100kcal, prepare_rounded_values_display, round_rdi_percent

# Helper function for loading CSV files
def load_csv_file(filename, error_message):
    try:
        if not os.path.exists(filename):
            st.error(f"ไม่พบไฟล์ {filename} กรุณาตรวจสอบไฟล์")
            return pd.DataFrame()
        return pd.read_csv(filename, encoding="utf-8-sig")
    except Exception as e:
        st.error(f"{error_message}: {e}")
        return pd.DataFrame()

# Helper function for creating nutrient dictionaries
def create_nutrient_dict(values, multiplier=1.0):
    return {
        key: value * multiplier if value is not None else None
        for key, value in values.items()
    }

# Nutrient mapping dictionary for faster lookups
NUTRIENT_MAPPING = {
    "อิ่มตัว": "saturated_fat",
    "ทรานส์": "trans_fat",
    "คอเลสเตอรอล": "cholesterol",
    "พลังงาน": "energy",
    "โปรตีน": "protein",
    "ไขมัน": "fat",
    "น้ำตาล": "sugar",
    "ใยอาหาร": "fiber",
    "โซเดียม": "sodium",
}

# RDI mapping dictionary
RDI_MAPPING = {
    "protein": "โปรตีน",
    "fiber": "ใยอาหาร",
    "fat": "ไขมันทั้งหมด",
    "saturated_fat": "ไขมันอิ่มตัว",
    "cholesterol": "คอเลสเตอรอล",
    "sodium": "โซเดียม",
    "potassium": "โพแทสเซียม",
    "calcium": "แคลเซียม",
    "phosphorus": "ฟอสฟอรัส",
    "magnesium": "แมกนีเซียม",
    "iron": "เหล็ก",
    "iodine": "ไอโอดีน",
    "zinc": "สังกะสี",
    "selenium": "ซีลีเนียม",
    "copper": "ทองแดง",
    "manganese": "แมงกานีส",
    "molybdenum": "โมลิบดีนัม",
    "chromium": "โครเมียม",
    "chloride": "คลอไรด์",
    "vitamin_a": "วิตามินเอ",
    "vitamin_d": "วิตามินดี",
    "vitamin_e": "วิตามินอี",
    "vitamin_k": "วิตามินเค",
    "vitamin_b1": "วิตามินบี1/ไทอามีน",
    "vitamin_b2": "วิตามินบี2/ไรโบฟลาวิน",
    "niacin": "ไนอะซิน",
    "pantothenic_acid": "กรดแพนโททีนิก",
    "vitamin_b6": "วิตามินบี6",
    "biotin": "ไบโอติน",
    "folate": "โฟเลต",
    "vitamin_b12": "วิตามินบี12",
    "vitamin_c": "วิตามินซี"
}

@st.cache_data
def load_food_groups():
    return load_csv_file("serve_size_database.csv", "เกิดข้อผิดพลาดในการโหลดข้อมูลกลุ่มอาหาร")

@st.cache_data
def load_claims_table(table_type):
    # Remove "table" prefix if it exists in table_type
    table_num = table_type.replace("table", "") if isinstance(table_type, str) else table_type
    filename = f"nutrition_claims_table{table_num}.csv"
    
    claims_df = load_csv_file(filename, "เกิดข้อผิดพลาดในการโหลดตารางคำกล่าวอ้าง")
    
    # Debug: Print fiber claims for liquid foods
    if str(table_num) == "2":
        try:
            liquid_fiber_claims = claims_df[(claims_df['state'] == 'liquid') & 
                                        (claims_df['nutrient'].str.contains('fiber', case=False))]
            if not liquid_fiber_claims.empty:
                print(f"DEBUG - Loaded liquid fiber claims from table {table_num}:")
                print(liquid_fiber_claims[['claim_text', 'threshold', 'threshold_100kcal']])
        except Exception as e:
            print(f"Error debugging fiber claims: {str(e)}")
    
    return claims_df

@st.cache_data
def load_disclaimers():
    return load_csv_file("disclaimer_rules.csv", "เกิดข้อผิดพลาดในการโหลดข้อความเตือน")

@st.cache_data
def load_condition_lookup():
    df = load_csv_file("condition_lookup.csv", "เกิดข้อผิดพลาดในการโหลดเงื่อนไขเพิ่มเติม")
    if not df.empty:
        df["condition"] = df["condition"].astype(str)
        return df

@st.cache_data
def load_thai_rdis():
    df = load_csv_file("Thai_RDIs.csv", "เกิดข้อผิดพลาดในการโหลดข้อมูล Thai RDIs")
    if df.empty:
        st.error("ไม่พบข้อมูล Thai RDIs หรือไฟล์ Thai_RDIs.csv ไม่ถูกต้อง")
    return df

def get_rdi_value(nutrient_key, thai_rdis):
    if thai_rdis.empty:
        return None
    
    thai_name = RDI_MAPPING.get(nutrient_key)
    if not thai_name:
        return None
    
    rdi_row = thai_rdis[thai_rdis['สารอาหาร'] == thai_name]
    if rdi_row.empty:
        return None
    
    return rdi_row.iloc[0]['ปริมาณที่แนะนำต่อวัน (Thai RDIs)']

def calculate_energy_from_saturated_fat(saturated_fat, energy):
    """
    คำนวณพลังงานที่มาจากไขมันอิ่มตัว (ไขมัน 1g = 9kcal)
    และคำนวณเป็นเปอร์เซ็นต์ของพลังงานทั้งหมด
    """
    if saturated_fat is None or energy is None or energy == 0:
        return None
        
    # คำนวณพลังงานจากไขมันอิ่มตัว (1g = 9kcal)
    saturated_fat_energy = saturated_fat * 9
    
    # คำนวณเป็นเปอร์เซ็นต์ของพลังงานทั้งหมด
    saturated_fat_energy_percent = (saturated_fat_energy / energy) * 100
    
    return saturated_fat_energy_percent

def evaluate_threshold(threshold_str, values_dict, nutrient_key, label_values=None):
    try:
        is_fiber = nutrient_key == "fiber"
        
        def convert_operator(op):
            operator_map = {"≥": ">=", "≤": "<="}
            return operator_map.get(op, op)
        
        raw_match = re.match(r"raw_(\w+)\s*([<>]=?|[≤≥])\s*(\d+(\.\d+)?)", threshold_str)
        if raw_match and label_values is not None:
            raw_nutrient = raw_match.group(1)
            operator = convert_operator(raw_match.group(2))
            threshold = float(raw_match.group(3))
            
            raw_value = label_values.get(raw_nutrient)
            if raw_value is None:
                return True
                
            return eval(f"{raw_value} {operator} {threshold}")
            
        rdi_match = re.search(r"([<>≥≤]=?|>=|<=)\s*(\d+(\.\d+)?)\s*%?\s*RDI", threshold_str.strip(), re.IGNORECASE)
        if rdi_match:
            operator = convert_operator(rdi_match.group(1))
            threshold = float(rdi_match.group(2))
            rdi_key = f"{nutrient_key}_rdi_percent"
            value = values_dict.get(rdi_key)
            
            if value is None:
                return False
                
            result = eval(f"{value} {operator} {threshold}")
            
            return result

        simple_match = re.match(r"([<>≥≤]=?)\s*(\d+(\.\d+)?)", threshold_str.strip())
        if simple_match:
            operator = convert_operator(simple_match.group(1))
            threshold = float(simple_match.group(2))
            value = values_dict.get(nutrient_key)
            if value is None:
                return False
                
            result = eval(f"{value} {operator} {threshold}")
            
            return result

        if "หรือ" in threshold_str:
            or_conditions = [cond.strip() for cond in threshold_str.split("หรือ")]
            return any(evaluate_threshold(cond, values_dict, nutrient_key, label_values) for cond in or_conditions)
            
        if "และ" in threshold_str:
            and_conditions = [cond.strip() for cond in threshold_str.split("และ")]
            return all(evaluate_threshold(cond, values_dict, nutrient_key, label_values) for cond in and_conditions)

        match = re.match(r"(.*?)\s*([<>≥≤]=?)\s*(\d+(\.\d+)?)", threshold_str)
        if match:
            nutrient_name = match.group(1).strip()
            operator = convert_operator(match.group(2))
            threshold = float(match.group(3))
            key = normalize_nutrient_key(nutrient_name)
            value = values_dict.get(key)
            if value is None:
                return False
                
            return eval(f"{value} {operator} {threshold}")

        return False
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการประเมินเงื่อนไข: {e}")
        return False

def normalize_nutrient_key(name):
    name = name.lower()
    # Check for exact matches first
    for thai_key, eng_key in NUTRIENT_MAPPING.items():
        if thai_key in name:
            # Special case for fat to avoid matching saturated or trans fat
            if thai_key == "ไขมัน" and ("อิ่มตัว" in name or "ทรานส์" in name):
                continue
            return eng_key
    
    # Check for RDI percentage
    if "%" in name and "rdi" in name:
        base_nutrient = name.split("%")[0].strip()
        return f"{normalize_nutrient_key(base_nutrient)}_rdi_percent"
    
    return name

def float_input(label, default=None):
    val = st.text_input(label, value="" if default is None else str(default))
    if val.strip() == "":
        return None
    try:
        return float(val)
    except ValueError:
        st.error(f"ค่าที่ใส่ในช่อง '{label}' ไม่ใช่ตัวเลข กรุณาใส่ตัวเลขที่ถูกต้อง")
        return None

def evaluate_special_rule(special_rule, values_dict, label_values=None):
    """
    ตรวจสอบเงื่อนไขเพิ่มเติมสำหรับการกล่าวอ้าง
    เช่น กรณีไขมันอิ่มตัวที่ต้องตรวจสอบไขมันทรานส์ด้วย
    """
    if not special_rule or pd.isna(special_rule):
        return True
        
    try:
        # แยกเงื่อนไขเพิ่มเติมเป็นรายการ
        rules = [rule.strip() for rule in str(special_rule).split(',')]
        
        for rule in rules:
            # ตรวจสอบรูปแบบ "nutrient operator value"
            match = re.match(r"(\w+)\s*([<>]=?|[≤≥])\s*(\d+(\.\d+)?)", rule)
            if match:
                nutrient = match.group(1)
                operator = match.group(2)
                value = float(match.group(3))
                
                # ตรวจสอบเงื่อนไขสำหรับหน่วยบริโภคอ้างอิง (values_dict) และหน่วยบริโภคบนฉลาก (label_values)
                # เงื่อนไขต้องเป็นจริงสำหรับทั้งสองกรณี (AND logic)

                # --- ตรวจสอบหน่วยบริโภคอ้างอิง ---
                ref_value = values_dict.get(nutrient)
                # ถ้าไม่มีค่า หรือค่าไม่ผ่านเงื่อนไข ให้ถือว่าไม่ผ่านทันที
                if ref_value is None or not eval(f"{ref_value} {operator} {value}"):
                    return False

                # --- ตรวจสอบหน่วยบริโภคบนฉลาก (ถ้ามี) ---
                if label_values is not None:
                    label_value = label_values.get(nutrient)
                    # ถ้าไม่มีค่า หรือค่าไม่ผ่านเงื่อนไข ให้ถือว่าไม่ผ่านทันที
                    if label_value is None or not eval(f"{label_value} {operator} {value}"):
                        return False
                
                # หากผ่านการตรวจสอบทั้งหมดสำหรับ rule นี้ ให้วนลูปเพื่อตรวจสอบ rule ถัดไป
                
        return True
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการตรวจสอบเงื่อนไขเพิ่มเติม: {e}")
        return False

def show():
    st.title("ตรวจสอบคำกล่าวอ้างทางโภชนาการ")

    thai_rdis = load_thai_rdis()

    if thai_rdis.empty:
        st.error("ไม่สามารถดำเนินการตรวจสอบได้เนื่องจากไม่มีข้อมูล Thai RDIs")
        st.write("โปรดตรวจสอบว่าไฟล์ Thai_RDIs.csv มีอยู่และถูกต้อง")
        return

    food_groups = load_food_groups()
    if food_groups.empty:
        st.error("ไม่สามารถดำเนินการตรวจสอบได้เนื่องจากไม่พบข้อมูลกลุ่มอาหาร")
        return

    # Initialize variables to prevent UnboundLocalError
    group_info = None
    food_state_value = "solid"  # Default value
    
    # Flag to indicate whether reference serving size was entered manually by the user
    is_ref_serving_user_input = False
    
    group_labels = {row["food_type_th"]: row["food_type_th"] for _, row in food_groups.iterrows()}
    food_options = ["ไม่อยู่ในบัญชีหมายเลข 2"] + list(group_labels.keys())
    selected_label = st.selectbox("เลือกกลุ่มอาหารตามบัญชีหมายเลข 2 (พิมพ์เพื่อค้นหาได้เลย)", food_options)

    if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
        group_info = food_groups[food_groups["food_type_th"] == selected_label].iloc[0].copy()  # Copy to allow modification
        # Detect items with missing reference serving size (blank or NaN)
        missing_serving = pd.isna(group_info["serving_value"]) or str(group_info["serving_value"]).strip() == ""
        if missing_serving:
            st.warning("⚠️ ไม่พบข้อมูลหน่วยบริโภคอ้างอิงสำหรับรายการนี้ กรุณากรอกปริมาณผงที่ละลายน้ำในหน่วยกรัม ตามปริมาณสำหรับเตรียมเพื่อให้อยู่ในสภาพพร้อมบริโภค เช่น เครื่องดื่มผง ให้กรอกปริมาณสำหรับเตรียม 200 มิลลิลิตร วิธีบริโภค คือ 1 ซอง (30 กรัม) ละลายน้ำ 300 มิลลิลิตร จากการเทียบบัญญัติไตรยางค์ จะได้ 20 กรัม ละลายน้ำ 200 มิลลิลตร เป็นต้น")
            manual_serving = float_input("กรอกหน่วยบริโภคอ้างอิง แล้วกด Enter:")
            # หากผู้ใช้ไม่กรอกค่าที่ถูกต้อง ให้หยุดการทำงานของโปรแกรมไว้ก่อน
            if manual_serving is None:
                st.error("กรุณากรอกหน่วยบริโภคอ้างอิงเพื่อดำเนินการต่อ")
                st.stop()
            # Override missing reference serving size with user input
            group_info["serving_value"] = manual_serving
            group_info["unit"] = "กรัม"
            is_ref_serving_user_input = True  # Mark that the reference size came from user input
            st.info(f"กลุ่มนี้ใช้หน่วยบริโภคอ้างอิง: {manual_serving} กรัม")
        else:
            st.info(f"กลุ่มนี้ใช้หน่วยบริโภคอ้างอิง: {group_info['serving_value']} {group_info['unit']}")
        table_type = "table1"
    else:
        st.caption("ระบบจะใช้ตารางที่ 2 (บัญชีหมายเลข 4) ซึ่งอ้างอิงต่อ 100 กรัมหรือ 100 มิลลิลิตร")
        food_state = st.radio(
            "ลักษณะของอาหาร(เมื่อพร้อมบริโภค):",
            ["ของแข็ง (กรัม)", "ของเหลว (มิลลิลิตร)"],
            horizontal=True
        )
        food_state_value = "solid" if food_state == "ของแข็ง (กรัม)" else "liquid"

        # สถานะของผลิตภัณฑ์ (ต้องเตรียมหรือพร้อมบริโภคแล้ว)
        prep_option = st.radio(
            "สถานะผลิตภัณฑ์:",
            ["พร้อมบริโภคแล้ว", "ต้องเตรียม (เช่น ผงชง)"],
            horizontal=True
        )

        # ถ้าต้องเตรียม ให้รับค่าปริมาณผงที่ใช้สำหรับ 100 มิลลิลิตรพร้อมบริโภค
        manual_prep_grams = None
        if prep_option == "ต้องเตรียม (เช่น ผงชง)":
            st.info("กรุณากรอกปริมาณผง (กรัม) ที่ใช้เตรียมอาหาร/เครื่องดื่มให้พร้อมบริโภค 100 มิลลิลิตร\n\nตัวอย่าง: วิธีบริโภค 1 ซอง (50 กรัม) ผสมน้ำ 200 มิลลิลิตร  \u2192 25 กรัม ต่อ 100 มิลลิลิตร")
            manual_prep_grams = float_input("ปริมาณผง (กรัม) ต่อ 100 มิลลิลิตร พร้อมบริโภค:")
        table_type = "table2"

    # เพิ่มตัวเลือกวิธีการตรวจสอบ
    nutrition_check_method = st.radio(
        "วิธีการตรวจสอบ:",
        ["ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)", "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)"],
        horizontal=True
    )

    # ปริมาณหน่วยบริโภคบนหน้าฉลาก
    actual_serving_size = st.number_input("ปริมาณหน่วยบริโภคที่ระบุในฉลาก (กรัม หรือ มิลลิลตร) *กรุณาแปลงหน่อยให้เป็น กรัม หรือ มิลลิลิตรเท่านั้น เช่น 1 ช้อนโต๊ะ = 15 มิลลิลิตร", min_value=0.1, step=0.1)

    # แสดงหัวข้อแตกต่างกันตามวิธีที่เลือก
    if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
        st.subheader("ข้อมูลจากผลวิเคราะห์ต่อ 100 g หรือ 100 ml")
    else:
        st.subheader("ข้อมูลจากฉลากโภชนาการต่อ 1 หน่วยบริโภค")
        st.warning("⚠️ กรณีที่มีสารอาหารที่ไม่สามารถระบุค่าแน่ชัดได้ เช่น \"น้อยกว่า 1\" ขอให้กรอกค่าที่น้อยกว่าแทน เช่น 0.9 มิเช่นนั้นโปรแกรมจะไม่สามารถคำนวณได้\n\n*ทั้งนี้ การตรวจสอบข้อมูลจากฉลากโภชนาการ เป็นการตรวจสอบจากตัวเลขที่ผ่านการปัดมาแล้ว ดังนั้นอาจทำให้ผลการคำนวณคลาดเคลื่อนจากความเป็นจริง หากท่านมีผลวิเคราะห์ แนะนำให้ใช้การตรวจสอบจากผลวิเคราะห์จะมีความแม่นยำกว่า")

    has_added_sugar = None
    if table_type == "table1":
        has_added_sugar = st.radio(
            "การเติมน้ำตาล:",
            ["มีการเติมน้ำตาล", "ไม่มีการเติมน้ำตาล"],
            horizontal=True
        )

    nutrient_values = {
        "energy": float_input("พลังงาน (kcal):"),
        "protein": float_input("โปรตีน (g):"),
        "fat": float_input("ไขมัน (g):"),
        "saturated_fat": float_input("ไขมันอิ่มตัว (g):"),
        "trans_fat": float_input("ไขมันทรานส์ (g):"),
        "cholesterol": float_input("คอเลสเตอรอล (mg):"),
        "sugar": float_input("น้ำตาล (g):"),
        "fiber": float_input("ใยอาหาร (g):"),
        "sodium": float_input("โซเดียม (mg):"),
        "potassium": float_input("โพแทสเซียม (mg):")
    }

    # ข้อมูลวิตามินและเกลือแร่
    VITAMIN_MINERAL_GROUPS = {
        "วิตามินที่ละลายในไขมัน": {
            "วิตามินเอ": {"unit": "µg RAE", "key": "vitamin_a"},
            "วิตามินดี": {"unit": "µg", "key": "vitamin_d"},
            "วิตามินอี": {"unit": "mg α-TE", "key": "vitamin_e"},
            "วิตามินเค": {"unit": "µg", "key": "vitamin_k"}
        },
        "วิตามินที่ละลายในน้ำ": {
            "วิตามินบี1/ไทอามีน": {"unit": "mg", "key": "vitamin_b1"},
            "วิตามินบี2/ไรโบฟลาวิน": {"unit": "mg", "key": "vitamin_b2"},
            "ไนอะซิน": {"unit": "mg NE", "key": "niacin"},
            "กรดแพนโททีนิก": {"unit": "mg", "key": "pantothenic_acid"},
            "วิตามินบี6": {"unit": "mg", "key": "vitamin_b6"},
            "ไบโอติน": {"unit": "µg", "key": "biotin"},
            "โฟเลต": {"unit": "µg DFE", "key": "folate"},
            "วิตามินบี12": {"unit": "µg", "key": "vitamin_b12"},
            "วิตามินซี": {"unit": "mg", "key": "vitamin_c"}
        },
        "เกลือแร่": {
            "แคลเซียม": {"unit": "mg", "key": "calcium"},
            "ฟอสฟอรัส": {"unit": "mg", "key": "phosphorus"},
            "แมกนีเซียม": {"unit": "mg", "key": "magnesium"},
            "เหล็ก": {"unit": "mg", "key": "iron"},
            "ไอโอดีน": {"unit": "µg", "key": "iodine"},
            "สังกะสี": {"unit": "mg", "key": "zinc"},
            "ซีลีเนียม": {"unit": "µg", "key": "selenium"},
            "ทองแดง": {"unit": "µg", "key": "copper"},
            "แมงกานีส": {"unit": "mg", "key": "manganese"},
            "โมลิบดีนัม": {"unit": "µg", "key": "molybdenum"},
            "โครเมียม": {"unit": "µg", "key": "chromium"}
        },
        "เกลือแร่ที่เป็นอิเล็กโทรไลต์": {
            "คลอไรด์": {"unit": "mg", "key": "chloride"}
        }
    }

    # ส่วนกรอกข้อมูลวิตามินและเกลือแร่
    st.subheader("กลุ่มวิตามินและแร่ธาตุ")
    
    # แสดงเป็นกลุ่มวิตามินและเกลือแร่
    for group_name, nutrients in VITAMIN_MINERAL_GROUPS.items():
        with st.expander(f"{group_name}", expanded=False):
            cols = st.columns(2)
            i = 0
            for nutrient_name, info in nutrients.items():
                with cols[i % 2]:
                    input_label = f"{nutrient_name} ({info['unit']}):"
                    if nutrition_check_method == "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)":
                        input_label = f"{nutrient_name} (%RDI ต่อหน่วยบริโภค):"
                    
                    value = float_input(input_label) # Use existing float_input
                                        
                    if value is not None:
                        nutrient_values[info['key']] = value
                        if nutrition_check_method == "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)" and is_vitamin_or_mineral(info['key']):
                            nutrient_values[info['key'] + "_is_direct_rdi"] = True
                        
                        # เก็บวิตามินที่กรอกไว้ใน session_state เพื่อใช้ในการตรวจสอบ
                        if "selected_vitamins" not in st.session_state:
                            st.session_state.selected_vitamins = []
                        if info['key'] not in st.session_state.selected_vitamins:
                            st.session_state.selected_vitamins.append(info['key'])
                i += 1

    # แสดงข้อมูลที่กรอกทั้งหมด (สำหรับดีบัก)
    debug_mode = False  # เปลี่ยนเป็น False ในเวอร์ชันสมบูรณ์
    if debug_mode:
        vitamin_keys = [k for k, v in nutrient_values.items() if v is not None and is_vitamin_or_mineral(k)]
        if vitamin_keys:
            st.write("ข้อมูลวิตามินและเกลือแร่ที่กรอก:")
            vitamin_data = {}
            for k in vitamin_keys:
                thai_name = RDI_MAPPING.get(k, k)
                vitamin_data[thai_name] = nutrient_values[k]
            st.json(vitamin_data)
        else:
            st.warning("ไม่พบข้อมูลวิตามินและเกลือแร่ที่กรอก")

    # ----------------- ปุ่มตรวจสอบคำกล่าวอ้าง -----------------
    if st.button("🔍 ตรวจสอบคำกล่าวอ้าง"):
        # ตรวจสอบกรณีต้องเตรียมแต่ไม่ได้กรอกปริมาณผง
        if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and 'prep_option' in locals() and prep_option == "ต้องเตรียม (เช่น ผงชง)":
            if manual_prep_grams is None:
                st.error("กรุณากรอกปริมาณผง (กรัม) ต่อ 100 มิลลิลิตร ก่อนทำการตรวจสอบ")
                st.stop()
        
        # Clear session state for report messages at the beginning of a new check
        # if "current_evaluation_messages_for_report" in st.session_state:
        #     del st.session_state.current_evaluation_messages_for_report # Clear for next run
        st.session_state.current_evaluation_messages_for_report = [] # Initialize for current run
        
        claims = load_claims_table(table_type)
        if claims.empty:
            st.error("ไม่สามารถดำเนินการตรวจสอบได้เนื่องจากไม่พบข้อมูลตารางคำกล่าวอ้าง")
            return

        # เก็บ disclaimers ไว้แสดงท้ายสุด
        final_disclaimer_results = None

        # Track which claims we've already processed to avoid duplicates
        processed_claims = set()
        duplicate_count = 0
        vm_duplicate_count = 0

        if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and "state" in claims.columns:
            claims = claims[claims["state"] == food_state_value]
            if claims.empty:
                st.error(f"ไม่พบข้อมูลคำกล่าวอ้างสำหรับอาหารประเภท {food_state_value}")
                return

        disclaimers = load_disclaimers()
        condition_lookup = load_condition_lookup()
        
        if condition_lookup.empty:
            st.error("ไม่พบข้อมูลเงื่อนไขการกล่าวอ้าง (condition_lookup.csv)")
            return

        adjusted_multiplier = 1.0
        
        if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
            try:
                ref_value = float(group_info["serving_value"])
                ref_unit = group_info["unit"].lower()
                
                if ref_unit in ["กรัม", "g", "ml", "มิลลิลิตร"]:
                    if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
                        # For analysis results (per 100g/ml), use the function from nutrition_cal.py
                        adjusted_values = adjust_per_100_to_serving(
                            nutrient_values=nutrient_values, 
                            serving_size=actual_serving_size, 
                            ref_serving_size=ref_value,
                            is_user_input=is_ref_serving_user_input
                        )
                        
                        # สร้าง label_values จากการคำนวณผลวิเคราะห์ต่อ 100g/ml ไปเป็นค่าต่อหน่วยบริโภคปกติ
                        # This is needed for checking claims against both conditions for foods in บัญชีหมายเลข 2
                        label_values = {}
                        serving_conversion = actual_serving_size / 100
                        for key, value in nutrient_values.items():
                            if value is not None:
                                label_values[key] = value * serving_conversion
                                # Round the value according to regulations
                                label_values[key] = round_nutrition_value(label_values[key], key)
                                
                                # Debug removed
                        
                        if ref_value <= 30:
                            if is_ref_serving_user_input:
                                st.info(f"สำหรับหน่วยบริโภคอ้างอิงที่ผู้ใช้กำหนด ≤ 30 {ref_unit}: ปรับจากค่าต่อ 100 {ref_unit} เป็นค่าต่อ {ref_value} {ref_unit}")
                            else:
                                st.info(f"สำหรับอาหารที่มีหน่วยบริโภคอ้างอิง ≤ 30 {ref_unit}: ปรับจากค่าต่อ 100 {ref_unit} เป็นค่าต่อ {ref_value * 2} {ref_unit}")
                        else:
                            st.info(f"สำหรับอาหารที่มีหน่วยบริโภคอ้างอิง > 30 {ref_unit}: ปรับจากค่าต่อ 100 {ref_unit} เป็นค่าต่อ {ref_value} {ref_unit}")
                    else:
                        # For nutrition label data (per serving), keep the original calculation
                        if ref_value <= 30:
                            if is_ref_serving_user_input:
                                # Do not double when the user has manually entered the reference serving size
                                adjusted_multiplier = ref_value / actual_serving_size
                                st.info(f"สำหรับหน่วยบริโภคอ้างอิงที่ผู้ใช้กำหนด ≤ 30 กรัม: คูณด้วย {ref_value} ÷ {actual_serving_size} = {adjusted_multiplier:.2f}")
                            else:
                                adjusted_multiplier = (ref_value * 2) / actual_serving_size
                                st.info(f"สำหรับอาหารที่มีหน่วยบริโภคอ้างอิง ≤ 30 กรัม: คูณปริมาณสารอาหารด้วย ({ref_value} × 2) ÷ {actual_serving_size} = {adjusted_multiplier:.2f}")
                        else:
                            adjusted_multiplier = ref_value / actual_serving_size
                            st.info(f"สำหรับอาหารที่มีหน่วยบริโภคอ้างอิง > 30 กรัม: คูณด้วย {ref_value} ÷ {actual_serving_size} = {adjusted_multiplier:.2f}")
                        
                        # Prepare nutrient_values for adjustment, converting direct RDI % to absolute amounts first
                        temp_nutrient_values_for_adjustment = {}
                        if not thai_rdis.empty: # Ensure RDI data is loaded
                            for key, value in nutrient_values.items():
                                if value is None:
                                    temp_nutrient_values_for_adjustment[key] = None
                                    continue

                                # Check if the key is for a vitamin/mineral and was input as direct RDI
                                if is_vitamin_or_mineral(key) and nutrient_values.get(key + "_is_direct_rdi"):
                                    try:
                                        direct_rdi_percent = float(value)
                                        thai_rdi_abs = get_rdi_value(key, thai_rdis)
                                        
                                        if thai_rdi_abs is not None and thai_rdi_abs > 0:
                                            abs_amount_label_serving = (direct_rdi_percent / 100.0) * thai_rdi_abs
                                            temp_nutrient_values_for_adjustment[key] = abs_amount_label_serving
                                        else:
                                            temp_nutrient_values_for_adjustment[key] = 0 # Fallback if RDI not found or zero
                                            st.warning(f"ไม่สามารถแปลง %RDI ของ {RDI_MAPPING.get(key, key)} เป็นค่าสัมบูรณ์ได้ เนื่องจากไม่พบค่า RDI หรือค่า RDI เป็น 0")
                                    except ValueError:
                                        st.error(f"ค่า %RDI ที่ระบุสำหรับ {RDI_MAPPING.get(key, key)} ('{value}') ไม่ใช่ตัวเลขที่ถูกต้อง")
                                        temp_nutrient_values_for_adjustment[key] = 0 # Fallback for invalid float conversion
                                else:
                                    # For other nutrients or non-direct RDI V/M, use the value as is
                                    temp_nutrient_values_for_adjustment[key] = value
                        else:
                            st.error("ไม่สามารถแปลงค่า %RDI ของวิตามิน/แร่ธาตุได้ เนื่องจากข้อมูล Thai RDIs ไม่พร้อมใช้งาน ทำให้ค่าที่ปรับแก้อาจไม่ถูกต้องสำหรับวิตามิน/แร่ธาตุที่กรอกเป็น %RDI")
                            # Fallback: use nutrient_values as is, which means %RDI will be treated as absolute if thai_rdis is missing
                            temp_nutrient_values_for_adjustment = nutrient_values.copy() 

                        adjusted_values = create_nutrient_dict(temp_nutrient_values_for_adjustment, adjusted_multiplier)
                        
                        # In this case, label_values is already equal to nutrient_values
                        label_values = nutrient_values.copy()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการคำนวณตัวปรับค่าสำหรับอาหารในบัญชีหมายเลข 2: {e}") # More specific error message
                # Fallback for adjusted_values (multiplier might not be correct, but provides a base)
                adjusted_multiplier = 1.0 
                adjusted_values = create_nutrient_dict(nutrient_values, adjusted_multiplier)
                
                # Fallback for label_values depends on the input method
                if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
                    # If analysis method, an error here means per-serving (label_values) calculation failed.
                    # Setting to {} prevents using per-100g values as per-serving values.
                    label_values = {}
                    st.warning("ไม่สามารถคำนวณค่าสารอาหารต่อหน่วยบริโภคบนฉลากจากผลวิเคราะห์ได้อย่างสมบูรณ์ อาจมีผลต่อการแสดง %RDI และการตรวจสอบคำกล่าวอ้างบางส่วน")
                else: # For "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)"
                    # If label input method, nutrient_values are already per-serving.
                    label_values = nutrient_values.copy() # This is a correct fallback.
        else:
            # This 'else' corresponds to: if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2"
            if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)" and \
               'prep_option' in locals() and prep_option == "ต้องเตรียม (เช่น ผงชง)" and \
               manual_prep_grams is not None and manual_prep_grams > 0:
                # ผู้ใช้กรอกปริมาณผงที่ใช้เตรียม 100 มิลลิลิตรพร้อมบริโภค
                # ผลวิเคราะห์เป็นต่อ 100 กรัมผง ดังนั้นต้องคูณ (manual_prep_grams / 100)
                conversion_factor = manual_prep_grams / 100.0
                adjusted_values = create_nutrient_dict(nutrient_values, conversion_factor)
                # คำนวณค่าต่อ 1 หน่วยบริโภคบนฉลาก (ปริมาณผงที่ใช้ต่อการบริโภค 1 ครั้ง)
                label_values = {}
                serving_conversion = actual_serving_size / 100.0  # actual_serving_size คือกรัมผงต่อหนึ่งหน่วยบริโภค
                for key, val in nutrient_values.items():
                    if val is not None:
                        per_serving_val = val * serving_conversion
                        label_values[key] = round_nutrition_value(per_serving_val, key)
                st.info(f"🔄 ปรับค่าผลวิเคราะห์ต่อ 100 กรัมผง เป็นต่อ 100 มิลลิลิตรพร้อมบริโภค (ใช้ {manual_prep_grams:.1f} กรัมผง)")
            else:
                adjusted_values = create_nutrient_dict(nutrient_values, adjusted_multiplier)  # adjusted_multiplier is 1.0 by default
                # คำนวณค่า label_values ต่อ 1 หน่วยบริโภคบนฉลากจากผลวิเคราะห์ต่อ 100 g/ml (ready-to-consume)
                label_values = {}
                serving_conversion = actual_serving_size / 100.0 if actual_serving_size > 0 else 1.0
                for key, val in nutrient_values.items():
                    if val is not None:
                        per_serving_val = val * serving_conversion
                        label_values[key] = round_nutrition_value(per_serving_val, key)
        
        if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and actual_serving_size > 0:
            # Only apply conversion if checking from nutrition label (per serving)
            # Skip conversion if checking from analysis results (already per 100g/ml)
            if nutrition_check_method == "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)":
                # หากเป็นผลิตภัณฑ์ที่ต้องเตรียม (ผงชง) และมีการกรอก manual_prep_grams ให้ใช้ค่านี้ในการแปลงเป็นต่อ 100 มิลลิลิตรพร้อมบริโภค
                if 'prep_option' in locals() and prep_option == "ต้องเตรียม (เช่น ผงชง)" and manual_prep_grams is not None and manual_prep_grams > 0:
                    conversion_factor = manual_prep_grams / actual_serving_size
                    st.info(f"🔄 ปรับค่าจาก {actual_serving_size:.1f} กรัมผง เป็นต่อ 100 มิลลิลิตรพร้อมบริโภค (ใช้ {manual_prep_grams:.1f} กรัม ต่อ 100 มิลลิลิตร)")
                else:
                    conversion_factor = 100 / actual_serving_size
                    unit_display = "กรัม" if food_state_value == "solid" else "มิลลิลิตร"
                    st.info(f"🔄 ทุกสารอาหารถูกคำนวณต่อ 100 {unit_display} (หน่วยบริโภคบนฉลาก {actual_serving_size} {unit_display})")

                for nutrient_key, value in nutrient_values.items():
                    if value is not None:
                        # If direct RDI input for V/M, convert %RDI to absolute amount first, then scale
                        if nutrient_values.get(nutrient_key + "_is_direct_rdi") and \
                           is_vitamin_or_mineral(nutrient_key) and \
                           not thai_rdis.empty:
                            
                            direct_rdi_percent = value # This is the user-inputted %RDI
                            thai_rdi_abs = get_rdi_value(nutrient_key, thai_rdis)
                            
                            if thai_rdi_abs is not None and thai_rdi_abs > 0:
                                abs_amount_label_serving = (direct_rdi_percent / 100.0) * thai_rdi_abs
                                adjusted_values[nutrient_key] = abs_amount_label_serving * conversion_factor
                            else:
                                # RDI not found or zero, cannot convert %RDI to absolute, set scaled value to 0
                                adjusted_values[nutrient_key] = 0 
                        else:
                            # Standard case: scale the absolute value
                            adjusted_values[nutrient_key] = value * conversion_factor
                
                unit_display = "กรัม" if food_state_value == "solid" else "มิลลิลิตร"
                st.info(f"🔄 ทุกสารอาหารถูกคำนวณต่อ 100 {unit_display} (หน่วยบริโภคบนฉลาก {actual_serving_size} {unit_display})")
            else:
                # If checking from analysis results, values are already per 100g/ml
                unit_display = "กรัม" if food_state_value == "solid" else "มิลลิลิตร"
            
            if adjusted_values.get("energy") is not None and adjusted_values.get("energy") > 0:
                energy_per_100 = adjusted_values["energy"]
                
                # Use the calculate_per_100kcal function from nutrition_cal.py
                per_100kcal_values = calculate_per_100kcal(adjusted_values, energy_per_100)
                adjusted_values.update(per_100kcal_values)
                
                # Calculate %RDI per 100kcal for vitamins and minerals
                if not thai_rdis.empty:
                    for nutrient_key, value in adjusted_values.items():
                        if value is not None and "_rdi_percent" not in nutrient_key and is_vitamin_or_mineral(nutrient_key):
                            rdi_value = get_rdi_value(nutrient_key, thai_rdis)
                            if rdi_value is not None:
                                percent_rdi_per_100kcal = (value * (100 / energy_per_100) / rdi_value) * 100
                                per_100kcal_values[f"{nutrient_key}_rdi_percent_per_100kcal"] = round_nutrition_value(percent_rdi_per_100kcal, 1)
                    
                    # Update with the additional RDI percentages
                    adjusted_values.update(per_100kcal_values)
                    
                st.info(f"🔄 คำนวณค่าสารอาหารต่อ 100 kcal สำหรับโปรตีน, ใยอาหาร และวิตามิน/แร่ธาตุแล้ว")
            else:
                st.error("ไม่สามารถคำนวณค่าต่อ 100 kcal เนื่องจากไม่มีค่าพลังงานหรือค่าพลังงานเป็น 0")
        
        # ย้ายการแสดงผลการปัดเลขสำหรับสารอาหารมาที่นี่ หลังจากปรับค่าแล้ว
        with st.expander("ดูผลการปัดเลขสารอาหารตามหลักเกณฑ์กฎหมาย", expanded=False):
            # นำข้อมูล adjusted_values มาสร้างตารางแสดงผลการปัดเลข (ใช้ค่าที่ปรับแล้ว)
            # เก็บค่าที่ยังไม่ปัดเลขเพื่อแสดงเปรียบเทียบ
            unrounded_values = {}
            for key, value in adjusted_values.items():
                if value is not None and "_per_100kcal" not in key and "_rdi_percent" not in key:
                    if nutrition_check_method == "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)" and is_vitamin_or_mineral(key):
                        continue  # Skip vitamins and minerals for this method in the rounding display
                    unrounded_values[key] = value
            
            # กำหนดค่าตัวแปรที่จะส่งไปยังฟังก์ชัน prepare_rounded_values_display
            is_in_list_2 = selected_label != "ไม่อยู่ในบัญชีหมายเลข 2"
            serving_size_value = actual_serving_size if actual_serving_size > 0 else 0
            # Determine reference serving size value for the report
            if is_in_list_2:
                # For foods in List 2, use the reference serving size from the food group information
                try:
                    ref_serving_size_value = float(group_info["serving_value"]) if group_info is not None else 0
                except (ValueError, TypeError, KeyError):
                    ref_serving_size_value = 0
            else:
                # For foods NOT in List 2, the reference is always 100 g/ml by regulation
                ref_serving_size_value = 100
            
            # --- END reference serving size determination ---
            


            # นำค่าที่ยังไม่ปัดเลขมาสร้างตารางเปรียบเทียบกับค่าที่ปัดเลขแล้ว
            rounded_display_data = prepare_rounded_values_display(
                unrounded_values, 
                serving_size=serving_size_value,
                ref_serving_size=ref_serving_size_value,
                is_in_list_2=is_in_list_2,
                original_input_values=nutrient_values,
                is_from_analysis=(nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)"),
                skip_double_small_ref=is_ref_serving_user_input
            )
            
            # สร้างตารางแสดงผล
            if rounded_display_data:
                st.markdown("### ค่าสารอาหารก่อนและหลังการปัดเลข")
                st.markdown("ตามประกาศกระทรวงสาธารณสุข (ฉบับที่ 445) พ.ศ.2566 เรื่องฉลากโภชนาการ")
                
                # แสดงข้อมูลหน่วยที่ใช้สำหรับการปัดเลข
                if is_in_list_2:
                    if group_info is not None:
                        ref_unit = group_info["unit"].lower()
                        ref_value = float(group_info["serving_value"])
                        display_size = ref_value if (ref_value <= 30 and is_ref_serving_user_input) else (ref_value * 2 if ref_value <= 30 else ref_value)
                else:
                    unit_display = "กรัม" if food_state_value == "solid" else "มิลลิลิตร"
                
                # สร้าง DataFrame
                df_rounded = pd.DataFrame(rounded_display_data)
                
                # ปรับชื่อคอลัมน์เพื่อการแสดงผล
                if is_in_list_2:
                    # กรณีอาหารอยู่ในบัญชีหมายเลข 2 แสดงค่าครบทุกขั้นตอน
                    df_display = df_rounded[["nutrient", "per_100g", "per_serving", "per_serving_rounded", "per_ref_serving", "per_ref_serving_rounded", "unit"]]
                    
                    # หน่วยบริโภคบนฉลากและหน่วยบริโภคอ้างอิง
                    # แก้ไขการตรวจสอบ group_info จากการใช้เงื่อนไข if โดยตรง เป็นการตรวจสอบว่ามีค่าหรือไม่
                    try:
                        ref_unit = group_info["unit"].lower() if isinstance(group_info, pd.Series) and "unit" in group_info else "g/ml"
                        serving_display = f"{serving_size_value} {ref_unit}"
                        
                        # คำนวณ reference serving display
                        factor = 2 if (ref_serving_size_value <= 30 and not is_ref_serving_user_input) else 1
                        display_ref_size = ref_serving_size_value * factor
                        ref_serving_display = f"{display_ref_size} {ref_unit}"
                    except (TypeError, AttributeError, KeyError):
                        # ถ้าเกิดข้อผิดพลาดใดๆ ใช้ค่าเริ่มต้น
                        serving_display = f"{serving_size_value} g/ml"
                        ref_serving_display = f"{ref_serving_size_value} g/ml"
                    
                    # กำหนดชื่อคอลัมน์
                    column_names = {
                        "nutrient": "สารอาหาร",
                        "per_100g": f"ต่อ 100 g/ml",
                        "per_serving": f"ต่อ {serving_display}",
                        "per_serving_rounded": f"{serving_display}ปัดเลข",
                        "per_ref_serving": f"ต่อ {ref_serving_display}",
                        "per_ref_serving_rounded": f"{ref_serving_display}ปัดเลข",
                        "unit": "หน่วย"
                    }
                    # Check for duplicate names and adjust column_names dictionary IF IN LIST 2
                    if serving_display == ref_serving_display:
                        column_names["per_serving"] = f"ต่อ {serving_display} (ฉลาก)"
                        column_names["per_serving_rounded"] = f"{serving_display}ปัดเลข (ฉลาก)"
                        column_names["per_ref_serving"] = f"ต่อ {ref_serving_display} (อ้างอิง)"
                        column_names["per_ref_serving_rounded"] = f"{ref_serving_display}ปัดเลข (อ้างอิง)"
                else:
                    # กรณีอาหารไม่อยู่ในบัญชีหมายเลข 2 แสดงเฉพาะค่าต่อ 100g/ml
                    df_display = df_rounded[["nutrient", "input_value", "per_serving", "per_serving_rounded", "per_ref_serving", "per_ref_serving_rounded", "unit"]]
                    column_names = {
                        "nutrient": "สารอาหาร",
                        "input_value": "ค่าที่กรอก",
                        "per_serving": "ค่าบนฉลาก",
                        "per_serving_rounded": "ปัดเลข(ฉลาก)",
                        "per_ref_serving": "ค่าอ้างอิง",
                        "per_ref_serving_rounded": "ปัดเลข(อ้างอิง)",
                        "unit": "หน่วย"
                    }
                
                # ตั้งชื่อคอลัมน์
                df_display.columns = list(column_names.values())
                
                # แสดงตาราง
                st.dataframe(df_display, hide_index=True)
            else:
                st.warning("ไม่มีข้อมูลสารอาหารสำหรับการแสดงผลการปัดเลข")

        if nutrient_values.get("saturated_fat") is not None and nutrient_values.get("energy") is None:
            st.error("คุณได้กรอกค่าไขมันอิ่มตัวแต่ไม่ได้กรอกค่าพลังงาน กรุณากรอกค่าพลังงานเพื่อการคำนวณที่ถูกต้อง")
            return
        
        if table_type == "table1" and has_added_sugar == "ไม่มีการเติมน้ำตาล":
            if nutrient_values["energy"] is None:
                st.error("กรุณากรอกค่าพลังงานก่อนทำการตรวจสอบ")
                return
                
            energy_value = adjusted_values.get("energy")
            is_low_energy = energy_value is not None and energy_value <= 40
            
            sugar_claim_message = f"""
            ✅ น้ำตาล (sugar): สามารถใช้คำกล่าวอ้าง: ไม่เติมน้ำตาล (no sugar added)

            **เงื่อนไขการกล่าวอ้าง:**
            1. ไม่มีส่วนประกอบที่มีการเติมหรือเพิ่มปริมาณน้ำตาล เช่น แยม เยลลี น้ำผลไม้เข้มข้น หรือนมข้นหวาน
            2. ไม่มีการเติมน้ำตาลหรือส่วนประกอบอื่นที่มีน้ำตาล เพื่อทำหน้าที่แทนน้ำตาลในระหว่างการผลิตหรือบรรจุ
            3. น้ำตาลที่เกิดขึ้นจากระบวนการผลิต (ถ้ามี) ต้องเป็นไปตามเงื่อนไข "ปราศจาก/ไม่มี"
            """
            
            energy_warning = None
            if not is_low_energy:
                energy_warning = "⚠️ ต้องกำกับว่า \"ไม่ใช่อาหารพลังงานต่ำ\""

        if adjusted_values.get("saturated_fat") is not None and adjusted_values.get("energy") is not None:
            saturated_fat_energy_percent = calculate_energy_from_saturated_fat(
                adjusted_values["saturated_fat"], 
                adjusted_values["energy"]
            )
            if saturated_fat_energy_percent is not None:
                adjusted_values["saturated_fat_energy_percent"] = saturated_fat_energy_percent
        
        
        # คำนวณ disclaimers หลังจากมีค่า adjusted_values แล้ว
        final_disclaimer_results = prepare_disclaimers(
            nutrient_values, 
            adjusted_values, 
            selected_label, 
            actual_serving_size, 
            food_state_value, 
            group_info,
            nutrition_check_method  # Pass nutrition_check_method
        )

        # label_values should be correctly populated by prior logic (lines 473-519).
        # The re-initialization `label_values = {}` (original line 683) is removed or made conditional.
        # The overwrite `label_values = nutrient_values.copy()` (original line 685) is the main issue for List 2 Analysis Method.

        # If label_values is not already a dictionary (e.g. due to some unexpected path), initialize it.
        if not isinstance(label_values, dict):
            label_values = {}

        # The problematic line `label_values = nutrient_values.copy()` (original line 685) is now commented out 
        # to preserve the `label_values` calculated for List 2, Analysis Method (lines 484-490).
        # For other scenarios, label_values is already nutrient_values.copy() or an empty dict from exceptions.
        
        # Correctly initialize/copy label_values based on the method
        # If analysis per 100g, label_values should have been populated by adjust_per_100_to_serving
        # If label per serving, label_values is a copy of nutrient_values (raw inputs)
        if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
            if not isinstance(label_values, dict):
                 label_values = {} # Fallback, though it should be set
        else: # "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)"
            temp_label_values = {}
            for k, v_val in nutrient_values.items():
                if not k.endswith("_is_direct_rdi"): 
                    temp_label_values[k] = v_val
            label_values = temp_label_values


        try:
            # label_values = nutrient_values.copy() # THIS LINE (original 685) IS THE CULPRIT - KEEPING IT COMMENTED
            
            if label_values.get("saturated_fat") is not None and label_values.get("energy") is not None:
                sf_val = label_values["saturated_fat"]
                en_val = label_values["energy"]
                if isinstance(sf_val, (int, float)) and isinstance(en_val, (int, float)):
                    label_saturated_fat_energy_percent = calculate_energy_from_saturated_fat(
                        float(sf_val), 
                        float(en_val)
                    )
                    if label_saturated_fat_energy_percent is not None:
                        label_values["saturated_fat_energy_percent"] = label_saturated_fat_energy_percent
            
            if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                if group_info is not None and isinstance(group_info, pd.Series) and 'serving_value' in group_info:
                    ref_value = float(group_info["serving_value"])
                    if ref_value <= 30:
                        st.info("กรณีอาหารที่มีหน่วยบริโภคอ้างอิง ≤ 30 กรัม: ระบบจะตรวจสอบทั้งจากค่าที่ปรับแก้ (หน่วยบริโภคอ้างอิง x 2) และค่าจากฉลาก")
                    else:
                        st.info("กรณีอาหารที่มีหน่วยบริโภคอ้างอิง > 30 กรัม: ระบบจะตรวจสอบทั้งจากค่าที่ปรับแก้และค่าจากฉลาก")
                else: 
                    st.warning("ไม่สามารถอ่านค่าหน่วยบริโภคอ้างอิงได้ ข้อมูลบางส่วนอาจไม่ถูกต้อง")

            else: # Not in List 2
                st.info("กรณีไม่อยู่ในบัญชีหมายเลข 2: ระบบจะคำนวณปริมาณสารอาหารต่อ 100g/100ml เท่านั้น")

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการตรวจสอบหน่วยบริโภค: {e}")

        # --- START NEW RDI CALCULATION LOGIC ---
        if not thai_rdis.empty:
            # Process label_values first (per serving values)
            for nutrient_key in list(label_values.keys()): # Iterate over copy of keys
                if nutrient_values.get(nutrient_key + "_is_direct_rdi"): # Check original nutrient_values for the flag
                    # User inputted %RDI directly. 'value' from nutrient_values.items() is this direct %RDI.
                    direct_rdi_percentage = label_values[nutrient_key] # This is the %RDI value
                    label_values[nutrient_key + "_rdi_percent"] = direct_rdi_percentage
                    
                    # Calculate absolute amount from this %RDI
                    thai_rdi_abs = get_rdi_value(nutrient_key, thai_rdis)
                    if thai_rdi_abs is not None and thai_rdi_abs > 0:
                        absolute_amount = (direct_rdi_percentage / 100.0) * thai_rdi_abs
                        label_values[nutrient_key] = absolute_amount # Overwrite/set absolute amount
                    else:
                        label_values[nutrient_key] = 0 # Or some indicator of uncalculable
                # For nutrients where user inputted absolute amount, calculate %RDI.
                # This applies to vitamins, minerals, protein, fiber, etc., that have an RDI.
                # Ensure we are not reprocessing already calculated RDI values or flags.
                elif not nutrient_key.endswith(('_rdi_percent', '_per_100kcal', '_is_direct_rdi')) and \
                     adjusted_values.get(nutrient_key) is not None:
                    thai_rdi_abs = get_rdi_value(nutrient_key, thai_rdis)
                    if thai_rdi_abs is not None and thai_rdi_abs > 0:
                        current_adj_val = adjusted_values.get(nutrient_key)
                        if isinstance(current_adj_val, (int, float)):
                            computed_rdi = (float(current_adj_val) / thai_rdi_abs) * 100
                            if is_vitamin_or_mineral(nutrient_key):
                                computed_rdi = round_rdi_percent(computed_rdi)
                            adjusted_values[nutrient_key + "_rdi_percent"] = computed_rdi
                        else:
                            adjusted_values[nutrient_key + "_rdi_percent"] = 0 # Default to 0 if value is not numeric
                            
                        # Calculate %RDI per 100kcal if not in List 2 and applicable
                        if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2": 
                            energy_per_100 = adjusted_values.get("energy")
                            if energy_per_100 is not None and energy_per_100 > 0 and isinstance(current_adj_val, (int, float)):
                                nutrient_per_100kcal = (float(current_adj_val) * 100.0) / energy_per_100
                                adjusted_values[f"{nutrient_key}_rdi_percent_per_100kcal"] = round_nutrition_value((nutrient_per_100kcal / thai_rdi_abs) * 100, 1)
                    else:
                        # If RDI is not applicable (no thai_rdi_abs or it's 0), set _rdi_percent to 0,
                        # but only if it hasn't been set by a preceding condition (e.g. _is_direct_rdi path).
                        if adjusted_values.get(nutrient_key + "_rdi_percent") is None:
                             adjusted_values[nutrient_key + "_rdi_percent"] = 0
                elif (is_vitamin_or_mineral(nutrient_key) or nutrient_key in ["protein", "fiber"]) and adjusted_values.get(nutrient_key) is not None:
                    thai_rdi_abs = get_rdi_value(nutrient_key, thai_rdis)
                    if thai_rdi_abs is not None and thai_rdi_abs > 0:
                        current_adj_val = adjusted_values.get(nutrient_key)
                        if isinstance(current_adj_val, (int, float)):
                            computed_rdi = (float(current_adj_val) / thai_rdi_abs) * 100
                            if is_vitamin_or_mineral(nutrient_key):
                                computed_rdi = round_rdi_percent(computed_rdi)
                            adjusted_values[nutrient_key + "_rdi_percent"] = computed_rdi
                        else:
                            adjusted_values[nutrient_key + "_rdi_percent"] = 0
                            
                        if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                            energy_per_100 = adjusted_values.get("energy")
                            if energy_per_100 is not None and energy_per_100 > 0 and isinstance(current_adj_val, (int, float)):
                                nutrient_per_100kcal = (float(current_adj_val) * 100.0) / energy_per_100
                                adjusted_values[f"{nutrient_key}_rdi_percent_per_100kcal"] = round_nutrition_value((nutrient_per_100kcal / thai_rdi_abs) * 100, 1)
                    else:
                        adjusted_values[nutrient_key + "_rdi_percent"] = 0
        # --- END NEW RDI CALCULATION LOGIC ---

        # Comment out or remove the OLD RDI calculation block to prevent interference
        # if not thai_rdis.empty:
        #     rdi_values = {}
        #     has_vitamins_minerals = False
        #     for nutrient_key, value in nutrient_values.items():
        #         if value is not None and is_vitamin_or_mineral(nutrient_key) and not nutrient_key.endswith("_is_direct_rdi"):
        #             has_vitamins_minerals = True
        #             break
        #     for nutrient_key, value in nutrient_values.items():
        #         if value is not None and not nutrient_key.endswith("_is_direct_rdi"):
        #             if nutrient_key in ["energy", "fat", "saturated_fat", "trans_fat", "cholesterol", "carbohydrate", "sugar", "sodium"]:
        #                 continue
        #             rdi_value = get_rdi_value(nutrient_key, thai_rdis)
        #             if rdi_value is not None:
        #                 pass # This logic is now handled above

        # แสดงตาราง %RDI (แสดงทุกครั้งที่มีค่า RDI หรือมีการกรอกวิตามิน/แร่ธาตุ)
        has_rdi_data = False
        rdi_data = []
        
        # ตรวจสอบทุกสารอาหารที่มีในข้อมูล
        for nutrient_key, value in nutrient_values.items():
            if value is not None:
                rdi_value = get_rdi_value(nutrient_key, thai_rdis)
                if rdi_value is not None:
                    has_rdi_data = True
                    
                    label_percent_rdi = None
                    # Determine how to get/calculate label_percent_rdi
                    if nutrition_check_method == "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)" and \
                       is_vitamin_or_mineral(nutrient_key) and \
                       nutrient_values.get(nutrient_key + "_is_direct_rdi"):
                        # User inputted %RDI directly. 'value' from nutrient_values.items() is this direct %RDI.
                        label_percent_rdi = value 
                    else:
                        # Calculate %RDI from an absolute amount per label serving.
                        # This absolute amount is either from scaled analysis (in label_values for analysis method)
                        # or direct absolute input ('value' from nutrient_values for label method, non-direct RDI V/M or non-V/M).
                        absolute_amount_on_label = None
                        if nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
                            if label_values and nutrient_key in label_values and label_values[nutrient_key] is not None:
                                absolute_amount_on_label = label_values[nutrient_key]
                        else: # "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)"
                              # This branch covers:
                              # 1. Non-vitamins/minerals (where 'value' is absolute amount)
                              # 2. Vitamins/minerals where absolute amount was input (i.e., _is_direct_rdi is False or not present)
                            absolute_amount_on_label = value # 'value' is the absolute amount here

                        if absolute_amount_on_label is not None and rdi_value is not None and rdi_value > 0:
                            label_percent_rdi = (absolute_amount_on_label / rdi_value) * 100
                            if is_vitamin_or_mineral(nutrient_key):
                                label_percent_rdi = round_rdi_percent(label_percent_rdi)
                    
                    # คำนวณ %RDI จากหน่วยบริโภคอ้างอิง (Uses adjusted_values)
                    ref_percent_rdi = None 
                    if adjusted_values and nutrient_key in adjusted_values and adjusted_values[nutrient_key] is not None and rdi_value is not None and rdi_value > 0:
                            ref_percent_rdi = (adjusted_values[nutrient_key] / rdi_value) * 100
                            if is_vitamin_or_mineral(nutrient_key):
                                ref_percent_rdi = round_rdi_percent(ref_percent_rdi)
                    
                    thai_name = RDI_MAPPING.get(nutrient_key)
                    nutrient_display = thai_name if thai_name else nutrient_key
                    
                    rdi_data.append({
                        "สารอาหาร": nutrient_display,
                        "%Thai RDI จากหน่วยบริโภคบนฉลาก": f"{label_percent_rdi:.1f}%" if label_percent_rdi is not None else "N/A",
                        "%Thai RDI ตามหน่วยบริโภคอ้างอิง": f"{ref_percent_rdi:.1f}%" if ref_percent_rdi is not None else "N/A"
                    })
        
        if has_rdi_data:
            st.markdown("<small>% Thai RDI ที่คำนวณได้จากหน่วยบริโภคบนฉลากและหน่วยบริโภคอ้างอิง</small>", unsafe_allow_html=True)
            rdi_df = pd.DataFrame(rdi_data)
            st.dataframe(rdi_df, hide_index=True)

        # แสดงผลการตรวจสอบทั้งหมด
        st.markdown("### ผลการตรวจสอบ")
        results_found = False
        warning_shown = False  # เพิ่มตัวแปรเพื่อติดตามว่ามีการแสดงข้อความเตือนแล้วหรือไม่

        # ตรวจสอบทั่วไป
        for idx, row in claims.iterrows():
            nutrient = row["nutrient"]
            threshold_str = str(row["threshold"])
            threshold_rdi = str(row["threshold_rdi"]) if not pd.isna(row["threshold_rdi"]) else ""
            claim_text = row["claim_text"]
            condition_id = row.get("condition", "")
            special_rule = row.get("special_rule", "")
            
            # Generate a unique identifier for this claim to avoid duplicates
            claim_key = f"{nutrient}_{claim_text}"
            
            # Skip if we've already processed this combination of nutrient and claim text
            if claim_key in processed_claims:
                duplicate_count += 1
                continue
                
            # Add to processed claims
            processed_claims.add(claim_key)
            
            # Add debug information for claim evaluation
            if "fiber" in str(nutrient).lower() or "ใยอาหาร" in str(nutrient):
                # คำนวณค่า fiber per 100kcal
                if adjusted_values.get("fiber") is not None and adjusted_values.get("energy") is not None:
                    energy = adjusted_values.get("energy")
                    fiber = adjusted_values.get("fiber")
                    if energy > 0:
                        # การคำนวณที่ถูกต้อง: สัดส่วนใยอาหารต่อ 100kcal
                        fiber_per_100kcal = fiber * (100 / energy)
                        # เก็บค่า fiber_per_100kcal ไว้ในตัวแปร
                        adjusted_values["fiber_per_100kcal"] = fiber_per_100kcal
                        # แสดงค่า DEBUG เพื่อตรวจสอบการคำนวณ
                        # Debug removed
                else:
                    # st.write("DEBUG - ไม่สามารถคำนวณค่าใยอาหารต่อ 100kcal ได้เนื่องจากไม่มีค่าใยอาหารหรือพลังงาน")
                    pass
                
            # ตรวจสอบว่ามีคอลัมน์ saturate_fat_energy<=10%Energy หรือไม่
            saturate_fat_energy_condition = row.get("saturate_fat_energy<=10%Energy", "")
            
            # ตรวจสอบว่า saturate_fat_energy_condition เป็นสตริงหรือไม่
            if not isinstance(saturate_fat_energy_condition, str):
                saturate_fat_energy_condition = str(saturate_fat_energy_condition) if saturate_fat_energy_condition is not None else ""
            
            # ตรวจสอบเงื่อนไขพลังงานจากไขมันอิ่มตัว (ถ้ามี)
            is_saturated_fat_energy_condition = saturate_fat_energy_condition and saturate_fat_energy_condition.lower() == "true"

            nutrient_key = normalize_nutrient_key(nutrient)
            
            # ข้ามการตรวจสอบสารอาหารที่ไม่มีการกรอกข้อมูล
            if adjusted_values.get(nutrient_key) is None:
                continue

            # Debug: สำหรับ fiber claim evaluation
            if nutrient_key == "fiber":
                # st.info(f"DEBUG - Fiber evaluation start: nutrient={nutrient}, claim={claim_text}, thresh={threshold_str}")
                # st.info(f"DEBUG - Condition 1: selected_label='{selected_label}', food_state='{food_state}', food_state_value='{food_state_value}'")
                # if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                #     st.info(f"DEBUG - *** This is IN list 2 (selected_label={selected_label}) ***")
                # else:
                #     st.info(f"DEBUG - *** This is NOT in list 2 (selected_label={selected_label}) ***")
                pass

            # Issue: Selected "อยู่ในบัญชีหมายเลข 2" but evaluating as if not
            # Fix: Make sure we're correctly determining if we're in list 2 
            is_in_list_2 = selected_label != "ไม่อยู่ในบัญชีหมายเลข 2"
            
            # Start of claim evaluation debug
            if nutrient_key == "fiber":
                if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                    # st.info(f"DEBUG - Evaluating High Fiber Claim: claim_text={claim_text}, threshold={threshold_str}, value={adjusted_values.get('fiber')}")
                    pass
                elif "แหล่งของ" in claim_text or ("source" in claim_text.lower() and "excellent source" not in claim_text.lower()):
                    # st.info(f"DEBUG - Evaluating Source Fiber Claim: claim_text={claim_text}, threshold={threshold_str}, value={adjusted_values.get('fiber')}")
                    pass

            # ประเมินเงื่อนไขจาก adjusted_values - เฉพาะกรณีที่ threshold_str ไม่ใช่ "nan"
            if threshold_str == "nan":
                # ถ้า threshold เป็น nan การตัดสินใจจะขึ้นอยู่กับ threshold_100kcal หรือ threshold_rdi ภายหลัง
                # *** การแก้ไขหลัก: สำหรับใยอาหารเหลวที่ไม่อยู่ในบัญชี 2 ต้องเริ่มเป็น False เสมอ ***
                if nutrient_key == "fiber" and not is_in_list_2 and food_state_value == "liquid":
                     adjusted_result = False # <<< แก้ไขตรงนี้
                # --- คงตรรกะเดิมสำหรับกรณีอื่นไว้ก่อน (อาจต้องทบทวนภายหลัง) ---
                elif nutrient_key == "fiber" and not is_in_list_2 and food_state_value == "solid":
                     adjusted_result = True 
                # เพิ่ม elif สำหรับกรณีอื่นๆ ที่ไม่ใช่ fiber หรืออยู่ในบัญชี 2
                elif nutrient_key != "fiber" or is_in_list_2:
                     adjusted_result = True # คงตรรกะเดิม
                else: # กรณีที่ไม่ควรเกิดขึ้น
                     adjusted_result = False
                # ต้องตรวจสอบ threshold จริงที่ต้องใช้
                if nutrient_key == "fiber" and not is_in_list_2:
                    # กรณีของเหลวไม่อยู่ในบัญชีหมายเลข 2 ใช้ค่าเฉพาะเจาะจง
                    if food_state_value == "liquid":
                        fiber_value = adjusted_values.get("fiber")
                        # st.info(f"DEBUG - Processing liquid fiber (nan thresh): value={fiber_value}, claim={claim_text}")
                        if fiber_value is not None:
                            # Detailed debug for claim text detection
                            # st.info(f"DEBUG - Claim text details: text='{claim_text}', length={len(claim_text)}")
                            # st.info(f"DEBUG - 'สูง' in text: {'สูง' in claim_text}, 'high' in text: {'high' in claim_text.lower()}, 'rich' in text: {'rich' in claim_text.lower()}")
                            # st.info(f"DEBUG - 'แหล่งของ' in text: {'แหล่งของ' in claim_text}, 'source' in text: {'source' in claim_text.lower()}")
                            
                            # Check for high first to avoid matching "source" in "excellent source of"
                            if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                                # For "high" claim: must be >= 3g
                                adjusted_result = fiber_value >= 3.0
                                # st.info(f"DEBUG - Special fiber HIGH check (nan thresh): {fiber_value} >= 3.0 = {adjusted_result}")
                                # Add extra check to verify this is definitely a high claim
                                # st.info(f"DEBUG - Claim verification: high/สูง in claim: {'สูง' in claim_text}, high in claim: {'high' in claim_text.lower()}, rich in claim: {'rich' in claim_text.lower()}")
                            # More specific source detection to avoid false positives from "excellent source of"
                            elif "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                                # For "high" claim: must be >= 3g
                                adjusted_result = fiber_value >= 3.0
                                # st.info(f"DEBUG - Special fiber HIGH check (nan thresh): {fiber_value} >= 3.0 = {adjusted_result}")
                                # Add extra check to verify this is definitely a high claim
                                # st.info(f"DEBUG - Claim verification: high/สูง in claim: {'สูง' in claim_text}, high in claim: {'high' in claim_text.lower()}, rich in claim: {'rich' in claim_text.lower()}")
                            # More specific source detection to avoid false positives from "excellent source of"
                            elif "แหล่งของ" in claim_text or (" source " in (" " + claim_text.lower() + " ")) or claim_text.lower().startswith("source"):
                                # For "source of" claim: must be >= 1.5g
                                adjusted_result = fiber_value >= 1.5
                                # st.info(f"DEBUG - Special fiber SOURCE check (nan thresh): {fiber_value} >= 1.5 = {adjusted_result}")
                            else:
                                # st.info(f"DEBUG - No specific claim text match for fiber with nan threshold")
                                adjusted_result = False
                        else:
                            # st.info(f"DEBUG - No fiber value provided with nan threshold")
                            adjusted_result = False
                    else:
                        adjusted_result = True  # สำหรับของแข็ง ใช้ค่าตาม threshold_rdi
                else:
                    adjusted_result = True  # สำหรับสารอาหารอื่นที่ไม่ใช่ fiber หรือกรณีอยู่ในบัญชีหมายเลข 2
            else:
                # ตรวจสอบว่ามีการกำหนด threshold_100kcal หรือไม่
                threshold_100kcal = str(row.get("threshold_100kcal", "nan"))
                
                # Debug: แสดง threshold สำหรับ fiber
                if nutrient_key == "fiber" and not is_in_list_2 and food_state_value == "liquid":
                    # st.info(f"DEBUG - fiber: thresh={threshold_str}, thresh_100kcal={threshold_100kcal}, value={adjusted_values.get('fiber')}, food_state={food_state}, claim_text={claim_text}")
                    pass
                
                # ตรวจสอบปริมาณต่อ 100g/100ml เป็นค่าเริ่มต้น
                adjusted_result = evaluate_threshold(threshold_str, adjusted_values, nutrient_key, None)
                
                # Debug: แสดงผลการประเมินเงื่อนไข
                if nutrient_key == "fiber" and not is_in_list_2 and food_state_value == "liquid":
                    # st.info(f"DEBUG - fiber eval result: {adjusted_result}, ค่า threshold: {threshold_str}")
                    # สำหรับใยอาหารในอาหารของเหลวที่ไม่อยู่ในบัญชีหมายเลข 2
                    # ไม่ใช้ผลการตรวจสอบต่อ 100g/ml (adjusted_result) แต่จะใช้เกณฑ์ต่อ 100kcal เท่านั้น
                    adjusted_result = False  # รีเซ็ตผลลัพธ์เริ่มต้น เพื่อให้ตัดสินใจด้วยเกณฑ์ต่อ 100kcal เท่านั้น
                    pass
                
                # สำหรับโปรตีนและใยอาหารในอาหารที่ไม่อยู่ในบัญชีหมายเลข 2
                # ตรวจสอบทั้งแบบต่อ 100g/100ml และต่อ 100kcal
                if not is_in_list_2 and threshold_100kcal != "nan" and nutrient_key in ["protein", "fiber"]:
                    per_100kcal_key = f"{nutrient_key}_per_100kcal"
                    
                    # ตรวจสอบว่ามีค่า per_100kcal หรือไม่
                    if per_100kcal_key in adjusted_values:
                        # สร้าง values_dict ชั่วคราวที่เก็บค่า per_100kcal_key ในชื่อ nutrient_key
                        temp_values = {nutrient_key: adjusted_values.get(per_100kcal_key)}
                        
                        # Debug: แสดงค่า per_100kcal สำหรับ fiber ในอาหารของเหลว
                        if nutrient_key == "fiber" and food_state_value == "liquid":
                            # st.info(f"DEBUG - fiber per 100kcal: value={adjusted_values.get(per_100kcal_key)}, threshold={threshold_100kcal}")
                            pass
                        
                        # ตรวจสอบเงื่อนไขต่อ 100kcal
                        per_100kcal_result = evaluate_threshold(threshold_100kcal, temp_values, nutrient_key, None)
                        
                        # Debug: แสดงผลการประเมินต่อ 100kcal
                        if nutrient_key == "fiber" and food_state_value == "liquid":
                            # st.info(f"DEBUG - fiber per 100kcal eval result: {per_100kcal_result}")
                            pass
                        
                        # กรณีพิเศษสำหรับใยอาหารในอาหารของเหลว
                        if nutrient_key == "fiber" and food_state_value == "liquid" and not is_in_list_2:
                            # ใช้เฉพาะผลการตรวจสอบต่อ 100kcal - แต่ต้องใช้ค่าตามเกณฑ์
                            fiber_value = adjusted_values.get("fiber")
                            fiber_per_100kcal = adjusted_values.get("fiber_per_100kcal")
                            
                            if fiber_value is not None and fiber_per_100kcal is not None:
                                # DEBUG: แสดงค่าที่ใช้ในการตรวจสอบ
                                # Debug removed
                                
                                if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                                    # For "high" claim: must be >= 3g per 100kcal for liquid foods not in list 2
                                    threshold_met = fiber_per_100kcal >= 3.0
                                    # ใช้เฉพาะผลการประเมินต่อ 100kcal เท่านั้น
                                    # Debug removed
                                    adjusted_result = threshold_met
                                elif "แหล่งของ" in claim_text or ("source" in claim_text.lower() and "excellent source" not in claim_text.lower()):
                                    # For "source of" claim: must be >= 1.5g per 100kcal for liquid foods not in list 2
                                    threshold_met = fiber_per_100kcal >= 1.5
                                    # ใช้เฉพาะผลการประเมินต่อ 100kcal เท่านั้น
                                    # Debug removed
                                    adjusted_result = threshold_met
                                else:
                                    adjusted_result = False
                            else:
                                adjusted_result = False
                        else:
                            # สำหรับโปรตีนและใยอาหารในอาหารของแข็ง
                            # อาหารนั้นผ่านเงื่อนไขหากผ่านเงื่อนไขใดเงื่อนไขหนึ่ง (OR)
                            adjusted_result = adjusted_result or per_100kcal_result
            
            # Fix: For foods in list 2 (บัญชีหมายเลข 2) check fiber claims more strictly
            if is_in_list_2 and nutrient_key == "fiber":
                fiber_value = adjusted_values.get("fiber")
                # st.info(f"DEBUG - In list 2 fiber check: value={fiber_value}, food_state={food_state}, is_in_list_2={is_in_list_2}")
                if fiber_value is not None:
                    # For liquid foods in list 2, adjust the validation based on their specific thresholds
                    if food_state_value == "liquid":
                        # st.info(f"DEBUG - Processing liquid in list 2 fiber claim: {claim_text}")
                        if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                            # For "high" claim in liquids - should be >= 3g
                            original_result = adjusted_result
                            adjusted_result = fiber_value >= 3.0
                            # st.info(f"DEBUG - Liquid in list 2 fiber high check: {fiber_value} >= 3.0 = {adjusted_result} (was {original_result})")
                        elif "แหล่งของ" in claim_text or ("source" in claim_text.lower() and "excellent source" not in claim_text.lower()):
                            # For "source of" claim in liquids - should be >= 1.5g
                            original_result = adjusted_result
                            adjusted_result = fiber_value >= 1.5
                            # st.info(f"DEBUG - Liquid in list 2 fiber source check: {fiber_value} >= 1.5 = {adjusted_result} (was {original_result})")
            
            # ถ้ามี threshold_rdi ให้ตรวจสอบด้วย
            rdi_result = True  # ค่าเริ่มต้นเป็น True
            if threshold_rdi and threshold_rdi.strip() and threshold_rdi != "nan":
                # แปลง threshold_rdi เพื่อให้มีรูปแบบถูกต้องสำหรับการประเมิน
                rdi_eval_str = format_rdi_threshold(threshold_rdi)
                
                # ตรวจสอบว่ามี rdi_key หรือไม่
                rdi_key = f"{nutrient_key}_rdi_percent"
                if rdi_key in adjusted_values:
                    rdi_result = evaluate_threshold(rdi_eval_str, adjusted_values, nutrient_key, None)
                else:
                    # ไม่มีค่า RDI ให้ใช้ค่า default เป็น False
                    rdi_result = False
            
            # ตรวจสอบค่า %RDI ต่อ 100kcal ด้วย (สำหรับวิตามินและแร่ธาตุ)
            threshold_rdi_100kcal = str(row.get("threshold_rdi_100kcal", "nan"))
            per_100kcal_rdi_result = False
            
            if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and threshold_rdi_100kcal != "nan" and is_vitamin_or_mineral(nutrient_key):
                # มีการกำหนด threshold_rdi_100kcal และเป็นวิตามินหรือแร่ธาตุ
                # ตรวจสอบ %RDI ต่อ 100kcal
                per_100kcal_rdi_key = f"{nutrient_key}_rdi_percent_per_100kcal"
                
                # สร้าง values_dict ชั่วคราวที่เก็บค่า per_100kcal_rdi_key ในชื่อ nutrient_key_rdi_percent
                # เพื่อให้ evaluate_threshold ทำงานได้โดยไม่ต้องแก้ไขฟังก์ชัน
                temp_values = {f"{nutrient_key}_rdi_percent": adjusted_values.get(per_100kcal_rdi_key)}
                
                # ประเมินเงื่อนไข %RDI ต่อ 100kcal
                per_100kcal_rdi_result = evaluate_threshold(threshold_rdi_100kcal, temp_values, nutrient_key, None)
                
                # อาหารนั้นผ่านเงื่อนไขหากผ่านเงื่อนไขใดเงื่อนไขหนึ่ง (OR)
                rdi_result = rdi_result or per_100kcal_rdi_result
            
            # รวมผลการประเมินทั้งสองส่วน
            adjusted_result = adjusted_result and rdi_result
            
            # ตรวจสอบเงื่อนไขพลังงานจากไขมันอิ่มตัว (ถ้ามี)
            if is_saturated_fat_energy_condition:
                saturated_fat_value = adjusted_values.get("saturated_fat")
                if saturated_fat_value is not None and adjusted_result:
                    # ตรวจสอบว่าพลังงานจากไขมันอิ่มตัวต้องไม่เกิน 10% ของพลังงานทั้งหมด
                    saturated_fat_energy_percent = adjusted_values.get("saturated_fat_energy_percent")
                    if saturated_fat_energy_percent is not None and saturated_fat_energy_percent > 10:
                        adjusted_result = False
                        if not warning_shown:  # แสดงข้อความเตือนเฉพาะเมื่อยังไม่เคยแสดง
                            st.warning(f"⚠️ แม้ว่าปริมาณไขมันอิ่มตัวจะอยู่ในเกณฑ์ต่ำ แต่พลังงานที่มาจากไขมันอิ่มตัว ({saturated_fat_energy_percent:.1f}%) เกิน 10% ของพลังงานทั้งหมด")
                            warning_shown = True  # บันทึกว่ามีการแสดงข้อความเตือนแล้ว")
            
            # ตรวจสอบเพิ่มเติมกับค่าที่ไม่ปรับแก้ (label_values) เฉพาะกรณีไม่อยู่ในบัญชีหมายเลข 2
            label_result = False
            if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and label_values:
                try:
                    # สร้าง dictionary สำหรับเปรียบเทียบจากค่าในฉลาก
                    label_comparison = label_values.copy()
                   
                    # Calculate and add %RDI to label_comparison directly from its own values for relevant nutrients.
                    # This ensures that claim evaluation for 'label_result' uses %RDI derived from per-label-serving amounts.
                    # Iterate over keys actually present in label_comparison (which are per-serving amounts)
                    for lc_key in list(label_comparison.keys()): 
                        # Check if the nutrient is one for which RDI claims are typically made (e.g., protein, fiber, vitamins, minerals)
                        # The original code explicitly checked protein and fiber. We can extend or refine this set.
                        if lc_key in ["protein", "fiber"] or is_vitamin_or_mineral(lc_key):
                            rdi_value_for_lc_key = get_rdi_value(lc_key, thai_rdis)
                            amount_in_label = label_comparison.get(lc_key)

                            if rdi_value_for_lc_key is not None and amount_in_label is not None and rdi_value_for_lc_key > 0:
                                percent_rdi_for_label = (amount_in_label / rdi_value_for_lc_key) * 100
                                label_comparison[f"{lc_key}_rdi_percent"] = percent_rdi_for_label
                            # If RDI value isn't found, or amount is None, or RDI is 0, then _rdi_percent is not added.
                    
                    # ตรวจสอบว่าผ่านเงื่อนไขจากค่าในฉลากหรือไม่
                    if threshold_str == "nan":
                        label_threshold_result = True
                    else:
                        label_threshold_result = evaluate_threshold(threshold_str, label_comparison, nutrient_key, None)
                    
                    # ตรวจสอบ threshold_rdi สำหรับค่าในฉลาก
                    label_rdi_result = True
                    if threshold_rdi and threshold_rdi.strip() and threshold_rdi != "nan":
                        # แปลง threshold_rdi เพื่อให้มีรูปแบบถูกต้องสำหรับการประเมิน
                        label_rdi_eval_str = format_rdi_threshold(threshold_rdi)
                        
                        # ตรวจสอบว่ามี rdi_key หรือไม่
                        rdi_key = f"{nutrient_key}_rdi_percent"
                        if rdi_key in label_comparison:
                            label_rdi_result = evaluate_threshold(label_rdi_eval_str, label_comparison, nutrient_key, None)
                        else:
                            # ไม่มีค่า RDI ให้ใช้ค่า default เป็น False
                            label_rdi_result = False
                    
                    # รวมผลการประเมินทั้งสองส่วน
                    label_result = label_threshold_result and label_rdi_result
                    
                    # ตรวจสอบเงื่อนไขพลังงานจากไขมันอิ่มตัว (ถ้ามี)
                    if is_saturated_fat_energy_condition:
                        label_saturated_fat_value = label_values.get("saturated_fat")
                        if label_saturated_fat_value is not None and label_result:
                            # ตรวจสอบว่าพลังงานจากไขมันอิ่มตัวต้องไม่เกิน 10% ของพลังงานทั้งหมด
                            label_saturated_fat_energy_percent = label_values.get("saturated_fat_energy_percent")
                            if label_saturated_fat_energy_percent is not None and label_saturated_fat_energy_percent > 10:
                                label_result = False
                                # ไม่ต้องแสดงข้อความเตือนซ้ำ เพราะจะใช้ตัวแปร warning_shown ที่ตรวจสอบแล้ว
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประเมินค่าจากฉลาก: {str(e)}")
                
            # ต้องตรวจสอบว่าทั้ง adjusted และ label value ต้องผ่านเงื่อนไข (เฉพาะกรณีอยู่ในบัญชีหมายเลข 2)
            if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and label_values:
                # สำหรับทุกสารอาหารในบัญชีหมายเลข 2 ใช้เงื่อนไขเดียวกัน
                # ต้องผ่านทั้งเงื่อนไขจากค่าบนฉลากและค่าจากหน่วยบริโภคอ้างอิง
                result = adjusted_result and label_result
            else:
                # กรณีไม่มี label_values (e.g. error during its creation for List 2 item)
                # หรือไม่อยู่ในบัญชีหมายเลข 2 ให้ใช้แค่ adjusted_result
                result = adjusted_result
            
            # กรณีพิเศษสำหรับคำกล่าวอ้าง "ปราศจากน้ำตาล" (sugar-free) เมื่อใช้ผลวิเคราะห์โภชนาการต่อ 100g/ml
            if nutrient_key == "sugar" and "ปราศจาก" in claim_text and nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)":
                sugar_on_label_rounded = label_values.get('sugar')
                sugar_on_reference_rounded = adjusted_values.get('sugar')
                
                # ต้องปัดเลขเป็น 0 ทั้งสองกรณีจึงจะกล่าวอ้างได้
                if not (sugar_on_label_rounded == 0 and sugar_on_reference_rounded == 0):
                    result = False

            # ตรวจสอบเงื่อนไขเพิ่มเติม (special rule)
            if result and special_rule and not pd.isna(special_rule) and str(special_rule).strip():
                if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                    ref_value = float(group_info["serving_value"])
                    ref_unit = group_info["unit"].lower()
                    
                    if ref_unit in ["กรัม", "g", "ml", "มิลลิลิตร"] and ref_value <= 30:
                        # กรณีหน่วยบริโภคอ้างอิง ≤ 30 กรัม ตรวจสอบทั้งจากค่าดิบและค่าปรับ
                        special_rule_result = evaluate_special_rule(special_rule, nutrient_values, None) or evaluate_special_rule(special_rule, adjusted_values, label_values)
                    else:
                        # กรณีอื่นๆ ใช้ทั้ง adjusted_values และ label_values
                        special_rule_result = evaluate_special_rule(special_rule, adjusted_values, label_values)
                else:
                    # กรณีไม่อยู่ในบัญชีหมายเลข 2 ใช้เฉพาะ adjusted_values
                    special_rule_result = evaluate_special_rule(special_rule, adjusted_values, None)
                
                result = result and special_rule_result
            
            results_found = True
            
            if result:
                # กำหนดค่าเริ่มต้นให้ display_threshold ก่อน
                display_threshold = threshold_str 
                
                # สำหรับกรณีใยอาหารในอาหารของเหลวที่ไม่อยู่ในบัญชีหมายเลข 2
                threshold_100kcal = str(row.get("threshold_100kcal", "nan"))
                
                
                if threshold_str == "nan" and threshold_100kcal != "nan" and nutrient_key == "fiber" and selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and food_state_value == "liquid":
                    # ใช้ threshold_100kcal แทน threshold_str ที่เป็น nan และแสดงให้ชัดเจนว่าเป็นหน่วยต่อ 100kcal
                    fiber_per_100kcal = adjusted_values.get("fiber_per_100kcal", 0)
                    if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                        # For "high" claim: must be >= 3g per 100kcal
                        if fiber_per_100kcal < 3.0:
                            result = False
                            display_threshold = f"(ต้อง ≥ 3.0g ต่อ 100kcal แต่มี {fiber_per_100kcal:.2f}g)"
                        else:
                            display_threshold = "fiber>=3.0g"
                    elif "แหล่งของ" in claim_text or ("source" in claim_text.lower() and "excellent source" not in claim_text.lower()):
                        # For "source of" claim: must be >= 1.5g per 100kcal
                        if fiber_per_100kcal < 1.5:
                            result = False
                        else:
                            display_threshold = "fiber>=1.5g"
                else:
                    display_threshold = threshold_str
                
                claim_text_to_show = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' ({display_threshold})"
                
                # เพิ่มตัวแปรเพื่อเก็บรายละเอียดว่าผ่านเงื่อนไขใด
                condition_detail = ""
                
                # ตรวจสอบเงื่อนไข per 100g/ml
                per_100g_result = evaluate_threshold(threshold_str, adjusted_values, nutrient_key, None)
                
                # ตรวจสอบเงื่อนไข per 100kcal สำหรับโปรตีนและใยอาหาร
                per_100kcal_result = False
                if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and threshold_100kcal != "nan" and nutrient_key in ["protein", "fiber"]:
                    per_100kcal_key = f"{nutrient_key}_per_100kcal"
                    if adjusted_values.get(per_100kcal_key) is not None:
                        temp_values = {nutrient_key: adjusted_values.get(per_100kcal_key)}
                        per_100kcal_result = evaluate_threshold(threshold_100kcal, temp_values, nutrient_key, None)
                        
                        # กรณีพิเศษสำหรับใยอาหารในอาหารของเหลว (liquid)
                        # เช็คซ้ำว่าผ่านเงื่อนไขจริง ๆ หรือไม่ 
                        if nutrient_key == "fiber" and food_state_value == "liquid" and selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                            fiber_per_100kcal = adjusted_values.get("fiber_per_100kcal")
                            
                            # First check if it's a HIGH claim (because high claims may contain "source" in "excellent source of")
                            if "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                                # For HIGH claims, only override if fiber_per_100kcal >= 3.0
                                if fiber_per_100kcal is not None:
                                    if fiber_per_100kcal >= 3.0:
                                        # Override the message for high claims that meet the threshold
                                        message = message.replace("❌", "✅")
                                        message = message.replace("ไม่เข้าเงื่อนไข", "สามารถใช้คำกล่าวอ้าง")
                                        message = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' (fiber>=3.0g) [ผ่านเงื่อนไขต่อ 100kcal]"
                                    else:
                                        # คงสถานะ ❌ และเพิ่มข้อความเหตุผล
                                        message += f" (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 3.0g ต่อ 100kcal)"
                            
                            # Then check if it's a SOURCE claim (but not a HIGH claim)
                            elif "แหล่งของ" in claim_text or (("source" in claim_text.lower()) and not any(term in claim_text.lower() for term in ["high", "rich", "excellent"])):
                                # For SOURCE claims, override if fiber_per_100kcal >= 1.5
                                if fiber_per_100kcal is not None:
                                    if fiber_per_100kcal >= 1.5:
                                        # Override the message for source claims that meet the threshold
                                        message = message.replace("❌", "✅")
                                        message = message.replace("ไม่เข้าเงื่อนไข", "สามารถใช้คำกล่าวอ้าง")
                                        message = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' (fiber>=1.5g) [ผ่านเงื่อนไขต่อ 100kcal]"
                                    else:
                                        # คงสถานะ ❌ และเพิ่มข้อความเหตุผล
                                        message += f" (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 1.5g ต่อ 100kcal)"
                    
                # แสดง threshold_rdi ด้วยหากมี
                if threshold_rdi:
                    claim_text_to_show = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' "
                    if display_threshold != "nan":
                        claim_text_to_show += f"({display_threshold}"
                        if threshold_rdi:
                            claim_text_to_show += f", {threshold_rdi}"
                        claim_text_to_show += ")"
                    else:
                        claim_text_to_show += f"({threshold_rdi})"
                
                # ระบุว่าผ่านการประเมินจากเงื่อนไขใด (per 100g/ml หรือ per 100kcal)
                if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                    # สำหรับโปรตีนและใยอาหาร
                    if threshold_100kcal != "nan" and nutrient_key in ["protein", "fiber"]:
                        if per_100g_result and per_100kcal_result:
                            condition_detail = " [ผ่านทั้งเงื่อนไขต่อ 100g/ml และต่อ 100kcal]"
                        elif per_100g_result:
                            condition_detail = " [ผ่านเงื่อนไขต่อ 100g/ml]"
                        elif per_100kcal_result:
                            # แสดงค่า threshold_100kcal แทนที่ threshold_str เมื่อผ่านเงื่อนไขต่อ 100kcal เท่านั้น
                            claim_text_to_show = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' ({threshold_100kcal})"
                            condition_detail = " [ผ่านเงื่อนไขต่อ 100kcal]"
                    
                    # สำหรับวิตามินและแร่ธาตุ
                    elif row.get("threshold_rdi_100kcal", "nan") != "nan" and is_vitamin_or_mineral(nutrient_key):
                        rdi_per_100g = evaluate_threshold(threshold_rdi, adjusted_values, nutrient_key, None) if threshold_rdi and threshold_rdi != "nan" else False
                        
                        if rdi_per_100g and per_100kcal_rdi_result:
                            condition_detail = " [ผ่านทั้งเงื่อนไขต่อ 100g/ml และต่อ 100kcal]"
                        elif rdi_per_100g:
                            condition_detail = " [ผ่านเงื่อนไขต่อ 100g/ml]"
                        elif per_100kcal_rdi_result:
                            # แสดงค่า threshold_rdi_100kcal แทนที่ threshold_rdi เมื่อผ่านเงื่อนไขต่อ 100kcal เท่านั้น
                            threshold_display = threshold_rdi_100kcal
                            if "RDI" not in threshold_display:
                                threshold_display += "% RDI"
                            claim_text_to_show = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' ({threshold_display})"
                            condition_detail = " [ผ่านเงื่อนไขต่อ 100kcal]"
                
                # ระบุว่าผ่านการประเมินจากค่าในฉลากหรือหน่วยบริโภคอ้างอิง
                if not adjusted_result and label_result:
                    condition_detail = " [ตามค่าจากฉลาก]"
                
                # เพิ่มรายละเอียดว่าผ่านเงื่อนไขใด
                claim_text_to_show += condition_detail
                
                # แสดงเงื่อนไขเพิ่มเติม (ถ้ามี)
                if special_rule and not pd.isna(special_rule) and str(special_rule).strip():
                    # ตรวจสอบและแปลงเงื่อนไขเพิ่มเติมเป็นภาษาไทย
                    if ("คอเลสเตอรอล" in nutrient or "cholesterol" in nutrient.lower()) and "saturated_fat" in special_rule:
                        # ตรวจสอบว่าอยู่ในบัญชีหมายเลข 2 หรือไม่
                        if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                            # อยู่ในบัญชีหมายเลข 2 ใช้ค่า 2
                            claim_text_to_show += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=2"
                        else:
                            # ไม่อยู่ในบัญชีหมายเลข 2 ตรวจสอบว่าเป็นอาหารของแข็งหรือของเหลว
                            if food_state_value == "solid":
                                claim_text_to_show += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=1.5"
                            else:
                                claim_text_to_show += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=0.75"
                    elif ("ไขมันอิ่มตัว" in nutrient or "saturated fat" in nutrient.lower()) and "trans_fat" in special_rule:
                        # แสดงเฉพาะกรณี "ปราศจาก" และอยู่ในบัญชีหมายเลข 2 เท่านั้น
                        if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and "ปราศจาก" in claim_text:
                            claim_text_to_show += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันทรานส์<0.5"
                    else:
                        claim_text_to_show += f"\n   📌 เงื่อนไขเพิ่มเติม: {special_rule}"
                    
                # กรณีพิเศษสำหรับใยอาหาร - ต้องตรวจสอบซ้ำก่อนแสดงผล
                if nutrient_key == "fiber" and food_state_value == "liquid" and selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                    fiber_per_100kcal = adjusted_values.get("fiber_per_100kcal", 0)
                    if "แหล่งของ" in claim_text or ("source" in claim_text.lower() and "excellent source" not in claim_text.lower()):
                        # ตรวจสอบที่แท้จริงสำหรับ source claim: ต้องมีค่า >= 1.5g ต่อ 100kcal
                        if fiber_per_100kcal < 1.5:
                            # ไม่ควรแสดงเป็น success message แต่ต้องแสดงเป็น info message
                            st.info(f"❌ {nutrient}: ไม่เข้าเงื่อนไข '{claim_text}' (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 1.5g ต่อ 100kcal)")
                            continue  # ข้ามการแสดง success message
                    elif "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                        # ตรวจสอบที่แท้จริงสำหรับ high claim: ต้องมีค่า >= 3.0g ต่อ 100kcal
                        if fiber_per_100kcal < 3.0:
                            # ไม่ควรแสดงเป็น success message แต่ต้องแสดงเป็น info message
                            st.info(f"❌ {nutrient}: ไม่เข้าเงื่อนไข '{claim_text}' (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 3.0g ต่อ 100kcal)")
                            continue  # ข้ามการแสดง success message

                st.success(claim_text_to_show)
                st.session_state.current_evaluation_messages_for_report.append({"text": claim_text_to_show, "is_success": True, "conditions_text": None})

                # --- Fat warning for List 2 fiber claims ---
                if (
                    nutrient_key == "fiber"
                    and selected_label != "ไม่อยู่ในบัญชีหมายเลข 2"
                    and adjusted_values.get("fiber_rdi_percent", 0) >= 10
                ):
                    fat_ref = adjusted_values.get("fat")
                    fat_label = label_values.get("fat") if label_values else None
                    fat_ref_in_range = fat_ref is not None and 3 < fat_ref <= 13
                    fat_label_in_range = fat_label is not None and 3 < fat_label <= 13
                    if fat_ref_in_range or fat_label_in_range:
                        warning_text = "⚠️ ต้องกำกับด้วยปริมาณไขมันทั้งหมดต่อปริมาณที่กินต่อครั้งที่แสดงบนฉลากด้วยอักษรที่มีขนาดไม่เล็กกว่าครึ่งหนึ่งของข้อความกล่าวอ้าง"
                        st.warning(warning_text)
                        st.session_state.current_evaluation_messages_for_report.append({
                            "text": warning_text,
                            "is_success": False,
                            "conditions_text": None
                        })

                # แสดงเงื่อนไขการกล่าวอ้าง (ถ้ามี)
                # แสดงเงื่อนไขการกล่าวอ้าง (ถ้ามี)
                if pd.notna(condition_id) and not condition_lookup.empty:
                    try:
                        condition_ids_str = str(condition_id).split(',')
                        condition_ids = [c.strip() for c in condition_ids_str if c.strip().isdigit()]
                        
                        if len(condition_ids) > 1:
                            st.markdown("**เงื่อนไขการกล่าวอ้าง:**")
                            
                        conditions_found_for_ui = False
                        all_conditions_for_report = []

                        for cid_str in condition_ids:
                            match_note = condition_lookup[condition_lookup["condition"] == cid_str]
                            if match_note.empty: # Try regex for exact match if direct failed (e.g. "1.0" vs "1")
                                match_note = condition_lookup[condition_lookup["condition"].astype(str).str.fullmatch(cid_str)]

                            if not match_note.empty:
                                conditions_found_for_ui = True
                                condition_description = match_note.iloc[0]['description']
                                all_conditions_for_report.append(f"• {condition_description}" if len(condition_ids) > 1 else condition_description)
                                if len(condition_ids) > 1:
                                    st.markdown(f"• {condition_description}")
                                else:
                                    st.markdown(f"**เงื่อนไขการกล่าวอ้าง:** {condition_description}")
                        
                        if all_conditions_for_report and st.session_state.current_evaluation_messages_for_report and \
                           isinstance(st.session_state.current_evaluation_messages_for_report[-1], dict):
                            prefix = "เงื่อนไขการกล่าวอ้าง:\n" if len(all_conditions_for_report) > 1 and any("•" in cond for cond in all_conditions_for_report) else "เงื่อนไขการกล่าวอ้าง: "
                            st.session_state.current_evaluation_messages_for_report[-1]["conditions_text"] = prefix + "\n".join(all_conditions_for_report)
                        
                        if not conditions_found_for_ui and condition_ids:
                            st.warning(f"ไม่พบข้อมูลเงื่อนไขสำหรับ ID: {', '.join(condition_ids)}")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการแสดงเงื่อนไข: {e}")
            else:
                # แสดงข้อความไม่ผ่านเงื่อนไข พร้อมแสดง threshold_rdi ถ้ามี
                message = f"❌ {nutrient}: ไม่เข้าเงื่อนไข '{claim_text}' "
                
                # เพิ่มการแสดงค่า threshold ในข้อความแสดงผลเมื่อไม่ผ่านเงื่อนไข
                if threshold_str and threshold_str != "nan":
                    message = f"❌ {nutrient}: ไม่เข้าเงื่อนไข '{claim_text}' ({threshold_str}) "
                
                # เพิ่มเงื่อนไขพิเศษเสมอสำหรับคอเลสเตอรอล ทั้งกรณีผ่านและไม่ผ่านเกณฑ์
                if ("คอเลสเตอรอล" in nutrient or "cholesterol" in str(nutrient).lower()):
                    # ตรวจสอบว่าอยู่ในบัญชีหมายเลข 2 หรือไม่
                    if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                        # อยู่ในบัญชีหมายเลข 2 ใช้ค่า 2
                        message += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=2"
                    else:
                        # ไม่อยู่ในบัญชีหมายเลข 2 ตรวจสอบว่าเป็นอาหารของแข็งหรือของเหลว
                        if food_state_value == "solid":
                            message += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=1.5"
                        else:
                            message += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันอิ่มตัว<=0.75"
                
                # เพิ่มเงื่อนไขเพิ่มเติมสำหรับไขมันอิ่มตัวกรณีไม่ผ่านเงื่อนไข
                if ("ไขมันอิ่มตัว" in nutrient or "saturated fat" in str(nutrient).lower()) and "ปราศจาก" in claim_text and selected_label != "ไม่อยู่ในบัญชีหมายเลข 2":
                    message += f"\n   📌 เงื่อนไขเพิ่มเติม: ไขมันทรานส์<0.5"
                
                # กรณีพิเศษสำหรับ fiber ในอาหารของเหลวที่ไม่อยู่ในบัญชีหมายเลข 2
                special_threshold_display = None
                if nutrient_key == "fiber" and food_state_value == "liquid" and selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                    fiber_per_100kcal = adjusted_values.get("fiber_per_100kcal")
                    # Debug removed
                    
                    # ตรวจสอบเงื่อนไขตามประเภทคำกล่าวอ้าง
                    if "แหล่งของ" in claim_text or (("source" in claim_text.lower()) and not any(term in claim_text.lower() for term in ["high", "rich", "excellent"])):
                        # คำกล่าวอ้าง "แหล่งของ" ต้องมีค่า >= 1.5g ต่อ 100kcal
                        if fiber_per_100kcal is not None:
                            passed = fiber_per_100kcal >= 1.5
                            
                            if passed:
                                message = message.replace("❌", "✅")
                                message = message.replace("ไม่เข้าเงื่อนไข", "สามารถใช้คำกล่าวอ้าง")
                                message = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' (fiber>=1.5g) [ผ่านเงื่อนไขต่อ 100kcal]"
                            else:
                                # ถ้าไม่ผ่านเงื่อนไข ตรวจสอบว่าขณะนี้แสดงผลว่าผ่านหรือไม่
                                if "✅" in message:
                                    # หากขณะนี้แสดงว่าผ่าน แต่ไม่ผ่านจริง ให้แก้ไขเป็นไม่ผ่าน
                                    message = message.replace("✅", "❌")
                                    message = message.replace("สามารถใช้คำกล่าวอ้าง", "ไม่เข้าเงื่อนไข")
                                message += f" (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 1.5g ต่อ 100kcal)"
                    elif "สูง" in claim_text or "high" in claim_text.lower() or "rich" in claim_text.lower():
                        # คำกล่าวอ้าง "สูง" ต้องมีค่า >= 3.0g ต่อ 100kcal
                        if fiber_per_100kcal is not None:
                            passed = fiber_per_100kcal >= 3.0
                            
                            if passed:
                                message = message.replace("❌", "✅")
                                message = message.replace("ไม่เข้าเงื่อนไข", "สามารถใช้คำกล่าวอ้าง")
                                message = f"✅ {nutrient}: สามารถใช้คำกล่าวอ้าง: '{claim_text}' (fiber>=3.0g) [ผ่านเงื่อนไขต่อ 100kcal]"
                            else:
                                # คงสถานะ ❌ และเพิ่มข้อความเหตุผล
                                message += f" (ค่าใยอาหารต่อ 100kcal = {fiber_per_100kcal:.2f}g แต่ต้องมีค่า ≥ 3.0g ต่อ 100kcal)"

                # For failed conditions use st.info() instead of st.success()
                if "✅" in message:
                    st.success(message)
                    st.session_state.current_evaluation_messages_for_report.append({"text": message, "is_success": True, "conditions_text": None})
                else:
                    st.info(message)
                    st.session_state.current_evaluation_messages_for_report.append({"text": message, "is_success": False, "conditions_text": None})
                
                # เพิ่มการแสดงเงื่อนไขการกล่าวอ้างหากผ่านเงื่อนไข fiber และมี condition_id
                if "✅" in message and nutrient_key == "fiber" and pd.notna(condition_id) and not condition_lookup.empty:
                    try:
                        condition_ids_str = str(condition_id).split(',')
                        condition_ids = [c.strip() for c in condition_ids_str if c.strip().isdigit()]
                        
                        if len(condition_ids) > 1:
                            st.markdown("**เงื่อนไขการกล่าวอ้าง:**")
                        
                        conditions_found_for_ui_fiber = False
                        all_conditions_for_report_fiber = []

                        for cid_str in condition_ids:
                            match_note = condition_lookup[condition_lookup["condition"] == cid_str]
                            if match_note.empty:
                                match_note = condition_lookup[condition_lookup["condition"].astype(str).str.fullmatch(cid_str)]
                            
                            if not match_note.empty:
                                conditions_found_for_ui_fiber = True
                                condition_description = match_note.iloc[0]['description']
                                all_conditions_for_report_fiber.append(f"• {condition_description}" if len(condition_ids) > 1 else condition_description)
                                if len(condition_ids) > 1:
                                    st.markdown(f"• {condition_description}")
                                else:
                                    st.markdown(f"**เงื่อนไขการกล่าวอ้าง:** {condition_description}")
                        
                        if all_conditions_for_report_fiber and st.session_state.current_evaluation_messages_for_report and \
                           isinstance(st.session_state.current_evaluation_messages_for_report[-1], dict):
                            prefix = "เงื่อนไขการกล่าวอ้าง:\n" if len(all_conditions_for_report_fiber) > 1 and any("•" in cond for cond in all_conditions_for_report_fiber) else "เงื่อนไขการกล่าวอ้าง: "
                            st.session_state.current_evaluation_messages_for_report[-1]["conditions_text"] = prefix + "\n".join(all_conditions_for_report_fiber)

                        if not conditions_found_for_ui_fiber and condition_ids:
                            st.warning(f"ไม่พบข้อมูลเงื่อนไขสำหรับ ID (fiber): {', '.join(condition_ids)}")
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการแสดงเงื่อนไข (fiber): {e}")
        
        # ตรวจสอบวิตามินและแร่ธาตุก่อนตรวจสอบ results_found
        # Track which vitamin/mineral claims we've already processed
        processed_vm_claims = set()
        
        # เรียกใช้ฟังก์ชัน check_vitamin_mineral_claims โดยส่งค่า selected_label และ label_values เพิ่มเติม
        # เพื่อใช้ในการตรวจสอบทั้งค่าจากหน่วยบริโภคบนฉลากและหน่วยบริโภคอ้างอิงสำหรับอาหารในบัญชีหมายเลข 2
        vitamin_mineral_results = []
        vm_results = check_vitamin_mineral_claims(nutrient_values, adjusted_values, claims, thai_rdis, selected_label, label_values)
        
        # Filter out duplicate vitamin/mineral results
        if vm_results:
            for result in vm_results:
                vm_key = f"{result['nutrient']}_{result['claim_type']}"
                if vm_key not in processed_vm_claims:
                    vitamin_mineral_results.append(result)
                    processed_vm_claims.add(vm_key)
                else:
                    vm_duplicate_count += 1
        
        # ถ้ามีผลลัพธ์จากวิตามินและแร่ธาตุ ให้กำหนด results_found เป็น True ด้วย
        if vitamin_mineral_results:
            results_found = True
            
        # Comment out the debug message
        # แสดงข้อมูลการกรองรายการซ้ำซ้อน เฉพาะกรณีไม่อยู่ในบัญชีหมายเลข 2
        # if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" and (duplicate_count > 0 or vm_duplicate_count > 0):
        #     st.caption(f"ระบบกรองรายการประเมินซ้ำซ้อนออกแล้ว {duplicate_count + vm_duplicate_count} รายการ")
        
        if not results_found:
            st.warning("ไม่พบผลการตรวจสอบใดๆ โปรดตรวจสอบข้อมูลที่ป้อนและลองอีกครั้ง")
        else:
            # แสดงข้อความกล่าวอ้างเกี่ยวกับน้ำตาล (ถ้ามี)
            if table_type == "table1" and has_added_sugar == "ไม่มีการเติมน้ำตาล":
                st.success(sugar_claim_message)
                st.session_state.current_evaluation_messages_for_report.append({"text": sugar_claim_message, "is_success": True, "conditions_text": None})
                if energy_warning:
                    st.warning(energy_warning)
                    st.session_state.current_evaluation_messages_for_report.append({"text": energy_warning, "is_success": False, "conditions_text": "Warning"}) # Mark as warning
            
            # แสดงผลการตรวจสอบวิตามินและแร่ธาตุ
            if vitamin_mineral_results:
                st.warning("เงื่อนไขการกล่าวอ้างกลุ่มวิตามินและแร่ธาตุ: ต้องปฏิบัติตามเงื่อนไขข้อ 2.2 ของบัญชีนี้ด้วย")
                vm_general_condition = "เงื่อนไขการกล่าวอ้างกลุ่มวิตามินและแร่ธาตุ: ต้องปฏิบัติตามเงื่อนไขข้อ 2.2 ของบัญชีนี้ด้วย"
                
                for result in vitamin_mineral_results:
                    if result["pass"]:
                        claim_text_to_show = f"✅ {result['nutrient']}: สามารถใช้คำกล่าวอ้าง: '{result['claim_type']}' ({result['threshold']}) "
                        st.success(claim_text_to_show)
                        st.session_state.current_evaluation_messages_for_report.append({
                            "text": claim_text_to_show, 
                            "is_success": True, 
                            "conditions_text": vm_general_condition # Ensure this is correctly assigned
                        })
                    else:
                        claim_text_to_show = f"❌ {result['nutrient']}: ไม่เข้าเงื่อนไข '{result['claim_type']}' ({result['threshold']}) "
                        st.info(claim_text_to_show)
                        st.session_state.current_evaluation_messages_for_report.append({
                            "text": claim_text_to_show, 
                            "is_success": False, 
                            "conditions_text": None 
                        })
            
            # แสดงข้อความเตือน หลังจากแสดงผลการตรวจสอบทั้งหมด
            st.warning("📢 **ข้อความกล่าวอ้างทั้งหมด อย่างน้อยต้องมีภาษาไทย**", icon="⚠️")

            # แสดง disclaimers ท้ายสุด
            if final_disclaimer_results:
                st.markdown("### ⚠️ ข้อความที่ต้องแสดงเพิ่มเติม (Disclaimers) ตามเงื่อนไขข้อ 2.2")
                
                # ตรวจสอบประเภทอาหารเพื่อแสดงคอลัมน์ให้เหมาะสม
                if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
                    # กรณีอาหารไม่อยู่ในบัญชีหมายเลข 2 แสดงค่าจากหน่วยบริโภคอ้างอิงเท่านั้น
                    cols = st.columns([2, 1.5, 1, 1.5])
                    cols[0].markdown("**สารอาหาร**")
                    cols[1].markdown("**ค่าจากหน่วยบริโภคอ้างอิง (100g/100ml)**")
                    cols[2].markdown("**ค่าที่กำหนด**")
                    cols[3].markdown("**หน่วย**")
                    
                    # แสดงข้อมูลในรูปแบบตาราง
                    for disclaimer in final_disclaimer_results:
                        cols = st.columns([2, 1.5, 1, 1.5])
                        cols[0].write(disclaimer['nutrient'])
                        cols[1].write(f"{disclaimer['reference_value']:.1f}")
                        cols[2].write(f"{disclaimer['threshold']:.1f}")
                        cols[3].write(disclaimer['unit'])
                        
                        # แสดงข้อความ disclaimer
                        st.warning(disclaimer['message'])
                else:
                    # กรณีอาหารอยู่ในบัญชีหมายเลข 2 แสดงค่าจากทั้งสองแหล่ง
                    cols = st.columns([2, 1, 1, 1, 1.5])
                    cols[0].markdown("**สารอาหาร**")
                    cols[1].markdown("**ค่าบนฉลาก**")
                    cols[2].markdown("**ค่าจากหน่วยบริโภคอ้างอิง**")
                    cols[3].markdown("**ค่าที่กำหนด**")
                    cols[4].markdown("**หน่วย**")
                    
                    # แสดงข้อมูลในรูปแบบตาราง
                    for disclaimer in final_disclaimer_results:
                        cols = st.columns([2, 1, 1, 1, 1.5])
                        cols[0].write(disclaimer['nutrient'])
                        cols[1].write(f"{disclaimer['label_value']:.1f}")
                        cols[2].write(f"{disclaimer['reference_value']:.1f}")
                        cols[3].write(f"{disclaimer['threshold']:.1f}")
                        cols[4].write(disclaimer['unit'])
                        
                        # แสดงข้อความ disclaimer
                        st.warning(disclaimer['message'])

            # --- Prepare data for report generation ---
            report_data = {
                "selected_label": selected_label,
                "food_state_value": food_state_value if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2" else (group_info['state'] if group_info is not None and isinstance(group_info, pd.Series) and 'state' in group_info else food_state_value),
                "nutrition_check_method": nutrition_check_method,
                "actual_serving_size": actual_serving_size,
                "ref_serving_size": ref_serving_size_value,
                "prep_option": locals().get("prep_option", None),
                "has_added_sugar": has_added_sugar if table_type == "table1" else None,
                "nutrient_inputs": nutrient_values, # Original user inputs
                "RDI_MAPPING_ วิตามิน": RDI_MAPPING, # Pass the mapping
                "VITAMIN_MINERAL_UNITS": { # Pass units for the report
                    **{info['key']: info['unit'] for group in VITAMIN_MINERAL_GROUPS.values() for info in group.values()},
                    "energy": "kcal", "protein": "g", "fat": "g", "saturated_fat": "g",
                    "trans_fat": "g", "cholesterol": "mg", "sugar": "g", "fiber": "g",
                    "sodium": "mg", "potassium": "mg"
                },
                "table_type": table_type,
                "is_in_list_2": selected_label != "ไม่อยู่ในบัญชีหมายเลข 2",
                "group_info_for_report": group_info.to_dict() if group_info is not None and isinstance(group_info, pd.Series) else None,
                
                # Calculations
                "adjusted_nutrient_values": adjusted_values,
                "label_nutrient_values_for_report": label_values, 
                "per_100kcal_values": adjusted_values.get("per_100kcal_values", {}), # Ensure this key exists if used
                "saturated_fat_energy_percent": adjusted_values.get("saturated_fat_energy_percent"),
                "label_saturated_fat_energy_percent": label_values.get("saturated_fat_energy_percent"),
                "rounded_values_display_df": df_display if 'df_display' in locals() and isinstance(df_display, pd.DataFrame) else pd.DataFrame(),
                "rdi_display_df": rdi_df if 'rdi_df' in locals() and isinstance(rdi_df, pd.DataFrame) else pd.DataFrame(),
                
                # Evaluation - This needs to be built by capturing st.success/st.info messages
                "evaluation_messages": [], # Will be populated below
                "disclaimer_results": final_disclaimer_results if final_disclaimer_results else [],
                "sugar_claim_message_for_report": sugar_claim_message if table_type == "table1" and has_added_sugar == "ไม่มีการเติมน้ำตาล" else None,
                "energy_warning_for_report": energy_warning if table_type == "table1" and has_added_sugar == "ไม่มีการเติมน้ำตาล" and 'energy_warning' in locals() else None,
            }
            
            # Capture evaluation messages for the report
            # This requires refactoring how messages are displayed or capturing them
            # For now, we'll build it from the claim results logic directly if possible
            # This is a simplified version; a more robust solution would involve a dedicated list for report messages
            
            # The following block that manually constructed current_eval_messages is no longer needed
            # as messages are captured directly into session_state.
            # current_eval_messages = []
            # # General claims
            # for idx, row in claims.iterrows():
            #     nutrient = row["nutrient"]
            #     claim_text = row["claim_text"]
            #     claim_key = f"{nutrient}_{claim_text}"
            #     if claim_key not in processed_claims: continue
            #     pass 
            # # Vitamin/Mineral Claims
            # if vitamin_mineral_results:
            #     for vm_res in vitamin_mineral_results:
            #         text = f"{vm_res['nutrient']}: {('สามารถใช้' if vm_res['pass'] else 'ไม่เข้าเงื่อนไข')}คำกล่าวอ้าง: '{vm_res['claim_type']}' ({vm_res['threshold']})"
            #         icon = "✅" if vm_res['pass'] else "❌"
            #         current_eval_messages.append({"text": f"{icon} {text}", "is_success": vm_res['pass']})
            
            report_data["evaluation_messages"] = st.session_state.get("current_evaluation_messages_for_report", [])

            # Add download button
            st.markdown("--- ") # Separator
            add_styled_paragraph_report = lambda text, bold=False, italic=False, font_size=11, color=None: None # Dummy for report context
            try:
                report_stream = generate_nutrition_report(report_data)
                st.download_button(
                    label="📥 ดาวน์โหลดผลการตรวจสอบ (Word)",
                    data=report_stream,
                    file_name="nutrition_analysis_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการสร้างไฟล์ Word: {e}")
                st.error("กรุณาตรวจสอบว่าได้ติดตั้งไลบรารี python-docx แล้ว (pip install python-docx)")


# เพิ่มฟังก์ชันสำหรับตรวจสอบว่าเป็นวิตามินหรือแร่ธาตุหรือไม่
def is_vitamin_or_mineral(nutrient_key):
    """
    ตรวจสอบว่า nutrient_key เป็นวิตามินหรือแร่ธาตุหรือไม่
    """
    if not nutrient_key:
        return False
        
    nutrient_key_lower = str(nutrient_key).lower()
    
    # รายการสารอาหารที่ไม่ใช่วิตามินหรือแร่ธาตุ - ให้คืนค่า False ทันที
    non_vm_nutrients = [
        "energy", "พลังงาน", "kcal", "calories", "calorie",
        "fat", "ไขมัน", "ไขมันทั้งหมด", 
        "saturated_fat", "ไขมันอิ่มตัว",
        "trans_fat", "ไขมันทรานส์",
        "cholesterol", "คอเลสเตอรอล",
        "carbohydrate", "คาร์โบไฮเดรต", "คาร์บ", "carb",
        "sugar", "น้ำตาล", "น้ำตาลทั้งหมด",
        "protein", "โปรตีน", # เพิ่มโปรตีนเข้าไปในรายการ
        "fiber", "ใยอาหาร", "dietary fiber" # เพิ่มใยอาหารเข้าไปในรายการ
    ]
    
    # ตรวจสอบว่าเป็นสารอาหารที่ไม่ใช่วิตามินหรือแร่ธาตุหรือไม่
    for non_vm in non_vm_nutrients:
        if non_vm in nutrient_key_lower:
            return False
    
    # ตัวอย่างชื่อวิตามินในภาษาไทย (จาก Thai_RDIs.csv)
    thai_vitamins = [
        "วิตามินเอ", "วิตามินดี", "วิตามินอี", "วิตามินเค", "วิตามินซี",
        "วิตามินบี1", "วิตามินบี2", "วิตามินบี6", "วิตามินบี12", "ไทอามีน", "ไรโบฟลาวิน",
        "ไบโอติน", "โฟเลต", "ไนอะซิน", "กรดแพนโททีนิก", "โฟลิก", "กรดแพนโททีนิก",
        "แคลเซียม", "เหล็ก", "ฟอสฟอรัส", "แมกนีเซียม", "สังกะสี",
        "ไอโอดีน", "ทองแดง", "ซีลีเนียม", "แมงกานีส", "โมลิบดีนัม", 
        "โครเมียม", "โพแทสเซียม", "คลอไรด์"
    ]
    
    # คำสำคัญภาษาอังกฤษ
    eng_keywords = [
        "vitamin", "mineral", 
        "a", "d", "e", "k", "c", "b",
        "b1", "b2", "b3", "b6", "b12",
        "thiamine", "riboflavin", "niacin", "pantothenic", "biotin", 
        "folate", "folic", "cobalamin", "ascorbic",
        "calcium", "phosphorus", "iron", "potassium", "zinc", 
        "magnesium", "iodine", "selenium", "copper", "manganese",
        "molybdenum", "chromium", "chloride"
    ]
    
    # เพิ่มโซเดียมเป็นกรณีพิเศษ - โซเดียมเป็นแร่ธาตุแต่ควรถูกตรวจสอบแยกต่างหาก
    # เนื่องจากเกี่ยวข้องกับคำกล่าวอ้างเกี่ยวกับโซเดียมต่ำ/ปราศจาก
    if "sodium" in nutrient_key_lower or "โซเดียม" in nutrient_key_lower:
        return False
    
    # ตรวจสอบชื่อวิตามินภาษาไทยโดยตรง
    for vitamin in thai_vitamins:
        if vitamin.lower() in nutrient_key_lower:
            return True
    
    # ตรวจสอบคำสำคัญภาษาอังกฤษ
    for keyword in eng_keywords:
        if keyword.lower() in nutrient_key_lower:
            return True
            
    return False

def is_same_vitamin_mineral(user_input, claim_nutrient):
    """
    ตรวจสอบว่า user_input และ claim_nutrient เป็นวิตามินหรือแร่ธาตุชนิดเดียวกันหรือไม่
    """
    # ถ้าไม่มีข้อมูล
    if not user_input or not claim_nutrient:
        return False
        
    # แปลงเป็นตัวพิมพ์เล็กเพื่อให้การเปรียบเทียบแม่นยำยิ่งขึ้น
    user_input_lower = str(user_input).lower().strip()
    claim_nutrient_lower = str(claim_nutrient).lower().strip()
    
    # เปรียบเทียบโดยตรงทั้งคำ
    if user_input_lower == claim_nutrient_lower:
        return True
    
    # แผนที่การจับคู่แม่นยำสำหรับวิตามินและแร่ธาตุ
    exact_match_map = {
        # วิตามิน - ชื่อภาษาไทยเป็นคีย์หลัก
        "วิตามินเอ": ["vitamin a", "vitamin_a", "วิตามินเอ"],
        "วิตามินดี": ["vitamin d", "vitamin_d", "วิตามินดี", "calciferol", "แคลซิเฟอรอล"],
        "วิตามินอี": ["vitamin e", "vitamin_e", "วิตามินอี", "tocopherol", "โทโคเฟอรอล"],
        "วิตามินเค": ["vitamin k", "vitamin_k", "วิตามินเค", "phylloquinone", "ฟิลโลควิโนน"],
        "วิตามินบี1": ["vitamin b1", "vitamin_b1", "วิตามินบี1", "thiamine", "ไทอามีน", "thiamin", "วิตามินบี1/ไทอามีน", "วิตามิน บี1"],
        "วิตามินบี2": ["vitamin b2", "vitamin_b2", "วิตามินบี2", "riboflavin", "ไรโบฟลาวิน", "วิตามินบี2/ไรโบฟลาวิน", "วิตามิน บี2"],
        "วิตามินบี6": ["vitamin b6", "vitamin_b6", "วิตามินบี6", "pyridoxine", "ไพริดอกซีน"],
        "วิตามินบี12": ["vitamin b12", "vitamin_b12", "วิตามินบี12", "cobalamin", "โคบาลามิน"],
        "วิตามินซี": ["vitamin c", "vitamin_c", "วิตามินซี", "ascorbic acid", "กรดแอสคอร์บิก"],
        "โฟเลต": ["folate", "folic acid", "โฟเลต", "กรดโฟลิก"],
        "ไนอะซิน": ["niacin", "nicotinic acid", "ไนอะซิน", "กรดนิโคตินิก"],
        "ไบโอติน": ["biotin", "ไบโอติน"],
        "กรดแพนโทเธนิก": ["pantothenic acid", "กรดแพนโทเธนิก", "แพนโททีนิก"],
        
        # แร่ธาตุ - ชื่อภาษาไทยเป็นคีย์หลัก
        "แคลเซียม": ["calcium", "แคลเซียม"],
        "เหล็ก": ["iron", "เหล็ก"],
        "ฟอสฟอรัส": ["phosphorus", "ฟอสฟอรัส"],
        "แมกนีเซียม": ["magnesium", "แมกนีเซียม"],
        "สังกะสี": ["zinc", "สังกะสี"],
        "ไอโอดีน": ["iodine", "ไอโอดีน"],
        "ทองแดง": ["copper", "ทองแดง"],
        "โพแทสเซียม": ["potassium", "โพแทสเซียม"],
        "แมงกานีส": ["manganese", "แมงกานีส"],
        "ซีลีเนียม": ["selenium", "ซีลีเนียม"],
        "โมลิบดีนัม": ["molybdenum", "โมลิบดีนัม"],
        "โครเมียม": ["chromium", "โครเมียม"],
        "คลอไรด์": ["chloride", "คลอไรด์"],
        
        # สารอาหารอื่นๆ ที่เป็นคนละกลุ่ม - ใช้ในการตรวจสอบเพื่อป้องกันการจับคู่ผิด
        "โปรตีน": ["protein", "โปรตีน"],
        "ใยอาหาร": ["fiber", "dietary fiber", "ใยอาหาร"],
        "พลังงาน": ["energy", "พลังงาน", "kcal", "calories"]
    }
    
    # สร้าง reverse map เพื่อให้ค้นหาง่ายขึ้น
    reverse_map = {}
    for main_key, aliases in exact_match_map.items():
        for alias in aliases:
            reverse_map[alias] = main_key
    
    # ตรวจสอบโดยตรงจาก user_input
    for match_key in exact_match_map.keys():
        # เช็คคำเต็มเท่านั้น ไม่เช็ค substring
        if user_input_lower == match_key or user_input_lower in exact_match_map[match_key]:
            # เมื่อเจอ user_input แล้ว ต้องเช็คว่า claim_nutrient ตรงกับกลุ่มเดียวกันหรือไม่
            main_nutrient = match_key
            for claim_alias in exact_match_map[main_nutrient]:
                if claim_nutrient_lower == claim_alias or claim_nutrient_lower == main_nutrient:
                    return True
                    
            # กรณี claim_nutrient อาจจะเป็นคีย์หลักใน map
            if claim_nutrient_lower in exact_match_map and main_nutrient in exact_match_map[claim_nutrient_lower]:
                return True
                
            # กรณี claim_nutrient อาจจะมาในรูปแบบ alias ในกลุ่มอื่น
            if claim_nutrient_lower in reverse_map and reverse_map[claim_nutrient_lower] == main_nutrient:
                return True
    
    # ตรวจสอบจาก claim_nutrient ในกรณีที่ยังไม่พบจากการค้นหาด้านบน
    for match_key in exact_match_map.keys():
        if claim_nutrient_lower == match_key or claim_nutrient_lower in exact_match_map[match_key]:
            main_nutrient = match_key
            for user_alias in exact_match_map[main_nutrient]:
                if user_input_lower == user_alias or user_input_lower == main_nutrient:
                    return True
            
            # ใช้ reverse map ตรวจสอบเช่นกัน
            if user_input_lower in reverse_map and reverse_map[user_input_lower] == main_nutrient:
                return True
    
    # กรณี user_input และ claim_nutrient เป็นคีย์ที่ไม่พบใน map ทั้งคู่ แต่ควรจะ match กัน
    # ใช้ reverse map เพื่อดูว่าทั้งคู่อยู่ในกลุ่มเดียวกันหรือไม่
    if user_input_lower in reverse_map and claim_nutrient_lower in reverse_map:
        return reverse_map[user_input_lower] == reverse_map[claim_nutrient_lower]
        
    # กรณีพิเศษสำหรับวิตามิน
    # ตรวจสอบกรณีที่มีคำว่า "vitamin" หรือ "วิตามิน" ตามด้วยตัวอักษรเดียวกัน
    user_vitamin_match = re.search(r'(vitamin|วิตามิน)\s*([a-z])\b', user_input_lower)
    claim_vitamin_match = re.search(r'(vitamin|วิตามิน)\s*([a-z])\b', claim_nutrient_lower)
    
    if user_vitamin_match and claim_vitamin_match:
        user_letter = user_vitamin_match.group(2)
        claim_letter = claim_vitamin_match.group(2)
        if user_letter == claim_letter:
            return True
    
    return False

# ฟังก์ชันสำหรับตรวจสอบเงื่อนไขวิตามินและแร่ธาตุ
def check_vitamin_mineral_claims(nutrient_values, adjusted_values, claims_table, RDI_df, selected_label=None, label_values=None):
    """
    ตรวจสอบคำกล่าวอ้างเกี่ยวกับวิตามินและแร่ธาตุ
    
    Args:
        nutrient_values (dict): ค่าสารอาหารจากหน่วยบริโภคบนฉลาก
        adjusted_values (dict): ค่าสารอาหารจากหน่วยบริโภคอ้างอิง
        claims_table (pd.DataFrame): ตารางคำกล่าวอ้าง
        RDI_df (pd.DataFrame): ตาราง RDI
        selected_label (str, optional): ประเภทอาหาร เช่น "ไม่อยู่ในบัญชีหมายเลข 2"
        label_values (dict, optional): ค่าสารอาหารจากฉลากที่ปรับค่าแล้ว
    """
    try:
        vitamin_mineral_claims = []
        
        # หาวิตามินและแร่ธาตุทั้งหมดที่กรอกข้อมูล
        vitamin_keys = [key for key in nutrient_values.keys() if is_vitamin_or_mineral(key) and nutrient_values[key] is not None]
        
        if not vitamin_keys:
            return []
        
        for vitamin_key in vitamin_keys:
            vitamin_value = nutrient_values.get(vitamin_key)
            if vitamin_value is None:
                continue
                
            thai_name = RDI_MAPPING.get(vitamin_key, vitamin_key)
            
            rdi_value = None
            for _, row in RDI_df.iterrows():
                if is_same_vitamin_mineral(thai_name, row['สารอาหาร']):
                    try:
                        rdi_value = float(row['ปริมาณที่แนะนำต่อวัน (Thai RDIs)'])
                        break
                    except (ValueError, TypeError) as e:
                        st.error(f"ข้อมูล RDI ไม่ถูกต้อง: {e}")
                        continue
            
            if rdi_value is None:
                continue
            
            try:
                # คำนวณ %RDI จากค่าที่ปรับแก้แล้ว (adjusted_values)
                adjusted_value = adjusted_values.get(vitamin_key, 0)
                if adjusted_value is None:
                    continue
                    
                percent_rdi = (adjusted_value / rdi_value) * 100
                if is_vitamin_or_mineral(vitamin_key):
                    percent_rdi = round_rdi_percent(percent_rdi)
                percent_rdi_per_100kcal = adjusted_values.get(f"{vitamin_key}_rdi_percent_per_100kcal", 0)
                
                # คำนวณ %RDI จากค่าในฉลาก (label_values) - สำหรับกรณีอยู่ในบัญชีหมายเลข 2
                label_percent_rdi = None
                if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and label_values and label_values.get(vitamin_key) is not None:
                    label_value = label_values.get(vitamin_key, 0)
                    if label_value is not None:
                        label_percent_rdi = (label_value / rdi_value) * 100
                        if is_vitamin_or_mineral(vitamin_key):
                            label_percent_rdi = round_rdi_percent(label_percent_rdi)
                
                matching_claims = []
                for _, row in claims_table.iterrows():
                    if 'nutrient' not in row:
                        continue
                    nutrient = row['nutrient']
                    if is_same_vitamin_mineral(thai_name, str(nutrient)):
                        matching_claims.append(row)
                
                if not matching_claims:
                    continue
                
                for claim_row in matching_claims:
                    claim_type = claim_row.get('claim_type', '')
                    if claim_type == '':
                        claim_type = claim_row.get('state', '')
                    
                    nutrient = claim_row['nutrient']
                    claim_text = claim_row.get('claim_text', '')
                    
                    threshold = None
                    threshold_str = ""
                    threshold_rdi_100kcal = str(claim_row.get("threshold_rdi_100kcal", "nan"))
                    
                    # Check both per 100g/ml and per 100kcal thresholds
                    claim_valid_adjusted = False
                    claim_valid_label = False
                    threshold_str = ""
                    
                    # Check per 100g/ml threshold for adjusted values
                    if 'threshold_rdi' in claim_row and not pd.isna(claim_row['threshold_rdi']):
                        threshold_str = str(claim_row['threshold_rdi'])
                        match = re.search(r'([<>≥≤]=?)\s*(\d+(?:\.\d+)?)', threshold_str)
                        if match:
                            operator = match.group(1)
                            threshold_value = float(match.group(2))
                            
                            if operator == '>=' or operator == '≥':
                                claim_valid_adjusted = percent_rdi >= threshold_value
                                if label_percent_rdi is not None:
                                    claim_valid_label = label_percent_rdi >= threshold_value
                            elif operator == '>':
                                claim_valid_adjusted = percent_rdi > threshold_value
                                if label_percent_rdi is not None:
                                    claim_valid_label = label_percent_rdi > threshold_value
                            elif operator == '<=' or operator == '≤':
                                claim_valid_adjusted = percent_rdi <= threshold_value
                                if label_percent_rdi is not None:
                                    claim_valid_label = label_percent_rdi <= threshold_value
                            elif operator == '<':
                                claim_valid_adjusted = percent_rdi < threshold_value
                                if label_percent_rdi is not None:
                                    claim_valid_label = label_percent_rdi < threshold_value
                            else:
                                claim_valid_adjusted = False
                                claim_valid_label = False
                                
                            threshold_str = f"{operator} {threshold_value}% RDI"
                        else:
                            try:
                                threshold_value = float(threshold_str)
                                claim_valid_adjusted = percent_rdi >= threshold_value
                                if label_percent_rdi is not None:
                                    claim_valid_label = label_percent_rdi >= threshold_value
                                threshold_str = f">= {threshold_value}% RDI"
                            except (ValueError, TypeError):
                                continue
                    
                    # Check per 100kcal threshold if available
                    per_100kcal_valid = False
                    if threshold_rdi_100kcal != "nan":
                        match = re.search(r'([<>≥≤]=?)\s*(\d+(?:\.\d+)?)', threshold_rdi_100kcal)
                        if match:
                            operator = match.group(1)
                            threshold_value = float(match.group(2))
                            
                            if operator == '>=' or operator == '≥':
                                per_100kcal_valid = percent_rdi_per_100kcal >= threshold_value
                            elif operator == '>':
                                per_100kcal_valid = percent_rdi_per_100kcal > threshold_value
                            elif operator == '<=' or operator == '≤':
                                per_100kcal_valid = percent_rdi_per_100kcal <= threshold_value
                            elif operator == '<':
                                per_100kcal_valid = percent_rdi_per_100kcal < threshold_value
                            else:
                                per_100kcal_valid = False
                            
                            # ปรับเฉพาะ claim_valid_adjusted เท่านั้น
                            claim_valid_adjusted = claim_valid_adjusted or per_100kcal_valid
                            
                            # Update threshold string to show both conditions
                            if threshold_str:
                                threshold_str += f" หรือ {operator} {threshold_value}% RDI ต่อ 100kcal"
                            else:
                                threshold_str = f"{operator} {threshold_value}% RDI ต่อ 100kcal"
                    
                    # กำหนดเงื่อนไขการผ่านเกณฑ์ตามประเภทอาหาร
                    if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and label_percent_rdi is not None:
                        # กรณีอยู่ในบัญชีหมายเลข 2 (selected_label != "ไม่อยู่ในบัญชีหมายเลข 2")
                        # ต้องผ่านทั้งจากค่าในฉลากและค่าที่ปรับแก้ (เงื่อนไขเดียวกันกับสารอาหารอื่น)
                        claim_valid = claim_valid_adjusted and claim_valid_label
                    else:
                        # กรณีไม่อยู่ในบัญชีหมายเลข 2 (selected_label == "ไม่อยู่ในบัญชีหมายเลข 2")
                        # หรือกรณีไม่มีค่า label_percent_rdi ให้ใช้เฉพาะค่าที่ปรับแก้
                        claim_valid = claim_valid_adjusted
                    
                    if claim_valid:
                        vitamin_mineral_claims.append({
                            "nutrient": nutrient,
                            "claim_type": claim_text,
                            "threshold": threshold_str,
                            "pass": True,
                            "label_percent": label_percent_rdi if label_percent_rdi is not None else percent_rdi,
                            "ref_percent": percent_rdi,
                            "per_100kcal_percent": percent_rdi_per_100kcal
                        })
                    else:
                        vitamin_mineral_claims.append({
                            "nutrient": nutrient,
                            "claim_type": claim_text,
                            "threshold": threshold_str,
                            "pass": False,
                            "label_percent": label_percent_rdi if label_percent_rdi is not None else percent_rdi,
                            "ref_percent": percent_rdi,
                            "per_100kcal_percent": percent_rdi_per_100kcal
                        })
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการคำนวณ %RDI สำหรับ {thai_name}: {e}")
                continue
        
        return vitamin_mineral_claims
        
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการตรวจสอบคำกล่าวอ้างวิตามินและแร่ธาตุ: {e}")
        return []

# ฟังก์ชันสำหรับตรวจสอบเงื่อนไขวิตามินและแร่ธาตุ
def check_single_vitamin_mineral_claim(adjusted_values, vitamin_key, rdi_df):
    """
    ตรวจสอบการกล่าวอ้างวิตามินและแร่ธาตุ โดยพิจารณาค่า %RDI
    ตามประกาศกระทรวงสาธารณสุข (ฉบับที่ 182) พ.ศ. 2541
    """
    
    # ตรวจสอบว่ามีข้อมูลสารอาหาร
    if vitamin_key not in adjusted_values:
        return False, "ไม่มีข้อมูลวิตามินหรือแร่ธาตุที่ระบุ"
    
    # ดึงค่าที่ปรับแก้แล้ว
    adjusted_value = adjusted_values.get(vitamin_key, 0)
    percent_rdi = adjusted_values.get(f"{vitamin_key}_rdi_percent", 0)
    if is_vitamin_or_mineral(vitamin_key):
        percent_rdi = round_rdi_percent(percent_rdi)
    
    
    # ดึงค่า per 100kcal (ถ้ามี)
    percent_rdi_per_100kcal = adjusted_values.get(f"{vitamin_key}_rdi_percent_per_100kcal", 0)
    
    # ตรวจสอบว่าเป็นปริมาณที่มากพอสำหรับการกล่าวอ้าง
    # เกณฑ์ตามประกาศฯ คือต้องมีอย่างน้อย 10% ของ Thai RDI
    
    # ผ่านเงื่อนไขถ้าหาก:
    # 1. %RDI ต่อ 100g/ml มากกว่าหรือเท่ากับ 15%
    condition1 = percent_rdi >= 15
    
    # 2. %RDI ต่อ 100kcal มากกว่าหรือเท่ากับ 5%
    condition2 = percent_rdi_per_100kcal >= 5
    
    # ผ่านถ้าเข้าเงื่อนไขใดเงื่อนไขหนึ่ง
    if condition1 or condition2:
        message = f"✅ สามารถกล่าวอ้างได้ (Per 100g/ml: {percent_rdi:.1f}% RDI"
        if percent_rdi_per_100kcal > 0:
            message += f", Per 100kcal: {percent_rdi_per_100kcal:.1f}% RDI"
        message += ")"
        return True, message
    else:
        message = f"❌ ไม่สามารถกล่าวอ้างได้ (Per 100g/ml: {percent_rdi:.1f}% RDI"
        if percent_rdi_per_100kcal > 0:
            message += f", Per 100kcal: {percent_rdi_per_100kcal:.1f}% RDI"
        message += ") - ต้องการอย่างน้อย 15% RDI ต่อ 100g/ml หรือ 5% RDI ต่อ 100kcal"
        return False, message

def format_rdi_threshold(threshold_rdi_str):
    """
    แปลงรูปแบบของ threshold RDI ให้เหมาะสมสำหรับการประเมิน
    เช่น "20" -> ">= 20% RDI", ">= 20" -> ">= 20% RDI", "20% RDI" -> ">= 20% RDI"
    """
    if not threshold_rdi_str or pd.isna(threshold_rdi_str) or threshold_rdi_str == "nan":
        return None
        
    threshold_rdi_str = str(threshold_rdi_str).strip()
    
    # ตรวจสอบว่ามีเครื่องหมายหรือไม่
    has_operator = any(op in threshold_rdi_str for op in [">=", "<=", ">", "<", "≥", "≤"])
    
    # แยกตัวเลขออกจากเครื่องหมาย (>=, >, <, <=)
    match = re.search(r'([<>≥≤]=?)\s*(\d+(\.\d+)?)', threshold_rdi_str)
    if match:
        operator = match.group(1)
        value = match.group(2)
        if "RDI" not in threshold_rdi_str:
            return f"{operator} {value}% RDI"
        else:
            return threshold_rdi_str
    
    # ถ้าไม่มีเครื่องหมายและไม่มี RDI
    if "RDI" not in threshold_rdi_str:
        try:
            # ตรวจสอบว่าเป็นตัวเลขหรือไม่
            float(threshold_rdi_str)
            return f">= {threshold_rdi_str}% RDI"
        except ValueError:
            return None
    
    # มี RDI อยู่แล้ว แต่ตรวจสอบเครื่องหมาย
    if not has_operator:
        # ไม่มีเครื่องหมาย ให้เพิ่ม >=
        return f">= {threshold_rdi_str}"
    else:
        return threshold_rdi_str

def prepare_disclaimers(nutrient_values, adjusted_values, selected_label, 
                        actual_serving_size=None, food_state_value=None, 
                        group_info=None, nutrition_check_method=None):
    """
    เตรียมข้อมูล disclaimers จากทั้งหน่วยบริโภคบนฉลากและหน่วยบริโภคอ้างอิง
    
    Args:
        nutrient_values (dict): ค่าสารอาหารจากหน่วยบริโภคบนฉลาก (หรือต่อ 100g/ml ถ้าเป็นผลวิเคราะห์)
        adjusted_values (dict): ค่าสารอาหารจากหน่วยบริโภคอ้างอิง
        selected_label (str): ประเภทของอาหาร เช่น "ไม่อยู่ในบัญชีหมายเลข 2"
        actual_serving_size (float, optional): ปริมาณหน่วยบริโภคบนฉลาก
        food_state_value (str, optional): สถานะของอาหาร ("solid" หรือ "liquid")
        group_info (pd.Series, optional): ข้อมูลกลุ่มอาหารจาก food_groups
        nutrition_check_method (str, optional): วิธีการตรวจสอบที่เลือก ("ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)" หรือ "ตรวจสอบจากฉลากโภชนาการ (ต่อ 1 หน่วยบริโภค)")
        
    Returns:
        list: รายการ disclaimers ที่ต้องแสดง
    """
    # disclaimer_values_label will hold values per actual_serving_size for "label check"
    # disclaimer_values_reference will hold values per reference serving size (from adjusted_values)

    disclaimer_values_label = {}
    
    if selected_label != "ไม่อยู่ในบัญชีหมายเลข 2" and \
       nutrition_check_method == "ตรวจสอบจากผลวิเคราะห์โภชนาการ (ต่อ 100 g หรือ ml)" and \
       actual_serving_size is not None and actual_serving_size > 0:
        # Case: In List 2, input is per 100g analysis.
        # We need to scale nutrient_values (which are per 100g) to actual_serving_size for the "label check".
        conversion_factor = actual_serving_size / 100.0
        disclaimer_values_label = {
            'total_fat': float(nutrient_values.get('fat', 0) or 0) * conversion_factor,
            'saturated_fat': float(nutrient_values.get('saturated_fat', 0) or 0) * conversion_factor,
            'cholesterol': float(nutrient_values.get('cholesterol', 0) or 0) * conversion_factor,
            'sodium': float(nutrient_values.get('sodium', 0) or 0) * conversion_factor,
            'total_sugars': float(nutrient_values.get('sugar', 0) or 0) * conversion_factor
        }
    else:
        # Default case (Not in List 2 OR input is already per serving):
        # disclaimer_values_label uses nutrient_values directly (which are already per serving or will be ignored if not in list 2)
        disclaimer_values_label = {
            'total_fat': float(nutrient_values.get('fat', 0) or 0),
            'saturated_fat': float(nutrient_values.get('saturated_fat', 0) or 0),
            'cholesterol': float(nutrient_values.get('cholesterol', 0) or 0),
            'sodium': float(nutrient_values.get('sodium', 0) or 0),
            'total_sugars': float(nutrient_values.get('sugar', 0) or 0)
        }

    disclaimer_values_reference = {
        'total_fat': float(adjusted_values.get('fat', 0) or 0),
        'saturated_fat': float(adjusted_values.get('saturated_fat', 0) or 0),
        'cholesterol': float(adjusted_values.get('cholesterol', 0) or 0),
        'sodium': float(adjusted_values.get('sodium', 0) or 0),
        'total_sugars': float(adjusted_values.get('sugar', 0) or 0)
    }

    # กรณีอาหารไม่อยู่ในบัญชีหมายเลข 2 ให้คำนวณจากหน่วยบริโภคอ้างอิงเท่านั้น
    if selected_label == "ไม่อยู่ในบัญชีหมายเลข 2":
        disclaimer_results_reference = check_disclaimers(disclaimer_values_reference)
        
        final_results = []
        for disclaimer in disclaimer_results_reference:
            unit_text = "กรัม" if food_state_value == "solid" else "มิลลิลิตร"
            
            if actual_serving_size is not None and actual_serving_size > 0:
                value_per_actual_serving = (disclaimer['value'] / 100.0) * actual_serving_size
                disclaimer['message'] = (
                    f"⚠️ ปริมาณ {disclaimer['nutrient']} อยู่ในเกณฑ์ที่ต้องมีคำชี้แจง (Disclaimer) ประกอบคำกล่าวอ้าง: "
                    f"มี{disclaimer['nutrient']} {value_per_actual_serving:.1f} {disclaimer['unit']} ต่อ {actual_serving_size:.1f} {unit_text} "
                    f"หรือ มี{disclaimer['nutrient']} {disclaimer['value']:.1f} {disclaimer['unit']} ต่อ 100 {unit_text}"
                )
            else:
                disclaimer['message'] = (
                    f"⚠️ ปริมาณ {disclaimer['nutrient']} อยู่ในเกณฑ์ที่ต้องมีคำชี้แจง (Disclaimer) ประกอบคำกล่าวอ้าง: "
                                   f"มี{disclaimer['nutrient']} {disclaimer['value']:.1f} {disclaimer['unit']} ต่อ 100 {unit_text}"
                )
            
            disclaimer['label_value'] = 0
            disclaimer['reference_value'] = disclaimer['value']
            final_results.append(disclaimer)
            
        return final_results
    
    # กรณีอาหารอยู่ในบัญชีหมายเลข 2 ตรวจสอบทั้งจากหน่วยบริโภคบนฉลากและหน่วยบริโภคอ้างอิง
    else:
        # ตรวจสอบว่า food_state_value มีค่าหรือไม่ กรณีอาหารอยู่ในบัญชีหมายเลข 2 อาจไม่มีค่านี้
        if food_state_value is None:
            food_state_value = "solid"  # ค่าเริ่มต้น
            
        # disclaimer_values_label is now correctly scaled if input was per 100g for List 2 items.
        disclaimer_results_label = check_disclaimers(disclaimer_values_label)
        disclaimer_results_reference = check_disclaimers(disclaimer_values_reference)
        
        final_results = []
        
        # สร้าง dictionaries เพื่อการค้นหาที่รวดเร็ว
        label_nutrients_dict = {}
        reference_nutrients_dict = {}
        
        # เก็บค่าจากหน่วยบริโภคบนฉลาก
        for disclaimer in disclaimer_results_label:
            nutrient = disclaimer['nutrient']
            label_nutrients_dict[nutrient] = disclaimer
        
        # เก็บค่าจากหน่วยบริโภคอ้างอิง
        for disclaimer in disclaimer_results_reference:
            nutrient = disclaimer['nutrient']
            reference_nutrients_dict[nutrient] = disclaimer
        
        # รวมสารอาหารที่เกินเกณฑ์จากทั้งสองกรณี
        all_disclaimer_nutrients = set(list(label_nutrients_dict.keys()) + list(reference_nutrients_dict.keys()))
        
        # ตรวจสอบทุกสารอาหารที่ต้องแสดง disclaimer
        for nutrient in all_disclaimer_nutrients:
            # เตรียมข้อมูลที่จำเป็น
            in_label = nutrient in label_nutrients_dict
            in_reference = nutrient in reference_nutrients_dict
            
            # ค่าสารอาหารและหน่วย
            thai_nutrient_name = None
            if in_label:
                label_value = label_nutrients_dict[nutrient]['value']
                threshold = label_nutrients_dict[nutrient]['threshold']
                unit = label_nutrients_dict[nutrient]['unit']
                thai_nutrient_name = nutrient
            elif in_reference:
                label_value = 0  # จะถูกแทนที่ด้วยค่าจริง
                threshold = reference_nutrients_dict[nutrient]['threshold']
                unit = reference_nutrients_dict[nutrient]['unit']
                thai_nutrient_name = nutrient
            
            if in_reference:
                reference_value = reference_nutrients_dict[nutrient]['value']
            else:
                reference_value = 0  # จะถูกแทนที่ด้วยค่าจริง
            
            # ดึงค่าจริงจากข้อมูลสารอาหารเดิม แม้ไม่เกินเกณฑ์
            # สำหรับสารอาหารที่มีชื่อภาษาไทย
            nutrient_key_mapping = {
                'ไขมันทั้งหมด': 'total_fat',
                'ไขมันอิ่มตัว': 'saturated_fat',
                'คอเลสเตอรอล': 'cholesterol',
                'โซเดียม': 'sodium',
                'น้ำตาลทั้งหมด': 'total_sugars'
            }
            
            eng_key = nutrient_key_mapping.get(thai_nutrient_name)
            if eng_key:
                # ถ้าไม่เกินเกณฑ์บนฉลาก แต่มีค่าในข้อมูลเดิม
                if not in_label and eng_key in disclaimer_values_label:
                    label_value = disclaimer_values_label[eng_key]
                
                # ถ้าไม่เกินเกณฑ์ในหน่วยอ้างอิง แต่มีค่าในข้อมูลเดิม
                if not in_reference and eng_key in disclaimer_values_reference:
                    reference_value = disclaimer_values_reference[eng_key]
                    
            # ปัดเลขตามหลักเกณฑ์ของกฎหมาย
            nutrient_type_map = {
                'ไขมันทั้งหมด': 'fat',
                'ไขมันอิ่มตัว': 'saturated_fat',
                'คอเลสเตอรอล': 'cholesterol',
                'โซเดียม': 'sodium',
                'น้ำตาลทั้งหมด': 'sugar'
            }
            
            # ใช้ function round_nutrition_value เพื่อปัดเลขตามหลักเกณฑ์
            nutrient_type = nutrient_type_map.get(thai_nutrient_name, 'other')
            label_value = round_nutrition_value(label_value, nutrient_type)
            reference_value = round_nutrition_value(reference_value, nutrient_type)
            
            actual_size_str = str(actual_serving_size) if actual_serving_size is not None else "1"
            
            message = f"⚠️ ปริมาณ {nutrient} อยู่ในเกณฑ์ที่ต้องมีคำชี้แจง (Disclaimer) ประกอบคำกล่าวอ้าง: "
            
            # ปรับข้อความตามสถานการณ์
            if group_info is not None and isinstance(group_info, pd.Series) and 'serving_value' in group_info and 'unit' in group_info:
                ref_serving_size = float(group_info['serving_value'])
                ref_unit = group_info['unit']
                is_small_serving = ref_serving_size <= 30 and ref_unit.lower() in ["กรัม", "g", "ml", "มิลลิลิตร"]
                display_ref_size = ref_serving_size * 2 if is_small_serving else ref_serving_size
                
                # กรณีที่เกินทั้งสองหน่วยบริโภค
                if in_label and in_reference:
                    message += (f"มี{nutrient} {label_value:.1f} {unit} ต่อ {actual_size_str} {ref_unit} "
                                f"หรือ มี{nutrient} {reference_value:.1f} {unit} ต่อ {display_ref_size:.1f} {ref_unit}")
                # กรณีที่เกินเฉพาะหน่วยบริโภคบนฉลาก
                elif in_label:
                    message += f"มี{nutrient} {label_value:.1f} {unit} ต่อ {actual_size_str} {ref_unit}"
                # กรณีที่เกินเฉพาะหน่วยบริโภคอ้างอิง
                elif in_reference:
                    message += f"มี{nutrient} {reference_value:.1f} {unit} ต่อ {display_ref_size:.1f} {ref_unit}"
            else:
                # กรณีที่เกินทั้งสองหน่วยบริโภค
                if in_label and in_reference:
                    message += (f"มี{nutrient} {label_value:.1f} {unit} ต่อหน่วยบริโภค ({actual_size_str} g/ml) และ "
                                f"มี{nutrient} {reference_value:.1f} {unit} ต่อหน่วยบริโภคอ้างอิง")
                # กรณีที่เกินเฉพาะหน่วยบริโภคบนฉลาก
                elif in_label:
                    message += f"มี{nutrient} {label_value:.1f} {unit} ต่อหน่วยบริโภค ({actual_size_str} g/ml)"
                # กรณีที่เกินเฉพาะหน่วยบริโภคอ้างอิง
                elif in_reference:
                    message += f"มี{nutrient} {reference_value:.1f} {unit} ต่อหน่วยบริโภคอ้างอิง"
            
            # สร้าง dictionary ผลลัพธ์
            combined_disclaimer = {
                'nutrient': nutrient,
                'label_value': label_value,
                'reference_value': reference_value,
                'threshold': threshold,
                'unit': unit,
                'message': message
            }
            
            final_results.append(combined_disclaimer)
                
        return final_results
