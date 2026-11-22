# -*- coding: utf-8 -*-
import os
import sys
import json
import math
import time
import uuid
import random
import subprocess
import threading
import urllib.request
import tkinter as tk
from tkinter import messagebox
import minecraft_launcher_lib

APP_TITLE = "SLIME CLIENT 26.2"
MC_VERSION = "26.2"
APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".slimeclient")
CONFIG_PATH = os.path.join(APP_DIR, "slime_launcher_config.json")


class SlimeClientApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Slime Client 26.2")
        self.root.geometry("1040x640")
        self.root.minsize(820, 540)
        self.root.configure(bg="#040806")
        self.root.resizable(True, True)

        self.is_fullscreen = False
        self.is_launching = False
        self.particles = []
        self.selected_ram = 4

        self.username_var = tk.StringVar(value="SlimeOyuncu")
        self.mc_fullscreen_var = tk.BooleanVar(value=True)
        self.safe_mods_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="● Sistem hazır • Minecraft 26.2 Fabric")

        self.load_config()

        # Ana arka plan tuvali (Siyah-Yeşil dinamik tema)
        self.bg_canvas = tk.Canvas(self.root, bg="#040806", highlightthickness=0, bd=0)
        self.bg_canvas.pack(fill="both", expand=True)

        # Merkez kontrol paneli
        self.card_outer = tk.Frame(self.bg_canvas, bg="#22C55E", padx=2, pady=2)
        self.card = tk.Frame(self.card_outer, bg="#08110C", padx=32, pady=24)
        self.card.pack(fill="both", expand=True)

        self.build_card_ui()
        self.card_window = self.bg_canvas.create_window(520, 320, window=self.card_outer, anchor="center")

        self.init_particles(34)
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.bg_canvas.bind("<Configure>", self.on_resize)

        self.draw_static_background(1040, 640)
        self.animate_background()

    def load_config(self):
        try:
            os.makedirs(APP_DIR, exist_ok=True)
            if os.path.exists(CONFIG_PATH):
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("username"):
                    self.username_var.set(data["username"])
                if isinstance(data.get("ram"), int) and data["ram"] in (2, 4, 6, 8):
                    self.selected_ram = data["ram"]
                if isinstance(data.get("mc_fullscreen"), bool):
                    self.mc_fullscreen_var.set(data["mc_fullscreen"])
        except Exception:
            pass

    def save_config(self):
        try:
            os.makedirs(APP_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "username": self.username_var.get().strip() or "SlimeOyuncu",
                        "ram": self.selected_ram,
                        "mc_fullscreen": self.mc_fullscreen_var.get(),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    def build_card_ui(self):
        # Üst Bar: Logo + Başlık + Tam Ekran & Klasör Butonları
        top_bar = tk.Frame(self.card, bg="#08110C")
        top_bar.pack(fill="x", pady=(0, 18))

        # Özel çizim Slime Küpü İkonu
        logo_canvas = tk.Canvas(top_bar, width=46, height=46, bg="#08110C", highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 14))
        logo_canvas.create_rectangle(3, 3, 43, 43, fill="#16A34A", outline="#4ADE80", width=2)
        logo_canvas.create_rectangle(9, 9, 37, 37, fill="#15803D", outline="")
        logo_canvas.create_rectangle(13, 16, 19, 22, fill="#041309", outline="")
        logo_canvas.create_rectangle(27, 16, 33, 22, fill="#041309", outline="")
        logo_canvas.create_rectangle(20, 26, 26, 31, fill="#041309", outline="")

        title_box = tk.Frame(top_bar, bg="#08110C")
        title_box.pack(side="left")

        tk.Label(
            title_box,
            text=APP_TITLE,
            font=("Segoe UI", 20, "bold"),
            fg="#ECFDF5",
            bg="#08110C",
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="FABRIC PVP & FPS ENGINE  •  SİYAH-ZÜMRÜT SÜRÜM",
            font=("Segoe UI", 9, "bold"),
            fg="#22C55E",
            bg="#08110C",
        ).pack(anchor="w")

        # Sağ üst kontrol butonları
        controls_box = tk.Frame(top_bar, bg="#08110C")
        controls_box.pack(side="right", anchor="n")

        self.fs_btn = tk.Button(
            controls_box,
            text="⛶ TAM EKRAN (F11)",
            font=("Segoe UI", 9, "bold"),
            fg="#ECFDF5",
            bg="#0F2418",
            activebackground="#16A34A",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.toggle_fullscreen,
        )
        self.fs_btn.pack(side="left", padx=(0, 8))

        mods_btn = tk.Button(
            controls_box,
            text="📁 MODLAR",
            font=("Segoe UI", 9, "bold"),
            fg="#A7F3D0",
            bg="#0F2418",
            activebackground="#15803D",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.open_mods_folder,
        )
        mods_btn.pack(side="left")

        # Ayırıcı neon çizgi
        tk.Frame(self.card, bg="#143823", height=1).pack(fill="x", pady=(0, 18))

        # Oyuncu Adı Bölümü
        tk.Label(
            self.card,
            text="OYUNCU ADI (KULLANICI ADI)",
            font=("Segoe UI", 9, "bold"),
            fg="#86EFAC",
            bg="#08110C",
        ).pack(anchor="w", pady=(0, 6))

        entry_border = tk.Frame(self.card, bg="#1E5634", padx=2, pady=2)
        entry_border.pack(fill="x", pady=(0, 16))

        self.username_entry = tk.Entry(
            entry_border,
            textvariable=self.username_var,
            font=("Segoe UI", 13, "bold"),
            fg="#FFFFFF",
            bg="#0C1912",
            insertbackground="#22C55E",
            relief="flat",
            bd=8,
        )
        self.username_entry.pack(fill="x")

        # RAM Seçimi Bölümü
        tk.Label(
            self.card,
            text="BELLEK (RAM) AYIRMA",
            font=("Segoe UI", 9, "bold"),
            fg="#86EFAC",
            bg="#08110C",
        ).pack(anchor="w", pady=(0, 6))

        ram_row = tk.Frame(self.card, bg="#08110C")
        ram_row.pack(fill="x", pady=(0, 16))

        self.ram_buttons = {}
        for gb in (2, 4, 6, 8):
            btn = tk.Button(
                ram_row,
                text=f"{gb} GB RAM",
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                bd=0,
                pady=8,
                cursor="hand2",
                command=lambda val=gb: self.set_ram(val),
            )
            btn.pack(side="left", expand=True, fill="x", padx=4)
            self.ram_buttons[gb] = btn
        self.refresh_ram_buttons()

        # Seçenekler Kutusu
        opts_box = tk.Frame(self.card, bg="#0B1710", padx=14, pady=10)
        opts_box.pack(fill="x", pady=(0, 18))

        tk.Checkbutton(
            opts_box,
            text="Minecraft'ı doğrudan Tam Ekranda başlat",
            variable=self.mc_fullscreen_var,
            font=("Segoe UI", 10, "bold"),
            fg="#D1FAE5",
            bg="#0B1710",
            selectcolor="#06120B",
            activebackground="#0B1710",
            activeforeground="#4ADE80",
            cursor="hand2",
        ).pack(anchor="w")

        tk.Checkbutton(
            opts_box,
            text="Eksik temel FPS modlarını kontrol et (Sodium / Lithium / Fabric API)",
            variable=self.safe_mods_var,
            font=("Segoe UI", 9),
            fg="#86EFAC",
            bg="#0B1710",
            selectcolor="#06120B",
            activebackground="#0B1710",
            activeforeground="#4ADE80",
            cursor="hand2",
        ).pack(anchor="w", pady=(4, 0))

        # Ana OYNA Butonu
        self.play_btn = tk.Button(
            self.card,
            text="▶   OYNA   (MINECRAFT 26.2)",
            font=("Segoe UI", 14, "bold"),
            fg="#031208",
            bg="#22C55E",
            activebackground="#4ADE80",
            activeforeground="#031208",
            relief="flat",
            bd=0,
            pady=14,
            cursor="hand2",
            command=self.start_launch,
        )
        self.play_btn.pack(fill="x", pady=(0, 14))
        self.play_btn.bind("<Enter>", lambda e: self.play_btn.configure(bg="#4ADE80") if not self.is_launching else None)
        self.play_btn.bind("<Leave>", lambda e: self.play_btn.configure(bg="#22C55E") if not self.is_launching else None)

        # İlerleme Çubuğu ve Durum Satırı
        self.progress_bg = tk.Canvas(self.card, height=8, bg="#0E1F15", highlightthickness=0)
        self.progress_bg.pack(fill="x", pady=(0, 8))
        self.progress_bar = self.progress_bg.create_rectangle(0, 0, 0, 8, fill="#22C55E", outline="")

        footer = tk.Frame(self.card, bg="#08110C")
        footer.pack(fill="x")

        tk.Label(
            footer,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "bold"),
            fg="#6EE7B7",
            bg="#08110C",
        ).pack(side="left")

        tk.Label(
            footer,
            text="F11: Tam Ekran  •  ESC: Çıkış",
            font=("Segoe UI", 8),
            fg="#4B7A5E",
            bg="#08110C",
        ).pack(side="right")

    def set_ram(self, gb: int):
        self.selected_ram = gb
        self.refresh_ram_buttons()

    def refresh_ram_buttons(self):
        for gb, btn in self.ram_buttons.items():
            if gb == self.selected_ram:
                btn.configure(bg="#16A34A", fg="#FFFFFF")
            else:
                btn.configure(bg="#0E1F15", fg="#86EFAC")

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.fs_btn.configure(text="🗗 PENCERE (ESC)", bg="#16A34A")
        else:
            self.fs_btn.configure(text="⛶ TAM EKRAN (F11)", bg="#0F2418")

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.fs_btn.configure(text="⛶ TAM EKRAN (F11)", bg="#0F2418")

    def open_mods_folder(self):
        mods_dir = os.path.join(APP_DIR, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        os.startfile(mods_dir)

    def set_progress(self, percent: float, text: str):
        def _update():
            self.status_var.set(text)
            w = max(1, self.progress_bg.winfo_width())
            fill_w = int((max(0.0, min(100.0, percent)) / 100.0) * w)
            self.progress_bg.coords(self.progress_bar, 0, 0, fill_w, 8)
        self.root.after(0, _update)

    # Dinamik Siyah-Yeşil Arka Plan Çizimi
    def init_particles(self, count: int):
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": random.uniform(0.0, 1.0),
                "y": random.uniform(0.0, 1.0),
                "r": random.uniform(4.0, 18.0),
                "speed": random.uniform(0.0008, 0.0026),
                "drift": random.uniform(-0.0005, 0.0005),
                "phase": random.uniform(0, math.pi * 2),
                "tone": random.choice(["#0B3B20", "#115E33", "#15803D", "#16A34A"]),
            })

    def draw_static_background(self, w: int, h: int):
        self.bg_canvas.delete("static_bg")
        if w <= 10 or h <= 10:
            return

        # Dikey siyah -> koyu zümrüt geçiş bantları
        bands = 28
        for i in range(bands):
            t = i / float(bands - 1)
            glow = math.sin(t * math.pi)
            r = int(4 + glow * 8)
            g = int(8 + glow * 34)
            b = int(6 + glow * 18)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y1 = int((i / bands) * h)
            y2 = int(((i + 1) / bands) * h) + 1
            self.bg_canvas.create_rectangle(0, y1, w, y2, fill=color, outline="", tags="static_bg")

        # İnce neon-zümrüt siber ızgara çizgileri
        step = 56
        for x in range(0, w, step):
            self.bg_canvas.create_line(x, 0, x, h, fill="#091D12", width=1, tags="static_bg")
        for y in range(0, h, step):
            self.bg_canvas.create_line(0, y, w, y, fill="#091D12", width=1, tags="static_bg")

        # Köşe dekoratif yeşil enerji çerçeveleri
        pad = 18
        arm = 48
        accent = "#16A34A"
        self.bg_canvas.create_line(pad, pad, pad + arm, pad, fill=accent, width=2, tags="static_bg")
        self.bg_canvas.create_line(pad, pad, pad, pad + arm, fill=accent, width=2, tags="static_bg")

        self.bg_canvas.create_line(w - pad, pad, w - pad - arm, pad, fill=accent, width=2, tags="static_bg")
        self.bg_canvas.create_line(w - pad, pad, w - pad, pad + arm, fill=accent, width=2, tags="static_bg")

        self.bg_canvas.create_line(pad, h - pad, pad + arm, h - pad, fill=accent, width=2, tags="static_bg")
        self.bg_canvas.create_line(pad, h - pad, pad, h - pad - arm, fill=accent, width=2, tags="static_bg")

        self.bg_canvas.create_line(w - pad, h - pad, w - pad - arm, h - pad, fill=accent, width=2, tags="static_bg")
        self.bg_canvas.create_line(w - pad, h - pad, w - pad, h - pad - arm, fill=accent, width=2, tags="static_bg")

        self.bg_canvas.tag_lower("static_bg")

    def on_resize(self, event):
        w, h = event.width, event.height
        self.bg_canvas.coords(self.card_window, w // 2, h // 2)
        self.draw_static_background(w, h)

    def animate_background(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        self.bg_canvas.delete("slime_orb")

        if w > 20 and h > 20:
            now = time.time()
            for p in self.particles:
                p["y"] -= p["speed"]
                p["x"] += p["drift"] + math.sin(now * 1.4 + p["phase"]) * 0.0003
                if p["y"] < -0.05:
                    p["y"] = 1.05
                    p["x"] = random.uniform(0.0, 1.0)
                if p["x"] < 0.0:
                    p["x"] = 1.0
                elif p["x"] > 1.0:
                    p["x"] = 0.0

                cx = p["x"] * w
                cy = p["y"] * h
                r = p["r"]

                self.bg_canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=p["tone"], outline="#22C55E", width=1, tags="slime_orb"
                )
                # Slime küresi iç parlama noktası
                hr = max(2.0, r * 0.28)
                self.bg_canvas.create_oval(
                    cx - r * 0.45, cy - r * 0.45,
                    cx - r * 0.45 + hr, cy - r * 0.45 + hr,
                    fill="#86EFAC", outline="", tags="slime_orb"
                )

            self.bg_canvas.tag_raise("slime_orb", "static_bg")

        self.root.after(35, self.animate_background)

    # Oyun Başlatma İşlemi
    def start_launch(self):
        if self.is_launching:
            return
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Uyarı", "Lütfen bir oyuncu adı girin.")
            return

        self.save_config()
        self.is_launching = True
        self.play_btn.configure(text="⏳  HAZIRLANIYOR...", bg="#15803D", state="disabled")
        threading.Thread(target=self.launch_worker, args=(username,), daemon=True).start()

    def ensure_safe_mods(self, mods_dir: str):
        os.makedirs(mods_dir, exist_ok=True)
        existing = [f.lower() for f in os.listdir(mods_dir)]
        targets = [
            ("fabric-api", "fabric-api"),
            ("sodium", "sodium"),
            ("lithium", "lithium"),
        ]
        for slug, prefix in targets:
            if any(prefix in name for name in existing):
                continue
            try:
                api_url = f'https://api.modrinth.com/v2/project/{slug}/version?game_versions=%5B%2226.2%22%5D&loaders=%5B%22fabric%22%5D'
                req = urllib.request.Request(api_url, headers={"User-Agent": "SlimeClient/26.2"})
                versions = json.loads(urllib.request.urlopen(req, timeout=10).read().decode("utf-8"))
                if versions:
                    file_info = versions[0]["files"][0]
                    dest = os.path.join(mods_dir, file_info["filename"])
                    urllib.request.urlretrieve(file_info["url"], dest)
            except Exception:
                pass

    def find_installed_fabric_version(self) -> str:
        versions_dir = os.path.join(APP_DIR, "versions")
        if os.path.isdir(versions_dir):
            for name in sorted(os.listdir(versions_dir), reverse=True):
                if name.startswith("fabric-loader-") and name.endswith(f"-{MC_VERSION}"):
                    json_file = os.path.join(versions_dir, name, f"{name}.json")
                    if os.path.exists(json_file):
                        return name
        return ""

    def launch_worker(self, username: str):
        try:
            os.makedirs(APP_DIR, exist_ok=True)
            mods_dir = os.path.join(APP_DIR, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            if self.safe_mods_var.get():
                self.set_progress(20, "● Temel FPS modları kontrol ediliyor...")
                self.ensure_safe_mods(mods_dir)

            self.set_progress(45, "● Fabric 26.2 profili doğrulanıyor...")
            fabric_ver_id = self.find_installed_fabric_version()

            if not fabric_ver_id:
                self.set_progress(60, "● Fabric 26.2 kuruluyor (ilk seferde 1-2 dk sürebilir)...")
                loader_ver = minecraft_launcher_lib.fabric.get_latest_loader_version()
                minecraft_launcher_lib.fabric.install_fabric(
                    MC_VERSION, APP_DIR, loader_version=loader_ver
                )
                fabric_ver_id = f"fabric-loader-{loader_ver}-{MC_VERSION}"

            self.set_progress(85, "● Minecraft 26.2 başlatılıyor...")
            offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}"))
            options = {
                "username": username,
                "uuid": offline_uuid,
                "token": "0",
                "jvmArguments": [
                    f"-Xmx{self.selected_ram}G",
                    f"-Xms{max(1, self.selected_ram // 2)}G",
                ],
                "launcherName": "SlimeClient",
                "launcherVersion": "26.2",
            }

            cmd = minecraft_launcher_lib.command.get_minecraft_command(
                fabric_ver_id, APP_DIR, options
            )
            if self.mc_fullscreen_var.get() and "--fullscreen" not in cmd:
                cmd.append("--fullscreen")

            self.set_progress(100, "● Oyun başlatıldı! İyi eğlenceler.")
            subprocess.Popen(cmd, cwd=APP_DIR)

            time.sleep(2.5)
            self.root.after(0, self.reset_launch_button)

        except Exception as err:
            self.root.after(0, self.reset_launch_button)
            self.set_progress(0, "● Başlatma sırasında hata oluştu.")
            self.root.after(0, lambda: messagebox.showerror("Başlatma Hatası", str(err)))

    def reset_launch_button(self):
        self.is_launching = False
        self.play_btn.configure(
            text="▶   OYNA   (MINECRAFT 26.2)",
            bg="#22C55E",
            state="normal",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SlimeClientApp(root)
    root.mainloop()
