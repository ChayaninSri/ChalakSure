import streamlit as st

def show():
    st.title("ฉลากชัวร์ 2.0")
    st.write("กรุณาเลือกเมนูจากแถบด้านซ้ายเพื่อเริ่มต้นการตรวจสอบ")
    
    # Add program information
    st.markdown("---")
    st.markdown("### ข้อมูลโปรแกรม")
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #007bff;">
        <p style="margin: 0; font-size: 1rem; line-height: 1.6; color: #333333;">
            <strong style="color: #1a1a1a;">โปรแกรมตรวจสอบฉลากนี้ พัฒนาขึ้นโดย ภก.ชญานิน ศรีชมภู</strong><br>
            <span style="color: #444444;">สำนักงานสาธารณสุขจังหวัดสมุทรปราการ</span><br><br>
            <span style="color: #444444;">หากท่านพบข้อผิดพลาดกรุณา feedback มาที่</span><br>
            <a href="mailto:chayanin.srichompoo@gmail.com" style="color: #0066cc; text-decoration: none; font-weight: 500;">
                📧 chayanin.srichompoo@gmail.com
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)