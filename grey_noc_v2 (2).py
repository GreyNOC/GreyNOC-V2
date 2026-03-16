#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║        GREY NOC V2 — NETWORK OPERATIONS CENTER       ║
║        80s Retro Terminal Edition  ▌ FULL BUILD      ║
╚══════════════════════════════════════════════════════╝
Requirements:
    pip install scapy psutil
    Run as Administrator for raw packet capture + airplane mode toggle.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import socket
import time
import math
import random
import json
import csv
import io
import os
import sys
import platform
import subprocess
from datetime import datetime
from collections import deque

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP
    HAS_SCAPY = True
except Exception:
    HAS_SCAPY = False

# ══════════════════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "bg":       "#020c02",
    "panel":    "#040e04",
    "border":   "#1a4a1a",
    "glow":     "#00ff41",
    "dim":      "#006a1a",
    "mid":      "#00c832",
    "amber":    "#ffb000",
    "red":      "#ff2020",
    "red_dim":  "#7a0000",
    "blue":     "#00cfff",
    "cyan":     "#00ffee",
    "white":    "#d0ffd0",
    "scanline": "#080f08",
    "dark":     "#010801",
    "grid":     "#0a200a",
    "map_bg":   "#010d01",
    "map_land": "#0a2a0a",
    "map_line": "#1a5a1a",
}

FM  = ("Courier New", 8)
FMB = ("Courier New", 8, "bold")
FM9 = ("Courier New", 9)
FM9B= ("Courier New", 9, "bold")
F11B= ("Courier New", 11, "bold")
F14B= ("Courier New", 14, "bold")
F16B= ("Courier New", 16, "bold")

# ══════════════════════════════════════════════════════════════════════════════
# WORLD MAP DATA  (simplified Mercator coastline polygons, normalised 0-1)
# Each entry is a list of (lon, lat) in degrees → converted at draw time
# ══════════════════════════════════════════════════════════════════════════════
# fmt: (lon -180..180, lat -90..90)
CONTINENTS = {
    "North America": [
        (-168,72),(-140,70),(-120,75),(-90,72),(-80,68),(-70,62),
        (-55,47),(-52,47),(-56,44),(-70,43),(-75,35),(-80,25),
        (-87,15),(-83,9),(-77,8),(-75,10),(-62,12),(-60,15),
        (-68,18),(-72,20),(-84,22),(-87,21),(-90,18),(-92,15),
        (-88,16),(-83,10),(-77,8),(-60,10),(-55,5),(-58,3),
        (-52,4),(-50,5),(-60,0),(-65,-5),(-70,0),(-75,0),
        (-80,0),(-85,5),(-90,10),(-95,15),(-100,20),(-105,22),
        (-110,25),(-115,27),(-118,30),(-120,33),(-122,37),
        (-124,42),(-126,48),(-130,55),(-135,58),(-138,60),
        (-140,62),(-145,60),(-148,62),(-152,58),(-155,59),
        (-160,60),(-165,63),(-168,66),(-168,72),
    ],
    "South America": [
        (-70,-55),(-65,-55),(-63,-52),(-58,-48),(-50,-28),
        (-48,-26),(-40,-20),(-35,-10),(-34,-7),(-35,-5),
        (-38,0),(-50,0),(-58,1),(-60,5),(-62,8),(-60,12),
        (-65,10),(-70,12),(-72,10),(-75,0),(-80,-3),(-80,-8),
        (-77,-14),(-75,-18),(-70,-22),(-68,-30),(-66,-33),
        (-67,-38),(-66,-43),(-65,-48),(-68,-52),(-70,-55),
    ],
    "Europe": [
        (-10,36),(0,36),(5,43),(8,44),(15,44),(18,40),(25,37),
        (28,40),(32,42),(35,48),(32,52),(22,55),(18,58),(15,58),
        (10,58),(5,57),(0,51),(-5,48),(-5,44),(-8,43),(-9,39),
        (-10,36),
    ],
    "Africa": [
        (-17,15),(-15,10),(-15,5),(-8,5),(0,5),(5,4),(10,2),
        (15,0),(20,-5),(25,-15),(30,-20),(32,-28),(35,-32),
        (30,-35),(25,-35),(18,-35),(15,-30),(12,-22),(10,-15),
        (8,-5),(5,0),(2,5),(0,8),(-5,5),(-10,5),(-15,10),
        (-17,15),(0,20),(10,22),(15,24),(20,22),(30,20),(35,22),
        (42,12),(44,10),(42,5),(40,0),(42,-10),(40,-12),
        (35,-18),(30,-20),(25,-30),(20,-34),(15,-34),(10,-30),
        (5,-25),(0,-18),(-5,-14),(-10,-8),(-15,-5),(-18,5),
        (-15,10),(-17,15),
    ],
    "Asia": [
        (25,37),(35,37),(37,36),(42,37),(48,30),(55,25),(60,22),
        (65,22),(70,20),(75,8),(80,10),(85,18),(90,22),(95,22),
        (100,3),(105,5),(110,2),(115,5),(120,8),(125,10),
        (125,15),(120,20),(118,25),(120,30),(122,32),(125,35),
        (130,35),(135,34),(140,36),(142,40),(142,46),(140,50),
        (135,48),(130,42),(128,38),(130,35),(125,30),(122,25),
        (115,20),(110,15),(105,10),(100,5),(95,0),(90,-5),
        (85,5),(80,10),(75,8),(70,8),(65,10),(60,15),(55,20),
        (50,25),(45,28),(40,30),(35,35),(30,37),(25,37),
    ],
    "Australia": [
        (114,-22),(120,-18),(125,-14),(130,-12),(136,-12),
        (140,-15),(145,-18),(150,-22),(152,-25),(153,-28),
        (152,-32),(150,-36),(147,-38),(145,-38),(143,-38),
        (140,-37),(138,-35),(136,-35),(134,-32),(130,-32),
        (128,-30),(124,-28),(122,-24),(116,-20),(114,-22),
    ],
}

# Known IP geolocation seeds (ip_prefix → approx lon,lat)
IP_GEO = {
    "8.8":    (-97, 38),    # Google US
    "8.4":    (-97, 38),
    "1.1":    (151, -33),   # Cloudflare AU
    "1.0":    (151, -33),
    "208.67": (-97, 38),    # OpenDNS
    "9.9":    (-97, 38),
    "192.168": (-100, 45),  # Private
    "10.":    (-100, 45),
    "172.16": (-100, 45),
    "103.":   (103, 1),     # SG
    "185.":   (2, 48),      # FR
    "91.":    (37, 55),     # RU
    "5.":     (15, 50),     # EU
    "77.":    (15, 50),
    "194.":   (10, 51),     # DE
    "195.":   (10, 51),
    "213.":   (10, 51),
    "217.":   (2, 48),
    "52.":    (-97, 38),    # AWS
    "54.":    (-97, 38),
    "35.":    (-97, 38),    # GCP
    "34.":    (-97, 38),
    "104.":   (-97, 38),    # CF
    "203.":   (139, 35),    # JP
    "202.":   (116, 39),    # CN
    "125.":   (116, 39),
    "60.":    (116, 39),
    "61.":    (116, 39),
    "218.":   (116, 39),
    "119.":   (103, 1),
    "27.":    (77, 28),     # IN
    "49.":    (77, 28),
    "122.":   (77, 28),
    "200.":   (-50, -15),   # BR
    "201.":   (-50, -15),
    "189.":   (-58, -12),
    "190.":   (-65, -20),
    "41.":    (30, 0),      # Africa
    "105.":   (15, 5),
    "196.":   (25, -28),
}

def ip_to_lonlat(ip):
    """Heuristic: map IP to approximate lon/lat."""
    for prefix, loc in IP_GEO.items():
        if ip.startswith(prefix):
            # jitter so dots don't overlap
            return (loc[0] + random.uniform(-3,3),
                    loc[1] + random.uniform(-3,3))
    # fallback random
    return (random.uniform(-170, 170), random.uniform(-60, 70))

def lonlat_to_xy(lon, lat, w, h):
    """Mercator-ish projection."""
    x = (lon + 180) / 360 * w
    lat_r = math.radians(max(-85, min(85, lat)))
    merc  = math.log(math.tan(math.pi/4 + lat_r/2))
    y = h/2 - merc / (2*math.pi) * h * 1.3
    return x, y

def ts():
    return datetime.now().strftime("%H:%M:%S")

def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class GreyNOC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GREY NOC V2  ▌  NETWORK OPERATIONS CENTER")
        self.configure(bg=C["bg"])
        self.geometry("1600x960")
        self.minsize(1400, 860)

        # State
        self.running       = True
        self.sniffing      = False
        self.sniff_thread  = None
        self.scan_thread   = None
        self.my_ip         = local_ip()
        self.airplane_mode = False
        self.blink_state   = True   # for blinking lights

        # Data
        self.packets       = deque(maxlen=1000)
        self.hosts         = {}      # ip → dict
        self.map_nodes     = {}      # ip → {lon,lat,age,color,pkts}
        self.bw_history    = deque(maxlen=120)
        self.bw_in         = 0
        self.bw_out        = 0
        self.pkt_count     = 0
        self.tcp_count     = 0
        self.udp_count     = 0
        self.icmp_count    = 0
        self.arp_count     = 0
        self.alert_log     = deque(maxlen=300)
        self.session_start = datetime.now()
        self.total_bytes   = 0
        self.radar_blips   = []
        self.radar_angle   = 0.0
        self.earth_angle   = 0.0
        self.map_lines     = []      # (src_xy, dst_xy, age, color)

        self._build_ui()
        self._start_loops()

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL HELPER
    # ══════════════════════════════════════════════════════════════════════════
    def _panel(self, parent, title, expand=True, width=None):
        outer = tk.Frame(parent, bg=C["border"])
        if expand:
            outer.pack(fill="both", expand=True, pady=(0,3))
        else:
            outer.pack(fill="x", pady=(0,3))
        inner = tk.Frame(outer, bg=C["panel"], padx=5, pady=3)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        hdr = tk.Frame(inner, bg=C["panel"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"▌{title}", bg=C["panel"], fg=C["glow"],
                 font=F11B, anchor="w").pack(side="left")
        tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", pady=(2,3))
        return inner

    # ══════════════════════════════════════════════════════════════════════════
    # UI BUILD
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_topbar()

        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=3, pady=3)

        # Left column (radar + earth + stats)
        left = tk.Frame(body, bg=C["bg"], width=300)
        left.pack(side="left", fill="y", padx=(0,3))
        left.pack_propagate(False)
        self._build_radar(left)
        self._build_earth(left)
        self._build_stats_panel(left)

        # Center column (world map + packet log + bw)
        center = tk.Frame(body, bg=C["bg"])
        center.pack(side="left", fill="both", expand=True, padx=(0,3))
        self._build_world_map(center)
        self._build_packet_log(center)
        self._build_bw_graph(center)

        # Right column (host tracker + port scanner)
        right = tk.Frame(body, bg=C["bg"], width=340)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_controls(right)
        self._build_host_tracker(right)
        self._build_port_scanner(right)

    # ══════════════════════════════════════════════════════════════════════════
    # TOP BAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["dark"], height=48)
        bar.pack(fill="x", padx=0, pady=0)
        bar.pack_propagate(False)

        tk.Label(bar, text="▓▒░ GREY NOC V2 ░▒▓",
                 bg=C["dark"], fg=C["glow"], font=F16B).pack(side="left", padx=10)
        tk.Label(bar, text="NETWORK OPERATIONS CENTER",
                 bg=C["dark"], fg=C["mid"], font=FM9B).pack(side="left")

        right = tk.Frame(bar, bg=C["dark"])
        right.pack(side="right", padx=8)

        # KILL SWITCH (airplane mode)
        self.btn_kill = tk.Button(
            right, text="✈ KILL SWITCH: OFF",
            bg=C["dim"], fg=C["bg"],
            font=FMB, relief="flat", padx=8, pady=4,
            activebackground=C["red"],
            cursor="hand2",
            command=self._toggle_airplane)
        self.btn_kill.pack(side="right", padx=6)

        # EXPORT (red)
        self.btn_export = tk.Button(
            right, text="⬛ EXPORT DATA",
            bg=C["red"], fg="#ffffff",
            font=FMB, relief="flat", padx=8, pady=4,
            activebackground="#cc0000",
            cursor="hand2",
            command=self._export_data)
        self.btn_export.pack(side="right", padx=4)

        # Capture toggle
        self.btn_sniff = tk.Button(
            right, text="▶ START CAPTURE",
            bg=C["border"], fg=C["glow"],
            font=FM9B, relief="flat", padx=8, pady=4,
            activebackground=C["dim"],
            cursor="hand2",
            command=self._toggle_sniff)
        self.btn_sniff.pack(side="right", padx=4)

        self.lbl_ip = tk.Label(right, text=f"HOST: {self.my_ip}",
                                bg=C["dark"], fg=C["mid"], font=FM9B)
        self.lbl_ip.pack(side="right", padx=10)

        self.lbl_time = tk.Label(right, text="", bg=C["dark"],
                                  fg=C["amber"], font=FM9B)
        self.lbl_time.pack(side="right", padx=10)

    # ══════════════════════════════════════════════════════════════════════════
    # RADAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_radar(self, parent):
        p = self._panel(parent, "RADAR SWEEP", expand=False)
        self.radar_canvas = tk.Canvas(p, width=280, height=230,
                                       bg=C["dark"], highlightthickness=0)
        self.radar_canvas.pack()

    def _draw_radar(self):
        c = self.radar_canvas
        c.delete("all")
        cx, cy, r = 140, 115, 105
        # Rings
        for i in range(1, 5):
            rr = r*i/4
            c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr, outline=C["grid"])
        # Lines
        c.create_line(cx-r,cy,cx+r,cy, fill=C["grid"])
        c.create_line(cx,cy-r,cx,cy+r, fill=C["grid"])
        for a in [45,135]:
            rad=math.radians(a)
            c.create_line(cx+r*math.cos(rad),cy+r*math.sin(rad),
                          cx-r*math.cos(rad),cy-r*math.sin(rad),
                          fill=C["grid"],dash=(2,6))
        # Trail
        for t in range(35,0,-1):
            ang = math.radians(self.radar_angle - t*2)
            g   = int(0x50*(t/35))
            col = f"#00{g:02x}00"
            x2  = cx+r*math.cos(ang); y2=cy+r*math.sin(ang)
            c.create_line(cx,cy,x2,y2,fill=col,width=2)
        # Arm
        sx=cx+r*math.cos(math.radians(self.radar_angle))
        sy=cy+r*math.sin(math.radians(self.radar_angle))
        c.create_line(cx,cy,sx,sy,fill=C["glow"],width=2)
        # Blips
        dead=[]
        for i,(ba,bd,age,col) in enumerate(self.radar_blips):
            bx=cx+bd*r*math.cos(math.radians(ba))
            by=cy+bd*r*math.sin(math.radians(ba))
            fade=max(0,1-age/90)
            if fade<0.04: dead.append(i); continue
            sz=4*fade+2
            c.create_oval(bx-sz,by-sz,bx+sz,by+sz,fill=col,outline="")
            c.create_oval(bx-sz*2,by-sz*2,bx+sz*2,by+sz*2,
                          outline=col,width=1)
        for i in reversed(dead): self.radar_blips.pop(i)
        self.radar_blips=[(a,d,age+1,col) for a,d,age,col in self.radar_blips]
        c.create_oval(cx-3,cy-3,cx+3,cy+3,fill=C["glow"],outline="")
        c.create_text(cx,cy-r-14,
                      text=f"TRACKING {len(self.hosts)} HOST(S)",
                      fill=C["amber"],font=FM)

    # ══════════════════════════════════════════════════════════════════════════
    # EARTH
    # ══════════════════════════════════════════════════════════════════════════
    def _build_earth(self, parent):
        p = self._panel(parent, "GLOBAL TRACKER", expand=False)
        self.earth_canvas = tk.Canvas(p, width=280, height=180,
                                       bg=C["dark"], highlightthickness=0)
        self.earth_canvas.pack()

    def _draw_earth(self):
        c = self.earth_canvas
        c.delete("all")
        cx,cy,r = 140,90,72
        ang = self.earth_angle
        # Glow
        for gr in range(r+16,r,-2):
            a=(gr-r)/16; v=int(0x0c*(1-a))
            col=f"#{v:02x}{v+4:02x}{v:02x}" if v>0 else C["dark"]
            c.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,outline=col)
        c.create_oval(cx-r,cy-r,cx+r,cy+r,fill="#020d04",outline=C["mid"],width=2)
        lon_rad=math.radians(ang)
        # Lat lines
        for lat_d in range(-60,90,30):
            lat=math.radians(lat_d)
            ry=r*math.cos(lat); yp=cy+r*math.sin(lat)
            if ry>2: c.create_oval(cx-ry,yp-3,cx+ry,yp+3,outline=C["grid"])
        # Lon lines
        for ld in range(0,360,30):
            lon=math.radians(ld+ang)
            pts=[]
            for la_d in range(-80,90,10):
                la=math.radians(la_d)
                x3=math.cos(la)*math.cos(lon)
                y3=math.sin(la)
                z3=math.cos(la)*math.sin(lon)
                if z3<0: continue
                pts.append((cx+r*x3,cy-r*y3))
            for i in range(len(pts)-1):
                c.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],
                              fill=C["grid"])
        # Continents (blob)
        blobs=[
            [(0.3,0.3),(0.5,0.2),(0.6,0.4),(0.4,0.6),(0.2,0.5)],
            [(-0.2,0.3),(0.0,0.1),(0.1,-0.2),(-0.1,-0.6),(-0.3,-0.3)],
            [(0.1,0.4),(0.6,0.3),(0.7,0.1),(0.5,-0.1),(0.2,0.1)],
        ]
        for blob in blobs:
            spts=[]
            for bx2,by2 in blob:
                rx2=bx2*math.cos(lon_rad)-0.2*math.sin(lon_rad)
                rz2=bx2*math.sin(lon_rad)+0.2*math.cos(lon_rad)
                if rz2<-0.1: continue
                px=cx+r*rx2; py=cy-r*by2
                if math.sqrt(rx2**2+by2**2)<1.05: spts.append((px,py))
            if len(spts)>2:
                flat=[v for pt in spts for v in pt]
                try: c.create_polygon(flat,fill=C["dim"],outline=C["mid"],smooth=True)
                except: pass
        c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=C["mid"],width=2)
        c.create_text(cx,cy+r+12,
                      text=f"ROT {ang:.1f}°  PKTS {self.pkt_count}",
                      fill=C["mid"],font=FM)

    # ══════════════════════════════════════════════════════════════════════════
    # STATS PANEL
    # ══════════════════════════════════════════════════════════════════════════
    def _build_stats_panel(self, parent):
        p = self._panel(parent, "SESSION STATISTICS", expand=True)
        self.stat_vars = {}
        rows = [
            ("PACKETS",  C["glow"]),
            ("TCP",      C["glow"]),
            ("UDP",      C["blue"]),
            ("ICMP",     C["amber"]),
            ("ARP",      C["mid"]),
            ("HOSTS",    C["cyan"]),
            ("TOTAL BW", C["glow"]),
            ("BW ↓",     C["glow"]),
            ("BW ↑",     C["blue"]),
            ("CPU %",    C["amber"]),
            ("MEM %",    C["amber"]),
            ("UPTIME",   C["mid"]),
            ("ALERTS",   C["red"]),
        ]
        for key, col in rows:
            row = tk.Frame(p, bg=C["panel"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f"{key:<11}", bg=C["panel"], fg=C["dim"],
                     font=FM, anchor="w").pack(side="left")
            v = tk.Label(row, text="---", bg=C["panel"], fg=col, font=FMB,
                         anchor="e")
            v.pack(side="right")
            self.stat_vars[key] = v

        # Status LEDs
        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", pady=4)
        led_row = tk.Frame(p, bg=C["panel"])
        led_row.pack(fill="x")
        self.leds = {}
        for name, col in [("NET",C["glow"]),("SCAN",C["amber"]),("ALERT",C["red"])]:
            sub = tk.Frame(led_row, bg=C["panel"])
            sub.pack(side="left", expand=True)
            led = tk.Canvas(sub, width=14, height=14, bg=C["panel"],
                            highlightthickness=0)
            led.pack(side="left", padx=2)
            tk.Label(sub, text=name, bg=C["panel"], fg=C["dim"],
                     font=FM).pack(side="left")
            self.leds[name] = (led, col)

    def _update_stats(self):
        elapsed = (datetime.now() - self.session_start)
        h,rem = divmod(int(elapsed.total_seconds()),3600)
        m,s   = divmod(rem,60)

        self.stat_vars["PACKETS"].config(text=str(self.pkt_count))
        self.stat_vars["TCP"].config(text=str(self.tcp_count))
        self.stat_vars["UDP"].config(text=str(self.udp_count))
        self.stat_vars["ICMP"].config(text=str(self.icmp_count))
        self.stat_vars["ARP"].config(text=str(self.arp_count))
        self.stat_vars["HOSTS"].config(text=str(len(self.hosts)))
        self.stat_vars["TOTAL BW"].config(
            text=f"{self.total_bytes/1048576:.2f}MB")
        self.stat_vars["UPTIME"].config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.stat_vars["ALERTS"].config(text=str(len(self.alert_log)))

        if self.bw_history:
            last=self.bw_history[-1]
            self.stat_vars["BW ↓"].config(text=f"{last[0]/1024:.1f}KB/s")
            self.stat_vars["BW ↑"].config(text=f"{last[1]/1024:.1f}KB/s")

        if HAS_PSUTIL:
            cpu=psutil.cpu_percent()
            mem=psutil.virtual_memory().percent
            self.stat_vars["CPU %"].config(
                text=f"{cpu:.1f}%",
                fg=C["red"] if cpu>80 else C["amber"] if cpu>50 else C["glow"])
            self.stat_vars["MEM %"].config(
                text=f"{mem:.1f}%",
                fg=C["red"] if mem>85 else C["amber"] if mem>65 else C["glow"])

        # Blink LEDs
        self.blink_state = not self.blink_state
        self._blink_led("NET",   self.sniffing,       C["glow"])
        self._blink_led("SCAN",  self.scan_thread and self.scan_thread.is_alive(),
                        C["amber"])
        self._blink_led("ALERT", len(self.alert_log)>0, C["red"])

    def _blink_led(self, name, active, on_col):
        led, col = self.leds[name]
        led.delete("all")
        if active and self.blink_state:
            fill = on_col
        elif active:
            fill = C["dim"]
        else:
            fill = "#111111"
        led.create_oval(2,2,12,12,fill=fill,outline=on_col if active else "#222")

    # ══════════════════════════════════════════════════════════════════════════
    # WORLD MAP
    # ══════════════════════════════════════════════════════════════════════════
    def _build_world_map(self, parent):
        p = self._panel(parent, "GLOBAL CONNECTION MAP", expand=False)
        self.map_canvas = tk.Canvas(p, height=280, bg=C["map_bg"],
                                     highlightthickness=0)
        self.map_canvas.pack(fill="x", pady=2)
        self.map_canvas.bind("<Configure>", lambda e: self._draw_world_map())

        legend = tk.Frame(p, bg=C["panel"])
        legend.pack(fill="x")
        for txt, col in [("● TCP",C["glow"]),("● UDP",C["blue"]),
                          ("● ICMP",C["amber"]),("● ARP",C["mid"]),
                          ("● ALERT",C["red"])]:
            tk.Label(legend, text=txt, bg=C["panel"], fg=col,
                     font=FM).pack(side="left", padx=6)

    def _draw_world_map(self):
        c = self.map_canvas
        c.delete("all")
        W = c.winfo_width() or 800
        H = 280

        # Background grid
        for lon in range(-180, 181, 30):
            x,_ = lonlat_to_xy(lon, 0, W, H)
            c.create_line(x, 0, x, H, fill=C["grid"], dash=(2,6))
        for lat in range(-60, 91, 30):
            _, y = lonlat_to_xy(0, lat, W, H)
            c.create_line(0, y, W, y, fill=C["grid"], dash=(2,6))

        # Draw continents
        for name, pts in CONTINENTS.items():
            screen=[]
            for lon,lat in pts:
                x,y = lonlat_to_xy(lon,lat,W,H)
                screen.append(x); screen.append(y)
            if len(screen)>=6:
                try:
                    c.create_polygon(screen, fill=C["map_land"],
                                     outline=C["map_line"], width=1, smooth=False)
                except: pass

        # Connection lines (fade)
        dead=[]
        for i,(sxy,dxy,age,col) in enumerate(self.map_lines):
            fade=max(0,1-age/60)
            if fade<0.05: dead.append(i); continue
            g=int(int(col[3:5],16)*fade) if len(col)==7 else 0
            # Draw arc-ish line
            sx,sy=sxy; dx,dy=dxy
            mx=(sx+dx)/2; my=min(sy,dy)-20*fade
            # bezier approx with 2 lines
            c.create_line(sx,sy,mx,my,dx,dy,
                          fill=col,width=max(1,int(2*fade)),smooth=True)
        for i in reversed(dead): self.map_lines.pop(i)
        self.map_lines=[(s,d,age+1,col) for s,d,age,col in self.map_lines]

        # Host blips (blinking)
        now_blink = self.blink_state
        for ip, node in list(self.map_nodes.items()):
            x,y = lonlat_to_xy(node["lon"], node["lat"], W, H)
            col = node["color"]
            age = node["age"]
            # Outer ring (fades with inactivity)
            fade = min(1.0, node["pkts"]/5)
            r_out = 6+fade*4
            if now_blink or age < 5:
                c.create_oval(x-r_out,y-r_out,x+r_out,y+r_out,
                              outline=col, width=1)
            # Inner dot (always on)
            c.create_oval(x-3,y-3,x+3,y+3, fill=col, outline="")
            # Label for active nodes
            if node["pkts"] > 3:
                c.create_text(x+6, y-6, text=ip.split(".")[-1],
                              fill=col, font=FM, anchor="w")
            node["age"] = age + 1

        # My location dot
        my_lon, my_lat = ip_to_lonlat(self.my_ip)
        mx, my2 = lonlat_to_xy(my_lon, my_lat, W, H)
        # Pulsing ring for self
        pulse = 8 + 4*math.sin(time.time()*3)
        c.create_oval(mx-pulse,my2-pulse,mx+pulse,my2+pulse,
                      outline=C["cyan"], width=2)
        c.create_oval(mx-4,my2-4,mx+4,my2+4,fill=C["cyan"],outline="")
        c.create_text(mx+8,my2-8,text="YOU",fill=C["cyan"],font=FMB,anchor="w")

        # Scanlines
        for y in range(0,H,3):
            c.create_line(0,y,W,y,fill=C["scanline"],stipple="gray25")

        # Corner labels
        c.create_text(4,4,text=f"NODES: {len(self.map_nodes)}",
                      fill=C["amber"],font=FM,anchor="nw")
        c.create_text(W-4,4,
                      text=f"CONNECTIONS: {len(self.map_lines)}",
                      fill=C["amber"],font=FM,anchor="ne")

    def _register_map_node(self, ip, color):
        if ip.startswith(("127.","0.")):
            return
        if ip not in self.map_nodes:
            lon,lat = ip_to_lonlat(ip)
            self.map_nodes[ip] = {
                "lon":lon,"lat":lat,"age":0,"color":color,"pkts":0
            }
        self.map_nodes[ip]["pkts"] += 1
        self.map_nodes[ip]["age"]   = 0
        self.map_nodes[ip]["color"] = color

    def _add_map_connection(self, src, dst, color):
        W = self.map_canvas.winfo_width() or 800
        H = 280
        if src not in self.map_nodes or dst not in self.map_nodes:
            return
        sxy = lonlat_to_xy(self.map_nodes[src]["lon"],
                            self.map_nodes[src]["lat"], W, H)
        dxy = lonlat_to_xy(self.map_nodes[dst]["lon"],
                            self.map_nodes[dst]["lat"], W, H)
        if len(self.map_lines) < 200:
            self.map_lines.append((sxy, dxy, 0, color))

    # ══════════════════════════════════════════════════════════════════════════
    # PACKET LOG
    # ══════════════════════════════════════════════════════════════════════════
    def _build_packet_log(self, parent):
        p = self._panel(parent, "LIVE PACKET CAPTURE", expand=False)
        hdr = tk.Frame(p, bg=C["panel"])
        hdr.pack(fill="x")
        for txt,w in [("TIME",8),("SRC",18),("DST",18),("PROTO",7),
                      ("LEN",6),("INFO",28)]:
            tk.Label(hdr,text=txt,width=w,bg=C["panel"],fg=C["amber"],
                     font=FM,anchor="w").pack(side="left")
        tk.Frame(p,bg=C["border"],height=1).pack(fill="x",pady=2)
        self.pkt_log = scrolledtext.ScrolledText(
            p, height=9, bg=C["bg"], fg=C["glow"], font=FM,
            relief="flat", wrap="none", state="disabled",
            insertbackground=C["glow"])
        self.pkt_log.pack(fill="x")
        for tag,col in [("tcp",C["glow"]),("udp",C["blue"]),
                         ("icmp",C["amber"]),("arp",C["mid"]),
                         ("other",C["dim"])]:
            self.pkt_log.tag_config(tag, foreground=col)
        btn_row = tk.Frame(p, bg=C["panel"])
        btn_row.pack(fill="x", pady=2)
        tk.Button(btn_row, text="⚡ SIMULATE TRAFFIC",
                  bg=C["border"], fg=C["amber"], font=FM,
                  relief="flat", command=self._simulate_traffic,
                  cursor="hand2").pack(side="right")
        tk.Button(btn_row, text="⬜ CLEAR LOG",
                  bg=C["border"], fg=C["dim"], font=FM,
                  relief="flat", command=self._clear_log,
                  cursor="hand2").pack(side="right", padx=4)

    def _log_packet(self, time_s, src, dst, proto, length, info, tag="other"):
        line = f"{time_s:<9}{src:<19}{dst:<19}{proto:<8}{length:<7}{info}\n"
        self.pkt_log.config(state="normal")
        self.pkt_log.insert("end", line, tag)
        lines = int(self.pkt_log.index("end-1c").split(".")[0])
        if lines > 400:
            self.pkt_log.delete("1.0","60.0")
        self.pkt_log.see("end")
        self.pkt_log.config(state="disabled")

    def _clear_log(self):
        self.pkt_log.config(state="normal")
        self.pkt_log.delete("1.0","end")
        self.pkt_log.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    # BANDWIDTH GRAPH
    # ══════════════════════════════════════════════════════════════════════════
    def _build_bw_graph(self, parent):
        p = self._panel(parent, "BANDWIDTH MONITOR", expand=False)
        self.bw_canvas = tk.Canvas(p, height=100, bg=C["dark"],
                                    highlightthickness=0)
        self.bw_canvas.pack(fill="x", pady=2)

    def _draw_bw(self):
        c = self.bw_canvas
        c.delete("all")
        W = c.winfo_width() or 700
        H = 100
        pad = 28
        for gy in range(0,H,20):
            c.create_line(pad,gy,W,gy,fill=C["grid"],dash=(2,4))
        if not self.bw_history:
            c.create_text(W//2,H//2,text="AWAITING DATA…",
                          fill=C["dim"],font=FM9)
            return
        mx = max((max(x) for x in self.bw_history),default=1) or 1
        n  = len(self.bw_history)
        step = (W-pad)/max(n,1)
        def pts(idx):
            return [(pad+i*step, H-(pair[idx]/mx)*(H-8))
                    for i,pair in enumerate(self.bw_history)]
        def draw_area(pts_list, col):
            if len(pts_list)<2: return
            poly=list(pts_list[0])
            for pp in pts_list[1:]: poly+=list(pp)
            poly+=[pts_list[-1][0],H,pts_list[0][0],H]
            c.create_polygon(poly,fill=col,outline="",stipple="gray25")
            for i in range(len(pts_list)-1):
                c.create_line(pts_list[i][0],pts_list[i][1],
                              pts_list[i+1][0],pts_list[i+1][1],
                              fill=col,width=2)
        draw_area(pts(0), C["glow"])
        draw_area(pts(1), C["blue"])
        c.create_text(2,6,text="↓IN",fill=C["glow"],font=FM,anchor="w")
        c.create_text(2,18,text="↑OUT",fill=C["blue"],font=FM,anchor="w")
        last=self.bw_history[-1]
        c.create_text(W-2,6,text=f"{last[0]/1024:.1f}KB/s",
                      fill=C["glow"],font=FM,anchor="e")
        c.create_text(W-2,18,text=f"{last[1]/1024:.1f}KB/s",
                      fill=C["blue"],font=FM,anchor="e")
        for y in range(0,H,3):
            c.create_line(0,y,W,y,fill=C["scanline"],stipple="gray50")

    # ══════════════════════════════════════════════════════════════════════════
    # CONTROLS (kill switch + export live in topbar; here we add extra info)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_controls(self, parent):
        p = self._panel(parent, "SYSTEM CONTROL", expand=False)

        self.lbl_airplane = tk.Label(
            p, text="NETWORK:  ONLINE",
            bg=C["panel"], fg=C["glow"], font=FM9B)
        self.lbl_airplane.pack(fill="x", pady=2)

        info_row = tk.Frame(p, bg=C["panel"])
        info_row.pack(fill="x", pady=2)
        tk.Label(info_row, text="KILL SWITCH controls Windows\nAirplane Mode via netsh/devcon.",
                 bg=C["panel"], fg=C["dim"], font=FM,
                 justify="left").pack(side="left")

        self.btn_kill2 = tk.Button(
            p, text="✈  TOGGLE AIRPLANE MODE",
            bg=C["red_dim"], fg=C["red"],
            font=FM9B, relief="flat", padx=6, pady=5,
            activebackground=C["red"],
            activeforeground=C["bg"],
            cursor="hand2",
            command=self._toggle_airplane)
        self.btn_kill2.pack(fill="x", pady=4)

        tk.Frame(p, bg=C["border"], height=1).pack(fill="x", pady=2)
        tk.Label(p, text="EXPORT OPTIONS:", bg=C["panel"],
                 fg=C["amber"], font=FM).pack(anchor="w")

        for txt, cmd in [("⬛ EXPORT CSV",   lambda: self._export_data("csv")),
                          ("⬛ EXPORT JSON",  lambda: self._export_data("json")),
                          ("⬛ EXPORT TXT",   lambda: self._export_data("txt"))]:
            tk.Button(p, text=txt, bg=C["red"], fg="#fff",
                      font=FM, relief="flat", pady=3,
                      cursor="hand2",
                      activebackground="#aa0000",
                      command=cmd).pack(fill="x", pady=1)

    # ══════════════════════════════════════════════════════════════════════════
    # HOST TRACKER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_host_tracker(self, parent):
        p = self._panel(parent, "HOST TRACKER", expand=True)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("NOC.Treeview",
                        background=C["bg"], foreground=C["glow"],
                        fieldbackground=C["bg"], font=FM, rowheight=16)
        style.configure("NOC.Treeview.Heading",
                        background=C["border"], foreground=C["amber"],
                        font=FM)
        style.map("NOC.Treeview",
                  background=[("selected",C["dim"])],
                  foreground=[("selected",C["bg"])])
        cols = ("IP","PKTS","BYTES","PROTO","LAST")
        self.host_tree = ttk.Treeview(p, columns=cols, show="headings",
                                       style="NOC.Treeview", height=10)
        for col,w in zip(cols,[110,50,65,50,65]):
            self.host_tree.heading(col,text=col)
            self.host_tree.column(col,width=w,anchor="w")
        sb = ttk.Scrollbar(p, orient="vertical",
                            command=self.host_tree.yview)
        self.host_tree.configure(yscrollcommand=sb.set)
        self.host_tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _update_hosts(self):
        for r in self.host_tree.get_children():
            self.host_tree.delete(r)
        for ip,info in sorted(self.hosts.items(),
                              key=lambda x:x[1]["pkts"],reverse=True)[:60]:
            self.host_tree.insert("","end",values=(
                ip, info["pkts"],
                f"{info['bytes']//1024}K",
                info.get("proto","?"),
                info["last_seen"]))

    # ══════════════════════════════════════════════════════════════════════════
    # PORT SCANNER
    # ══════════════════════════════════════════════════════════════════════════
    def _build_port_scanner(self, parent):
        p = self._panel(parent, "PORT SCANNER", expand=False)
        row=tk.Frame(p,bg=C["panel"]); row.pack(fill="x",pady=2)
        tk.Label(row,text="TARGET:",bg=C["panel"],fg=C["amber"],font=FM).pack(side="left")
        self.scan_target=tk.Entry(row,bg=C["bg"],fg=C["glow"],font=FM9,
                                   width=18,insertbackground=C["glow"],
                                   relief="flat",highlightthickness=1,
                                   highlightcolor=C["border"])
        self.scan_target.insert(0,self.my_ip)
        self.scan_target.pack(side="left",padx=4)

        row2=tk.Frame(p,bg=C["panel"]); row2.pack(fill="x",pady=2)
        tk.Label(row2,text="PORTS:",bg=C["panel"],fg=C["amber"],font=FM).pack(side="left")
        self.scan_ports=tk.Entry(row2,bg=C["bg"],fg=C["glow"],font=FM9,
                                  width=18,insertbackground=C["glow"],
                                  relief="flat",highlightthickness=1,
                                  highlightcolor=C["border"])
        self.scan_ports.insert(0,"22,80,443,3389,8080,445,21,25,53,3306")
        self.scan_ports.pack(side="left",padx=4)

        self.btn_scan=tk.Button(p,text="▶ SCAN TARGET",
                                 bg=C["border"],fg=C["glow"],font=FM9B,
                                 relief="flat",activebackground=C["dim"],
                                 cursor="hand2",command=self._start_scan)
        self.btn_scan.pack(fill="x",pady=3)
        self.scan_progress=tk.Label(p,text="READY",bg=C["panel"],
                                     fg=C["dim"],font=FM)
        self.scan_progress.pack(fill="x")
        self.scan_log=scrolledtext.ScrolledText(
            p,height=7,bg=C["bg"],fg=C["glow"],font=FM,
            relief="flat",state="disabled",insertbackground=C["glow"])
        self.scan_log.pack(fill="both",expand=True,pady=2)
        self.scan_log.tag_config("open",  foreground=C["glow"])
        self.scan_log.tag_config("closed",foreground=C["dim"])
        self.scan_log.tag_config("info",  foreground=C["amber"])

    def _start_scan(self):
        if self.scan_thread and self.scan_thread.is_alive(): return
        target=self.scan_target.get().strip()
        try: ports=[int(p.strip()) for p in self.scan_ports.get().split(",") if p.strip()]
        except: ports=[80,443,22,3389]
        self.scan_log.config(state="normal")
        self.scan_log.delete("1.0","end")
        self.scan_log.insert("end",f"[{ts()}] SCANNING {target}...\n","info")
        self.scan_log.config(state="disabled")
        self.btn_scan.config(text="⏳ SCANNING…",state="disabled")
        self._add_alert(f"SCAN started on {target}")
        self.scan_thread=threading.Thread(
            target=self._scan_worker,args=(target,ports),daemon=True)
        self.scan_thread.start()

    def _scan_worker(self,target,ports):
        open_p=[]
        for i,port in enumerate(ports):
            self.after(0,lambda i=i,t=len(ports),p=port:
                       self.scan_progress.config(
                           text=f"PORT {p} ({i+1}/{t})",fg=C["amber"]))
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(0.5)
                r=s.connect_ex((target,port)); s.close()
                if r==0:
                    svc=self._svc(port); open_p.append(port)
                    self.after(0,lambda p=port,sv=svc:
                               self._scan_log_add(f"[OPEN]   {p:<6} {sv}\n","open"))
                else:
                    self.after(0,lambda p=port:
                               self._scan_log_add(f"[CLOSED] {p}\n","closed"))
            except:
                self.after(0,lambda p=port:
                           self._scan_log_add(f"[ERROR]  {p}\n","closed"))
        self.after(0,lambda:self._scan_log_add(
            f"\n── DONE: {len(open_p)}/{len(ports)} OPEN ──\n","info"))
        self.after(0,lambda:self.btn_scan.config(text="▶ SCAN TARGET",state="normal"))
        self.after(0,lambda:self.scan_progress.config(
            text=f"DONE — {len(open_p)} open",fg=C["glow"]))
        self._add_alert(f"SCAN complete: {len(open_p)} open on {target}")
        if open_p:
            a=random.uniform(0,360); d=random.uniform(0.3,0.9)
            self.radar_blips.append((a,d,0,C["red"]))

    def _scan_log_add(self,text,tag):
        self.scan_log.config(state="normal")
        self.scan_log.insert("end",text,tag)
        self.scan_log.see("end")
        self.scan_log.config(state="disabled")

    def _svc(self,port):
        return {21:"FTP",22:"SSH",23:"TELNET",25:"SMTP",53:"DNS",
                80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",
                139:"NETBIOS",3306:"MYSQL",3389:"RDP",5432:"PGSQL",
                6379:"REDIS",8080:"HTTP-ALT",8443:"HTTPS-ALT",
                27017:"MONGO"}.get(port,"UNKNOWN")

    # ══════════════════════════════════════════════════════════════════════════
    # AIRPLANE MODE / KILL SWITCH
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_airplane(self):
        self.airplane_mode = not self.airplane_mode
        if self.airplane_mode:
            self._enable_airplane()
        else:
            self._disable_airplane()

    def _enable_airplane(self):
        self._add_alert("KILL SWITCH: Enabling Airplane Mode…")
        threading.Thread(target=self._airplane_on, daemon=True).start()

    def _disable_airplane(self):
        self._add_alert("KILL SWITCH: Disabling Airplane Mode…")
        threading.Thread(target=self._airplane_off, daemon=True).start()

    def _airplane_on(self):
        """Disable all network adapters on Windows."""
        ok = False
        try:
            if platform.system() == "Windows":
                # Disable WiFi via netsh
                r1 = subprocess.run(
                    ["netsh", "interface", "set", "interface",
                     "Wi-Fi", "admin=disable"],
                    capture_output=True, timeout=10)
                # Also disable Ethernet as a broad kill
                r2 = subprocess.run(
                    ["netsh", "interface", "set", "interface",
                     "Ethernet", "admin=disable"],
                    capture_output=True, timeout=10)
                ok = True
            else:
                subprocess.run(["nmcli", "radio", "all", "off"],
                                timeout=10)
                ok = True
        except Exception as e:
            self.after(0,lambda:self._add_alert(f"KILL ERR: {e}"))
            self.airplane_mode = False

        if ok:
            self.after(0, self._update_kill_ui)
            self.after(0,lambda:self._add_alert(
                "KILL SWITCH: ✈ AIRPLANE MODE ON — All adapters disabled"))

    def _airplane_off(self):
        """Re-enable network adapters."""
        ok = False
        try:
            if platform.system() == "Windows":
                subprocess.run(
                    ["netsh","interface","set","interface",
                     "Wi-Fi","admin=enable"],
                    capture_output=True,timeout=10)
                subprocess.run(
                    ["netsh","interface","set","interface",
                     "Ethernet","admin=enable"],
                    capture_output=True,timeout=10)
                ok = True
            else:
                subprocess.run(["nmcli","radio","all","on"],timeout=10)
                ok = True
        except Exception as e:
            self.after(0,lambda:self._add_alert(f"KILL ERR: {e}"))
            self.airplane_mode = True

        if ok:
            self.after(0, self._update_kill_ui)
            self.after(0,lambda:self._add_alert(
                "KILL SWITCH: ✈ AIRPLANE MODE OFF — Adapters restored"))

    def _update_kill_ui(self):
        if self.airplane_mode:
            self.btn_kill.config(text="✈ KILL SWITCH: ON",
                                  bg=C["red"], fg="#ffffff")
            self.btn_kill2.config(bg=C["red"],fg="#ffffff",
                                   text="✈ AIRPLANE MODE: ACTIVE")
            self.lbl_airplane.config(text="NETWORK:  ✈ OFFLINE",fg=C["red"])
        else:
            self.btn_kill.config(text="✈ KILL SWITCH: OFF",
                                  bg=C["dim"], fg=C["bg"])
            self.btn_kill2.config(bg=C["red_dim"],fg=C["red"],
                                   text="✈ TOGGLE AIRPLANE MODE")
            self.lbl_airplane.config(text="NETWORK:  ONLINE",fg=C["glow"])

    # ══════════════════════════════════════════════════════════════════════════
    # EXPORT
    # ══════════════════════════════════════════════════════════════════════════
    def _export_data(self, fmt=None):
        if fmt is None:
            fmt = "csv"

        filetypes = {
            "csv":  [("CSV files","*.csv"),("All files","*.*")],
            "json": [("JSON files","*.json"),("All files","*.*")],
            "txt":  [("Text files","*.txt"),("All files","*.*")],
        }
        defext = {"csv":".csv","json":".json","txt":".txt"}
        path = filedialog.asksaveasfilename(
            title="Export NOC Data",
            defaultextension=defext[fmt],
            filetypes=filetypes[fmt],
            initialfile=f"grey_noc_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{defext[fmt]}")
        if not path:
            return

        elapsed = datetime.now() - self.session_start
        data = {
            "export_time":   datetime.now().isoformat(),
            "session_start": self.session_start.isoformat(),
            "uptime_seconds":int(elapsed.total_seconds()),
            "local_ip":      self.my_ip,
            "total_packets": self.pkt_count,
            "tcp_packets":   self.tcp_count,
            "udp_packets":   self.udp_count,
            "icmp_packets":  self.icmp_count,
            "arp_packets":   self.arp_count,
            "total_bytes":   self.total_bytes,
            "host_count":    len(self.hosts),
            "hosts": {
                ip: {
                    "packets":   v["pkts"],
                    "bytes":     v["bytes"],
                    "protocol":  v.get("proto","?"),
                    "last_seen": v["last_seen"],
                }
                for ip,v in self.hosts.items()
            },
            "alerts": list(self.alert_log),
            "map_nodes": {
                ip: {"lon":v["lon"],"lat":v["lat"],"packets":v["pkts"]}
                for ip,v in self.map_nodes.items()
            },
            "bandwidth_history": list(self.bw_history),
        }

        try:
            if fmt == "json":
                with open(path,"w") as f:
                    json.dump(data, f, indent=2)

            elif fmt == "csv":
                with open(path,"w",newline="") as f:
                    w = csv.writer(f)
                    w.writerow(["GREY NOC V2 — EXPORT",
                                datetime.now().isoformat()])
                    w.writerow([])
                    w.writerow(["SESSION SUMMARY"])
                    for k,v in list(data.items())[:9]:
                        w.writerow([k,v])
                    w.writerow([])
                    w.writerow(["HOST TRACKER"])
                    w.writerow(["IP","PACKETS","BYTES","PROTOCOL","LAST SEEN"])
                    for ip,v in data["hosts"].items():
                        w.writerow([ip,v["packets"],v["bytes"],
                                    v["protocol"],v["last_seen"]])
                    w.writerow([])
                    w.writerow(["ALERT LOG"])
                    for a in data["alerts"]:
                        w.writerow([a])
                    w.writerow([])
                    w.writerow(["MAP NODES"])
                    w.writerow(["IP","LON","LAT","PACKETS"])
                    for ip,v in data["map_nodes"].items():
                        w.writerow([ip,v["lon"],v["lat"],v["packets"]])

            elif fmt == "txt":
                lines = [
                    "="*60,
                    "  GREY NOC V2 — NETWORK OPERATIONS CENTER",
                    f"  Export: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "="*60,"",
                    "SESSION SUMMARY",
                    "-"*40,
                    f"  Local IP      : {self.my_ip}",
                    f"  Session Start : {self.session_start.strftime('%H:%M:%S')}",
                    f"  Uptime        : {int(elapsed.total_seconds())}s",
                    f"  Total Packets : {self.pkt_count}",
                    f"    TCP         : {self.tcp_count}",
                    f"    UDP         : {self.udp_count}",
                    f"    ICMP        : {self.icmp_count}",
                    f"    ARP         : {self.arp_count}",
                    f"  Total Bytes   : {self.total_bytes:,}",
                    f"  Hosts Seen    : {len(self.hosts)}","",
                    "HOST TRACKER",
                    "-"*40,
                ]
                for ip,v in sorted(self.hosts.items(),
                                   key=lambda x:x[1]["pkts"],reverse=True):
                    lines.append(
                        f"  {ip:<18} pkts={v['pkts']:<6} "
                        f"bytes={v['bytes']//1024}KB  "
                        f"proto={v.get('proto','?'):<5} "
                        f"last={v['last_seen']}")
                lines += ["","ALERT LOG","-"*40]
                lines += [f"  {a}" for a in list(self.alert_log)[:50]]
                lines += ["","="*60,"  END OF REPORT","="*60]
                with open(path,"w") as f:
                    f.write("\n".join(lines))

            self._add_alert(f"EXPORT: Saved {fmt.upper()} → {os.path.basename(path)}")
            messagebox.showinfo("Export Complete",
                                f"Data exported to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))
            self._add_alert(f"EXPORT ERR: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    # CAPTURE / SIMULATION
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_sniff(self):
        if not self.sniffing: self._start_sniff()
        else:                 self._stop_sniff()

    def _start_sniff(self):
        if not HAS_SCAPY:
            self._add_alert("Scapy unavailable — simulation mode")
            self._simulate_traffic(); return
        self.sniffing = True
        self.btn_sniff.config(text="⏹ STOP CAPTURE",fg=C["red"])
        self._add_alert(f"Capture started on {self.my_ip}")
        self.sniff_thread = threading.Thread(
            target=lambda: sniff(prn=self._handle_packet, store=False,
                                  stop_filter=lambda x: not self.sniffing),
            daemon=True)
        self.sniff_thread.start()

    def _stop_sniff(self):
        self.sniffing = False
        self.btn_sniff.config(text="▶ START CAPTURE",fg=C["glow"])
        self._add_alert("Capture stopped")

    def _handle_packet(self, pkt):
        try:
            self.pkt_count += 1
            length = len(pkt)
            self.total_bytes += length
            src = dst = proto = info = ""
            tag = "other"
            if IP in pkt:
                src=pkt[IP].src; dst=pkt[IP].dst
                if TCP in pkt:
                    proto="TCP"; tag="tcp"; self.tcp_count+=1
                    info=f":{pkt[TCP].sport}→{pkt[TCP].dport}"
                    col=C["glow"]
                elif UDP in pkt:
                    proto="UDP"; tag="udp"; self.udp_count+=1
                    info=f":{pkt[UDP].sport}→{pkt[UDP].dport}"
                    col=C["blue"]
                elif ICMP in pkt:
                    proto="ICMP"; tag="icmp"; self.icmp_count+=1
                    info=f"type={pkt[ICMP].type}"; col=C["amber"]
                else:
                    proto="IP"; col=C["dim"]
            elif ARP in pkt:
                src=pkt[ARP].psrc; dst=pkt[ARP].pdst
                proto="ARP"; tag="arp"; self.arp_count+=1
                info=f"who-has {dst}"; col=C["mid"]
            else: return

            for ip in [src,dst]:
                if ip not in self.hosts:
                    self.hosts[ip]={"pkts":0,"bytes":0,"last_seen":"","proto":proto}
                self.hosts[ip]["pkts"]+=1
                self.hosts[ip]["bytes"]+=length
                self.hosts[ip]["last_seen"]=ts()
                self.hosts[ip]["proto"]=proto

            self.bw_in += length
            self._register_map_node(src, col)
            self._register_map_node(dst, col)

            if random.random()<0.3:
                self._add_map_connection(src,dst,col)

            if src not in self.map_nodes or self.hosts[src]["pkts"]==1:
                a=random.uniform(0,360); d=random.uniform(0.2,0.95)
                self.radar_blips.append((a,d,0,col))

            self.after(0,lambda:self._log_packet(ts(),src,dst,proto,
                                                  str(length),info,tag))
        except: pass

    def _simulate_traffic(self):
        def _sim():
            PROTOS=[("TCP",C["glow"],"tcp"),("UDP",C["blue"],"udp"),
                    ("ICMP",C["amber"],"icmp"),("ARP",C["mid"],"arp")]
            HOSTS=["192.168.1.1","192.168.1.100","10.0.0.1",
                   "8.8.8.8","8.8.4.4","1.1.1.1","1.0.0.1",
                   "52.94.228.167","35.190.0.1","104.18.20.15",
                   "185.199.108.153","91.108.56.180","203.0.113.5",
                   "125.209.222.141","27.107.0.1","200.143.0.1",
                   "41.58.0.1","103.31.4.1","60.28.202.119"]
            while self.running:
                src=random.choice(HOSTS); dst=random.choice(HOSTS)
                if src==dst: continue
                proto,col,tag=random.choice(PROTOS)
                sport=random.randint(1024,65535)
                dport=random.choice([80,443,22,53,3389,8080,25,110,445])
                size=random.randint(40,1500)
                info=f":{sport}→{dport}"

                self.pkt_count+=1
                self.total_bytes+=size
                if tag=="tcp": self.tcp_count+=1
                elif tag=="udp": self.udp_count+=1
                elif tag=="icmp": self.icmp_count+=1
                elif tag=="arp": self.arp_count+=1

                for ip in [src,dst]:
                    if ip not in self.hosts:
                        self.hosts[ip]={"pkts":0,"bytes":0,
                                         "last_seen":"","proto":proto}
                    self.hosts[ip]["pkts"]+=1
                    self.hosts[ip]["bytes"]+=size
                    self.hosts[ip]["last_seen"]=ts()
                    self.hosts[ip]["proto"]=proto

                self.bw_in+=size*random.uniform(0.4,1.0)
                self.bw_out+=size*random.uniform(0.1,0.5)

                self._register_map_node(src,col)
                self._register_map_node(dst,col)
                if random.random()<0.25:
                    self._add_map_connection(src,dst,col)

                if random.random()<0.12:
                    a=random.uniform(0,360); d=random.uniform(0.2,0.95)
                    self.radar_blips.append((a,d,0,col))

                self.after(0,lambda s=src,d2=dst,pr=proto,
                           sz=size,inf=info,tg=tag:
                           self._log_packet(ts(),s,d2,pr,str(sz),inf,tg))
                time.sleep(random.uniform(0.04,0.25))

        threading.Thread(target=_sim,daemon=True).start()
        self._add_alert("Simulation mode: synthetic traffic active")

    # ══════════════════════════════════════════════════════════════════════════
    # ALERTS
    # ══════════════════════════════════════════════════════════════════════════
    def _add_alert(self, msg):
        self.alert_log.appendleft(f"[{ts()}] {msg}")

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN LOOPS
    # ══════════════════════════════════════════════════════════════════════════
    def _start_loops(self):
        self._loop_clock()
        self._loop_radar()
        self._loop_earth()
        self._loop_map()
        self._loop_bw()
        self._loop_ui()
        self.after(600, self._simulate_traffic)

    def _loop_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000,self._loop_clock)

    def _loop_radar(self):
        self.radar_angle=(self.radar_angle+2.5)%360
        self._draw_radar()
        self.after(40,self._loop_radar)

    def _loop_earth(self):
        self.earth_angle=(self.earth_angle+0.4)%360
        self._draw_earth()
        self.after(40,self._loop_earth)

    def _loop_map(self):
        self._draw_world_map()
        self.after(500,self._loop_map)   # map redraws at 2fps (less CPU)

    def _loop_bw(self):
        self.bw_history.append((self.bw_in,self.bw_out))
        self.bw_in=0; self.bw_out=0
        self._draw_bw()
        self.after(1000,self._loop_bw)

    def _loop_ui(self):
        self._update_stats()
        self._update_hosts()
        self.after(1500,self._loop_ui)

    # ══════════════════════════════════════════════════════════════════════════
    # QUIT
    # ══════════════════════════════════════════════════════════════════════════
    def on_close(self):
        self.running=False; self.sniffing=False
        self.destroy()


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if platform.system()=="Windows":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except: pass
    app = GreyNOC()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
