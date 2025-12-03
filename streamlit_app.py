import streamlit as st
import numpy as np
import time
import math

# -----------------------------------------
# CONFIG
# -----------------------------------------
GRID = 15
SCALE = 30  # upscale เพื่อความคมชัด
ENEMY_HP = 10
ENEMY_SPEED = 0.25
TOWER_DAMAGE = 3
TOWER_RANGE = 3
MONEY_START = 50

# -----------------------------------------
# STATE
# -----------------------------------------
if "towers" not in st.session_state:
    st.session_state.towers = []
if "enemies" not in st.session_state:
    st.session_state.enemies = []
if "money" not in st.session_state:
    st.session_state.money = MONEY_START
if "lives" not in st.session_state:
    st.session_state.lives = 10
if "tick" not in st.session_state:
    st.session_state.tick = 0

PATH = [(i, GRID // 2) for i in range(GRID)]

# -----------------------------------------
# GAME FUNCTIONS
# -----------------------------------------
def spawn_enemy():
    st.session_state.enemies.append({
        "x": 0,
        "y": GRID//2,
        "hp": ENEMY_HP,
        "progress": 0
    })


def move_enemies():
    for e in st.session_state.enemies:
        e["progress"] += ENEMY_SPEED
        e["x"] = int(e["progress"])

    leak = [e for e in st.session_state.enemies if e["x"] >= GRID]
    for _ in leak:
        st.session_state.lives -= 1

    st.session_state.enemies = [e for e in st.session_state.enemies if e["x"] < GRID and e["hp"] > 0]


def tower_attack():
    for tx, ty in st.session_state.towers:
        for e in st.session_state.enemies:
            dist = math.dist((tx, ty), (e["x"], e["y"]))
            if dist <= TOWER_RANGE:
                e["hp"] -= TOWER_DAMAGE


def reset_game():
    st.session_state.towers = []
    st.session_state.enemies = []
    st.session_state.money = MONEY_START
    st.session_state.lives = 10
    st.session_state.tick = 0


# -----------------------------------------
# GRAPHIC FUNCTIONS (HD GRID)
# -----------------------------------------
def draw_circle(board, cx, cy, r, color):
    """วาดวงกลม HD (ศัตรู)"""
    for x in range(cx - r, cx + r):
        for y in range(cy - r, cy + r):
            if (x - cx)**2 + (y - cy)**2 <= r*r:
                board[y, x] = color


def draw_tower(board, x, y):
    """วาดป้อมแบบ icon (สี่เหลี่ยม + หลังคา)"""
    px = x * SCALE
    py = y * SCALE

    # ตัวป้อม
    board[py+8:py+22, px+8:px+22] = [0, 150, 255]

    # หลังคา
    board[py+5:py+12, px+12:px+18] = [0, 90, 200]

    # เงาเล็ก ๆ
    board[py+22:py+26, px+10:px+20] = [20, 20, 40]


def draw_enemy(board, ex, ey):
    """วาดศัตรูแบบวงกลมแดง"""
    cx = int(ex * SCALE + SCALE/2)
    cy = int(ey * SCALE + SCALE/2)
    radius = SCALE // 3
    draw_circle(board, cx, cy, radius, [255, 70, 70])


def render_board():
    board = np.zeros((GRID * SCALE, GRID * SCALE, 3), dtype=np.uint8)
    board[:] = [40, 40, 60]  # พื้นหลัง

    # Path สีครีม
    for x, y in PATH:
        px = x * SCALE
        py = y * SCALE
        board[py:py+SCALE, px:px+SCALE] = [220, 200, 150]

    # Grid เส้นบาง ๆ
    for i in range(GRID):
        board[:, i*SCALE:i*SCALE+1] = [80, 80, 100]
        board[i*SCALE:i*SCALE+1, :] = [80, 80, 100]

    # Towers
    for x, y in st.session_state.towers:
        draw_tower(board, x, y)

    # Enemies
    for e in st.session_state.enemies:
        if 0 <= e["x"] < GRID:
            draw_enemy(board, e["x"], e["y"])

    return board


# -----------------------------------------
# UI
# -----------------------------------------
st.title("🏰 Tower Defense — HD Graphics Edition")

col1, col2 = st.columns([1, 1])

with col1:
    st.write(f"💰 เงิน: **{st.session_state.money}**")
    st.write(f"❤️ ชีวิต: **{st.session_state.lives}**")

with col2:
    if st.button("🔄 เริ่มใหม่"):
        reset_game()


# -----------------------------------------
# GAME LOOP
# -----------------------------------------
if st.session_state.lives > 0:
    st.session_state.tick += 1

    if st.session_state.tick % 20 == 0:
        spawn_enemy()

    tower_attack()
    move_enemies()

    board = render_board()
    st.image(board, width=450)

    time.sleep(0.10)
    st.rerun()

else:
    st.image(render_board(), width=450)
    st.header("💀 Game Over — ลองใหม่อีกครั้ง!")
