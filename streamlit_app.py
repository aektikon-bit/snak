import streamlit as st
import numpy as np
import time

# ---------- CONFIG ----------
BOARD_SIZE = 20
SPEED = 0.12     # วินาทีต่อ 1 การขยับ

# ---------- INITIAL STATE ----------
if "snake" not in st.session_state:
    st.session_state.snake = [(10, 10)]
    st.session_state.direction = "RIGHT"
    st.session_state.food = (5, 5)
    st.session_state.game_over = False

# ---------- GAME LOGIC ----------
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

    # ชนกำแพงหรือชนตัวเอง = จบเกม
    if (
        new_head[0] < 0 or new_head[0] >= BOARD_SIZE or
        new_head[1] < 0 or new_head[1] >= BOARD_SIZE or
        new_head in st.session_state.snake
    ):
        st.session_state.game_over = True
        return

    # ตรวจอาหาร
    if new_head == st.session_state.food:
        st.session_state.snake = [new_head] + st.session_state.snake
        st.session_state.food = place_food()
    else:
        st.session_state.snake = [new_head] + st.session_state.snake[:-1]

# ---------- UI ----------
st.title("🐍 Snake Game ด้วย Streamlit")

col1, col2, col3 = st.columns([1,1,1])

with col2:
    if st.button("🔄 เริ่มใหม่"):
        st.session_state.snake = [(10,10)]
        st.session_state.direction = "RIGHT"
        st.session_state.food = place_food()
        st.session_state.game_over = False

# ปุ่มควบคุมทิศทาง
up = st.button("⬆ UP")
left, right = st.columns(2)
down = st.button("⬇ DOWN")

if up:
    st.session_state.direction = "UP"
if down:
    st.session_state.direction = "DOWN"
if left:
    st.session_state.direction = "LEFT"
if right:
    st.session_state.direction = "RIGHT"

# ---------- RENDER GAME BOARD ----------
board = np.zeros((BOARD_SIZE, BOARD_SIZE, 3), dtype=np.uint8)

# งู (สีเขียว)
for (x, y) in st.session_state.snake:
    board[y, x] = [0, 255, 0]

# อาหาร (สีแดง)
fx, fy = st.session_state.food
board[fy, fx] = [255, 0, 0]

# แสดงกระดาน
st.image(board, width=400)

# ---------- AUTO UPDATE ----------
if not st.session_state.game_over:
    move_snake()
    time.sleep(SPEED)
    st.rerun()
else:
    st.write("### ❌ Game Over")
