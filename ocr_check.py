import streamlit as st
# import easyocr  # Commented out temporarily due to deployment issues
# import numpy as np  # Commented out temporarily due to deployment issues
# import cv2  # Commented out temporarily due to deployment issues

from checks import (
    check_expiry_phrases,
    check_packsize_phrases,
    check_registration_number,
    check_producer,
    check_ingredients,
    check_allergy_warning
)

def show():
    st.title("ตรวจสอบส่วนประกอบหลักของฉลาก")
    st.warning("⚠️ ฟีเจอร์นี้ถูกปิดใช้งานชั่วคราวเนื่องจากปัญหาการ deploy")
    st.info("กรุณาใช้ฟีเจอร์ 'ตรวจสอบข้อความจากสูตรส่วนประกอบ' แทน")
    
    # Commented out OCR functionality temporarily
    """
    uploaded_file = st.file_uploader("อัปโหลดภาพฉลากอาหารของคุณที่นี่", type=['jpg', 'png', 'jpeg'])

    def is_image_blurry(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        return fm < 100

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(img, channels="BGR", caption='ภาพฉลากที่อัปโหลด', use_column_width=True)

        if is_image_blurry(img):
            st.error("⚠️ ภาพนี้ไม่ชัด กรุณาถ่ายใหม่")
        else:
            reader = easyocr.Reader(['th', 'en'])
            result = reader.readtext(img, detail=0)
            text = "\n".join(result)

            st.subheader("ข้อความที่ได้จากภาพ:")
            user_text = st.text_area("กรุณาตรวจสอบและแก้ไขข้อความเพื่อความถูกต้อง:", text, height=200)

            if st.button("🔍 ตรวจสอบฉลาก"):
                st.info("📌 **โปรดทราบ:** ข้อมูลที่แสดงผลขึ้นอยู่กับข้อความที่ระบบถอดได้จากภาพ หากพบความผิดพลาด กรุณาตรวจสอบข้อความด้วยตนเอง และปรับแก้ก่อนกดตรวจสอบอีกครั้ง")

                if check_expiry_phrases(user_text):
                    st.error("⚠️ ขาดข้อความ 'หมดอายุ' หรือ 'ควรบริโภคก่อน'")
                else:
                    st.success("✅ มีข้อความวันหมดอายุ")

                if check_packsize_phrases(user_text):
                    st.error("⚠️ ขาดข้อความแสดงปริมาณ")
                else:
                    st.success("✅ มีข้อความปริมาณอาหาร")

                if check_registration_number(user_text):
                    st.error("⚠️ ขาดเลขสารบบอาหาร")
                else:
                    st.success("✅ มีเลขสารบบอาหาร")

                if check_producer(user_text):
                    st.error("⚠️ ขาดข้อมูลผู้ผลิตหรือนำเข้า")
                else:
                    st.success("✅ มีการแสดงผู้ผลิตหรือนำเข้า")

                if check_ingredients(user_text):
                    st.error("⚠️ ขาดข้อมูลส่วนประกอบ")
                else:
                    st.success("✅ มีการแสดงส่วนประกอบ")

                if check_allergy_warning(user_text):
                    st.warning("⚠️ ไม่พบคำเตือนเกี่ยวกับสารก่อภูมิแพ้")
                else:
                    st.success("✅ มีคำเตือนเกี่ยวกับสารก่อภูมิแพ้แล้ว")
    """
