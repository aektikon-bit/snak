import streamlit as st
import numpy as np
import time

# ---------------- CONFIG ----------------
BOARD_SIZE = 20

SKINS = {
    "เขียว": [0, 255, 0],
    "น้ำเงิน": [0, 120, 255],
    "ม่วง": [180, 0, 255],
    "เหลือง": [255, 220, 0]
}

BACKGROUNDS = {
    "ดำ": [0, 0, 0],
    "เทา": [30, 30, 30],
    "น้ำเงินเข้ม": [10, 20, 60],
}

# ---------------- INITIAL STATE ----------------
if "snake" not in st.session_state:
    st.session_state.snake = [(10, 10)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = (5, 5)
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.speed = 0.15
    st.session_state.skin = "เขียว"
    st.session_state.bg = "ดำ"

# ---------------- GAME LOGIC ----------------
def place_food():
    while True:
        pos = (
            np.random.randint(0, BOARD_SIZE),
            np.random.randint(0, BOARD_SIZE)
        )
        if pos not in st.session_state.snake:
            return pos

def move_snake():
    if st.session_state.game_over:
        return

    head = st.session_state.snake[0]
    x, y = head

    if st.session_state.direction == "UP":
        new_head = (x, y - 1)
    elif st.session_state.direction == "DOWN":
        new_head = (x, y + 1)
    elif st.session_state.direction == "LEFT":
        new_head = (x - 1, y)
    else:
        new_head = (x + 1, y)

    # ชนกำแพงหรือชนตัวเอง -> จบเกม
    if (
        new_head[0] < 0 or new_head[0] >= BOARD_SIZE or
        new_head[1] < 0 or new_head[1] >= BOARD_SIZE or
        new_head in st.session_state.snake
    ):
        st.session_state.game_over = True
        return

    # กินอาหาร
    if new_head == st.session_state.food:
        st.session_state.snake = [new_head] + st.session_state.snake
        st.session_state.food = place_food()
        st.session_state.score += 1
    else:
        st.session_state.snake = [new_head] + st.session_state.snake[:-1]

# ---------------- UI ----------------
st.title("🐍 Snake Game — Enhanced Edition")

# Settings UI
with st.sidebar:
    st.header("⚙️ ตั้งค่าเกม")
    st.session_state.speed = st.slider("ความเร็วงู (วินาทีต่อ 1 ก้าว)", 0.05, 0.5, st.session_state.speed)
    st.session_state.skin = st.selectbox("สกินงู", list(SKINS.keys()))
    st.session_state.bg = st.selectbox("สีพื้นหลัง", list(BACKGROUNDS.keys()))

    if st.button("🔄 เริ่มใหม่"):
        st.session_state.snake = [(10, 10)]
        st.session_state.direction = "RIGHT"
        st.session_state.food = place_food()
        st.session_state.game_over = False
        st.session_state.score = 0

# แสดงคะแนน
st.subheader(f"คะแนน: {st.session_state.score}")

# ---------------- KEYBOARD INPUT (WASD + Arrow Keys) ----------------
# ใช้ text_input Trick รับคีย์แบบ real-time
key = st.text_input("กดปุ่มควบคุม (WASD หรือ Arrow keys)", value="", key="key_input")

key = key.lower()
if key in ["w", "arrowup"] and st.session_state.direction != "DOWN":
    st.session_state.direction = "UP"
elif key in ["s", "arrowdown"] and st.session_state.direction != "UP":
    st.session_state.direction = "DOWN"
elif key in ["a", "arrowleft"] and st.session_state.direction != "RIGHT":
    st.session_state.direction = "LEFT"
elif key in ["d", "arrowright"] and st.session_state.direction != "LEFT":
    st.session_state.direction = "RIGHT"

# ---------------- RENDER BOARD ----------------
bg = BACKGROUNDS[st.session_state.bg]
skin = SKINS[st.session_state.skin]

board = np.zeros((BOARD_SIZE, BOARD_SIZE, 3), dtype=np.uint8)
board[:, :] = bg

# สีงู
for (x, y) in st.session_state.snake:
    board[y, x] = skin

# สีอาหาร
fx, fy = st.session_state.food
board[fy, fx] = [255, 0, 0]

st.image(board, width=400)

# ---------------- GAME LOOP ----------------
if not st.session_state.game_over:
    move_snake()
    time.sleep(st.session_state.speed)
    st.rerun()
else:
    st.write("### ❌ Game Over — กดเริ่มใหม่เพื่อเล่นอีกครั้ง!")
