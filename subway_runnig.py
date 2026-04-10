#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║       SUBWAY SURFERS — REMASTERED PYTHON EDITION                ║
║   Fixed & Optimized  |  Pure Python + Pygame                    ║
╚══════════════════════════════════════════════════════════════════╝

INSTALL:   pip install pygame
RUN:       python subway_surfers_fixed.py

CONTROLS:
  ← →        Change lane
  ↑ / SPACE  Jump (double-jump supported)
  ↓          Roll / slide
  SHIFT      Sprint
  B          Brake
  A          Toggle Autopilot
  G          God Mode
  P / ESC    Pause
  C          Cycle camera
  T          Cycle theme
  N          Night vision
  J          Jetpack
  M          Slow motion
  X          ×5 multiplier
  1-6        Speed presets
  0          Auto speed
"""

import pygame
import math
import random
import time
import json
import os
import copy
from collections import deque

# ══════════════════════════════════════════════════════════════════════
#  PYGAME INIT  (must happen before anything font/surface related)
# ══════════════════════════════════════════════════════════════════════
pygame.init()
pygame.mixer.quit()   # disable sound so it never crashes on missing audio

# ══════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════
SW, SH      = 1280, 720
FPS         = 60
TITLE       = "Subway Surfers — Remastered"
SAVE_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")

# Lane X positions in 3-D world
LANE_X      = [-2.2, 0.0, 2.2]

# Physics
GRAVITY         = -24.0
JUMP_VEL        = 11.0
ROLL_DUR        = 0.5
LANE_CHANGE_T   = 0.14

# World
BASE_SPEED      = 12.0
MAX_SPEED       = 800.0
SPEED_RAMP      = 0.8
SPAWN_AHEAD     = 55.0
NEAR            = 0.3
FAR             = 100.0
BASE_FOV        = 70.0

# ── Colours ──────────────────────────────────────────────────────────
WHITE   = (255,255,255); BLACK  = (0,0,0)
YELLOW  = (255,220,0);   GOLD   = (255,180,0)
RED     = (220,40,40);   DKRED  = (120,15,15)
GREEN   = (40,200,60);   CYAN   = (40,220,220)
BLUE    = (60,100,220);  DKBLUE = (25,45,130)
MAGENTA = (220,40,220);  ORANGE = (255,130,0)
BROWN   = (130,70,25);   GRAY   = (150,150,150)
DKGRAY  = (70,70,70);    LTGRAY = (200,200,200)
SKIN    = (235,185,145); PURPLE = (130,35,190)
NEON_G  = (40,255,90);   NEON_P = (190,40,255)
NEON_C  = (40,220,255);  NAVY   = (10,10,70)

# ── Themes ────────────────────────────────────────────────────────────
THEMES = {
    "city":   dict(sky1=(25,70,170),  sky2=(70,130,210), g1=(58,58,62),  g2=(48,48,52),
                   bld=(85,85,90),    fog=(75,120,190),  fog_d=65, amb=0.58),
    "subway": dict(sky1=(8,8,18),     sky2=(18,18,32),   g1=(28,28,33),  g2=(18,18,23),
                   bld=(45,45,55),    fog=(12,12,28),    fog_d=38, amb=0.32),
    "desert": dict(sky1=(200,150,55), sky2=(235,195,95), g1=(185,150,85),g2=(165,130,65),
                   bld=(175,135,75),  fog=(225,185,105), fog_d=58, amb=0.72),
    "night":  dict(sky1=(3,3,15),     sky2=(8,8,35),     g1=(12,12,22),  g2=(8,8,16),
                   bld=(18,18,45),    fog=(5,5,25),      fog_d=32, amb=0.22),
    "neon":   dict(sky1=(4,0,18),     sky2=(12,4,36),    g1=(8,0,26),    g2=(6,0,20),
                   bld=(28,4,56),     fog=(8,0,28),      fog_d=30, amb=0.28),
}
THEME_KEYS = list(THEMES.keys())

# ── Power-ups ─────────────────────────────────────────────────────────
PU_MAGNET  = "magnet";  PU_SHIELD = "shield"; PU_JETPACK = "jetpack"
PU_X2      = "x2";      PU_X3     = "x3";     PU_X5      = "x5"
PU_SNKRS   = "sneakers";PU_SLOW   = "slowmo"; PU_TURBO   = "turbo"

PU_DUR = {PU_MAGNET:12,PU_SHIELD:8,PU_JETPACK:12,PU_X2:15,PU_X3:12,
          PU_X5:10,PU_SNKRS:10,PU_SLOW:6,PU_TURBO:8}
PU_COL = {PU_MAGNET:CYAN,PU_SHIELD:BLUE,PU_JETPACK:NEON_C,PU_X2:YELLOW,
          PU_X3:YELLOW,PU_X5:ORANGE,PU_SNKRS:GREEN,PU_SLOW:MAGENTA,PU_TURBO:RED}
PU_LBL = {PU_MAGNET:"MAG",PU_SHIELD:"SHD",PU_JETPACK:"JET",PU_X2:"×2",
          PU_X3:"×3",PU_X5:"×5",PU_SNKRS:"SNK",PU_SLOW:"SLO",PU_TURBO:"TRB"}

OT_TRAIN = "train"; OT_LOW = "low"; OT_HIGH = "high"; OT_BARREL = "barrel"

CHARS = [
    dict(name="Jake",  body=CYAN,    hair=YELLOW, pants=BLUE,   shoe=RED),
    dict(name="Tricky",body=RED,     hair=DKRED,  pants=DKGRAY, shoe=WHITE),
    dict(name="Fresh", body=GREEN,   hair=GRAY,   pants=BLUE,   shoe=YELLOW),
    dict(name="Spike", body=MAGENTA, hair=PURPLE, pants=BLACK,  shoe=CYAN),
    dict(name="Yutani",body=NEON_C,  hair=NEON_P, pants=NAVY,   shoe=NEON_G),
]

# ══════════════════════════════════════════════════════════════════════
#  MATH
# ══════════════════════════════════════════════════════════════════════

def clamp(v,lo,hi): return max(lo,min(hi,v))
def lerp(a,b,t):    return a+(b-a)*clamp(t,0,1)

def lerp_col(c1,c2,t):
    t=clamp(t,0,1)
    return (int(c1[0]+(c2[0]-c1[0])*t),
            int(c1[1]+(c2[1]-c1[1])*t),
            int(c1[2]+(c2[2]-c1[2])*t))

def smoothstep(t):
    t=clamp(t,0,1); return t*t*(3-2*t)

def fog_col(col, depth, fc, fd):
    t=clamp((depth/fd)**2,0,1)
    return lerp_col(col,fc,t)

def shade(col, n, sd, amb):
    d=max(0.0, n[0]*sd[0]+n[1]*sd[1]+n[2]*sd[2])
    b=clamp(amb+(1-amb)*d,0,1)
    return (int(col[0]*b),int(col[1]*b),int(col[2]*b))

# ── 4×4 row-major matrix ──────────────────────────────────────────────

def eye4():
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

def mmul(a,b):
    o=[0]*16
    for r in range(4):
        for c in range(4):
            s=0.0
            for k in range(4): s+=a[r*4+k]*b[k*4+c]
            o[r*4+c]=s
    return o

def mtranslate(tx,ty,tz):
    m=eye4(); m[3]=tx; m[7]=ty; m[11]=tz; return m

def mscale(sx,sy,sz):
    return [sx,0,0,0, 0,sy,0,0, 0,0,sz,0, 0,0,0,1]

def mrotz(a):
    c,s=math.cos(a),math.sin(a)
    return [c,-s,0,0, s,c,0,0, 0,0,1,0, 0,0,0,1]

def mpersp(fov_deg,aspect,near,far):
    f=1.0/math.tan(math.radians(fov_deg)*0.5)
    nf=1.0/(near-far)
    return [f/aspect,0,0,0, 0,f,0,0,
            0,0,(far+near)*nf,(2*far*near)*nf,
            0,0,-1,0]

def mlookat(eye,center,up):
    fx=center[0]-eye[0]; fy=center[1]-eye[1]; fz=center[2]-eye[2]
    fl=math.sqrt(fx*fx+fy*fy+fz*fz) or 1e-8
    fx/=fl; fy/=fl; fz/=fl
    sx=fy*up[2]-fz*up[1]; sy=fz*up[0]-fx*up[2]; sz=fx*up[1]-fy*up[0]
    sl=math.sqrt(sx*sx+sy*sy+sz*sz) or 1e-8
    sx/=sl; sy/=sl; sz/=sl
    ux=sy*fz-sz*fy; uy=sz*fx-sx*fz; uz=sx*fy-sy*fx
    return [sx,sy,sz,-(sx*eye[0]+sy*eye[1]+sz*eye[2]),
            ux,uy,uz,-(ux*eye[0]+uy*eye[1]+uz*eye[2]),
            -fx,-fy,-fz,(fx*eye[0]+fy*eye[1]+fz*eye[2]),
            0,0,0,1]

def tvec4(m,x,y,z,w=1.0):
    return (m[0]*x+m[1]*y+m[2]*z+m[3]*w,
            m[4]*x+m[5]*y+m[6]*z+m[7]*w,
            m[8]*x+m[9]*y+m[10]*z+m[11]*w,
            m[12]*x+m[13]*y+m[14]*z+m[15]*w)

def proj_pt(pv,wx,wy,wz):
    cx,cy,cz,cw=tvec4(pv,wx,wy,wz)
    if cw<=1e-4: return None
    nx,ny=cx/cw,cy/cw
    if abs(nx)>1.6 or abs(ny)>1.6: return None
    return int((nx*0.5+0.5)*SW), int((1-(ny*0.5+0.5))*SH), (cz/cw)*0.5+0.5

# ══════════════════════════════════════════════════════════════════════
#  RENDERER
# ══════════════════════════════════════════════════════════════════════

class Renderer:
    def __init__(self, surf):
        self.surf=surf
        self.pv=eye4()
        self.fc=(80,130,200)
        self.fd=60.0
        self.amb=0.55
        self.sd=[0.5,0.8,0.3]
        # Pre-baked sky surface (regenerated when theme changes)
        self._sky_cache={}

    def proj(self,wx,wy,wz): return proj_pt(self.pv,wx,wy,wz)

    def line3(self,p0,p1,col,w=1):
        a=self.proj(*p0); b=self.proj(*p1)
        if not a or not b: return
        c=fog_col(col,(a[2]+b[2])*0.5*self.fd,self.fc,self.fd)
        pygame.draw.line(self.surf,c,(a[0],a[1]),(b[0],b[1]),w)

    def quad3(self,v4,col,n=(0,1,0),wire=False):
        pts=[]
        az=0.0
        for v in v4:
            p=self.proj(*v)
            if not p: return
            pts.append((p[0],p[1])); az+=p[2]
        az/=4
        c=shade(col,n,self.sd,self.amb)
        c=fog_col(c,az*self.fd,self.fc,self.fd)
        if wire: pygame.draw.polygon(self.surf,c,pts,1)
        else:
            pygame.draw.polygon(self.surf,c,pts)
            edge=tuple(max(0,x-30) for x in c)
            pygame.draw.polygon(self.surf,edge,pts,1)

    def box(self,cx,cy,cz,w,h,d,cols,wire=False):
        hw,hh,hd=w/2,h/2,d/2
        v=[(cx-hw,cy-hh,cz-hd),(cx+hw,cy-hh,cz-hd),
           (cx+hw,cy+hh,cz-hd),(cx-hw,cy+hh,cz-hd),
           (cx-hw,cy-hh,cz+hd),(cx+hw,cy-hh,cz+hd),
           (cx+hw,cy+hh,cz+hd),(cx-hw,cy+hh,cz+hd)]
        faces=[
            ([v[4],v[5],v[6],v[7]],(0,0,1),"front"),
            ([v[1],v[0],v[3],v[2]],(0,0,-1),"back"),
            ([v[0],v[4],v[7],v[3]],(-1,0,0),"left"),
            ([v[5],v[1],v[2],v[6]],(1,0,0),"right"),
            ([v[3],v[7],v[6],v[2]],(0,1,0),"top"),
            ([v[0],v[1],v[5],v[4]],(0,-1,0),"bot"),
        ]
        def fd_f(f):
            ps=[self.proj(*p) for p in f[0]]
            ps=[p for p in ps if p]
            return sum(p[2] for p in ps)/len(ps) if ps else 1e9
        for q,n,nm in sorted(faces,key=fd_f,reverse=True):
            c=cols.get(nm,cols.get("*",GRAY)) if isinstance(cols,dict) else cols
            self.quad3(q,c,n,wire)

    def cyl(self,cx,cy,cz,r,h,col,segs=10,wire=False):
        angs=[2*math.pi*i/segs for i in range(segs)]
        tv=[(cx+r*math.cos(a),cy+h/2,cz+r*math.sin(a)) for a in angs]
        bv=[(cx+r*math.cos(a),cy-h/2,cz+r*math.sin(a)) for a in angs]
        for i in range(segs):
            j=(i+1)%segs
            nx=math.cos((angs[i]+angs[j])/2); nz=math.sin((angs[i]+angs[j])/2)
            self.quad3([bv[i],bv[j],tv[j],tv[i]],col,(nx,0,nz),wire)

    def draw_sky(self,theme):
        tc=THEMES[theme]
        # Cached sky gradient surface
        if theme not in self._sky_cache:
            sky=pygame.Surface((SW,SH//2+10))
            c1,c2=tc["sky1"],tc["sky2"]
            for y in range(SH//2+10):
                t=y/(SH//2+10)
                pygame.draw.line(sky,lerp_col(c1,c2,t),(0,y),(SW,y))
            # Stars for dark themes
            if theme in ("night","subway","neon"):
                for i in range(100):
                    sx=(i*137+53)%SW; sy=(i*79+11)%(SH//2-5)
                    br=80+(i%3)*60
                    r=1 if i%4==0 else 0
                    pygame.draw.circle(sky,(br,br,br),(sx,sy),r)
            self._sky_cache[theme]=sky
        self.surf.blit(self._sky_cache[theme],(0,0))

    def draw_ground(self,theme,cam_z):
        tc=THEMES[theme]
        c1,c2=tc["g1"],tc["g2"]
        strip=8.0
        for s in range(30):
            z0=cam_z+s*strip; z1=z0+strip
            col=c1 if s%2==0 else c2
            pts=[]
            for wx,wz in [(-12,z0),(12,z0),(12,z1),(-12,z1)]:
                p=self.proj(wx,0,wz)
                if p: pts.append((p[0],p[1]))
            if len(pts)==4:
                pygame.draw.polygon(self.surf,col,pts)

    def draw_track(self,theme,cam_z):
        tc=THEMES[theme]
        rc=tc.get("rail",LTGRAY) if "rail" in tc else LTGRAY
        # Use baked colors from theme
        rail_c=lerp_col(tc["g1"],(200,200,205),0.7)
        tie_c=lerp_col(tc["g1"],(110,75,45),0.8)

        # Rails (4 lines)
        for rx in [-3.0,-1.0,1.0,3.0]:
            pts=[]
            for i in range(30):
                z=cam_z+i*2.8
                p=self.proj(rx,0.04,z)
                if p: pts.append((p[0],p[1]))
            if len(pts)>1:
                for i in range(len(pts)-1):
                    w=max(1,int(3*(1-i/30)))
                    pygame.draw.line(self.surf,rail_c,pts[i],pts[i+1],w)

        # Ties
        ts=1.4; off=cam_z%ts
        for i in range(28):
            tz=cam_z+i*ts-off
            pl=self.proj(-3.2,0.01,tz); pr=self.proj(3.2,0.01,tz)
            if pl and pr:
                w=max(1,int(pl[2]*20))
                pygame.draw.line(self.surf,tie_c,(pl[0],pl[1]),(pr[0],pr[1]),w)

    def draw_poles(self,cam_z):
        pc=(100,100,105)
        for i in range(8):
            cz=cam_z+i*14.0
            # Left/right poles
            self.box(-4.5,1.5,cz,0.09,3.0,0.09,pc)
            self.box(4.5,1.5,cz,0.09,3.0,0.09,pc)
            # Cross bar
            self.box(0,3.2,cz,9.0,0.07,0.07,pc)

    def draw_building(self,bx,bz,bw,bh,bd,theme):
        tc=THEMES[theme]
        bc=tc["bld"]
        dark=tuple(max(0,c-25) for c in bc)
        light=tuple(min(255,c+20) for c in bc)
        self.box(bx,bh/2,bz,bw,bh,bd,
                 {"front":bc,"back":dark,"left":dark,"right":dark,"top":light,"bot":dark})
        # Windows
        wc=YELLOW if theme not in("neon",) else NEON_G
        wr_n=int(bh/2.5); wc_n=max(1,int(bw/1.8))
        for r in range(1,wr_n+1):
            wy=r*2.2
            if wy>bh-1: break
            for c in range(wc_n):
                ox=(c-wc_n/2+0.5)*(bw/wc_n)
                self.box(bx+ox,wy,bz-bd/2-0.05,0.28,0.45,0.05,wc)
        # Roof
        self.box(bx,bh+0.1,bz,bw*0.55,0.25,bd*0.55,tc["bld"])


# ══════════════════════════════════════════════════════════════════════
#  CHARACTER
# ══════════════════════════════════════════════════════════════════════

class Character3D:
    """Persistent — created once per run, not every frame"""
    def __init__(self,cd):
        self.bc=cd["body"]; self.hc=cd["hair"]
        self.pc=cd["pants"];self.sc=cd["shoe"]
        self.t=0.0; self.wire=False

    def tick(self,dt,spd):
        self.t+=dt*clamp(spd/10,0.5,5)*3.2

    def draw(self,ren,px,py,pz,rolling=False,lean=0.0,jet=False,inv_blink=False):
        if inv_blink: return
        t=self.t
        lsw=math.sin(t)*0.5 if not rolling else 0.0
        asw=math.sin(t+math.pi)*0.42
        lx=lean*0.16

        # HEAD
        ren.box(px+lx,py+1.64,pz,0.23,0.23,0.23,SKIN,self.wire)
        ren.box(px+lx,py+1.76,pz,0.23,0.07,0.23,self.hc,self.wire)
        for ex in(-0.07,0.07):
            ren.box(px+lx+ex,py+1.63,pz-0.12,0.04,0.04,0.02,BLACK,self.wire)
        ren.box(px+lx,py+1.54,pz-0.12,0.09,0.025,0.02,DKRED,self.wire)

        # TORSO
        tc={f:self.bc for f in("front","back","top","bot")}
        tc["left"]=tuple(max(0,c-20) for c in self.bc)
        tc["right"]=tuple(min(255,c+20) for c in self.bc)
        ren.box(px+lx,py+1.12,pz,0.32,0.46,0.19,tc,self.wire)

        # HIPS
        ren.box(px+lx,py+0.78,pz,0.28,0.20,0.17,self.pc,self.wire)

        if rolling:
            ren.box(px,py+0.26,pz,0.40,0.40,0.40,self.pc,self.wire)
        else:
            ol=lsw*0.28; or_=(-lsw)*0.28
            # LEFT LEG
            ren.box(px+lx-0.11,py+0.64+ol*0.3,pz+ol,0.12,0.40,0.12,self.pc,self.wire)
            ren.box(px+lx-0.11,py+0.38+ol*0.3,pz+ol+0.07,0.13,0.09,0.21,self.sc,self.wire)
            # RIGHT LEG
            ren.box(px+lx+0.11,py+0.64+or_*0.3,pz+or_,0.12,0.40,0.12,self.pc,self.wire)
            ren.box(px+lx+0.11,py+0.38+or_*0.3,pz+or_+0.07,0.13,0.09,0.21,self.sc,self.wire)
            # ARMS
            al=asw*0.30; ar=(-asw)*0.30
            ren.box(px+lx-0.23,py+1.05+al*0.2,pz-al*0.5,0.11,0.34,0.11,SKIN,self.wire)
            ren.box(px+lx+0.23,py+1.05+ar*0.2,pz-ar*0.5,0.11,0.34,0.11,SKIN,self.wire)

        # JETPACK
        if jet:
            ren.box(px+lx,py+1.10,pz+0.15,0.27,0.45,0.13,DKGRAY,self.wire)
            ren.box(px+lx-0.09,py+0.68,pz+0.16,0.08,0.22,0.08,GRAY,self.wire)
            ren.box(px+lx+0.09,py+0.68,pz+0.16,0.08,0.22,0.08,GRAY,self.wire)


# ══════════════════════════════════════════════════════════════════════
#  OBSTACLE / COIN / POWERUP DRAW
# ══════════════════════════════════════════════════════════════════════

def draw_train(ren,ox,oz):
    ren.box(ox,1.0,oz,1.85,2.0,5.6,
            {"front":BLUE,"back":DKBLUE,"left":DKBLUE,"right":DKBLUE,
             "top":(55,55,155),"bot":DKGRAY})
    for wz in(-1.8,-0.6,0.6,1.8):
        ren.box(ox-0.92,1.3,oz+wz,0.04,0.56,0.66,NEON_C)
        ren.box(ox+0.92,1.3,oz+wz,0.04,0.56,0.66,NEON_C)
    ren.box(ox,0.8,oz-2.82,1.85,0.3,0.09,LTGRAY)
    ren.box(ox,0.8,oz-2.86,0.42,0.23,0.09,YELLOW)
    for wz in(-1.8,0.0,1.8):
        for wx in(-0.84,0.84):
            ren.cyl(ox+wx,0.19,oz+wz,0.27,0.17,DKGRAY,segs=8)

def draw_low_barrier(ren,ox,oz):
    ren.box(ox,0.30,oz,1.88,0.62,0.36,RED)
    for sh in(0.12,0.38): ren.box(ox,sh,oz,1.88,0.10,0.37,YELLOW)
    for px in(-0.86,0.86): ren.box(ox+px,0.58,oz,0.09,1.12,0.09,LTGRAY)

def draw_high_barrier(ren,ox,oz):
    ren.box(ox,1.0,oz,1.88,2.0,0.31,RED)
    for sh in(0.3,0.8,1.3,1.8): ren.box(ox,sh,oz,1.88,0.10,0.32,YELLOW)

def draw_barrel(ren,ox,oz):
    ren.cyl(ox,0.42,oz,0.39,0.82,BROWN,segs=10)
    for by in(0.05,0.42,0.78): ren.cyl(ox,by,oz,0.40,0.09,GRAY,segs=10)
    ren.box(ox,0.88,oz,0.05,0.30,0.05,YELLOW)

def draw_coin(ren,cx,cy,cz,spin_t,ph):
    spin=spin_t*3+ph; cs,sn=math.cos(spin),math.sin(spin)
    r=0.21; segs=10
    tv=[]; bv=[]
    for i in range(segs):
        a=2*math.pi*i/segs
        bx2=r*math.cos(a)*cs; bz2=r*math.cos(a)*sn; by2=r*math.sin(a)
        tv.append((cx+bx2,cy+by2+0.022,cz+bz2))
        bv.append((cx+bx2,cy+by2-0.022,cz+bz2))
    for i in range(segs):
        j=(i+1)%segs
        ren.quad3([bv[i],bv[j],tv[j],tv[i]],GOLD,(0,0,1))
    ren.quad3([tv[0],tv[segs//3],tv[2*segs//3],tv[0]],YELLOW,(0,1,0))

def draw_powerup(ren,px,py,pz,ptype,spin_t,ph):
    spin=spin_t*2+ph
    sc=0.33+0.04*math.sin(spin_t*4)
    col=PU_COL.get(ptype,WHITE)
    ren.box(px,py,pz,sc*0.68,sc*0.68,sc*0.68,col)
    bright=tuple(min(255,c+65) for c in col)
    ren.box(px,py,pz,sc*0.32,sc*0.32,sc*0.32,bright)


# ══════════════════════════════════════════════════════════════════════
#  PARTICLES
# ══════════════════════════════════════════════════════════════════════

class Pt:
    __slots__=["x","y","z","vx","vy","vz","col","life","ml","sz","tp"]
    def __init__(self,x,y,z,vx,vy,vz,col,life,sz=3,tp="dot"):
        self.x=x;self.y=y;self.z=z
        self.vx=vx;self.vy=vy;self.vz=vz
        self.col=col;self.life=life;self.ml=life;self.sz=sz;self.tp=tp

class Particles:
    def __init__(self): self.ps=[]

    def spark(self,x,y,z,n=10):
        for _ in range(n):
            a=random.uniform(0,math.pi*2); sp=random.uniform(1.5,4.5)
            self.ps.append(Pt(x,y,z,math.cos(a)*sp,math.sin(a)*sp*0.5+1.5,
                              random.uniform(-0.8,0.8),
                              random.choice([YELLOW,GOLD,WHITE]),
                              random.uniform(0.25,0.65),random.randint(3,6),"spark"))

    def explode(self,x,y,z):
        for _ in range(28):
            a=random.uniform(0,math.pi*2); sp=random.uniform(2,9)
            col=random.choice([RED,ORANGE,YELLOW,(255,255,80)])
            self.ps.append(Pt(x,y,z,math.cos(a)*sp,random.uniform(1,7),
                              math.sin(a)*sp*0.4,col,random.uniform(0.3,0.9),
                              random.randint(4,10),"spark"))

    def dust(self,x,y,z):
        for _ in range(7):
            self.ps.append(Pt(x+random.uniform(-0.4,0.4),y+0.05,z,
                              random.uniform(-1.5,1.5),random.uniform(0.5,2.5),
                              random.uniform(-0.5,0.5),GRAY,
                              random.uniform(0.3,0.65),random.randint(2,5),"smoke"))

    def jet(self,x,y,z):
        for ox in(-0.10,0.10):
            col=random.choice([RED,ORANGE,YELLOW])
            self.ps.append(Pt(x+ox,y+0.58,z+0.19,
                              random.uniform(-0.5,0.5),random.uniform(-5,-9),
                              random.uniform(-0.4,0.4),col,
                              random.uniform(0.08,0.24),random.randint(4,9),"flame"))

    def update(self,dt):
        alive=[]
        for p in self.ps:
            p.x+=p.vx*dt; p.y+=p.vy*dt; p.z+=p.vz*dt
            if p.tp!="flame": p.vy-=7*dt
            p.life-=dt
            if p.life>0: alive.append(p)
        self.ps=alive

    def draw(self,ren):
        pv=ren.pv; surf=ren.surf
        for p in self.ps:
            proj=proj_pt(pv,p.x,p.y,p.z)
            if not proj: continue
            sx,sy,depth=proj
            a=clamp(p.life/p.ml,0,1)
            col=tuple(int(c*a) for c in p.col)
            sz=max(1,int(p.sz*(1-depth*0.4)))
            pygame.draw.circle(surf,col,(sx,sy),sz)


# ══════════════════════════════════════════════════════════════════════
#  SPAWNERS
# ══════════════════════════════════════════════════════════════════════

class ObstSpawner:
    def __init__(self): self.nz=45.0
    def spawn(self,dm=1.0):
        z=self.nz
        kind=random.choices([OT_TRAIN,OT_LOW,OT_HIGH,OT_BARREL],
                            weights=[28,22,22,18])[0]
        obs=[]
        if kind==OT_TRAIN:
            l=random.randint(0,2); obs.append(dict(type=OT_TRAIN,lane=l,z=z))
        elif kind==OT_LOW:
            ls=random.sample([0,1,2],random.randint(1,2))
            for l in ls: obs.append(dict(type=OT_LOW,lane=l,z=z))
        elif kind==OT_HIGH:
            obs.append(dict(type=OT_HIGH,lane=random.randint(0,2),z=z))
        else:
            for l in random.sample([0,1,2],random.randint(1,3)):
                obs.append(dict(type=OT_BARREL,lane=l,z=z+random.uniform(0,1.5)))
        # Ensure not all 3 lanes blocked for trains/barriers
        used=[o["lane"] for o in obs if o["type"] in(OT_LOW,OT_HIGH)]
        if len(used)==3: obs.pop()
        gap=clamp(random.uniform(10,22)/dm,6,22)
        self.nz=z+gap
        return obs

class CoinSpawner:
    def __init__(self): self.nz=22.0
    def spawn(self):
        z=self.nz; lane=random.randint(0,2)
        pat=random.choice(["row","arc","zigzag","scatter"])
        coins=[]
        if pat=="row":
            for i in range(10):
                coins.append(dict(lane=lane,y=0.65,z=z+i*1.2,ph=i*0.3))
        elif pat=="arc":
            for i in range(10):
                coins.append(dict(lane=lane,y=0.65+math.sin(i/9*math.pi)*2.1,
                                  z=z+i*1.1,ph=i*0.4))
        elif pat=="zigzag":
            for i in range(10):
                coins.append(dict(lane=i%3,y=0.65,z=z+i*1.1,ph=i*0.3))
        else:
            for i in range(8):
                coins.append(dict(lane=random.randint(0,2),
                                  y=random.uniform(0.4,1.6),
                                  z=z+random.uniform(0,13),ph=random.uniform(0,6.28)))
        self.nz=z+random.uniform(9,18)
        return coins

class BldSpawner:
    def __init__(self): self.nl=8.0; self.nr=8.0
    def spawn(self,cam_z,ahead=60):
        blds=[]
        while self.nl<cam_z+ahead:
            blds.append(self._mk(-1,self.nl)); self.nl+=random.uniform(8,22)
        while self.nr<cam_z+ahead:
            blds.append(self._mk(1,self.nr)); self.nr+=random.uniform(8,22)
        return blds
    def _mk(self,side,z):
        import random as _r
        bx=side*(_r.uniform(6.5,10.0))
        return dict(side=side,bx=bx,z=z,w=_r.uniform(3,7),
                    h=_r.uniform(5,22),d=_r.uniform(3.5,8))


# ══════════════════════════════════════════════════════════════════════
#  AUTOPILOT
# ══════════════════════════════════════════════════════════════════════

class Autopilot:
    def __init__(self): self.on=False
    def decide(self,lane,wz,speed,obs):
        look=max(9,speed*0.6); danger=[0.0,0.0,0.0]
        for o in obs:
            d=o["z"]-wz
            if 0.5<d<look:
                w=9/max(0.1,d)
                danger[o["lane"]]+=w*(1.6 if o["type"]==OT_TRAIN else 1.0)
        tl,jump,roll=lane,False,False
        if danger[lane]>0.4:
            ahead=[o for o in obs if o["lane"]==lane and 0.5<(o["z"]-wz)<look*0.5]
            if ahead:
                ot=ahead[0]["type"]
                safe=sorted(range(3),key=lambda l2:danger[l2])[0]
                if ot==OT_LOW: roll=True
                elif ot==OT_HIGH and danger[safe]>danger[lane]*0.5: jump=True
                else: tl=safe if safe!=lane else lane
        return tl,jump,roll


# ══════════════════════════════════════════════════════════════════════
#  SAVE / LOAD
# ══════════════════════════════════════════════════════════════════════

DEFAULT_SAVE=dict(hi=0,coins=0,dist=0.0,runs=0,achs=[],lb=[],char=0,theme="city")

def load_save():
    try:
        with open(SAVE_FILE) as f: d=json.load(f)
        for k,v in DEFAULT_SAVE.items():
            if k not in d: d[k]=copy.deepcopy(v)
        return d
    except: return copy.deepcopy(DEFAULT_SAVE)

def save_data(d):
    try:
        with open(SAVE_FILE,"w") as f: json.dump(d,f,indent=2)
    except: pass


# ══════════════════════════════════════════════════════════════════════
#  FONTS
# ══════════════════════════════════════════════════════════════════════

def make_fonts():
    fn=pygame.font.match_font("segoeui,arialrounded,arial,freesansbold")
    fm=pygame.font.match_font("consolas,couriernew,monospace")
    def F(size): return pygame.font.Font(fn,size) if fn else pygame.font.SysFont(None,size)
    def Fm(size): return pygame.font.Font(fm,size) if fm else pygame.font.SysFont(None,size)
    return dict(huge=F(58),big=F(38),med=F(26),sm=F(18),tiny=Fm(14))


# ══════════════════════════════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════════════════════════════

class HUD:
    def __init__(self,fonts):
        self.f=fonts
        self.sv=0.0; self.cv=0.0
        self.ach_q=deque(); self.ach_t=0.0; self.ach_txt=""
        self.combo_txt=""; self.combo_t=0.0
        self.warn_txt=""; self.warn_t=0.0
        self.flash_t=0.0; self.flash_col=WHITE
        self.flash_surf=pygame.Surface((SW,SH),pygame.SRCALPHA)

    def push_ach(self,name): self.ach_q.append(name)
    def combo(self,txt): self.combo_txt=txt; self.combo_t=1.8
    def warn(self,txt): self.warn_txt=txt; self.warn_t=1.2
    def flash(self,col,dur=0.18): self.flash_t=dur; self.flash_col=col

    def tick(self,dt,score,coins):
        self.sv=lerp(self.sv,float(score),min(1,dt*10))
        self.cv=lerp(self.cv,float(coins),min(1,dt*12))
        if self.ach_t>0: self.ach_t-=dt
        if self.ach_t<=0 and self.ach_q:
            self.ach_txt=self.ach_q.popleft(); self.ach_t=3.2
        for attr in("flash_t","combo_t","warn_t"):
            v=getattr(self,attr); setattr(self,attr,max(0,v-dt))

    def _txt(self,surf,text,font,col,x,y,center=False):
        s=font.render(text,True,(0,0,0))
        r=s.get_rect()
        if center: r.centerx=x
        else: r.x=x
        r.y=y; surf.blit(s,(r.x+2,r.y+2))
        s=font.render(text,True,col)
        r=s.get_rect()
        if center: r.centerx=x
        else: r.x=x
        r.y=y; surf.blit(s,r)

    def _bar(self,surf,x,y,w,h,pct,col):
        pygame.draw.rect(surf,(35,35,35),(x,y,w,h),border_radius=3)
        fw=int(w*clamp(pct,0,1))
        if fw>0: pygame.draw.rect(surf,col,(x,y,fw,h),border_radius=3)
        pygame.draw.rect(surf,(70,70,70),(x,y,w,h),1,border_radius=3)

    def draw(self,surf,g):
        f=self.f
        # Top bar
        bar=pygame.Surface((SW,58),pygame.SRCALPHA); bar.fill((0,0,0,110))
        surf.blit(bar,(0,0))
        # Score
        self._txt(surf,f"SCORE  {int(self.sv):>10}",f["big"],WHITE,12,7)
        # Coins
        self._txt(surf,f"● {int(self.cv)}",f["big"],YELLOW,SW//2,7,center=True)
        # Distance
        self._txt(surf,f"{g['dist']:.0f} m",f["big"],GREEN,SW-160,7)
        # HP
        for i in range(3):
            c=RED if i<g["hp"] else (55,15,15)
            pygame.draw.circle(surf,c,(14+i*32,70),11)
            pygame.draw.circle(surf,BLACK,(14+i*32,70),11,2)
        # Speed
        self._txt(surf,f"SPD  {g['spd']:>7.1f}",f["med"],CYAN,SW-200,43)
        self._bar(surf,SW-200,64,186,9,g["spd"]/MAX_SPEED,CYAN)
        # Pups
        py=88
        for ptype,rem in list(g["pups"].items())[:5]:
            dur=PU_DUR.get(ptype,10)
            col=PU_COL.get(ptype,WHITE)
            lbl=PU_LBL.get(ptype,"?")
            self._txt(surf,lbl,f["sm"],col,12,py)
            self._bar(surf,54,py+2,128,11,rem/dur,col)
            self._txt(surf,f"{rem:.1f}s",f["tiny"],col,188,py+2)
            py+=22
        # Mult badge
        if g["mult"]>1:
            self._txt(surf,f"×{g['mult']}",f["big"],ORANGE,SW//2+90,5,center=True)
        # Streak
        if g["streak"]>=5:
            c=lerp_col(YELLOW,RED,clamp((g["streak"]-5)/15,0,1))
            self._txt(surf,f"🔥{g['streak']}×",f["med"],c,SW//2-130,10,center=True)
        # Bottom
        bot=pygame.Surface((SW,36),pygame.SRCALPHA); bot.fill((0,0,0,80))
        surf.blit(bot,(0,SH-36))
        m,s2=divmod(int(g["time"]),60)
        self._txt(surf,f"TIME {m:02d}:{s2:02d}",f["sm"],LTGRAY,12,SH-28)
        self._txt(surf,f"FPS {g['fps']}",f["tiny"],DKGRAY,SW-70,SH-20)
        # Minimap
        mx,my,mw,mh=SW//2-60,SH-35,120,29
        pygame.draw.rect(surf,(18,18,18,180),(mx,my,mw,mh),border_radius=4)
        pygame.draw.rect(surf,(70,70,70),(mx,my,mw,mh),1,border_radius=4)
        for li in(1,2): pygame.draw.line(surf,(55,55,55),(mx+li*mw//3,my),(mx+li*mw//3,my+mh))
        pmx=mx+(g["lane"]*mw//3)+mw//6
        pygame.draw.polygon(surf,GREEN,[(pmx,my+3),(pmx-7,my+mh-3),(pmx+7,my+mh-3)])
        # Autopilot
        if g["ap"]:
            aps=pygame.Surface((180,30),pygame.SRCALPHA); aps.fill((90,0,190,155))
            surf.blit(aps,(SW//2-90,SH-76))
            pygame.draw.rect(surf,MAGENTA,(SW//2-90,SH-76,180,30),2,border_radius=4)
            self._txt(surf,"◈ AUTOPILOT ◈",f["sm"],WHITE,SW//2,SH-70,center=True)
        # God mode
        if g["god"]:
            self._txt(surf,"✦ GOD MODE ✦",f["med"],YELLOW,12,SH-70)
        # Ach popup
        if self.ach_t>0:
            av=clamp(min(self.ach_t,3.2-self.ach_t)/0.5,0,1)
            as_=pygame.Surface((360,52),pygame.SRCALPHA); as_.fill((18,18,18,int(200*av)))
            surf.blit(as_,(SW//2-180,SH//2-80))
            pygame.draw.rect(surf,YELLOW,(SW//2-180,SH//2-80,360,52),2,border_radius=6)
            self._txt(surf,"★ ACHIEVEMENT ★",f["sm"],YELLOW,SW//2,SH//2-76,center=True)
            self._txt(surf,self.ach_txt,f["med"],WHITE,SW//2,SH//2-54,center=True)
        # Combo
        if self.combo_t>0:
            sc2=1+0.28*math.sin(self.combo_t*8)
            cs=f["big"].render(self.combo_txt,True,ORANGE)
            cw,ch=f["big"].size(self.combo_txt)
            cs2=pygame.transform.scale(cs,(int(cw*sc2),int(ch*sc2)))
            surf.blit(cs2,cs2.get_rect(center=(SW//2,SH//2+65)))
        # Warning
        if self.warn_t>0:
            pulse=0.5+0.5*math.sin(time.time()*12)
            c=lerp_col(DKRED,RED,pulse)
            self._txt(surf,self.warn_txt,f["big"],c,SW//2,SH-118,center=True)
        # Flash
        if self.flash_t>0:
            av=int(clamp(self.flash_t/0.18,0,1)*88)
            self.flash_surf.fill((*self.flash_col,av))
            surf.blit(self.flash_surf,(0,0))


# ══════════════════════════════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════════════════════════════

class Menu:
    def __init__(self,screen,fonts,save):
        self.sc=screen; self.f=fonts; self.sv=save
        self.clk=pygame.time.Clock()

    def _clear(self,col=(6,6,18)): self.sc.fill(col)

    def _bg(self,t):
        for i in range(14):
            y=(i*60+int(t*75))%SH
            pygame.draw.line(self.sc,(20+i%3*12,20+i%3*12,35+i%3*12),(0,y),(SW,y),1)

    def _txt(self,text,font,col,x,y,center=False):
        s=font.render(text,True,BLACK)
        r=s.get_rect()
        if center: r.centerx=x
        else: r.x=x
        r.y=y; self.sc.blit(s,(r.x+2,r.y+2))
        s=font.render(text,True,col); r=s.get_rect()
        if center: r.centerx=x
        else: r.x=x
        r.y=y; self.sc.blit(s,r)

    def main(self):
        items=[("▶  PLAY","play"),("🏆 LEADERBOARD","lb"),
               ("❓ CONTROLS","ctrl"),("✖  QUIT","quit")]
        sel=0; t0=time.time()
        while True:
            dt=self.clk.tick(60)/1000; t=time.time()-t0
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: return "quit"
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_UP: sel=(sel-1)%len(items)
                    if ev.key==pygame.K_DOWN: sel=(sel+1)%len(items)
                    if ev.key in(pygame.K_RETURN,pygame.K_KP_ENTER): return items[sel][1]
                    if ev.key==pygame.K_ESCAPE: return "quit"
            self._clear((4,4,16)); self._bg(t)
            pulse=abs(math.sin(t*1.2))
            tc=lerp_col(CYAN,NEON_P,pulse)
            self._txt("SUBWAY SURFERS",self.f["huge"],tc,SW//2,22,True)
            self._txt("REMASTERED PYTHON EDITION",self.f["sm"],GRAY,SW//2,88,True)
            hs=self.sv.get("hi",0); coins=self.sv.get("coins",0)
            self._txt(f"HIGH SCORE:  {hs:,}",self.f["big"],YELLOW,SW//2,130,True)
            self._txt(f"● {coins:,}  total coins",self.f["sm"],GREEN,SW//2,178,True)
            # Char selector
            chars_x=SW//2-len(CHARS)*36
            for i,c in enumerate(CHARS):
                cx=chars_x+i*72; sel_c=self.sv.get("char",0)
                col=c["body"]; r=(cx-28,215,56,42)
                if i==sel_c:
                    pygame.draw.rect(self.sc,(30,30,70),r,border_radius=8)
                    pygame.draw.rect(self.sc,CYAN,r,2,border_radius=8)
                else:
                    pygame.draw.rect(self.sc,(18,18,28),r,border_radius=8)
                    pygame.draw.rect(self.sc,(50,50,60),r,1,border_radius=8)
                pygame.draw.circle(self.sc,c["body"],(cx,233),14)
                pygame.draw.circle(self.sc,c["hair"],(cx,224),8)
                ns=self.f["tiny"].render(c["name"],True,GRAY)
                self.sc.blit(ns,(cx-ns.get_width()//2,256))
            for ev2 in []: pass  # char click handled below
            # Keys for char select
            keys=pygame.key.get_pressed()
            # Menu items
            for i,(lbl,_) in enumerate(items):
                y=292+i*56
                if i==sel:
                    pygame.draw.rect(self.sc,(28,28,75),(SW//2-195,y-4,390,46),border_radius=8)
                    pygame.draw.rect(self.sc,CYAN,(SW//2-195,y-4,390,46),2,border_radius=8)
                    c2=CYAN
                else: c2=LTGRAY
                self._txt(lbl,self.f["med"],c2,SW//2,y,True)
            self._txt("← → select character  |  ↑↓ menu  |  ENTER confirm",
                      self.f["tiny"],DKGRAY,SW//2,SH-24,True)
            pygame.display.flip()

    def leaderboard(self):
        lb=sorted(self.sv.get("lb",[]),key=lambda x:x.get("score",0),reverse=True)
        t0=time.time()
        while True:
            self.clk.tick(60)
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: return
                if ev.type in(pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): return
            self._clear((4,4,14)); self._bg(time.time()-t0)
            self._txt("LEADERBOARD",self.f["big"],YELLOW,SW//2,18,True)
            medals=["🥇","🥈","🥉"]
            for i,e in enumerate(lb[:10]):
                y=72+i*46
                m=medals[i] if i<3 else f"#{i+1}"
                row=f"{m}  {e.get('score',0):>12,}  {e.get('dist',0):>8.0f}m  ●{e.get('coins',0)}"
                c=YELLOW if i==0 else LTGRAY if i<3 else GRAY
                self._txt(row,self.f["sm"],c,110,y)
            self._txt("Any key to return",self.f["tiny"],DKGRAY,SW//2,SH-24,True)
            pygame.display.flip()

    def controls(self):
        lines=["← → Change lane","↑ / SPACE  Jump (double-jump)","↓  Roll / slide",
               "SHIFT  Sprint    |    B  Brake","A  Autopilot     |    G  God Mode",
               "P / ESC  Pause   |    C  Camera","T  Theme cycle   |    N  Night vision",
               "J  Jetpack   M  Slow-mo   X  ×5","1-6  Speed presets   0  Auto speed"]
        t0=time.time()
        while True:
            self.clk.tick(60)
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: return
                if ev.type in(pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN): return
            self._clear((4,6,14)); self._bg(time.time()-t0)
            self._txt("CONTROLS",self.f["big"],CYAN,SW//2,22,True)
            for i,ln in enumerate(lines):
                self._txt(ln,self.f["med"],WHITE,SW//2,88+i*52,True)
            self._txt("Any key to return",self.f["tiny"],DKGRAY,SW//2,SH-24,True)
            pygame.display.flip()

    def game_over(self,score,dist,coins,streak,new_hi):
        choices=[("▶  PLAY AGAIN","play"),("🏠  MAIN MENU","menu")]
        sel=0; t0=time.time()
        while True:
            dt=self.clk.tick(60)/1000; t=time.time()-t0
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: return "quit"
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_UP: sel=0
                    if ev.key==pygame.K_DOWN: sel=1
                    if ev.key in(pygame.K_RETURN,pygame.K_KP_ENTER): return choices[sel][1]
                    if ev.key==pygame.K_r: return "play"
                    if ev.key in(pygame.K_m,pygame.K_ESCAPE): return "menu"
            self._clear((16,3,3)); self._bg(t*0.5)
            sc2=1+0.05*math.sin(t*3)
            go=self.f["huge"].render("GAME  OVER",True,RED)
            gw,gh=int(go.get_width()*sc2),int(go.get_height()*sc2)
            go2=pygame.transform.scale(go,(gw,gh))
            self.sc.blit(go2,go2.get_rect(centerx=SW//2,y=18))
            if new_hi:
                self._txt("★  NEW HIGH SCORE!  ★",self.f["big"],YELLOW,SW//2,100,True)
            y=148
            for lbl,val,col in[("SCORE",f"{score:,}",WHITE if not new_hi else YELLOW),
                                ("DISTANCE",f"{dist:.0f} m",GREEN),
                                ("COINS",f"● {coins}",YELLOW),
                                ("MAX STREAK",f"{streak}×",ORANGE)]:
                self._txt(f"{lbl:<14}",self.f["med"],GRAY,SW//2-200,y)
                self._txt(val,self.f["med"],col,SW//2+60,y); y+=46
            for i,(lbl,_) in enumerate(choices):
                cy=SH-130+i*54
                if i==sel:
                    pygame.draw.rect(self.sc,(45,45,115),(SW//2-178,cy-6,356,44),border_radius=8)
                    pygame.draw.rect(self.sc,CYAN,(SW//2-178,cy-6,356,44),2,border_radius=8)
                self._txt(lbl,self.f["med"],CYAN if i==sel else LTGRAY,SW//2,cy,True)
            self._txt("R=Retry  M=Menu  ↑↓ Select  ENTER Confirm",
                      self.f["tiny"],DKGRAY,SW//2,SH-18,True)
            pygame.display.flip()

    def pause(self,game):
        items=[("▶  RESUME","resume"),("A  AUTOPILOT","ap"),
               ("G  GOD MODE","god"),("↩  MAIN MENU","menu")]
        sel=0
        while True:
            self.clk.tick(60)
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: return "menu"
                if ev.type==pygame.KEYDOWN:
                    if ev.key==pygame.K_UP: sel=(sel-1)%len(items)
                    if ev.key==pygame.K_DOWN: sel=(sel+1)%len(items)
                    if ev.key in(pygame.K_RETURN,pygame.K_KP_ENTER):
                        act=items[sel][1]
                        if act=="resume": return "resume"
                        if act=="menu": return "menu"
                        if act=="ap": game["autopilot"].on=not game["autopilot"].on
                        if act=="god": game["godmode"]=not game["godmode"]
                    if ev.key in(pygame.K_ESCAPE,pygame.K_p): return "resume"
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,170))
            self.sc.blit(ov,(0,0))
            pw,ph=440,68+len(items)*56
            px,py=SW//2-pw//2,SH//2-ph//2
            pygame.draw.rect(self.sc,(10,10,30),(px,py,pw,ph),border_radius=12)
            pygame.draw.rect(self.sc,CYAN,(px,py,pw,ph),2,border_radius=12)
            self._txt("PAUSED",self.f["big"],CYAN,SW//2,py+14,True)
            ap_str="ON" if game["autopilot"].on else "OFF"
            god_str="ON" if game["godmode"] else "OFF"
            for i,(lbl,_) in enumerate(items):
                lbl2=lbl
                if "AUTOPILOT" in lbl: lbl2=f"A  AUTOPILOT: {ap_str}"
                if "GOD" in lbl: lbl2=f"G  GOD MODE: {god_str}"
                y=py+66+i*54
                if i==sel:
                    pygame.draw.rect(self.sc,(28,28,78),(px+10,y-4,pw-20,44),border_radius=6)
                    pygame.draw.rect(self.sc,CYAN,(px+10,y-4,pw-20,44),2,border_radius=6)
                self._txt(lbl2,self.f["sm"],CYAN if i==sel else LTGRAY,SW//2,y,True)
            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════════════════════════════════

def run(screen,save,fonts,menu):
    clk=pygame.time.Clock()
    ren=Renderer(screen)
    hud=HUD(fonts)

    # ── State ────────────────────────────────────────────────────────
    ci=save.get("char",0)
    char=Character3D(CHARS[ci])
    theme=save.get("theme","city")
    ap=Autopilot()
    pts=Particles()

    g=dict(
        lane=1, lf=1, lt=1, lct=0, lchanging=False,
        x=LANE_X[1], y=0.0, wz=0.0, vy=0.0,
        inair=False, jumpcount=0, rolling=False, rollt=0,
        lean=0.0, dist=0.0, spd=BASE_SPEED, bspd=BASE_SPEED,
        manual_spd=None, sprinting=False, braking=False,
        score=0, coins=0, mult=1,
        streak=0, max_streak=0, combo=0, last_coin_t=0.0,
        hp=3, invt=0.0, alive=True, godmode=False,
        pups={}, jet_alt=0.0,
        obs=[], coinlist=[], pups_world=[], blds=[],
        obs_sp=ObstSpawner(), coin_sp=CoinSpawner(), bld_sp=BldSpawner(),
        cam_eye=[0,1.9,-4.0], cam_at=[0,1.1,14.0],
        cam_bob=0.0, cam_shake=0.0, cam_mode=0,
        fov=BASE_FOV, cin_t=0.0,
        time=0.0, fps=60, _ff=0, _ft=0.0,
        spin_t=0.0, danger=False, nv=False,
        autopilot=ap, theme=theme,
        ap_obj=ap, godmode_ref=False,
    )
    g["ap"]=ap; g["godmode"]=False

    # Pre-populate world
    for _ in range(9): g["coinlist"].extend(g["coin_sp"].spawn())
    for _ in range(5): g["obs"].extend(g["obs_sp"].spawn())
    g["blds"].extend(g["bld_sp"].spawn(0))

    last_t=time.time()
    result="menu"

    while True:
        now=time.time(); dt=min(now-last_t,0.05); last_t=now
        g["_ff"]+=1; g["_ft"]+=dt
        if g["_ft"]>=0.5:
            g["fps"]=int(g["_ff"]/g["_ft"]); g["_ff"]=0; g["_ft"]=0.0

        # ── EVENTS ────────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return "quit"
            if ev.type==pygame.KEYDOWN:
                k=ev.key
                if k in(pygame.K_p,pygame.K_ESCAPE):
                    r=menu.pause(g)
                    if r=="menu": return "menu"
                    last_t=time.time(); continue
                if not g["ap"].on:
                    if k==pygame.K_LEFT:  _change_lane(g,-1)
                    if k==pygame.K_RIGHT: _change_lane(g,1)
                    if k in(pygame.K_UP,pygame.K_SPACE): _jump(g,pts)
                    if k==pygame.K_DOWN: _roll(g)
                if k==pygame.K_a: g["ap"].on=not g["ap"].on
                if k==pygame.K_g: g["godmode"]=not g["godmode"]; hud.flash(YELLOW)
                if k==pygame.K_c: g["cam_mode"]=(g["cam_mode"]+1)%3
                if k==pygame.K_t:
                    idx=THEME_KEYS.index(g["theme"])
                    g["theme"]=THEME_KEYS[(idx+1)%len(THEME_KEYS)]
                    save["theme"]=g["theme"]
                if k==pygame.K_n: g["nv"]=not g["nv"]
                if k==pygame.K_j: g["pups"][PU_JETPACK]=PU_DUR[PU_JETPACK]
                if k==pygame.K_m: g["pups"][PU_SLOW]=PU_DUR[PU_SLOW]
                if k==pygame.K_x: g["pups"][PU_X5]=PU_DUR[PU_X5]
                if k==pygame.K_1: g["manual_spd"]=12.0
                if k==pygame.K_2: g["manual_spd"]=50.0
                if k==pygame.K_3: g["manual_spd"]=150.0
                if k==pygame.K_4: g["manual_spd"]=350.0
                if k==pygame.K_5: g["manual_spd"]=600.0
                if k==pygame.K_6: g["manual_spd"]=MAX_SPEED
                if k==pygame.K_0: g["manual_spd"]=None
                if k in(pygame.K_PLUS,pygame.K_EQUALS):
                    g["manual_spd"]=min(MAX_SPEED,(g["manual_spd"] or g["spd"])*1.4)
                if k==pygame.K_MINUS:
                    g["manual_spd"]=max(2,(g["manual_spd"] or g["spd"])*0.7)

        held=pygame.key.get_pressed()
        g["sprinting"]=bool(held[pygame.K_LSHIFT] or held[pygame.K_RSHIFT])
        g["braking"]=bool(held[pygame.K_b])

        if not g["alive"]:
            # Save stats
            new_hi=g["score"]>save.get("hi",0)
            if new_hi: save["hi"]=g["score"]
            save["coins"]=save.get("coins",0)+g["coins"]
            save["dist"]=save.get("dist",0.0)+g["dist"]
            save["runs"]=save.get("runs",0)+1
            lb=save.get("lb",[]); lb.append({"score":g["score"],"dist":g["dist"],"coins":g["coins"]})
            lb.sort(key=lambda x:x.get("score",0),reverse=True); save["lb"]=lb[:10]
            save_data(save)
            return menu.game_over(g["score"],g["dist"],g["coins"],g["max_streak"],new_hi)

        # ── UPDATE ────────────────────────────────────────────────────
        _update(g,dt,char,pts,hud)

        # ── RENDER ────────────────────────────────────────────────────
        theme=g["theme"]; tc=THEMES[theme]
        ren.fc=tc["fog"]; ren.fd=float(tc["fog_d"]); ren.amb=tc["amb"]
        ren.sd=[0.5,0.82,0.32]

        proj_m=mpersp(g["fov"],SW/SH,NEAR,FAR)
        view_m=mlookat(g["cam_eye"],g["cam_at"],[0,1,0])
        ren.pv=mmul(proj_m,view_m)

        ren.draw_sky(theme)
        ren.draw_ground(theme,g["wz"])
        ren.draw_track(theme,g["wz"])
        ren.draw_poles(g["wz"])

        # Buildings
        for b in g["blds"]:
            dz=b["z"]-g["wz"]
            if -5<dz<FAR: ren.draw_building(b["bx"],b["z"],b["w"],b["h"],b["d"],theme)

        # World objects sorted back-to-front
        objs=[]
        for o in g["obs"]:
            d=o["z"]-g["wz"]
            if -3<d<FAR: objs.append(("obs",o,d))
        for c in g["coinlist"]:
            d=c["z"]-g["wz"]
            if 0<d<FAR: objs.append(("coin",c,d))
        for p in g["pups_world"]:
            d=p["z"]-g["wz"]
            if 0<d<FAR: objs.append(("pu",p,d))
        objs.sort(key=lambda x:x[2],reverse=True)

        for kind,obj,_ in objs:
            if kind=="obs":
                ot=obj["type"]; lx=LANE_X[obj["lane"]]
                if ot==OT_TRAIN: draw_train(ren,lx,obj["z"])
                elif ot==OT_LOW: draw_low_barrier(ren,lx,obj["z"])
                elif ot==OT_HIGH: draw_high_barrier(ren,lx,obj["z"])
                elif ot==OT_BARREL: draw_barrel(ren,lx,obj["z"])
            elif kind=="coin":
                draw_coin(ren,LANE_X[obj["lane"]],obj["y"],obj["z"],g["spin_t"],obj["ph"])
            elif kind=="pu":
                draw_powerup(ren,LANE_X[obj["lane"]],0.7,obj["z"],obj["type"],g["spin_t"],obj["ph"])

        # Character
        char_y=g["y"]+g["jet_alt"]
        inv_blink=g["invt"]>0 and int(g["invt"]*9)%2==0
        char.draw(ren,g["x"],char_y,g["wz"]+0.9,
                  rolling=g["rolling"],lean=g["lean"],
                  jet=PU_JETPACK in g["pups"],inv_blink=inv_blink)

        # Particles
        pts.draw(ren)

        # Speed lines
        si=clamp((g["spd"]-120)/600,0,1)
        if si>0.05: _speed_lines(screen,si,g["spin_t"])

        # Danger vignette
        if g["danger"] and g["invt"]<=0:
            pulse=0.4+0.6*abs(math.sin(g["time"]*7))
            alpha=int(pulse*55)
            vig=pygame.Surface((SW,SH),pygame.SRCALPHA)
            for th in range(8,0,-2):
                a=alpha*(9-th)//8
                pygame.draw.rect(vig,(200,20,20,a),(th*4,th*3,SW-th*8,SH-th*6),th)
            screen.blit(vig,(0,0))

        # Night vision
        if g["nv"]:
            nv=pygame.Surface((SW,SH),pygame.SRCALPHA); nv.fill((0,38,0,65))
            screen.blit(nv,(0,0))

        hud.draw(screen,{
            "score":g["score"],"coins":g["coins"],"dist":g["dist"],
            "spd":g["spd"],"hp":g["hp"],"mult":g["mult"],
            "pups":g["pups"],"lane":g["lane"],
            "fps":g["fps"],"ap":g["ap"].on,
            "god":g["godmode"],"streak":g["streak"],"time":g["time"],
        })

        pygame.display.flip()
        clk.tick(FPS)
    return result


def _change_lane(g,d):
    nl=clamp(g["lane"]+d,0,2)
    if nl!=g["lane"] and not g["lchanging"]:
        g["lf"]=g["lane"]; g["lt"]=nl; g["lane"]=nl
        g["lchanging"]=True; g["lct"]=0; g["lean"]=-d*0.46

def _jump(g,pts):
    maxj=3 if PU_SNKRS in g["pups"] else 2
    if g["jumpcount"]<maxj:
        vel=JUMP_VEL*(1.4 if PU_SNKRS in g["pups"] else 0.85**g["jumpcount"])
        g["vy"]=vel; g["inair"]=True; g["jumpcount"]+=1
        pts.dust(g["x"],0,g["wz"])

def _roll(g):
    if not g["inair"] and not g["rolling"]:
        g["rolling"]=True; g["rollt"]=ROLL_DUR

def _update(g,dt,char,pts,hud):
    g["time"]+=dt; g["spin_t"]+=dt

    # Speed
    if g["manual_spd"] is not None:
        tspd=clamp(g["manual_spd"],2,MAX_SPEED)
    else:
        tspd=g["bspd"]
        if g["sprinting"]: tspd=min(tspd*1.55,MAX_SPEED)
        if g["braking"]:   tspd=max(tspd*0.28,4)
        if PU_TURBO in g["pups"]: tspd=min(tspd*1.8,MAX_SPEED)
        if PU_SLOW  in g["pups"]: tspd=max(tspd*0.35,4)
    if g["manual_spd"] is None:
        g["bspd"]=min(g["bspd"]+SPEED_RAMP*dt,MAX_SPEED*0.78)
    g["spd"]=lerp(g["spd"],tspd,min(1,dt*4))
    g["spd"]=clamp(g["spd"],2,MAX_SPEED)
    eff=g["spd"]*(0.35 if PU_SLOW in g["pups"] else 1.0)

    # FOV drift
    g["fov"]=lerp(BASE_FOV,BASE_FOV+26,smoothstep(clamp(g["spd"]/350,0,1)))

    g["wz"]+=eff*dt; g["dist"]+=eff*dt

    # Gravity
    if g["inair"] or g["y"]>0:
        g["vy"]+=GRAVITY*dt; g["y"]+=g["vy"]*dt
        if g["y"]<=0:
            g["y"]=0; g["vy"]=0; g["inair"]=False; g["jumpcount"]=0
            pts.dust(g["x"],0,g["wz"])

    # Roll
    if g["rolling"]: g["rollt"]-=dt;g["rolling"]=g["rollt"]>0

    # Lane change
    if g["lchanging"]:
        g["lct"]+=dt; t2=smoothstep(g["lct"]/LANE_CHANGE_T)
        g["x"]=lerp(LANE_X[g["lf"]],LANE_X[g["lt"]],t2)
        g["lean"]=lerp(g["lean"],0,dt*9)
        if g["lct"]>=LANE_CHANGE_T:
            g["lchanging"]=False; g["x"]=LANE_X[g["lt"]]; g["lean"]=0
    else:
        g["x"]=lerp(g["x"],LANE_X[g["lane"]],dt*18)

    # Jetpack
    if PU_JETPACK in g["pups"]:
        g["jet_alt"]=min(3.8,g["jet_alt"]+dt*5)
        pts.jet(g["x"],g["y"],g["wz"])
    else:
        g["jet_alt"]=max(0,g["jet_alt"]-dt*9)

    char.tick(dt,g["spd"])

    # Pups timer
    exp=[k for k,v in g["pups"].items() if v<=dt]
    for k in exp: del g["pups"][k]
    for k in list(g["pups"]): g["pups"][k]-=dt
    g["mult"]=5 if PU_X5 in g["pups"] else 3 if PU_X3 in g["pups"] else 2 if PU_X2 in g["pups"] else 1

    # Invincibility
    g["invt"]=max(0,g["invt"]-dt)

    # Autopilot
    if g["ap"].on:
        tl,jmp,rol=g["ap"].decide(g["lane"],g["wz"],g["spd"],g["obs"])
        if tl!=g["lane"] and not g["lchanging"]: _change_lane(g,tl-g["lane"])
        if jmp: _jump(g,pts)
        if rol: _roll(g)

    # Camera
    _update_cam(g,dt)

    # Score
    g["score"]+=int(eff*dt*g["mult"])

    # Spawn
    look=g["wz"]+SPAWN_AHEAD
    dm=1+g["dist"]/7000
    while g["obs_sp"].nz<look: g["obs"].extend(g["obs_sp"].spawn(dm))
    while g["coin_sp"].nz<look: g["coinlist"].extend(g["coin_sp"].spawn())
    g["blds"].extend(g["bld_sp"].spawn(g["wz"]))
    if random.random()<0.0007 or (not g["pups_world"] and random.random()<0.002):
        pt=random.choice(list(PU_DUR.keys()))
        g["pups_world"].append(dict(type=pt,lane=random.randint(0,2),
                                    z=look,ph=random.uniform(0,6.28)))
    # Despawn
    cut=g["wz"]-6
    g["obs"]=[o for o in g["obs"] if o["z"]>cut]
    g["coinlist"]=[c for c in g["coinlist"] if c["z"]>cut]
    g["pups_world"]=[p for p in g["pups_world"] if p["z"]>cut]
    g["blds"]=[b for b in g["blds"] if b["z"]>cut-50]

    # Collisions
    char_y=g["y"]+g["jet_alt"]
    for obs in g["obs"]:
        if _check_obs(g,obs,char_y):
            _damage(g,hud,pts); break
    # Coins
    mag=3.0 if PU_MAGNET in g["pups"] else 1.1
    rem=[]
    for c in g["coinlist"]:
        dx=abs(g["x"]-LANE_X[c["lane"]]); dz=abs(c["z"]-g["wz"])
        if dx<mag and dz<mag*1.5:
            now=time.time()
            if now-g["last_coin_t"]<0.6: g["combo"]+=1
            else: g["combo"]=1
            g["last_coin_t"]=now
            amt=g["mult"]; g["coins"]+=amt; g["score"]+=amt*14
            g["streak"]+=1; g["max_streak"]=max(g["max_streak"],g["streak"])
            if g["combo"]>=6: hud.combo(f"COMBO ×{g['combo']}!")
            pts.spark(LANE_X[c["lane"]],c["y"],c["z"])
            rem.append(c)
    for c in rem: g["coinlist"].remove(c)
    # World pups
    rem_p=[]
    for p in g["pups_world"]:
        dx=abs(g["x"]-LANE_X[p["lane"]]); dz=abs(p["z"]-g["wz"])
        if dx<1.4 and dz<1.4:
            g["pups"][p["type"]]=PU_DUR[p["type"]]
            hud.flash(PU_COL.get(p["type"],WHITE))
            rem_p.append(p)
    for p in rem_p: g["pups_world"].remove(p)

    # Danger
    near=[o for o in g["obs"] if o["lane"]==g["lane"] and 0<(o["z"]-g["wz"])<9]
    g["danger"]=bool(near)
    if near and (near[0]["z"]-g["wz"])<5: hud.warn("⚠  OBSTACLE AHEAD  ⚠")

    pts.update(dt)
    hud.tick(dt,g["score"],g["coins"])


def _check_obs(g,obs,char_y):
    if g["invt"]>0 or g["godmode"]: return False
    if PU_JETPACK in g["pups"] and char_y>1.8: return False
    dz=abs(obs["z"]-g["wz"]); dl=abs(obs["lane"]-g["lane"])
    if dl>=1 or dz>3.5: return False
    ot=obs["type"]
    if ot==OT_LOW and (g["rolling"] or g["y"]>0.55): return False
    if ot==OT_HIGH and g["y"]>1.0: return False
    return dl<0.55 and dz<2.8

def _damage(g,hud,pts):
    if g["invt"]>0 or g["godmode"]: return
    if PU_SHIELD in g["pups"]:
        del g["pups"][PU_SHIELD]; hud.flash(CYAN); g["cam_shake"]=0.4
        hud.warn("🛡 SHIELD ABSORBED HIT"); return
    g["hp"]=max(0,g["hp"]-1); g["invt"]=2.4; g["cam_shake"]=0.6
    g["streak"]=0; g["combo"]=0
    hud.flash(RED,0.28)
    pts.explode(g["x"],g["y"]+0.5,g["wz"])
    if g["hp"]<=0: g["alive"]=False

def _update_cam(g,dt):
    g["cam_bob"]+=dt*clamp(g["spd"]/12,0.3,4)*2.8
    bob=math.sin(g["cam_bob"])*0.065
    if g["cam_shake"]>0: g["cam_shake"]-=dt
    sh=math.sin(time.time()*44)*g["cam_shake"]*0.3
    sy2=math.cos(time.time()*40)*g["cam_shake"]*0.22
    cy=g["y"]+g["jet_alt"]
    cm=g["cam_mode"]
    if cm==0:   # behind
        g["cam_eye"]=[g["x"]+sh,1.9+bob+sy2,g["wz"]-4.0]
        g["cam_at"]=[g["x"],cy+1.1,g["wz"]+14]
    elif cm==1: # side
        g["cam_eye"]=[g["x"]-7+sh,2.2+sy2,g["wz"]+2]
        g["cam_at"]=[g["x"],cy+1.0,g["wz"]+5]
    else:       # cinematic
        g["cin_t"]=g.get("cin_t",0)+dt*0.4
        cx=math.sin(g["cin_t"])*6+g["x"]
        g["cam_eye"]=[cx+sh,4.2+sy2,g["wz"]-5.5]
        g["cam_at"]=[g["x"],cy+1.0,g["wz"]+9]

def _speed_lines(surf,intensity,t):
    cx,cy=SW//2,SH//2; n=int(intensity*26)
    for i in range(n):
        angle=(i/n)*math.pi*2+t*0.55
        r0=SH*0.17; r1=SH*(0.21+intensity*0.44*random.random())
        x0,y0=cx+int(math.cos(angle)*r0),cy+int(math.sin(angle)*r0)
        x1,y1=cx+int(math.cos(angle)*r1),cy+int(math.sin(angle)*r1)
        a=int(intensity*75)
        pygame.draw.line(surf,(a,a+18,a+28),(x0,y0),(x1,y1),1)


# ══════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════

def main():
    screen=pygame.display.set_mode((SW,SH),pygame.DOUBLEBUF)
    pygame.display.set_caption(TITLE)
    # Icon
    try:
        icon=pygame.Surface((32,32)); icon.fill(BLUE)
        pygame.draw.circle(icon,YELLOW,(16,16),10)
        pygame.display.set_icon(icon)
    except: pass

    fonts=make_fonts()
    save=load_save()
    menu=Menu(screen,fonts,save)

    print(f"[{TITLE}]")
    print(f"  Runs: {save.get('runs',0)}  |  High Score: {save.get('hi',0):,}")
    print(f"  Save: {SAVE_FILE}")

    action="menu"
    while action!="quit":
        if action=="menu":
            action=menu.main()
        elif action=="lb":
            menu.leaderboard(); action="menu"
        elif action=="ctrl":
            menu.controls(); action="menu"
        elif action=="play":
            action=run(screen,save,fonts,menu)
            save_data(save)
        else:
            break

    save_data(save)
    pygame.quit()
    print(f"\nThanks for playing!")
    print(f"  High Score: {save.get('hi',0):,}")
    print(f"  Total Runs: {save.get('runs',0)}")

if __name__=="__main__":
    main()