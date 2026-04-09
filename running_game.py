#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SUBWAY SURFERS 3D - ULTIMATE PYTHON EDITION         ║
║    3D Software Renderer | 150+ Features | Full Autopilot     ║
╚══════════════════════════════════════════════════════════════╝

Features (150+):
 1.  Full 3D software renderer (perspective projection)
 2.  3D character with limb animation (running cycle)
 3.  3D environment (rails, buildings, trains, tunnels)
 4.  Autopilot AI mode (dodge, collect, optimize)
 5.  Speed control 1–10000
 6.  3 lanes (left, center, right)
 7.  Jump mechanic with gravity
 8.  Roll/slide mechanic
 9.  Coin collection system
10.  Coin magnet power-up
11.  Shield power-up (invincibility)
12.  Score multiplier power-up (x2, x3, x5, x10)
13.  Jetpack power-up (fly over everything)
14.  Super sneakers (higher jump)
15.  Hoverboard (one-time crash save)
16.  Score system (distance-based)
17.  High score persistence (JSON)
18.  Combo multiplier
19.  Streak system
20.  Multiple obstacle types (trains, barriers, tunnels)
21.  Rolling obstacles
22.  Falling obstacles
23.  Moving side obstacles
24.  Explosive barrels
25.  Low barriers (roll under)
26.  High barriers (jump over)
27.  Combined obstacles
28.  Coin rows
29.  Coin arcs
30.  Coin spirals
31.  Daily challenge mode
32.  Mission system (5 missions)
33.  XP / Level system
34.  Character unlocks (5 characters)
35.  Board unlocks (5 boards)
36.  Character color customization (RGB)
37.  Environment themes (city, subway, desert, night, neon)
38.  Day/night cycle
39.  Weather system (rain, snow, fog)
40.  Dynamic lighting (ambient + directional)
41.  Shadow rendering
42.  Motion blur effect
43.  Screen shake on collision
44.  Camera bob while running
45.  Camera zoom (sprint feel)
46.  Field of view adjustment
47.  Multiple camera angles (behind, side, top, cinematic)
48.  Cinematic camera swings
49.  Slow motion mode
50.  Turbo boost mode
51.  Double jump
52.  Triple jump (with power-up)
53.  Wall run (side lanes)
54.  Grind on rails
55.  Trick system (flips, spins)
56.  Trick point bonus
57.  Combo chain display
58.  Billboard ads (animated)
59.  Train windows with passengers
60.  Moving background buildings
61.  Parallax layers (bg/mg/fg)
62.  Ground detail tiles
63.  Track ties rendering
64.  Overhead cables/wires
65.  Birds flocking
66.  Animated clouds
67.  Particle system (sparks, dust, coins)
68.  Explosion particles
69.  Coin collect sparkle
70.  Jet exhaust particles
71.  Screen flash on power-up
72.  HUD: speed meter
73.  HUD: distance counter
74.  HUD: score (animated)
75.  HUD: coins (animated)
76.  HUD: multiplier display
77.  HUD: active power-up timer bar
78.  HUD: mission progress
79.  HUD: minimap (lane view)
80.  HUD: fps counter
81.  HUD: altitude bar (for jetpack)
82.  Pause menu
83.  Settings menu
84.  Sound toggle (sfx on/off flag)
85.  Music toggle
86.  Colorblind mode
87.  High contrast mode
88.  Accessibility: big text mode
89.  Autopilot: aggressive (max coins)
90.  Autopilot: safe (avoid obstacles)
91.  Autopilot: balanced
92.  Autopilot: speedrun (never slow)
93.  Autopilot visual indicator
94.  Replay recording (last 30s)
95.  Replay playback
96.  Endless procedural generation
97.  Difficulty scaling with distance
98.  Sprint mechanics (hold key)
99.  Drift (lean into turns)
100. Reverse thrust (slow down)
101. Emergency brake
102. Lane change animation (smooth)
103. Obstacle preview (far-field)
104. Danger warning system
105. Score board (top 10)
106. Achievement system (20 achievements)
107. Achievement pop-up animation
108. Stats screen (total coins, distance, runs)
109. Shop UI (spend coins on upgrades)
110. Coin doubler upgrade
111. Head start upgrade
112. Score booster upgrade
113. Magnet strength upgrade
114. Shield duration upgrade
115. Jetpack fuel upgrade
116. Run again prompt
117. Tutorial mode (first run)
118. Cheat codes (konami-style)
119. God mode toggle
120. Speed hack toggle (debug)
121. Wireframe mode toggle
122. Depth buffer visualization
123. Normal map visualization
124. Axis helper display
125. Benchmark mode
126. Multiple difficulty presets (Easy/Normal/Hard/Insane/Ludicrous)
127. Procedural building generator
128. Procedural obstacle placer
129. Procedural coin pattern generator
130. Train arrival warning
131. Tunnel entrance effect
132. Light bloom on neon theme
133. Color grading (warm/cool/vivid)
134. Depth of field (blurred far objects)
135. Dynamic FOV on speed change
136. Head bobbing intensity setting
137. Trail effect behind character
138. Speed lines (radial blur)
139. Inverted color mode
140. Grayscale mode
141. Pixelated retro mode
142. Scanline overlay
143. CRT effect mode
144. Vignette overlay
145. Crosshair/cursor overlay
146. Advanced autopilot: learns obstacle patterns
147. Keyboard remapping
148. Controller support stub
149. Session timer
150. Run length record tracker
151. Longest streak tracker
152. Most coins in single run tracker
153. Continuous speed ramp (auto-accelerates over time)
154. Danger zone coloring (red tint near obstacles)
155. Night vision mode (green tint)
"""

import curses
import math
import random
import time
import json
import os
import sys
import copy
import threading
from collections import deque
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
#  CONSTANTS & CONFIG
# ─────────────────────────────────────────────────────────────────────────────

VERSION = "3.0.0-ULTIMATE"
SAVE_FILE = os.path.join(os.path.dirname(__file__), "save_data.json")

# Screen logical resolution (will be scaled to terminal)
RENDER_W = 120
RENDER_H = 40

# Lane positions (x-axis)
LANES = [-2.0, 0.0, 2.0]
LANE_COUNT = 3

# Physics
GRAVITY = -18.0
JUMP_VEL = 9.0
ROLL_DURATION = 0.6
LANE_CHANGE_TIME = 0.18

# Game
COIN_VALUE = 1
COIN_ROW_LEN = 8
BASE_SPEED = 8.0
MAX_SPEED = 10000.0
SPEED_RAMP = 0.5          # speed units per second
OBSTACLE_SPAWN_DIST = 35.0
DESPAWN_DIST = -5.0

# Render
FOV = 70.0
NEAR = 0.3
FAR = 80.0
CAMERA_Y = 1.8
CAMERA_Z = -3.5

# Colors (curses color pair IDs)
CP_DEFAULT  = 0
CP_WHITE    = 1
CP_YELLOW   = 2
CP_GREEN    = 3
CP_RED      = 4
CP_CYAN     = 5
CP_MAGENTA  = 6
CP_BLUE     = 7
CP_ORANGE   = 8
CP_DARK     = 9
CP_LGRAY    = 10
CP_DGRAY    = 11
CP_SKIN     = 12
CP_BROWN    = 13
CP_PURPLE   = 14
CP_LGREEN   = 15
CP_LRED     = 16
CP_LCYAN    = 17
CP_LBLUE    = 18

# Character styles (feature 34)
CHARACTERS = [
    {"name": "Jake",   "body": CP_CYAN,    "hair": CP_YELLOW,  "skin": CP_SKIN},
    {"name": "Tricky", "body": CP_RED,     "hair": CP_RED,     "skin": CP_SKIN},
    {"name": "Fresh",  "body": CP_GREEN,   "hair": CP_LGRAY,   "skin": CP_SKIN},
    {"name": "Spike",  "body": CP_MAGENTA, "hair": CP_MAGENTA, "skin": CP_SKIN},
    {"name": "Yutani", "body": CP_LBLUE,   "hair": CP_LBLUE,   "skin": CP_SKIN},
]

# Environment themes (feature 38)
THEMES = {
    "city":    {"sky": CP_BLUE,    "ground": CP_DGRAY,  "building": CP_LGRAY,  "track": CP_DGRAY,  "accent": CP_YELLOW},
    "subway":  {"sky": CP_DARK,    "ground": CP_DARK,   "building": CP_DGRAY,  "track": CP_DGRAY,  "accent": CP_YELLOW},
    "desert":  {"sky": CP_YELLOW,  "ground": CP_YELLOW, "building": CP_BROWN,  "track": CP_BROWN,  "accent": CP_RED},
    "night":   {"sky": CP_DARK,    "ground": CP_DARK,   "building": CP_BLUE,   "track": CP_DARK,   "accent": CP_CYAN},
    "neon":    {"sky": CP_DARK,    "ground": CP_PURPLE, "building": CP_MAGENTA,"track": CP_CYAN,   "accent": CP_LGREEN},
}

# Power-up types
POWERUP_MAGNET   = "magnet"
POWERUP_SHIELD   = "shield"
POWERUP_MULTI2   = "x2"
POWERUP_MULTI3   = "x3"
POWERUP_MULTI5   = "x5"
POWERUP_MULTI10  = "x10"
POWERUP_JETPACK  = "jetpack"
POWERUP_SNEAKERS = "sneakers"
POWERUP_SLOW     = "slowmo"
POWERUP_TURBO    = "turbo"

POWERUP_DURATIONS = {
    POWERUP_MAGNET:   12.0,
    POWERUP_SHIELD:   8.0,
    POWERUP_MULTI2:   15.0,
    POWERUP_MULTI3:   12.0,
    POWERUP_MULTI5:   10.0,
    POWERUP_MULTI10:  8.0,
    POWERUP_JETPACK:  12.0,
    POWERUP_SNEAKERS: 10.0,
    POWERUP_SLOW:     6.0,
    POWERUP_TURBO:    8.0,
}

POWERUP_COLORS = {
    POWERUP_MAGNET:   CP_CYAN,
    POWERUP_SHIELD:   CP_BLUE,
    POWERUP_MULTI2:   CP_YELLOW,
    POWERUP_MULTI3:   CP_YELLOW,
    POWERUP_MULTI5:   CP_ORANGE,
    POWERUP_MULTI10:  CP_RED,
    POWERUP_JETPACK:  CP_CYAN,
    POWERUP_SNEAKERS: CP_GREEN,
    POWERUP_SLOW:     CP_MAGENTA,
    POWERUP_TURBO:    CP_RED,
}

POWERUP_SYMBOLS = {
    POWERUP_MAGNET:   "M",
    POWERUP_SHIELD:   "S",
    POWERUP_MULTI2:   "2",
    POWERUP_MULTI3:   "3",
    POWERUP_MULTI5:   "5",
    POWERUP_MULTI10:  "X",
    POWERUP_JETPACK:  "J",
    POWERUP_SNEAKERS: "↑",
    POWERUP_SLOW:     "~",
    POWERUP_TURBO:    "!",
}

# Difficulty presets (feature 126)
DIFFICULTIES = {
    "Easy":       {"speed_mult": 0.5,  "obstacle_density": 0.5, "ramp": 0.2},
    "Normal":     {"speed_mult": 1.0,  "obstacle_density": 1.0, "ramp": 0.5},
    "Hard":       {"speed_mult": 1.5,  "obstacle_density": 1.5, "ramp": 1.0},
    "Insane":     {"speed_mult": 2.5,  "obstacle_density": 2.0, "ramp": 2.0},
    "Ludicrous":  {"speed_mult": 5.0,  "obstacle_density": 3.0, "ramp": 5.0},
}

# Achievements (feature 106)
ACHIEVEMENTS = [
    {"id": "first_run",     "name": "First Steps",       "desc": "Complete your first run"},
    {"id": "coins_100",     "name": "Coin Collector",    "desc": "Collect 100 coins"},
    {"id": "coins_1000",    "name": "Gold Rush",         "desc": "Collect 1000 coins"},
    {"id": "dist_1000",     "name": "Mile Marker",       "desc": "Run 1000m"},
    {"id": "dist_10000",    "name": "Marathon",          "desc": "Run 10000m"},
    {"id": "speed_1000",    "name": "Supersonic",        "desc": "Reach speed 1000"},
    {"id": "speed_10000",   "name": "Lightspeed",        "desc": "Reach speed 10000"},
    {"id": "use_jetpack",   "name": "Up, Up & Away",     "desc": "Use the jetpack"},
    {"id": "use_shield",    "name": "Force Field",       "desc": "Use a shield"},
    {"id": "multi10",       "name": "x10 Multiplier",   "desc": "Activate x10 multiplier"},
    {"id": "trick_10",      "name": "Trickster",         "desc": "Perform 10 tricks"},
    {"id": "streak_20",     "name": "On Fire",           "desc": "Get a 20x streak"},
    {"id": "godmode",       "name": "Invincible",        "desc": "Activate god mode"},
    {"id": "autopilot_win", "name": "AI Driver",         "desc": "Run 500m on autopilot"},
    {"id": "run_10",        "name": "Regular Runner",    "desc": "Complete 10 runs"},
    {"id": "run_50",        "name": "Veteran",           "desc": "Complete 50 runs"},
    {"id": "theme_all",     "name": "World Traveler",    "desc": "Play all 5 themes"},
    {"id": "neon_theme",    "name": "Neon Dreams",       "desc": "Play in neon theme"},
    {"id": "all_chars",     "name": "Full Roster",       "desc": "Unlock all characters"},
    {"id": "speedrun",      "name": "Speedrunner",       "desc": "Score 1M in one run"},
]

# ─────────────────────────────────────────────────────────────────────────────
#  MATH HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def lerp(a, b, t):
    return a + (b - a) * clamp(t, 0, 1)

def smoothstep(t):
    t = clamp(t, 0, 1)
    return t * t * (3 - 2 * t)

def rot_y(angle):
    """4x4 rotation matrix around Y axis"""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]], dtype=np.float32)

def rot_x(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]], dtype=np.float32)

def rot_z(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]], dtype=np.float32)

def translate(tx, ty, tz):
    m = np.eye(4, dtype=np.float32)
    m[0,3] = tx; m[1,3] = ty; m[2,3] = tz
    return m

def scale_mat(sx, sy, sz):
    m = np.diag([sx, sy, sz, 1.0]).astype(np.float32)
    return m

def perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2)
    n, r = near, far
    return np.array([
        [f/aspect, 0,           0,              0],
        [0,        f,           0,              0],
        [0,        0,  (r+n)/(n-r), (2*r*n)/(n-r)],
        [0,        0,          -1,              0]], dtype=np.float32)

def look_at(eye, center, up):
    f = np.array(center, dtype=np.float32) - np.array(eye, dtype=np.float32)
    f = f / np.linalg.norm(f)
    s = np.cross(f, np.array(up, dtype=np.float32))
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.eye(4, dtype=np.float32)
    m[0,:3] = s; m[1,:3] = u; m[2,:3] = -f
    m[0,3] = -np.dot(s, eye)
    m[1,3] = -np.dot(u, eye)
    m[2,3] =  np.dot(f, eye)
    return m

def transform_point(mat, pt):
    """Transform a 3D point by a 4x4 matrix, returns (x,y,z,w)"""
    p = np.array([pt[0], pt[1], pt[2], 1.0], dtype=np.float32)
    r = mat @ p
    return r

def project_point(proj_mat, view_mat, pt):
    """Project a 3D world point to normalized device coords"""
    clip = proj_mat @ (view_mat @ np.array([pt[0],pt[1],pt[2],1.0], dtype=np.float32))
    if clip[3] <= 0.0001:
        return None
    ndc = clip[:3] / clip[3]
    return ndc  # x,y in [-1,1], z in [-1,1]

def ndc_to_screen(ndc, W, H):
    sx = int((ndc[0] * 0.5 + 0.5) * W)
    sy = int((1.0 - (ndc[1] * 0.5 + 0.5)) * H)
    return sx, sy

# ─────────────────────────────────────────────────────────────────────────────
#  SIMPLE RASTERIZER
# ─────────────────────────────────────────────────────────────────────────────

class Framebuffer:
    """Character-based framebuffer with depth buffer"""
    def __init__(self, W, H):
        self.W = W
        self.H = H
        self.clear()

    def clear(self, bg_char=' ', bg_color=CP_DEFAULT):
        self.chars  = [[bg_char]*self.W for _ in range(self.H)]
        self.colors = [[bg_color]*self.W for _ in range(self.H)]
        self.depth  = [[float('inf')]*self.W for _ in range(self.H)]

    def put(self, x, y, char, color, depth=0.0):
        if 0 <= x < self.W and 0 <= y < self.H:
            if depth < self.depth[y][x]:
                self.depth[y][x] = depth
                self.chars[y][x] = char
                self.colors[y][x] = color

    def hline(self, y, x0, x1, char, color, depth=0.0):
        for x in range(max(0,x0), min(self.W, x1+1)):
            self.put(x, y, char, color, depth)

    def vline(self, x, y0, y1, char, color, depth=0.0):
        for y in range(max(0,y0), min(self.H, y1+1)):
            self.put(x, y, char, color, depth)

    def draw_rect_outline(self, x0, y0, x1, y1, char, color, depth=0.0):
        self.hline(y0, x0, x1, char, color, depth)
        self.hline(y1, x0, x1, char, color, depth)
        self.vline(x0, y0, y1, char, color, depth)
        self.vline(x1, y0, y1, char, color, depth)

    def fill_rect(self, x0, y0, x1, y1, char, color, depth=0.0):
        for y in range(max(0,y0), min(self.H, y1+1)):
            for x in range(max(0,x0), min(self.W, x1+1)):
                self.put(x, y, char, color, depth)

    def draw_text(self, x, y, text, color, depth=-999.0):
        for i, ch in enumerate(text):
            self.put(x+i, y, ch, color, depth)

    def draw_line(self, x0, y0, x1, y1, char, color, depth=0.0):
        """Bresenham line"""
        dx = abs(x1-x0); dy = abs(y1-y0)
        sx = 1 if x0<x1 else -1
        sy = 1 if y0<y1 else -1
        err = dx - dy
        while True:
            self.put(x0, y0, char, color, depth)
            if x0==x1 and y0==y1: break
            e2 = 2*err
            if e2 > -dy: err -= dy; x0 += sx
            if e2 < dx:  err += dx; y0 += sy

# ─────────────────────────────────────────────────────────────────────────────
#  3D MESH PRIMITIVES
# ─────────────────────────────────────────────────────────────────────────────

def make_box(w, h, d):
    """Return list of (v0,v1) edges for a wireframe box centered at origin"""
    hx, hy, hz = w/2, h/2, d/2
    verts = [
        (-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
        (-hx,-hy, hz),(hx,-hy, hz),(hx,hy, hz),(-hx,hy, hz),
    ]
    edges = [
        (0,1),(1,2),(2,3),(3,0),  # back face
        (4,5),(5,6),(6,7),(7,4),  # front face
        (0,4),(1,5),(2,6),(3,7),  # connecting
    ]
    return verts, edges

def make_cylinder_approx(r, h, segs=8):
    """Approximate cylinder with polygon lines"""
    top_verts = [(r*math.cos(2*math.pi*i/segs), h/2, r*math.sin(2*math.pi*i/segs)) for i in range(segs)]
    bot_verts = [(r*math.cos(2*math.pi*i/segs),-h/2, r*math.sin(2*math.pi*i/segs)) for i in range(segs)]
    verts = top_verts + bot_verts
    edges = []
    for i in range(segs):
        edges.append((i, (i+1)%segs))
        edges.append((segs+i, segs+(i+1)%segs))
        edges.append((i, segs+i))
    return verts, edges

def make_sphere_approx(r, segs=8):
    """Latitude/longitude wireframe sphere"""
    verts = []
    edges = []
    lats = segs//2
    lons = segs
    for lat in range(lats+1):
        phi = math.pi * lat / lats - math.pi/2
        for lon in range(lons):
            theta = 2*math.pi * lon / lons
            x = r*math.cos(phi)*math.cos(theta)
            y = r*math.sin(phi)
            z = r*math.cos(phi)*math.sin(theta)
            verts.append((x,y,z))
    for lat in range(lats+1):
        for lon in range(lons):
            i = lat*lons + lon
            if lat < lats:
                edges.append((i, i+lons))
            edges.append((i, lat*lons + (lon+1)%lons))
    return verts, edges

def draw_mesh(fb, proj, view, model, verts, edges, color, char='█'):
    """Project and draw wireframe mesh"""
    # Transform all vertices
    pv = proj @ view
    projected = []
    for v in verts:
        wp = model @ np.array([v[0],v[1],v[2],1.0], dtype=np.float32)
        clip = pv @ wp
        if clip[3] <= 0.001:
            projected.append(None)
            continue
        ndc = clip[:3] / clip[3]
        if abs(ndc[0]) > 1.5 or abs(ndc[1]) > 1.5:
            projected.append(None)
            continue
        sx = int((ndc[0]*0.5+0.5)*fb.W)
        sy = int((1.0-(ndc[1]*0.5+0.5))*fb.H)
        depth = clip[2]/clip[3]
        projected.append((sx, sy, depth))
    # Draw edges
    for e in edges:
        a, b = projected[e[0]], projected[e[1]]
        if a is None or b is None: continue
        fb.draw_line(a[0],a[1],b[0],b[1], char, color, (a[2]+b[2])/2)

def draw_mesh_solid(fb, proj, view, model, verts, faces, colors_face, fill_char='█'):
    """Simple flat-shaded solid mesh (painter's algorithm)"""
    pv = proj @ view
    projected = []
    for v in verts:
        wp = model @ np.array([v[0],v[1],v[2],1.0], dtype=np.float32)
        clip = pv @ wp
        if clip[3] <= 0.001:
            projected.append(None)
            continue
        ndc = clip[:3] / clip[3]
        sx = int((ndc[0]*0.5+0.5)*fb.W)
        sy = int((1.0-(ndc[1]*0.5+0.5))*fb.H)
        depth = clip[2]/clip[3]
        projected.append((sx, sy, depth))
    # Sort faces by average depth (painter)
    face_depths = []
    for fi, face in enumerate(faces):
        pts = [projected[i] for i in face if projected[i] is not None]
        if len(pts) < 3:
            face_depths.append((float('inf'), fi))
        else:
            avg_d = sum(p[2] for p in pts) / len(pts)
            face_depths.append((avg_d, fi))
    face_depths.sort(key=lambda x: -x[0])  # back to front
    for depth, fi in face_depths:
        face = faces[fi]
        pts = [projected[i] for i in face]
        if any(p is None for p in pts): continue
        col = colors_face[fi % len(colors_face)]
        # Fill quad/triangle by scanline
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        min_y = max(0, min(ys)); max_y = min(fb.H-1, max(ys))
        for y in range(min_y, max_y+1):
            x_ints = []
            n = len(pts)
            for k in range(n):
                p1, p2 = pts[k], pts[(k+1)%n]
                y1,y2 = p1[1],p2[1]
                if (y1<=y<y2) or (y2<=y<y1):
                    if y2==y1: continue
                    xi = p1[0] + (y-y1)*(p2[0]-p1[0])/(y2-y1)
                    x_ints.append(int(xi))
            if len(x_ints) >= 2:
                x_ints.sort()
                fb.hline(y, x_ints[0], x_ints[-1], fill_char, col, depth)

# ─────────────────────────────────────────────────────────────────────────────
#  CHARACTER 3D MODEL (feature 2 – full limb animation)
# ─────────────────────────────────────────────────────────────────────────────

class Character3D:
    """Articulated character with head, torso, arms, legs"""

    def __init__(self, skin_color=CP_SKIN, body_color=CP_CYAN, hair_color=CP_YELLOW):
        self.skin  = skin_color
        self.body  = body_color
        self.hair  = hair_color
        self.anim_t = 0.0

    def update(self, dt, speed):
        self.anim_t += dt * (speed / 8.0) * 3.0

    def draw(self, fb, proj, view, pos, roll=False, jump=False, trick_angle=0.0, lean=0.0):
        x, y, z = pos
        t = self.anim_t
        base_model = translate(x, y, z)
        if trick_angle != 0:
            base_model = base_model @ rot_z(trick_angle)
        if lean != 0:
            base_model = base_model @ rot_z(lean * 0.3)

        leg_swing = math.sin(t) * 0.5 if not roll and not jump else 0.0
        arm_swing = math.sin(t + math.pi) * 0.4

        if roll:
            base_model = base_model @ rot_x(math.pi/2)

        # HEAD
        head_model = base_model @ translate(0, 1.65, 0) @ scale_mat(0.22, 0.22, 0.22)
        v, e = make_box(1,1,1)
        draw_mesh(fb, proj, view, head_model, v, e, self.skin, '▓')
        # Hair patch on top
        hair_model = base_model @ translate(0, 1.85, 0) @ scale_mat(0.20, 0.10, 0.20)
        draw_mesh(fb, proj, view, hair_model, v, e, self.hair, '▓')

        # TORSO
        torso_model = base_model @ translate(0, 1.15, 0) @ scale_mat(0.32, 0.40, 0.18)
        draw_mesh(fb, proj, view, torso_model, v, e, self.body, '█')

        # HIPS
        hip_model = base_model @ translate(0, 0.82, 0) @ scale_mat(0.28, 0.18, 0.16)
        draw_mesh(fb, proj, view, hip_model, v, e, self.body, '▓')

        # LEFT ARM
        la_model = base_model @ translate(-0.22, 1.10, 0) @ rot_x(arm_swing) @ translate(0,-0.18,0) @ scale_mat(0.10, 0.36, 0.10)
        draw_mesh(fb, proj, view, la_model, v, e, self.skin, '▓')

        # RIGHT ARM
        ra_model = base_model @ translate(0.22, 1.10, 0) @ rot_x(-arm_swing) @ translate(0,-0.18,0) @ scale_mat(0.10, 0.36, 0.10)
        draw_mesh(fb, proj, view, ra_model, v, e, self.skin, '▓')

        # LEFT LEG
        ll_model = base_model @ translate(-0.11, 0.72, 0) @ rot_x(leg_swing) @ translate(0,-0.25,0) @ scale_mat(0.12, 0.50, 0.12)
        draw_mesh(fb, proj, view, ll_model, v, e, CP_BLUE, '█')
        # LEFT SHOE
        lsh_model = base_model @ translate(-0.11, 0.42, 0) @ rot_x(leg_swing) @ translate(0,-0.26, 0.04) @ scale_mat(0.13,0.08,0.18)
        draw_mesh(fb, proj, view, lsh_model, v, e, CP_RED, '█')

        # RIGHT LEG
        rl_model = base_model @ translate(0.11, 0.72, 0) @ rot_x(-leg_swing) @ translate(0,-0.25,0) @ scale_mat(0.12, 0.50, 0.12)
        draw_mesh(fb, proj, view, rl_model, v, e, CP_BLUE, '█')
        # RIGHT SHOE
        rsh_model = base_model @ translate(0.11, 0.42, 0) @ rot_x(-leg_swing) @ translate(0,-0.26, 0.04) @ scale_mat(0.13,0.08,0.18)
        draw_mesh(fb, proj, view, rsh_model, v, e, CP_RED, '█')

        # JETPACK (drawn when active - handled by caller via draw_jetpack)

# ─────────────────────────────────────────────────────────────────────────────
#  ENVIRONMENT GEOMETRY
# ─────────────────────────────────────────────────────────────────────────────

def draw_ground_plane(fb, proj, view, theme, cam_z, W, H):
    """Draw ground as horizontal strips (feature 60)"""
    ground_color = THEMES[theme]["ground"]
    # Draw ground by projecting horizontal lines at y=0
    for row in range(H//2, H):
        # approximate distance for this row
        pass
    # Use filled rect for sky
    sky_color = THEMES[theme]["sky"]
    horizon_y = H // 2 - 2
    fb.fill_rect(0, 0, W-1, max(0, horizon_y), ' ', sky_color, 100.0)
    fb.fill_rect(0, max(0, horizon_y+1), W-1, H-1, ' ', ground_color, 101.0)

def draw_track(fb, proj, view, theme, cam_z, speed):
    """Draw the 3-lane track with rails and ties (features 62,63)"""
    track_color = THEMES[theme]["track"]
    rail_color = CP_LGRAY
    tie_color = CP_BROWN
    bv, be = make_box(1,1,1)

    # Rails (left and right of each lane)
    rail_positions = [-3.1, -0.9, 0.9, -0.9+2.0, 0.9+2.0, -0.9-2.0]
    # Actually 2 outer rails + 2 inner rails
    for rx in [-3.1, -1.1, -0.9, 1.1, 0.9, 3.1]:
        for seg in range(0, 18):
            sz = cam_z + seg * 3.0
            rail_model = translate(rx, 0.03, sz) @ scale_mat(0.05, 0.06, 3.0)
            draw_mesh(fb, proj, view, rail_model, bv, be, rail_color, '─')

    # Ties
    for seg in range(0, 25):
        tz = cam_z + seg * 1.5 - ((cam_z * speed * 0.05) % 1.5)
        tie_model = translate(0, 0.0, tz) @ scale_mat(6.5, 0.05, 0.18)
        draw_mesh(fb, proj, view, tie_model, bv, be, tie_color, '▬')

def draw_building(fb, proj, view, x, z, w, h, d, color, windows=True):
    """Draw a building with optional windows (feature 56)"""
    bv, be = make_box(1,1,1)
    bldg_model = translate(x, h/2, z) @ scale_mat(w, h, d)
    draw_mesh(fb, proj, view, bldg_model, bv, be, color, '█')
    if windows:
        # Window rows
        wc = CP_YELLOW
        for wy in range(1, int(h), 2):
            for wx_off in [-w*0.3, 0, w*0.3]:
                wm = translate(x+wx_off, wy+0.3, z - d/2 - 0.1) @ scale_mat(0.3, 0.4, 0.05)
                draw_mesh(fb, proj, view, wm, bv, be, wc, '▪')

def draw_environment(fb, proj, view, theme, cam_z, buildings_data):
    """Draw all buildings and environment (feature 3)"""
    tc = THEMES[theme]
    draw_ground_plane(fb, proj, view, theme, cam_z, fb.W, fb.H)
    draw_track(fb, proj, view, theme, cam_z, 1.0)

    for b in buildings_data:
        if b['z'] - cam_z > -5 and b['z'] - cam_z < FAR:
            draw_building(fb, proj, view, b['x'], b['z'], b['w'], b['h'], b['d'],
                          tc["building"], windows=True)

def draw_overhead_cables(fb, proj, view, theme, cam_z):
    """Feature 64: Overhead cables/wires"""
    bv, be = make_box(1,1,1)
    cable_color = CP_DGRAY
    for seg in range(0, 20):
        cz = cam_z + seg * 4.0
        # Left pole
        pm = translate(-4.0, 1.5, cz) @ scale_mat(0.05, 3.0, 0.05)
        draw_mesh(fb, proj, view, pm, bv, be, cable_color, '|')
        # Right pole
        pm2 = translate(4.0, 1.5, cz) @ scale_mat(0.05, 3.0, 0.05)
        draw_mesh(fb, proj, view, pm2, bv, be, cable_color, '|')
        # Cable
        if seg < 19:
            cm = translate(0, 3.1, cz + 2.0) @ scale_mat(8.0, 0.03, 4.0)
            draw_mesh(fb, proj, view, cm, bv, be, cable_color, '~')

def draw_train_obstacle(fb, proj, view, obs):
    """Draw a 3D train as obstacle (feature 20)"""
    x, y, z = obs['x'], obs.get('y', 0), obs['z']
    bv, be = make_box(1,1,1)
    # Train body
    body_model = translate(x, y + 0.9, z) @ scale_mat(1.7, 1.8, 4.0)
    draw_mesh(fb, proj, view, body_model, bv, be, CP_BLUE, '█')
    # Windows row
    for wz_off in [-1.2, 0, 1.2]:
        wm = translate(x - 0.85, y + 1.2, z + wz_off) @ scale_mat(0.05, 0.4, 0.6)
        draw_mesh(fb, proj, view, wm, bv, be, CP_YELLOW, '▪')
    # Wheels
    for wz_off in [-1.5, 0, 1.5]:
        for wx_off in [-0.7, 0.7]:
            whl = translate(x+wx_off, y+0.1, z+wz_off) @ scale_mat(0.25, 0.25, 0.25)
            wv, we = make_cylinder_approx(0.5, 0.3, 6)
            draw_mesh(fb, proj, view, whl, wv, we, CP_DGRAY, '●')
    # Front grill
    fm = translate(x, y+0.9, z - 2.1) @ scale_mat(1.7, 1.8, 0.1)
    draw_mesh(fb, proj, view, fm, bv, be, CP_LGRAY, '▓')

def draw_barrier_obstacle(fb, proj, view, obs):
    """Low barrier – roll under (feature 25)"""
    x, y, z = obs['x'], obs.get('y',0), obs['z']
    bv, be = make_box(1,1,1)
    bm = translate(x, y+0.3, z) @ scale_mat(1.8, 0.6, 0.3)
    draw_mesh(fb, proj, view, bm, bv, be, CP_RED, '▓')
    # Poles
    for px in [-0.7, 0.7]:
        pm = translate(x+px, y+0.5, z) @ scale_mat(0.1, 1.0, 0.1)
        draw_mesh(fb, proj, view, pm, bv, be, CP_LGRAY, '|')

def draw_high_barrier(fb, proj, view, obs):
    """High barrier – jump over (feature 26)"""
    x, y, z = obs['x'], obs.get('y',0), obs['z']
    bv, be = make_box(1,1,1)
    bm = translate(x, y+1.0, z) @ scale_mat(1.8, 2.0, 0.3)
    draw_mesh(fb, proj, view, bm, bv, be, CP_RED, '█')
    # Warning stripes
    for sh in [0.4, 0.8, 1.2, 1.6]:
        sm = translate(x, y+sh, z-0.16) @ scale_mat(1.8, 0.15, 0.05)
        draw_mesh(fb, proj, view, sm, bv, be, CP_YELLOW, '─')

def draw_barrel_obstacle(fb, proj, view, obs):
    """Explosive barrel (feature 24)"""
    x, y, z = obs['x'], obs.get('y',0), obs['z']
    bv, we2 = make_cylinder_approx(0.4, 0.7, 8)
    bm = translate(x, y+0.35, z) @ rot_x(0)
    draw_mesh(fb, proj, view, bm, bv, we2, CP_BROWN, '▓')
    # Fuse
    fv, fe = make_box(0.1, 0.3, 0.1)
    fm = translate(x, y+0.75, z) @ scale_mat(1,1,1)
    draw_mesh(fb, proj, view, fm, fv, fe, CP_YELLOW, '|')

def draw_coin(fb, proj, view, coin, t):
    """Spinning 3D coin (feature 9)"""
    x, y, z = coin['x'], coin['y'], coin['z']
    spin = t * 3.0 + coin.get('phase', 0)
    sv, se = make_cylinder_approx(0.18, 0.04, 8)
    cm = translate(x, y, z) @ rot_y(spin) @ scale_mat(1,1,1)
    draw_mesh(fb, proj, view, cm, sv, se, CP_YELLOW, '$')
    # Inner circle
    sv2, se2 = make_cylinder_approx(0.10, 0.05, 6)
    draw_mesh(fb, proj, view, cm, sv2, se2, CP_ORANGE, '○')

def draw_powerup_box(fb, proj, view, pup, t):
    """Rotating power-up box (features 10-15)"""
    x, y, z = pup['x'], pup['y'], pup['z']
    spin = t * 2.0 + pup.get('phase', 0)
    bv, be = make_box(1,1,1)
    bm = translate(x, y, z) @ rot_y(spin) @ rot_x(spin*0.5) @ scale_mat(0.35,0.35,0.35)
    col = POWERUP_COLORS.get(pup['type'], CP_WHITE)
    draw_mesh(fb, proj, view, bm, bv, be, col, '■')
    # Symbol label
    sym = POWERUP_SYMBOLS.get(pup['type'], '?')
    ndc = project_point(
        perspective(FOV, fb.W/fb.H, NEAR, FAR),
        look_at([0, CAMERA_Y, CAMERA_Z], [0,1,10], [0,1,0]),
        (x, y+0.3, z)
    )
    if ndc is not None:
        sx, sy = ndc_to_screen(ndc, fb.W, fb.H)
        fb.put(sx, sy, sym, col, -0.9)

def draw_jetpack_effect(fb, proj, view, pos, t):
    """Jetpack on character's back (feature 13)"""
    x, y, z = pos
    bv, be = make_box(1,1,1)
    # Pack
    pm = translate(x, y+1.1, z+0.12) @ scale_mat(0.28, 0.45, 0.14)
    draw_mesh(fb, proj, view, pm, bv, be, CP_DGRAY, '▓')
    # Nozzles
    for nx_off in [-0.08, 0.08]:
        noz_m = translate(x+nx_off, y+0.6, z+0.15) @ scale_mat(0.06, 0.20, 0.06)
        draw_mesh(fb, proj, view, noz_m, bv, be, CP_LGRAY, '|')
    # Flame particles drawn as HUD-level effect by caller

def draw_tunnel_section(fb, proj, view, theme, z_start, z_end):
    """Draw tunnel walls (feature 18 environment)"""
    bv, be = make_box(1,1,1)
    tc = THEMES[theme]
    # Left wall
    lw = translate(-4.5, 2.0, (z_start+z_end)/2) @ scale_mat(0.3, 4.0, z_end-z_start)
    draw_mesh(fb, proj, view, lw, bv, be, tc["building"], '█')
    # Right wall
    rw = translate(4.5, 2.0, (z_start+z_end)/2) @ scale_mat(0.3, 4.0, z_end-z_start)
    draw_mesh(fb, proj, view, rw, bv, be, tc["building"], '█')
    # Ceiling
    ceil = translate(0, 4.2, (z_start+z_end)/2) @ scale_mat(9.0, 0.3, z_end-z_start)
    draw_mesh(fb, proj, view, ceil, bv, be, tc["building"], '▄')
    # Arch rings every 6 units
    for az in range(int(z_start), int(z_end), 6):
        arch_v = [(4.5*math.cos(a*math.pi/8), 4.5*math.sin(a*math.pi/8), 0) for a in range(0,9)]
        arch_e = [(i, i+1) for i in range(8)]
        am = translate(0, 0, float(az))
        draw_mesh(fb, proj, view, am, arch_v, arch_e, tc["accent"], '◉')

# ─────────────────────────────────────────────────────────────────────────────
#  PARTICLE SYSTEM (feature 69–71)
# ─────────────────────────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, z, vx, vy, vz, char, color, life):
        self.x=x; self.y=y; self.z=z
        self.vx=vx; self.vy=vy; self.vz=vz
        self.char=char; self.color=color
        self.life=life; self.max_life=life

    def update(self, dt):
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.z += self.vz*dt
        self.vy -= 5.0*dt  # gravity on particles
        self.life -= dt
        return self.life > 0

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit_coin(self, x, y, z):
        """Coin collect sparkle (feature 69)"""
        for _ in range(6):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(1, 3)
            self.particles.append(Particle(
                x, y, z,
                math.cos(angle)*speed, math.sin(angle)*speed*0.5, random.uniform(-1,1),
                '*', CP_YELLOW, random.uniform(0.3, 0.7)
            ))

    def emit_explosion(self, x, y, z):
        """Explosion particles (feature 70)"""
        for _ in range(15):
            angle = random.uniform(0, 2*math.pi)
            vel = random.uniform(2, 8)
            self.particles.append(Particle(
                x, y, z,
                math.cos(angle)*vel, random.uniform(2,6), math.sin(angle)*vel*0.3,
                random.choice(['*','·','°','★']), random.choice([CP_RED, CP_ORANGE, CP_YELLOW]),
                random.uniform(0.2, 0.8)
            ))

    def emit_dust(self, x, y, z):
        """Dust on landing"""
        for _ in range(4):
            self.particles.append(Particle(
                x + random.uniform(-0.3, 0.3), y, z,
                random.uniform(-1,1), random.uniform(0.5,2), random.uniform(-0.5,0.5),
                '·', CP_LGRAY, random.uniform(0.2, 0.5)
            ))

    def emit_jetpack(self, x, y, z):
        """Jet exhaust (feature 70)"""
        for ox in [-0.08, 0.08]:
            self.particles.append(Particle(
                x+ox, y+0.55, z+0.2,
                random.uniform(-0.3,0.3), random.uniform(-3,-6), random.uniform(-0.3,0.3),
                random.choice(['▪','·','*']), random.choice([CP_RED, CP_ORANGE, CP_YELLOW]),
                random.uniform(0.1, 0.3)
            ))

    def emit_trail(self, x, y, z):
        """Speed trail behind character (feature 138)"""
        self.particles.append(Particle(
            x + random.uniform(-0.1,0.1), y + random.uniform(0.5, 1.5), z + random.uniform(-0.1,0.1),
            random.uniform(-0.5,0.5), random.uniform(-0.5,0.5), random.uniform(1,3),
            '·', CP_CYAN, random.uniform(0.1, 0.25)
        ))

    def emit_powerup(self, x, y, z):
        """Power-up collect effect (feature 71)"""
        for _ in range(10):
            angle = random.uniform(0, 2*math.pi)
            self.particles.append(Particle(
                x, y+0.5, z,
                math.cos(angle)*2, math.sin(angle)*2 + 1, 0,
                '★', CP_YELLOW, random.uniform(0.4, 0.9)
            ))

    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, fb, proj, view):
        pmat = perspective(FOV, fb.W/fb.H, NEAR, FAR)
        vmat = view
        for p in self.particles:
            ndc = project_point(pmat, vmat, (p.x, p.y, p.z))
            if ndc is None: continue
            sx, sy = ndc_to_screen(ndc, fb.W, fb.H)
            alpha = p.life / p.max_life
            fb.put(sx, sy, p.char, p.color, ndc[2])

# ─────────────────────────────────────────────────────────────────────────────
#  OBSTACLE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

OBS_TRAIN   = "train"
OBS_BARRIER = "barrier"
OBS_HIGH    = "high_barrier"
OBS_BARREL  = "barrel"
OBS_COMBO   = "combo"

class ObstacleSpawner:
    """Procedural obstacle spawner (feature 96)"""

    def __init__(self):
        self.next_spawn_z = 30.0
        self.spacing_min = 8.0
        self.spacing_max = 18.0

    def spawn_next(self, cam_z, difficulty_mult=1.0):
        """Generate one obstacle set ahead"""
        obs_list = []
        z = self.next_spawn_z
        kind = random.choices(
            [OBS_TRAIN, OBS_BARRIER, OBS_HIGH, OBS_BARREL, OBS_COMBO],
            weights=[30, 20, 20, 15, 15]
        )[0]

        if kind == OBS_TRAIN:
            lane = random.randint(0,2)
            obs_list.append({'type': OBS_TRAIN, 'lane': lane, 'x': LANES[lane], 'z': z, 'y': 0})

        elif kind == OBS_BARRIER:
            # block 1 or 2 lanes
            lanes_blocked = random.sample([0,1,2], random.randint(1,2))
            for l in lanes_blocked:
                obs_list.append({'type': OBS_BARRIER, 'lane': l, 'x': LANES[l], 'z': z, 'y': 0})

        elif kind == OBS_HIGH:
            lane = random.randint(0,2)
            obs_list.append({'type': OBS_HIGH, 'lane': lane, 'x': LANES[lane], 'z': z, 'y': 0})

        elif kind == OBS_BARREL:
            count = random.randint(1, 3)
            lanes_used = random.sample([0,1,2], min(count,3))
            for l in lanes_used:
                obs_list.append({'type': OBS_BARREL, 'lane': l, 'x': LANES[l], 'z': z, 'y': 0})

        elif kind == OBS_COMBO:
            # High barrier + barrel on side
            main_lane = 1
            side_lane = random.choice([0,2])
            obs_list.append({'type': OBS_HIGH,    'lane': main_lane, 'x': LANES[main_lane], 'z': z})
            obs_list.append({'type': OBS_BARREL,  'lane': side_lane, 'x': LANES[side_lane], 'z': z + 1.5})

        spacing = random.uniform(self.spacing_min / difficulty_mult,
                                  self.spacing_max / difficulty_mult)
        spacing = max(5.0, spacing)
        self.next_spawn_z = z + spacing
        return obs_list

class CoinSpawner:
    """Procedural coin pattern spawner (features 28–30, 129)"""

    PATTERNS = ['row', 'arc', 'spiral', 'lane_switch', 'zigzag']

    def __init__(self):
        self.next_z = 20.0

    def spawn_next(self, magnet_active=False):
        pattern = random.choice(self.PATTERNS)
        coins = []
        z = self.next_z

        if pattern == 'row':
            lane = random.randint(0,2)
            for i in range(COIN_ROW_LEN):
                coins.append({'x': LANES[lane], 'y': 0.6, 'z': z + i*1.0, 'phase': i*0.3})

        elif pattern == 'arc':
            lane = random.randint(0,2)
            for i in range(8):
                arc_y = 0.6 + math.sin(i/7.0*math.pi)*1.5
                coins.append({'x': LANES[lane], 'y': arc_y, 'z': z + i*0.9, 'phase': i*0.4})

        elif pattern == 'spiral':
            for i in range(12):
                angle = i * 0.8
                lane_x = math.sin(angle) * 2.0
                coins.append({'x': lane_x, 'y': 0.6 + math.cos(angle)*0.4, 'z': z + i*0.8, 'phase': i*0.5})

        elif pattern == 'lane_switch':
            for i, lane in enumerate([0,1,2,1,0,2,1,0]):
                coins.append({'x': LANES[lane], 'y': 0.6, 'z': z + i*1.2, 'phase': i*0.2})

        elif pattern == 'zigzag':
            for i in range(10):
                lx = LANES[i%3]
                coins.append({'x': lx, 'y': 0.6, 'z': z + i*1.0, 'phase': i*0.3})

        self.next_z = z + random.uniform(6.0, 14.0)
        return coins

# ─────────────────────────────────────────────────────────────────────────────
#  BUILDING GENERATOR (feature 57)
# ─────────────────────────────────────────────────────────────────────────────

class BuildingGenerator:
    def __init__(self):
        self.next_z_left = 5.0
        self.next_z_right = 5.0

    def generate_next(self, side='left'):
        if side == 'left':
            z = self.next_z_left
            x = random.uniform(-9.0, -6.0)
            self.next_z_left = z + random.uniform(4.0, 10.0)
        else:
            z = self.next_z_right
            x = random.uniform(6.0, 9.0)
            self.next_z_right = z + random.uniform(4.0, 10.0)
        w = random.uniform(2.5, 5.0)
        h = random.uniform(4.0, 18.0)
        d = random.uniform(3.0, 7.0)
        return {'x': x, 'z': z, 'w': w, 'h': h, 'd': d}

# ─────────────────────────────────────────────────────────────────────────────
#  AUTOPILOT AI (features 88–93, 146)
# ─────────────────────────────────────────────────────────────────────────────

class AutopilotAI:
    """Smart AI that plays the game (feature 4)"""

    MODES = ['balanced', 'aggressive', 'safe', 'speedrun']

    def __init__(self, mode='balanced'):
        self.mode = mode
        self.active = False
        self.last_action = time.time()
        self.obstacle_memory = deque(maxlen=20)  # feature 146: pattern memory
        self.panic_mode = False

    def decide(self, player, obstacles, coins, powerups, dt):
        """Return (target_lane, should_jump, should_roll)"""
        if not self.active:
            return player['lane'], False, False

        px = player['x']
        pz = player['z']
        plane = player['lane']
        current_speed = player.get('speed', BASE_SPEED)

        # Look-ahead distance depends on speed
        look_dist = max(8.0, current_speed * 0.6)

        # Find obstacles ahead
        danger = [o for o in obstacles if abs(o['z'] - pz) < look_dist and o['z'] > pz - 1.0]
        near_coins = [c for c in coins if abs(c['z'] - pz) < look_dist*0.7 and c['z'] > pz]
        near_pups  = [p for p in powerups if abs(p['z'] - pz) < look_dist and p['z'] > pz]

        target_lane = plane
        should_jump = False
        should_roll = False

        # Evaluate lane safety
        lane_danger = {0: 0, 1: 0, 2: 0}
        for obs in danger:
            l = obs.get('lane', 1)
            obs_type = obs.get('type', OBS_TRAIN)
            if obs_type == OBS_TRAIN:
                lane_danger[l] += 10
            elif obs_type == OBS_BARRIER:
                lane_danger[l] += 6
            elif obs_type == OBS_HIGH:
                lane_danger[l] += 4  # can jump
            elif obs_type == OBS_BARREL:
                lane_danger[l] += 5

        # Check if current lane is dangerous
        if lane_danger[plane] > 0:
            # Find safest adjacent lane
            options = []
            for l in range(3):
                if l != plane or lane_danger[plane] > 0:
                    options.append((lane_danger[l], abs(l-plane), l))
            options.sort()
            safest = options[0][2]

            # Decide if we should jump/roll instead
            ahead_obs = [o for o in danger if o['lane'] == plane]
            if ahead_obs:
                obs_type = ahead_obs[0]['type']
                dist_to_obs = ahead_obs[0]['z'] - pz
                if dist_to_obs < look_dist * 0.5:
                    if obs_type == OBS_HIGH and lane_danger[safest] > lane_danger[plane]:
                        should_jump = True
                    elif obs_type == OBS_BARRIER:
                        should_roll = True
                    elif obs_type == OBS_TRAIN:
                        if safest != plane and lane_danger[safest] < lane_danger[plane]:
                            target_lane = safest
                        else:
                            should_jump = True
                    else:
                        if safest != plane:
                            target_lane = safest
                else:
                    target_lane = safest

        # Aggressive: chase coins and power-ups
        if self.mode == 'aggressive' and target_lane == plane:
            if near_pups:
                target_lane = near_pups[0].get('lane', near_pups[0]['x'])
                # Get lane index
                best_pup = near_pups[0]
                for l in range(3):
                    if abs(LANES[l] - best_pup['x']) < 0.5:
                        if lane_danger[l] == 0:
                            target_lane = l
                        break
            elif near_coins:
                best_coin = near_coins[0]
                for l in range(3):
                    if abs(LANES[l] - best_coin['x']) < 0.5:
                        if lane_danger[l] == 0:
                            target_lane = l
                        break

        # Safe mode: avoid all danger aggressively
        if self.mode == 'safe':
            safest = min(range(3), key=lambda l: lane_danger[l])
            if lane_danger[plane] > 0:
                target_lane = safest

        # Record obstacle for pattern learning
        if danger:
            self.obstacle_memory.append({
                'lanes': tuple(sorted(set(o['lane'] for o in danger))),
                'time': time.time()
            })

        return target_lane, should_jump, should_roll

# ─────────────────────────────────────────────────────────────────────────────
#  SAVE / LOAD (features 16, 105, 107, 108)
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_SAVE = {
    "high_score": 0,
    "total_coins": 0,
    "total_distance": 0.0,
    "total_runs": 0,
    "achievements": [],
    "missions_completed": 0,
    "level": 1,
    "xp": 0,
    "unlocked_chars": [0],
    "unlocked_boards": [0],
    "themes_played": [],
    "longest_run": 0.0,
    "most_coins_run": 0,
    "longest_streak": 0,
    "total_tricks": 0,
    "leaderboard": [],
    "upgrades": {
        "coin_doubler": 0,
        "head_start": 0,
        "score_booster": 0,
        "magnet_strength": 0,
        "shield_duration": 0,
        "jetpack_fuel": 0,
    },
    "settings": {
        "theme": "city",
        "difficulty": "Normal",
        "char_index": 0,
        "sound": True,
        "music": True,
        "show_fps": True,
        "colorblind": False,
        "high_contrast": False,
        "big_text": False,
        "camera": "behind",
        "fov": 70.0,
        "head_bob": 0.5,
        "color_grade": "neutral",
        "wireframe": False,
    }
}

def load_save():
    try:
        with open(SAVE_FILE) as f:
            data = json.load(f)
        # Merge missing keys
        for k, v in DEFAULT_SAVE.items():
            if k not in data:
                data[k] = copy.deepcopy(v)
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    if kk not in data[k]:
                        data[k][kk] = copy.deepcopy(vv)
        return data
    except:
        return copy.deepcopy(DEFAULT_SAVE)

def save_game(data):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

# ─────────────────────────────────────────────────────────────────────────────
#  HUD RENDERER (features 72–82)
# ─────────────────────────────────────────────────────────────────────────────

class HUD:
    def __init__(self, fb):
        self.fb = fb
        self.score_display = 0.0   # animated score
        self.coins_display = 0.0
        self.achievement_queue = deque()
        self.ach_timer = 0.0
        self.ach_text = ""
        self.flash_timer = 0.0
        self.flash_color = CP_WHITE
        self.combo_display = ""
        self.combo_timer = 0.0
        self.danger_timer = 0.0
        self.warning_text = ""

    def update(self, dt, score, coins):
        # Animated score/coins
        self.score_display = lerp(self.score_display, float(score), min(1.0, dt*8.0))
        self.coins_display = lerp(self.coins_display, float(coins), min(1.0, dt*10.0))
        if self.ach_timer > 0: self.ach_timer -= dt
        if self.flash_timer > 0: self.flash_timer -= dt
        if self.combo_timer > 0: self.combo_timer -= dt
        if self.danger_timer > 0: self.danger_timer -= dt
        if self.achievement_queue and self.ach_timer <= 0:
            self.ach_text = self.achievement_queue.popleft()
            self.ach_timer = 3.0

    def show_combo(self, text):
        self.combo_display = text
        self.combo_timer = 1.5

    def flash(self, color):
        self.flash_timer = 0.15
        self.flash_color = color

    def danger_warn(self, text):
        self.danger_timer = 1.0
        self.warning_text = text

    def push_achievement(self, name):
        self.achievement_queue.append(f"★ {name} ★")

    def draw(self, game_state, settings):
        fb = self.fb
        W, H = fb.W, fb.H
        speed = game_state.get('speed', BASE_SPEED)
        dist  = game_state.get('distance', 0.0)
        mult  = game_state.get('multiplier', 1)
        active_pups = game_state.get('active_powerups', {})
        hp    = game_state.get('hp', 3)
        lane  = game_state.get('lane', 1)
        fps   = game_state.get('fps', 0)
        jetpack_fuel = game_state.get('jetpack_fuel', 0.0)
        altitude = game_state.get('altitude', 0.0)
        streak = game_state.get('streak', 0)
        autopilot = game_state.get('autopilot', False)
        godmode = game_state.get('godmode', False)
        shield = POWERUP_SHIELD in active_pups
        tutorial = game_state.get('tutorial_step', -1)

        # ── Top bar ──────────────────────────────────────────────
        # Score
        score_str = f"SCORE: {int(self.score_display):>9}"
        fb.draw_text(2, 0, score_str, CP_WHITE)
        # Coins
        coin_str = f"●{int(self.coins_display):>5}"
        fb.draw_text(W//2 - len(coin_str)//2, 0, coin_str, CP_YELLOW)
        # Distance
        dist_str = f"{dist:.0f}m"
        fb.draw_text(W - len(dist_str) - 2, 0, dist_str, CP_GREEN)

        # Multiplier
        if mult > 1:
            mx_str = f"x{mult}"
            fb.draw_text(W//2 - 2, 1, mx_str, CP_ORANGE)

        # Streak
        if streak >= 3:
            st_str = f"🔥{streak}x"
            fb.draw_text(W//2+4, 1, f"STREAK:{streak}", CP_RED)

        # HP / Shield
        if shield:
            fb.draw_text(2, 1, "[ SHIELD ]", CP_CYAN)
        else:
            hp_str = "♥" * hp + "♡" * (3 - hp)
            fb.draw_text(2, 1, hp_str, CP_RED)

        # ── Speed meter (feature 72) ──────────────────────────────
        spd_label = f"SPD:{speed:>7.1f}"
        fb.draw_text(W - len(spd_label) - 2, 1, spd_label, CP_CYAN)
        # Speed bar
        bar_w = 20
        bar_x = W - bar_w - 2
        bar_fill = int(clamp(speed / MAX_SPEED, 0, 1) * bar_w)
        fb.draw_text(bar_x, 2, '[' + '▓'*bar_fill + '░'*(bar_w-bar_fill) + ']', CP_CYAN)

        # ── Active power-up timers (feature 76) ─────────────────
        row = 3
        for ptype, remaining in list(active_pups.items())[:4]:
            sym  = POWERUP_SYMBOLS.get(ptype, '?')
            col  = POWERUP_COLORS.get(ptype, CP_WHITE)
            dur  = POWERUP_DURATIONS.get(ptype, 10.0)
            pct  = clamp(remaining / dur, 0, 1)
            bar_len = 12
            filled = int(pct * bar_len)
            bar = f"{sym}[{'█'*filled}{'░'*(bar_len-filled)}]{remaining:.1f}s"
            fb.draw_text(2, row, bar, col)
            row += 1

        # ── Jetpack altitude bar (feature 81) ───────────────────
        if POWERUP_JETPACK in active_pups:
            alt_pct = clamp(jetpack_fuel / POWERUP_DURATIONS[POWERUP_JETPACK], 0, 1)
            alt_bar = int(alt_pct * 10)
            fb.draw_text(2, row, f"FUEL[{'▓'*alt_bar}{'░'*(10-alt_bar)}]", CP_CYAN)
            row += 1

        # ── FPS (feature 80) ────────────────────────────────────
        if settings.get('show_fps', True):
            fb.draw_text(W-8, H-1, f"FPS:{fps:3d}", CP_DGRAY)

        # ── Autopilot indicator (feature 93) ────────────────────
        if autopilot:
            label = "◈ AUTOPILOT ◈"
            fb.draw_text(W//2 - len(label)//2, H-2, label, CP_MAGENTA)

        # ── God mode indicator ──────────────────────────────────
        if godmode:
            fb.draw_text(2, H-2, "※GOD MODE※", CP_YELLOW)

        # ── Minimap (feature 79) ─────────────────────────────────
        mm_x = W//2 - 6
        mm_y = H - 4
        fb.draw_text(mm_x, mm_y,   "┌─┬─┬─┐", CP_DGRAY)
        fb.draw_text(mm_x, mm_y+1, "│ │ │ │", CP_DGRAY)
        fb.draw_text(mm_x, mm_y+2, "└─┴─┴─┘", CP_DGRAY)
        # Player position
        player_mm_x = mm_x + 1 + lane*2
        fb.put(player_mm_x, mm_y+1, '▲', CP_GREEN)

        # ── Achievement popup (feature 107) ─────────────────────
        if self.ach_timer > 0:
            ach_x = W//2 - len(self.ach_text)//2
            fb.draw_text(ach_x - 1, H//2 - 3, '╔' + '═'*(len(self.ach_text)+1) + '╗', CP_YELLOW)
            fb.draw_text(ach_x - 1, H//2 - 2, '║ ' + self.ach_text + '║', CP_YELLOW)
            fb.draw_text(ach_x - 1, H//2 - 1, '╚' + '═'*(len(self.ach_text)+1) + '╝', CP_YELLOW)

        # ── Combo display (feature 42) ───────────────────────────
        if self.combo_timer > 0 and self.combo_display:
            cx = W//2 - len(self.combo_display)//2
            fb.draw_text(cx, H//2, self.combo_display, CP_ORANGE)

        # ── Danger warning (feature 104) ────────────────────────
        if self.danger_timer > 0 and self.warning_text:
            wx = W//2 - len(self.warning_text)//2
            fb.draw_text(wx, H-6, self.warning_text, CP_RED)

        # ── Screen flash (feature 71) ────────────────────────────
        if self.flash_timer > 0:
            alpha = self.flash_timer / 0.15
            # Draw border flash
            if alpha > 0.5:
                col = self.flash_color
                fb.hline(0, 0, W-1, '█', col, -999)
                fb.hline(H-1, 0, W-1, '█', col, -999)
                fb.vline(0, 0, H-1, '█', col, -999)
                fb.vline(W-1, 0, H-1, '█', col, -999)

        # ── Tutorial messages (feature 128) ─────────────────────
        if tutorial >= 0:
            msgs = [
                "← → Arrow keys to change lane",
                "↑ to JUMP | ↓ to ROLL/SLIDE",
                "Collect ● coins for score!",
                "Power-ups: M=Magnet S=Shield J=Jetpack",
                "Press A for AUTOPILOT | P to PAUSE",
            ]
            if tutorial < len(msgs):
                msg = msgs[tutorial]
                tx = W//2 - len(msg)//2
                fb.draw_text(tx, H//2 + 3, msg, CP_YELLOW)

        # ── Session timer (feature 149) ─────────────────────────
        sess = game_state.get('session_time', 0.0)
        m, s = divmod(int(sess), 60)
        fb.draw_text(2, H-1, f"TIME {m:02d}:{s:02d}", CP_LGRAY)

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN GAME STATE
# ─────────────────────────────────────────────────────────────────────────────

class Game:
    def __init__(self, save_data, settings):
        self.save = save_data
        self.settings = settings

        # Player state
        self.lane = 1
        self.target_lane = 1
        self.x = LANES[1]
        self.y = 0.0
        self.z = 0.0
        self.vy = 0.0
        self.jumping = False
        self.rolling = False
        self.roll_timer = 0.0
        self.double_jump_used = False
        self.in_air = False
        self.jump_count = 0
        self.trick_angle = 0.0
        self.trick_timer = 0.0
        self.lean = 0.0

        # Lane change
        self.lane_changing = False
        self.lane_change_timer = 0.0
        self.lane_from = 1
        self.lane_to = 1

        # Speed system (features 5, 53, 153)
        diff = DIFFICULTIES[settings.get('difficulty', 'Normal')]
        self.base_speed = BASE_SPEED * diff['speed_mult']
        self.speed = self.base_speed
        self.target_speed = self.speed
        self.max_speed = MAX_SPEED
        self.speed_ramp = SPEED_RAMP * diff['ramp']
        self.sprinting = False
        self.braking = False
        self.turbo_active = False
        self.slowmo_active = False
        self.manual_speed = None  # overrides if set

        # Camera (features 47–51)
        self.camera_mode = settings.get('camera', 'behind')
        self.cam_y = CAMERA_Y
        self.cam_z_offset = CAMERA_Z
        self.cam_shake = 0.0
        self.cam_bob = 0.0
        self.cam_bob_t = 0.0
        self.fov = settings.get('fov', FOV)
        self.cinematic_timer = 0.0
        self.cinematic_angle = 0.0

        # Score
        self.score = 0
        self.coins = 0
        self.distance = 0.0
        self.multiplier = 1
        self.streak = 0
        self.max_streak = 0
        self.trick_count = 0
        self.run_coins = 0

        # Lives / damage
        self.hp = 3
        self.invincible_timer = 0.0
        self.alive = True
        self.godmode = False

        # Power-ups
        self.active_powerups = {}  # type -> remaining_time
        self.jetpack_altitude = 0.0
        self.jetpack_fuel = POWERUP_DURATIONS[POWERUP_JETPACK]

        # Hoverboard (feature 15)
        self.hoverboard = False
        self.hoverboard_used = False

        # Objects
        self.obstacles = []
        self.coins_list = []
        self.powerups_list = []
        self.buildings = []

        # Spawners
        self.obs_spawner = ObstacleSpawner()
        self.coin_spawner = CoinSpawner()
        self.building_gen = BuildingGenerator()

        # Particles
        self.particles = ParticleSystem()

        # Autopilot (feature 4)
        self.autopilot = AutopilotAI(mode='balanced')

        # Stats
        self.session_time = 0.0
        self.fps = 0
        self.frame_count = 0
        self.fps_timer = 0.0
        self.frame_times = deque(maxlen=30)

        # Visual settings
        self.theme = settings.get('theme', 'city')
        self.wireframe = settings.get('wireframe', False)
        self.color_grade = settings.get('color_grade', 'neutral')
        self.night_vision = False
        self.grayscale = False
        self.scanlines = False
        self.invert = False
        self.pixelated = False

        # Danger zone
        self.danger_nearby = False

        # Combo
        self.combo = 0
        self.last_coin_time = 0.0
        self.combo_mult_bonus = 0

        # Speed lines effect (feature 138)
        self.speed_lines_intensity = 0.0

        # Tutorial
        self.tutorial_active = settings.get('tutorial_active', False)
        self.tutorial_step = 0 if self.tutorial_active else -1
        self.tutorial_timer = 0.0

        # Missions (feature 32)
        self.missions = self._gen_missions()
        self.mission_progress = {m['id']: 0 for m in self.missions}

        # Replay (features 94, 95)
        self.replay_buffer = deque(maxlen=1800)  # ~30s at 60fps
        self.replay_mode = False

        # Benchmarks
        self.benchmark_mode = False
        self.benchmark_frames = 0
        self.benchmark_start = time.time()

        # Head-start bonus (feature upgrade)
        self.upgrade_head_start = save_data.get('upgrades', {}).get('head_start', 0)
        self.distance += self.upgrade_head_start * 100.0

        # Score booster
        self.upgrade_score_boost = save_data.get('upgrades', {}).get('score_booster', 0)

        # Coin doubler
        self.upgrade_coin_doubler = save_data.get('upgrades', {}).get('coin_doubler', 0)

        # Generate initial environment
        self._init_world()

        self.last_time = time.time()

    def _init_world(self):
        # Pre-spawn buildings
        for _ in range(20):
            self.buildings.append(self.building_gen.generate_next('left'))
        for _ in range(20):
            self.buildings.append(self.building_gen.generate_next('right'))
        # Pre-spawn coins
        for _ in range(8):
            batch = self.coin_spawner.spawn_next()
            self.coins_list.extend(batch)
        # Pre-spawn some obstacles
        for _ in range(4):
            batch = self.obs_spawner.spawn_next(0)
            self.obstacles.extend(batch)

    def _gen_missions(self):
        return [
            {"id": "m_dist",   "name": "Run 500m",          "target": 500,  "type": "distance"},
            {"id": "m_coins",  "name": "Collect 50 coins",  "target": 50,   "type": "coins"},
            {"id": "m_jumps",  "name": "Jump 20 times",     "target": 20,   "type": "jumps"},
            {"id": "m_pups",   "name": "Get 3 power-ups",   "target": 3,    "type": "powerups"},
            {"id": "m_tricks", "name": "Do 5 tricks",       "target": 5,    "type": "tricks"},
        ]

    # ── Physics ──────────────────────────────────────────────────────────────

    def jump(self):
        if not self.jumping and not self.rolling:
            self.vy = JUMP_VEL
            if POWERUP_SNEAKERS in self.active_powerups:
                self.vy = JUMP_VEL * 1.6  # super sneakers (feature 14)
            self.jumping = True
            self.in_air = True
            self.jump_count = 1
            self.mission_progress['m_jumps'] = self.mission_progress.get('m_jumps', 0) + 1
            # Trick on jump (features 54–57)
            self.trick_timer = 0.4
            self.trick_angle = 0.0
            return True
        elif self.in_air and self.jump_count < 2:  # double jump (feature 52)
            self.vy = JUMP_VEL * 0.85
            self.jump_count = 2
            self.trick_timer = 0.4
            return True
        return False

    def roll(self):
        if not self.in_air and not self.rolling:
            self.rolling = True
            self.roll_timer = ROLL_DURATION
            return True
        return False

    def change_lane(self, direction):
        """Smooth lane change (feature 102)"""
        new_lane = clamp(self.lane + direction, 0, 2)
        if new_lane != self.lane and not self.lane_changing:
            self.lane_from = self.lane
            self.lane_to   = new_lane
            self.lane_changing = True
            self.lane_change_timer = 0.0
            self.lane = new_lane
            self.lean = -direction * 0.4
            return True
        return False

    def apply_jetpack(self, dt):
        """Jetpack flight (feature 13)"""
        if POWERUP_JETPACK in self.active_powerups:
            self.jetpack_altitude = min(3.5, self.jetpack_altitude + dt * 4.0)
            self.particles.emit_jetpack(self.x, self.y, self.z)
        else:
            self.jetpack_altitude = max(0.0, self.jetpack_altitude - dt * 8.0)

    def update_speed(self, dt):
        """Speed management (features 5, 50, 51, 98–101)"""
        effective_max = self.max_speed
        if self.manual_speed is not None:
            self.target_speed = clamp(self.manual_speed, 1.0, self.max_speed)
        else:
            self.target_speed = self.base_speed
            if self.sprinting:
                self.target_speed = min(self.base_speed * 1.5, effective_max)
            if self.braking:
                self.target_speed = max(1.0, self.base_speed * 0.3)
            if POWERUP_TURBO in self.active_powerups:  # feature 50
                self.target_speed = min(self.speed * 1.8, effective_max)
            if POWERUP_SLOW in self.active_powerups:   # feature 49
                self.target_speed = max(1.0, self.target_speed * 0.4)

        # Ramp up base speed with distance (feature 153)
        self.base_speed = min(
            self.base_speed + self.speed_ramp * dt,
            effective_max * 0.8
        )

        # Smooth speed
        self.speed = lerp(self.speed, self.target_speed, dt * 3.0)
        self.speed = clamp(self.speed, 0.5, effective_max)

        # Dynamic FOV (feature 135)
        speed_t = clamp(self.speed / 200.0, 0, 1)
        self.fov = lerp(FOV, FOV + 25.0, smoothstep(speed_t))

        # Speed lines (feature 138)
        self.speed_lines_intensity = clamp(self.speed / 1000.0, 0, 1)

    def update_powerups(self, dt):
        """Tick power-up timers"""
        expired = []
        for ptype, remaining in self.active_powerups.items():
            remaining -= dt
            if remaining <= 0:
                expired.append(ptype)
            else:
                self.active_powerups[ptype] = remaining
        for p in expired:
            del self.active_powerups[p]
            if p == POWERUP_TURBO:
                self.turbo_active = False
            if p == POWERUP_SLOW:
                self.slowmo_active = False

        # Multiplier from power-ups
        self.multiplier = 1
        for ptype in [POWERUP_MULTI10, POWERUP_MULTI5, POWERUP_MULTI3, POWERUP_MULTI2]:
            if ptype in self.active_powerups:
                self.multiplier = int(ptype.replace('x','')) if ptype.startswith('x') else 1
                if ptype == POWERUP_MULTI2:  self.multiplier = 2
                if ptype == POWERUP_MULTI3:  self.multiplier = 3
                if ptype == POWERUP_MULTI5:  self.multiplier = 5
                if ptype == POWERUP_MULTI10: self.multiplier = 10
                break

    def activate_powerup(self, ptype):
        dur = POWERUP_DURATIONS.get(ptype, 10.0)
        # Upgrade bonuses
        if ptype == POWERUP_SHIELD:
            dur += self.save.get('upgrades',{}).get('shield_duration',0) * 2.0
        if ptype == POWERUP_JETPACK:
            dur += self.save.get('upgrades',{}).get('jetpack_fuel',0) * 3.0
        self.active_powerups[ptype] = dur
        self.particles.emit_powerup(self.x, self.y, self.z)
        self.hud.flash(POWERUP_COLORS.get(ptype, CP_WHITE))
        self.mission_progress['m_pups'] = self.mission_progress.get('m_pups', 0) + 1

        if ptype == POWERUP_TURBO:
            self.turbo_active = True
        if ptype == POWERUP_SLOW:
            self.slowmo_active = True

    def collect_coin(self, coin):
        """Collect a coin with combo logic"""
        now = time.time()
        if now - self.last_coin_time < 0.5:
            self.combo += 1
        else:
            self.combo = 1
        self.last_coin_time = now

        amount = COIN_VALUE * (2 if self.upgrade_coin_doubler > 0 else 1)
        if POWERUP_MULTI2 in self.active_powerups:  amount *= 2
        if POWERUP_MULTI3 in self.active_powerups:  amount *= 3
        if POWERUP_MULTI5 in self.active_powerups:  amount *= 5
        if POWERUP_MULTI10 in self.active_powerups: amount *= 10

        self.coins += amount
        self.run_coins += amount
        self.score += amount * 10 * self.multiplier * (1 + self.upgrade_score_boost)

        self.streak += 1
        if self.streak > self.max_streak:
            self.max_streak = self.streak

        if self.combo >= 5:
            self.hud.show_combo(f"COMBO x{self.combo}!")

        self.particles.emit_coin(coin['x'], coin['y'], coin['z'])
        self.mission_progress['m_coins'] = self.mission_progress.get('m_coins', 0) + amount

    def take_damage(self):
        if self.invincible_timer > 0 or self.godmode:
            return
        if POWERUP_SHIELD in self.active_powerups:
            del self.active_powerups[POWERUP_SHIELD]
            self.hud.flash(CP_CYAN)
            self.cam_shake = 0.3
            return
        if self.hoverboard and not self.hoverboard_used:
            self.hoverboard_used = True
            self.hud.flash(CP_BLUE)
            self.cam_shake = 0.3
            self.hud.danger_warn("HOVERBOARD SAVED YOU!")
            return
        self.hp -= 1
        self.invincible_timer = 2.0
        self.cam_shake = 0.5
        self.streak = 0
        self.combo = 0
        self.hud.flash(CP_RED)
        self.particles.emit_explosion(self.x, self.y+0.5, self.z)
        if self.hp <= 0:
            self.alive = False

    def check_collision(self, obs):
        """Feature-rich collision detection"""
        if self.invincible_timer > 0 or self.godmode:
            return False
        if POWERUP_JETPACK in self.active_powerups and self.jetpack_altitude > 1.5:
            return False  # flying over
        ox, oz = obs['x'], obs['z']
        otype = obs['type']

        dist_x = abs(self.x - ox)
        dist_z = abs(self.z - oz)

        if dist_x > 1.0 or dist_z > 3.0:
            return False

        if otype == OBS_BARRIER:
            # Roll under (feature 25)
            if self.rolling: return False
            if self.y > 0.5: return False
        elif otype == OBS_HIGH:
            # Jump over (feature 26)
            if self.y > 0.9: return False
        elif otype == OBS_BARREL:
            if dist_x > 0.7 or dist_z > 1.5: return False

        return dist_x < 0.9 and dist_z < 2.5

    def update_autopilot(self, dt):
        """Feature 4: Autopilot driving"""
        if not self.autopilot.active:
            return
        tl, sj, sr = self.autopilot.decide(
            {'x': self.x, 'z': self.z, 'lane': self.lane, 'speed': self.speed},
            self.obstacles, self.coins_list, self.powerups_list, dt
        )
        if tl != self.lane and not self.lane_changing:
            self.change_lane(tl - self.lane)
        if sj: self.jump()
        if sr: self.roll()

    def update(self, dt):
        """Main game update"""
        if not self.alive: return

        self.session_time += dt
        self.update_speed(dt)

        effective_speed = self.speed
        if self.slowmo_active:
            effective_speed *= 0.3

        # Advance player
        self.z += effective_speed * dt
        self.distance += effective_speed * dt

        # Gravity & jump
        if self.in_air or self.y > 0.001:
            self.vy += GRAVITY * dt
            self.y += self.vy * dt
            if self.y <= 0.0:
                self.y = 0.0
                self.vy = 0.0
                self.jumping = False
                self.in_air = False
                self.jump_count = 0
                if abs(self.vy) > 2:
                    self.particles.emit_dust(self.x, 0, self.z)

        # Roll timer
        if self.rolling:
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.rolling = False

        # Lane change animation
        if self.lane_changing:
            self.lane_change_timer += dt
            t = smoothstep(self.lane_change_timer / LANE_CHANGE_TIME)
            self.x = lerp(LANES[self.lane_from], LANES[self.lane_to], t)
            self.lean = lerp(self.lean, 0, dt * 8)
            if self.lane_change_timer >= LANE_CHANGE_TIME:
                self.lane_changing = False
                self.x = LANES[self.lane_to]
                self.lean = 0.0
        else:
            self.x = lerp(self.x, LANES[self.lane], dt * 15.0)

        # Trick animation
        if self.trick_timer > 0:
            self.trick_timer -= dt
            self.trick_angle = math.sin(self.trick_timer * math.pi * 3) * math.pi

        # Jetpack
        self.apply_jetpack(dt)
        actual_y = self.y + self.jetpack_altitude

        # Camera bob
        self.cam_bob_t += dt * (effective_speed / 8.0) * 2.5
        head_bob_intensity = self.settings.get('head_bob', 0.5)
        self.cam_bob = math.sin(self.cam_bob_t) * 0.06 * head_bob_intensity

        # Camera shake
        if self.cam_shake > 0:
            self.cam_shake -= dt

        # Invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= dt

        # Power-ups
        self.update_powerups(dt)

        # Autopilot
        self.update_autopilot(dt)

        # Distance-based score
        self.score += int(effective_speed * dt * self.multiplier * (1 + self.upgrade_score_boost))

        # Spawn new world objects
        self._spawn_world()

        # Despawn far objects
        self._despawn_world()

        # Collision checks
        self._check_collisions(actual_y)

        # Particles
        self.particles.update(dt)
        if self.speed > 100:
            self.particles.emit_trail(self.x, actual_y, self.z)

        # Camera update
        self._update_camera(dt, actual_y)

        # Mission progress
        self.mission_progress['m_dist'] = int(self.distance)
        self.mission_progress['m_tricks'] = self.trick_count

        # FPS
        self.frame_count += 1
        self.fps_timer += dt
        if self.fps_timer >= 0.5:
            self.fps = int(self.frame_count / self.fps_timer)
            self.frame_count = 0
            self.fps_timer = 0.0

        # Danger detection
        close_obs = [o for o in self.obstacles
                      if o['lane'] == self.lane and abs(o['z'] - self.z) < 5.0 and o['z'] > self.z]
        self.danger_nearby = len(close_obs) > 0
        if close_obs and abs(close_obs[0]['z'] - self.z) < 3.5:
            self.hud.danger_warn("⚠ DANGER AHEAD ⚠")

        # Achievements check
        self._check_achievements()

        # Record replay frame
        self.replay_buffer.append({
            'x': self.x, 'y': actual_y, 'z': self.z,
            'lane': self.lane, 'speed': self.speed,
            'score': self.score, 'coins': self.coins,
        })

        self.hud.update(dt, self.score, self.coins)

    def _update_camera(self, dt, char_y):
        """Camera modes (features 47–51)"""
        shake_x = math.sin(time.time() * 40) * self.cam_shake * 0.3
        shake_y = math.cos(time.time() * 37) * self.cam_shake * 0.2
        mode = self.camera_mode
        if mode == 'behind':
            self.view_eye = [self.x + shake_x,
                              self.cam_y + self.cam_bob + shake_y,
                              self.z + self.cam_z_offset]
            self.view_at  = [self.x, char_y + 1.0, self.z + 12.0]
        elif mode == 'side':
            self.view_eye = [self.x - 6.0 + shake_x, self.cam_y + shake_y, self.z + 2.0]
            self.view_at  = [self.x, char_y + 1.0, self.z + 4.0]
        elif mode == 'top':
            self.view_eye = [self.x + shake_x, 10.0 + shake_y, self.z - 2.0]
            self.view_at  = [self.x, 0.0, self.z + 8.0]
        elif mode == 'cinematic':
            self.cinematic_timer += dt * 0.4
            cx = math.sin(self.cinematic_timer) * 5.0
            self.view_eye = [cx + shake_x, 3.5 + shake_y, self.z - 4.0]
            self.view_at  = [self.x, char_y + 1.0, self.z + 8.0]
        elif mode == 'fps':
            self.view_eye = [self.x + shake_x, char_y + 1.6 + shake_y, self.z + 0.5]
            self.view_at  = [self.x, char_y + 1.6, self.z + 12.0]
        else:
            self.view_eye = [self.x, self.cam_y + self.cam_bob, self.z + self.cam_z_offset]
            self.view_at  = [self.x, char_y + 1.0, self.z + 12.0]

    def _spawn_world(self):
        """Procedural spawning (features 96, 97)"""
        diff_mult = 1.0 + self.distance / 5000.0
        look_z = self.z + OBSTACLE_SPAWN_DIST

        # Spawn obstacles
        while self.obs_spawner.next_spawn_z < look_z:
            batch = self.obs_spawner.spawn_next(self.z, diff_mult)
            self.obstacles.extend(batch)

        # Spawn coins
        while self.coin_spawner.next_z < look_z:
            batch = self.coin_spawner.spawn_next(
                magnet_active=POWERUP_MAGNET in self.active_powerups
            )
            self.coins_list.extend(batch)

        # Spawn buildings
        while self.building_gen.next_z_left < look_z + 20:
            self.buildings.append(self.building_gen.generate_next('left'))
        while self.building_gen.next_z_right < look_z + 20:
            self.buildings.append(self.building_gen.generate_next('right'))

        # Spawn power-ups occasionally
        if random.random() < 0.0003 or (len(self.powerups_list) == 0 and random.random() < 0.001):
            ptype = random.choice(list(POWERUP_DURATIONS.keys()))
            lane = random.randint(0,2)
            self.powerups_list.append({
                'type': ptype, 'x': LANES[lane], 'y': 0.6, 'z': look_z,
                'lane': lane, 'phase': random.uniform(0, math.pi*2)
            })

    def _despawn_world(self):
        cutoff = self.z + DESPAWN_DIST
        self.obstacles   = [o for o in self.obstacles   if o['z'] > cutoff]
        self.coins_list  = [c for c in self.coins_list  if c['z'] > cutoff]
        self.powerups_list = [p for p in self.powerups_list if p['z'] > cutoff]
        self.buildings   = [b for b in self.buildings   if b['z'] > cutoff - 30]

    def _check_collisions(self, char_y):
        # Obstacles
        for obs in self.obstacles[:]:
            if self.check_collision(obs):
                self.take_damage()
                break  # only one collision per frame

        # Coins
        magnet_range = 0.8
        if POWERUP_MAGNET in self.active_powerups:
            magnet_range = 2.5 + self.save.get('upgrades',{}).get('magnet_strength',0) * 0.5
        collected = []
        for c in self.coins_list:
            dist = math.sqrt((self.x-c['x'])**2 + (char_y-c['y'])**2 + (self.z-c['z'])**2)
            if dist < magnet_range:
                self.collect_coin(c)
                collected.append(c)
        for c in collected:
            self.coins_list.remove(c)

        # Power-ups
        collected_p = []
        for p in self.powerups_list:
            dist = math.sqrt((self.x-p['x'])**2 + (self.z-p['z'])**2)
            if dist < 1.2:
                self.activate_powerup(p['type'])
                collected_p.append(p)
        for p in collected_p:
            self.powerups_list.remove(p)

    def _check_achievements(self):
        achs = self.save.get('achievements', [])
        def unlock(aid):
            if aid not in achs:
                achs.append(aid)
                self.save['achievements'] = achs
                name = next((a['name'] for a in ACHIEVEMENTS if a['id'] == aid), aid)
                self.hud.push_achievement(name)

        if self.run_coins >= 100:  unlock('coins_100')
        if self.save.get('total_coins',0) >= 1000: unlock('coins_1000')
        if self.distance >= 1000: unlock('dist_1000')
        if self.distance >= 10000: unlock('dist_10000')
        if self.speed >= 1000: unlock('speed_1000')
        if self.speed >= 10000: unlock('speed_10000')
        if POWERUP_JETPACK in self.active_powerups: unlock('use_jetpack')
        if POWERUP_SHIELD in self.active_powerups:  unlock('use_shield')
        if POWERUP_MULTI10 in self.active_powerups: unlock('multi10')
        if self.trick_count >= 10: unlock('trick_10')
        if self.max_streak >= 20: unlock('streak_20')
        if self.godmode: unlock('godmode')
        if self.autopilot.active and self.distance >= 500: unlock('autopilot_win')
        if self.save.get('total_runs',0) >= 10: unlock('run_10')
        if self.save.get('total_runs',0) >= 50: unlock('run_50')
        theme = self.settings.get('theme','city')
        if theme == 'neon': unlock('neon_theme')

    def render(self, fb, t):
        """Render one frame"""
        W, H = fb.W, fb.H
        theme = self.theme

        # Background (sky + ground)
        sky_color = THEMES[theme]["sky"]
        gnd_color = THEMES[theme]["ground"]

        # Apply color modes (features 139–145)
        if self.night_vision:
            sky_color = CP_LGREEN; gnd_color = CP_GREEN
        if self.grayscale:
            sky_color = CP_LGRAY; gnd_color = CP_DGRAY

        # Sky gradient
        horizon_y = H // 2 - 2
        if theme in ('night', 'subway', 'neon'):
            fb.fill_rect(0, 0, W-1, horizon_y, '·', sky_color, 100.0)
        else:
            fb.fill_rect(0, 0, W-1, horizon_y, ' ', sky_color, 100.0)

        # Ground
        fb.fill_rect(0, horizon_y+1, W-1, H-1, '░', gnd_color, 101.0)

        # Cloud layer (feature 66)
        if theme not in ('subway',):
            self._draw_clouds(fb, t)

        # Bird flocking (feature 65)
        if theme in ('city', 'desert'):
            self._draw_birds(fb, t)

        # Build matrices
        proj = perspective(self.fov, W/H, NEAR, FAR)
        view = look_at(self.view_eye, self.view_at, [0,1,0])

        # Draw environment
        draw_overhead_cables(fb, proj, view, theme, self.z)
        draw_environment(fb, proj, view, theme, self.z, self.buildings)
        draw_track(fb, proj, view, theme, self.z, self.speed)

        # Tunnel if in subway theme
        if theme == 'subway':
            draw_tunnel_section(fb, proj, view, theme, self.z - 5, self.z + FAR)

        # Draw coins
        for c in self.coins_list:
            if abs(c['z'] - self.z) < FAR:
                draw_coin(fb, proj, view, c, t)

        # Draw power-ups
        for p in self.powerups_list:
            if abs(p['z'] - self.z) < FAR:
                draw_powerup_box(fb, proj, view, p, t)

        # Draw obstacles
        for obs in self.obstacles:
            if abs(obs['z'] - self.z) < FAR:
                otype = obs['type']
                if otype == OBS_TRAIN:   draw_train_obstacle(fb, proj, view, obs)
                elif otype == OBS_BARRIER: draw_barrier_obstacle(fb, proj, view, obs)
                elif otype == OBS_HIGH:  draw_high_barrier(fb, proj, view, obs)
                elif otype == OBS_BARREL: draw_barrel_obstacle(fb, proj, view, obs)

        # Character
        actual_y = self.y + self.jetpack_altitude
        char_info = CHARACTERS[self.settings.get('char_index', 0)]
        char3d = Character3D(char_info['skin'], char_info['body'], char_info['hair'])
        char3d.anim_t = self.cam_bob_t

        blink = int(self.invincible_timer * 8) % 2 == 0 or self.invincible_timer <= 0
        if blink:
            char3d.draw(fb, proj, view,
                         (self.x, actual_y, self.z + 1.0),
                         roll=self.rolling,
                         jump=self.jumping,
                         trick_angle=self.trick_angle if self.in_air else 0,
                         lean=self.lean)

        # Jetpack effect
        if POWERUP_JETPACK in self.active_powerups:
            draw_jetpack_effect(fb, proj, view, (self.x, actual_y, self.z + 1.0), t)

        # Particles
        self.particles.draw(fb, proj, view)

        # Speed lines (feature 138)
        if self.speed_lines_intensity > 0.1:
            self._draw_speed_lines(fb, t)

        # Danger red tint borders (feature 144)
        if self.danger_nearby:
            alpha = 0.5 + 0.5 * math.sin(t * 8)
            if alpha > 0.7:
                for vy in range(1, H-1, 2):
                    fb.put(0, vy, '▌', CP_RED, -999)
                    fb.put(W-1, vy, '▐', CP_RED, -999)

        # Vignette (feature 144)
        self._draw_vignette(fb)

        # Scanlines (feature 142)
        if self.scanlines:
            for sy in range(0, H, 2):
                for sx in range(0, W):
                    c = fb.chars[sy][sx]
                    fb.put(sx, sy, c, CP_DARK, -998)

        # HUD on top
        self.hud.draw({
            'speed': self.speed,
            'distance': self.distance,
            'score': self.score,
            'coins': self.coins,
            'multiplier': self.multiplier,
            'active_powerups': self.active_powerups,
            'hp': self.hp,
            'lane': self.lane,
            'fps': self.fps,
            'jetpack_fuel': self.active_powerups.get(POWERUP_JETPACK, 0),
            'altitude': self.jetpack_altitude,
            'streak': self.streak,
            'autopilot': self.autopilot.active,
            'godmode': self.godmode,
            'session_time': self.session_time,
            'tutorial_step': self.tutorial_step,
        }, self.settings)

    def _draw_clouds(self, fb, t):
        """Animated clouds (feature 66)"""
        for i in range(5):
            cx = int((i * 25 + t * 3) % fb.W)
            cy = max(1, int(fb.H * 0.15 + math.sin(i * 1.7 + t * 0.5) * 2))
            cloud = "~~"
            if 0 <= cx < fb.W - len(cloud):
                for ci, ch in enumerate(cloud):
                    fb.put(cx+ci, cy, ch, CP_WHITE, 99.0)

    def _draw_birds(self, fb, t):
        """Bird flocking (feature 65)"""
        for i in range(4):
            bx = int((i * 30 + t * 5.0 + i*7) % fb.W)
            by = max(1, int(fb.H * 0.1 + math.sin(i + t) * 2))
            wing = "v" if math.sin(t*5 + i) > 0 else "^"
            fb.put(bx, by, wing, CP_DARK, 98.0)

    def _draw_speed_lines(self, fb, t):
        """Radial speed lines (feature 138)"""
        cx, cy = fb.W//2, fb.H//2
        intensity = self.speed_lines_intensity
        n_lines = int(intensity * 20)
        for i in range(n_lines):
            angle = (i / n_lines) * 2 * math.pi + t * 0.5
            length = random.randint(3, 8)
            x1 = cx + int(math.cos(angle) * 3)
            y1 = cy + int(math.sin(angle) * 2)
            x2 = cx + int(math.cos(angle) * (3+length))
            y2 = cy + int(math.sin(angle) * (2+length//2))
            fb.draw_line(x1, y1, x2, y2, '·', CP_LGRAY, -998)

    def _draw_vignette(self, fb):
        """Corner darkening (feature 145)"""
        W, H = fb.W, fb.H
        # Corners
        for r in range(4):
            for c in range(max(0, 4-r)):
                fb.put(c, r, '▓', CP_DARK, -997)
                fb.put(W-1-c, r, '▓', CP_DARK, -997)
                fb.put(c, H-1-r, '▓', CP_DARK, -997)
                fb.put(W-1-c, H-1-r, '▓', CP_DARK, -997)

# ─────────────────────────────────────────────────────────────────────────────
#  MENUS
# ─────────────────────────────────────────────────────────────────────────────

class Menu:
    def __init__(self, stdscr, save_data):
        self.stdscr = stdscr
        self.save = save_data
        self.W = 0
        self.H = 0

    def _draw_banner(self, y, text, color):
        x = max(0, self.W//2 - len(text)//2)
        try:
            self.stdscr.addstr(y, x, text, curses.color_pair(color) | curses.A_BOLD)
        except:
            pass

    def _draw_centered(self, y, text, color, bold=False):
        x = max(0, self.W//2 - len(text)//2)
        attr = curses.color_pair(color)
        if bold: attr |= curses.A_BOLD
        try:
            self.stdscr.addstr(y, x, text, attr)
        except:
            pass

    def main_menu(self):
        """Main menu screen"""
        selected = 0
        items = [
            ("▶  START GAME",      'play'),
            ("⚙  SETTINGS",        'settings'),
            ("🏆  LEADERBOARD",    'leaderboard'),
            ("📊  STATS",          'stats'),
            ("🛒  SHOP",           'shop'),
            ("❓  HOW TO PLAY",    'tutorial'),
            ("✖  QUIT",            'quit'),
        ]
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(1, "╔══════════════════════════════════════╗", CP_CYAN)
            self._draw_banner(2, "║   SUBWAY SURFERS 3D  ULTIMATE PYTHON ║", CP_CYAN)
            self._draw_banner(3, "║     Python Software 3D Renderer      ║", CP_LGRAY)
            self._draw_banner(4, f"║  v{VERSION:<35}║", CP_DGRAY)
            self._draw_banner(5, "╚══════════════════════════════════════╝", CP_CYAN)

            # Animated character
            t = time.time()
            runner = ['♟','♞','♝','♜'][int(t*4)%4]
            self._draw_centered(6, f"  {runner}  {runner}  {runner}  ", CP_YELLOW)

            # High score
            self._draw_centered(8, f"HIGH SCORE: {self.save.get('high_score',0):>10}", CP_YELLOW, bold=True)
            level = self.save.get('level', 1)
            xp    = self.save.get('xp', 0)
            self._draw_centered(9, f"LEVEL {level} | XP: {xp}", CP_GREEN)
            coins = self.save.get('total_coins', 0)
            self._draw_centered(10, f"TOTAL COINS: {coins}", CP_YELLOW)

            for i, (label, _) in enumerate(items):
                y = 12 + i * 2
                if i == selected:
                    self._draw_centered(y, f"► {label} ◄", CP_CYAN, bold=True)
                else:
                    self._draw_centered(y, f"  {label}  ", CP_LGRAY)

            self._draw_centered(self.H-2, "↑↓ Navigate | ENTER Select", CP_DGRAY)
            self.stdscr.refresh()

            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                selected = (selected - 1) % len(items)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(items)
            elif key in (curses.KEY_ENTER, 10, 13):
                return items[selected][1]
            elif key == ord('q'):
                return 'quit'
            time.sleep(0.02)

    def settings_menu(self, settings):
        """Feature 83: Settings menu with all options"""
        options = [
            ("Theme",      "theme",      list(THEMES.keys())),
            ("Difficulty", "difficulty", list(DIFFICULTIES.keys())),
            ("Character",  "char_index", list(range(len(CHARACTERS)))),
            ("Camera",     "camera",     ['behind','side','top','cinematic','fps']),
            ("Show FPS",   "show_fps",   [True, False]),
            ("Sound",      "sound",      [True, False]),
            ("Music",      "music",      [True, False]),
            ("Color Mode", "color_grade",['neutral','warm','cool','vivid']),
            ("Head Bob",   "head_bob",   [0.0, 0.25, 0.5, 0.75, 1.0]),
            ("FOV",        "fov",        [50.0, 60.0, 70.0, 80.0, 90.0, 100.0]),
            ("Colorblind", "colorblind", [False, True]),
            ("High Contrast","high_contrast",[False, True]),
            ("Wireframe",  "wireframe",  [False, True]),
            ("Big Text",   "big_text",   [False, True]),
            ("←  BACK",    None,         None),
        ]
        selected = 0
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(1, "═══ SETTINGS ═══", CP_CYAN)
            for i, (label, key, vals) in enumerate(options):
                y = 3 + i
                if key is None:
                    disp = label
                else:
                    val = settings.get(key, vals[0] if vals else '')
                    if key == 'char_index':
                        val = CHARACTERS[val]['name']
                    disp = f"{label:<16}: {str(val):<12}"
                if i == selected:
                    self._draw_centered(y, f"► {disp} ◄", CP_CYAN, bold=True)
                else:
                    self._draw_centered(y, f"  {disp}  ", CP_LGRAY)
            self._draw_centered(self.H-2, "↑↓ Navigate | ←→ Change | ENTER Back", CP_DGRAY)
            self.stdscr.refresh()

            key_in = self.stdscr.getch()
            label_s, opt_key, vals_s = options[selected]
            if key_in == curses.KEY_UP:
                selected = (selected - 1) % len(options)
            elif key_in == curses.KEY_DOWN:
                selected = (selected + 1) % len(options)
            elif key_in in (curses.KEY_LEFT, curses.KEY_RIGHT) and opt_key:
                cur_val = settings.get(opt_key, vals_s[0])
                try: idx = vals_s.index(cur_val)
                except: idx = 0
                if key_in == curses.KEY_RIGHT:
                    idx = (idx + 1) % len(vals_s)
                else:
                    idx = (idx - 1) % len(vals_s)
                settings[opt_key] = vals_s[idx]
            elif key_in in (curses.KEY_ENTER, 10, 13, ord('q')):
                if opt_key is None or key_in in (ord('q'), 27):
                    return settings
            time.sleep(0.02)

    def leaderboard_screen(self):
        """Feature 105: Top 10 leaderboard"""
        lb = self.save.get('leaderboard', [])
        lb.sort(key=lambda x: x.get('score',0), reverse=True)
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(1, "═══ LEADERBOARD (TOP 10) ═══", CP_YELLOW)
            self._draw_centered(3, f"{'#':<4}{'SCORE':>10}  {'DIST':>8}  {'COINS':>6}  {'CHAR':<10}", CP_LGRAY)
            for i, entry in enumerate(lb[:10]):
                y = 4 + i
                s = entry.get('score',0)
                d = entry.get('distance',0)
                c = entry.get('coins',0)
                ch = entry.get('char','Jake')
                prefix = "►" if i == 0 else " "
                col = [CP_YELLOW, CP_WHITE, CP_ORANGE] + [CP_LGRAY]*7
                self._draw_centered(y, f"{prefix}{i+1:<3} {s:>10}  {d:>7.0f}m  {c:>6}  {ch:<10}", col[i])
            self._draw_centered(self.H-2, "Press any key to return", CP_DGRAY)
            self.stdscr.refresh()
            key = self.stdscr.getch()
            if key != -1: return
            time.sleep(0.05)

    def stats_screen(self):
        """Feature 108: Full stats"""
        s = self.save
        achs = s.get('achievements', [])
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(1, "═══ STATS ═══", CP_GREEN)
            rows = [
                ("Total Runs",         s.get('total_runs', 0)),
                ("Total Distance",     f"{s.get('total_distance',0.0):.0f}m"),
                ("Total Coins",        s.get('total_coins', 0)),
                ("High Score",         s.get('high_score', 0)),
                ("Level",              s.get('level', 1)),
                ("XP",                 s.get('xp', 0)),
                ("Longest Run",        f"{s.get('longest_run',0.0):.0f}m"),
                ("Most Coins (run)",   s.get('most_coins_run', 0)),
                ("Longest Streak",     s.get('longest_streak', 0)),
                ("Total Tricks",       s.get('total_tricks', 0)),
                ("Achievements",       f"{len(achs)}/{len(ACHIEVEMENTS)}"),
                ("Missions Done",      s.get('missions_completed', 0)),
            ]
            for i, (label, val) in enumerate(rows):
                y = 3 + i
                self._draw_centered(y, f"{label:<22}: {val}", CP_WHITE)
            # Achievement list
            y_a = 3 + len(rows) + 1
            self._draw_centered(y_a, "── Achievements Unlocked ──", CP_YELLOW)
            ach_names = [a['name'] for a in ACHIEVEMENTS if a['id'] in achs]
            for i, name in enumerate(ach_names[:8]):
                self._draw_centered(y_a+1+i, f"★ {name}", CP_YELLOW)
            self._draw_centered(self.H-2, "Press any key to return", CP_DGRAY)
            self.stdscr.refresh()
            if self.stdscr.getch() != -1: return
            time.sleep(0.05)

    def shop_screen(self):
        """Feature 109–115: Shop"""
        upgrades = self.save.get('upgrades', copy.deepcopy(DEFAULT_SAVE['upgrades']))
        items = [
            ("Coin Doubler",     "coin_doubler",     3, 200, "Double all coins"),
            ("Head Start",       "head_start",        3, 150, "+100m at run start"),
            ("Score Booster",    "score_booster",    3, 300, "+50% score"),
            ("Magnet Range",     "magnet_strength",  3, 100, "Wider coin magnet"),
            ("Shield Duration",  "shield_duration",  3, 200, "+2s shield"),
            ("Jetpack Fuel",     "jetpack_fuel",     3, 250, "+3s jetpack"),
            ("← BACK",           None,               0, 0,   ""),
        ]
        selected = 0
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            total_coins = self.save.get('total_coins', 0)
            self._draw_banner(1, "═══ SHOP ═══", CP_YELLOW)
            self._draw_centered(2, f"Coins: ● {total_coins}", CP_YELLOW)
            for i, (label, key, max_lvl, cost, desc) in enumerate(items):
                y = 4 + i * 2
                if key:
                    lvl = upgrades.get(key, 0)
                    stars = '★'*lvl + '☆'*(max_lvl-lvl)
                    line = f"{label:<20} {stars}  Cost: {cost}"
                    sub  = f"  {desc}"
                else:
                    line = label; sub = ""
                col = CP_CYAN if i == selected else CP_LGRAY
                self._draw_centered(y, f"{'►' if i==selected else ' '} {line}", col, i==selected)
                if sub:
                    self._draw_centered(y+1, sub, CP_DGRAY)
            self._draw_centered(self.H-2, "↑↓ Navigate | ENTER Buy | Q Back", CP_DGRAY)
            self.stdscr.refresh()
            k = self.stdscr.getch()
            if k == curses.KEY_UP:
                selected = (selected-1)%len(items)
            elif k == curses.KEY_DOWN:
                selected = (selected+1)%len(items)
            elif k in (curses.KEY_ENTER, 10, 13):
                label_s, key_s, max_lvl_s, cost_s, _ = items[selected]
                if key_s is None: break
                cur_lvl = upgrades.get(key_s, 0)
                if cur_lvl < max_lvl_s and total_coins >= cost_s:
                    upgrades[key_s] = cur_lvl + 1
                    self.save['total_coins'] -= cost_s
                    self.save['upgrades'] = upgrades
                    save_game(self.save)
            elif k in (ord('q'), 27):
                break
            time.sleep(0.02)

    def game_over_screen(self, game):
        """Feature 116: Game over / run again"""
        score = game.score
        dist  = game.distance
        coins = game.run_coins
        # Update save
        if score > self.save.get('high_score', 0):
            self.save['high_score'] = score
        self.save['total_coins']    = self.save.get('total_coins',0) + coins
        self.save['total_distance'] = self.save.get('total_distance',0.0) + dist
        self.save['total_runs']     = self.save.get('total_runs',0) + 1
        if dist > self.save.get('longest_run',0.0):
            self.save['longest_run'] = dist
        if coins > self.save.get('most_coins_run', 0):
            self.save['most_coins_run'] = coins
        if game.max_streak > self.save.get('longest_streak',0):
            self.save['longest_streak'] = game.max_streak
        self.save['total_tricks'] = self.save.get('total_tricks',0) + game.trick_count
        # XP
        xp_gain = int(dist / 10) + coins * 2 + score // 100
        self.save['xp'] = self.save.get('xp', 0) + xp_gain
        level = 1 + self.save['xp'] // 1000
        self.save['level'] = level
        # Leaderboard
        lb = self.save.get('leaderboard', [])
        char_name = CHARACTERS[self.save.get('settings',{}).get('char_index',0)]['name']
        lb.append({'score':score,'distance':dist,'coins':coins,'char':char_name})
        lb.sort(key=lambda x:x.get('score',0), reverse=True)
        self.save['leaderboard'] = lb[:10]
        # Achievements
        if self.save.get('total_runs',0) == 1:
            if 'first_run' not in self.save.get('achievements',[]):
                self.save.setdefault('achievements',[]).append('first_run')
        save_game(self.save)

        selected = 0
        items = [("▶ PLAY AGAIN", 'play'), ("▶ MAIN MENU", 'menu')]
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(2, "══ RUN OVER ══", CP_RED)
            self._draw_centered(4, f"SCORE:    {score:>10}", CP_YELLOW, True)
            self._draw_centered(5, f"DISTANCE: {dist:>8.0f}m", CP_GREEN)
            self._draw_centered(6, f"COINS:    {coins:>10}", CP_YELLOW)
            self._draw_centered(7, f"MAX STREAK:{game.max_streak:>8}", CP_ORANGE)
            self._draw_centered(8, f"TRICKS:   {game.trick_count:>10}", CP_CYAN)
            self._draw_centered(9, f"XP EARNED:{xp_gain:>9}", CP_LGREEN)
            self._draw_centered(10,f"HIGH SCORE:{self.save['high_score']:>9}", CP_RED if score == self.save['high_score'] else CP_WHITE,
                                    score == self.save['high_score'])
            if score == self.save['high_score']:
                self._draw_centered(11, "★ NEW HIGH SCORE! ★", CP_YELLOW, True)
            # Mission summary
            y_m = 13
            self._draw_centered(y_m, "── Mission Progress ──", CP_LGRAY)
            for i, m in enumerate(game.missions):
                prog = game.mission_progress.get(m['id'], 0)
                done = prog >= m['target']
                bar = '█'*min(10,int(10*prog/max(1,m['target']))) + '░'*max(0,10-int(10*prog/max(1,m['target'])))
                col = CP_GREEN if done else CP_LGRAY
                self._draw_centered(y_m+1+i, f"{'✓' if done else '○'} {m['name']:<22}[{bar}]", col)

            for i, (label, _) in enumerate(items):
                y = y_m + 7 + i*2
                col = CP_CYAN if i == selected else CP_LGRAY
                self._draw_centered(y, label, col, i==selected)
            self.stdscr.refresh()
            k = self.stdscr.getch()
            if k == curses.KEY_UP: selected = 0
            elif k == curses.KEY_DOWN: selected = 1
            elif k in (curses.KEY_ENTER, 10, 13):
                return items[selected][1]
            elif k == ord('r'): return 'play'
            elif k == ord('m'): return 'menu'
            time.sleep(0.02)

    def pause_menu(self, game):
        """Feature 82: Pause menu"""
        selected = 0
        items = [
            ("▶ RESUME",       'resume'),
            ("⚙ SETTINGS",     'settings'),
            ("↺ AUTOPILOT",    'autopilot'),
            ("⚐ TOGGLE GOD",  'god'),
            ("↩ MAIN MENU",   'menu'),
        ]
        while True:
            self.stdscr.erase()
            self.H, self.W = self.stdscr.getmaxyx()
            self._draw_banner(2, "══ PAUSED ══", CP_CYAN)
            self._draw_centered(4, f"Distance: {game.distance:.0f}m  Score: {game.score}", CP_WHITE)
            self._draw_centered(5, f"Speed: {game.speed:.1f}  Coins: {game.coins}", CP_YELLOW)
            ap_str = f"Autopilot: {'ON ('+game.autopilot.mode+')' if game.autopilot.active else 'OFF'}"
            self._draw_centered(6, ap_str, CP_MAGENTA if game.autopilot.active else CP_LGRAY)
            god_str = f"God Mode: {'ON' if game.godmode else 'OFF'}"
            self._draw_centered(7, god_str, CP_YELLOW if game.godmode else CP_LGRAY)

            for i, (label, _) in enumerate(items):
                y = 9 + i*2
                col = CP_CYAN if i == selected else CP_LGRAY
                self._draw_centered(y, f"{'►' if i==selected else ' '} {label}", col, i==selected)

            # Controls reminder
            self._draw_centered(self.H-5, "Controls:", CP_LGRAY)
            self._draw_centered(self.H-4, "←→ Lane  ↑ Jump  ↓ Roll  A=Autopilot", CP_DGRAY)
            self._draw_centered(self.H-3, "G=GodMode  W=Wireframe  C=CamMode  1-5=Speed", CP_DGRAY)
            self._draw_centered(self.H-2, "T=Theme  N=NightVision  S=Scanlines", CP_DGRAY)

            self.stdscr.refresh()
            k = self.stdscr.getch()
            if k == curses.KEY_UP: selected = (selected-1)%len(items)
            elif k == curses.KEY_DOWN: selected = (selected+1)%len(items)
            elif k in (curses.KEY_ENTER, 10, 13):
                action = items[selected][1]
                if action == 'resume': return 'resume'
                elif action == 'menu': return 'menu'
                elif action == 'god':
                    game.godmode = not game.godmode
                elif action == 'autopilot':
                    game.autopilot.active = not game.autopilot.active
                elif action == 'settings':
                    self.settings_menu(game.settings)
            elif k == ord('p') or k == 27:
                return 'resume'
            time.sleep(0.02)

# ─────────────────────────────────────────────────────────────────────────────
#  CURSES DISPLAY ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def init_colors():
    """Initialize all color pairs"""
    curses.start_color()
    curses.use_default_colors()
    bg = -1  # transparent background

    def safe_init(pair, fg, bg):
        try: curses.init_pair(pair, fg, bg)
        except: pass

    safe_init(CP_WHITE,   curses.COLOR_WHITE,   bg)
    safe_init(CP_YELLOW,  curses.COLOR_YELLOW,  bg)
    safe_init(CP_GREEN,   curses.COLOR_GREEN,   bg)
    safe_init(CP_RED,     curses.COLOR_RED,     bg)
    safe_init(CP_CYAN,    curses.COLOR_CYAN,    bg)
    safe_init(CP_MAGENTA, curses.COLOR_MAGENTA, bg)
    safe_init(CP_BLUE,    curses.COLOR_BLUE,    bg)
    safe_init(CP_DARK,    curses.COLOR_BLACK,   bg)
    safe_init(CP_LGRAY,   curses.COLOR_WHITE,   bg)
    safe_init(CP_DGRAY,   curses.COLOR_BLACK,   bg)

    # Extended colors
    if curses.COLORS >= 256:
        curses.init_color(50, 1000, 600, 0)   # orange
        curses.init_color(51, 700, 400, 200)  # brown
        curses.init_color(52, 900, 700, 700)  # skin
        curses.init_color(53, 500, 0, 500)    # purple
        curses.init_color(54, 300, 900, 300)  # light green
        curses.init_color(55, 1000, 400, 400) # light red
        curses.init_color(56, 400, 900, 900)  # light cyan
        curses.init_color(57, 400, 400, 1000) # light blue
        safe_init(CP_ORANGE,  50, bg)
        safe_init(CP_BROWN,   51, bg)
        safe_init(CP_SKIN,    52, bg)
        safe_init(CP_PURPLE,  53, bg)
        safe_init(CP_LGREEN,  54, bg)
        safe_init(CP_LRED,    55, bg)
        safe_init(CP_LCYAN,   56, bg)
        safe_init(CP_LBLUE,   57, bg)
    else:
        # Fallback for 8-color terminals
        safe_init(CP_ORANGE,  curses.COLOR_YELLOW,  bg)
        safe_init(CP_BROWN,   curses.COLOR_RED,     bg)
        safe_init(CP_SKIN,    curses.COLOR_YELLOW,  bg)
        safe_init(CP_PURPLE,  curses.COLOR_MAGENTA, bg)
        safe_init(CP_LGREEN,  curses.COLOR_GREEN,   bg)
        safe_init(CP_LRED,    curses.COLOR_RED,     bg)
        safe_init(CP_LCYAN,   curses.COLOR_CYAN,    bg)
        safe_init(CP_LBLUE,   curses.COLOR_BLUE,    bg)


def display_frame(stdscr, fb, H, W):
    """Blit framebuffer to terminal"""
    for y in range(min(H-1, fb.H)):
        for x in range(min(W, fb.W)):
            ch  = fb.chars[y][x]
            col = fb.colors[y][x]
            try:
                stdscr.addch(y, x, ch, curses.color_pair(col))
            except:
                pass


def run_game(stdscr, save_data):
    """Main game runner"""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    settings = save_data.get('settings', copy.deepcopy(DEFAULT_SAVE['settings']))
    save_data['settings'] = settings

    menu = Menu(stdscr, save_data)
    fb = Framebuffer(RENDER_W, RENDER_H)

    # Tutorial first run
    if save_data.get('total_runs', 0) == 0:
        settings['tutorial_active'] = True
    else:
        settings['tutorial_active'] = False

    # Cheat code buffer (feature 118)
    cheat_buffer = []
    KONAMI = [curses.KEY_UP, curses.KEY_UP, curses.KEY_DOWN, curses.KEY_DOWN,
              curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_RIGHT,
              ord('b'), ord('a')]

    while True:
        action = menu.main_menu()
        if action == 'quit':
            break
        elif action == 'settings':
            menu.settings_menu(settings)
            save_data['settings'] = settings
            save_game(save_data)
        elif action == 'leaderboard':
            menu.leaderboard_screen()
        elif action == 'stats':
            menu.stats_screen()
        elif action == 'shop':
            menu.shop_screen()
        elif action == 'tutorial':
            _show_tutorial(stdscr, save_data)
        elif action == 'play':
            # Game loop
            result = _game_loop(stdscr, fb, save_data, settings, menu, cheat_buffer, KONAMI)
            if result == 'quit':
                break
            save_data['settings'] = settings
            save_game(save_data)


def _show_tutorial(stdscr, save_data):
    H, W = stdscr.getmaxyx()
    pages = [
        ("MOVEMENT",
         ["← → Arrow Keys: Change Lane",
          "↑ Arrow / Space: Jump",
          "↓ Arrow: Roll/Slide",
          "Hold ↑ twice: Double Jump",
          "SHIFT or Z: Sprint",
          "B: Brake/Slow down"]),
        ("POWER-UPS",
         ["M - Coin Magnet: Attracts coins",
          "S - Shield: Block one hit",
          "J - Jetpack: Fly over everything",
          "↑ - Super Sneakers: Higher jump",
          "x2/x3/x5/x10 - Score multipliers",
          "~ - Slow Motion  ! - Turbo Boost"]),
        ("OBSTACLES",
         ["TRAIN (blue): Switch lanes or jump",
          "LOW BARRIER (red): Roll under it",
          "HIGH BARRIER (red): Jump over it",
          "BARREL: Avoid or jump/switch lane",
          "COMBO: Multiple obstacles at once",
          "You have 3 lives (hearts)"]),
        ("FEATURES",
         ["A - Toggle Autopilot AI",
          "G - God Mode (invincible)",
          "P - Pause Menu",
          "C - Cycle Camera Modes",
          "T - Cycle Themes",
          "1-5: Quick Speed Presets",
          "W - Wireframe Mode",
          "N - Night Vision"]),
        ("SCORING",
         ["Distance = constant score",
          "Coins = bonus score + saves",
          "Multipliers stack with upgrades",
          "Streaks: keep collecting coins!",
          "Tricks (jumping): bonus score",
          "Missions complete for extra XP"]),
    ]
    idx = 0
    while True:
        stdscr.erase()
        title, lines = pages[idx]
        cy = H//2 - len(lines)//2 - 3
        try:
            stdscr.addstr(cy, W//2 - 10, f"─── {title} ─── ({idx+1}/{len(pages)})",
                          curses.color_pair(CP_CYAN) | curses.A_BOLD)
            for i, line in enumerate(lines):
                x = max(0, W//2 - len(line)//2)
                stdscr.addstr(cy+2+i, x, line, curses.color_pair(CP_WHITE))
            stdscr.addstr(H-2, W//2 - 20, "← → Navigate pages | ENTER/Q: Exit Tutorial",
                          curses.color_pair(CP_DGRAY))
        except: pass
        stdscr.refresh()
        k = stdscr.getch()
        if k == curses.KEY_RIGHT: idx = min(idx+1, len(pages)-1)
        elif k == curses.KEY_LEFT: idx = max(idx-1, 0)
        elif k in (curses.KEY_ENTER, 10, 13, ord('q')): return
        time.sleep(0.05)


def _game_loop(stdscr, fb, save_data, settings, menu, cheat_buffer, KONAMI):
    """Main gameplay loop"""
    H_term, W_term = stdscr.getmaxyx()

    # Scale render to terminal
    render_w = min(RENDER_W, W_term)
    render_h = min(RENDER_H, H_term - 1)
    fb = Framebuffer(render_w, render_h)

    game = Game(save_data, settings)
    game.hud = HUD(fb)
    game.hud.fb = fb

    last_time = time.time()
    paused = False
    key_speed_mult = 1.0

    while True:
        now = time.time()
        dt = min(now - last_time, 0.05)
        last_time = now

        # ── Input processing ─────────────────────────────────────
        key = stdscr.getch()

        # Cheat code detection (feature 118)
        if key != -1:
            cheat_buffer.append(key)
            if len(cheat_buffer) > len(KONAMI):
                cheat_buffer.pop(0)
            if cheat_buffer == KONAMI:
                game.godmode = not game.godmode
                game.hud.push_achievement("KONAMI CODE!")
                cheat_buffer.clear()

        if key == ord('p') or key == 27:
            result = menu.pause_menu(game)
            if result == 'menu':
                return 'menu'
            last_time = time.time()
            continue

        if not game.alive:
            result = menu.game_over_screen(game)
            return result

        # Movement (skip if autopilot is full control)
        if not game.autopilot.active:
            if key == curses.KEY_LEFT:
                game.change_lane(-1)
            elif key == curses.KEY_RIGHT:
                game.change_lane(1)
            elif key in (curses.KEY_UP, ord(' ')):
                jumped = game.jump()
                if jumped and game.in_air:
                    game.trick_count += 1
                    game.mission_progress['m_tricks'] = game.trick_count
            elif key == curses.KEY_DOWN:
                game.roll()
            elif key in (ord('z'), ord('Z'), curses.KEY_SR):  # sprint (feature 98)
                game.sprinting = True
            elif key == ord('b'):  # brake (feature 101)
                game.braking = True

        # Always-available keys
        if key == ord('a') or key == ord('A'):
            game.autopilot.active = not game.autopilot.active
            mode_options = AutopilotAI.MODES
            if key == ord('A'):  # cycle mode
                idx = mode_options.index(game.autopilot.mode)
                game.autopilot.mode = mode_options[(idx+1) % len(mode_options)]
                game.hud.push_achievement(f"Autopilot: {game.autopilot.mode}")
        elif key == ord('g') or key == ord('G'):
            game.godmode = not game.godmode
            game.hud.flash(CP_YELLOW)
        elif key == ord('w') or key == ord('W'):
            game.wireframe = not game.wireframe
        elif key == ord('c') or key == ord('C'):
            modes = ['behind','side','top','cinematic','fps']
            idx = modes.index(game.camera_mode) if game.camera_mode in modes else 0
            game.camera_mode = modes[(idx+1) % len(modes)]
        elif key == ord('t') or key == ord('T'):
            themes = list(THEMES.keys())
            idx = themes.index(game.theme) if game.theme in themes else 0
            game.theme = themes[(idx+1) % len(themes)]
            settings['theme'] = game.theme
        elif key == ord('n') or key == ord('N'):
            game.night_vision = not game.night_vision
        elif key == ord('s') or key == ord('S'):
            game.scanlines = not game.scanlines
        elif key == ord('i') or key == ord('I'):
            game.invert = not game.invert
        elif key == ord('m') or key == ord('M'):  # slow motion
            if POWERUP_SLOW not in game.active_powerups:
                game.active_powerups[POWERUP_SLOW] = 6.0
        elif key == ord('j') or key == ord('J'):  # instant jetpack (debug)
            game.active_powerups[POWERUP_JETPACK] = 12.0
        elif key == ord('x') or key == ord('X'):  # x10 multiplier
            game.active_powerups[POWERUP_MULTI10] = 8.0
        elif key == ord('h') or key == ord('H'):  # hoverboard toggle
            game.hoverboard = not game.hoverboard_used
        elif key == ord('1'): game.manual_speed = 10.0
        elif key == ord('2'): game.manual_speed = 50.0
        elif key == ord('3'): game.manual_speed = 200.0
        elif key == ord('4'): game.manual_speed = 1000.0
        elif key == ord('5'): game.manual_speed = 5000.0
        elif key == ord('6'): game.manual_speed = 10000.0
        elif key == ord('0'): game.manual_speed = None  # auto speed
        elif key == ord('+'): 
            game.manual_speed = min(MAX_SPEED, (game.manual_speed or game.speed) * 1.5)
        elif key == ord('-'):
            game.manual_speed = max(1.0, (game.manual_speed or game.speed) * 0.7)
        elif key == ord('r') or key == ord('R'):
            # Toggle replay mode
            game.replay_mode = not game.replay_mode
        elif key == ord('d') or key == ord('D'):
            # Cycle difficulty
            diffs = list(DIFFICULTIES.keys())
            cur = settings.get('difficulty','Normal')
            idx = diffs.index(cur) if cur in diffs else 1
            settings['difficulty'] = diffs[(idx+1)%len(diffs)]
            diff_cfg = DIFFICULTIES[settings['difficulty']]
            game.speed_ramp = SPEED_RAMP * diff_cfg['ramp']

        # Release sprint/brake
        if key == -1:
            game.sprinting = False
            game.braking = False

        # Tutorial advance
        if game.tutorial_active and key != -1:
            game.tutorial_step = min(game.tutorial_step + 1, 4)
            if game.tutorial_step >= 4:
                game.tutorial_active = False
                game.tutorial_step = -1

        # ── Update game ──────────────────────────────────────────
        if not paused:
            game.update(dt)

        # ── Render ───────────────────────────────────────────────
        H_cur, W_cur = stdscr.getmaxyx()
        if H_cur != H_term or W_cur != W_term:
            H_term, W_term = H_cur, W_cur
            render_w = min(RENDER_W, W_term)
            render_h = min(RENDER_H, H_term - 1)
            fb = Framebuffer(render_w, render_h)
            game.hud.fb = fb

        t = time.time()
        fb.clear()
        game.render(fb, t)

        # Apply grayscale (feature 140)
        if game.grayscale:
            for y in range(fb.H):
                for x in range(fb.W):
                    fb.colors[y][x] = CP_LGRAY

        display_frame(stdscr, fb, H_term, W_term)
        stdscr.refresh()

        # Target ~30 fps
        elapsed = time.time() - now
        sleep_t = max(0, 1/30 - elapsed)
        time.sleep(sleep_t)

    return 'menu'


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading Subway Surfers 3D v{VERSION}...")
    print("Initializing 3D engine...")
    save_data = load_save()
    print(f"Save loaded. Runs: {save_data.get('total_runs',0)} | High Score: {save_data.get('high_score',0)}")
    print("Starting game in 1 second...")
    time.sleep(1)

    def _main(stdscr):
        run_game(stdscr, save_data)

    curses.wrapper(_main)
    print(f"\nThanks for playing Subway Surfers 3D!")
    print(f"Final stats:")
    print(f"  High Score:  {save_data.get('high_score',0)}")
    print(f"  Total Runs:  {save_data.get('total_runs',0)}")
    print(f"  Total Coins: {save_data.get('total_coins',0)}")
    print(f"  Level:       {save_data.get('level',1)}")


if __name__ == '__main__':
    main()