"""
╔══════════════════════════════════════════════════════════╗
║        ULTIMATE 3D SNAKE  —  v3.1  AUTOPILOT            ║
║  pip install pygame   →   python snake_ultimate.py       ║
║  Press F in-game to toggle AI autopilot (cheat mode)!   ║
╚══════════════════════════════════════════════════════════╝
"""

import pygame, sys, math, random, time, struct
from collections import deque

# ─────────────────────────────────────────────────────────
#  SAFE INIT
# ─────────────────────────────────────────────────────────
pygame.init()

_AUDIO = False
try:
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.mixer.init()
    _AUDIO = True
except Exception:
    pass

WIDTH, HEIGHT = 820, 580
PANEL_W = 190
GAME_W = WIDTH - PANEL_W
GAME_H        = HEIGHT
CELL          = 20
COLS          = GAME_W  // CELL
ROWS          = GAME_H  // CELL

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ultimate 3D Snake")
except Exception as e:
    print(f"Display error: {e}"); sys.exit(1)

clock = pygame.time.Clock()

# ─────────────────────────────────────────────────────────
#  FONTS
# ─────────────────────────────────────────────────────────
def safe_font(names, size, bold=False):
    for n in names:
        try:
            f = pygame.font.SysFont(n, size, bold=bold)
            if f: return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

F_HUGE = safe_font(["consolas","couriernew","monospace"], 62, True)
F_BIG  = safe_font(["consolas","couriernew","monospace"], 36, True)
F_MED  = safe_font(["consolas","couriernew","monospace"], 24)
F_SM   = safe_font(["consolas","couriernew","monospace"], 16)
F_XS   = safe_font(["consolas","couriernew","monospace"], 13)

# ─────────────────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────────────────
BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
GRAY     = (110, 110, 120)
DGRAY    = (38,  38,  50)
DARK_BG  = (8,   10,  18)
PANEL_BG = (11,  13,  22)
GRID_C   = (19,  22,  38)
GOLD     = (255, 210, 0)
CYAN     = (0,   215, 255)
ORANGE   = (255, 140, 0)
PURPLE   = (160, 55,  220)
AUTO_COL = (0,   255, 180)   # autopilot indicator color

# ─────────────────────────────────────────────────────────
#  AUDIO  — pure-Python PCM, zero external deps
# ─────────────────────────────────────────────────────────
_SND = {}

def _build_sound(freq, dur, vol=0.25):
    if not _AUDIO:
        return None
    try:
        sr = 22050
        n  = int(sr * dur)
        fd = max(1, int(sr * 0.013))
        ba = bytearray(n * 2)
        for i in range(n):
            v   = math.sin(2 * math.pi * freq * i / sr)
            env = min(1.0, min(i+1, n-i) / fd)
            s   = max(-32768, min(32767, int(v * env * vol * 32767)))
            struct.pack_into("<h", ba, i*2, s)
        return pygame.mixer.Sound(buffer=bytes(ba))
    except Exception:
        return None

def _load_sounds():
    defs = {"eat":(900,0.07,0.28),"die":(110,0.30,0.45),"powerup":(660,0.14,0.30),
            "levelup":(523,0.12,0.32),"combo":(750,0.08,0.26),
            "shield":(330,0.12,0.28),"menu":(440,0.06,0.18),
            "auto_on":(880,0.18,0.30),"auto_off":(440,0.14,0.25)}
    for k,(f,d,v) in defs.items():
        _SND[k] = _build_sound(f, d, v)

_load_sounds()

def sfx(name):
    s = _SND.get(name)
    if s:
        try: s.play()
        except Exception: pass

# ─────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────
def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def hsv(h, s, v):
    i=int(h*6); f=h*6-i
    p=v*(1-s); q=v*(1-f*s); t_=v*(1-(1-f)*s)
    r,g,b=[(v,t_,p),(q,v,p),(p,v,t_),(p,q,v),(t_,p,v),(v,p,q)][i%6]
    return (int(r*255),int(g*255),int(b*255))

def clamp(v,lo,hi): return max(lo,min(hi,v))

UP=(0,-1); DOWN=(0,1); LEFT=(-1,0); RIGHT=(1,0)
ALL_DIRS = [UP, DOWN, LEFT, RIGHT]
OPPOSITE = {UP:DOWN, DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}

# ─────────────────────────────────────────────────────────
#  SKINS
# ─────────────────────────────────────────────────────────
SKINS=[
    {"name":"Classic","tail":(0,90,55),  "head":(55,215,75), "req":0},
    {"name":"Ocean",  "tail":(0,55,150), "head":(35,170,255),"req":2},
    {"name":"Royal",  "tail":(75,0,150), "head":(170,55,255),"req":3},
    {"name":"Lava",   "tail":(140,20,0), "head":(255,85,15), "req":4},
    {"name":"Golden", "tail":(155,115,0),"head":(255,215,0), "req":5},
    {"name":"Ghost",  "tail":(75,75,95), "head":(195,195,215),"req":7},
    {"name":"Void",   "tail":(10,10,18), "head":(55,35,75),  "req":8},
    {"name":"Fire",   "tail":(155,28,0), "head":(255,175,0), "req":9},
    {"name":"Diamond","tail":(0,175,215),"head":(175,235,255),"req":10},
    {"name":"Rainbow","tail":None,       "head":None,         "req":6},
]

def seg_color(si, t, idx=0, total=1):
    s=SKINS[si]
    if s["name"]=="Rainbow":
        return hsv((idx/max(total,1)+time.time()*0.45)%1.0, 0.82, 0.95)
    return lerp(s["tail"], s["head"], t)

# ─────────────────────────────────────────────────────────
#  MAZE
# ─────────────────────────────────────────────────────────
def build_maze(lid, cols, rows):
    W=set(); cx,cy=cols//2,rows//2
    safe={(cx+dx,cy+dy) for dx in range(-4,5) for dy in range(-4,5)}
    if lid==0:
        for x in range(4,cols-4): W.add((x,cy))
        for y in range(3,rows-3): W.add((cx,y))
    elif lid==1:
        for bx,by in [(5,3),(cols-10,3),(5,rows-7),(cols-10,rows-7)]:
            for x in range(bx,bx+5):
                for y in range(by,by+4): W.add((x,y))
    elif lid==2:
        for x in range(3,cols-3): W.add((x,4)); W.add((x,rows-5))
        for y in range(4,rows-4): W.add((3,y)); W.add((cols-4,y))
        for g in range(cx-3,cx+4): W.discard((g,4)); W.discard((g,rows-5))
        for g in range(cy-3,cy+4): W.discard((3,g)); W.discard((cols-4,g))
    elif lid==3:
        for x in range(4,cols-4,5):
            for y in range(4,rows-4,4): W.add((x,y)); W.add((x+1,y))
    elif lid==4:
        for i in range(min(cols,rows)-4):
            W.add((i+2,i+2)); W.add((cols-3-i,i+2))
    W-=safe
    return {(x,y) for x,y in W if 0<=x<cols and 0<=y<rows}

# ─────────────────────────────────────────────────────────
#  DRAWING
# ─────────────────────────────────────────────────────────
_scan_surf = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
for _y in range(0,HEIGHT,2):
    pygame.draw.line(_scan_surf,(0,0,0,50),(0,_y),(WIDTH,_y))

_STARS=[(random.randint(0,GAME_W-1),random.randint(0,GAME_H-1),
         random.uniform(0.3,1.0)) for _ in range(90)]

_A = pygame.Surface((GAME_W,GAME_H), pygame.SRCALPHA)

def draw_stars(surf, tick):
    for sx,sy,br in _STARS:
        c=clamp(int(255*br*(0.6+0.4*math.sin(tick*0.04+sx))),0,255)
        surf.set_at((sx,sy),(c,c,min(255,c+22)))

def draw_cube(surf, x, y, size, base, head=False, glow=False, gcol=WHITE, bob=0):
    d=size//4; s=size-2; y=y+int(bob)
    top_c=lerp(base,WHITE,0.40); rgt_c=lerp(base,BLACK,0.42); rim_c=lerp(base,BLACK,0.65)
    top=[(x+1,y+1),(x+1+d,y+1-d),(x+s+d,y+1-d),(x+s,y+1)]
    rgt=[(x+s,y+1),(x+s+d,y+1-d),(x+s+d,y+s-d),(x+s,y+s)]
    fr=pygame.Rect(x+1,y+1,s-1,s-1)
    if glow:
        gs=pygame.Surface((size+14,size+14),pygame.SRCALPHA)
        pygame.draw.rect(gs,(*gcol,38),(0,0,size+14,size+14),border_radius=5)
        surf.blit(gs,(x-7,y-7))
    pygame.draw.polygon(surf,top_c,top)
    pygame.draw.polygon(surf,rgt_c,rgt)
    pygame.draw.rect(surf,base,fr)
    pygame.draw.polygon(surf,rim_c,top,1)
    pygame.draw.polygon(surf,rim_c,rgt,1)
    pygame.draw.rect(surf,rim_c,fr,1)
    if head:
        ex=x+s//3; ey=y+s//3
        pygame.draw.circle(surf,WHITE,(ex,ey),3)
        pygame.draw.circle(surf,WHITE,(ex+s//3,ey),3)
        pygame.draw.circle(surf,BLACK,(ex,ey),1)
        pygame.draw.circle(surf,BLACK,(ex+s//3,ey),1)
        if int(time.time()*4)%4<2:
            tx=x+s//2; ty=y+s-2+int(bob)
            pygame.draw.line(surf,(210,28,28),(tx,ty),(tx-3,ty+6),1)
            pygame.draw.line(surf,(210,28,28),(tx,ty),(tx+3,ty+6),1)

def draw_apple(surf, cx, cy, radius, tick, color=(215,38,38), ring=1.0):
    pulse=1.0+0.07*math.sin(tick*0.12)
    r=max(3,int(radius*pulse))
    dark=lerp(color,BLACK,0.58); brite=lerp(color,WHITE,0.48)
    pygame.draw.ellipse(surf,(14,14,26),(cx-r+4,cy+r-3,r*2,max(2,r//2)))
    steps=min(r,12)
    for i in range(steps,0,-1):
        c=lerp(color,dark,(1-i/steps)*0.5)
        pygame.draw.circle(surf,c,(cx,cy),max(1,int(r*i/steps)))
    hr=max(1,r//3); hx,hy=cx-r//3,cy-r//3
    pygame.draw.circle(surf,brite,(hx,hy),hr)
    pygame.draw.circle(surf,lerp(brite,color,0.5),(hx,hy),max(1,hr-1))
    pygame.draw.line(surf,(55,28,0),(cx,cy-r),(cx+3,cy-r-5),2)
    if ring<1.0:
        span=2*math.pi*ring; a0=-math.pi/2; segs=max(2,int(span*18)); pts=[]
        for i in range(segs+1):
            a=a0+span*(i/segs)
            pts.append((int(cx+(r+4)*math.cos(a)),int(cy+(r+4)*math.sin(a))))
        if len(pts)>=2: pygame.draw.lines(surf,GOLD,False,pts,2)

def draw_gem(surf, cx, cy, pu, tick):
    PC={"speed":GOLD,"slow":CYAN,"ghost":PURPLE,"double":ORANGE,
        "shield":(0,215,175),"shrink":(195,75,75)}
    PL={"speed":"SPD","slow":"SLW","ghost":"GHO","double":"x2","shield":"SHD","shrink":"SHK"}
    col=PC.get(pu,WHITE); r=clamp(int(9*(1.0+0.14*math.sin(tick*0.15))),5,14)
    gs=pygame.Surface((r*4,r*4),pygame.SRCALPHA)
    pygame.draw.circle(gs,(*col,45),(r*2,r*2),r*2); surf.blit(gs,(cx-r*2,cy-r*2))
    pygame.draw.circle(surf,lerp(col,WHITE,0.28),(cx,cy),r)
    pygame.draw.circle(surf,lerp(col,BLACK,0.18),(cx,cy),r,2)
    lbl=F_XS.render(PL.get(pu,"?"),True,BLACK); surf.blit(lbl,lbl.get_rect(center=(cx,cy)))

def draw_bar(surf,x,y,w,h,pct,fg,bg=DGRAY,lbl=""):
    pygame.draw.rect(surf,bg,(x,y,w,h),border_radius=3)
    fw=int(w*clamp(pct,0,1))
    if fw>0: pygame.draw.rect(surf,fg,(x,y,fw,h),border_radius=3)
    pygame.draw.rect(surf,(50,52,70),(x,y,w,h),1,border_radius=3)
    if lbl: surf.blit(F_XS.render(lbl,True,WHITE),(x+3,y+1))

def draw_box(surf,x,y,w,h,title=""):
    pygame.draw.rect(surf,PANEL_BG,(x,y,w,h),border_radius=5)
    pygame.draw.rect(surf,(38,42,65),(x,y,w,h),1,border_radius=5)
    if title: surf.blit(F_XS.render(title,True,GRAY),(x+6,y+4))

def draw_minimap(surf,px,py,mw,mh,snake,food,walls,enemies):
    pygame.draw.rect(surf,(13,16,28),(px,py,mw,mh))
    pygame.draw.rect(surf,DGRAY,(px,py,mw,mh),1)
    xs=mw/COLS; ys=mh/ROWS
    for wx,wy in walls:
        pygame.draw.rect(surf,(55,45,75),(px+int(wx*xs),py+int(wy*ys),max(1,int(xs)),max(1,int(ys))))
    fx,fy=food
    pygame.draw.rect(surf,(215,55,55),(px+int(fx*xs),py+int(fy*ys),3,3))
    for i,(bx,by) in enumerate(snake):
        c=(55,215,75) if i==0 else (0,135,55)
        pygame.draw.rect(surf,c,(px+int(bx*xs),py+int(by*ys),max(1,int(xs)),max(1,int(ys))))
    for e in enemies:
        pygame.draw.rect(surf,(255,55,55),(px+int(e.x*xs),py+int(e.y*ys),3,3))

# ─────────────────────────────────────────────────────────
#  PARTICLES
# ─────────────────────────────────────────────────────────
class Particle:
    __slots__=["x","y","vx","vy","col","life","ml","sz"]
    def __init__(self,x,y,col):
        a=random.uniform(0,2*math.pi); sp=random.uniform(1.5,5.0)
        self.x=float(x); self.y=float(y)
        self.vx=math.cos(a)*sp; self.vy=math.sin(a)*sp-random.uniform(0.5,2.5)
        self.col=col; self.life=random.randint(20,45); self.ml=self.life
        self.sz=random.randint(2,5)
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=0.14; self.vx*=0.97; self.life-=1
    def draw(self,surf):
        if self.life<=0: return
        a=int(255*self.life/self.ml); c=lerp(self.col,BLACK,1-self.life/self.ml)
        sz=self.sz; s=pygame.Surface((sz*2,sz*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(*c,a),(sz,sz),sz); surf.blit(s,(int(self.x)-sz,int(self.y)-sz))

class FloatText:
    def __init__(self,x,y,txt,col):
        self.x=float(x); self.y=float(y); self.txt=txt; self.col=col; self.life=55; self.ml=55
    def update(self): self.y-=1.1; self.life-=1
    def draw(self,surf):
        if self.life<=0: return
        s=F_MED.render(self.txt,True,self.col); s.set_alpha(int(255*self.life/self.ml))
        surf.blit(s,s.get_rect(center=(int(self.x),int(self.y))))

# ─────────────────────────────────────────────────────────
#  ENEMY
# ─────────────────────────────────────────────────────────
class Enemy:
    def __init__(self,x,y): self.x=x; self.y=y; self.timer=0
    def update(self,hx,hy,walls,ss,score):
        spd=max(6,14-score//5); self.timer+=1
        if self.timer<spd: return
        self.timer=0; best=None; bd=9999
        for dx,dy in (UP,DOWN,LEFT,RIGHT):
            nx,ny=self.x+dx,self.y+dy
            if (nx,ny) in walls or (nx,ny) in ss: continue
            if not(0<=nx<COLS and 0<=ny<ROWS): continue
            d=abs(nx-hx)+abs(ny-hy)
            if d<bd: bd=d; best=(nx,ny)
        if best: self.x,self.y=best
    def draw(self,surf,tick):
        p=abs(math.sin(tick*0.1)); c=lerp((175,18,18),(255,75,75),p)
        draw_cube(surf,self.x*CELL,self.y*CELL,CELL,c,glow=True,gcol=(255,38,38))

# ─────────────────────────────────────────────────────────
#  FOOD TYPES
# ─────────────────────────────────────────────────────────
FOODS=[{"name":"apple","pts":1,"col":(215,38,38),"w":70,"ttl":None},
       {"name":"orange","pts":3,"col":(255,138,0),"w":18,"ttl":8.0},
       {"name":"grape","pts":5,"col":(155,55,215),"w":8,"ttl":6.0},
       {"name":"star","pts":10,"col":(255,215,0),"w":4,"ttl":4.0}]

def rand_food():
    total=sum(f["w"] for f in FOODS); r=random.uniform(0,total)
    for f in FOODS:
        r-=f["w"]
        if r<=0: return f
    return FOODS[0]

# ─────────────────────────────────────────────────────────
#  AUTOPILOT — BFS pathfinding + smart target selection
# ─────────────────────────────────────────────────────────
# Powerup priority: beneficial ones to grab, bad ones to avoid
GOOD_PU  = {"speed", "double", "shield", "ghost"}
BAD_PU   = {"slow", "shrink"}

def _step(pos, d, wrap, cols, rows):
    """Apply one step in direction d, wrapping if needed. Returns None if OOB."""
    nx, ny = pos[0]+d[0], pos[1]+d[1]
    if wrap:
        return (nx % cols, ny % rows)
    if 0 <= nx < cols and 0 <= ny < rows:
        return (nx, ny)
    return None  # out of bounds — wall kill

def bfs(start, goals, blocked, cols, rows, wrap=False):
    """BFS from start toward any goal. Returns first-step direction or None."""
    if not goals: return None
    goal_set = set(goals)
    visited = {start}
    q = deque()
    for d in ALL_DIRS:
        nxt = _step(start, d, wrap, cols, rows)
        if nxt is None: continue
        if nxt in blocked: continue
        if nxt not in visited:
            visited.add(nxt)
            q.append((nxt, d))
    while q:
        pos, first_d = q.popleft()
        if pos in goal_set:
            return first_d
        for d in ALL_DIRS:
            nxt = _step(pos, d, wrap, cols, rows)
            if nxt is None: continue
            if nxt in blocked or nxt in visited: continue
            visited.add(nxt)
            q.append((nxt, d))
    return None

def flood_fill_size(start, blocked, cols, rows, wrap=False):
    """Count cells reachable from start without crossing blocked."""
    if start in blocked: return 0
    visited = {start}; q = deque([start])
    while q:
        pos = q.popleft()
        for d in ALL_DIRS:
            nxt = _step(pos, d, wrap, cols, rows)
            if nxt is None: continue
            if nxt in blocked or nxt in visited: continue
            visited.add(nxt); q.append(nxt)
    return len(visited)

def autopilot_dir(snake, food, walls, puf, bonus, enemies, mode, effects, shields, current_dir):
    """
    Choose safest next direction for the snake using BFS + flood-fill safety check.

    Key correctness rules:
    - blocked = walls | FULL body | enemies  (conservative: never assume tail frees up)
    - _step() handles portal wrapping identically to the game engine
    - flood fill threshold = len(snake) so we always have room to fit our body
    - never return OPPOSITE of current_dir (would collide with neck)
    """
    head  = snake[0]
    ss    = set(snake)          # full body — all cells blocked
    wrap  = (mode == "portal")
    enemy_cells = {(e.x, e.y) for e in enemies}
    blocked = walls | ss | enemy_cells

    # --- Build prioritised target list ---
    targets = []
    PU_SCORE = {"double": 100, "shield": 90, "speed": 80, "ghost": 70}
    now = time.time()
    for pu_pos, pu_type, pu_time in puf:
        if pu_type in GOOD_PU and (now - pu_time) < 18:
            targets.append((pu_pos, PU_SCORE.get(pu_type, 50)))
        # BAD_PU never added → never chased

    for bf_pos, bf_type, _ in bonus:
        targets.append((bf_pos, bf_type["pts"] * 30))

    targets.append((food, 10))
    targets.sort(key=lambda x: -x[1])

    # --- Try each target, BFS then safety check ---
    for target_pos, _ in targets:
        d = bfs(head, [target_pos], blocked, COLS, ROWS, wrap)
        if d is None: continue
        if d == OPPOSITE.get(current_dir): continue   # never 180
        nxt = _step(head, d, wrap, COLS, ROWS)
        if nxt is None or nxt in blocked: continue    # sanity: never step into wall/body
        # After stepping to nxt, body grows by 1 at front, tail stays (worst case = ate food)
        # So blocked for flood fill = original blocked minus nxt (we're standing there now)
        post_blocked = blocked - {nxt}
        free = flood_fill_size(nxt, post_blocked, COLS, ROWS, wrap)
        if free >= len(snake):                        # enough room for whole body
            return d

    # --- Fallback: largest open space, still avoiding 180 ---
    best_d = None; best_free = -1
    for d in ALL_DIRS:
        if d == OPPOSITE.get(current_dir): continue
        nxt = _step(head, d, wrap, COLS, ROWS)
        if nxt is None or nxt in blocked: continue
        post_blocked = blocked - {nxt}
        free = flood_fill_size(nxt, post_blocked, COLS, ROWS, wrap)
        if free > best_free: best_free = free; best_d = d
    return best_d

# ─────────────────────────────────────────────────────────
#  AUTOPILOT SPEED  (mutable so it persists across Game instances)
#  1 = slowest (1 step per 1000 frames), 1000 = fastest (1 step per frame)
# ─────────────────────────────────────────────────────────
_AUTO_SPEED = [700]   # default 700 out of 1000

TURBO_STEPS = 2000   # steps per frame in turbo — ~120,000 moves/sec at 60fps

def auto_interval(spd):
    """Returns (interval, steps_per_frame).
    Below 1000: 1 step every N frames. At 1000: TURBO."""
    if spd >= 1000:
        return (1, TURBO_STEPS)
    t = clamp(spd, 1, 999) / 999.0
    return (max(1, round(60 ** (1.0 - t))), 1)

# ─────────────────────────────────────────────────────────
#  GAME CLASS
# ─────────────────────────────────────────────────────────
class Game:
    def __init__(self,mode,diff,skin):
        self.mode=mode; self.diff=diff; self.skin=skin
        BASE={"easy":11,"normal":8,"hard":5,"insane":3}
        self.base_spd=BASE[diff]; self.move_spd=self.base_spd
        self.walls=build_maze(random.randint(0,4),COLS,ROWS) if mode=="maze" else set()
        cx,cy=COLS//2,ROWS//2
        self.snake=deque([(cx,cy),(cx-1,cy),(cx-2,cy)])
        self.dir=RIGHT; self.pend=RIGHT
        self.food_t=rand_food(); self.food=self._spawn(); self.food_ts=time.time()
        self.bonus=[]
        self.puf=[]; PU_EV={"easy":160,"normal":280,"hard":420,"insane":580}
        PU_MX={"easy":3,"normal":2,"hard":1,"insane":1}
        self.pu_ev=PU_EV[diff]; self.pu_mx=PU_MX[diff]; self.pu_t=0
        self.effects={}; self.shields=0
        self.score=0; self.combo=0; self.max_combo=0
        self.level=1; self.xp=0; self.xp_cap=5
        self.enemies=[]
        if mode=="survival": self.enemies=[Enemy(*self._spawn())]
        self.blitz_start=time.time()
        self.parts=[]; self.floats=[]; self.trail=deque(maxlen=14)
        self.flash_col=None; self.flash_t=0
        self.banner=""; self.banner_col=WHITE; self.banner_t=0
        self.frame=0; self.tick=0; self.bob=0.0
        self.t_start=time.time(); self.eaten=0
        # ── AUTOPILOT ──
        self.autopilot=False
        self.auto_pulse=0
        self.auto_speed=_AUTO_SPEED[0]   # shared mutable so it persists across restarts

    def _spawn(self,extra=()):
        occ=set(self.snake)|self.walls|set(extra)
        for _ in range(600):
            p=(random.randint(1,COLS-2),random.randint(1,ROWS-2))
            if p not in occ: return p
        return (1,1)

    def _ss(self): return set(self.snake)
    def _flash(self,col,t=12): self.flash_col=col; self.flash_t=t
    def _banner(self,txt,col=WHITE,t=85): self.banner=txt; self.banner_col=col; self.banner_t=t
    def _burst(self,x,y,col,n=18):
        for _ in range(n): self.parts.append(Particle(x,y,col))
    def _float(self,x,y,txt,col=WHITE): self.floats.append(FloatText(x,y,txt,col))
    def _active(self,nm): return nm in self.effects and self.effects[nm]>time.time()
    def _eff_spd(self):
        if self.autopilot:
            return auto_interval(self.auto_speed)[0]
        s=self.move_spd
        if self._active("speed"): s=max(2,s-3)
        if self._active("slow"):  s=s+4
        return s

    def _steps_this_frame(self):
        """How many snake steps to run this frame."""
        if self.autopilot:
            interval, per_frame = auto_interval(self.auto_speed)
            if per_frame > 1:
                return per_frame  # TURBO
            return 1 if self.frame % interval == 0 else 0
        return 1 if self.frame % self._eff_spd() == 0 else 0

    def _set_auto_speed(self, spd):
        self.auto_speed = clamp(spd, 1, 1000)
        _AUTO_SPEED[0]  = self.auto_speed

    def _apply_pu(self,nm):
        DUR={"speed":5,"slow":5,"ghost":7,"double":8}
        NAMES={"speed":"SPEED BOOST!","slow":"SLOW DOWN","ghost":"GHOST MODE!",
               "double":"DOUBLE SCORE!","shield":"SHIELD UP!","shrink":"SHRINK"}
        PCOLS={"speed":GOLD,"slow":CYAN,"ghost":PURPLE,"double":ORANGE,
               "shield":(0,215,175),"shrink":(195,75,75)}
        if nm=="shield": self.shields+=1
        elif nm=="shrink":
            for _ in range(min(3,len(self.snake)-1)): self.snake.pop()
        else: self.effects[nm]=time.time()+DUR.get(nm,5)
        self._banner(NAMES.get(nm,nm.upper()),PCOLS.get(nm,WHITE)); sfx("powerup")

    def toggle_autopilot(self):
        self.autopilot = not self.autopilot
        if self.autopilot:
            sfx("auto_on")
            self._banner("AUTOPILOT ON!", AUTO_COL, 90)
            self._burst(self.snake[0][0]*CELL+CELL//2,
                        self.snake[0][1]*CELL+CELL//2, AUTO_COL, 20)
        else:
            sfx("auto_off")
            self._banner("AUTOPILOT OFF", GRAY, 60)

    def _run_autopilot(self):
        """Compute and apply autopilot direction. Called right before each move."""
        d = autopilot_dir(
            list(self.snake), self.food, self.walls,
            self.puf, self.bonus, self.enemies,
            self.mode, self.effects, self.shields, self.dir
        )
        if d is not None:
            # Never allow a 180° reversal into own body
            if d != OPPOSITE.get(self.dir):
                self.pend = d

    def _do_step(self, now):
        """Execute one snake move. Returns 'dead', 'playing'(shield), or None(ok)."""
        if self.autopilot:
            self._run_autopilot()
        self.dir=self.pend
        hx,hy=self.snake[0]; nx,ny=hx+self.dir[0],hy+self.dir[1]
        if self.mode=="portal": nx%=COLS; ny%=ROWS
        else:
            if not(0<=nx<COLS and 0<=ny<ROWS): return self._die()
        if (nx,ny) in self.walls: return self._die()
        ss=self._ss()
        if (nx,ny) in ss and not self._active("ghost"): return self._die()
        for e in self.enemies:
            if (e.x,e.y)==(nx,ny): return self._die()
        self.snake.appendleft((nx,ny)); self.trail.appendleft((nx,ny))
        ate=False
        if (nx,ny)==self.food:
            pts=self.food_t["pts"]*(2 if self._active("double") else 1)
            self.combo+=1; self.max_combo=max(self.max_combo,self.combo)
            mx=min(10,1+self.combo//3); pts*=mx
            self.score+=pts; self.xp+=1; self.eaten+=1
            px2=nx*CELL+CELL//2; py2=ny*CELL+CELL//2
            self._burst(px2,py2,self.food_t["col"],22)
            self._float(px2,py2-10,f"+{pts}"+(f" x{mx}" if mx>1 else ""),self.food_t["col"])
            self._flash((185,255,185),6); sfx("eat")
            if self.combo>1: sfx("combo")
            if self.xp>=self.xp_cap:
                self.xp-=self.xp_cap; self.xp_cap=int(self.xp_cap*1.45)+2
                self.level+=1; self.move_spd=max(2,self.base_spd-self.level//2)
                self._banner(f"LEVEL {self.level}!",GOLD,100); sfx("levelup")
            self.food_t=rand_food(); self.food=self._spawn(); self.food_ts=now; ate=True
        else: self.snake.pop()
        for bf in list(self.bonus):
            if (nx,ny)==bf[0]:
                pts=bf[1]["pts"]*(2 if self._active("double") else 1)
                self.score+=pts
                px2=nx*CELL+CELL//2; py2=ny*CELL+CELL//2
                self._burst(px2,py2,bf[1]["col"],26)
                self._float(px2,py2-10,f"+{pts}!",bf[1]["col"])
                self._flash((255,255,175),8); self.bonus.remove(bf)
                if not ate: self.snake.appendleft((nx,ny)); ate=True
        for pu in list(self.puf):
            if (nx,ny)==pu[0]:
                self._apply_pu(pu[1])
                self._burst(nx*CELL+CELL//2,ny*CELL+CELL//2,(255,215,90),15)
                self.puf.remove(pu)
        return None

    def update(self):
        self.frame+=1; self.tick+=1; self.bob+=0.17
        self.auto_pulse = (self.auto_pulse + 1) % 60
        now=time.time()
        self.effects={k:v for k,v in self.effects.items() if v>now}
        if self.mode=="blitz" and now-self.blitz_start>=60.0: return "timeout"
        self.pu_t+=1
        if self.pu_t>=self.pu_ev and len(self.puf)<self.pu_mx:
            self.pu_t=0
            TYPES=["speed","slow","ghost","double","shield","shrink"]
            p=self._spawn([f[0] for f in self.puf])
            self.puf.append([p,random.choice(TYPES),now])
        self.puf=[p for p in self.puf if now-p[2]<28]
        self.bonus=[b for b in self.bonus if b[1]["ttl"] is None or now-b[2]<b[1]["ttl"]]
        if random.random()<0.0018 and len(self.bonus)<2:
            self.bonus.append([self._spawn(),random.choice(FOODS[1:]),now])
        if self.food_t["ttl"] and now-self.food_ts>self.food_t["ttl"]:
            self.food_t=FOODS[0]; self.food=self._spawn(); self.food_ts=now

        steps = self._steps_this_frame()
        for _ in range(steps):
            r = self._do_step(now)
            if r == "dead": return "dead"
            # "playing" = shield saved us, keep going in turbo

        ss=self._ss()
        for e in self.enemies:
            e.update(self.snake[0][0],self.snake[0][1],self.walls,ss,self.score)
            if (e.x,e.y)==self.snake[0]: return self._die()
        if self.mode=="survival":
            want=1+self.score//8
            while len(self.enemies)<min(want,5):
                p=self._spawn(); self.enemies.append(Enemy(*p))
        self.parts=[p for p in self.parts if p.life>0]
        for p in self.parts: p.update()
        self.floats=[f for f in self.floats if f.life>0]
        for f in self.floats: f.update()
        if self.flash_t>0: self.flash_t-=1
        if self.banner_t>0: self.banner_t-=1
        return "playing"

    def _die(self):
        hx,hy=self.snake[0]
        self._burst(hx*CELL+CELL//2,hy*CELL+CELL//2,(255,55,55),40)
        self._flash((195,0,0),22); sfx("die"); self.combo=0
        if self.shields>0:
            self.shields-=1; self._banner("SHIELD SAVED YOU!",(0,215,175)); sfx("shield")
            return "playing"
        return "dead"

    def draw(self,surf,scanlines,fps_on,fps_val,hi,muted):
        surf.fill(DARK_BG,(0,0,GAME_W,GAME_H))
        draw_stars(surf,self.tick)
        for gx in range(0,GAME_W,CELL): pygame.draw.line(surf,GRID_C,(gx,0),(gx,GAME_H))
        for gy in range(0,GAME_H,CELL): pygame.draw.line(surf,GRID_C,(0,gy),(GAME_W,gy))

        # ── Draw autopilot path hint (BFS target line) ──
        if self.autopilot:
            # Draw a subtle line from head to current BFS target
            targets = []
            PU_SCORE = {"double":100,"shield":90,"speed":80,"ghost":70}
            now = time.time()
            for pu_pos,pu_type,pu_time in self.puf:
                if pu_type in GOOD_PU and now-pu_time<18:
                    targets.append((pu_pos, PU_SCORE.get(pu_type,50)))
            for bf_pos,bf_type,_ in self.bonus:
                targets.append((bf_pos, bf_type["pts"]*30))
            targets.append((self.food, 10))
            targets.sort(key=lambda x:-x[1])
            if targets:
                tgt = targets[0][0]
                hpx = self.snake[0][0]*CELL+CELL//2
                hpy = self.snake[0][1]*CELL+CELL//2
                tpx = tgt[0]*CELL+CELL//2
                tpy = tgt[1]*CELL+CELL//2
                a = int(55 + 30*math.sin(self.auto_pulse*0.2))
                ls = pygame.Surface((GAME_W,GAME_H), pygame.SRCALPHA)
                pygame.draw.line(ls,(*AUTO_COL,a),(hpx,hpy),(tpx,tpy),2)
                pygame.draw.circle(ls,(*AUTO_COL,a+40),(tpx,tpy),7,2)
                surf.blit(ls,(0,0))

        for wx,wy in self.walls: draw_cube(surf,wx*CELL,wy*CELL,CELL,(55,45,75))
        tlist=list(self.trail)[1:]
        for i,(tx,ty) in enumerate(tlist):
            a=max(0,35-i*3); ts=pygame.Surface((CELL-4,CELL-4),pygame.SRCALPHA)
            ts.fill((55,195,75,a)); surf.blit(ts,(tx*CELL+2,ty*CELL+2))
        if self._active("ghost"):
            _A.fill((90,45,185,14)); surf.blit(_A,(0,0))
        if self._active("speed") or self._eff_spd()<=3:
            hx2,hy2=self.snake[0]; cx2=hx2*CELL+CELL//2; cy2=hy2*CELL+CELL//2
            _A.fill((0,0,0,0))
            for _ in range(6):
                a=random.uniform(0,2*math.pi); l=random.randint(28,75)
                pygame.draw.line(_A,(255,255,255,22),(cx2,cy2),(cx2+int(math.cos(a)*l),cy2+int(math.sin(a)*l)),1)
            surf.blit(_A,(0,0))
        for pu in self.puf:
            px2,py2=pu[0]; draw_gem(surf,px2*CELL+CELL//2,py2*CELL+CELL//2,pu[1],self.tick)
        for bf in self.bonus:
            bx,by=bf[0]; r=1.0
            if bf[1]["ttl"]: r=max(0.0,1.0-(time.time()-bf[2])/bf[1]["ttl"])
            draw_apple(surf,bx*CELL+CELL//2,by*CELL+CELL//2,CELL//2-1,self.tick,color=bf[1]["col"],ring=r)
        r=1.0
        if self.food_t["ttl"]: r=max(0.0,1.0-(time.time()-self.food_ts)/self.food_t["ttl"])
        fx,fy=self.food
        draw_apple(surf,fx*CELL+CELL//2,fy*CELL+CELL//2,CELL//2,self.tick,color=self.food_t["col"],ring=r)
        total=len(self.snake); bob=math.sin(self.bob)*1.4
        for i,(sx,sy) in enumerate(reversed(self.snake)):
            idx=total-1-i; t=idx/max(total-1,1); c=seg_color(self.skin,t,idx,total)
            # Autopilot: add subtle teal glow to head
            is_auto_head = (idx==0 and self.autopilot)
            draw_cube(surf,sx*CELL,sy*CELL,CELL,c,head=(idx==0),
                      glow=(idx==0 and (self._active("ghost") or self.autopilot)),
                      gcol=(0,255,180) if is_auto_head else (155,75,255),
                      bob=bob if idx==0 else 0)
        for e in self.enemies: e.draw(surf,self.tick)
        for p in self.parts: p.draw(surf)
        for f in self.floats: f.draw(surf)
        if self.flash_t>0:
            a=int(175*self.flash_t/22); _A.fill((*self.flash_col,a)); surf.blit(_A,(0,0))
        if self.banner_t>0:
            a=min(255,self.banner_t*5); bt=F_MED.render(self.banner,True,self.banner_col)
            bt.set_alpha(a); surf.blit(bt,bt.get_rect(center=(GAME_W//2,34)))
        if scanlines: surf.blit(_scan_surf,(0,0),(0,0,GAME_W,GAME_H))

        # ─── PANEL ───
        PX=GAME_W; surf.fill(PANEL_BG,(PX,0,PANEL_W,HEIGHT))
        pygame.draw.line(surf,(33,37,58),(PX,0),(PX,HEIGHT),2)
        t1=F_SM.render("ULTIMATE",True,(75,215,75)); t2=F_SM.render("3D SNAKE",True,(55,175,55))
        surf.blit(t1,t1.get_rect(center=(PX+PANEL_W//2,9))); surf.blit(t2,t2.get_rect(center=(PX+PANEL_W//2,25)))
        yo=48
        draw_box(surf,PX+5,yo,PANEL_W-10,50,"SCORE")
        sc=F_BIG.render(str(self.score),True,WHITE); surf.blit(sc,sc.get_rect(center=(PX+PANEL_W//2,yo+28))); yo+=55
        draw_box(surf,PX+5,yo,PANEL_W-10,33,"BEST")
        hs=F_MED.render(str(hi),True,GOLD); surf.blit(hs,hs.get_rect(center=(PX+PANEL_W//2,yo+15))); yo+=38
        draw_box(surf,PX+5,yo,PANEL_W-10,40,f"LEVEL {self.level}")
        draw_bar(surf,PX+8,yo+22,PANEL_W-16,11,self.xp/self.xp_cap,CYAN,lbl=f"XP {self.xp}/{self.xp_cap}"); yo+=45
        if self.combo>1:
            mx=min(10,1+self.combo//3); cc=lerp((255,200,0),(255,75,0),min(1,self.combo/15))
            draw_box(surf,PX+5,yo,PANEL_W-10,33,"COMBO")
            ct=F_MED.render(f"x{mx}  ({self.combo})",True,cc); surf.blit(ct,(PX+8,yo+12)); yo+=38
        draw_box(surf,PX+5,yo,PANEL_W-10,33,"LENGTH")
        lt=F_MED.render(str(len(self.snake)),True,(155,255,155)); surf.blit(lt,lt.get_rect(center=(PX+PANEL_W//2,yo+15))); yo+=38
        if self.mode=="blitz":
            rem=max(0,60.0-(time.time()-self.blitz_start)); tc=(255,75,75) if rem<10 else WHITE
            draw_box(surf,PX+5,yo,PANEL_W-10,33,"TIME LEFT")
            tt=F_MED.render(f"{rem:.1f}s",True,tc); surf.blit(tt,tt.get_rect(center=(PX+PANEL_W//2,yo+15))); yo+=38
        else:
            el=time.time()-self.t_start
            draw_box(surf,PX+5,yo,PANEL_W-10,33,"TIME")
            tt=F_MED.render(f"{int(el)//60:02d}:{int(el)%60:02d}",True,GRAY); surf.blit(tt,tt.get_rect(center=(PX+PANEL_W//2,yo+15))); yo+=38
        if self.shields>0:
            draw_box(surf,PX+5,yo,PANEL_W-10,26)
            st=F_SM.render(f"[SHIELD x{self.shields}]",True,(0,215,175)); surf.blit(st,(PX+8,yo+7)); yo+=30
        now=time.time()
        ECOLS={"speed":GOLD,"slow":CYAN,"ghost":PURPLE,"double":ORANGE}
        EDUR={"speed":5,"slow":5,"ghost":7,"double":8}
        active=[(k,v) for k,v in self.effects.items() if v>now]
        if active:
            draw_box(surf,PX+5,yo,PANEL_W-10,14+len(active)*19,"ACTIVE")
            for i,(nm,exp) in enumerate(active):
                draw_bar(surf,PX+8,yo+15+i*19,PANEL_W-16,13,(exp-now)/EDUR.get(nm,5),ECOLS.get(nm,WHITE),lbl=nm.upper())
            yo+=20+len(active)*19

        # ── AUTOPILOT STATUS + SPEED BAR ──
        pulse_a = int(180 + 75*math.sin(self.auto_pulse*0.2))
        bar_x = PX+8; bar_w = PANEL_W-16

        if self.autopilot:
            ap_col = lerp(AUTO_COL, WHITE, 0.25)
            pygame.draw.rect(surf,(0,38,28),(PX+5,yo,PANEL_W-10,30),border_radius=5)
            pygame.draw.rect(surf,AUTO_COL,(PX+5,yo,PANEL_W-10,30),2,border_radius=5)
            auto_lbl = F_SM.render("⬡ AUTOPILOT ON", True, ap_col)
            auto_lbl.set_alpha(pulse_a)
            surf.blit(auto_lbl, auto_lbl.get_rect(center=(PX+PANEL_W//2, yo+14)))
            yo += 34
        else:
            pygame.draw.rect(surf,(20,20,28),(PX+5,yo,PANEL_W-10,22),border_radius=5)
            pygame.draw.rect(surf,(45,48,65),(PX+5,yo,PANEL_W-10,22),1,border_radius=5)
            hint = F_XS.render("[F] AUTOPILOT OFF", True, DGRAY)
            surf.blit(hint, hint.get_rect(center=(PX+PANEL_W//2, yo+11)))
            yo += 26

        # Speed bar (always visible)
        is_turbo = (self.auto_speed >= 1000)
        spd_label_txt = f"SPD [{self.auto_speed}]  < / >" if not is_turbo else "SPD [TURBO]"
        spd_label = F_XS.render(spd_label_txt, True, (255,140,0) if is_turbo else (AUTO_COL if self.autopilot else GRAY))
        surf.blit(spd_label, (bar_x, yo))
        yo += 14
        bar_h = 10
        bar_pct = (self.auto_speed - 1) / 999.0
        pygame.draw.rect(surf,(18,22,38),(bar_x, yo, bar_w, bar_h), border_radius=4)
        if is_turbo:
            pulse_c = lerp((255,120,0),(255,30,0), abs(math.sin(self.auto_pulse*0.15)))
            pygame.draw.rect(surf, pulse_c, (bar_x, yo, bar_w, bar_h), border_radius=4)
        else:
            spd_col = lerp(lerp(CYAN, GOLD, min(1, bar_pct*2)), (255,60,60), max(0, bar_pct*2-1))
            fw = max(4, int(bar_w * bar_pct))
            pygame.draw.rect(surf, spd_col, (bar_x, yo, fw, bar_h), border_radius=4)
            thumb_x = bar_x + fw - 3
            pygame.draw.rect(surf, WHITE, (thumb_x, yo-1, 5, bar_h+2), border_radius=2)
        pygame.draw.rect(surf,(55,60,90),(bar_x, yo, bar_w, bar_h), 1, border_radius=4)
        self._spd_bar_rect = pygame.Rect(bar_x, yo, bar_w, bar_h)
        yo += bar_h + 6

        # ── BIG DEDICATED TURBO BUTTON ──
        tb_h = 32
        if is_turbo:
            # Active: pulsing fire gradient
            pa = abs(math.sin(self.auto_pulse * 0.18))
            tb_col  = lerp((220, 60, 0), (255, 180, 0), pa)
            tb_edge = lerp((255, 200, 0), (255, 80,  0), pa)
            tb_text_col = WHITE
            tb_label = "⚡ TURBO  ON ⚡"
        else:
            tb_col  = (28, 14, 6)
            tb_edge = (100, 50, 10)
            tb_text_col = (160, 80, 20)
            tb_label = "⚡ TURBO x100000"
        pygame.draw.rect(surf, tb_col,  (bar_x, yo, bar_w, tb_h), border_radius=6)
        pygame.draw.rect(surf, tb_edge, (bar_x, yo, bar_w, tb_h), 2, border_radius=6)
        # inner glow when active
        if is_turbo:
            glow_s = pygame.Surface((bar_w-4, tb_h-4), pygame.SRCALPHA)
            ga = int(40 + 30*pa)
            glow_s.fill((255, 160, 0, ga))
            surf.blit(glow_s, (bar_x+2, yo+2))
        tb_surf = F_SM.render(tb_label, True, tb_text_col)
        surf.blit(tb_surf, tb_surf.get_rect(center=(bar_x + bar_w//2, yo + tb_h//2)))
        hint_surf = F_XS.render("[ T ] to toggle", True, (80,40,10) if not is_turbo else (200,120,0))
        surf.blit(hint_surf, hint_surf.get_rect(center=(bar_x + bar_w//2, yo + tb_h - 5)))
        self._turbo_rect = pygame.Rect(bar_x, yo, bar_w, tb_h)
        yo += tb_h + 4

        mmy=HEIGHT-90
        surf.blit(F_XS.render("MAP",True,GRAY),(PX+8,mmy-13))
        draw_minimap(surf,PX+5,mmy,PANEL_W-10,82,list(self.snake),self.food,self.walls,self.enemies)
        MCOLS={"classic":GRAY,"portal":CYAN,"maze":PURPLE,"blitz":ORANGE,"survival":(255,75,75),"zen":(75,215,75)}
        md=F_XS.render(f"{self.mode.upper()} / {self.diff.upper()}",True,MCOLS.get(self.mode,GRAY))
        surf.blit(md,md.get_rect(center=(PX+PANEL_W//2,HEIGHT-13)))
        if fps_on: surf.blit(F_XS.render(f"FPS {fps_val:.0f}",True,DGRAY),(4,HEIGHT-15))
        if muted:  surf.blit(F_XS.render("MUTED (M)",True,DGRAY),(4,HEIGHT-28))

# ─────────────────────────────────────────────────────────
#  MENUS
# ─────────────────────────────────────────────────────────
_T=[0]

def _bg(surf):
    surf.fill(DARK_BG); draw_stars(surf,_T[0])

def _ov(surf,a=150):
    ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,a)); surf.blit(ov,(0,0))

def _title_anim(surf):
    chars="ULTIMATE 3D SNAKE"; cw=34; tw=len(chars)*cw; sx=WIDTH//2-tw//2
    CL=[(75,215,75),(55,195,255),(195,75,255),(255,195,0),(255,75,75)]
    for i,ch in enumerate(chars):
        wy=math.sin(_T[0]*0.055+i*0.38)*5; c=CL[i%len(CL)]
        surf.blit(F_BIG.render(ch,True,c),(sx+i*cw,38+wy))

MODES=[("classic","CLASSIC","Standard snake. Walls kill.",GRAY),
       ("portal","PORTAL","Walls wrap around like Pac-Man.",CYAN),
       ("maze","MAZE","Navigate through obstacle walls.",PURPLE),
       ("blitz","BLITZ","60 seconds — highest score wins!",ORANGE),
       ("survival","SURVIVAL","Enemies hunt you. Survive!",(255,75,75)),
       ("zen","ZEN","No death. Infinite snake. Pure chill.",(75,215,75))]

DIFFS=[("easy","EASY","Slow + frequent power-ups.",(75,215,75)),
       ("normal","NORMAL","Balanced. The real experience.",WHITE),
       ("hard","HARD","Fast + rare power-ups + smart enemies.",ORANGE),
       ("insane","INSANE","Max speed. Minimum mercy.",(255,55,55))]

def select_menu(surf,title,options):
    sel=0
    while True:
        _T[0]+=1; _bg(surf); _title_anim(surf); _ov(surf,105)
        surf.blit(F_BIG.render(title,True,WHITE),F_BIG.render(title,True,WHITE).get_rect(center=(WIDTH//2,108)))
        for i,(key,lbl,desc,col) in enumerate(options):
            s=(i==sel); bx=WIDTH//2-270; by=142+i*56; bw=540; bh=48
            bg=lerp((18,20,33),(32,28,52),1 if s else 0)
            pygame.draw.rect(surf,bg,(bx,by,bw,bh),border_radius=7)
            if s: pygame.draw.rect(surf,col,(bx,by,bw,bh),2,border_radius=7)
            surf.blit(F_MED.render(lbl,True,col if s else GRAY),(bx+12,by+5))
            surf.blit(F_XS.render(desc,True,(175,175,195) if s else (72,72,92)),(bx+12,by+27))
        h=F_XS.render("UP/DOWN   ENTER select",True,DGRAY); surf.blit(h,h.get_rect(center=(WIDTH//2,HEIGHT-16)))
        pygame.display.flip(); clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_UP:   sel=(sel-1)%len(options); sfx("menu")
                if ev.key==pygame.K_DOWN: sel=(sel+1)%len(options); sfx("menu")
                if ev.key in(pygame.K_RETURN,pygame.K_SPACE): return options[sel][0]

def skin_menu(surf,unlocked):
    avail=[i for i,s in enumerate(SKINS) if s["req"]<=unlocked]
    if not avail: avail=[0]
    ptr=0
    while True:
        _T[0]+=1; _bg(surf); _title_anim(surf); _ov(surf,110)
        surf.blit(F_BIG.render("CHOOSE SKIN",True,WHITE),F_BIG.render("CHOOSE SKIN",True,WHITE).get_rect(center=(WIDTH//2,108)))
        PER=5
        for idx in range(len(SKINS)):
            s=SKINS[idx]; locked=s["req"]>unlocked; row=idx//PER; ci=idx%PER
            bx=WIDTH//2-(PER*126)//2+ci*126; by=142+row*96; bw=118; bh=84
            sel=(idx==avail[ptr%len(avail)])
            pygame.draw.rect(surf,(22,25,40) if not locked else (13,13,22),(bx,by,bw,bh),border_radius=7)
            if sel and not locked: pygame.draw.rect(surf,(75,215,75),(bx,by,bw,bh),2,border_radius=7)
            pc=seg_color(idx,0.8,2,3) if not locked else DGRAY
            draw_cube(surf,bx+8,by+10,CELL,pc,head=True)
            draw_cube(surf,bx+30,by+10,CELL,seg_color(idx,0.5,1,3) if not locked else DGRAY)
            draw_cube(surf,bx+52,by+10,CELL,seg_color(idx,0.1,0,3) if not locked else DGRAY)
            nc=WHITE if not locked else (45,45,55)
            nm=F_XS.render(s["name"],True,nc); surf.blit(nm,nm.get_rect(center=(bx+bw//2,by+56)))
            if locked:
                lk=F_XS.render(f"Lv{s['req']}",True,(72,72,82)); surf.blit(lk,lk.get_rect(center=(bx+bw//2,by+68)))
        h=F_XS.render("LEFT/RIGHT  TAB  ENTER",True,DGRAY); surf.blit(h,h.get_rect(center=(WIDTH//2,HEIGHT-16)))
        pygame.display.flip(); clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key in(pygame.K_RIGHT,pygame.K_TAB): ptr=(ptr+1)%len(avail); sfx("menu")
                if ev.key==pygame.K_LEFT: ptr=(ptr-1)%len(avail); sfx("menu")
                if ev.key in(pygame.K_RETURN,pygame.K_SPACE): return avail[ptr%len(avail)]

def gameover_screen(surf,g,hi):
    el=time.time()-g.t_start
    while True:
        _T[0]+=1; _bg(surf); _ov(surf,145)
        surf.blit(F_HUGE.render("GAME OVER",True,(215,55,55)),F_HUGE.render("GAME OVER",True,(215,55,55)).get_rect(center=(WIDTH//2,78)))
        rows=[("SCORE",str(g.score),WHITE),("BEST",str(hi),GOLD),
              ("LENGTH",str(len(g.snake)),(155,255,155)),("LEVEL",str(g.level),CYAN),
              ("MAX COMBO",f"x{min(10,1+g.max_combo//3)} ({g.max_combo})",ORANGE),
              ("TIME",f"{int(el)//60:02d}:{int(el)%60:02d}",GRAY),
              ("APPLES",str(g.eaten),(215,95,95)),("MODE",g.mode.upper(),PURPLE)]
        TX=WIDTH//2-195
        for i,(lb,vl,col) in enumerate(rows):
            pygame.draw.rect(surf,(18,20,33) if i%2==0 else (13,15,26),(TX,148+i*34,390,30),border_radius=4)
            surf.blit(F_SM.render(lb,True,GRAY),(TX+10,152+i*34))
            vt=F_SM.render(vl,True,col); surf.blit(vt,(TX+390-vt.get_width()-10,152+i*34))
        if g.score>=hi and g.score>0:
            nt=F_MED.render("*** NEW HIGH SCORE! ***",True,GOLD)
            nt.set_alpha(clamp(int(200+55*math.sin(_T[0]*0.1)),0,255)); surf.blit(nt,nt.get_rect(center=(WIDTH//2,438)))
        h=F_SM.render("ENTER = play again    ESC = main menu",True,GRAY); surf.blit(h,h.get_rect(center=(WIDTH//2,HEIGHT-20)))
        pygame.display.flip(); clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_RETURN: return "again"
                if ev.key==pygame.K_ESCAPE: return "menu"

def pause_screen(surf):
    ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,155)); surf.blit(ov,(0,0))
    surf.blit(F_HUGE.render("PAUSED",True,WHITE),F_HUGE.render("PAUSED",True,WHITE).get_rect(center=(WIDTH//2,HEIGHT//2-28)))
    surf.blit(F_SM.render("ESC resume    R restart    Q main menu",True,GRAY),
              F_SM.render("ESC resume    R restart    Q main menu",True,GRAY).get_rect(center=(WIDTH//2,HEIGHT//2+30)))
    pygame.display.flip()
    while True:
        clock.tick(30)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: return "resume"
                if ev.key==pygame.K_r:      return "restart"
                if ev.key in(pygame.K_q,):  return "menu"

# ─────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────
def main():
    hi=0; best_lv=0; scanlines=False; fps_on=False; muted=False
    dragging_spd = False
    while True:
        mode=select_menu(screen,"SELECT MODE",MODES)
        diff=select_menu(screen,"SELECT DIFFICULTY",DIFFS)
        skin=skin_menu(screen,best_lv)
        while True:
            g=Game(mode,diff,skin); result="playing"
            while result=="playing":
                _T[0]+=1; clock.tick(60); fps=clock.get_fps()
                for ev in pygame.event.get():
                    if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
                    if ev.type==pygame.KEYDOWN:
                        k=ev.key
                        if   k in(pygame.K_UP,   pygame.K_w) and g.dir!=DOWN:  g.pend=UP
                        elif k in(pygame.K_DOWN, pygame.K_s) and g.dir!=UP:    g.pend=DOWN
                        elif k in(pygame.K_LEFT, pygame.K_a) and g.dir!=RIGHT: g.pend=LEFT
                        elif k in(pygame.K_RIGHT,pygame.K_d) and g.dir!=LEFT:  g.pend=RIGHT
                        elif k==pygame.K_f: g.toggle_autopilot()
                        # ── AUTOPILOT SPEED  < and > keys ──
                        elif k==pygame.K_COMMA  or k==pygame.K_LEFTBRACKET:
                            g._set_auto_speed(g.auto_speed - 10)
                        elif k==pygame.K_PERIOD or k==pygame.K_RIGHTBRACKET:
                            g._set_auto_speed(g.auto_speed + 10)
                        elif k==pygame.K_t:   # TURBO toggle
                            g._set_auto_speed(1000 if g.auto_speed < 1000 else 700)
                        elif k==pygame.K_ESCAPE:
                            pr=pause_screen(screen)
                            if pr=="menu":    result="menu";    break
                            if pr=="restart": result="restart"; break
                        elif k==pygame.K_r:  result="restart"; break
                        elif k==pygame.K_F1: scanlines=not scanlines
                        elif k==pygame.K_F3: fps_on=not fps_on
                        elif k==pygame.K_m:  muted=not muted
                    # ── MOUSE: click/drag speed bar ──
                    elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                        bar = getattr(g, '_spd_bar_rect', None)
                        turbo_btn = getattr(g, '_turbo_rect', None)
                        if turbo_btn and turbo_btn.collidepoint(ev.pos):
                            g._set_auto_speed(1000 if g.auto_speed < 1000 else 700)
                        elif bar and bar.collidepoint(ev.pos):
                            dragging_spd = True
                            pct = clamp((ev.pos[0]-bar.x)/bar.width, 0, 1)
                            g._set_auto_speed(max(1, int(1 + pct*999)))
                    elif ev.type==pygame.MOUSEBUTTONUP and ev.button==1:
                        dragging_spd = False
                    elif ev.type==pygame.MOUSEMOTION and dragging_spd:
                        bar = getattr(g, '_spd_bar_rect', None)
                        if bar:
                            pct = clamp((ev.pos[0]-bar.x)/bar.width, 0, 1)
                            g._set_auto_speed(max(1, int(1 + pct*999)))
                if result!="playing": break
                result=g.update()
                hi=max(hi,g.score); best_lv=max(best_lv,g.level)
                g.draw(screen,scanlines,fps_on,fps,hi,muted)
                pygame.display.flip()
            if result in("dead","timeout"):
                hi=max(hi,g.score)
                if gameover_screen(screen,g,hi)=="again": continue
                else: break
            elif result=="restart": continue
            elif result=="menu": break

if __name__=="__main__":
    main()