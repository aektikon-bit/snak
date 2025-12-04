import streamlit as st
import pandas as pd

st.set_page_config(page_title="ระบบคำนวณคะแนนนักศึกษา", layout="centered")
st.title("📘 ระบบคำนวณคะแนนนักศึกษา")

# -------------------------
# ฟังก์ชันคำนวณเกรด
# -------------------------
def grade_from_score(total):
    if total >= 80:
        return "A"
    elif total >= 75:
        return "B+"
    elif total >= 70:
        return "B"
    elif total >= 65:
        return "C+"
    elif total >= 60:
        return "C"
    elif total >= 55:
        return "D+"
    elif total >= 50:
        return "D"
    else:
        return "F"

# -------------------------
# กรอกจำนวนคน
# -------------------------
st.subheader("🧑‍🎓 จำนวนผู้เรียน")
num = st.number_input("จำนวนคนที่ต้องการกรอก", min_value=1, max_value=50, step=1)

students = []

# -------------------------
# สร้างฟอร์มสำหรับแต่ละคน
# -------------------------
st.write("### 📝 กรอกคะแนนนักศึกษา")

for i in range(int(num)):
    with st.container():
        st.markdown(f"#### นักศึกษาคนที่ {i+1}")

        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input(f"ชื่อ #{i+1}", key=f"name_{i}")
        with col2:
            mid = st.number_input(f"กลางภาค (0-30) #{i+1}", min_value=0.0, max_value=30.0, key=f"mid_{i}")
        with col3:
            final = st.number_input(f"ปลายภาค (0-70) #{i+1}", min_value=0.0, max_value=70.0, key=f"final_{i}")

        students.append([name, mid, final])

st.write("---")

# -------------------------
# ปุ่มคำนวณ
# -------------------------
if st.button("คำนวณผลคะแนนทั้งหมด"):
    result = []

    for s in students:
        name, mid, final = s
        total = mid + final
        grade = grade_from_score(total)
        result.append([name, mid, final, total, grade])

    df = pd.DataFrame(result, columns=["ชื่อ", "กลางภาค", "ปลายภาค", "คะแนนรวม", "เกรด"])

    # เริ่มลำดับที่ 1
    df.index = df.index + 1
    df.index.name = "ลำดับ"

    st.success("✔ คำนวณเรียบร้อยแล้ว!")
    st.dataframe(df, use_container_width=True)
