#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║        GREY NOC V2 — NETWORK OPERATIONS CENTER       ║
║        80s Retro Terminal Edition  ▌ v4.0            ║
╚══════════════════════════════════════════════════════╝
Layout:
  TOP HALF  → [Radar+Earth+Stats | WORLD MAP | Packet Log]
  BOT HALF  → [BW Graph + Host Tracker | PORT SCANNER (full)]

Requirements:
    pip install scapy psutil
    Run as Administrator for packet capture + airplane mode.
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
import os
import platform
import subprocess
from datetime import datetime, timedelta
from collections import deque

try:
    import psutil; HAS_PSUTIL = True
except: HAS_PSUTIL = False

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP; HAS_SCAPY = True
except: HAS_SCAPY = False

# ══════════════════════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════════════════════
C = {
    "bg":      "#020c02", "panel":   "#030e03", "border":  "#1a4a1a",
    "glow":    "#00ff41", "dim":     "#005a18",  "mid":     "#00c832",
    "amber":   "#ffb000", "red":     "#ff2020",  "red_dim": "#5a0000",
    "blue":    "#00cfff", "cyan":    "#00ffee",  "purple":  "#cc00ff",
    "scanline":"#060d06", "dark":    "#010801",  "grid":    "#091809",
    "map_bg":  "#010c01", "map_land":"#0c2a0c",  "map_line":"#1e5a1e",
    "orange":  "#ff8800", "pink":    "#ff4488",
}
FM   = ("Courier New", 8)
FMB  = ("Courier New", 8,  "bold")
FM9  = ("Courier New", 9)
FM9B = ("Courier New", 9,  "bold")
F11B = ("Courier New", 11, "bold")
F16B = ("Courier New", 16, "bold")

# ══════════════════════════════════════════════════════════════════════════════
# CONTINENT DATA
# ══════════════════════════════════════════════════════════════════════════════
CONTINENTS = {
    "N.America":[(-168,72),(-140,70),(-120,75),(-90,72),(-80,68),(-70,62),
        (-55,47),(-52,47),(-56,44),(-70,43),(-75,35),(-80,25),(-87,15),
        (-83,9),(-77,8),(-60,10),(-55,5),(-52,4),(-50,5),(-60,0),(-65,-5),
        (-70,0),(-80,0),(-85,5),(-90,10),(-95,15),(-100,20),(-105,22),
        (-110,25),(-115,27),(-118,30),(-120,33),(-122,37),(-124,42),
        (-126,48),(-130,55),(-135,58),(-140,62),(-145,60),(-152,58),
        (-160,60),(-165,63),(-168,66),(-168,72)],
    "S.America":[(-70,-55),(-65,-55),(-63,-52),(-58,-48),(-50,-28),
        (-48,-26),(-40,-20),(-35,-10),(-34,-7),(-35,-5),(-38,0),(-50,0),
        (-58,1),(-60,5),(-62,8),(-60,12),(-65,10),(-70,12),(-72,10),
        (-75,0),(-80,-3),(-80,-8),(-77,-14),(-75,-18),(-70,-22),(-68,-30),
        (-66,-33),(-67,-38),(-66,-43),(-65,-48),(-68,-52),(-70,-55)],
    "Europe":[(-10,36),(0,36),(5,43),(8,44),(15,44),(18,40),(25,37),
        (28,40),(32,42),(35,48),(32,52),(22,55),(18,58),(15,58),(10,58),
        (5,57),(0,51),(-5,48),(-5,44),(-8,43),(-9,39),(-10,36)],
    "Africa":[(-17,15),(-15,10),(-15,5),(-8,5),(0,5),(5,4),(10,2),(15,0),
        (20,-5),(25,-15),(30,-20),(32,-28),(35,-32),(30,-35),(25,-35),
        (18,-35),(15,-30),(12,-22),(10,-15),(8,-5),(5,0),(2,5),(0,8),
        (-5,5),(-10,5),(-15,10),(-17,15),(0,20),(10,22),(15,24),(20,22),
        (30,20),(35,22),(42,12),(44,10),(42,5),(40,0),(42,-10),(40,-12),
        (35,-18),(30,-20),(25,-30),(20,-34),(15,-34),(10,-30),(5,-25),
        (0,-18),(-5,-14),(-10,-8),(-15,-5),(-18,5),(-15,10),(-17,15)],
    "Asia":[(25,37),(35,37),(37,36),(42,37),(48,30),(55,25),(60,22),(65,22),
        (70,20),(75,8),(80,10),(85,18),(90,22),(95,22),(100,3),(105,5),
        (110,2),(115,5),(120,8),(125,10),(125,15),(120,20),(118,25),(120,30),
        (122,32),(125,35),(130,35),(135,34),(140,36),(142,40),(142,46),
        (140,50),(135,48),(130,42),(128,38),(130,35),(125,30),(122,25),
        (115,20),(110,15),(105,10),(100,5),(95,0),(90,-5),(85,5),(80,10),
        (75,8),(70,8),(65,10),(60,15),(55,20),(50,25),(45,28),(40,30),
        (35,35),(30,37),(25,37)],
    "Australia":[(114,-22),(120,-18),(125,-14),(130,-12),(136,-12),(140,-15),
        (145,-18),(150,-22),(152,-25),(153,-28),(152,-32),(150,-36),
        (147,-38),(145,-38),(143,-38),(140,-37),(138,-35),(136,-35),
        (134,-32),(130,-32),(128,-30),(124,-28),(122,-24),(116,-20),(114,-22)],
    "Greenland":[(-45,84),(-20,83),(-18,77),(-24,72),(-42,70),(-52,68),
        (-55,70),(-52,76),(-45,84)],
}

IP_GEO = {
    "8.8":(-97,38),"8.4":(-97,38),"1.1":(151,-33),"1.0":(151,-33),
    "208.67":(-97,38),"192.168":(-100,45),"10.":(-100,45),
    "172.16":(-100,45),"172.17":(-100,45),"103.":(103,1),"185.":(2,48),
    "91.":(37,55),"5.":(15,50),"77.":(15,50),"194.":(10,51),
    "195.":(10,51),"213.":(10,51),"217.":(2,48),"52.":(-97,38),
    "54.":(-97,38),"35.":(-97,38),"34.":(-97,38),"104.":(-97,38),
    "203.":(139,35),"202.":(116,39),"125.":(116,39),"60.":(116,39),
    "61.":(116,39),"218.":(116,39),"119.":(103,1),"27.":(77,28),
    "49.":(77,28),"122.":(77,28),"200.":(-50,-15),"201.":(-50,-15),
    "189.":(-58,-12),"190.":(-65,-20),"41.":(30,0),"105.":(15,5),
    "196.":(25,-28),"162.":(-97,38),"13.":(-97,38),"18.":(-97,38),
    "23.":(-97,38),"64.":(-97,38),"66.":(-97,38),"69.":(-97,38),
    "72.":(-97,38),"128.":(-97,38),"151.":(151,-33),
}

SCAN_PROFILES = {
    "Quick":   [21,22,23,25,53,80,110,139,143,443,445,3389,8080],
    "Web":     [80,443,8080,8443,8000,8888,3000,4000,5000,9000,9090],
    "Full":    list(range(1,1025)),
    "Stealth": [21,22,23,25,53,80,110,135,139,143,389,443,445,512,513,514,
                587,631,993,995,1433,1521,3306,3389,5432,5900,6379,8080,8443,27017],
    "Database":[1433,1521,3306,5432,5984,6379,7474,8086,9042,9200,27017,28017,50000],
    "Malware": [31337,1234,4444,6666,6667,9999,12345,54321,65535,1080,3128,8888,7777],
    "Tracker": [80,443,1080,3128,8080,8118,9050,9051,1194,500,4500,1723,
                1701,1433,3306,5432,27017,6379,11211],
    "Custom":  [],
}

SVC_DB = {
    21:"FTP",22:"SSH",23:"TELNET",25:"SMTP",53:"DNS",67:"DHCP",
    80:"HTTP",88:"KERBEROS",110:"POP3",111:"SUNRPC",123:"NTP",
    135:"MS-RPC",137:"NETBIOS-NS",139:"NETBIOS-SSN",143:"IMAP",
    161:"SNMP",179:"BGP",389:"LDAP",443:"HTTPS",445:"SMB",
    465:"SMTPS",500:"ISAKMP",512:"REXEC",513:"RLOGIN",514:"SYSLOG",
    515:"LPD",554:"RTSP",587:"SUBMISSION",631:"IPP",636:"LDAPS",
    993:"IMAPS",995:"POP3S",1080:"SOCKS",1194:"OPENVPN",1433:"MSSQL",
    1521:"ORACLE",1701:"L2TP",1723:"PPTP",1812:"RADIUS",1900:"UPnP",
    2049:"NFS",3128:"SQUID",3268:"LDAP-GC",3306:"MYSQL",3389:"RDP",
    4444:"METASPLOIT",4500:"IPSEC",5432:"PGSQL",5900:"VNC",
    5984:"COUCHDB",6379:"REDIS",6667:"IRC",8000:"HTTP-ALT",
    8080:"HTTP-PROXY",8118:"PRIVOXY",8443:"HTTPS-ALT",8888:"JUPYTER",
    9000:"PHP-FPM",9042:"CASSANDRA",9050:"TOR",9051:"TOR-CTRL",
    9090:"PROMETHEUS",9200:"ELASTICSEARCH",11211:"MEMCACHED",
    27017:"MONGODB",28017:"MONGO-WEB",31337:"ELITE/BACK-ORIFICE",
    50000:"IBM-DB2",
}

TRACKER_PORTS = {1080,3128,8080,8118,9050,9051,1194,500,4500,1723,1701,
                  31337,4444,6667,12345,54321,65535}

def ip_to_lonlat(ip):
    for prefix,loc in IP_GEO.items():
        if ip.startswith(prefix):
            return (loc[0]+random.uniform(-2,2), loc[1]+random.uniform(-2,2))
    return (random.uniform(-160,160), random.uniform(-55,65))

def lonlat_to_xy(lon, lat, w, h):
    x = (lon+180)/360*w
    lat_r = math.radians(max(-82,min(82,lat)))
    merc  = math.log(math.tan(math.pi/4+lat_r/2))
    y = h/2 - merc/(2*math.pi)*h*1.25
    return x, y

def ts(): return datetime.now().strftime("%H:%M:%S")

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip=s.getsockname()[0]; s.close(); return ip
    except: return "127.0.0.1"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
class GreyNOC(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GREY NOC V2  ▌  NETWORK OPERATIONS CENTER  v4.0")
        self.configure(bg=C["bg"])
        self.geometry("1700x1000")
        self.minsize(1500,900)

        self.running       = True
        self.sniffing      = False
        self.sniff_thread  = None
        self.scan_thread   = None
        self.my_ip         = local_ip()
        self.airplane_mode = False
        self.blink_state   = True
        self.map_zoom      = 1.0
        self.map_pan_x     = 0
        self.map_pan_y     = 0
        self._map_drag     = None

        # Data stores
        self.hosts         = {}
        self.map_nodes     = {}
        self.bw_history    = deque(maxlen=120)
        self.bw_in = self.bw_out = 0
        self.pkt_count = self.tcp_count = 0
        self.udp_count = self.icmp_count = self.arp_count = 0
        self.alert_log     = deque(maxlen=300)
        self.session_start = datetime.now()
        self.total_bytes   = 0
        self.radar_blips   = []
        self.radar_angle   = 0.0
        self.earth_angle   = 0.0
        self.map_lines     = []   # (sx,sy,dx,dy,age,col)
        self.scan_history  = []
        self._scan_running = False
        self._scan_open    = []
        self._scan_banners = {}
        self._sched_job    = None
        self._live_tracker_active = False
        self._tracker_hits = []

        self._build_ui()
        self._apply_styles()
        self._start_loops()

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _panel(self, parent, title, expand=True, height=None):
        outer = tk.Frame(parent, bg=C["border"])
        kw = dict(fill="both", expand=True, pady=(0,2)) if expand else dict(fill="x", pady=(0,2))
        if height: outer.configure(height=height)
        outer.pack(**kw)
        inner = tk.Frame(outer, bg=C["panel"], padx=4, pady=3)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(inner, text=f"▌{title}", bg=C["panel"],
                 fg=C["glow"], font=F11B, anchor="w").pack(fill="x")
        tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", pady=(1,3))
        return inner

    def _btn(self, parent, text, cmd, fg=None, bg=None, font=None, **kw):
        return tk.Button(parent, text=text, command=cmd,
                         bg=bg or C["border"], fg=fg or C["glow"],
                         font=font or FM9B, relief="flat",
                         activebackground=C["dim"], activeforeground=C["glow"],
                         cursor="hand2", **kw)

    def _lbl(self, parent, text, fg=None, font=None, **kw):
        return tk.Label(parent, text=text, bg=C["panel"],
                        fg=fg or C["dim"], font=font or FM, **kw)

    def _apply_styles(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("TNotebook", background=C["bg"], borderwidth=0)
        s.configure("TNotebook.Tab", background=C["dark"], foreground=C["dim"],
                    font=FM9B, padding=[8,3], borderwidth=0)
        s.map("TNotebook.Tab", background=[("selected",C["border"])],
              foreground=[("selected",C["glow"])])
        s.configure("NOC.Treeview", background=C["bg"], foreground=C["glow"],
                    fieldbackground=C["bg"], font=FM, rowheight=15)
        s.configure("NOC.Treeview.Heading", background=C["border"],
                    foreground=C["amber"], font=FM)
        s.map("NOC.Treeview", background=[("selected",C["dim"])],
              foreground=[("selected",C["bg"])])
        s.configure("green.Horizontal.TProgressbar",
                    troughcolor=C["dark"], background=C["glow"],
                    darkcolor=C["glow"], lightcolor=C["mid"])

    # ══════════════════════════════════════════════════════════════════════════
    # LAYOUT  ── TOP BAR + body split top/bottom
    # ══════════════════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_topbar()

        # Outer paned window splits screen top/bottom
        self.pw_main = tk.PanedWindow(self, orient="vertical",
                                       bg=C["dark"], sashwidth=5,
                                       sashrelief="flat")
        self.pw_main.pack(fill="both", expand=True, padx=2, pady=2)

        # ── TOP HALF ──────────────────────────────────────────────────────
        top_half = tk.Frame(self.pw_main, bg=C["bg"])
        self.pw_main.add(top_half, minsize=300)

        # Three equal columns in top half
        top_half.columnconfigure(0, weight=1)
        top_half.columnconfigure(1, weight=1)
        top_half.columnconfigure(2, weight=1)
        top_half.rowconfigure(0, weight=1)

        col_left   = tk.Frame(top_half, bg=C["bg"])
        col_map    = tk.Frame(top_half, bg=C["bg"])
        col_right  = tk.Frame(top_half, bg=C["bg"])
        col_left .grid(row=0, column=0, sticky="nsew", padx=(0,2))
        col_map  .grid(row=0, column=1, sticky="nsew", padx=2)
        col_right.grid(row=0, column=2, sticky="nsew", padx=(2,0))

        self._build_left_col(col_left)
        self._build_world_map(col_map)
        self._build_packet_log(col_right)

        # ── BOTTOM HALF ───────────────────────────────────────────────────
        bot_half = tk.Frame(self.pw_main, bg=C["bg"])
        self.pw_main.add(bot_half, minsize=300)

        bot_half.columnconfigure(0, weight=1)
        bot_half.columnconfigure(1, weight=2)
        bot_half.rowconfigure(0, weight=1)

        col_bl = tk.Frame(bot_half, bg=C["bg"])
        col_br = tk.Frame(bot_half, bg=C["bg"])
        col_bl.grid(row=0, column=0, sticky="nsew", padx=(0,2))
        col_br.grid(row=0, column=1, sticky="nsew", padx=(2,0))

        self._build_bottom_left(col_bl)
        self._build_port_scanner(col_br)

    # ══════════════════════════════════════════════════════════════════════════
    # TOP BAR
    # ══════════════════════════════════════════════════════════════════════════
    def _build_topbar(self):
        bar = tk.Frame(self, bg=C["dark"], height=46)
        bar.pack(fill="x"); bar.pack_propagate(False)

        tk.Label(bar, text="▓▒░ GREY NOC V2 ░▒▓",
                 bg=C["dark"], fg=C["glow"], font=F16B).pack(side="left",padx=10)
        tk.Label(bar, text="NETWORK OPERATIONS CENTER  v4.0",
                 bg=C["dark"], fg=C["dim"], font=FM9B).pack(side="left")

        r = tk.Frame(bar, bg=C["dark"]); r.pack(side="right", padx=8)

        self.btn_kill = tk.Button(r, text="✈ KILL SWITCH: OFF",
                                   bg=C["dim"], fg=C["bg"], font=FMB,
                                   relief="flat", padx=8, pady=3,
                                   cursor="hand2", command=self._toggle_airplane)
        self.btn_kill.pack(side="right", padx=5)

        self._btn(r,"⬛ EXPORT",self._export_data,bg=C["red"],
                  fg="#fff",font=FMB,padx=8,pady=3).pack(side="right",padx=3)

        self.btn_sniff = self._btn(r,"▶ START CAPTURE",self._toggle_sniff,
                                    padx=8,pady=3)
        self.btn_sniff.pack(side="right", padx=3)

        self.lbl_ip = tk.Label(r,text=f"HOST: {self.my_ip}",
                                bg=C["dark"],fg=C["mid"],font=FM9B)
        self.lbl_ip.pack(side="right",padx=10)
        self.lbl_time = tk.Label(r,text="",bg=C["dark"],fg=C["amber"],font=FM9B)
        self.lbl_time.pack(side="right",padx=8)

    # ══════════════════════════════════════════════════════════════════════════
    # LEFT COLUMN  (top-half, 1/3)  — radar + earth + stats
    # ══════════════════════════════════════════════════════════════════════════
    def _build_left_col(self, parent):
        self._build_radar(parent)
        self._build_earth(parent)
        self._build_stats_panel(parent)

    # ── RADAR ─────────────────────────────────────────────────────────────────
    def _build_radar(self, parent):
        p = self._panel(parent, "RADAR SWEEP", expand=False)
        self.radar_canvas = tk.Canvas(p, height=200, bg=C["dark"],
                                       highlightthickness=0)
        self.radar_canvas.pack(fill="x")

    def _draw_radar(self):
        c = self.radar_canvas; c.delete("all")
        W = c.winfo_width() or 300; H = 200
        cx,cy,r = W//2, H//2, min(W//2,H//2)-12
        for i in range(1,5):
            rr=r*i/4
            c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=C["grid"])
        c.create_line(cx-r,cy,cx+r,cy,fill=C["grid"])
        c.create_line(cx,cy-r,cx,cy+r,fill=C["grid"])
        for a in [45,135]:
            rad=math.radians(a)
            c.create_line(cx+r*math.cos(rad),cy+r*math.sin(rad),
                          cx-r*math.cos(rad),cy-r*math.sin(rad),
                          fill=C["grid"],dash=(2,6))
        for t in range(40,0,-1):
            ang=math.radians(self.radar_angle-t*2)
            g=int(0x55*(t/40))
            c.create_line(cx,cy,cx+r*math.cos(ang),cy+r*math.sin(ang),
                          fill=f"#00{g:02x}00",width=2)
        sx=cx+r*math.cos(math.radians(self.radar_angle))
        sy=cy+r*math.sin(math.radians(self.radar_angle))
        c.create_line(cx,cy,sx,sy,fill=C["glow"],width=2)
        dead=[]
        for i,(ba,bd,age,col) in enumerate(self.radar_blips):
            bx=cx+bd*r*math.cos(math.radians(ba))
            by=cy+bd*r*math.sin(math.radians(ba))
            fade=max(0,1-age/100)
            if fade<0.03: dead.append(i); continue
            sz=4*fade+2
            c.create_oval(bx-sz,by-sz,bx+sz,by+sz,fill=col,outline="")
            c.create_oval(bx-sz*2.2,by-sz*2.2,bx+sz*2.2,by+sz*2.2,
                          outline=col,width=1)
        for i in reversed(dead): self.radar_blips.pop(i)
        self.radar_blips=[(a,d,age+1,col) for a,d,age,col in self.radar_blips]
        c.create_oval(cx-3,cy-3,cx+3,cy+3,fill=C["glow"],outline="")
        c.create_text(cx,cy-r-10,
                      text=f"TRACKING {len(self.hosts)} HOSTS",
                      fill=C["amber"],font=FM)

    # ── EARTH ─────────────────────────────────────────────────────────────────
    def _build_earth(self, parent):
        p = self._panel(parent,"GLOBAL TRACKER",expand=False)
        self.earth_canvas = tk.Canvas(p,height=170,bg=C["dark"],
                                       highlightthickness=0)
        self.earth_canvas.pack(fill="x")

    def _draw_earth(self):
        c=self.earth_canvas; c.delete("all")
        W=c.winfo_width() or 300; H=170
        cx,cy,r=W//2,H//2-5,min(W//2,H//2)-14
        ang=self.earth_angle
        for gr in range(r+12,r,-2):
            a=(gr-r)/12; v=int(0x0c*(1-a))
            col=f"#{v:02x}{v+3:02x}{v:02x}" if v>0 else C["dark"]
            c.create_oval(cx-gr,cy-gr,cx+gr,cy+gr,outline=col)
        c.create_oval(cx-r,cy-r,cx+r,cy+r,fill="#020d04",outline=C["mid"],width=2)
        lon_rad=math.radians(ang)
        for lat_d in range(-60,90,30):
            lat=math.radians(lat_d); ry=r*math.cos(lat); yp=cy+r*math.sin(lat)
            if ry>2: c.create_oval(cx-ry,yp-3,cx+ry,yp+3,outline=C["grid"])
        for ld in range(0,360,30):
            lon=math.radians(ld+ang); pts=[]
            for la_d in range(-80,90,10):
                la=math.radians(la_d)
                x3=math.cos(la)*math.cos(lon); y3=math.sin(la)
                z3=math.cos(la)*math.sin(lon)
                if z3<0: continue
                pts.append((cx+r*x3,cy-r*y3))
            for i in range(len(pts)-1):
                c.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],
                              fill=C["grid"])
        blobs=[[(0.3,0.3),(0.5,0.2),(0.6,0.4),(0.4,0.6),(0.2,0.5)],
               [(-0.2,0.3),(0.0,0.1),(0.1,-0.2),(-0.1,-0.6),(-0.3,-0.3)],
               [(0.1,0.4),(0.6,0.3),(0.7,0.1),(0.5,-0.1),(0.2,0.1)]]
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
                      text=f"ROT {ang:.0f}°  PKTS:{self.pkt_count}",
                      fill=C["mid"],font=FM)

    # ── STATS ─────────────────────────────────────────────────────────────────
    def _build_stats_panel(self, parent):
        p=self._panel(parent,"SESSION STATISTICS",expand=True)
        self.stat_vars={}
        rows=[("PACKETS",C["glow"]),("TCP",C["glow"]),("UDP",C["blue"]),
              ("ICMP",C["amber"]),("ARP",C["mid"]),("HOSTS",C["cyan"]),
              ("MB TOTAL",C["glow"]),("BW ↓",C["glow"]),("BW ↑",C["blue"]),
              ("CPU%",C["amber"]),("MEM%",C["amber"]),("UPTIME",C["mid"]),
              ("ALERTS",C["red"])]
        for key,col in rows:
            row=tk.Frame(p,bg=C["panel"]); row.pack(fill="x",pady=1)
            tk.Label(row,text=f"{key:<10}",bg=C["panel"],fg=C["dim"],
                     font=FM,anchor="w").pack(side="left")
            v=tk.Label(row,text="---",bg=C["panel"],fg=col,font=FMB,anchor="e")
            v.pack(side="right")
            self.stat_vars[key]=v
        tk.Frame(p,bg=C["border"],height=1).pack(fill="x",pady=3)
        led_row=tk.Frame(p,bg=C["panel"]); led_row.pack(fill="x")
        self.leds={}
        for name,col in [("NET",C["glow"]),("SCAN",C["amber"]),
                          ("TRACKER",C["red"]),("SCHED",C["blue"])]:
            sub=tk.Frame(led_row,bg=C["panel"]); sub.pack(side="left",expand=True)
            led=tk.Canvas(sub,width=12,height=12,bg=C["panel"],highlightthickness=0)
            led.pack(side="left",padx=1)
            tk.Label(sub,text=name,bg=C["panel"],fg=C["dim"],font=FM).pack(side="left")
            self.leds[name]=(led,col)

    def _update_stats(self):
        elapsed=datetime.now()-self.session_start
        h,rem=divmod(int(elapsed.total_seconds()),3600); m,s=divmod(rem,60)
        self.stat_vars["PACKETS"].config(text=str(self.pkt_count))
        self.stat_vars["TCP"].config(text=str(self.tcp_count))
        self.stat_vars["UDP"].config(text=str(self.udp_count))
        self.stat_vars["ICMP"].config(text=str(self.icmp_count))
        self.stat_vars["ARP"].config(text=str(self.arp_count))
        self.stat_vars["HOSTS"].config(text=str(len(self.hosts)))
        self.stat_vars["MB TOTAL"].config(text=f"{self.total_bytes/1048576:.2f}")
        self.stat_vars["UPTIME"].config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.stat_vars["ALERTS"].config(text=str(len(self.alert_log)))
        if self.bw_history:
            last=self.bw_history[-1]
            self.stat_vars["BW ↓"].config(text=f"{last[0]/1024:.1f}K/s")
            self.stat_vars["BW ↑"].config(text=f"{last[1]/1024:.1f}K/s")
        if HAS_PSUTIL:
            cpu=psutil.cpu_percent(); mem=psutil.virtual_memory().percent
            self.stat_vars["CPU%"].config(text=f"{cpu:.1f}%",
                fg=C["red"] if cpu>80 else C["amber"] if cpu>50 else C["glow"])
            self.stat_vars["MEM%"].config(text=f"{mem:.1f}%",
                fg=C["red"] if mem>85 else C["amber"] if mem>65 else C["glow"])
        self.blink_state=not self.blink_state
        self._blink_led("NET",   self.sniffing,      C["glow"])
        self._blink_led("SCAN",  self._scan_running, C["amber"])
        self._blink_led("TRACKER",self._live_tracker_active, C["red"])
        self._blink_led("SCHED", self._sched_job is not None, C["blue"])

    def _blink_led(self,name,active,on_col):
        led,col=self.leds[name]; led.delete("all")
        fill=on_col if(active and self.blink_state) else(C["dim"] if active else "#111")
        led.create_oval(1,1,11,11,fill=fill,outline=on_col if active else "#222",width=1)

    # ══════════════════════════════════════════════════════════════════════════
    # WORLD MAP  (center third of top half)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_world_map(self, parent):
        # Title bar
        tb=tk.Frame(parent,bg=C["panel"]); tb.pack(fill="x",pady=(0,1))
        tk.Label(tb,text="▌GLOBAL CONNECTION MAP",bg=C["panel"],
                 fg=C["glow"],font=F11B).pack(side="left",padx=5)
        zf=tk.Frame(tb,bg=C["panel"]); zf.pack(side="right",padx=4)
        self._btn(zf,"⊕",self._map_zoom_in,  font=FM,padx=3).pack(side="left")
        self._btn(zf,"⊖",self._map_zoom_out, font=FM,padx=3).pack(side="left",padx=2)
        self._btn(zf,"⟳",self._map_reset,    font=FM,padx=3).pack(side="left")
        self._btn(tb,"⬡ POP OUT",self._map_popout,font=FM).pack(side="right",padx=4)

        # Legend
        leg=tk.Frame(parent,bg=C["panel"]); leg.pack(fill="x")
        for txt,col in [("● TCP",C["glow"]),("● UDP",C["blue"]),
                         ("● ICMP",C["amber"]),("● ARP",C["mid"]),
                         ("● ALERT",C["red"]),("● YOU",C["cyan"])]:
            tk.Label(leg,text=txt,bg=C["panel"],fg=col,font=FM).pack(side="left",padx=4)
        self.lbl_map_stat=tk.Label(leg,text="",bg=C["panel"],
                                    fg=C["amber"],font=FM)
        self.lbl_map_stat.pack(side="right",padx=6)

        # Canvas — fills remaining height
        self.map_canvas=tk.Canvas(parent,bg=C["map_bg"],
                                   highlightthickness=0,cursor="crosshair")
        self.map_canvas.pack(fill="both",expand=True)
        self.map_canvas.bind("<ButtonPress-1>",  self._map_drag_start)
        self.map_canvas.bind("<B1-Motion>",       self._map_drag_move)
        self.map_canvas.bind("<ButtonRelease-1>", self._map_drag_end)
        self.map_canvas.bind("<MouseWheel>",      self._map_scroll)
        self.map_canvas.bind("<Motion>",          self._map_hover)
        self.map_canvas.bind("<Configure>",       lambda e:self._draw_world_map())

        self.map_tooltip=tk.Label(parent,text="",bg=C["amber"],fg=C["dark"],
                                   font=FM,relief="flat",padx=3)

    def _map_zoom_in(self):
        self.map_zoom=min(self.map_zoom*1.35,10.0); self._draw_world_map()
    def _map_zoom_out(self):
        self.map_zoom=max(self.map_zoom/1.35,0.4); self._draw_world_map()
    def _map_reset(self):
        self.map_zoom=1.0; self.map_pan_x=0; self.map_pan_y=0
        self._draw_world_map()
    def _map_drag_start(self,e): self._map_drag=(e.x,e.y)
    def _map_drag_move(self,e):
        if self._map_drag:
            self.map_pan_x+=e.x-self._map_drag[0]
            self.map_pan_y+=e.y-self._map_drag[1]
            self._map_drag=(e.x,e.y); self._draw_world_map()
    def _map_drag_end(self,e): self._map_drag=None
    def _map_scroll(self,e):
        if e.delta>0: self._map_zoom_in()
        else:         self._map_zoom_out()

    def _map_hover(self,e):
        c=self.map_canvas
        W=c.winfo_width() or 500; H=c.winfo_height() or 400
        closest=None; md=18
        for ip,node in self.map_nodes.items():
            x,y=self._proj(node["lon"],node["lat"],W,H)
            d=math.hypot(e.x-x,e.y-y)
            if d<md: md=d; closest=(ip,node,x,y)
        if closest:
            ip,node,x,y=closest
            self.map_tooltip.config(
                text=f" {ip}  pkts:{node['pkts']}  ({node['lon']:.0f},{node['lat']:.0f}) ")
            self.map_tooltip.place(x=x+8,y=y-16)
        else:
            self.map_tooltip.place_forget()

    def _map_popout(self):
        win=tk.Toplevel(self); win.title("GREY NOC — GLOBAL MAP")
        win.configure(bg=C["bg"]); win.geometry("1200x700")
        c2=tk.Canvas(win,bg=C["map_bg"],highlightthickness=0)
        c2.pack(fill="both",expand=True)
        def loop():
            if win.winfo_exists():
                W=c2.winfo_width() or 1200; H=c2.winfo_height() or 700
                self._draw_map_on(c2,W,H,1.0,0,0); win.after(500,loop)
        c2.bind("<Configure>",lambda e:loop()); win.after(100,loop)

    def _proj(self,lon,lat,W,H):
        x,y=lonlat_to_xy(lon,lat,W,H)
        cx,cy=W/2,H/2
        return cx+(x-cx)*self.map_zoom+self.map_pan_x, cy+(y-cy)*self.map_zoom+self.map_pan_y

    def _draw_world_map(self):
        c=self.map_canvas
        W=c.winfo_width() or 500; H=c.winfo_height() or 400
        self._draw_map_on(c,W,H,self.map_zoom,self.map_pan_x,self.map_pan_y)
        self.lbl_map_stat.config(
            text=f"z:{self.map_zoom:.1f}x  n:{len(self.map_nodes)}  c:{len(self.map_lines)}")

    def _draw_map_on(self,c,W,H,zoom,px,py):
        c.delete("all")
        def proj(lon,lat):
            x,y=lonlat_to_xy(lon,lat,W,H); cx,cy=W/2,H/2
            return cx+(x-cx)*zoom+px, cy+(y-cy)*zoom+py
        c.create_rectangle(0,0,W,H,fill=C["map_bg"],outline="")
        # Grid
        for lon in range(-180,181,30):
            x,_=proj(lon,0); c.create_line(x,0,x,H,fill=C["grid"],dash=(2,8))
        for lat in range(-60,91,30):
            _,y=proj(0,lat); c.create_line(0,y,W,y,fill=C["grid"],dash=(2,8))
        # Continents
        for name,pts in CONTINENTS.items():
            coords=[]
            for lon,lat in pts:
                x,y=proj(lon,lat); coords.extend([x,y])
            if len(coords)>=6:
                try: c.create_polygon(coords,fill=C["map_land"],
                                      outline=C["map_line"],width=1)
                except: pass
        # Connection arcs + animated dot
        dead=[]
        for i,(sx,sy,dx,dy,age,col) in enumerate(self.map_lines):
            fade=max(0,1-age/80)
            if fade<0.04: dead.append(i); continue
            cx2,cy2=W/2,H/2
            sx2=cx2+(sx-cx2)*zoom+px; sy2=cy2+(sy-cy2)*zoom+py
            dx2=cx2+(dx-cx2)*zoom+px; dy2=cy2+(dy-cy2)*zoom+py
            mx=(sx2+dx2)/2; my=min(sy2,dy2)-22*fade
            c.create_line(sx2,sy2,mx,my,dx2,dy2,fill=col,
                          width=max(1,int(2*fade)),smooth=True)
            t=(age%18)/18.0
            bx=sx2*(1-t)**2+mx*2*t*(1-t)+dx2*t**2
            by=sy2*(1-t)**2+my*2*t*(1-t)+dy2*t**2
            dr=3*fade
            c.create_oval(bx-dr,by-dr,bx+dr,by+dr,fill=col,outline="")
        for i in reversed(dead): self.map_lines.pop(i)
        self.map_lines=[(sx,sy,dx,dy,age+1,col)
                        for sx,sy,dx,dy,age,col in self.map_lines]
        # Nodes
        blink=self.blink_state
        for ip,node in list(self.map_nodes.items()):
            x,y=proj(node["lon"],node["lat"])
            col=node["color"]; pkts=node["pkts"]
            ro=max(5,min(14,5+math.log1p(pkts)*1.5))*zoom
            if blink: c.create_oval(x-ro,y-ro,x+ro,y+ro,outline=col,width=1)
            r2=ro*0.55
            c.create_oval(x-r2,y-r2,x+r2,y+r2,outline=col,width=1)
            rc=max(2,2.5*zoom)
            c.create_oval(x-rc,y-rc,x+rc,y+rc,fill=col,outline="")
            if zoom>1.8 or pkts>15:
                c.create_text(x+rc+3,y-4,text=ip,fill=col,font=FM,anchor="w")
        # YOU
        mylo=ip_to_lonlat(self.my_ip)
        mx2,my2=proj(mylo[0],mylo[1])
        pulse=7+2.5*math.sin(time.time()*3); pr=pulse*zoom
        c.create_oval(mx2-pr,my2-pr,mx2+pr,my2+pr,outline=C["cyan"],width=2)
        c.create_oval(mx2-3,my2-3,mx2+3,my2+3,fill=C["cyan"],outline="")
        c.create_text(mx2+pr+4,my2-5,text="YOU",fill=C["cyan"],font=FMB,anchor="w")
        # Scanlines
        for sl in range(0,H,4):
            c.create_line(0,sl,W,sl,fill=C["scanline"],stipple="gray25")
        # HUD corners
        c.create_text(6,6,text=f"z:{zoom:.1f}x",fill=C["amber"],font=FM,anchor="nw")
        c.create_text(W-6,6,text=f"N:{len(self.map_nodes)} L:{len(self.map_lines)}",
                      fill=C["amber"],font=FM,anchor="ne")
        c.create_text(6,H-6,text=f"pkts:{self.pkt_count}",
                      fill=C["dim"],font=FM,anchor="sw")
        c.create_text(W-6,H-6,text=datetime.now().strftime("%H:%M:%S"),
                      fill=C["dim"],font=FM,anchor="se")

    def _register_map_node(self,ip,color):
        if ip.startswith(("127.","0.","255.")): return
        if ip not in self.map_nodes:
            lon,lat=ip_to_lonlat(ip)
            self.map_nodes[ip]={"lon":lon,"lat":lat,"age":0,"color":color,"pkts":0}
        self.map_nodes[ip]["pkts"]+=1; self.map_nodes[ip]["color"]=color

    def _add_map_connection(self,src,dst,color):
        if src not in self.map_nodes or dst not in self.map_nodes: return
        W=self.map_canvas.winfo_width() or 500
        H=self.map_canvas.winfo_height() or 400
        sx,sy=lonlat_to_xy(self.map_nodes[src]["lon"],self.map_nodes[src]["lat"],W,H)
        dx,dy=lonlat_to_xy(self.map_nodes[dst]["lon"],self.map_nodes[dst]["lat"],W,H)
        if len(self.map_lines)<300: self.map_lines.append((sx,sy,dx,dy,0,color))

    # ══════════════════════════════════════════════════════════════════════════
    # PACKET LOG  (right third of top half)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_packet_log(self, parent):
        p=self._panel(parent,"LIVE PACKET CAPTURE",expand=True)
        hdr=tk.Frame(p,bg=C["panel"]); hdr.pack(fill="x")
        for txt,w in [("TIME",8),("SRC",16),("DST",16),("PROTO",6),("LEN",6),("INFO",20)]:
            tk.Label(hdr,text=txt,width=w,bg=C["panel"],fg=C["amber"],
                     font=FM,anchor="w").pack(side="left")
        tk.Frame(p,bg=C["border"],height=1).pack(fill="x",pady=2)
        self.pkt_log=scrolledtext.ScrolledText(
            p,bg=C["bg"],fg=C["glow"],font=FM,relief="flat",
            wrap="none",state="disabled",insertbackground=C["glow"])
        self.pkt_log.pack(fill="both",expand=True)
        for tag,col in [("tcp",C["glow"]),("udp",C["blue"]),
                         ("icmp",C["amber"]),("arp",C["mid"]),("other",C["dim"])]:
            self.pkt_log.tag_config(tag,foreground=col)
        br=tk.Frame(p,bg=C["panel"]); br.pack(fill="x",pady=2)
        self._btn(br,"⚡ SIMULATE",self._simulate_traffic,font=FM).pack(side="right",padx=2)
        self._btn(br,"⬜ CLEAR",self._clear_log,fg=C["dim"],font=FM).pack(side="right")

    def _log_packet(self,t,src,dst,proto,length,info,tag="other"):
        line=f"{t:<9}{src:<17}{dst:<17}{proto:<7}{length:<7}{info}\n"
        self.pkt_log.config(state="normal")
        self.pkt_log.insert("end",line,tag)
        if int(self.pkt_log.index("end-1c").split(".")[0])>600:
            self.pkt_log.delete("1.0","80.0")
        self.pkt_log.see("end"); self.pkt_log.config(state="disabled")

    def _clear_log(self):
        self.pkt_log.config(state="normal"); self.pkt_log.delete("1.0","end")
        self.pkt_log.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    # BOTTOM LEFT  — BW graph + host tracker + controls
    # ══════════════════════════════════════════════════════════════════════════
    def _build_bottom_left(self, parent):
        self._build_bw_graph(parent)
        self._build_host_tracker(parent)
        self._build_controls(parent)

    def _build_bw_graph(self, parent):
        p=self._panel(parent,"BANDWIDTH MONITOR",expand=False)
        self.bw_canvas=tk.Canvas(p,height=90,bg=C["dark"],highlightthickness=0)
        self.bw_canvas.pack(fill="x",pady=2)

    def _draw_bw(self):
        c=self.bw_canvas; c.delete("all")
        W=c.winfo_width() or 400; H=90; pad=26
        for gy in range(0,H,20):
            c.create_line(pad,gy,W,gy,fill=C["grid"],dash=(2,4))
        if not self.bw_history:
            c.create_text(W//2,H//2,text="AWAITING DATA",fill=C["dim"],font=FM9); return
        mx=max((max(x) for x in self.bw_history),default=1) or 1
        n=len(self.bw_history); step=(W-pad)/max(n,1)
        def mk(idx): return [(pad+i*step,H-(pair[idx]/mx)*(H-8))
                              for i,pair in enumerate(self.bw_history)]
        def fill(pts,col):
            if len(pts)<2: return
            poly=list(pts[0])
            for pp in pts[1:]: poly+=list(pp)
            poly+=[pts[-1][0],H,pts[0][0],H]
            c.create_polygon(poly,fill=col,outline="",stipple="gray25")
            for i in range(len(pts)-1):
                c.create_line(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],fill=col,width=2)
        fill(mk(0),C["glow"]); fill(mk(1),C["blue"])
        last=self.bw_history[-1]
        c.create_text(2,4,text=f"↓{last[0]/1024:.1f}K/s",fill=C["glow"],font=FM,anchor="nw")
        c.create_text(2,15,text=f"↑{last[1]/1024:.1f}K/s",fill=C["blue"],font=FM,anchor="nw")
        for y in range(0,H,3):
            c.create_line(0,y,W,y,fill=C["scanline"],stipple="gray50")

    def _build_host_tracker(self, parent):
        p=self._panel(parent,"HOST TRACKER",expand=True)
        cols=("IP","PKTS","BYTES","PROTO","LAST")
        self.host_tree=ttk.Treeview(p,columns=cols,show="headings",
                                     style="NOC.Treeview",height=10)
        for col,w in zip(cols,[115,45,60,50,62]):
            self.host_tree.heading(col,text=col)
            self.host_tree.column(col,width=w,anchor="w")
        sb=ttk.Scrollbar(p,orient="vertical",command=self.host_tree.yview)
        self.host_tree.configure(yscrollcommand=sb.set)
        self.host_tree.pack(side="left",fill="both",expand=True)
        sb.pack(side="right",fill="y")
        self.host_tree.bind("<Button-3>",self._host_rclick)

    def _host_rclick(self,e):
        iid=self.host_tree.identify_row(e.y)
        if not iid: return
        ip=self.host_tree.item(iid,"values")[0]
        m=tk.Menu(self,tearoff=0,bg=C["panel"],fg=C["glow"],
                  activebackground=C["border"])
        m.add_command(label=f"Quick scan {ip}",
                      command=lambda:self._quick_scan(ip))
        m.add_command(label=f"Ping {ip}",
                      command=lambda:self._do_ping(ip))
        m.add_command(label=f"Traceroute {ip}",
                      command=lambda:self._do_traceroute(ip))
        m.add_command(label=f"Pin to map",
                      command=lambda:self._register_map_node(ip,C["cyan"]))
        m.post(e.x_root,e.y_root)

    def _quick_scan(self,ip):
        self.scan_target_var.set(ip)
        self.scan_profile_var.set("Quick")
        self._on_profile_change(); self._start_scan()

    def _update_hosts(self):
        for r in self.host_tree.get_children(): self.host_tree.delete(r)
        for ip,info in sorted(self.hosts.items(),
                              key=lambda x:x[1]["pkts"],reverse=True)[:80]:
            self.host_tree.insert("","end",values=(
                ip,info["pkts"],f"{info['bytes']//1024}K",
                info.get("proto","?"),info["last_seen"]))

    def _build_controls(self, parent):
        p=self._panel(parent,"SYSTEM CONTROL",expand=False)
        self.lbl_net=tk.Label(p,text="● NETWORK: ONLINE",
                               bg=C["panel"],fg=C["glow"],font=FM9B)
        self.lbl_net.pack(fill="x",pady=2)
        self.btn_kill2=tk.Button(p,text="✈ TOGGLE AIRPLANE MODE",
                                  bg=C["red_dim"],fg=C["red"],font=FM9B,
                                  relief="flat",padx=6,pady=4,cursor="hand2",
                                  activebackground=C["red"],activeforeground="#fff",
                                  command=self._toggle_airplane)
        self.btn_kill2.pack(fill="x",pady=2)
        br=tk.Frame(p,bg=C["panel"]); br.pack(fill="x",pady=2)
        for txt,fmt in [("⬛CSV","csv"),("⬛JSON","json"),("⬛TXT","txt")]:
            tk.Button(br,text=txt,bg=C["red"],fg="#fff",font=FM,relief="flat",
                      pady=2,cursor="hand2",activebackground="#aa0000",
                      command=lambda f=fmt:self._export_data(f)
                      ).pack(side="left",fill="x",expand=True,padx=1)

    # ══════════════════════════════════════════════════════════════════════════
    # PORT SCANNER  (right 2/3 of bottom half)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_port_scanner(self, parent):
        # Use a notebook for Scanner / Live Tracker / Schedule tabs
        nb=ttk.Notebook(parent); nb.pack(fill="both",expand=True)
        self.scan_nb=nb
        tab_scan   =tk.Frame(nb,bg=C["bg"])
        tab_tracker=tk.Frame(nb,bg=C["bg"])
        tab_sched  =tk.Frame(nb,bg=C["bg"])
        nb.add(tab_scan,   text="  ▶ PORT SCANNER  ")
        nb.add(tab_tracker,text="  👁 LIVE TRACKER  ")
        nb.add(tab_sched,  text="  ⏰ SCHEDULER  ")
        self._build_scan_tab(tab_scan)
        self._build_tracker_tab(tab_tracker)
        self._build_sched_tab(tab_sched)

    # ── PORT SCANNER TAB ──────────────────────────────────────────────────────
    def _build_scan_tab(self, parent):
        p=self._panel(parent,"PORT SCANNER  ▌ ADVANCED",expand=True)

        # Row 1: target + quick actions
        r1=tk.Frame(p,bg=C["panel"]); r1.pack(fill="x",pady=2)
        tk.Label(r1,text="TARGET",bg=C["panel"],fg=C["amber"],font=FM,
                 width=7,anchor="w").pack(side="left")
        self.scan_target_var=tk.StringVar(value=self.my_ip)
        tk.Entry(r1,textvariable=self.scan_target_var,bg=C["dark"],fg=C["glow"],
                 font=FM9,width=20,insertbackground=C["glow"],relief="flat",
                 highlightthickness=1,highlightcolor=C["glow"]).pack(side="left",padx=4)
        self._btn(r1,"PING",   lambda:self._do_ping(self.scan_target_var.get()),  font=FM,padx=4).pack(side="left",padx=2)
        self._btn(r1,"TRACE",  lambda:self._do_traceroute(self.scan_target_var.get()),font=FM,padx=4).pack(side="left",padx=2)
        self._btn(r1,"WHOIS",  lambda:self._do_whois(self.scan_target_var.get()),  font=FM,padx=4).pack(side="left",padx=2)

        # Row 2: profile + timeout + threads
        r2=tk.Frame(p,bg=C["panel"]); r2.pack(fill="x",pady=2)
        tk.Label(r2,text="PROFILE",bg=C["panel"],fg=C["amber"],font=FM,
                 width=7,anchor="w").pack(side="left")
        self.scan_profile_var=tk.StringVar(value="Quick")
        prof=ttk.Combobox(r2,textvariable=self.scan_profile_var,
                           values=list(SCAN_PROFILES.keys()),
                           width=11,font=FM,state="readonly")
        prof.pack(side="left",padx=4)
        prof.bind("<<ComboboxSelected>>",lambda e:self._on_profile_change())
        for lbl,var,w2,default in [("TMO",None,5,"0.5"),("THR",None,4,"80")]:
            tk.Label(r2,text=lbl,bg=C["panel"],fg=C["dim"],font=FM).pack(side="left",padx=3)
            v=tk.StringVar(value=default)
            tk.Entry(r2,textvariable=v,bg=C["dark"],fg=C["glow"],font=FM,
                     width=w2,insertbackground=C["glow"],relief="flat").pack(side="left")
            if lbl=="TMO": self.scan_timeout_var=v
            else:          self.scan_threads_var=v

        # Row 3: ports
        r3=tk.Frame(p,bg=C["panel"]); r3.pack(fill="x",pady=2)
        tk.Label(r3,text="PORTS",bg=C["panel"],fg=C["amber"],font=FM,
                 width=7,anchor="w").pack(side="left")
        self.scan_ports_var=tk.StringVar(value="22,80,443,3389,8080,445,21,25,53")
        tk.Entry(r3,textvariable=self.scan_ports_var,bg=C["dark"],fg=C["glow"],
                 font=FM,width=42,insertbackground=C["glow"],relief="flat",
                 highlightthickness=1,highlightcolor=C["glow"]).pack(side="left",padx=4)

        # Row 4: options
        r4=tk.Frame(p,bg=C["panel"]); r4.pack(fill="x",pady=1)
        self.grab_banners=tk.BooleanVar(value=True)
        self.os_detect   =tk.BooleanVar(value=True)
        self.auto_save   =tk.BooleanVar(value=False)
        for txt,var in [("Banner Grab",self.grab_banners),
                         ("OS Detect",self.os_detect),
                         ("Auto-Save",self.auto_save)]:
            tk.Checkbutton(r4,text=txt,variable=var,bg=C["panel"],fg=C["mid"],
                           selectcolor=C["dark"],activebackground=C["panel"],
                           font=FM).pack(side="left",padx=4)

        # Scan button row
        r5=tk.Frame(p,bg=C["panel"]); r5.pack(fill="x",pady=3)
        self.btn_scan=self._btn(r5,"▶▶ SCAN TARGET",self._start_scan,font=FM9B,padx=8,pady=4)
        self.btn_scan.pack(side="left",fill="x",expand=True)
        self._btn(r5,"■ STOP",self._stop_scan,fg=C["red"],font=FM,padx=6,pady=4).pack(side="left",padx=3)
        self._btn(r5,"HISTORY",self._show_scan_history,font=FM,padx=6,pady=4).pack(side="left",padx=3)
        self._btn(r5,"⬛SAVE",self._save_scan_report,bg=C["red"],fg="#fff",font=FM,padx=6,pady=4).pack(side="left")

        # Progress
        self.scan_pct=tk.DoubleVar(value=0)
        ttk.Progressbar(p,variable=self.scan_pct,maximum=100,
                        style="green.Horizontal.TProgressbar").pack(fill="x",pady=2)
        self.scan_status=tk.Label(p,text="READY",bg=C["panel"],
                                   fg=C["dim"],font=FM)
        self.scan_status.pack(fill="x")

        # Port heatmap
        self.heatmap_canvas=tk.Canvas(p,height=28,bg=C["dark"],
                                       highlightthickness=0)
        self.heatmap_canvas.pack(fill="x",pady=2)

        # Results
        self.scan_log=scrolledtext.ScrolledText(
            p,bg=C["bg"],fg=C["glow"],font=FM,relief="flat",
            state="disabled",height=12)
        self.scan_log.pack(fill="both",expand=True,pady=2)
        for tag,col in [("open",C["glow"]),("closed",C["dim"]),("info",C["amber"]),
                         ("banner",C["blue"]),("warn",C["red"]),
                         ("ping",C["cyan"]),("trace",C["purple"]),("os",C["orange"])]:
            self.scan_log.tag_config(tag,foreground=col)

    # ── LIVE TRACKER TAB ──────────────────────────────────────────────────────
    def _build_tracker_tab(self, parent):
        p=self._panel(parent,"LIVE TRACKER DETECTION",expand=True)
        tk.Label(p,text=(
            "Monitors active connections for suspicious ports,\n"
            "known tracker IPs, proxy/VPN/Tor endpoints,\n"
            "and anomalous packet patterns in real-time."),
            bg=C["panel"],fg=C["dim"],font=FM,justify="left").pack(anchor="w",pady=4)

        r1=tk.Frame(p,bg=C["panel"]); r1.pack(fill="x",pady=3)
        self.btn_tracker=self._btn(r1,"▶ START LIVE TRACKER",
                                    self._toggle_live_tracker,
                                    font=FM9B,padx=8,pady=4)
        self.btn_tracker.pack(side="left",fill="x",expand=True)
        self._btn(r1,"⬜ CLEAR",self._clear_tracker_log,
                  fg=C["dim"],font=FM,padx=6).pack(side="left",padx=4)

        # Options
        r2=tk.Frame(p,bg=C["panel"]); r2.pack(fill="x",pady=2)
        self.tr_check_ports =tk.BooleanVar(value=True)
        self.tr_check_geo   =tk.BooleanVar(value=True)
        self.tr_check_volume=tk.BooleanVar(value=True)
        for txt,var in [("Suspicious Ports",self.tr_check_ports),
                         ("Geo Anomaly",self.tr_check_geo),
                         ("Volume Spike",self.tr_check_volume)]:
            tk.Checkbutton(r2,text=txt,variable=var,bg=C["panel"],fg=C["mid"],
                           selectcolor=C["dark"],activebackground=C["panel"],
                           font=FM).pack(side="left",padx=6)

        self.lbl_tracker_status=tk.Label(p,text="STATUS: IDLE",
                                          bg=C["panel"],fg=C["dim"],font=FM9B)
        self.lbl_tracker_status.pack(fill="x",pady=2)

        # Summary bar
        sum_row=tk.Frame(p,bg=C["panel"]); sum_row.pack(fill="x",pady=2)
        self.tracker_summary_vars={}
        for key,col in [("HITS",C["red"]),("SUSP PORTS",C["amber"]),
                         ("GEO FLAGS",C["orange"]),("VOL SPIKES",C["purple"])]:
            sub=tk.Frame(sum_row,bg=C["border"]); sub.pack(side="left",fill="x",expand=True,padx=2,pady=2)
            si=tk.Frame(sub,bg=C["panel"]); si.pack(fill="both",expand=True,padx=1,pady=1)
            tk.Label(si,text=key,bg=C["panel"],fg=C["dim"],font=FM).pack()
            v=tk.Label(si,text="0",bg=C["panel"],fg=col,font=F11B)
            v.pack(); self.tracker_summary_vars[key]=v

        # Hit log
        self.tracker_log=scrolledtext.ScrolledText(
            p,bg=C["bg"],fg=C["glow"],font=FM,relief="flat",state="disabled")
        self.tracker_log.pack(fill="both",expand=True,pady=4)
        for tag,col in [("hit",C["red"]),("warn",C["amber"]),
                         ("info",C["dim"]),("port",C["orange"]),
                         ("geo",C["purple"]),("vol",C["blue"])]:
            self.tracker_log.tag_config(tag,foreground=col)

        self._tracker_hits_count=0
        self._tracker_port_hits=0
        self._tracker_geo_hits=0
        self._tracker_vol_hits=0

    def _toggle_live_tracker(self):
        self._live_tracker_active=not self._live_tracker_active
        if self._live_tracker_active:
            self.btn_tracker.config(text="■ STOP LIVE TRACKER",fg=C["red"])
            self.lbl_tracker_status.config(text="STATUS: ● SCANNING",fg=C["glow"])
            self._add_alert("Live Tracker: started")
            threading.Thread(target=self._live_tracker_worker,daemon=True).start()
        else:
            self.btn_tracker.config(text="▶ START LIVE TRACKER",fg=C["glow"])
            self.lbl_tracker_status.config(text="STATUS: STOPPED",fg=C["dim"])
            self._add_alert("Live Tracker: stopped")

    def _live_tracker_worker(self):
        """Poll active connections every 2 seconds and flag anomalies."""
        prev_bytes={}
        while self._live_tracker_active and self.running:
            try:
                # Check all known hosts for suspicious ports
                if self.tr_check_ports.get():
                    for ip,info in list(self.hosts.items()):
                        for port in TRACKER_PORTS:
                            if info.get("proto","") in ("TCP","UDP"):
                                dport=info.get("dport",0)
                                if dport in TRACKER_PORTS:
                                    msg=(f"[!] SUSPICIOUS PORT {dport} "
                                         f"({SVC_DB.get(dport,'?')}) from {ip}")
                                    self._tracker_port_hits+=1
                                    self.after(0,lambda m=msg:
                                               self._tracker_log(m,"port"))

                # Check for volume spikes
                if self.tr_check_volume.get():
                    for ip,info in list(self.hosts.items()):
                        prev=prev_bytes.get(ip,0)
                        curr=info["bytes"]
                        delta=curr-prev
                        prev_bytes[ip]=curr
                        if delta>500_000:  # >500KB in 2s
                            msg=(f"[!] VOLUME SPIKE: {ip} "
                                 f"+{delta//1024}KB in 2s")
                            self._tracker_vol_hits+=1
                            self.after(0,lambda m=msg:
                                       self._tracker_log(m,"vol"))

                # Check geo anomalies (unexpected continent combos)
                if self.tr_check_geo.get():
                    regions=set()
                    for ip in list(self.map_nodes.keys()):
                        lon=self.map_nodes[ip]["lon"]
                        if lon<-30:   regions.add("AMERICAS")
                        elif lon<60:  regions.add("EUROPE/AFRICA")
                        else:         regions.add("ASIA/PAC")
                    if len(regions)>2:
                        msg=f"[~] GEO SPREAD: Traffic across {', '.join(regions)}"
                        self._tracker_geo_hits+=1
                        self.after(0,lambda m=msg:self._tracker_log(m,"geo"))

                self._tracker_hits_count=(self._tracker_port_hits+
                                           self._tracker_geo_hits+
                                           self._tracker_vol_hits)
                self.after(0,self._update_tracker_summary)

            except Exception as e:
                pass
            time.sleep(2.0)

    def _tracker_log(self,text,tag="info"):
        self.tracker_log.config(state="normal")
        self.tracker_log.insert("end",f"[{ts()}] {text}\n",tag)
        self.tracker_log.see("end")
        self.tracker_log.config(state="disabled")
        self._add_alert(f"TRACKER: {text[:60]}")

    def _clear_tracker_log(self):
        self.tracker_log.config(state="normal")
        self.tracker_log.delete("1.0","end")
        self.tracker_log.config(state="disabled")

    def _update_tracker_summary(self):
        self.tracker_summary_vars["HITS"].config(
            text=str(self._tracker_hits_count))
        self.tracker_summary_vars["SUSP PORTS"].config(
            text=str(self._tracker_port_hits))
        self.tracker_summary_vars["GEO FLAGS"].config(
            text=str(self._tracker_geo_hits))
        self.tracker_summary_vars["VOL SPIKES"].config(
            text=str(self._tracker_vol_hits))

    # ── SCHEDULER TAB ─────────────────────────────────────────────────────────
    def _build_sched_tab(self, parent):
        p=self._panel(parent,"SCHEDULED AUTO-SCAN",expand=True)
        tk.Label(p,text="Automatically repeat port scans at a set interval.",
                 bg=C["panel"],fg=C["dim"],font=FM).pack(anchor="w",pady=4)

        r1=tk.Frame(p,bg=C["panel"]); r1.pack(fill="x",pady=3)
        tk.Label(r1,text="TARGET",bg=C["panel"],fg=C["amber"],font=FM,
                 width=8,anchor="w").pack(side="left")
        self.sched_target_var=tk.StringVar(value=self.my_ip)
        tk.Entry(r1,textvariable=self.sched_target_var,bg=C["dark"],fg=C["glow"],
                 font=FM9,width=20,insertbackground=C["glow"],relief="flat",
                 highlightthickness=1,highlightcolor=C["glow"]).pack(side="left",padx=4)

        r2=tk.Frame(p,bg=C["panel"]); r2.pack(fill="x",pady=3)
        tk.Label(r2,text="INTERVAL",bg=C["panel"],fg=C["amber"],font=FM,
                 width=8,anchor="w").pack(side="left")
        self.sched_interval_var=tk.StringVar(value="300")
        tk.Entry(r2,textvariable=self.sched_interval_var,bg=C["dark"],fg=C["glow"],
                 font=FM9,width=8,insertbackground=C["glow"],relief="flat").pack(side="left",padx=4)
        tk.Label(r2,text="seconds",bg=C["panel"],fg=C["dim"],font=FM).pack(side="left")

        r3=tk.Frame(p,bg=C["panel"]); r3.pack(fill="x",pady=3)
        tk.Label(r3,text="PROFILE",bg=C["panel"],fg=C["amber"],font=FM,
                 width=8,anchor="w").pack(side="left")
        self.sched_profile_var=tk.StringVar(value="Quick")
        ttk.Combobox(r3,textvariable=self.sched_profile_var,
                     values=list(SCAN_PROFILES.keys()),
                     width=12,font=FM,state="readonly").pack(side="left",padx=4)

        r4=tk.Frame(p,bg=C["panel"]); r4.pack(fill="x",pady=3)
        self.sched_save=tk.BooleanVar(value=True)
        tk.Checkbutton(r4,text="Save each scan result automatically",
                       variable=self.sched_save,bg=C["panel"],fg=C["mid"],
                       selectcolor=C["dark"],activebackground=C["panel"],
                       font=FM).pack(side="left")

        btn_row=tk.Frame(p,bg=C["panel"]); btn_row.pack(fill="x",pady=4)
        self.btn_sched=self._btn(btn_row,"▶ START SCHEDULER",
                                  self._toggle_scheduler,font=FM9B,padx=8,pady=4)
        self.btn_sched.pack(side="left",fill="x",expand=True)

        self.lbl_sched_status=tk.Label(p,text="SCHEDULER: IDLE",
                                        bg=C["panel"],fg=C["dim"],font=FM9B)
        self.lbl_sched_status.pack(fill="x",pady=2)

        self.lbl_sched_next=tk.Label(p,text="NEXT SCAN: —",
                                      bg=C["panel"],fg=C["amber"],font=FM)
        self.lbl_sched_next.pack(fill="x")

        self.sched_log=scrolledtext.ScrolledText(
            p,bg=C["bg"],fg=C["glow"],font=FM,relief="flat",
            state="disabled")
        self.sched_log.pack(fill="both",expand=True,pady=4)
        self.sched_log.tag_config("info",foreground=C["amber"])
        self.sched_log.tag_config("result",foreground=C["glow"])
        self.sched_log.tag_config("err",foreground=C["red"])

        self._sched_running=False
        self._sched_next_time=None

    def _toggle_scheduler(self):
        self._sched_running=not self._sched_running
        if self._sched_running:
            self.btn_sched.config(text="■ STOP SCHEDULER",fg=C["red"])
            self.lbl_sched_status.config(text="SCHEDULER: ● RUNNING",fg=C["glow"])
            self._add_alert("Scheduler: started")
            self._sched_job=threading.Thread(
                target=self._scheduler_worker,daemon=True)
            self._sched_job.start()
        else:
            self.btn_sched.config(text="▶ START SCHEDULER",fg=C["glow"])
            self.lbl_sched_status.config(text="SCHEDULER: STOPPED",fg=C["dim"])
            self.lbl_sched_next.config(text="NEXT SCAN: —")
            self._sched_job=None
            self._add_alert("Scheduler: stopped")

    def _scheduler_worker(self):
        while self._sched_running and self.running:
            try:
                interval=int(self.sched_interval_var.get())
            except: interval=300
            interval=max(10,interval)
            target=self.sched_target_var.get().strip()
            profile=self.sched_profile_var.get()
            ports=SCAN_PROFILES.get(profile,[80,443,22])

            self._sched_next_time=datetime.now()+timedelta(seconds=interval)
            self.after(0,lambda t=self._sched_next_time:
                       self.lbl_sched_next.config(
                           text=f"NEXT SCAN: {t.strftime('%H:%M:%S')}"))

            self._sched_log_write(
                f"[{ts()}] Scheduled scan: {target} | {profile} | {len(ports)} ports","info")

            # Run the scan inline (simple sequential, not threaded)
            open_ports=[]
            timeout=0.5
            for port in ports:
                if not self._sched_running: break
                try:
                    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    s.settimeout(timeout)
                    r=s.connect_ex((target,port)); s.close()
                    if r==0: open_ports.append(port)
                except: pass

            result=(f"[{ts()}] RESULT: {len(open_ports)}/{len(ports)} open"
                    f" → {','.join(str(p) for p in open_ports)}")
            self._sched_log_write(result,"result")
            self._add_alert(f"SCHED: {target} {len(open_ports)}/{len(ports)} open")

            if self.sched_save.get():
                self.scan_history.append({
                    "time":ts(),"target":target,
                    "ports_scanned":len(ports),"open_ports":open_ports,
                    "banners":{},"os_guess":"(scheduled)",
                })

            # Wait for next interval
            for _ in range(interval*2):
                if not self._sched_running: break
                time.sleep(0.5)

    def _sched_log_write(self,text,tag="info"):
        self.sched_log.config(state="normal")
        self.sched_log.insert("end",text+"\n",tag)
        self.sched_log.see("end")
        self.sched_log.config(state="disabled")

    # ══════════════════════════════════════════════════════════════════════════
    # SCAN LOGIC
    # ══════════════════════════════════════════════════════════════════════════
    def _on_profile_change(self):
        name=self.scan_profile_var.get()
        ports=SCAN_PROFILES.get(name,[])
        if name=="Full": self.scan_ports_var.set("1-1024")
        elif name!="Custom":
            self.scan_ports_var.set(",".join(str(p) for p in ports))

    def _parse_ports(self,raw):
        ports=[]
        for part in raw.split(","):
            part=part.strip()
            if "-" in part:
                a,b=part.split("-",1)
                try: ports.extend(range(int(a),int(b)+1))
                except: pass
            else:
                try: ports.append(int(part))
                except: pass
        return sorted(set(ports))

    def _start_scan(self):
        if self._scan_running: return
        target=self.scan_target_var.get().strip()
        ports=self._parse_ports(self.scan_ports_var.get())
        if not ports: self._scan_log("No valid ports","warn"); return
        try: timeout=float(self.scan_timeout_var.get())
        except: timeout=0.5
        try: n_thr=min(int(self.scan_threads_var.get()),200)
        except: n_thr=80
        self._scan_running=True; self._scan_open=[]; self._scan_banners={}
        self.scan_log.config(state="normal"); self.scan_log.delete("1.0","end")
        self.scan_log.config(state="disabled"); self.scan_pct.set(0)
        self.btn_scan.config(text="⏳ SCANNING…",state="disabled")
        self._scan_log(f"[{ts()}] TARGET:{target}  PORTS:{len(ports)}"
                       f"  THR:{n_thr}  TMO:{timeout}s","info")
        self._scan_log(f"PROFILE:{self.scan_profile_var.get()}"
                       f"  BANNER:{self.grab_banners.get()}"
                       f"  OS:{self.os_detect.get()}","info")
        self._scan_log("─"*70+"\n","info")
        self._add_alert(f"SCAN: {target} ({len(ports)} ports)")
        self.scan_thread=threading.Thread(
            target=self._scan_worker,args=(target,ports,timeout,n_thr),daemon=True)
        self.scan_thread.start()

    def _stop_scan(self):
        self._scan_running=False; self._scan_log("\n[!] ABORTED","warn")

    def _scan_worker(self,target,ports,timeout,n_thr):
        total=len(ports); done=[0]; lock=threading.Lock()
        sem=threading.Semaphore(n_thr)
        def scan_one(port):
            if not self._scan_running: sem.release(); return
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(timeout); r=s.connect_ex((target,port))
                if r==0:
                    svc=SVC_DB.get(port,"UNKNOWN"); banner=""
                    if self.grab_banners.get():
                        try:
                            s.settimeout(1.0)
                            if port in(80,8080): s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                            raw=s.recv(256)
                            banner=raw.decode("utf-8","ignore").split("\n")[0].strip()[:55]
                        except: pass
                    s.close()
                    flag="⚠" if port in TRACKER_PORTS else ""
                    with lock: self._scan_open.append(port)
                    if banner: self._scan_banners[port]=banner
                    self.after(0,lambda p=port,sv=svc,bn=banner,fl=flag:
                               self._scan_log(f"[OPEN]{fl}  {p:<6}{sv:<15}{bn}","open"))
                else:
                    s.close()
                    if total<60:
                        self.after(0,lambda p=port:self._scan_log(f"[----]  {p}","closed"))
            except: pass
            finally:
                sem.release()
                with lock: done[0]+=1
                pct=done[0]/total*100
                self.after(0,lambda p=pct,d=done[0],po=port:
                           self._update_scan_prog(p,d,total,po))
        threads=[]
        for port in ports:
            if not self._scan_running: break
            sem.acquire()
            t=threading.Thread(target=scan_one,args=(port,),daemon=True)
            t.start(); threads.append(t)
        for t in threads: t.join()
        os_g="(skipped)"
        if self.os_detect.get(): os_g=self._guess_os(target)
        n=len(self._scan_open)
        self.after(0,lambda n=n,t=total,os_g=os_g,tgt=target:
                   self._scan_finish(n,t,os_g,tgt))

    def _update_scan_prog(self,pct,done,total,port):
        self.scan_pct.set(pct)
        self.scan_status.config(text=f"SCANNING {done}/{total}  last:{port}",fg=C["amber"])

    def _scan_finish(self,n_open,total,os_guess,target):
        self._scan_running=False
        self.btn_scan.config(text="▶▶ SCAN TARGET",state="normal")
        self.scan_pct.set(100)
        self.scan_status.config(text=f"DONE — {n_open}/{total} open  OS:{os_guess}",fg=C["glow"])
        self._scan_log("─"*70,"info")
        self._scan_log(f"RESULT:  {n_open}/{total} open","info")
        self._scan_log(f"OS FINGERPRINT:  {os_guess}","os")
        if self._scan_open:
            self._scan_log(f"OPEN PORTS:  {','.join(str(p) for p in self._scan_open)}","open")
        susp=[p for p in self._scan_open if p in TRACKER_PORTS]
        if susp:
            self._scan_log(f"⚠ SUSPICIOUS/TRACKER PORTS: {','.join(str(p) for p in susp)}","warn")
        self._draw_heatmap()
        self._add_alert(f"SCAN done: {n_open} open on {target}  OS:{os_guess}")
        self.scan_history.append({
            "time":ts(),"target":target,"ports_scanned":total,
            "open_ports":list(self._scan_open),"banners":dict(self._scan_banners),
            "os_guess":os_guess,
        })
        if self.auto_save.get(): self._save_scan_report(auto=True)
        if n_open:
            a=random.uniform(0,360); d=random.uniform(0.3,0.9)
            self.radar_blips.append((a,d,0,C["red"]))

    def _guess_os(self,target):
        try:
            cmd=(["ping","-n","1","-w","1000",target] if platform.system()=="Windows"
                 else ["ping","-c","1","-W","1",target])
            out=subprocess.run(cmd,capture_output=True,text=True,timeout=5).stdout.upper()
            if "TTL=128" in out or "TTL=127" in out: return "Windows (TTL~128)"
            if "TTL=64"  in out or "TTL=63"  in out: return "Linux/macOS (TTL~64)"
            if "TTL=255" in out:                      return "Network Device (TTL~255)"
            if "TTL="    in out:                      return "Unknown OS"
            return "No Response"
        except: return "OS Detect Failed"

    def _draw_heatmap(self):
        c=self.heatmap_canvas; c.delete("all")
        W=c.winfo_width() or 500; H=28
        c.create_rectangle(0,0,W,H,fill=C["dark"],outline="")
        c.create_text(4,4,text="PORT HEATMAP 0-1024",fill=C["dim"],font=FM,anchor="nw")
        for port in self._scan_open:
            if port<=1024:
                x=int(port/1024*(W-6))+3
                col=C["red"] if port in TRACKER_PORTS else C["glow"]
                c.create_line(x,8,x,H-2,fill=col,width=2)
        # Danger zone labels
        for p,lbl in [(22,"SSH"),(80,"HTTP"),(443,"HTTPS"),(3389,"RDP")]:
            x=int(p/1024*(W-6))+3
            c.create_text(x,6,text=lbl,fill=C["dim"],font=FM,anchor="s")

    def _scan_log(self,text,tag="info"):
        self.scan_log.config(state="normal")
        self.scan_log.insert("end",text+"\n",tag)
        self.scan_log.see("end")
        self.scan_log.config(state="disabled")

    def _save_scan_report(self,auto=False):
        if not self.scan_history:
            if not auto: messagebox.showinfo("No Data","Run a scan first."); return
        if auto:
            path=f"noc_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            path=filedialog.asksaveasfilename(
                title="Save Scan Report",
                defaultextension=".txt",
                filetypes=[("Text","*.txt"),("JSON","*.json"),("All","*.*")],
                initialfile=f"noc_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if not path: return
        if path.endswith(".json"):
            with open(path,"w") as f: json.dump(self.scan_history,f,indent=2)
        else:
            lines=["="*60,"  GREY NOC V2 — SCAN REPORT",
                   f"  {datetime.now().isoformat()}","="*60]
            for sc in self.scan_history:
                lines+=[f"\nTARGET:  {sc['target']}",f"TIME:    {sc['time']}",
                        f"SCANNED: {sc['ports_scanned']}  OPEN: {len(sc['open_ports'])}",
                        f"OS:      {sc['os_guess']}","OPEN:"]
                for p in sc["open_ports"]:
                    bn=sc["banners"].get(p,"")
                    flag="⚠" if p in TRACKER_PORTS else " "
                    lines.append(f"  {flag} {p:<6}{SVC_DB.get(p,'?'):<14}{bn}")
                lines.append("-"*40)
            with open(path,"w") as f: f.write("\n".join(lines))
        self._add_alert(f"Scan saved: {os.path.basename(path)}")
        if not auto: messagebox.showinfo("Saved",f"Saved:\n{path}")

    def _show_scan_history(self):
        if not self.scan_history:
            messagebox.showinfo("No History","No scans yet."); return
        win=tk.Toplevel(self); win.title("SCAN HISTORY")
        win.configure(bg=C["bg"]); win.geometry("700x400")
        st=scrolledtext.ScrolledText(win,bg=C["bg"],fg=C["glow"],font=FM,relief="flat")
        st.pack(fill="both",expand=True,padx=4,pady=4)
        for sc in reversed(self.scan_history):
            st.insert("end",
                f"[{sc['time']}] {sc['target']}  "
                f"{len(sc['open_ports'])}/{sc['ports_scanned']} open  "
                f"OS:{sc['os_guess']}\n")
            if sc["open_ports"]:
                st.insert("end",f"  → {','.join(str(p) for p in sc['open_ports'])}\n")
            st.insert("end","─"*55+"\n")

    # ── PING / TRACEROUTE / WHOIS ──────────────────────────────────────────────
    def _do_ping(self,target):
        self._scan_log(f"\n[PING → {target}]","info")
        def run():
            try:
                cmd=(["ping","-n","4",target] if platform.system()=="Windows"
                     else ["ping","-c","4",target])
                out=subprocess.run(cmd,capture_output=True,text=True,timeout=15).stdout
                for line in out.splitlines():
                    if line.strip():
                        self.after(0,lambda l=line:self._scan_log(l,"ping"))
            except Exception as e:
                self.after(0,lambda:self._scan_log(f"PING ERR: {e}","warn"))
        threading.Thread(target=run,daemon=True).start()

    def _do_traceroute(self,target):
        self._scan_log(f"\n[TRACEROUTE → {target}]","info")
        def run():
            try:
                cmd=(["tracert","-h","15","-w","1000",target]
                     if platform.system()=="Windows"
                     else ["traceroute","-m","15",target])
                proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,text=True)
                for line in proc.stdout:
                    if line.strip():
                        self.after(0,lambda l=line.rstrip():self._scan_log(l,"trace"))
            except Exception as e:
                self.after(0,lambda:self._scan_log(f"TRACE ERR: {e}","warn"))
        threading.Thread(target=run,daemon=True).start()

    def _do_whois(self,target):
        self._scan_log(f"\n[WHOIS → {target}]","info")
        def run():
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(8); s.connect(("whois.iana.org",43))
                s.send((target+"\r\n").encode())
                resp=b""
                while True:
                    chunk=s.recv(4096)
                    if not chunk: break
                    resp+=chunk
                s.close()
                for line in resp.decode("utf-8","ignore").splitlines()[:30]:
                    self.after(0,lambda l=line:self._scan_log(l,"banner"))
            except Exception as e:
                self.after(0,lambda:self._scan_log(f"WHOIS ERR: {e}","warn"))
        threading.Thread(target=run,daemon=True).start()

    # ══════════════════════════════════════════════════════════════════════════
    # AIRPLANE MODE
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_airplane(self):
        self.airplane_mode=not self.airplane_mode
        if self.airplane_mode: threading.Thread(target=self._airplane_on,daemon=True).start()
        else:                  threading.Thread(target=self._airplane_off,daemon=True).start()

    def _airplane_on(self):
        try:
            if platform.system()=="Windows":
                for iface in ["Wi-Fi","Ethernet","Local Area Connection"]:
                    subprocess.run(["netsh","interface","set","interface",
                                    iface,"admin=disable"],capture_output=True,timeout=10)
            else: subprocess.run(["nmcli","radio","all","off"],timeout=10)
        except Exception as e: self.after(0,lambda:self._add_alert(f"KILL ERR:{e}"))
        self.after(0,self._update_kill_ui)
        self.after(0,lambda:self._add_alert("✈ AIRPLANE MODE ON"))

    def _airplane_off(self):
        try:
            if platform.system()=="Windows":
                for iface in ["Wi-Fi","Ethernet","Local Area Connection"]:
                    subprocess.run(["netsh","interface","set","interface",
                                    iface,"admin=enable"],capture_output=True,timeout=10)
            else: subprocess.run(["nmcli","radio","all","on"],timeout=10)
        except Exception as e: self.after(0,lambda:self._add_alert(f"KILL ERR:{e}"))
        self.after(0,self._update_kill_ui)
        self.after(0,lambda:self._add_alert("✈ AIRPLANE MODE OFF"))

    def _update_kill_ui(self):
        if self.airplane_mode:
            self.btn_kill.config(text="✈ KILL: ACTIVE",bg=C["red"],fg="#fff")
            self.btn_kill2.config(bg=C["red"],fg="#fff",text="✈ AIRPLANE MODE: ON")
            self.lbl_net.config(text="● NETWORK: ✈ OFFLINE",fg=C["red"])
        else:
            self.btn_kill.config(text="✈ KILL SWITCH: OFF",bg=C["dim"],fg=C["bg"])
            self.btn_kill2.config(bg=C["red_dim"],fg=C["red"],text="✈ TOGGLE AIRPLANE MODE")
            self.lbl_net.config(text="● NETWORK: ONLINE",fg=C["glow"])

    # ══════════════════════════════════════════════════════════════════════════
    # EXPORT
    # ══════════════════════════════════════════════════════════════════════════
    def _export_data(self,fmt="csv"):
        exts={"csv":".csv","json":".json","txt":".txt"}
        path=filedialog.asksaveasfilename(
            title="Export NOC Data",defaultextension=exts[fmt],
            filetypes=[(fmt.upper(),f"*{exts[fmt]}"),("All","*.*")],
            initialfile=f"grey_noc_{datetime.now().strftime('%Y%m%d_%H%M%S')}{exts[fmt]}")
        if not path: return
        elapsed=datetime.now()-self.session_start
        data={"export_time":datetime.now().isoformat(),
              "uptime_s":int(elapsed.total_seconds()),
              "local_ip":self.my_ip,
              "total_packets":self.pkt_count,"tcp":self.tcp_count,
              "udp":self.udp_count,"icmp":self.icmp_count,"arp":self.arp_count,
              "total_bytes":self.total_bytes,
              "hosts":{ip:{"pkts":v["pkts"],"bytes":v["bytes"],
                            "proto":v.get("proto","?"),"last":v["last_seen"]}
                       for ip,v in self.hosts.items()},
              "alerts":list(self.alert_log),
              "scan_history":self.scan_history,
              "tracker_hits":{"total":self._tracker_hits_count,
                               "ports":self._tracker_port_hits,
                               "geo":self._tracker_geo_hits,
                               "volume":self._tracker_vol_hits}}
        try:
            if fmt=="json":
                with open(path,"w") as f: json.dump(data,f,indent=2)
            elif fmt=="csv":
                with open(path,"w",newline="") as f:
                    w=csv.writer(f)
                    w.writerow(["GREY NOC V2",datetime.now().isoformat()])
                    w.writerow([])
                    for k,v in list(data.items()):
                        if not isinstance(v,(dict,list)): w.writerow([k,v])
                    w.writerow([]); w.writerow(["IP","PKTS","BYTES","PROTO","LAST"])
                    for ip,v in data["hosts"].items():
                        w.writerow([ip,v["pkts"],v["bytes"],v["proto"],v["last"]])
            elif fmt=="txt":
                h,rem=divmod(int(elapsed.total_seconds()),3600); m,s=divmod(rem,60)
                lines=["="*60," GREY NOC V2 — FULL EXPORT",
                       f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}","="*60,"",
                       "SESSION",f"  IP: {self.my_ip}",
                       f"  Uptime: {h:02d}:{m:02d}:{s:02d}",
                       f"  Packets: {self.pkt_count} (TCP:{self.tcp_count} UDP:{self.udp_count})",
                       f"  Bytes: {self.total_bytes:,}","","HOSTS","-"*40]
                for ip,v in sorted(data["hosts"].items(),
                                   key=lambda x:x[1]["pkts"],reverse=True):
                    lines.append(f"  {ip:<18}pkts={v['pkts']:<6}bytes={v['bytes']//1024}KB")
                if self.scan_history:
                    lines+=["","SCAN HISTORY","-"*40]
                    for sc in self.scan_history:
                        lines.append(f"  [{sc['time']}] {sc['target']} "
                                     f"{len(sc['open_ports'])}/{sc['ports_scanned']} open")
                lines+=["","ALERTS","-"*40]
                lines+=[f"  {a}" for a in list(self.alert_log)[:50]]
                with open(path,"w") as f: f.write("\n".join(lines))
            self._add_alert(f"EXPORT: {os.path.basename(path)}")
            messagebox.showinfo("Exported",f"Saved:\n{path}")
        except Exception as e: messagebox.showerror("Export Failed",str(e))

    # ══════════════════════════════════════════════════════════════════════════
    # CAPTURE & SIMULATION
    # ══════════════════════════════════════════════════════════════════════════
    def _toggle_sniff(self):
        if not self.sniffing: self._start_sniff()
        else:                 self._stop_sniff()

    def _start_sniff(self):
        if not HAS_SCAPY:
            self._add_alert("Scapy not available — simulation mode")
            self._simulate_traffic(); return
        self.sniffing=True
        self.btn_sniff.config(text="⏹ STOP CAPTURE",fg=C["red"])
        self._add_alert(f"Capture started on {self.my_ip}")
        self.sniff_thread=threading.Thread(
            target=lambda:sniff(prn=self._handle_packet,store=False,
                                stop_filter=lambda x:not self.sniffing),daemon=True)
        self.sniff_thread.start()

    def _stop_sniff(self):
        self.sniffing=False
        self.btn_sniff.config(text="▶ START CAPTURE",fg=C["glow"])
        self._add_alert("Capture stopped")

    def _handle_packet(self,pkt):
        try:
            self.pkt_count+=1; length=len(pkt); self.total_bytes+=length
            src=dst=proto=info=""; tag="other"; col=C["dim"]
            if IP in pkt:
                src=pkt[IP].src; dst=pkt[IP].dst
                if TCP in pkt:
                    proto="TCP";tag="tcp";self.tcp_count+=1
                    sport=pkt[TCP].sport; dport=pkt[TCP].dport
                    info=f":{sport}→{dport}";col=C["glow"]
                    if self.hosts.get(src): self.hosts[src]["dport"]=dport
                elif UDP in pkt:
                    proto="UDP";tag="udp";self.udp_count+=1
                    info=f":{pkt[UDP].sport}→{pkt[UDP].dport}";col=C["blue"]
                elif ICMP in pkt:
                    proto="ICMP";tag="icmp";self.icmp_count+=1
                    info=f"t={pkt[ICMP].type}";col=C["amber"]
                else: proto="IP"
            elif ARP in pkt:
                src=pkt[ARP].psrc;dst=pkt[ARP].pdst
                proto="ARP";tag="arp";self.arp_count+=1
                info=f"who-has {dst}";col=C["mid"]
            else: return
            for ip in [src,dst]:
                if ip not in self.hosts:
                    self.hosts[ip]={"pkts":0,"bytes":0,"last_seen":"",
                                    "proto":proto,"dport":0}
                self.hosts[ip]["pkts"]+=1;self.hosts[ip]["bytes"]+=length
                self.hosts[ip]["last_seen"]=ts();self.hosts[ip]["proto"]=proto
            self.bw_in+=length
            self._register_map_node(src,col);self._register_map_node(dst,col)
            if random.random()<0.3: self._add_map_connection(src,dst,col)
            if self.hosts[src]["pkts"]==1:
                a=random.uniform(0,360);d=random.uniform(0.2,0.95)
                self.radar_blips.append((a,d,0,col))
            self.after(0,lambda:self._log_packet(ts(),src,dst,proto,str(length),info,tag))
        except: pass

    def _simulate_traffic(self):
        PROTOS=[("TCP",C["glow"],"tcp"),("UDP",C["blue"],"udp"),
                ("ICMP",C["amber"],"icmp"),("ARP",C["mid"],"arp")]
        HOSTS=["192.168.1.1","192.168.1.100","10.0.0.1","8.8.8.8","8.8.4.4",
               "1.1.1.1","1.0.0.1","52.94.228.167","35.190.0.1","104.18.20.15",
               "185.199.108.153","91.108.56.180","203.0.113.5","125.209.222.141",
               "27.107.0.1","200.143.0.1","41.58.0.1","103.31.4.1","60.28.202.119"]
        def _sim():
            while self.running:
                src=random.choice(HOSTS);dst=random.choice(HOSTS)
                if src==dst: continue
                proto,col,tag=random.choice(PROTOS)
                sport=random.randint(1024,65535)
                dport=random.choice([80,443,22,53,3389,8080,25,110,445,9050,3128])
                size=random.randint(40,1500);info=f":{sport}→{dport}"
                self.pkt_count+=1;self.total_bytes+=size
                if tag=="tcp":  self.tcp_count+=1
                elif tag=="udp": self.udp_count+=1
                elif tag=="icmp":self.icmp_count+=1
                elif tag=="arp": self.arp_count+=1
                for ip in [src,dst]:
                    if ip not in self.hosts:
                        self.hosts[ip]={"pkts":0,"bytes":0,"last_seen":"",
                                         "proto":proto,"dport":dport}
                    self.hosts[ip]["pkts"]+=1;self.hosts[ip]["bytes"]+=size
                    self.hosts[ip]["last_seen"]=ts()
                    self.hosts[ip]["proto"]=proto;self.hosts[ip]["dport"]=dport
                self.bw_in+=size*random.uniform(0.4,1.0)
                self.bw_out+=size*random.uniform(0.1,0.5)
                self._register_map_node(src,col);self._register_map_node(dst,col)
                if random.random()<0.3: self._add_map_connection(src,dst,col)
                if random.random()<0.1:
                    a=random.uniform(0,360);d=random.uniform(0.2,0.95)
                    self.radar_blips.append((a,d,0,col))
                self.after(0,lambda s=src,d2=dst,pr=proto,sz=size,
                           inf=info,tg=tag:
                           self._log_packet(ts(),s,d2,pr,str(sz),inf,tg))
                time.sleep(random.uniform(0.04,0.22))
        threading.Thread(target=_sim,daemon=True).start()
        self._add_alert("Simulation: synthetic traffic active")

    def _add_alert(self,msg):
        self.alert_log.appendleft(f"[{ts()}] {msg}")

    # ══════════════════════════════════════════════════════════════════════════
    # LOOPS
    # ══════════════════════════════════════════════════════════════════════════
    def _start_loops(self):
        self._loop_clock()
        self._loop_radar()
        self._loop_earth()
        self._loop_map()
        self._loop_bw()
        self._loop_ui()
        self.after(500,self._simulate_traffic)

    def _loop_clock(self):
        self.lbl_time.config(text=datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000,self._loop_clock)
    def _loop_radar(self):
        self.radar_angle=(self.radar_angle+2.5)%360; self._draw_radar()
        self.after(40,self._loop_radar)
    def _loop_earth(self):
        self.earth_angle=(self.earth_angle+0.4)%360; self._draw_earth()
        self.after(40,self._loop_earth)
    def _loop_map(self):
        self._draw_world_map(); self.after(400,self._loop_map)
    def _loop_bw(self):
        self.bw_history.append((self.bw_in,self.bw_out))
        self.bw_in=0;self.bw_out=0; self._draw_bw()
        self.after(1000,self._loop_bw)
    def _loop_ui(self):
        self._update_stats(); self._update_hosts()
        self.after(1500,self._loop_ui)

    def on_close(self):
        self.running=False;self.sniffing=False;self._scan_running=False
        self._live_tracker_active=False;self._sched_running=False
        self.destroy()

# ══════════════════════════════════════════════════════════════════════════════
if __name__=="__main__":
    if platform.system()=="Windows":
        try:
            import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except: pass
    app=GreyNOC()
    app.protocol("WM_DELETE_WINDOW",app.on_close)
    app.mainloop()
