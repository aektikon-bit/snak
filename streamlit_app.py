import streamlit as st
import numpy as np
import time
import math
import random

# ============================================
# CONFIG
# ============================================
GRID = 15
SCALE = 32       # HD Graphics
FPS = 0.08

# ===== Enemy types =====
ENEMY_TYPES = {
    "normal": {"hp": 12, "speed": 0.22, "color": [255, 80, 80]},
    "fast":   {"hp": 6,  "speed": 0.45, "color": [255, 200, 80]},
    "tank":   {"hp": 28, "speed": 0.16, "color": [160, 80, 255]},
    "armor":  {"hp": 18, "speed": 0.20, "color": [80, 180, 255]},
}

# ===== Tower types =====
TOWER_TYPES = {
    "basic": {"dmg": 3, "range": 3, "rate": 13, "color": [0, 150, 255], "price": 30},
    "rapid": {"dmg": 1, "range": 3, "rate": 6,  "color": [0, 250, 140], "price": 45},
    "sniper": {"dmg": 10, "range": 6, "rate": 25, "color": [255, 50, 50], "price": 60},
    "aoe": {"dmg": 5, "range": 3, "rate": 20, "aoe": True, "price": 80},
    "laser": {"dmg": 1, "range": 5, "rate": 1, "laser": True, "color": [255, 0, 200], "price": 100},
}

# ============================================
# SESSION STATE
# ============================================
if "towers" not in st.session_state:
    st.session_state.towers = []  # (x,y,type, cooldown)
if "bullets" not in st.session_state:
    st.session_state.bullets = []  # bullets in air
if "enemies" not in st.session_state:
    st.session_state.enemies = []
if "money" not in st.session_state:
    st.session_state.money = 80
if "lives" not in st.session_state:
    st.session_state.lives = 12
if "tick" not in st.session_state:
    st.session_state.tick = 0
if "select_tower" not in st.session_state:
    st.session_state.select_tower = "basic"

# enemy path
PATH = [(i, GRID // 2) for i in range(GRID)]

# ============================================
# GAME FUNCTIONS
# ============================================

def spawn_enemy():
    e_type = random.choice(list(ENEMY_TYPES.keys()))
    data = ENEMY_TYPES[e_type]
    st.session_state.enemies.append({
        "x": 0,
        "y": GRID//2,
        "progress": 0,
        "hp": data["hp"],
        "speed": data["speed"],
        "color": data["color"],
        "hit_flash": 0   # animation
    })

def tower_attack():
    for i, (tx, ty, t_type, cd) in enumerate(st.session_state.towers):
        tower = TOWER_TYPES[t_type]

        if cd > 0:
            st.session_state.towers[i] = (tx, ty, t_type, cd - 1)
            continue

        # หาเป้าหมาย
        target = None
        best_dist = 999

        for e in st.session_state.enemies:
            dist = math.dist((tx, ty), (e["x"], e["y"]))
            if dist <= tower["range"] and dist < best_dist:
                target = e
                best_dist = dist

        if target:
            # ยิงตามชนิดป้อม
            if "laser" in tower:
                target["hp"] -= tower["dmg"]
                target["hit_flash"] = 3  # animation
                # beam effect → bullets
                st.session_state.bullets.append({
                    "type": "laser",
                    "sx": tx, "sy": ty,
                    "ex": target["x"], "ey": target["y"],
                    "life": 2
                })
            elif "aoe" in tower:
                for e in st.session_state.enemies:
                    if math.dist((tx, ty), (e["x"], e["y"])) <= 2:
                        e["hp"] -= tower["dmg"]
                        e["hit_flash"] = 3
                st.session_state.bullets.append({
                    "type": "aoe",
                    "x": tx, "y": ty,
                    "life": 3
                })
            else:
                # bullet projectile
                st.session_state.bullets.append({
                    "type": "bullet",
                    "x": tx + 0.5,
                    "y": ty + 0.5,
                    "tx": target["x"] + 0.5,
                    "ty": target["y"] + 0.5,
                    "speed": 0.4,
                    "dmg": tower["dmg"],
                    "life": 40
                })

            st.session_state.towers[i] = (tx, ty, t_type, tower["rate"])


def move_bullets():
    new_bul = []
    for b in st.session_state.bullets:
        if b["type"] == "bullet":
            dx = b["tx"] - b["x"]
            dy = b["ty"] - b["y"]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 0.3:
                # hit target
                for e in st.session_state.enemies:
                    if int(e["x"]) == int(b["tx"]) and int(e["y"]) == int(b["ty"]):
                        e["hp"] -= b["dmg"]
                        e["hit_flash"] = 3
                continue
            b["x"] += dx/dist * b["speed"]
            b["y"] += dy/dist * b["speed"]
            b["life"] -= 1
            if b["life"] > 0:
                new_bul.append(b)

        elif b["type"] in ["laser", "aoe"]:
            b["life"] -= 1
            if b["life"] > 0:
                new_bul.append(b)

    st.session_state.bullets = new_bul


def move_enemies():
    new_list = []
    for e in st.session_state.enemies:
        e["progress"] += e["speed"]
        e["x"] = int(e["progress"])
        if e["hit_flash"] > 0:
            e["hit_flash"] -= 1

        if e["x"] >= GRID:
            st.session_state.lives -= 1
            continue
        if e["hp"] > 0:
            new_list.append(e)
        else:
            st.session_state.money += 4
    st.session_state.enemies = new_list


# ============================================
# RENDER FUNCTIONS
# ============================================

def draw_circle(board, cx, cy, r, col):
    for x in range(cx-r, cx+r):
        for y in range(cy-r, cy+r):
            if 0 <= x < board.shape[1] and 0 <= y < board.shape[0]:
                if (x-cx)**2 + (y-cy)**2 <= r*r:
                    board[y, x] = col


def render_board():
    W = GRID * SCALE
    H = GRID * SCALE
    bd = np.zeros((H, W, 3), dtype=np.uint8)
    bd[:] = [45, 45, 65]

    # draw path
    for x, y in PATH:
        px = x * SCALE
        py = y * SCALE
        bd[py:py+SCALE, px:px+SCALE] = [225, 205, 150]

    # grid
    for i in range(GRID):
        bd[:, i*SCALE:i*SCALE+1] = [80, 80, 100]
        bd[i*SCALE:i*SCALE+1, :] = [80, 80, 100]

    # towers
    for x, y, ttype, cd in st.session_state.towers:
        px, py = x*SCALE, y*SCALE
        color = TOWER_TYPES[ttype]["color"]
        bd[py+8:py+24, px+8:px+24] = color

    # enemies
    for e in st.session_state.enemies:
        cx = int(e["x"]*SCALE + SCALE/2)
        cy = int(e["y"]*SCALE + SCALE/2)
        r = SCALE // 3
        color = e["color"]
        if e["hit_flash"] > 0:
            color = [255, 255, 255]
        draw_circle(bd, cx, cy, r, color)

    # bullets
    for b in st.session_state.bullets:
        if b["type"] == "bullet":
            cx = int(b["x"]*SCALE)
            cy = int(b["y"]*SCALE)
            draw_circle(bd, cx, cy, SCALE//6, [255, 255, 100])

        elif b["type"] == "laser":
            sx = int(b["sx"]*SCALE + SCALE/2)
            sy = int(b["sy"]*SCALE + SCALE/2)
            ex = int(b["ex"]*SCALE + SCALE/2)
            ey = int(b["ey"]*SCALE + SCALE/2)
            # draw laser beam
            cv = bd
            for t in np.linspace(0, 1, 40):
                x = int(sx + (ex-sx)*t)
                y = int(sy + (ey-sy)*t)
                if 0 <= x < cv.shape[1] and 0 <= y < cv.shape[0]:
                    cv[y, x] = [255, 0, 255]

        elif b["type"] == "aoe":
            px = b["x"]*SCALE + SCALE/2
            py = b["y"]*SCALE + SCALE/2
            draw_circle(bd, int(px), int(py), SCALE//2, [255, 150, 0])

    return bd


# ============================================
# UI (Tower Selection)
# ============================================

st.title("🏰 Tower Defense — Ultra Edition")

st.markdown("### 🔥 **Choose your tower**")
tower_row = st.columns(len(TOWER_TYPES))

for i, t in enumerate(TOWER_TYPES.keys()):
    with tower_row[i]:
        if st.button(f"{t}\n💰{TOWER_TYPES[t]['price']}", key=f"btn_{t}"):
            st.session_state.select_tower = t

st.write(f"🎯 เลือกป้อมปัจจุบัน: **{st.session_state.select_tower}**")


# ============================================
# GAME LOOP
# ============================================

board = render_board()
st.image(board, width=500)

col1, col2, col3 = st.columns(3)

with col1:
    st.write(f"💰 เงิน: **{st.session_state.money}**")

with col2:
    st.write(f"❤️ ชีวิต: **{st.session_state.lives}**")

with col3:
    if st.button("🔄 รีเซ็ตเกม"):
        for k in ["towers", "bullets", "enemies", "money", "lives", "tick"]:
            st.session_state[k] = [] if isinstance(st.session_state[k], list) else 0
        st.session_state.money = 80
        st.session_state.lives = 12
        st.rerun()


# spawn enemy every few ticks
if st.session_state.tick % 20 == 0:
    spawn_enemy()

tower_attack()
move_bullets()
move_enemies()

st.session_state.tick += 1

time.sleep(FPS)
st.rerun()
