import streamlit as st
import numpy as np
import time
import math

# ---------------------------------------
# CONFIG
# ---------------------------------------
GRID = 15
CELL = 25
ENEMY_HP = 10
ENEMY_SPEED = 0.25
TOWER_DAMAGE = 3
TOWER_RANGE = 3
MONEY_START = 50

# ---------------------------------------
# INITIAL STATE
# ---------------------------------------
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

# ศัตรูเดินตาม path แนวนอน
PATH = [(i, GRID // 2) for i in range(GRID)]

# ---------------------------------------
# SPAWN ENEMY
# ---------------------------------------
def spawn_enemy():
    st.session_state.enemies.append({
        "x": 0,
        "y": GRID//2,
        "hp": ENEMY_HP,
        "progress": 0
    })

# ---------------------------------------
# MOVE ENEMIES
# ---------------------------------------
def move_enemies():
    for e in st.session_state.enemies:
        e["progress"] += ENEMY_SPEED
        e["x"] = int(e["progress"])

    # ถ้าหลุดจอ -> ลดชีวิต
    leak = [e for e in st.session_state.enemies if e["x"] >= GRID]
    for _ in leak:
        st.session_state.lives -= 1

    st.session_state.enemies = [e for e in st.session_state.enemies if e["x"] < GRID and e["hp"] > 0]

# ---------------------------------------
# TOWER ATTACK
# ---------------------------------------
def tower_attack():
    for tx, ty in st.session_state.towers:
        for e in st.session_state.enemies:
            dist = math.dist((tx, ty), (e["x"], e["y"]))
            if dist <= TOWER_RANGE:
                e["hp"] -= TOWER_DAMAGE

# ---------------------------------------
# GAME OVER
# ---------------------------------------
def reset_game():
    st.session_state.towers = []
    st.session_state.enemies = []
    st.session_state.money = MONEY_START
    st.session_state.lives = 10
    st.session_state.tick = 0

# ---------------------------------------
# UI
# ---------------------------------------
st.title("🏰 Tower Defense — Streamlit Edition")

col1, col2 = st.columns([1, 1])

with col1:
    st.write(f"💰 เงิน: {st.session_state.money}")
    st.write(f"❤️ ชีวิต: {st.session_state.lives}")

    build = st.button("➕ สร้างป้อม (30💰)")
    if build and st.session_state.money >= 30:
        st.session_state.build_mode = True
    else:
        st.session_state.build_mode = False

    if st.button("🔄 เริ่มใหม่"):
        reset_game()

with col2:
    st.write("🎯 วิธีเล่น:")
    st.write("- คลิกช่องเพื่อสร้างป้อม (ใช้เงิน 30)")
    st.write("- ศัตรูเดินจากซ้าย → ขวา")
    st.write("- ป้อมจะยิงอัตโนมัติ")
    st.write("- ป้องกันไม่ให้ศัตรุหลุดจอ")

# ---------------------------------------
# DRAW BOARD
# ---------------------------------------
board = np.zeros((GRID, GRID, 3), dtype=np.uint8)

# พื้นหลัง
board[:] = [50, 50, 50]

# path
for x, y in PATH:
    board[y, x] = [120, 120, 120]

# towers
for x, y in st.session_state.towers:
    board[y, x] = [0, 180, 255]

# enemies
for e in st.session_state.enemies:
    x, y = e["x"], e["y"]
    if 0 <= x < GRID:
        board[y, x] = [255, 60, 60]

# แสดงแผนที่
clicked = st.image(board, width=400)

# ---------------------------------------
# CHECK CLICK (เลือกช่องวางป้อม)
# ---------------------------------------
def place_tower():
    pos = st.session_state.get("clicked_cell", None)
    if pos and st.session_state.money >= 30:
        x, y = pos
        if (x, y) not in PATH and (x, y) not in st.session_state.towers:
            st.session_state.towers.append((x, y))
            st.session_state.money -= 30

# ---------------------------------------
# AUTO GAME LOOP
# ---------------------------------------
if st.session_state.lives > 0:
    st.session_state.tick += 1

    # spawn enemy ทุก 20 tick
    if st.session_state.tick % 20 == 0:
        spawn_enemy()

    tower_attack()
    move_enemies()

    time.sleep(0.1)
    st.rerun()

else:
    st.header("💀 Game Over")
