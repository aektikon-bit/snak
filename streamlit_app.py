# tower_ultimate.py
import streamlit as st
import numpy as np
import time, random, math, base64

# ======================================
# CONFIGURATION
# ======================================
GRID = 15
SCALE = 32
FPS = 0.08

# ======================================
# GAME STATE
# ======================================
if "tick" not in st.session_state: st.session_state.tick = 0
if "money" not in st.session_state: st.session_state.money = 80
if "lives" not in st.session_state: st.session_state.lives = 12
if "towers" not in st.session_state: st.session_state.towers = []
if "bullets" not in st.session_state: st.session_state.bullets = []
if "enemies" not in st.session_state: st.session_state.enemies = []
if "select_tower" not in st.session_state: st.session_state.select_tower = "basic"
if "inventory" not in st.session_state: st.session_state.inventory = []
if "hero" not in st.session_state: st.session_state.hero = {"x":7,"y":7,"hp":50,"level":1,"cd":0}
if "passives" not in st.session_state: st.session_state.passives = {"gold_bonus":0.1,"tower_dmg":1.2}
if "techs" not in st.session_state: st.session_state.techs = []

# ======================================
# ENEMIES / BOSSES
# ======================================
ENEMY_TYPES = {
    "normal": {"hp":12,"speed":0.22,"color":[255,80,80]},
    "fast": {"hp":6,"speed":0.45,"color":[255,200,80]},
    "tank": {"hp":28,"speed":0.16,"color":[160,80,255]},
    "armor":{"hp":18,"speed":0.20,"color":[80,180,255]},
}

BOSS_TYPES = {
    "stone_giant":{"hp":400,"speed":0.12,"size":1.5,"color":[120,120,255],"ability":"shockwave"}
}

PATH = [(i, GRID//2) for i in range(GRID)]

# ======================================
# TOWER TYPES
# ======================================
TOWER_TYPES = {
    "basic":[{"dmg":3,"range":3,"rate":13,"price":30},
             {"dmg":5,"range":3,"rate":10,"price":40},
             {"dmg":8,"range":4,"rate":7,"price":60}],
    "rapid":[{"dmg":1,"range":3,"rate":6,"price":45},
             {"dmg":2,"range":3,"rate":5,"price":60},
             {"dmg":3,"range":4,"rate":4,"price":80}],
    "sniper":[{"dmg":10,"range":6,"rate":25,"price":60},
              {"dmg":16,"range":7,"rate":22,"price":80},
              {"dmg":25,"range":8,"rate":18,"price":120}],
    "aoe":[{"dmg":5,"range":3,"rate":20,"aoe":True,"price":80},
           {"dmg":8,"range":3,"rate":17,"aoe":True,"price":110},
           {"dmg":12,"range":4,"rate":14,"aoe":True,"price":150}],
    "laser":[{"dmg":1,"range":5,"rate":1,"laser":True,"color":[255,0,200],"price":100},
             {"dmg":2,"range":5,"rate":1,"laser":True,"color":[255,0,200],"price":130},
             {"dmg":3,"range":6,"rate":1,"laser":True,"color":[255,0,200],"price":180}]
}

# ======================================
# UTILITY FUNCTIONS
# ======================================
def draw_circle(board,cx,cy,r,col):
    for x in range(cx-r,cx+r):
        for y in range(cy-r,cy+r):
            if 0<=x<board.shape[1] and 0<=y<board.shape[0]:
                if (x-cx)**2+(y-cy)**2<=r*r: board[y,x]=col

def play_music(path):
    audio_file = open(path,'rb').read()
    encoded = base64.b64encode(audio_file).decode()
    st.markdown(f"""
        <audio autoplay loop>
        <source src="data:audio/mp3;base64,{encoded}" type="audio/mp3">
        </audio>""",unsafe_allow_html=True)

def play_sfx(path):
    audio_file = open(path,'rb').read()
    encoded = base64.b64encode(audio_file).decode()
    st.markdown(f"<audio autoplay><source src='data:audio/wav;base64,{encoded}'></audio>",unsafe_allow_html=True)

# ======================================
# SPAWN ENEMIES
# ======================================
def spawn_enemy():
    e_type = random.choice(list(ENEMY_TYPES.keys()))
    data = ENEMY_TYPES[e_type]
    st.session_state.enemies.append({"x":0,"y":GRID//2,"progress":0,"hp":data["hp"],"speed":data["speed"],"color":data["color"],"hit_flash":0})

# ======================================
# HERO ACTIONS
# ======================================
def move_hero(dx,dy):
    hero = st.session_state.hero
    hero["x"] = max(0,min(GRID-1,hero["x"]+dx))
    hero["y"] = max(0,min(GRID-1,hero["y"]+dy))

# ======================================
# TOWER ATTACK
# ======================================
def tower_attack():
    for i,(tx,ty,ttype,cd,level) in enumerate(st.session_state.towers):
        tower = TOWER_TYPES[ttype][level-1]
        if cd>0:
            st.session_state.towers[i]=(tx,ty,ttype,cd-1,level)
            continue
        target=None
        best_dist=999
        for e in st.session_state.enemies:
            dist=math.dist((tx,ty),(e["x"],e["y"]))
            if dist<=tower["range"] and dist<best_dist: target=e; best_dist=dist
        if target:
            # laser/aoe/bullet
            if "laser" in tower:
                target["hp"]-=tower["dmg"]
                target["hit_flash"]=3
                st.session_state.bullets.append({"type":"laser","sx":tx,"sy":ty,"ex":target["x"],"ey":target["y"],"life":2})
            elif "aoe" in tower:
                for e in st.session_state.enemies:
                    if math.dist((tx,ty),(e["x"],e["y"]))<=2: e["hp"]-=tower["dmg"]; e["hit_flash"]=3
                st.session_state.bullets.append({"type":"aoe","x":tx,"y":ty,"life":3})
            else:
                st.session_state.bullets.append({"type":"bullet","x":tx+0.5,"y":ty+0.5,"tx":target["x"]+0.5,"ty":target["y"]+0.5,"speed":0.4,"dmg":tower["dmg"],"life":40})
            st.session_state.towers[i]=(tx,ty,ttype,tower["rate"],level)

# ======================================
# MOVE BULLETS
# ======================================
def move_bullets():
    new_bul=[]
    for b in st.session_state.bullets:
        if b["type"]=="bullet":
            dx=b["tx"]-b["x"]
            dy=b["ty"]-b["y"]
            dist=math.sqrt(dx*dx+dy*dy)
            if dist<0.3:
                for e in st.session_state.enemies:
                    if int(e["x"])==int(b["tx"]) and int(e["y"])==int(b["ty"]): e["hp"]-=b["dmg"]; e["hit_flash"]=3
                continue
            b["x"]+=dx/dist*b["speed"]
            b["y"]+=dy/dist*b["speed"]
            b["life"]-=1
            if b["life"]>0: new_bul.append(b)
        elif b["type"] in ["laser","aoe"]:
            b["life"]-=1
            if b["life"]>0: new_bul.append(b)
    st.session_state.bullets=new_bul

# ======================================
# MOVE ENEMIES
# ======================================
def move_enemies():
    new_list=[]
    for e in st.session_state.enemies:
        e["progress"]+=e["speed"]
        e["x"]=int(e["progress"])
        if e["hit_flash"]>0: e["hit_flash"]-=1
        if e["x"]>=GRID:
            st.session_state.lives-=1
            continue
        if e["hp"]>0: new_list.append(e)
        else: st.session_state.money+=int(4*(1+st.session_state.passives["gold_bonus"]))
    st.session_state.enemies=new_list

# ======================================
# RENDER BOARD
# ======================================
def render_board():
    W,H=GRID*SCALE,GRID*SCALE
    bd=np.zeros((H,W,3),dtype=np.uint8); bd[:]=[45,45,65]
    # path
    for x,y in PATH:
        px,py=x*SCALE,y*SCALE; bd[py:py+SCALE,px:px+SCALE]=[225,205,150]
    # grid lines
    for i in range(GRID):
        bd[:,i*SCALE:i*SCALE+1]=[80,80,100]; bd[i*SCALE:i*SCALE+1,:]=[80,80,100]
    # towers
    for x,y,ttype,cd,level in st.session_state.towers:
        px,py=x*SCALE,y*SCALE; color=TOWER_TYPES[ttype][level-1]["color"] if "color" in TOWER_TYPES[ttype][level-1] else [0,150,255]
        bd[py+8:py+24,px+8:px+24]=color
    # enemies
    for e in st.session_state.enemies:
        cx=int(e["x"]*SCALE+SCALE/2); cy=int(e["y"]*SCALE+SCALE/2); r=SCALE//3; color=e["color"]
        if e["hit_flash"]>0: color=[255,255,255]
        draw_circle(bd,cx,cy,r,color)
    # bullets
    for b in st.session_state.bullets:
        if b["type"]=="bullet": draw_circle(bd,int(b["x"]*SCALE),int(b["y"]*SCALE),SCALE//6,[255,255,100])
        elif b["type"]=="laser":
            sx=int(b["sx"]*SCALE+SCALE/2); sy=int(b["sy"]*SCALE+SCALE/2)
            ex=int(b["ex"]*SCALE+SCALE/2); ey=int(b["ey"]*SCALE+SCALE/2)
            for t in np.linspace(0,1,40):
                x=int(sx+(ex-sx)*t); y=int(sy+(ey-sy)*t)
                if 0<=x<bd.shape[1] and 0<=y<bd.shape[0]: bd[y,x]=[255,0,255]
        elif b["type"]=="aoe": draw_circle(bd,int(b["x"]*SCALE+SCALE/2),int(b["y"]*SCALE+SCALE/2),SCALE//2,[255,150,0])
    # hero
    hero=st.session_state.hero
    draw_circle(bd,hero["x"]*SCALE+SCALE//2,hero["y"]*SCALE+SCALE//2,SCALE//2,[0,255,255])
    return bd

# ======================================
# UI
# ======================================
st.title("🏰 Tower Ultimate Defense — Mega Edition")

st.markdown("### 🔥 เลือกป้อม / ซื้อ / อัปเกรด / Hero")
cols=st.columns(len(TOWER_TYPES))
for i,ttype in enumerate(TOWER_TYPES.keys()):
    with cols[i]:
        price=TOWER_TYPES[ttype][0]["price"]
        if st.button(f"{ttype}\n💰{price}",key=f"btn_{ttype}"):
            st.session_state.select_tower=ttype

st.write(f"🎯 ป้อมที่เลือก: **{st.session_state.select_tower}**")
st.write(f"💰 เงิน: {st.session_state.money} ❤️ ชีวิต: {st.session_state.lives} 💠 Hero HP: {st.session_state.hero['hp']}")

# Hero control
hero_col1,hero_col2,hero_col3=st.columns(3)
with hero_col1:
    if st.button("⬆️"): move_hero(0,-1)
with hero_col2:
    if st.button("⬅️"): move_hero(-1,0)
    if st.button("➡️"): move_hero(1,0)
with hero_col3:
    if st.button("⬇️"): move_hero(0,1)

# Spawn enemy
if st.session_state.tick%20==0: spawn_enemy()

# Tower attack / move bullets / move enemies
tower_attack()
move_bullets()
move_enemies()

# Render board
board=render_board()
st.image(board,width=500)

st.session_state.tick+=1
time.sleep(FPS)
st.rerun()
