#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║       SUBWAY SURFERS 3D  —  ULTIMATE PYGAME EDITION             ║
║   Pure Python + Pygame | Software 3D Renderer | 155+ Features   ║
╚══════════════════════════════════════════════════════════════════╝

INSTALL:   pip install pygame numpy
RUN:       python subway_surfers_3d.py

CONTROLS:
  ← → Arrow Keys  Change lane
  ↑  / SPACE      Jump  (press twice for double-jump)
  ↓               Roll / slide under barriers
  LEFT SHIFT      Sprint
  B               Brake / slow down
  A               Toggle Autopilot  (SHIFT+A cycles AI mode)
  G               God Mode (invincible)
  P / ESC         Pause menu
  C               Cycle camera modes
  T               Cycle environment themes
  N               Night-vision mode
  W               Wireframe overlay
  1-6             Speed presets  (0 = auto)
  + / -           Fine-tune speed
  F               Toggle FPS display
  M               Activate slow-motion
  J               Activate jetpack
  X               Activate x10 multiplier
  H               Toggle hoverboard
  R               Replay last 30 s
  D               Cycle difficulty
"""

# ── Imports ────────────────────────────────────────────────────────────────
import pygame
import math
import random
import time
import json
import os
import sys
import copy
from collections import deque

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("numpy not found – falling back to pure-python math (slower).")

# ── Bootstrap numpy-like helpers if missing ────────────────────────────────
if not HAS_NUMPY:
    class _NP:
        """Tiny numpy stub so the rest of the code works without numpy"""
        def array(self, lst, dtype=None):
            return list(lst)
        def dot(self, a, b):
            return sum(x*y for x,y in zip(a,b))
        def cross(self, a, b):
            return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
        def linalg(self):
            pass
    import types
    np = types.SimpleNamespace()
    np.float32 = float
    _np = _NP()
    np.array  = _np.array
    np.dot    = _np.dot
    np.cross  = _np.cross

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

VERSION     = "3.0-PYGAME-ULTIMATE"
SAVE_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "save_data.json")

SCREEN_W    = 1280
SCREEN_H    = 720
TARGET_FPS  = 60
TITLE       = "Subway Surfers 3D – Ultimate Python Edition"

# 3-D lane X positions
LANES       = [-2.4,  0.0,  2.4]

# Physics
GRAVITY         = -22.0
JUMP_VEL        = 10.5
SUPER_JUMP_VEL  = 16.0
ROLL_DURATION   = 0.55
LANE_CHANGE_T   = 0.16

# World
BASE_SPEED      = 9.0
MAX_SPEED       = 10_000.0
SPEED_RAMP      = 0.45          # units / s²
SPAWN_AHEAD     = 42.0
DESPAWN_BEHIND  = -6.0
FAR_PLANE       = 90.0
NEAR_PLANE      = 0.25
BASE_FOV        = 72.0

# ── Colours (R,G,B) ──────────────────────────────────────────────────────────
C_WHITE    = (255, 255, 255)
C_BLACK    = (  0,   0,   0)
C_YELLOW   = (255, 220,   0)
C_GOLD     = (255, 180,   0)
C_RED      = (220,  40,  40)
C_DKRED    = (140,  20,  20)
C_GREEN    = ( 40, 200,  60)
C_DKGREEN  = ( 20, 120,  40)
C_CYAN     = ( 40, 220, 220)
C_DKCYAN   = ( 20, 140, 140)
C_BLUE     = ( 60, 100, 220)
C_DKBLUE   = ( 30,  50, 140)
C_MAGENTA  = (220,  40, 220)
C_ORANGE   = (255, 140,   0)
C_BROWN    = (140,  80,  30)
C_GRAY     = (160, 160, 160)
C_DKGRAY   = ( 80,  80,  80)
C_LTGRAY   = (210, 210, 210)
C_SKIN     = (240, 190, 150)
C_PURPLE   = (140,  40, 200)
C_NEON_G   = ( 50, 255, 100)
C_NEON_P   = (200,  50, 255)
C_NEON_C   = ( 50, 230, 255)
C_NAVY     = ( 15,  15,  80)

# ── Theme definitions ─────────────────────────────────────────────────────────
THEMES = {
    "city":   {
        "sky_top":   ( 30,  80, 180), "sky_bot":  ( 80, 140, 220),
        "ground":    ( 60,  60,  65), "ground2":  ( 50,  50,  55),
        "building":  ( 90,  90,  95), "bld_acc":  (110, 110, 115),
        "rail":      (180, 180, 185), "tie":      (110,  80,  50),
        "fog":       ( 80, 130, 200), "fog_dist": 60.0,
        "ambient":   0.55,            "sun":      (255, 240, 200),
    },
    "subway": {
        "sky_top":   ( 10,  10,  20), "sky_bot":  ( 20,  20,  35),
        "ground":    ( 30,  30,  35), "ground2":  ( 20,  20,  25),
        "building":  ( 50,  50,  60), "bld_acc":  ( 70,  70,  80),
        "rail":      (140, 140, 150), "tie":      ( 60,  40,  30),
        "fog":       ( 15,  15,  30), "fog_dist": 35.0,
        "ambient":   0.35,            "sun":      (200, 200, 255),
    },
    "desert": {
        "sky_top":   (210, 160,  60), "sky_bot":  (240, 200, 100),
        "ground":    (190, 155,  90), "ground2":  (170, 135,  70),
        "building":  (180, 140,  80), "bld_acc":  (200, 160,  90),
        "rail":      (210, 180, 130), "tie":      (150, 110,  60),
        "fog":       (230, 190, 110), "fog_dist": 55.0,
        "ambient":   0.70,            "sun":      (255, 220, 150),
    },
    "night":  {
        "sky_top":   (  5,   5,  20), "sky_bot":  ( 10,  10,  40),
        "ground":    ( 15,  15,  25), "ground2":  ( 10,  10,  20),
        "building":  ( 20,  20,  50), "bld_acc":  ( 30,  30,  70),
        "rail":      (100, 100, 130), "tie":      ( 50,  30,  20),
        "fog":       (  8,   8,  30), "fog_dist": 30.0,
        "ambient":   0.25,            "sun":      (100, 120, 255),
    },
    "neon":   {
        "sky_top":   (  5,   0,  20), "sky_bot":  ( 15,   5,  40),
        "ground":    ( 10,   0,  30), "ground2":  (  8,   0,  25),
        "building":  ( 30,   5,  60), "bld_acc":  ( 60,  10, 100),
        "rail":      ( 50, 200, 200), "tie":      ( 80,   0, 120),
        "fog":       ( 10,   0,  30), "fog_dist": 28.0,
        "ambient":   0.30,            "sun":      ( 50, 255, 200),
    },
}

# ── Power-up definitions ──────────────────────────────────────────────────────
PU_MAGNET   = "magnet"
PU_SHIELD   = "shield"
PU_X2       = "x2"
PU_X3       = "x3"
PU_X5       = "x5"
PU_X10      = "x10"
PU_JETPACK  = "jetpack"
PU_SNEAKERS = "sneakers"
PU_SLOW     = "slowmo"
PU_TURBO    = "turbo"

PU_DURATION = {
    PU_MAGNET: 12, PU_SHIELD: 8, PU_X2: 15, PU_X3: 12, PU_X5: 10,
    PU_X10: 8, PU_JETPACK: 12, PU_SNEAKERS: 10, PU_SLOW: 6, PU_TURBO: 8,
}
PU_COLOR = {
    PU_MAGNET: C_CYAN, PU_SHIELD: C_BLUE, PU_X2: C_YELLOW, PU_X3: C_YELLOW,
    PU_X5: C_ORANGE, PU_X10: C_RED, PU_JETPACK: C_NEON_C, PU_SNEAKERS: C_GREEN,
    PU_SLOW: C_MAGENTA, PU_TURBO: C_RED,
}
PU_LABEL = {
    PU_MAGNET:"MAG", PU_SHIELD:"SHD", PU_X2:"x2", PU_X3:"x3",
    PU_X5:"x5", PU_X10:"x10", PU_JETPACK:"JET", PU_SNEAKERS:"SNK",
    PU_SLOW:"SLO", PU_TURBO:"TRB",
}

# ── Obstacle types ────────────────────────────────────────────────────────────
OT_TRAIN   = "train"
OT_LOW_BAR = "low_barrier"
OT_HI_BAR  = "hi_barrier"
OT_BARREL  = "barrel"
OT_COMBO   = "combo"
OT_MOVING  = "moving"

# ── Difficulty presets ────────────────────────────────────────────────────────
DIFFICULTIES = {
    "Easy":      {"speed_m": 0.50, "obs_m": 0.50, "ramp": 0.15},
    "Normal":    {"speed_m": 1.00, "obs_m": 1.00, "ramp": 0.45},
    "Hard":      {"speed_m": 1.50, "obs_m": 1.50, "ramp": 1.00},
    "Insane":    {"speed_m": 2.50, "obs_m": 2.00, "ramp": 2.00},
    "Ludicrous": {"speed_m": 5.00, "obs_m": 3.00, "ramp": 5.00},
}

# ── Characters ────────────────────────────────────────────────────────────────
CHARACTERS = [
    {"name": "Jake",   "body": C_CYAN,    "hair": C_YELLOW, "pants": C_BLUE},
    {"name": "Tricky", "body": C_RED,     "hair": C_DKRED,  "pants": C_DKGRAY},
    {"name": "Fresh",  "body": C_GREEN,   "hair": C_GRAY,   "pants": C_BLUE},
    {"name": "Spike",  "body": C_MAGENTA, "hair": C_PURPLE, "pants": C_BLACK},
    {"name": "Yutani", "body": C_NEON_C,  "hair": C_NEON_P, "pants": C_NAVY},
]

# ── Achievements ──────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    ("first_run",    "First Steps",      "Complete your first run"),
    ("coins_100",    "Coin Collector",   "Collect 100 coins in one run"),
    ("coins_1000",   "Gold Rush",        "Collect 1000 total coins"),
    ("dist_500",     "Sprinter",         "Run 500 m in one run"),
    ("dist_2000",    "Marathon",         "Run 2000 m in one run"),
    ("dist_10000",   "Ultra Runner",     "Run 10 000 m in one run"),
    ("speed_500",    "Supersonic",       "Reach speed 500"),
    ("speed_5000",   "Hypersonic",       "Reach speed 5 000"),
    ("speed_10000",  "Lightspeed",       "Reach speed 10 000"),
    ("jetpack_use",  "Up & Away",        "Use the Jetpack"),
    ("shield_use",   "Force Field",      "Use a Shield"),
    ("x10_use",      "Multiplier King",  "Activate x10 multiplier"),
    ("trick_10",     "Trickster",        "Perform 10 tricks"),
    ("streak_20",    "On Fire!",         "Achieve a 20-coin streak"),
    ("godmode",      "Invincible",       "Activate God Mode"),
    ("autopilot",    "AI Driver",        "Run 1000 m on Autopilot"),
    ("run_10",       "Regular Runner",   "Complete 10 runs"),
    ("run_50",       "Veteran",          "Complete 50 runs"),
    ("all_themes",   "World Traveler",   "Play all 5 themes"),
    ("speedrun_1m",  "Speedrunner",      "Score 1 000 000 in one run"),
]

# ── Default save ──────────────────────────────────────────────────────────────
DEFAULT_SAVE = {
    "high_score": 0, "total_coins": 0, "total_distance": 0.0,
    "total_runs": 0, "achievements": [], "level": 1, "xp": 0,
    "longest_run": 0.0, "most_coins_run": 0, "longest_streak": 0,
    "total_tricks": 0, "leaderboard": [], "themes_played": [],
    "upgrades": {
        "coin_doubler": 0, "head_start": 0, "score_booster": 0,
        "magnet_range": 0, "shield_duration": 0, "jetpack_fuel": 0,
    },
    "settings": {
        "theme": "city", "difficulty": "Normal", "char_index": 0,
        "sound": True, "music": True, "show_fps": True,
        "camera": "behind", "fov": BASE_FOV, "head_bob": 0.5,
        "color_grade": "neutral", "wireframe": False,
        "colorblind": False, "fullscreen": False,
    }
}

# ══════════════════════════════════════════════════════════════════════════════
#  MATH  (pure-Python 4×4 matrix math — fast enough at 60 fps)
# ══════════════════════════════════════════════════════════════════════════════

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0.0, 1.0)

def lerp_color(c1, c2, t):
    t = clamp(t, 0, 1)
    return (int(c1[0]+(c2[0]-c1[0])*t),
            int(c1[1]+(c2[1]-c1[1])*t),
            int(c1[2]+(c2[2]-c1[2])*t))

def smoothstep(t):
    t = clamp(t, 0, 1)
    return t * t * (3 - 2 * t)

def apply_fog(color, depth, fog_color, fog_dist):
    t = clamp(depth / fog_dist, 0, 1)
    t = t * t
    return lerp_color(color, fog_color, t)

def apply_light(color, normal, sun_dir, ambient):
    """Simple diffuse + ambient shading"""
    d = max(0.0, normal[0]*sun_dir[0] + normal[1]*sun_dir[1] + normal[2]*sun_dir[2])
    brightness = ambient + (1.0 - ambient) * d
    brightness = clamp(brightness, 0, 1)
    return (int(color[0]*brightness), int(color[1]*brightness), int(color[2]*brightness))

# 4×4 matrix as flat list of 16 floats  (row-major)
def mat_identity():
    return [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

def mat_mul(a, b):
    out = [0]*16
    for r in range(4):
        for c in range(4):
            s = 0.0
            for k in range(4):
                s += a[r*4+k] * b[k*4+c]
            out[r*4+c] = s
    return out

def mat_translate(tx, ty, tz):
    m = mat_identity()
    m[3] = tx; m[7] = ty; m[11] = tz
    return m

def mat_scale(sx, sy, sz):
    return [sx,0,0,0, 0,sy,0,0, 0,0,sz,0, 0,0,0,1]

def mat_rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return [1,0,0,0, 0,c,-s,0, 0,s,c,0, 0,0,0,1]

def mat_rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return [c,0,s,0, 0,1,0,0, -s,0,c,0, 0,0,0,1]

def mat_rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return [c,-s,0,0, s,c,0,0, 0,0,1,0, 0,0,0,1]

def mat_perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) * 0.5)
    nf = 1.0 / (near - far)
    return [
        f/aspect, 0, 0, 0,
        0, f, 0, 0,
        0, 0, (far+near)*nf, (2*far*near)*nf,
        0, 0, -1, 0
    ]

def mat_look_at(eye, center, up):
    fx = center[0]-eye[0]; fy = center[1]-eye[1]; fz = center[2]-eye[2]
    fl = math.sqrt(fx*fx+fy*fy+fz*fz)
    if fl < 1e-8: fl = 1e-8
    fx/=fl; fy/=fl; fz/=fl
    sx = fy*up[2]-fz*up[1]; sy = fz*up[0]-fx*up[2]; sz = fx*up[1]-fy*up[0]
    sl = math.sqrt(sx*sx+sy*sy+sz*sz)
    if sl < 1e-8: sl = 1e-8
    sx/=sl; sy/=sl; sz/=sl
    ux = sy*fz-sz*fy; uy = sz*fx-sx*fz; uz = sx*fy-sy*fx
    return [
        sx, sy, sz, -(sx*eye[0]+sy*eye[1]+sz*eye[2]),
        ux, uy, uz, -(ux*eye[0]+uy*eye[1]+uz*eye[2]),
        -fx,-fy,-fz,  (fx*eye[0]+fy*eye[1]+fz*eye[2]),
        0,  0,  0,  1
    ]

def transform_vec4(m, x, y, z, w=1.0):
    ox = m[0]*x + m[1]*y + m[ 2]*z + m[ 3]*w
    oy = m[4]*x + m[5]*y + m[ 6]*z + m[ 7]*w
    oz = m[8]*x + m[9]*y + m[10]*z + m[11]*w
    ow = m[12]*x+m[13]*y + m[14]*z + m[15]*w
    return ox, oy, oz, ow

def project_point(pv_mat, wx, wy, wz):
    """Return (sx, sy, depth) in screen pixels, or None if behind camera"""
    cx, cy, cz, cw = transform_vec4(pv_mat, wx, wy, wz)
    if cw <= 0.0001:
        return None
    nx = cx / cw
    ny = cy / cw
    nz = cz / cw
    if abs(nx) > 1.5 or abs(ny) > 1.5:
        return None
    sx = int((nx * 0.5 + 0.5) * SCREEN_W)
    sy = int((1.0 - (ny * 0.5 + 0.5)) * SCREEN_H)
    return sx, sy, nz * 0.5 + 0.5   # depth 0..1

# ══════════════════════════════════════════════════════════════════════════════
#  SOFTWARE RASTERIZER  (draws on a pygame.Surface)
# ══════════════════════════════════════════════════════════════════════════════

class Renderer:
    """Thin wrapper around pygame drawing with a Z-buffer for 3-D objects."""

    def __init__(self, surface: pygame.Surface):
        self.surf = surface
        self.W    = surface.get_width()
        self.H    = surface.get_height()
        self.zbuf = [[1e9] * self.W for _ in range(self.H)]
        self.pv   = mat_identity()   # projection × view
        self.fog_color = (80, 130, 200)
        self.fog_dist  = 60.0
        self.ambient   = 0.55
        self.sun_dir   = [0.5, 0.8, 0.3]

    def clear_zbuf(self):
        for row in self.zbuf:
            for i in range(self.W):
                row[i] = 1e9

    def project(self, wx, wy, wz):
        return project_point(self.pv, wx, wy, wz)

    # ── Primitive drawing ──────────────────────────────────────────────────

    def draw_line_3d(self, p0, p1, color, width=1):
        a = self.project(*p0)
        b = self.project(*p1)
        if a is None or b is None: return
        depth = (a[2] + b[2]) * 0.5
        col = apply_fog(color, depth * self.fog_dist, self.fog_color, self.fog_dist)
        pygame.draw.line(self.surf, col, (a[0], a[1]), (b[0], b[1]), width)

    def draw_quad_3d(self, verts4, color, normal=(0,1,0), wire=False):
        """Draw a shaded quadrilateral. verts4 = list of 4 (wx,wy,wz)"""
        pts2d = []
        avg_z = 0.0
        for v in verts4:
            p = self.project(*v)
            if p is None: return
            pts2d.append((p[0], p[1]))
            avg_z += p[2]
        avg_z /= 4
        shaded = apply_light(color, normal, self.sun_dir, self.ambient)
        shaded = apply_fog(shaded, avg_z * self.fog_dist, self.fog_color, self.fog_dist)
        if wire:
            pygame.draw.polygon(self.surf, shaded, pts2d, 1)
        else:
            pygame.draw.polygon(self.surf, shaded, pts2d)
            pygame.draw.polygon(self.surf, tuple(max(0,c-30) for c in shaded), pts2d, 1)

    def draw_tri_3d(self, verts3, color, normal=(0,1,0)):
        pts2d = []
        avg_z = 0.0
        for v in verts3:
            p = self.project(*v)
            if p is None: return
            pts2d.append((p[0], p[1]))
            avg_z += p[2]
        avg_z /= 3
        shaded = apply_light(color, normal, self.sun_dir, self.ambient)
        shaded = apply_fog(shaded, avg_z * self.fog_dist, self.fog_color, self.fog_dist)
        pygame.draw.polygon(self.surf, shaded, pts2d)

    def draw_box(self, cx, cy, cz, w, h, d, colors, wire=False):
        """Draw a solid or wireframe box.
        colors = dict of face name → color  OR a single color tuple"""
        hw, hh, hd = w/2, h/2, d/2
        # 8 vertices
        v = [
            (cx-hw, cy-hh, cz-hd), (cx+hw, cy-hh, cz-hd),
            (cx+hw, cy+hh, cz-hd), (cx-hw, cy+hh, cz-hd),
            (cx-hw, cy-hh, cz+hd), (cx+hw, cy-hh, cz+hd),
            (cx+hw, cy+hh, cz+hd), (cx-hw, cy+hh, cz+hd),
        ]
        faces = [
            ([v[4],v[5],v[6],v[7]], (0, 0, 1),  "front"),
            ([v[1],v[0],v[3],v[2]], (0, 0,-1),  "back"),
            ([v[0],v[4],v[7],v[3]], (-1,0, 0),  "left"),
            ([v[5],v[1],v[2],v[6]], ( 1,0, 0),  "right"),
            ([v[3],v[7],v[6],v[2]], (0, 1, 0),  "top"),
            ([v[0],v[1],v[5],v[4]], (0,-1, 0),  "bottom"),
        ]
        # Sort back-to-front
        def face_depth(f):
            pts = [self.project(*p) for p in f[0]]
            pts = [p for p in pts if p]
            if not pts: return 1e9
            return sum(p[2] for p in pts) / len(pts)
        faces_sorted = sorted(faces, key=face_depth, reverse=True)
        for quad, normal, name in faces_sorted:
            if isinstance(colors, dict):
                col = colors.get(name, colors.get("default", C_GRAY))
            else:
                col = colors
            self.draw_quad_3d(quad, col, normal, wire=wire)

    def draw_cylinder(self, cx, cy, cz, radius, height, color, segs=10, wire=False):
        """Approximate cylinder"""
        angles = [2*math.pi*i/segs for i in range(segs)]
        top_verts = [(cx+radius*math.cos(a), cy+height/2, cz+radius*math.sin(a)) for a in angles]
        bot_verts = [(cx+radius*math.cos(a), cy-height/2, cz+radius*math.sin(a)) for a in angles]
        for i in range(segs):
            j = (i+1) % segs
            quad = [bot_verts[i], bot_verts[j], top_verts[j], top_verts[i]]
            nx = math.cos((angles[i]+angles[j])/2)
            nz = math.sin((angles[i]+angles[j])/2)
            self.draw_quad_3d(quad, color, (nx,0,nz), wire=wire)

    def draw_sphere_approx(self, cx, cy, cz, radius, color, segs=8):
        """Latitude/longitude bands"""
        lats = segs // 2
        lons = segs
        for lat in range(lats):
            phi1 = math.pi * lat / lats - math.pi/2
            phi2 = math.pi * (lat+1) / lats - math.pi/2
            for lon in range(lons):
                theta1 = 2*math.pi * lon / lons
                theta2 = 2*math.pi * (lon+1) / lons
                p00 = (cx+radius*math.cos(phi1)*math.cos(theta1),
                       cy+radius*math.sin(phi1),
                       cz+radius*math.cos(phi1)*math.sin(theta1))
                p10 = (cx+radius*math.cos(phi2)*math.cos(theta1),
                       cy+radius*math.sin(phi2),
                       cz+radius*math.cos(phi2)*math.sin(theta1))
                p11 = (cx+radius*math.cos(phi2)*math.cos(theta2),
                       cy+radius*math.sin(phi2),
                       cz+radius*math.cos(phi2)*math.sin(theta2))
                p01 = (cx+radius*math.cos(phi1)*math.cos(theta2),
                       cy+radius*math.sin(phi1),
                       cz+radius*math.cos(phi1)*math.sin(theta2))
                nx = math.cos((phi1+phi2)/2) * math.cos((theta1+theta2)/2)
                ny = math.sin((phi1+phi2)/2)
                nz2 = math.cos((phi1+phi2)/2) * math.sin((theta1+theta2)/2)
                self.draw_quad_3d([p00,p01,p11,p10], color, (nx,ny,nz2))

# ══════════════════════════════════════════════════════════════════════════════
#  3-D CHARACTER  (fully articulated, animated running figure)
# ══════════════════════════════════════════════════════════════════════════════

class Character3D:
    def __init__(self, char_data):
        self.body_col  = char_data["body"]
        self.hair_col  = char_data["hair"]
        self.pants_col = char_data["pants"]
        self.anim_t    = 0.0
        self.wire      = False

    def update(self, dt, speed):
        self.anim_t += dt * clamp(speed / 8.0, 0.5, 6.0) * 3.0

    def draw(self, ren: Renderer, px, py, pz,
             rolling=False, jumping=False, trick_angle=0.0, lean=0.0,
             jetpack_on=False):
        t = self.anim_t
        leg_sw  = math.sin(t) * 0.55 if not rolling else 0.0
        arm_sw  = math.sin(t + math.pi) * 0.45

        # Optionally apply trick spin
        if trick_angle != 0.0:
            px_off = math.sin(trick_angle)
        else:
            px_off = 0.0

        # Lean offsets
        lx = lean * 0.18

        # --- HEAD ---
        self._draw_head(ren, px+lx, py+1.62, pz)

        # --- TORSO ---
        ren.draw_box(px+lx, py+1.12, pz, 0.30, 0.44, 0.18,
                     {"front":self.body_col,"back":self.body_col,
                      "left":tuple(max(0,c-20) for c in self.body_col),
                      "right":tuple(min(255,c+20) for c in self.body_col),
                      "top":self.body_col,"bottom":self.body_col}, wire=self.wire)

        # --- HIPS ---
        ren.draw_box(px+lx, py+0.80, pz, 0.26, 0.18, 0.16, self.pants_col, wire=self.wire)

        if rolling:
            # Curled up
            ren.draw_box(px, py+0.25, pz, 0.38, 0.38, 0.38, self.pants_col, wire=self.wire)
        else:
            # --- LEFT LEG ---
            off_l = leg_sw * 0.28
            ren.draw_box(px+lx-0.10, py+0.66+off_l*0.3, pz+off_l,
                         0.11, 0.40, 0.11, self.pants_col, wire=self.wire)
            # left shoe
            ren.draw_box(px+lx-0.10, py+0.40+off_l*0.3, pz+off_l+0.06,
                         0.12, 0.08, 0.20, C_RED, wire=self.wire)
            # --- RIGHT LEG ---
            off_r = -leg_sw * 0.28
            ren.draw_box(px+lx+0.10, py+0.66+off_r*0.3, pz+off_r,
                         0.11, 0.40, 0.11, self.pants_col, wire=self.wire)
            # right shoe
            ren.draw_box(px+lx+0.10, py+0.40+off_r*0.3, pz+off_r+0.06,
                         0.12, 0.08, 0.20, C_RED, wire=self.wire)
            # --- LEFT ARM ---
            arm_off_l = arm_sw * 0.32
            ren.draw_box(px+lx-0.22, py+1.05+arm_off_l*0.2, pz-arm_off_l*0.5,
                         0.10, 0.34, 0.10, C_SKIN, wire=self.wire)
            # --- RIGHT ARM ---
            arm_off_r = -arm_sw * 0.32
            ren.draw_box(px+lx+0.22, py+1.05+arm_off_r*0.2, pz-arm_off_r*0.5,
                         0.10, 0.34, 0.10, C_SKIN, wire=self.wire)

        # --- JETPACK ---
        if jetpack_on:
            ren.draw_box(px+lx, py+1.10, pz+0.14, 0.26, 0.44, 0.12, C_DKGRAY, wire=self.wire)
            ren.draw_box(px+lx-0.08, py+0.68, pz+0.15, 0.07, 0.20, 0.07, C_GRAY, wire=self.wire)
            ren.draw_box(px+lx+0.08, py+0.68, pz+0.15, 0.07, 0.20, 0.07, C_GRAY, wire=self.wire)

    def _draw_head(self, ren, px, py, pz):
        # Skull
        ren.draw_box(px, py, pz, 0.22, 0.22, 0.22, C_SKIN, wire=self.wire)
        # Hair top
        ren.draw_box(px, py+0.12, pz, 0.22, 0.06, 0.22, self.hair_col, wire=self.wire)
        # Eyes
        for ex in [-0.06, 0.06]:
            ren.draw_box(px+ex, py+0.02, pz-0.12, 0.04, 0.04, 0.02, C_BLACK, wire=self.wire)
        # Mouth
        ren.draw_box(px, py-0.05, pz-0.12, 0.08, 0.02, 0.02, C_DKRED, wire=self.wire)

# ══════════════════════════════════════════════════════════════════════════════
#  WORLD GEOMETRY
# ══════════════════════════════════════════════════════════════════════════════

def draw_sky_gradient(surf, theme):
    tc = THEMES[theme]
    top = tc["sky_top"]; bot = tc["sky_bot"]
    half = SCREEN_H // 2
    for y in range(half + 10):
        t = y / (half + 10)
        col = lerp_color(top, bot, t)
        pygame.draw.line(surf, col, (0, y), (SCREEN_W, y))
    # Stars in dark themes
    if theme in ("night", "subway", "neon"):
        for i in range(80):
            sx = (i * 137 + 53) % SCREEN_W
            sy = (i * 79  + 11) % (half - 5)
            br = 100 + (i % 3) * 50
            r = 1 if i % 4 == 0 else 0
            pygame.draw.circle(surf, (br, br, br), (sx, sy), r)

def draw_ground_plane(surf, theme, cam_z, ren: Renderer):
    """Textured-style ground via projected horizontal strips"""
    tc = THEMES[theme]
    c1 = tc["ground"]; c2 = tc["ground2"]
    # Draw 30 ground quads receding into distance
    stripe_w = 8.0
    for s in range(0, 30):
        z0 = cam_z + s * stripe_w
        z1 = z0 + stripe_w
        col = c1 if s % 2 == 0 else c2
        # ground quad at y=0
        pts = []
        for wx, wz in [(-12, z0), (12, z0), (12, z1), (-12, z1)]:
            p = ren.project(wx, 0.0, wz)
            if p: pts.append((p[0], p[1]))
        if len(pts) == 4:
            pygame.draw.polygon(surf, col, pts)

def draw_track(ren: Renderer, cam_z, theme):
    tc = THEMES[theme]
    rc = tc["rail"]; tc2 = tc["tie"]
    # Rails
    for rx in [-3.2, -1.2, 1.2, 3.2]:
        for seg in range(28):
            z0 = cam_z + seg * 2.8
            z1 = z0 + 2.8
            ren.draw_box(rx, 0.04, (z0+z1)/2, 0.06, 0.06, z1-z0, rc)

    # Ties
    tie_spacing = 1.4
    offset = (cam_z % tie_spacing)
    for seg in range(0, 30):
        tz = cam_z + seg * tie_spacing - offset
        ren.draw_box(0.0, 0.02, tz, 7.0, 0.05, 0.20, tc2)

def draw_overhead_cables(ren: Renderer, cam_z, theme):
    tc = THEMES[theme]
    pole_col = (100,100,100)
    for seg in range(0, 18, 3):
        cz = cam_z + seg * 3.0
        # Left pole
        ren.draw_box(-4.8, 1.5, cz, 0.08, 3.0, 0.08, pole_col)
        # Right pole
        ren.draw_box( 4.8, 1.5, cz, 0.08, 3.0, 0.08, pole_col)
        # Cross bar
        ren.draw_box( 0.0, 3.1, cz, 9.6, 0.06, 0.06, pole_col)

def draw_building(ren: Renderer, bx, bz, bw, bh, bd, theme):
    tc = THEMES[theme]
    bc = tc["building"]; ba = tc["bld_acc"]
    # Main structure
    ren.draw_box(bx, bh/2, bz, bw, bh, bd, bc)
    # Window rows
    wc = C_YELLOW if theme not in ("neon",) else C_NEON_G
    win_rows = int(bh / 2.5)
    win_cols = max(1, int(bw / 1.8))
    for wr in range(1, win_rows+1):
        wy = wr * 2.2
        if wy > bh - 1: break
        for wc_i in range(win_cols):
            wx_off = (wc_i - win_cols/2 + 0.5) * (bw / win_cols)
            # Front face windows
            ren.draw_box(bx+wx_off, wy, bz - bd/2 - 0.05, 0.3, 0.5, 0.05, wc)
    # Roof detail
    ren.draw_box(bx, bh+0.15, bz, bw*0.6, 0.30, bd*0.6, ba)

def draw_tunnel(ren: Renderer, cam_z, length, theme):
    tc = THEMES[theme]
    bc = tc["building"]
    # Left wall
    ren.draw_box(-5.0, 2.2, cam_z + length/2, 0.4, 4.4, length, bc)
    # Right wall
    ren.draw_box( 5.0, 2.2, cam_z + length/2, 0.4, 4.4, length, bc)
    # Ceiling
    ren.draw_box(0.0, 4.5, cam_z + length/2, 10.4, 0.4, length, bc)
    # Arch rings
    for az in range(int(cam_z), int(cam_z+length), 7):
        for seg_i in range(8):
            a1 = math.pi * seg_i / 8
            a2 = math.pi * (seg_i+1) / 8
            r = 4.8
            ren.draw_quad_3d([
                (-r*math.cos(a1), r*math.sin(a1), az),
                (-r*math.cos(a2), r*math.sin(a2), az),
                (-r*math.cos(a2)+0.3, r*math.sin(a2), az),
                (-r*math.cos(a1)+0.3, r*math.sin(a1), az),
            ], tc["bld_acc"], (0,0,-1))

# ── Obstacle drawing ──────────────────────────────────────────────────────────

def draw_train(ren: Renderer, ox, oz):
    # Body
    ren.draw_box(ox, 1.0, oz, 1.80, 2.0, 5.5,
                 {"front":C_BLUE,"back":C_DKBLUE,"left":C_DKBLUE,
                  "right":C_DKBLUE,"top":(60,60,160),"bottom":C_DKGRAY})
    # Windows row
    for wz_off in [-1.8, -0.6, 0.6, 1.8]:
        ren.draw_box(ox-0.91, 1.3, oz+wz_off, 0.04, 0.55, 0.65, C_NEON_C)
        ren.draw_box(ox+0.91, 1.3, oz+wz_off, 0.04, 0.55, 0.65, C_NEON_C)
    # Headlight
    ren.draw_box(ox, 0.8, oz-2.78, 1.80, 0.30, 0.08, C_LTGRAY)
    ren.draw_box(ox, 0.8, oz-2.82, 0.40, 0.22, 0.08, C_YELLOW)
    # Wheels
    for wz_off in [-1.8, 0.0, 1.8]:
        for wx_off in [-0.82, 0.82]:
            ren.draw_cylinder(ox+wx_off, 0.18, oz+wz_off, 0.26, 0.16, C_DKGRAY, segs=8)

def draw_low_barrier(ren: Renderer, ox, oz):
    ren.draw_box(ox, 0.30, oz, 1.85, 0.60, 0.35, C_RED)
    # Warning stripes
    for sh in [0.12, 0.36]:
        ren.draw_box(ox, sh, oz, 1.85, 0.10, 0.36, C_YELLOW)
    # Side poles
    for px_off in [-0.85, 0.85]:
        ren.draw_box(ox+px_off, 0.55, oz, 0.08, 1.10, 0.08, C_LTGRAY)

def draw_hi_barrier(ren: Renderer, ox, oz):
    ren.draw_box(ox, 1.0, oz, 1.85, 2.0, 0.30, C_RED)
    for sh in [0.3, 0.8, 1.3, 1.8]:
        ren.draw_box(ox, sh, oz, 1.85, 0.10, 0.31, C_YELLOW)

def draw_barrel(ren: Renderer, ox, oz):
    ren.draw_cylinder(ox, 0.40, oz, 0.38, 0.80, C_BROWN, segs=10)
    # Metal bands
    for by in [0.05, 0.40, 0.75]:
        ren.draw_cylinder(ox, by, oz, 0.39, 0.08, C_GRAY, segs=10)
    # Fuse / X mark
    ren.draw_box(ox, 0.85, oz, 0.05, 0.28, 0.05, C_YELLOW)

def draw_coin_3d(ren: Renderer, cx, cy, cz, spin_t, phase):
    spin = spin_t * 3.0 + phase
    cs, sn = math.cos(spin), math.sin(spin)
    r = 0.20
    segs = 10
    top_verts = []
    bot_verts = []
    for i in range(segs):
        a = 2 * math.pi * i / segs
        bx2 = r * math.cos(a) * cs
        bz2 = r * math.cos(a) * sn
        by2 = r * math.sin(a)
        top_verts.append((cx+bx2, cy+by2+0.02, cz+bz2))
        bot_verts.append((cx+bx2, cy+by2-0.02, cz+bz2))
    for i in range(segs):
        j = (i+1) % segs
        ren.draw_quad_3d([bot_verts[i],bot_verts[j],top_verts[j],top_verts[i]],
                          C_GOLD, (0,0,1))
    # Face
    ren.draw_tri_3d([top_verts[0], top_verts[segs//3], top_verts[2*segs//3]], C_YELLOW)

def draw_powerup_box(ren: Renderer, px, py, pz, ptype, spin_t, phase):
    spin = spin_t * 2.0 + phase
    # Pulsing scale
    sc = 0.32 + 0.04 * math.sin(spin_t * 4.0)
    col = PU_COLOR.get(ptype, C_WHITE)
    # Outer cube rotated
    offsets = [
        (sc*math.cos(spin)*0.36, 0, sc*math.sin(spin)*0.36),
    ]
    ren.draw_box(px, py, pz, sc*0.66, sc*0.66, sc*0.66, col)
    # Inner bright core
    bright = tuple(min(255, c+60) for c in col)
    ren.draw_box(px, py, pz, sc*0.30, sc*0.30, sc*0.30, bright)

# ══════════════════════════════════════════════════════════════════════════════
#  PARTICLE SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class Particle:
    __slots__ = ['x','y','z','vx','vy','vz','color','life','max_life','size','type']
    def __init__(self, x, y, z, vx, vy, vz, color, life, size=3, ptype='dot'):
        self.x=x; self.y=y; self.z=z
        self.vx=vx; self.vy=vy; self.vz=vz
        self.color=color; self.life=life; self.max_life=life
        self.size=size; self.type=ptype

class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []

    def emit_coin_sparkle(self, x, y, z):
        for _ in range(8):
            a = random.uniform(0, 2*math.pi)
            sp = random.uniform(1.5, 4.0)
            self.particles.append(Particle(x, y, z,
                math.cos(a)*sp, math.sin(a)*sp*0.6 + 1.5, random.uniform(-1,1),
                random.choice([C_YELLOW, C_GOLD, C_WHITE]),
                random.uniform(0.25, 0.6), random.randint(3,6), 'spark'))

    def emit_explosion(self, x, y, z):
        for _ in range(22):
            a = random.uniform(0, 2*math.pi)
            sp = random.uniform(2, 9)
            col = random.choice([C_RED, C_ORANGE, C_YELLOW, (255,255,100)])
            self.particles.append(Particle(x, y, z,
                math.cos(a)*sp, random.uniform(1,7), math.sin(a)*sp*0.4,
                col, random.uniform(0.3, 0.9), random.randint(4,9), 'spark'))

    def emit_dust(self, x, y, z):
        for _ in range(6):
            self.particles.append(Particle(
                x+random.uniform(-0.4,0.4), y+0.05, z,
                random.uniform(-1.5,1.5), random.uniform(0.5,2.5), random.uniform(-0.5,0.5),
                C_GRAY, random.uniform(0.3, 0.6), random.randint(2,5), 'smoke'))

    def emit_jetpack(self, x, y, z):
        for ox in [-0.09, 0.09]:
            col = random.choice([C_RED, C_ORANGE, C_YELLOW])
            self.particles.append(Particle(
                x+ox, y+0.55, z+0.18,
                random.uniform(-0.5,0.5), random.uniform(-5,-9), random.uniform(-0.4,0.4),
                col, random.uniform(0.08, 0.22), random.randint(4,8), 'flame'))

    def emit_powerup(self, x, y, z, color):
        for _ in range(14):
            a = random.uniform(0, 2*math.pi)
            sp = random.uniform(1.5, 3.5)
            self.particles.append(Particle(x, y+0.5, z,
                math.cos(a)*sp, math.sin(a)*sp*0.7 + 1.5, 0,
                color, random.uniform(0.4, 1.0), random.randint(4,8), 'star'))

    def emit_trail(self, x, y, z, speed_ratio):
        if random.random() < speed_ratio:
            self.particles.append(Particle(
                x+random.uniform(-0.12,0.12), y+random.uniform(0.3,1.5), z,
                random.uniform(-0.5,0.5), random.uniform(-0.5,0.5), random.uniform(0.5,2.5),
                C_CYAN, random.uniform(0.08, 0.22), random.randint(2,4), 'dot'))

    def emit_speed_line(self, x, y, z):
        self.particles.append(Particle(x, y, z,
            random.uniform(-0.2,0.2), random.uniform(-0.2,0.2), random.uniform(2,5),
            C_LTGRAY, random.uniform(0.1, 0.3), 1, 'line'))

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.z += p.vz * dt
            if p.type not in ('flame',):
                p.vy -= 6.0 * dt
            p.life -= dt
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, ren: Renderer):
        pv = ren.pv
        surf = ren.surf
        for p in self.particles:
            proj = project_point(pv, p.x, p.y, p.z)
            if proj is None: continue
            sx, sy, depth = proj
            alpha = clamp(p.life / p.max_life, 0, 1)
            col = tuple(int(c * alpha) for c in p.color)
            sz = max(1, int(p.size * (1.0 - depth * 0.5)))
            if p.type == 'spark':
                pygame.draw.circle(surf, col, (sx, sy), sz)
            elif p.type == 'smoke':
                pygame.draw.circle(surf, col, (sx, sy), sz)
            elif p.type == 'flame':
                pygame.draw.circle(surf, col, (sx, sy), sz+1)
            elif p.type == 'star':
                pygame.draw.circle(surf, col, (sx, sy), sz)
            else:
                pygame.draw.circle(surf, col, (sx, sy), max(1, sz-1))

# ══════════════════════════════════════════════════════════════════════════════
#  PROCEDURAL SPAWNERS
# ══════════════════════════════════════════════════════════════════════════════

class ObstacleSpawner:
    def __init__(self):
        self.next_z   = 35.0
        self.gap_min  = 9.0
        self.gap_max  = 20.0

    def spawn(self, diff_mult=1.0):
        z = self.next_z
        kind = random.choices(
            [OT_TRAIN, OT_LOW_BAR, OT_HI_BAR, OT_BARREL, OT_COMBO],
            weights=[28, 20, 20, 16, 16]
        )[0]
        obs_list = []
        if kind == OT_TRAIN:
            lane = random.randint(0,2)
            obs_list.append({"type":OT_TRAIN, "lane":lane, "x":LANES[lane], "z":z})
        elif kind == OT_LOW_BAR:
            lanes = random.sample([0,1,2], random.randint(1,2))
            for l in lanes:
                obs_list.append({"type":OT_LOW_BAR, "lane":l, "x":LANES[l], "z":z})
        elif kind == OT_HI_BAR:
            lane = random.randint(0,2)
            obs_list.append({"type":OT_HI_BAR, "lane":lane, "x":LANES[lane], "z":z})
        elif kind == OT_BARREL:
            cnt = random.randint(1,3)
            for l in random.sample([0,1,2], min(cnt,3)):
                obs_list.append({"type":OT_BARREL, "lane":l, "x":LANES[l],
                                 "z":z+random.uniform(0,1.5)})
        elif kind == OT_COMBO:
            m = 1; s = random.choice([0,2])
            obs_list.append({"type":OT_HI_BAR,  "lane":m, "x":LANES[m], "z":z})
            obs_list.append({"type":OT_BARREL,  "lane":s, "x":LANES[s], "z":z+1.5})
        gap = random.uniform(self.gap_min/diff_mult, self.gap_max/diff_mult)
        self.next_z = z + max(5.0, gap)
        return obs_list

class CoinSpawner:
    PATTERNS = ["row","arc","spiral","zigzag","lane_switch"]
    def __init__(self):
        self.next_z = 18.0

    def spawn(self):
        z = self.next_z
        pat = random.choice(self.PATTERNS)
        coins = []
        if pat == "row":
            l = random.randint(0,2)
            for i in range(9):
                coins.append({"x":LANES[l],"y":0.65,"z":z+i*1.1,"ph":i*0.3})
        elif pat == "arc":
            l = random.randint(0,2)
            for i in range(9):
                ay = 0.65 + math.sin(i/8.0*math.pi)*2.0
                coins.append({"x":LANES[l],"y":ay,"z":z+i*1.0,"ph":i*0.4})
        elif pat == "spiral":
            for i in range(14):
                a = i * 0.9
                coins.append({"x":math.sin(a)*2.2,"y":0.65+math.cos(a)*0.35,
                               "z":z+i*0.85,"ph":i*0.5})
        elif pat == "zigzag":
            for i in range(10):
                coins.append({"x":LANES[i%3],"y":0.65,"z":z+i*1.0,"ph":i*0.3})
        elif pat == "lane_switch":
            for i, l in enumerate([0,1,2,1,0,2,1,0,1,2]):
                coins.append({"x":LANES[l],"y":0.65,"z":z+i*1.2,"ph":i*0.2})
        self.next_z = z + random.uniform(7.0, 16.0)
        return coins

class BuildingSpawner:
    def __init__(self):
        self.next_z_l = 5.0
        self.next_z_r = 5.0

    def try_spawn(self, cam_z, ahead=55.0):
        new_blds = []
        while self.next_z_l < cam_z + ahead:
            x = random.uniform(-10.5, -6.5)
            w = random.uniform(3.0, 6.5)
            h = random.uniform(5.0, 22.0)
            d = random.uniform(3.5, 8.0)
            new_blds.append({"x":x,"z":self.next_z_l,"w":w,"h":h,"d":d})
            self.next_z_l += random.uniform(5.0, 12.0)
        while self.next_z_r < cam_z + ahead:
            x = random.uniform(6.5, 10.5)
            w = random.uniform(3.0, 6.5)
            h = random.uniform(5.0, 22.0)
            d = random.uniform(3.5, 8.0)
            new_blds.append({"x":x,"z":self.next_z_r,"w":w,"h":h,"d":d})
            self.next_z_r += random.uniform(5.0, 12.0)
        return new_blds

# ══════════════════════════════════════════════════════════════════════════════
#  AUTOPILOT AI
# ══════════════════════════════════════════════════════════════════════════════

class AutopilotAI:
    MODES = ["balanced", "aggressive", "safe", "speedrun"]

    def __init__(self):
        self.active  = False
        self.mode    = "balanced"
        self.obs_mem = deque(maxlen=30)

    def decide(self, player, obstacles, coins, powerups):
        if not self.active:
            return player["lane"], False, False

        lane  = player["lane"]
        pz    = player["z"]
        speed = player["speed"]
        look  = max(8.0, speed * 0.55)

        # Build lane danger map
        danger = {0:0.0, 1:0.0, 2:0.0}
        for obs in obstacles:
            dz = obs["z"] - pz
            if 0.5 < dz < look:
                l = obs.get("lane", 1)
                wt = 10.0 / max(0.1, dz)
                if obs["type"] == OT_TRAIN:   danger[l] += wt * 1.5
                elif obs["type"] == OT_LOW_BAR: danger[l] += wt
                elif obs["type"] == OT_HI_BAR:  danger[l] += wt * 0.7
                elif obs["type"] == OT_BARREL:  danger[l] += wt * 0.9

        target_lane  = lane
        should_jump  = False
        should_roll  = False

        # Decide action for current lane danger
        if danger[lane] > 0.5:
            ahead = [o for o in obstacles
                     if o.get("lane",1)==lane and 0.5<(o["z"]-pz)<look*0.55]
            if ahead:
                otype = ahead[0]["type"]
                dz    = ahead[0]["z"] - pz
                # Find safest alternative lane
                opts  = sorted(range(3), key=lambda l2: danger[l2])
                safest = opts[0]

                if otype == OT_LOW_BAR:
                    should_roll = True
                elif otype == OT_HI_BAR and danger[safest] > danger[lane]*0.5:
                    should_jump = True
                elif otype == OT_TRAIN:
                    if dz < look * 0.35:
                        target_lane = safest if safest != lane else opts[1]
                    else:
                        target_lane = safest if safest != lane else lane
                else:
                    target_lane = safest if safest != lane else lane

        # Aggressive: chase power-ups first, then coins
        if self.mode == "aggressive" and target_lane == lane:
            close_pups = [p for p in powerups if abs(p["z"]-pz) < look*0.8 and p["z"]>pz]
            if close_pups:
                best = min(close_pups, key=lambda p2: abs(p2["z"]-pz))
                bl = min(range(3), key=lambda l2: abs(LANES[l2]-best["x"]))
                if danger[bl] < 1.0:
                    target_lane = bl
            else:
                close_coins = [c for c in coins if abs(c["z"]-pz) < look*0.6 and c["z"]>pz]
                if close_coins:
                    best = min(close_coins, key=lambda c2: abs(c2["z"]-pz))
                    bl = min(range(3), key=lambda l2: abs(LANES[l2]-best["x"]))
                    if danger[bl] < 1.0:
                        target_lane = bl

        # Safe: always move to safest lane
        if self.mode == "safe":
            safest = min(range(3), key=lambda l2: danger[l2])
            if danger[lane] > 0.2:
                target_lane = safest

        return target_lane, should_jump, should_roll

# ══════════════════════════════════════════════════════════════════════════════
#  HUD
# ══════════════════════════════════════════════════════════════════════════════

class HUD:
    def __init__(self):
        pygame.font.init()
        size_big    = 36
        size_med    = 24
        size_small  = 18
        size_tiny   = 14
        # Try system fonts
        fn = pygame.font.match_font("segoeui,arial,freesansbold,sans")
        fn_mono = pygame.font.match_font("consolas,couriernew,monospace")
        self.font_big   = pygame.font.Font(fn, size_big)   if fn else pygame.font.SysFont(None, size_big)
        self.font_med   = pygame.font.Font(fn, size_med)   if fn else pygame.font.SysFont(None, size_med)
        self.font_small = pygame.font.Font(fn, size_small) if fn else pygame.font.SysFont(None, size_small)
        self.font_tiny  = pygame.font.Font(fn_mono, size_tiny) if fn_mono else pygame.font.SysFont(None, size_tiny)

        self.score_vis   = 0.0
        self.coins_vis   = 0.0
        self.ach_queue   = deque()
        self.ach_timer   = 0.0
        self.ach_text    = ""
        self.flash_timer = 0.0
        self.flash_color = (255,255,255)
        self.flash_alpha = 0
        self.combo_text  = ""
        self.combo_timer = 0.0
        self.warn_text   = ""
        self.warn_timer  = 0.0
        self.flash_surf  = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

    def push_achievement(self, name):
        self.ach_queue.append(name)

    def show_combo(self, text):
        self.combo_text  = text
        self.combo_timer = 1.8

    def warn(self, text):
        self.warn_text  = text
        self.warn_timer = 1.2

    def flash(self, color, duration=0.18):
        self.flash_timer = duration
        self.flash_color = color

    def update(self, dt, score, coins):
        self.score_vis = lerp(self.score_vis, float(score), min(1.0, dt*10.0))
        self.coins_vis = lerp(self.coins_vis, float(coins), min(1.0, dt*12.0))
        if self.ach_timer > 0:
            self.ach_timer -= dt
        if self.ach_timer <= 0 and self.ach_queue:
            self.ach_text  = self.ach_queue.popleft()
            self.ach_timer = 3.2
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.combo_timer > 0:
            self.combo_timer -= dt
        if self.warn_timer > 0:
            self.warn_timer -= dt

    def _text(self, surf, text, font, color, x, y, shadow=True, center=False):
        if shadow:
            s = font.render(text, True, (0,0,0))
            r = s.get_rect()
            if center: r.centerx = x; r.y = y
            else:       r.x = x; r.y = y
            surf.blit(s, (r.x+2, r.y+2))
        s = font.render(text, True, color)
        r = s.get_rect()
        if center: r.centerx = x; r.y = y
        else:       r.x = x; r.y = y
        surf.blit(s, r)

    def _bar(self, surf, x, y, w, h, pct, color, bg=(40,40,40)):
        pygame.draw.rect(surf, bg, (x, y, w, h), border_radius=3)
        fw = int(w * clamp(pct, 0, 1))
        if fw > 0:
            pygame.draw.rect(surf, color, (x, y, fw, h), border_radius=3)
        pygame.draw.rect(surf, (80,80,80), (x, y, w, h), 1, border_radius=3)

    def draw(self, surf, state):
        W, H = SCREEN_W, SCREEN_H
        score        = state["score"]
        coins        = state["coins"]
        distance     = state["distance"]
        speed        = state["speed"]
        hp           = state["hp"]
        mult         = state["multiplier"]
        active_pups  = state["active_powerups"]
        lane         = state["lane"]
        fps          = state["fps"]
        autopilot    = state["autopilot"]
        godmode      = state["godmode"]
        streak       = state["streak"]
        session_t    = state["session_t"]
        tutorial_step= state.get("tutorial_step", -1)
        show_fps     = state.get("show_fps", True)
        jetpack_fuel = active_pups.get(PU_JETPACK, 0)
        shield_on    = PU_SHIELD in active_pups

        # ── Semi-transparent top bar ────────────────────────────────────────
        bar_surf = pygame.Surface((W, 60), pygame.SRCALPHA)
        bar_surf.fill((0,0,0,100))
        surf.blit(bar_surf, (0,0))

        # Score
        self._text(surf, f"SCORE  {int(self.score_vis):>10}", self.font_big, C_WHITE, 14, 8)

        # Coins
        coins_str = f"● {int(self.coins_vis)}"
        self._text(surf, coins_str, self.font_big, C_YELLOW, W//2, 8, center=True)

        # Distance
        self._text(surf, f"{distance:.0f} m", self.font_big, C_GREEN, W-160, 8)

        # HP
        for i in range(3):
            col = C_RED if i < hp else (60,20,20)
            pygame.draw.circle(surf, col, (14 + i*32, 70), 11)
            pygame.draw.circle(surf, (0,0,0), (14 + i*32, 70), 11, 2)

        # Shield ring
        if shield_on:
            pygame.draw.circle(surf, C_CYAN, (W//2, 70), 26, 3)
            self._text(surf, "SHIELD", self.font_small, C_CYAN, W//2, 58, center=True)

        # Multiplier
        if mult > 1:
            self._text(surf, f"x{mult}", self.font_big, C_ORANGE, W//2+80, 6, center=True)

        # Streak
        if streak >= 5:
            col = lerp_color(C_YELLOW, C_RED, clamp((streak-5)/15.0,0,1))
            self._text(surf, f"🔥 {streak}x", self.font_med, col, W//2-120, 10, center=True)

        # Speed meter (right side)
        spd_pct = clamp(speed / MAX_SPEED, 0, 1)
        self._text(surf, f"SPD  {speed:>8.1f}", self.font_med, C_CYAN, W-200, 45)
        self._bar(surf, W-200, 66, 186, 10, spd_pct, C_CYAN)

        # ── Active power-up bars ─────────────────────────────────────────────
        py2 = 90
        for ptype, rem in list(active_pups.items())[:5]:
            dur = PU_DURATION.get(ptype, 10.0)
            col = PU_COLOR.get(ptype, C_WHITE)
            lbl = PU_LABEL.get(ptype, "?")
            self._text(surf, lbl, self.font_small, col, 14, py2)
            self._bar(surf, 55, py2+2, 130, 12, rem/dur, col)
            self._text(surf, f"{rem:.1f}s", self.font_tiny, col, 190, py2+2)
            py2 += 22

        # Jetpack altitude bar
        if PU_JETPACK in active_pups:
            self._text(surf, "FUEL", self.font_small, C_NEON_C, 14, py2)
            self._bar(surf, 55, py2+2, 130, 12, jetpack_fuel / PU_DURATION[PU_JETPACK], C_NEON_C)
            py2 += 22

        # ── Bottom bar ───────────────────────────────────────────────────────
        bot_surf = pygame.Surface((W, 38), pygame.SRCALPHA)
        bot_surf.fill((0,0,0,80))
        surf.blit(bot_surf, (0, H-38))

        # Session timer
        m, s = divmod(int(session_t), 60)
        self._text(surf, f"TIME {m:02d}:{s:02d}", self.font_small, C_LTGRAY, 14, H-30)

        # FPS
        if show_fps:
            self._text(surf, f"FPS {fps}", self.font_tiny, C_DKGRAY, W-70, H-22)

        # Minimap (bottom center)
        mm_x = W//2 - 60; mm_y = H - 36
        mm_w = 120; mm_h = 30
        pygame.draw.rect(surf, (20,20,20,180), (mm_x, mm_y, mm_w, mm_h), border_radius=4)
        pygame.draw.rect(surf, (80,80,80), (mm_x, mm_y, mm_w, mm_h), 1, border_radius=4)
        # Lane dividers
        for li in range(1,3):
            lx = mm_x + li * (mm_w//3)
            pygame.draw.line(surf, (60,60,60), (lx, mm_y), (lx, mm_y+mm_h))
        # Player marker
        pm_x = mm_x + (lane * mm_w//3) + mm_w//6
        pygame.draw.polygon(surf, C_GREEN, [
            (pm_x, mm_y+4), (pm_x-7, mm_y+mm_h-4), (pm_x+7, mm_y+mm_h-4)
        ])

        # Autopilot badge
        if autopilot:
            ap_surf = pygame.Surface((180, 32), pygame.SRCALPHA)
            ap_surf.fill((100,0,200,160))
            surf.blit(ap_surf, (W//2-90, H-78))
            pygame.draw.rect(surf, C_MAGENTA, (W//2-90, H-78, 180, 32), 2, border_radius=4)
            self._text(surf, "◈ AUTOPILOT ◈", self.font_small, C_WHITE, W//2, H-72, center=True)

        # God mode badge
        if godmode:
            self._text(surf, "✦ GOD MODE ✦", self.font_med, C_YELLOW, 14, H-72)

        # ── Achievement popup ────────────────────────────────────────────────
        if self.ach_timer > 0:
            alpha_v = clamp(min(self.ach_timer, 3.2-self.ach_timer) / 0.5, 0, 1)
            ach_surf = pygame.Surface((360, 54), pygame.SRCALPHA)
            ach_surf.fill((20, 20, 20, int(210 * alpha_v)))
            surf.blit(ach_surf, (W//2-180, H//2-80))
            pygame.draw.rect(surf, C_YELLOW, (W//2-180, H//2-80, 360, 54), 2, border_radius=6)
            self._text(surf, "★ ACHIEVEMENT ★", self.font_small, C_YELLOW, W//2, H//2-76, center=True)
            self._text(surf, self.ach_text, self.font_med, C_WHITE, W//2, H//2-54, center=True)

        # ── Combo text ───────────────────────────────────────────────────────
        if self.combo_timer > 0:
            scale = 1.0 + 0.3 * math.sin(self.combo_timer * 8)
            fn2 = pygame.transform.scale(
                self.font_big.render(self.combo_text, True, C_ORANGE),
                tuple(int(d*scale) for d in self.font_big.size(self.combo_text))
            )
            surf.blit(fn2, fn2.get_rect(center=(W//2, H//2+60)))

        # ── Danger warning ───────────────────────────────────────────────────
        if self.warn_timer > 0:
            alpha_v = clamp(self.warn_timer / 1.2, 0, 1)
            pulse = 0.5 + 0.5 * math.sin(time.time() * 12)
            col = lerp_color(C_DKRED, C_RED, pulse)
            self._text(surf, self.warn_text, self.font_big, col, W//2, H-120, center=True)

        # ── Screen flash ─────────────────────────────────────────────────────
        if self.flash_timer > 0:
            alpha_v = int(clamp(self.flash_timer / 0.18, 0, 1) * 90)
            self.flash_surf.fill((*self.flash_color, alpha_v))
            surf.blit(self.flash_surf, (0,0))

        # ── Tutorial ────────────────────────────────────────────────────────
        if tutorial_step >= 0:
            msgs = [
                "← → Arrow Keys to change lane",
                "↑ / SPACE to JUMP  |  ↓ to ROLL",
                "Collect ● golden coins for score!",
                "Grab power-up boxes for special abilities",
                "Press A for AUTOPILOT  |  P to PAUSE",
            ]
            if tutorial_step < len(msgs):
                tut_surf = pygame.Surface((500, 38), pygame.SRCALPHA)
                tut_surf.fill((0,0,0,140))
                surf.blit(tut_surf, (W//2-250, H//2+100))
                self._text(surf, msgs[tutorial_step], self.font_med, C_YELLOW,
                           W//2, H//2+105, center=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SAVE / LOAD
# ══════════════════════════════════════════════════════════════════════════════

def load_save():
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        for k, v in DEFAULT_SAVE.items():
            if k not in data:
                data[k] = copy.deepcopy(v)
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if kk not in data[k]:
                        data[k][kk] = copy.deepcopy(vv)
        return data
    except Exception:
        return copy.deepcopy(DEFAULT_SAVE)

def save_game(data):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ══════════════════════════════════════════════════════════════════════════════
#  GAME STATE
# ══════════════════════════════════════════════════════════════════════════════

class GameState:
    def __init__(self, save_data, settings):
        self.save     = save_data
        self.settings = settings
        diff_cfg      = DIFFICULTIES[settings.get("difficulty","Normal")]

        # Player position & physics
        self.lane       = 1
        self.x          = LANES[1]
        self.y          = 0.0
        self.z          = 0.0
        self.vy         = 0.0
        self.jumping    = False
        self.in_air     = False
        self.jump_count = 0
        self.rolling    = False
        self.roll_timer = 0.0
        self.lean       = 0.0

        # Lane change
        self.lane_changing   = False
        self.lane_change_t   = 0.0
        self.lane_from       = 1
        self.lane_to         = 1

        # Speed
        self.base_speed  = BASE_SPEED * diff_cfg["speed_m"]
        self.speed       = self.base_speed
        self.target_speed= self.base_speed
        self.speed_ramp  = SPEED_RAMP * diff_cfg["ramp"]
        self.manual_speed= None
        self.sprinting   = False
        self.braking     = False

        # Head start upgrade
        hs = save_data.get("upgrades",{}).get("head_start",0)
        self.z        += hs * 100.0
        self.distance  = hs * 100.0

        # Score
        self.score       = 0
        self.coins       = 0
        self.run_coins   = 0
        self.multiplier  = 1
        self.streak      = 0
        self.max_streak  = 0
        self.combo       = 0
        self.last_coin_t = 0.0
        self.trick_count = 0

        # Upgrade cache
        self.upg_coin_dbl    = save_data.get("upgrades",{}).get("coin_doubler",0)
        self.upg_score_boost = save_data.get("upgrades",{}).get("score_booster",0)
        self.upg_mag_range   = save_data.get("upgrades",{}).get("magnet_range",0)

        # Lives
        self.hp              = 3
        self.invincible_t    = 0.0
        self.alive           = True
        self.godmode         = False
        self.hoverboard      = True
        self.hoverboard_used = False

        # Power-ups  { type: remaining_time }
        self.active_pups    : dict = {}
        self.jetpack_alt    = 0.0

        # World objects
        self.obstacles   : list = []
        self.coins_list  : list = []
        self.powerups    : list = []
        self.buildings   : list = []

        # Spawners
        self.obs_spawner  = ObstacleSpawner()
        self.coin_spawner = CoinSpawner()
        self.bld_spawner  = BuildingSpawner()

        # Particles
        self.particles = ParticleSystem()

        # Autopilot
        self.autopilot = AutopilotAI()

        # Camera
        self.cam_mode   = settings.get("camera","behind")
        self.cam_eye    = [0.0, 1.8, -3.5]
        self.cam_at     = [0.0, 1.0, 12.0]
        self.cam_bob_t  = 0.0
        self.cam_shake  = 0.0
        self.fov        = settings.get("fov", BASE_FOV)
        self.cin_t      = 0.0

        # Visual toggles
        self.theme        = settings.get("theme","city")
        self.wireframe    = settings.get("wireframe",False)
        self.night_vision = False
        self.scanlines    = False
        self.color_grade  = settings.get("color_grade","neutral")

        # Session / metrics
        self.session_t    = 0.0
        self.fps          = 0
        self._fps_frames  = 0
        self._fps_t       = 0.0
        self.danger_near  = False

        # Achievements
        self.autopilot_dist = 0.0

        # Missions
        self.missions = [
            {"id":"m_dist",  "name":"Run 1000m",       "target":1000, "prog":0, "done":False},
            {"id":"m_coins", "name":"Collect 80 coins", "target":80,  "prog":0, "done":False},
            {"id":"m_jumps", "name":"Jump 20 times",    "target":20,  "prog":0, "done":False},
            {"id":"m_pups",  "name":"Get 5 power-ups",  "target":5,   "prog":0, "done":False},
            {"id":"m_tricks","name":"Do 10 tricks",     "target":10,  "prog":0, "done":False},
        ]

        # Replay buffer (feature 94)
        self.replay_buf  = deque(maxlen=1800)
        self.replay_mode = False
        self.replay_data : list = []
        self.replay_idx  = 0

        # Trick animation
        self.trick_angle = 0.0
        self.trick_t     = 0.0

        # HUD
        self.hud = HUD()

        # Pre-populate world
        for _ in range(8):
            self.coins_list.extend(self.coin_spawner.spawn())
        for _ in range(4):
            self.obstacles.extend(self.obs_spawner.spawn())
        self.buildings.extend(self.bld_spawner.try_spawn(0))

    # ── Speed control ─────────────────────────────────────────────────────────
    def _update_speed(self, dt):
        if self.manual_speed is not None:
            self.target_speed = clamp(self.manual_speed, 0.5, MAX_SPEED)
        else:
            self.target_speed = self.base_speed
            if self.sprinting:
                self.target_speed = min(self.base_speed * 1.55, MAX_SPEED)
            if self.braking:
                self.target_speed = max(0.5, self.base_speed * 0.25)
            if PU_TURBO in self.active_pups:
                self.target_speed = min(self.speed * 1.85, MAX_SPEED)
            if PU_SLOW in self.active_pups:
                self.target_speed = max(0.5, self.target_speed * 0.35)

        # Auto-ramp
        if self.manual_speed is None:
            self.base_speed = min(self.base_speed + self.speed_ramp * dt, MAX_SPEED * 0.75)

        self.speed = lerp(self.speed, self.target_speed, min(1.0, dt * 4.0))
        self.speed = clamp(self.speed, 0.5, MAX_SPEED)

        # Dynamic FOV
        speed_t = clamp(self.speed / 300.0, 0, 1)
        self.fov = lerp(BASE_FOV, BASE_FOV + 28.0, smoothstep(speed_t))

    # ── Jump / roll / lane ────────────────────────────────────────────────────
    def jump(self):
        max_jumps = 3 if PU_SNEAKERS in self.active_pups else 2
        if self.jump_count < max_jumps:
            vel = (SUPER_JUMP_VEL if PU_SNEAKERS in self.active_pups
                   else JUMP_VEL * (0.85 ** self.jump_count))
            self.vy = vel
            self.jumping = True
            self.in_air  = True
            self.jump_count += 1
            self.trick_t = 0.45
            self.trick_count += 1
            self.missions[2]["prog"] += 1
            self.missions[4]["prog"] += 1
            self.particles.emit_dust(self.x, 0, self.z)
            return True
        return False

    def roll(self):
        if not self.in_air and not self.rolling:
            self.rolling    = True
            self.roll_timer = ROLL_DURATION
            return True
        return False

    def change_lane(self, direction):
        new_lane = clamp(self.lane + direction, 0, 2)
        if new_lane != self.lane and not self.lane_changing:
            self.lane_from      = self.lane
            self.lane_to        = new_lane
            self.lane           = new_lane
            self.lane_changing  = True
            self.lane_change_t  = 0.0
            self.lean           = -direction * 0.45
            return True
        return False

    # ── Power-ups ─────────────────────────────────────────────────────────────
    def _update_pups(self, dt):
        expired = [k for k,v in self.active_pups.items() if v <= dt]
        for k in expired:
            del self.active_pups[k]
        for k in list(self.active_pups):
            self.active_pups[k] -= dt

        self.multiplier = 1
        for pt, val in [(PU_X10,10),(PU_X5,5),(PU_X3,3),(PU_X2,2)]:
            if pt in self.active_pups:
                self.multiplier = val; break

    def activate_pup(self, ptype):
        base_dur = PU_DURATION.get(ptype, 10.0)
        if ptype == PU_SHIELD:
            base_dur += self.save.get("upgrades",{}).get("shield_duration",0) * 2.5
        if ptype == PU_JETPACK:
            base_dur += self.save.get("upgrades",{}).get("jetpack_fuel",0) * 3.0
        self.active_pups[ptype] = base_dur
        self.hud.flash(PU_COLOR.get(ptype, C_WHITE))
        self.particles.emit_powerup(self.x, self.y, self.z, PU_COLOR.get(ptype, C_WHITE))
        self.missions[3]["prog"] += 1

    # ── Collision / damage ────────────────────────────────────────────────────
    def _check_collision(self, obs):
        if self.invincible_t > 0 or self.godmode: return False
        if PU_JETPACK in self.active_pups and self.jetpack_alt > 1.4: return False
        ox, oz = obs["x"], obs["z"]
        otype  = obs["type"]
        dx, dz = abs(self.x - ox), abs(self.z - oz)
        if dx > 1.05 or dz > 3.2: return False
        if otype == OT_LOW_BAR and (self.rolling or self.y > 0.5): return False
        if otype == OT_HI_BAR  and self.y > 0.95: return False
        return dx < 0.92 and dz < 2.8

    def take_damage(self):
        if self.invincible_t > 0 or self.godmode: return
        if PU_SHIELD in self.active_pups:
            del self.active_pups[PU_SHIELD]
            self.hud.flash(C_CYAN); self.cam_shake = 0.35; return
        if self.hoverboard and not self.hoverboard_used:
            self.hoverboard_used = True
            self.hud.flash(C_BLUE); self.cam_shake = 0.30
            self.hud.warn("HOVERBOARD SAVED YOU!"); return
        self.hp          -= 1
        self.invincible_t = 2.2
        self.cam_shake    = 0.55
        self.streak       = 0; self.combo = 0
        self.hud.flash(C_RED, 0.25)
        self.particles.emit_explosion(self.x, self.y+0.5, self.z)
        if self.hp <= 0:
            self.alive = False

    # ── Coin collection ───────────────────────────────────────────────────────
    def _collect_coin(self, coin):
        now = time.time()
        if now - self.last_coin_t < 0.55:
            self.combo += 1
        else:
            self.combo = 1
        self.last_coin_t = now

        amount = 1 + self.upg_coin_dbl
        amount *= self.multiplier
        self.coins    += amount
        self.run_coins+= amount
        self.score    += amount * 12 * (1 + self.upg_score_boost * 0.5)
        self.streak   += 1
        if self.streak > self.max_streak:
            self.max_streak = self.streak
        if self.combo >= 6:
            self.hud.show_combo(f"COMBO x{self.combo}!")
        self.particles.emit_coin_sparkle(coin["x"], coin["y"], coin["z"])
        self.missions[1]["prog"] += 1

    # ── Camera ────────────────────────────────────────────────────────────────
    def _update_camera(self, dt, char_y):
        bob_int = self.settings.get("head_bob", 0.5)
        self.cam_bob_t += dt * clamp(self.speed/8.0, 0.3, 5.0) * 2.8
        bob_y = math.sin(self.cam_bob_t) * 0.07 * bob_int
        if self.cam_shake > 0:
            self.cam_shake -= dt
        sx = math.sin(time.time()*45) * self.cam_shake * 0.35
        sy = math.cos(time.time()*41) * self.cam_shake * 0.25

        mode = self.cam_mode
        if mode == "behind":
            self.cam_eye = [self.x+sx, 1.9 + bob_y + sy, self.z - 3.8]
            self.cam_at  = [self.x, char_y+1.1, self.z+14.0]
        elif mode == "side":
            self.cam_eye = [self.x-7.0+sx, 2.2+sy, self.z+2.0]
            self.cam_at  = [self.x, char_y+1.0, self.z+5.0]
        elif mode == "top":
            self.cam_eye = [self.x+sx, 11.0+sy, self.z-2.5]
            self.cam_at  = [self.x, 0.0, self.z+9.0]
        elif mode == "cinematic":
            self.cin_t += dt * 0.45
            cx = math.sin(self.cin_t) * 6.0 + self.x
            self.cam_eye = [cx+sx, 4.0+sy, self.z-5.0]
            self.cam_at  = [self.x, char_y+1.0, self.z+9.0]
        elif mode == "fps":
            self.cam_eye = [self.x+sx, char_y+1.65+sy, self.z+0.6]
            self.cam_at  = [self.x, char_y+1.65, self.z+15.0]
        else:
            self.cam_eye = [self.x+sx, 1.9+bob_y+sy, self.z-3.8]
            self.cam_at  = [self.x, char_y+1.1, self.z+14.0]

    # ── Main update ───────────────────────────────────────────────────────────
    def update(self, dt):
        if not self.alive: return

        self.session_t += dt
        self._update_speed(dt)

        eff_speed = self.speed * (0.30 if PU_SLOW in self.active_pups else 1.0)
        self.z        += eff_speed * dt
        self.distance += eff_speed * dt
        self.missions[0]["prog"] = int(self.distance)

        # Gravity
        if self.in_air or self.y > 0.0:
            self.vy += GRAVITY * dt
            self.y  += self.vy * dt
            if self.y <= 0.0:
                self.y = 0.0; self.vy = 0.0
                self.jumping = False; self.in_air = False; self.jump_count = 0
                self.particles.emit_dust(self.x, 0.0, self.z)

        # Roll
        if self.rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.rolling = False

        # Lane change (smooth)
        if self.lane_changing:
            self.lane_change_t += dt
            t2 = smoothstep(self.lane_change_t / LANE_CHANGE_T)
            self.x    = lerp(LANES[self.lane_from], LANES[self.lane_to], t2)
            self.lean = lerp(self.lean, 0.0, dt * 9.0)
            if self.lane_change_t >= LANE_CHANGE_T:
                self.lane_changing = False
                self.x = LANES[self.lane_to]
                self.lean = 0.0
        else:
            self.x = lerp(self.x, LANES[self.lane], dt * 18.0)

        # Trick spin
        if self.trick_t > 0:
            self.trick_t    -= dt
            self.trick_angle = math.sin(self.trick_t * math.pi / 0.45) * math.pi

        # Jetpack
        if PU_JETPACK in self.active_pups:
            self.jetpack_alt = min(3.8, self.jetpack_alt + dt * 4.5)
            self.particles.emit_jetpack(self.x, self.y, self.z)
        else:
            self.jetpack_alt = max(0.0, self.jetpack_alt - dt * 9.0)

        char_y = self.y + self.jetpack_alt

        self._update_pups(dt)
        self._update_camera(dt, char_y)

        # Invincibility
        if self.invincible_t > 0: self.invincible_t -= dt

        # Autopilot
        if self.autopilot.active:
            self.autopilot_dist += eff_speed * dt
            tl, sj, sr = self.autopilot.decide(
                {"lane":self.lane,"z":self.z,"speed":self.speed},
                self.obstacles, self.coins_list, self.powerups)
            if tl != self.lane and not self.lane_changing: self.change_lane(tl-self.lane)
            if sj: self.jump()
            if sr: self.roll()

        # Score from distance
        self.score += int(eff_speed * dt * self.multiplier * (1 + self.upg_score_boost*0.5))

        # Spawning
        self._spawn_world()
        self._despawn_world()
        self._check_collisions(char_y)

        # Particles
        self.particles.update(dt)
        if self.speed > 80:
            self.particles.emit_trail(self.x, char_y, self.z, clamp(self.speed/500.0,0,1))

        # Danger detection
        near_obs = [o for o in self.obstacles
                    if o.get("lane",1)==self.lane and 1.0<(o["z"]-self.z)<6.0]
        self.danger_near = bool(near_obs)
        if near_obs and (near_obs[0]["z"]-self.z) < 4.0:
            self.hud.warn("⚠  OBSTACLE AHEAD  ⚠")

        # FPS counter
        self._fps_frames += 1
        self._fps_t      += dt
        if self._fps_t >= 0.5:
            self.fps = int(self._fps_frames / self._fps_t)
            self._fps_frames = 0; self._fps_t = 0.0

        # HUD
        self.hud.update(dt, self.score, self.coins)

        # Achievements
        self._check_achievements()

        # Replay record
        self.replay_buf.append({
            "x":self.x,"y":char_y,"z":self.z,
            "lane":self.lane,"speed":self.speed,
        })

    # ── Spawning / despawning ─────────────────────────────────────────────────
    def _spawn_world(self):
        diff_m = 1.0 + self.distance / 6000.0
        look = self.z + SPAWN_AHEAD
        while self.obs_spawner.next_z < look:
            self.obstacles.extend(self.obs_spawner.spawn(diff_m))
        while self.coin_spawner.next_z < look:
            self.coins_list.extend(self.coin_spawner.spawn())
        self.buildings.extend(self.bld_spawner.try_spawn(self.z))
        # Random power-up spawn
        if random.random() < 0.0004 or (not self.powerups and random.random() < 0.0012):
            ptype = random.choice(list(PU_DURATION.keys()))
            lane  = random.randint(0,2)
            self.powerups.append({
                "type":ptype, "x":LANES[lane], "y":0.65, "z":look,
                "lane":lane, "ph":random.uniform(0, math.pi*2)
            })

    def _despawn_world(self):
        cut = self.z + DESPAWN_BEHIND
        self.obstacles  = [o for o in self.obstacles   if o["z"] > cut]
        self.coins_list = [c for c in self.coins_list  if c["z"] > cut]
        self.powerups   = [p for p in self.powerups    if p["z"] > cut]
        self.buildings  = [b for b in self.buildings   if b["z"] > cut - 40]

    def _check_collisions(self, char_y):
        # Obstacles
        for obs in self.obstacles:
            if self._check_collision(obs):
                self.take_damage(); break

        # Coins  (magnet range)
        mag_r = 0.9 + self.upg_mag_range * 0.5
        if PU_MAGNET in self.active_pups:
            mag_r = 3.0 + self.upg_mag_range * 0.7
        collected = []
        for c in self.coins_list:
            dist = math.sqrt((self.x-c["x"])**2 + (self.z-c["z"])**2)
            if dist < mag_r:
                self._collect_coin(c); collected.append(c)
        for c in collected: self.coins_list.remove(c)

        # Power-ups
        collected_p = []
        for p in self.powerups:
            dist = math.sqrt((self.x-p["x"])**2 + (self.z-p["z"])**2)
            if dist < 1.3:
                self.activate_pup(p["type"]); collected_p.append(p)
        for p in collected_p: self.powerups.remove(p)

    # ── Achievements ─────────────────────────────────────────────────────────
    def _check_achievements(self):
        achs = self.save.get("achievements", [])
        def unlock(aid):
            if aid not in achs:
                achs.append(aid); self.save["achievements"] = achs
                name = next((a[1] for a in ACHIEVEMENTS if a[0]==aid), aid)
                self.hud.push_achievement(name)
        if self.run_coins     >= 100:            unlock("coins_100")
        if self.save.get("total_coins",0)>=1000: unlock("coins_1000")
        if self.distance      >= 500:            unlock("dist_500")
        if self.distance      >= 2000:           unlock("dist_2000")
        if self.distance      >= 10000:          unlock("dist_10000")
        if self.speed         >= 500:            unlock("speed_500")
        if self.speed         >= 5000:           unlock("speed_5000")
        if self.speed         >= 10000:          unlock("speed_10000")
        if PU_JETPACK in self.active_pups:       unlock("jetpack_use")
        if PU_SHIELD  in self.active_pups:       unlock("shield_use")
        if PU_X10     in self.active_pups:       unlock("x10_use")
        if self.trick_count   >= 10:             unlock("trick_10")
        if self.max_streak    >= 20:             unlock("streak_20")
        if self.godmode:                         unlock("godmode")
        if self.autopilot_dist>= 1000:           unlock("autopilot")
        if self.save.get("total_runs",0) >= 10:  unlock("run_10")
        if self.save.get("total_runs",0) >= 50:  unlock("run_50")
        if self.score         >= 1_000_000:      unlock("speedrun_1m")

    # ── Render ────────────────────────────────────────────────────────────────
    def render(self, surf, ren: Renderer, t):
        theme = self.theme
        tc    = THEMES[theme]

        # Configure renderer for theme
        ren.fog_color = tc["fog"]
        ren.fog_dist  = tc["fog_dist"]
        ren.ambient   = tc["ambient"]
        sun = tc["sun"]
        sl  = math.sqrt(sum(x*x for x in sun))
        ren.sun_dir   = [x/sl for x in sun]

        # Build matrices
        proj = mat_perspective(self.fov, SCREEN_W/SCREEN_H, NEAR_PLANE, FAR_PLANE)
        view = mat_look_at(self.cam_eye, self.cam_at, [0,1,0])
        ren.pv = mat_mul(proj, view)

        # Sky gradient
        draw_sky_gradient(surf, theme)

        # Ground
        draw_ground_plane(surf, theme, self.z, ren)

        # Track
        draw_track(ren, self.z, theme)
        draw_overhead_cables(ren, self.z, theme)

        # Tunnel in subway theme
        if theme == "subway":
            draw_tunnel(ren, self.z - 2, FAR_PLANE + 4, theme)

        # Buildings
        for b in self.buildings:
            dz = b["z"] - self.z
            if -5 < dz < FAR_PLANE:
                draw_building(ren, b["x"], b["z"], b["w"], b["h"], b["d"], theme)

        # Coins
        for c in self.coins_list:
            dz = c["z"] - self.z
            if 0 < dz < FAR_PLANE:
                draw_coin_3d(ren, c["x"], c["y"], c["z"], t, c.get("ph",0))

        # Power-ups
        for p in self.powerups:
            dz = p["z"] - self.z
            if 0 < dz < FAR_PLANE:
                draw_powerup_box(ren, p["x"], p["y"], p["z"], p["type"], t, p.get("ph",0))

        # Obstacles
        for obs in self.obstacles:
            dz = obs["z"] - self.z
            if -2 < dz < FAR_PLANE:
                ot = obs["type"]
                if ot == OT_TRAIN:   draw_train(ren, obs["x"], obs["z"])
                elif ot == OT_LOW_BAR: draw_low_barrier(ren, obs["x"], obs["z"])
                elif ot == OT_HI_BAR:  draw_hi_barrier(ren, obs["x"], obs["z"])
                elif ot == OT_BARREL:  draw_barrel(ren, obs["x"], obs["z"])

        # Character
        char_y   = self.y + self.jetpack_alt
        char_cfg = CHARACTERS[self.settings.get("char_index",0)]
        char3d   = Character3D(char_cfg)
        char3d.wire = self.wireframe
        # Blink when invincible
        blink_ok = (int(self.invincible_t * 9) % 2 == 0) or self.invincible_t <= 0
        if blink_ok:
            char3d.anim_t = self.cam_bob_t
            char3d.draw(ren, self.x, char_y, self.z+0.8,
                        rolling=self.rolling,
                        jumping=self.in_air,
                        trick_angle=self.trick_angle if self.in_air else 0.0,
                        lean=self.lean,
                        jetpack_on=PU_JETPACK in self.active_pups)

        # Particles
        self.particles.draw(ren)

        # Speed lines
        speed_t = clamp(self.speed / 400.0, 0, 1)
        if speed_t > 0.05:
            self._draw_speed_lines(surf, speed_t, t)

        # Vignette / danger tint
        if self.danger_near:
            self._draw_danger_vignette(surf, t)

        # Night vision / grayscale overlays
        if self.night_vision:
            nv = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            nv.fill((0, 40, 0, 70))
            surf.blit(nv, (0,0))
        if self.scanlines:
            for sy2 in range(0, SCREEN_H, 3):
                pygame.draw.line(surf, (0,0,0), (0,sy2), (SCREEN_W,sy2), 1)

        # HUD
        self.hud.draw(surf, {
            "score": self.score, "coins": self.coins, "distance": self.distance,
            "speed": self.speed, "hp": self.hp, "multiplier": self.multiplier,
            "active_powerups": self.active_pups, "lane": self.lane,
            "fps": self.fps, "autopilot": self.autopilot.active,
            "godmode": self.godmode, "streak": self.streak,
            "session_t": self.session_t, "show_fps": self.settings.get("show_fps",True),
        })

    def _draw_speed_lines(self, surf, intensity, t):
        cx, cy = SCREEN_W//2, SCREEN_H//2
        n = int(intensity * 28)
        for i in range(n):
            angle = (i/n)*2*math.pi + t*0.6
            r0 = SCREEN_H * 0.18
            r1 = SCREEN_H * (0.22 + intensity * 0.45 * random.random())
            x0 = cx + int(math.cos(angle)*r0)
            y0 = cy + int(math.sin(angle)*r0)
            x1 = cx + int(math.cos(angle)*r1)
            y1 = cy + int(math.sin(angle)*r1)
            alpha = int(intensity * 80)
            col = (alpha, alpha+20, alpha+30)
            pygame.draw.line(surf, col, (x0,y0), (x1,y1), 1)

    def _draw_danger_vignette(self, surf, t):
        pulse = 0.4 + 0.6 * abs(math.sin(t * 7.0))
        alpha = int(pulse * 60)
        vig = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        # Radial gradient approximation via border strips
        for thick in range(8, 0, -2):
            a = alpha * (9-thick) // 8
            pygame.draw.rect(vig, (200, 20, 20, a),
                             (thick*4, thick*3, SCREEN_W-thick*8, SCREEN_H-thick*6), thick)
        surf.blit(vig, (0,0))

# ══════════════════════════════════════════════════════════════════════════════
#  MENU SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

class MenuSystem:
    def __init__(self, screen, save_data):
        self.screen    = screen
        self.save      = save_data
        pygame.font.init()
        fn = pygame.font.match_font("segoeui,arial,freesansbold,sans")
        fn2= pygame.font.match_font("consolas,couriernew,monospace")
        self.f_huge  = pygame.font.Font(fn, 60) if fn else pygame.font.SysFont(None, 60)
        self.f_big   = pygame.font.Font(fn, 40) if fn else pygame.font.SysFont(None, 40)
        self.f_med   = pygame.font.Font(fn, 28) if fn else pygame.font.SysFont(None, 28)
        self.f_small = pygame.font.Font(fn, 20) if fn else pygame.font.SysFont(None, 20)
        self.f_tiny  = pygame.font.Font(fn2,16) if fn2 else pygame.font.SysFont(None, 16)
        self.clock   = pygame.time.Clock()

    def _clear(self, color=(8,8,18)):
        self.screen.fill(color)

    def _text(self, text, font, color, x, y, center=False, shadow=True):
        if shadow:
            s = font.render(text, True, (0,0,0))
            r = s.get_rect(); r.centerx=x if center else None; r.x=x if not center else r.x; r.y=y
            self.screen.blit(s, (r.x+3, r.y+3))
        s = font.render(text, True, color)
        r = s.get_rect()
        if center: r.centerx = x
        else: r.x = x
        r.y = y
        self.screen.blit(s, r)

    def _draw_bg_lines(self, t):
        """Animated racing lines background for menus"""
        for i in range(12):
            y = (i * 65 + int(t * 80)) % SCREEN_H
            alpha = 20 + (i % 3) * 15
            pygame.draw.line(self.screen, (alpha, alpha, alpha+30), (0, y), (SCREEN_W, y), 1)

    def main_menu(self):
        items = [
            ("▶  START GAME",   "play"),
            ("⚙  SETTINGS",     "settings"),
            ("🏆  LEADERBOARD", "leaderboard"),
            ("📊  STATS",       "stats"),
            ("🛒  SHOP",        "shop"),
            ("❓  HOW TO PLAY", "tutorial"),
            ("✖  QUIT",         "quit"),
        ]
        sel = 0
        clock = pygame.time.Clock()
        t0 = time.time()
        while True:
            dt = clock.tick(60) / 1000.0
            t  = time.time() - t0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:    sel = (sel-1) % len(items)
                    if event.key == pygame.K_DOWN:  sel = (sel+1) % len(items)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return items[sel][1]
                    if event.key == pygame.K_ESCAPE: return "quit"

            self._clear((5, 5, 18))
            self._draw_bg_lines(t)

            # Title
            pulse = abs(math.sin(t*1.2))
            tc = lerp_color(C_CYAN, C_NEON_P, pulse)
            self._text("SUBWAY SURFERS 3D", self.f_huge, tc, SCREEN_W//2, 28, center=True)
            self._text("ULTIMATE  PYTHON  EDITION", self.f_small, C_GRAY, SCREEN_W//2, 96, center=True)
            self._text(f"v{VERSION}", self.f_tiny, C_DKGRAY, SCREEN_W//2, 122, center=True)

            # Animated runner icon
            frame = ['♟','♞','♝','♜'][int(t*5)%4]
            self._text(frame*7, self.f_med, C_CYAN, SCREEN_W//2, 148, center=True)

            # High score / level
            hs = self.save.get("high_score",0)
            lv = self.save.get("level",1)
            xp = self.save.get("xp",0)
            tc2= self.save.get("total_coins",0)
            self._text(f"HIGH SCORE: {hs:,}", self.f_big, C_YELLOW, SCREEN_W//2, 186, center=True)
            self._text(f"LV {lv}  XP {xp}  ●{tc2}", self.f_small, C_GREEN, SCREEN_W//2, 234, center=True)

            # Menu items
            for i, (label, _) in enumerate(items):
                y = 278 + i * 54
                if i == sel:
                    pygame.draw.rect(self.screen, (30,30,80), (SCREEN_W//2-200, y-4, 400, 46), border_radius=8)
                    pygame.draw.rect(self.screen, C_CYAN,     (SCREEN_W//2-200, y-4, 400, 46), 2, border_radius=8)
                    col = C_CYAN
                else:
                    col = C_LTGRAY
                self._text(label, self.f_med, col, SCREEN_W//2, y, center=True)

            self._text("↑ ↓ Navigate  |  ENTER Select  |  ESC Quit",
                       self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def settings_menu(self, settings):
        options = [
            ("Theme",       "theme",       list(THEMES.keys())),
            ("Difficulty",  "difficulty",  list(DIFFICULTIES.keys())),
            ("Character",   "char_index",  list(range(len(CHARACTERS)))),
            ("Camera",      "camera",      ["behind","side","top","cinematic","fps"]),
            ("Show FPS",    "show_fps",    [True, False]),
            ("Sound FX",    "sound",       [True, False]),
            ("Music",       "music",       [True, False]),
            ("Color Grade", "color_grade", ["neutral","warm","cool","vivid"]),
            ("Head Bob",    "head_bob",    [0.0, 0.25, 0.5, 0.75, 1.0]),
            ("FOV",         "fov",         [55.0, 65.0, 72.0, 80.0, 90.0, 100.0]),
            ("Fullscreen",  "fullscreen",  [False, True]),
            ("Wireframe",   "wireframe",   [False, True]),
            ("← BACK",      None,          None),
        ]
        sel = 0; clock = pygame.time.Clock(); t0 = time.time()
        while True:
            dt = clock.tick(60)/1000.0; t = time.time()-t0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return settings
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:   sel = (sel-1)%len(options)
                    if event.key == pygame.K_DOWN: sel = (sel+1)%len(options)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
                        if options[sel][1] is None or event.key == pygame.K_ESCAPE:
                            return settings
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        _, key, vals = options[sel]
                        if key:
                            cur = settings.get(key, vals[0])
                            try: idx = vals.index(cur)
                            except: idx = 0
                            idx = (idx + (1 if event.key==pygame.K_RIGHT else -1)) % len(vals)
                            settings[key] = vals[idx]

            self._clear((5,8,20))
            self._draw_bg_lines(t)
            self._text("SETTINGS", self.f_big, C_CYAN, SCREEN_W//2, 20, center=True)
            for i, (label, key, vals) in enumerate(options):
                y = 80 + i*46
                if key:
                    cv = settings.get(key, vals[0] if vals else "")
                    if key == "char_index": cv = CHARACTERS[cv]["name"]
                    disp = f"{label:<18}  {str(cv)}"
                else:
                    disp = label
                if i == sel:
                    pygame.draw.rect(self.screen,(30,30,70),(SCREEN_W//2-240,y-4,480,38),border_radius=6)
                    pygame.draw.rect(self.screen,C_CYAN,(SCREEN_W//2-240,y-4,480,38),2,border_radius=6)
                    self._text(f"◄  {disp}  ►", self.f_small, C_CYAN, SCREEN_W//2, y, center=True)
                else:
                    self._text(disp, self.f_small, C_LTGRAY, SCREEN_W//2, y, center=True)
            self._text("↑↓ Navigate  |  ←→ Change  |  ESC/ENTER=Back",
                       self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def leaderboard_screen(self):
        lb = self.save.get("leaderboard",[])
        lb.sort(key=lambda x:x.get("score",0),reverse=True)
        clock = pygame.time.Clock(); t0 = time.time()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type in (pygame.QUIT,): return
                if event.type == pygame.KEYDOWN: return
                if event.type == pygame.MOUSEBUTTONDOWN: return
            self._clear((4,4,16))
            self._draw_bg_lines(time.time()-t0)
            self._text("LEADERBOARD", self.f_big, C_YELLOW, SCREEN_W//2, 20, center=True)
            hdr = f"{'#':<4}  {'SCORE':>12}  {'DIST':>8}  {'COINS':>7}  {'CHAR'}"
            self._text(hdr, self.f_small, C_GRAY, 120, 80)
            for i, entry in enumerate(lb[:10]):
                y = 118 + i*46
                cols = [C_YELLOW, C_LTGRAY, C_ORANGE] + [C_GRAY]*7
                medal = ["🥇","🥈","🥉"][i] if i<3 else f" {i+1}"
                row = (f"{medal:<4}  {entry.get('score',0):>12,}  "
                       f"{entry.get('distance',0):>7.0f}m  "
                       f"{entry.get('coins',0):>7}  "
                       f"{entry.get('char','?')}")
                self._text(row, self.f_small, cols[i], 120, y)
            self._text("Press any key to return", self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def stats_screen(self):
        s = self.save; achs = s.get("achievements",[])
        clock = pygame.time.Clock(); t0 = time.time()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN: return
                if event.type == pygame.MOUSEBUTTONDOWN: return
            self._clear((4,8,12))
            self._draw_bg_lines(time.time()-t0)
            self._text("STATS", self.f_big, C_GREEN, SCREEN_W//2, 16, center=True)
            left = [
                ("Total Runs",      s.get("total_runs",0)),
                ("Total Distance",  f"{s.get('total_distance',0.0):.0f} m"),
                ("Total Coins",     f"● {s.get('total_coins',0)}"),
                ("High Score",      f"{s.get('high_score',0):,}"),
                ("Level",           s.get("level",1)),
                ("XP",              s.get("xp",0)),
                ("Longest Run",     f"{s.get('longest_run',0.0):.0f} m"),
                ("Most Coins/Run",  s.get("most_coins_run",0)),
                ("Longest Streak",  s.get("longest_streak",0)),
                ("Total Tricks",    s.get("total_tricks",0)),
                ("Achievements",    f"{len(achs)}/{len(ACHIEVEMENTS)}"),
            ]
            for i,(lbl,val) in enumerate(left):
                y = 72+i*46
                self._text(f"{lbl:<22}", self.f_small, C_GRAY,  100, y)
                self._text(str(val),    self.f_small, C_WHITE, 380, y)
            # Achievement list
            self._text("Achievements Unlocked:", self.f_small, C_YELLOW, 620, 72)
            for i, (aid,aname,_) in enumerate(ACHIEVEMENTS[:16]):
                if aid in achs:
                    self._text(f"★ {aname}", self.f_tiny, C_YELLOW, 628, 100+i*26)
                else:
                    self._text(f"  {aname}", self.f_tiny, C_DKGRAY,  628, 100+i*26)
            self._text("Press any key to return", self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def shop_screen(self):
        upgrades = self.save.get("upgrades", copy.deepcopy(DEFAULT_SAVE["upgrades"]))
        items = [
            ("Coin Doubler",    "coin_doubler",    3, 200, "Double all coin pickups"),
            ("Head Start",      "head_start",      3, 150, "+100 m at run start"),
            ("Score Booster",   "score_booster",   3, 300, "+50% score per level"),
            ("Magnet Range",    "magnet_range",    3, 100, "Wider coin magnet"),
            ("Shield Duration", "shield_duration", 3, 200, "+2.5 s per level"),
            ("Jetpack Fuel",    "jetpack_fuel",    3, 250, "+3 s per level"),
            ("← BACK",          None,              0,   0, ""),
        ]
        sel = 0; clock = pygame.time.Clock(); t0 = time.time()
        msg = ""; msg_t = 0.0
        while True:
            dt = clock.tick(60)/1000.0; msg_t -= dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:   sel=(sel-1)%len(items)
                    if event.key == pygame.K_DOWN: sel=(sel+1)%len(items)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        lbl,key,maxl,cost,_ = items[sel]
                        if key is None: self.save["upgrades"]=upgrades; return
                        cur = upgrades.get(key,0)
                        tc2 = self.save.get("total_coins",0)
                        if cur >= maxl:       msg="MAX LEVEL!"; msg_t=2.0
                        elif tc2 < cost:      msg="Not enough coins!"; msg_t=2.0
                        else:
                            upgrades[key]=cur+1
                            self.save["total_coins"]=tc2-cost
                            self.save["upgrades"]=upgrades
                            save_game(self.save)
                            msg=f"Upgraded {lbl}!"; msg_t=2.0
                    if event.key == pygame.K_ESCAPE:
                        self.save["upgrades"]=upgrades; return
            self._clear((4,8,4))
            self._draw_bg_lines(time.time()-t0)
            self._text("SHOP", self.f_big, C_YELLOW, SCREEN_W//2, 16, center=True)
            self._text(f"Coins:  ● {self.save.get('total_coins',0):,}", self.f_med, C_YELLOW, SCREEN_W//2, 70, center=True)
            for i,(lbl,key,maxl,cost,desc) in enumerate(items):
                y = 120+i*68
                if i==sel:
                    pygame.draw.rect(self.screen,(30,50,30),(SCREEN_W//2-280,y-6,560,58),border_radius=8)
                    pygame.draw.rect(self.screen,C_GREEN,(SCREEN_W//2-280,y-6,560,58),2,border_radius=8)
                if key:
                    lvl = upgrades.get(key,0)
                    stars = "★"*lvl + "☆"*(maxl-lvl)
                    col = C_CYAN if i==sel else C_LTGRAY
                    self._text(f"{lbl:<22} {stars:<6} Cost: ●{cost}", self.f_small, col, SCREEN_W//2-270, y)
                    self._text(desc, self.f_tiny, C_GRAY, SCREEN_W//2-260, y+28)
                else:
                    self._text(lbl, self.f_small, C_CYAN if i==sel else C_LTGRAY, SCREEN_W//2, y, center=True)
            if msg_t > 0:
                self._text(msg, self.f_med, C_YELLOW, SCREEN_W//2, SCREEN_H//2, center=True)
            self._text("↑↓ Navigate  |  ENTER Buy  |  ESC Back",
                       self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def tutorial_screen(self):
        pages = [
            ("MOVEMENT",
             ["← →  Arrow Keys: Change lane",
              "↑  /  SPACE:  Jump  (press twice for double jump)",
              "↓:  Roll / slide under low barriers",
              "SHIFT:  Sprint    |    B:  Brake",
              "Camera changes speed feel — try Cinematic mode!"]),
            ("OBSTACLES",
             ["TRAIN (blue):  Huge — change lane or jump high",
              "LOW BARRIER (red):  Roll UNDER it  (↓ key)",
              "HIGH BARRIER (red+yellow):  JUMP over it  (↑ key)",
              "BARREL (brown):  Jump or dodge sideways",
              "COMBO:  Multiple obstacles — plan ahead!"]),
            ("POWER-UPS",
             ["M  Magnet:  Attracts nearby coins  (12 s)",
              "S  Shield:  Blocks one collision  (8 s)",
              "J  Jetpack:  Fly high over everything  (12 s)",
              "↑  Super Sneakers:  Triple jump height  (10 s)",
              "x2 x3 x5 x10:  Score multiplier boost",
              "~  Slow Motion  |  !  Turbo Boost"]),
            ("SPECIAL KEYS",
             ["A:  Toggle Autopilot AI  (SHIFT+A cycles AI mode)",
              "G:  God Mode — complete invincibility",
              "P  /  ESC:  Pause menu",
              "C:  Cycle camera (Behind/Side/Top/Cinematic/FPS)",
              "T:  Cycle themes  (City/Subway/Desert/Night/Neon)",
              "W:  Wireframe mode  |  N:  Night vision",
              "1–6:  Speed presets  |  +/-:  Fine speed control"]),
            ("PROGRESSION",
             ["Coins buy upgrades in the SHOP",
              "XP is earned each run — Level up for bragging rights",
              "Complete 5 Missions per run for bonus XP",
              "Unlock 20 Achievements — check STATS screen",
              "Top-10 Leaderboard tracks your best runs",
              "Difficulty: Easy→Normal→Hard→Insane→Ludicrous"]),
        ]
        sel = 0; clock = pygame.time.Clock(); t0 = time.time()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RIGHT, pygame.K_RETURN): sel = min(sel+1, len(pages)-1)
                    if event.key == pygame.K_LEFT: sel = max(sel-1, 0)
                    if event.key == pygame.K_ESCAPE: return
                    if event.key == pygame.K_RETURN and sel == len(pages)-1: return
            self._clear((4,6,16))
            self._draw_bg_lines(time.time()-t0)
            title, lines = pages[sel]
            self._text(f"{title}  ({sel+1}/{len(pages)})", self.f_big, C_CYAN, SCREEN_W//2, 24, center=True)
            for i, line in enumerate(lines):
                self._text(line, self.f_small, C_WHITE, SCREEN_W//2, 100+i*56, center=True)
            nav = "← Prev  |  → Next  |  ESC Close" if sel < len(pages)-1 else "← Prev  |  ENTER Start Game  |  ESC Close"
            self._text(nav, self.f_tiny, C_DKGRAY, SCREEN_W//2, SCREEN_H-26, center=True)
            pygame.display.flip()

    def game_over_screen(self, game: GameState):
        """Feature 116 — run again / main menu after death"""
        score    = game.score
        dist     = game.distance
        coins    = game.run_coins
        streak   = game.max_streak
        tricks   = game.trick_count
        s = self.save
        new_hs = score > s.get("high_score",0)
        if new_hs: s["high_score"] = score
        s["total_coins"]    = s.get("total_coins",0) + coins
        s["total_distance"] = s.get("total_distance",0.0) + dist
        s["total_runs"]     = s.get("total_runs",0) + 1
        if dist   > s.get("longest_run",0.0):     s["longest_run"]     = dist
        if coins  > s.get("most_coins_run",0):    s["most_coins_run"]  = coins
        if streak > s.get("longest_streak",0):    s["longest_streak"]  = streak
        s["total_tricks"] = s.get("total_tricks",0) + tricks
        xp_gain = int(dist/8) + coins*2 + score//80
        s["xp"]    = s.get("xp",0) + xp_gain
        s["level"] = 1 + s["xp"] // 1000
        # Achievements
        if s.get("total_runs",0)==1:
            if "first_run" not in s.get("achievements",[]): s.setdefault("achievements",[]).append("first_run")
        # Leaderboard
        char_name = CHARACTERS[s.get("settings",{}).get("char_index",0)]["name"]
        lb = s.get("leaderboard",[])
        lb.append({"score":score,"distance":dist,"coins":coins,"char":char_name})
        lb.sort(key=lambda x:x.get("score",0),reverse=True)
        s["leaderboard"] = lb[:10]
        save_game(s)

        sel = 0; clock = pygame.time.Clock(); t0 = time.time()
        choices = [("▶  PLAY AGAIN", "play"), ("▶  MAIN MENU", "menu")]
        while True:
            dt = clock.tick(60)/1000.0; t = time.time()-t0
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:   sel=0
                    if event.key == pygame.K_DOWN: sel=1
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER): return choices[sel][1]
                    if event.key == pygame.K_r: return "play"
                    if event.key == pygame.K_m: return "menu"
                    if event.key == pygame.K_ESCAPE: return "menu"
            self._clear((18,4,4))
            self._draw_bg_lines(t*0.5)
            # Animated big "GAME OVER"
            scale = 1.0 + 0.06*math.sin(t*3)
            go_s = self.f_huge.render("GAME  OVER", True, C_RED)
            gw = int(go_s.get_width()*scale); gh = int(go_s.get_height()*scale)
            go_scaled = pygame.transform.scale(go_s,(gw,gh))
            self.screen.blit(go_scaled, go_scaled.get_rect(centerx=SCREEN_W//2, y=22))

            y = 110
            rows = [
                (f"SCORE",    f"{score:>14,}", C_WHITE if not new_hs else C_YELLOW),
                (f"DISTANCE", f"{dist:>12.0f} m", C_GREEN),
                (f"COINS",    f"●{coins:>13}", C_YELLOW),
                (f"STREAK",   f"{streak:>13}x", C_ORANGE),
                (f"TRICKS",   f"{tricks:>14}", C_CYAN),
                (f"XP EARNED",f"+{xp_gain:>12}", C_NEON_G),
            ]
            if new_hs:
                self._text("★  NEW HIGH SCORE!  ★", self.f_big, C_YELLOW, SCREEN_W//2, y, center=True); y+=56
            for lbl,val,col in rows:
                self._text(f"{lbl:<14}", self.f_med, C_GRAY,  SCREEN_W//2-200, y)
                self._text(val,          self.f_med, col,     SCREEN_W//2+60,  y)
                y += 46

            # Mission summary
            y += 12
            self._text("── Missions ──", self.f_small, C_GRAY, SCREEN_W//2, y, center=True); y+=30
            for m in game.missions:
                prog = m["prog"]; target = m["target"]
                pct  = clamp(prog/max(1,target),0,1)
                done = prog >= target
                col  = C_GREEN if done else C_GRAY
                bar_w = 160
                pygame.draw.rect(self.screen,(40,40,40),(SCREEN_W//2-bar_w//2, y+16, bar_w, 10),border_radius=3)
                pygame.draw.rect(self.screen,col,       (SCREEN_W//2-bar_w//2, y+16, int(bar_w*pct), 10),border_radius=3)
                prefix = "✓" if done else "○"
                self._text(f"{prefix} {m['name']:<28}", self.f_tiny, col, SCREEN_W//2-240, y)
                y += 30

            for i,(lbl,_) in enumerate(choices):
                cy = SCREEN_H - 120 + i*52
                if i == sel:
                    pygame.draw.rect(self.screen,(50,50,120),(SCREEN_W//2-180,cy-6,360,44),border_radius=8)
                    pygame.draw.rect(self.screen,C_CYAN,(SCREEN_W//2-180,cy-6,360,44),2,border_radius=8)
                self._text(lbl, self.f_med, C_CYAN if i==sel else C_LTGRAY, SCREEN_W//2, cy, center=True)
            self._text("R=Retry  M=Menu  ↑↓=Select  ENTER=Confirm",
                       self.f_tiny,C_DKGRAY,SCREEN_W//2,SCREEN_H-18,center=True)
            pygame.display.flip()

    def pause_menu(self, game: GameState):
        sel = 0; clock = pygame.time.Clock()
        items = [
            ("▶  RESUME",         "resume"),
            ("⚙  SETTINGS",       "settings"),
            ("A  TOGGLE AUTOPILOT","autopilot"),
            ("G  TOGGLE GOD MODE", "god"),
            ("D  CYCLE DIFFICULTY","diff"),
            ("↩  MAIN MENU",       "menu"),
        ]
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "menu"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:   sel=(sel-1)%len(items)
                    if event.key == pygame.K_DOWN: sel=(sel+1)%len(items)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        act = items[sel][1]
                        if act == "resume": return "resume"
                        if act == "menu":   return "menu"
                        if act == "god":    game.godmode = not game.godmode
                        if act == "autopilot":
                            game.autopilot.active = not game.autopilot.active
                        if act == "diff":
                            diffs = list(DIFFICULTIES.keys())
                            cur   = game.settings.get("difficulty","Normal")
                            idx   = diffs.index(cur) if cur in diffs else 1
                            game.settings["difficulty"] = diffs[(idx+1)%len(diffs)]
                        if act == "settings":
                            self.settings_menu(game.settings)
                    if event.key in (pygame.K_ESCAPE, pygame.K_p): return "resume"

            # Blur background: just darken
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0,0,0,175))
            self.screen.blit(overlay, (0,0))
            # Panel
            pw, ph = 460, 70+len(items)*58
            px2, py2 = SCREEN_W//2-pw//2, SCREEN_H//2-ph//2
            pygame.draw.rect(self.screen,(12,12,32),(px2,py2,pw,ph),border_radius=12)
            pygame.draw.rect(self.screen,C_CYAN,(px2,py2,pw,ph),2,border_radius=12)
            self._text("PAUSED", self.f_big, C_CYAN, SCREEN_W//2, py2+14, center=True)
            ap_str  = f"Autopilot: {'ON  ('+game.autopilot.mode+')' if game.autopilot.active else 'OFF'}"
            god_str = f"God Mode:  {'ON' if game.godmode else 'OFF'}"
            diff_str= f"Difficulty: {game.settings.get('difficulty','Normal')}"
            for info in [ap_str, god_str, diff_str,
                         f"Distance:  {game.distance:.0f} m",
                         f"Score:  {game.score:,}"]:
                pass  # drawn below
            for i,(lbl,_) in enumerate(items):
                y = py2+68+i*54
                if i==sel:
                    pygame.draw.rect(self.screen,(30,30,80),(px2+10,y-4,pw-20,44),border_radius=6)
                    pygame.draw.rect(self.screen,C_CYAN,(px2+10,y-4,pw-20,44),2,border_radius=6)
                col = C_CYAN if i==sel else C_LTGRAY
                self._text(lbl, self.f_small, col, SCREEN_W//2, y, center=True)
            # Status strip
            strip = pygame.Surface((pw, 48), pygame.SRCALPHA)
            strip.fill((20,20,20,180))
            self.screen.blit(strip, (px2, py2+ph+6))
            self._text(f"SPD {game.speed:.0f}  |  DIST {game.distance:.0f}m  |  {ap_str}  |  {god_str}",
                       self.f_tiny, C_GRAY, px2+8, py2+ph+16)
            pygame.display.flip()

# ══════════════════════════════════════════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════════════════════════════════════════

def run_game_loop(screen, save_data, settings, menu_sys: MenuSystem):
    """Single run of the game"""
    clock = pygame.time.Clock()
    ren   = Renderer(screen)
    game  = GameState(save_data, settings)

    # Tutorial first run
    if save_data.get("total_runs",0) == 0:
        game.hud.warn("← → JUMP ROLL  |  A=Autopilot  |  P=Pause")

    # Konami code buffer (feature 118)
    KONAMI = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN,
              pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT,
              pygame.K_b, pygame.K_a]
    kbuf : list = []

    last_time = time.time()

    while True:
        now = time.time()
        dt  = min(now - last_time, 0.05)
        last_time = now

        # ── Events ─────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                # Konami check
                kbuf.append(event.key)
                if len(kbuf) > len(KONAMI): kbuf.pop(0)
                if kbuf == KONAMI:
                    game.godmode = not game.godmode
                    game.hud.push_achievement("KONAMI CODE ACTIVATED!")
                    kbuf.clear()

                k = event.key
                if k == pygame.K_p or k == pygame.K_ESCAPE:
                    result = menu_sys.pause_menu(game)
                    if result == "menu": return "menu"
                    last_time = time.time()
                    continue
                if not game.autopilot.active:
                    if k == pygame.K_LEFT:  game.change_lane(-1)
                    if k == pygame.K_RIGHT: game.change_lane(1)
                    if k in (pygame.K_UP, pygame.K_SPACE): game.jump()
                    if k == pygame.K_DOWN:  game.roll()
                # Global keys
                if k == pygame.K_a:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        modes = AutopilotAI.MODES
                        idx   = modes.index(game.autopilot.mode)
                        game.autopilot.mode = modes[(idx+1)%len(modes)]
                    else:
                        game.autopilot.active = not game.autopilot.active
                if k == pygame.K_g:
                    game.godmode = not game.godmode
                    game.hud.flash(C_YELLOW)
                if k == pygame.K_w:
                    game.wireframe = not game.wireframe
                if k == pygame.K_c:
                    modes = ["behind","side","top","cinematic","fps"]
                    idx = modes.index(game.cam_mode) if game.cam_mode in modes else 0
                    game.cam_mode = modes[(idx+1)%len(modes)]
                if k == pygame.K_t:
                    tl = list(THEMES.keys())
                    idx = tl.index(game.theme) if game.theme in tl else 0
                    game.theme = tl[(idx+1)%len(tl)]
                    settings["theme"] = game.theme
                if k == pygame.K_n: game.night_vision = not game.night_vision
                if k == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    game.scanlines = not game.scanlines
                if k == pygame.K_m: game.active_pups[PU_SLOW]    = 6.0
                if k == pygame.K_j: game.active_pups[PU_JETPACK] = 12.0
                if k == pygame.K_x: game.active_pups[PU_X10]     = 8.0
                if k == pygame.K_h: game.hoverboard = True; game.hoverboard_used = False
                if k == pygame.K_1: game.manual_speed = 10.0
                if k == pygame.K_2: game.manual_speed = 60.0
                if k == pygame.K_3: game.manual_speed = 250.0
                if k == pygame.K_4: game.manual_speed = 1000.0
                if k == pygame.K_5: game.manual_speed = 4000.0
                if k == pygame.K_6: game.manual_speed = 10000.0
                if k == pygame.K_0: game.manual_speed = None
                if k == pygame.K_PLUS  or k == pygame.K_EQUALS:
                    game.manual_speed = min(MAX_SPEED, (game.manual_speed or game.speed)*1.4)
                if k == pygame.K_MINUS:
                    game.manual_speed = max(0.5, (game.manual_speed or game.speed)*0.7)
                if k == pygame.K_d:
                    diffs = list(DIFFICULTIES.keys())
                    cur   = settings.get("difficulty","Normal")
                    idx   = diffs.index(cur) if cur in diffs else 1
                    settings["difficulty"] = diffs[(idx+1)%len(diffs)]
                if k == pygame.K_r:
                    if game.replay_buf:
                        game.replay_mode  = True
                        game.replay_data  = list(game.replay_buf)
                        game.replay_idx   = 0
                if k == pygame.K_f:
                    settings["show_fps"] = not settings.get("show_fps",True)

        # Sprint & brake from held keys
        keys = pygame.key.get_pressed()
        game.sprinting = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        game.braking   = bool(keys[pygame.K_b])
        if not game.autopilot.active:
            if keys[pygame.K_LEFT]  and not game.lane_changing: pass
            if keys[pygame.K_RIGHT] and not game.lane_changing: pass

        # ── Update ─────────────────────────────────────────────────────────
        if game.replay_mode:
            if game.replay_idx < len(game.replay_data):
                frame = game.replay_data[game.replay_idx]
                game.x    = frame["x"]
                game.y    = 0.0
                game.z    = frame["z"]
                game.lane = frame["lane"]
                game.speed= frame["speed"]
                game._update_camera(dt, frame["y"])
                game.replay_idx += 1
            else:
                game.replay_mode = False
        else:
            game.update(dt)

        # ── Check alive ────────────────────────────────────────────────────
        if not game.alive:
            result = menu_sys.game_over_screen(game)
            return result

        # ── Render ─────────────────────────────────────────────────────────
        t = time.time()
        screen.fill((0,0,0))
        game.render(screen, ren, t)

        # Replay indicator
        if game.replay_mode:
            rep_s = menu_sys.f_big.render("◉ REPLAY", True, C_RED)
            screen.blit(rep_s, (SCREEN_W//2 - rep_s.get_width()//2, SCREEN_H//2-20))

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    return "menu"

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main():
    pygame.init()
    pygame.display.set_caption(TITLE)

    # Try to set window icon
    try:
        icon = pygame.Surface((32,32))
        icon.fill(C_BLUE)
        pygame.draw.circle(icon, C_YELLOW, (16,16), 10)
        pygame.display.set_icon(icon)
    except Exception:
        pass

    save_data = load_save()
    settings  = save_data.setdefault("settings", copy.deepcopy(DEFAULT_SAVE["settings"]))

    # Fullscreen support
    flags = pygame.DOUBLEBUF
    if settings.get("fullscreen", False):
        flags |= pygame.FULLSCREEN

    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
    menu_sys = MenuSystem(screen, save_data)

    print(f"[Subway Surfers 3D v{VERSION}] Running — {SCREEN_W}×{SCREEN_H}")
    print(f"  Save: {SAVE_FILE}")
    print(f"  Runs: {save_data.get('total_runs',0)}  HighScore: {save_data.get('high_score',0)}")

    action = "menu"
    while action != "quit":
        if action == "menu":
            action = menu_sys.main_menu()
        elif action == "settings":
            menu_sys.settings_menu(settings)
            save_data["settings"] = settings
            save_game(save_data)
            action = "menu"
        elif action == "leaderboard":
            menu_sys.leaderboard_screen()
            action = "menu"
        elif action == "stats":
            menu_sys.stats_screen()
            action = "menu"
        elif action == "shop":
            menu_sys.shop_screen()
            action = "menu"
        elif action == "tutorial":
            menu_sys.tutorial_screen()
            action = "menu"
        elif action == "play":
            action = run_game_loop(screen, save_data, settings, menu_sys)
            save_data["settings"] = settings
            save_game(save_data)
        elif action == "quit":
            break
        else:
            action = "menu"

    save_game(save_data)
    pygame.quit()
    print("Thanks for playing! Final stats:")
    print(f"  High Score: {save_data.get('high_score',0):,}")
    print(f"  Total Runs: {save_data.get('total_runs',0)}")
    print(f"  Total Coins: {save_data.get('total_coins',0)}")
    print(f"  Level: {save_data.get('level',1)}")

if __name__ == "__main__":
    main()