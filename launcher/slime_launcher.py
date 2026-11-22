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

from slime_ui import (
    BG, SIDEBAR, CARD, BORDER, ACCENT, ACCENT_HI, ACCENT_DK, TEXT, MUTED, DIM, FONT,
    lerp_color, rrect, RButton, Card, Toggle, ProgressBar, NavItem, draw_slime,
)

APP_TITLE = "SLIME CLIENT"
MC_VERSION = "26.2"
APP_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".slimeclient")
CONFIG_PATH = os.path.join(APP_DIR, "slime_launcher_config.json")
PLAY_TEXT = "\u25B6   OYNA"


class SlimeClientApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Slime Client 26.2")
        self.root.geometry("1060x660")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        self.is_fullscreen = False
        self.is_launching = False
        self.selected_ram = 4
        self.blobs = []
        self.hero_w = 0
        self.hero_h = 0
        self.bg_img = None
        self.page = "play"

        self.username_var = tk.StringVar(value="SlimeOyuncu")
        self.mc_fullscreen_var = tk.BooleanVar(value=True)
        self.safe_mods_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Hazır")

        self.load_config()

        # --- Sol menü ---
        self.sidebar = tk.Frame(self.root, bg=SIDEBAR, width=230)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.build_sidebar()

        # --- Sağ içerik ---
        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(side="right", fill="both", expand=True)

        self.play_page = tk.Frame(self.content, bg=BG)
        self.settings_page = tk.Frame(self.content, bg=BG)
        self.build_play_page()
        self.build_settings_page()
        self.show_page("play")

        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        self.username_var.trace_add("write", lambda *a: self.refresh_info())
        self.status_var.trace_add("write", lambda *a: self.update_status_text())
        self.animate()

    # ------------------------------------------------------------------ config
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
                if isinstance(data.get("safe_mods"), bool):
                    self.safe_mods_var.set(data["safe_mods"])
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
                        "safe_mods": self.safe_mods_var.get(),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception:
            pass

    # ----------------------------------------------------------------- sidebar
    def build_sidebar(self):
        brand = tk.Canvas(self.sidebar, height=84, bg=SIDEBAR, highlightthickness=0)
        brand.pack(fill="x")
        rrect(brand, 22, 20, 62, 60, 11, fill=ACCENT, outline=ACCENT_HI, width=2)
        rrect(brand, 29, 27, 55, 53, 6, fill="#16A34A", outline="")
        for ex in (35, 46):
            brand.create_rectangle(ex, 35, ex + 4, 41, fill="#052E16", outline="")
        brand.create_rectangle(38, 46, 46, 49, fill="#052E16", outline="")
        brand.create_text(74, 33, text="SLIME", anchor="w", fill=TEXT, font=(FONT, 15, "bold"))
        brand.create_text(74, 52, text="CLIENT  \u2022  26.2", anchor="w", fill=ACCENT, font=(FONT, 8, "bold"))

        nav = tk.Frame(self.sidebar, bg=SIDEBAR)
        nav.pack(fill="x", padx=14, pady=(8, 0))
        self.nav_play = NavItem(nav, "\u25B6", "Oyna", lambda: self.show_page("play"))
        self.nav_play.pack(fill="x", pady=2)
        self.nav_settings = NavItem(nav, "\u2699", "Ayarlar", lambda: self.show_page("settings"))
        self.nav_settings.pack(fill="x", pady=2)
        self.nav_mods = NavItem(nav, "\u25A3", "Mod Klas\u00f6r\u00fc", self.open_mods_folder)
        self.nav_mods.pack(fill="x", pady=2)

        bottom = tk.Frame(self.sidebar, bg=SIDEBAR)
        bottom.pack(side="bottom", fill="x", padx=14, pady=16)

        # Oyuncu rozeti
        self.chip = tk.Canvas(bottom, height=56, bg=SIDEBAR, highlightthickness=0)
        self.chip.pack(fill="x", pady=(0, 10))
        self.chip.bind("<Configure>", lambda e: self.draw_chip())

        self.fs_btn = RButton(bottom, "\u26F6  Tam Ekran (F11)", self.toggle_fullscreen,
                              width=190, height=36, radius=10, bg="#16211B", hover="#1D2C23",
                              fg=MUTED, parent_bg=SIDEBAR, font=(FONT, 9, "bold"))
        self.fs_btn.pack(fill="x")

    def draw_chip(self):
        c = self.chip
        c.delete("all")
        w = c.winfo_width()
        if w < 20:
            return
        rrect(c, 0, 0, w, 56, 14, fill="#121B16", outline=BORDER)
        name = (self.username_var.get().strip() or "SlimeOyuncu")
        c.create_oval(12, 12, 44, 44, fill=ACCENT_DK, outline=ACCENT, width=2)
        c.create_text(28, 28, text=name[:1].upper(), fill="#ECFDF5", font=(FONT, 12, "bold"))
        c.create_text(54, 22, text=name[:16], anchor="w", fill=TEXT, font=(FONT, 10, "bold"))
        c.create_text(54, 38, text="\u00c7evrimd\u0131\u015f\u0131 profil", anchor="w", fill=MUTED, font=(FONT, 8))

    def show_page(self, name: str):
        self.page = name
        self.play_page.pack_forget()
        self.settings_page.pack_forget()
        if name == "play":
            self.play_page.pack(fill="both", expand=True)
        else:
            self.settings_page.pack(fill="both", expand=True)
        self.nav_play.set_active(name == "play")
        self.nav_settings.set_active(name == "settings")

    # --------------------------------------------------------------- play page
    def build_play_page(self):
        self.hero = tk.Canvas(self.play_page, bg=BG, highlightthickness=0, bd=0)
        self.hero.pack(fill="both", expand=True)

        self.play_btn = RButton(self.hero, PLAY_TEXT, self.start_launch, width=320, height=60,
                                radius=18, bg=ACCENT, hover=ACCENT_HI, fg="#04130A",
                                parent_bg=BG, font=(FONT, 16, "bold"))
        self.progress = ProgressBar(self.hero, width=320, height=8, parent_bg=BG)

        self.hero_items = {}
        self.play_win = self.hero.create_window(0, 0, window=self.play_btn, anchor="center")
        self.prog_win = self.hero.create_window(0, 0, window=self.progress, anchor="center")
        self.hero_items["title"] = self.hero.create_text(0, 0, text=APP_TITLE, fill=TEXT, font=(FONT, 34, "bold"))
        self.hero_items["sub"] = self.hero.create_text(
            0, 0, text="Minecraft 26.2  \u2022  Fabric  \u2022  PvP & FPS", fill=MUTED, font=(FONT, 11))
        self.hero_items["status"] = self.hero.create_text(0, 0, text="", fill=MUTED, font=(FONT, 9))
        self.hero_items["info"] = self.hero.create_text(0, 0, text="", fill=DIM, font=(FONT, 9, "bold"))

        self.init_blobs(14)
        self.hero.bind("<Configure>", self.on_hero_resize)
        self.update_status_text()
        self.refresh_info()

    def on_hero_resize(self, e):
        self.hero_w, self.hero_h = e.width, e.height
        if self._resize_job_pending():
            return
        self._resize_job = self.root.after(60, self.relayout_hero)

    def _resize_job_pending(self):
        job = getattr(self, "_resize_job", None)
        if job:
            try:
                self.root.after_cancel(job)
            except Exception:
                pass
        return False

    def relayout_hero(self):
        self._resize_job = None
        w, h = self.hero.winfo_width(), self.hero.winfo_height()
        if w < 50 or h < 50:
            return
        self.draw_background(w, h)
        mid = h * 0.5 - 10
        self.logo_base = (w / 2, mid - 70)
        self.hero.coords(self.hero_items["title"], w / 2, mid - 28 + 12)
        self.hero.coords(self.hero_items["sub"], w / 2, mid + 22)
        self.hero.coords(self.play_win, w / 2, mid + 82)
        self.hero.coords(self.prog_win, w / 2, mid + 138)
        self.hero.coords(self.hero_items["status"], w / 2, mid + 160)
        self.hero.coords(self.hero_items["info"], w / 2, h - 34)
        for key in ("title", "sub", "status", "info"):
            self.hero.tag_raise(self.hero_items[key])

    def draw_background(self, w, h):
        self.hero.delete("bgimg")
        img = tk.PhotoImage(width=w, height=h)
        top, bot = "#0A110D", "#07110B"
        glow = "#10301D"
        rows = []
        for y in range(h):
            t = y / max(1, h - 1)
            base = lerp_color(top, bot, t)
            rows.append(base)
        # Dikey geçiş (satır satır)
        for y, col in enumerate(rows):
            img.put(col, to=(0, y, w, y + 1))
        # Merkez parlaması: iç içe elips yerine, satır bazlı yumuşak yeşil bant
        cx_band = int(w * 0.5)
        for i in range(10):
            t = i / 9.0
            half = int(w * (0.48 - 0.04 * i))
            y0 = int(h * (0.12 + 0.02 * i))
            y1 = int(h * (0.80 - 0.03 * i))
            col = lerp_color("#0A110D", glow, t * 0.55)
            if half > 0 and y1 > y0:
                img.put(col, to=(max(0, cx_band - half), y0, min(w, cx_band + half), y1))
        self.bg_img = img
        self.hero.create_image(0, 0, image=img, anchor="nw", tags="bgimg")
        self.hero.tag_lower("bgimg")

    def init_blobs(self, n):
        self.blobs = []
        for _ in range(n):
            self.blobs.append({
                "x": random.uniform(0.0, 1.0),
                "y": random.uniform(0.0, 1.0),
                "r": random.uniform(5.0, 16.0),
                "speed": random.uniform(0.0006, 0.0018),
                "phase": random.uniform(0, math.pi * 2),
                "id": None,
            })

    def update_status_text(self):
        try:
            self.hero.itemconfigure(self.hero_items["status"], text=self.status_var.get())
        except Exception:
            pass

    def refresh_info(self):
        try:
            name = self.username_var.get().strip() or "SlimeOyuncu"
            self.hero.itemconfigure(
                self.hero_items["info"],
                text=f"{name}   \u2022   {self.selected_ram} GB RAM   \u2022   Fabric {MC_VERSION}",
            )
            self.draw_chip()
        except Exception:
            pass

    # ----------------------------------------------------------- settings page
    def build_settings_page(self):
        wrap = tk.Frame(self.settings_page, bg=BG)
        wrap.pack(fill="both", expand=True, padx=44, pady=34)

        tk.Label(wrap, text="Ayarlar", font=(FONT, 22, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        tk.Label(wrap, text="Profilini ve oyun performansını buradan ayarla.",
                 font=(FONT, 10), fg=MUTED, bg=BG).pack(anchor="w", pady=(2, 18))

        # --- Hesap kartı ---
        acc = Card(wrap)
        acc.pack(fill="x", pady=(0, 14))
        tk.Label(acc.inner, text="OYUNCU ADI", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w")
        entry_row = tk.Frame(acc.inner, bg=CARD)
        entry_row.pack(fill="x", pady=(8, 0))
        entry_card = Card(entry_row, parent_bg=CARD, fill="#0D1511", outline=BORDER, radius=12, pad=4)
        entry_card.pack(fill="x")
        self.username_entry = tk.Entry(
            entry_card.inner, textvariable=self.username_var, font=(FONT, 13), fg=TEXT,
            bg="#0D1511", insertbackground=ACCENT, relief="flat", bd=6,
            highlightthickness=0,
        )
        self.username_entry.pack(fill="x")
        self.username_entry.bind("<FocusIn>", lambda e: entry_card.set_outline(ACCENT))
        self.username_entry.bind("<FocusOut>", lambda e: entry_card.set_outline(BORDER))

        # --- RAM kartı ---
        ram = Card(wrap)
        ram.pack(fill="x", pady=(0, 14))
        head = tk.Frame(ram.inner, bg=CARD)
        head.pack(fill="x")
        tk.Label(head, text="BELLEK (RAM)", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(side="left")
        tk.Label(head, text="Daha fazla RAM = daha akıcı oyun (sistemine göre seç)",
                 font=(FONT, 8), fg=DIM, bg=CARD).pack(side="right")
        ram_row = tk.Frame(ram.inner, bg=CARD)
        ram_row.pack(fill="x", pady=(10, 0))
        self.ram_buttons = {}
        for gb in (2, 4, 6, 8):
            b = RButton(ram_row, f"{gb} GB", lambda v=gb: self.set_ram(v), width=100, height=40,
                        radius=12, parent_bg=CARD, font=(FONT, 10, "bold"))
            b.pack(side="left", expand=True, fill="x", padx=(0 if gb == 2 else 8, 0))
            self.ram_buttons[gb] = b
        self.refresh_ram_buttons()

        # --- Oyun seçenekleri kartı ---
        opts = Card(wrap)
        opts.pack(fill="x")
        tk.Label(opts.inner, text="OYUN", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w", pady=(0, 6))
        self.make_toggle_row(opts.inner, "Minecraft'ı tam ekranda başlat",
                             "Oyun açıldığında doğrudan tam ekran olur.", self.mc_fullscreen_var)
        tk.Frame(opts.inner, bg=BORDER, height=1).pack(fill="x", pady=8)
        self.make_toggle_row(opts.inner, "Eksik FPS modlarını kontrol et",
                             "Sodium, Lithium ve Fabric API eksikse otomatik indirir.", self.safe_mods_var)

    def make_toggle_row(self, parent, title, desc, var):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x")
        txt = tk.Frame(row, bg=CARD)
        txt.pack(side="left", fill="x", expand=True)
        tk.Label(txt, text=title, font=(FONT, 10, "bold"), fg=TEXT, bg=CARD).pack(anchor="w")
        tk.Label(txt, text=desc, font=(FONT, 8), fg=MUTED, bg=CARD).pack(anchor="w")
        Toggle(row, var, parent_bg=CARD).pack(side="right")

    def set_ram(self, gb: int):
        self.selected_ram = gb
        self.refresh_ram_buttons()
        self.refresh_info()
        self.save_config()

    def refresh_ram_buttons(self):
        for gb, btn in self.ram_buttons.items():
            if gb == self.selected_ram:
                btn.configure_button(bg=ACCENT, hover=ACCENT_HI, fg="#04130A")
            else:
                btn.configure_button(bg="#1A251F", hover="#223229", fg=MUTED)

    # ------------------------------------------------------------------ window
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        self.fs_btn.configure_button(
            text="\U0001F5D7  Pencere (ESC)" if self.is_fullscreen else "\u26F6  Tam Ekran (F11)")

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.fs_btn.configure_button(text="\u26F6  Tam Ekran (F11)")

    def open_mods_folder(self):
        mods_dir = os.path.join(APP_DIR, "mods")
        os.makedirs(mods_dir, exist_ok=True)
        try:
            os.startfile(mods_dir)
        except AttributeError:
            subprocess.Popen(["xdg-open", mods_dir])

    def set_progress(self, percent: float, text: str):
        def _update():
            self.status_var.set(text)
            self.progress.set(percent)
        self.root.after(0, _update)

    # --------------------------------------------------------------- animation
    def animate(self):
        w, h = self.hero.winfo_width(), self.hero.winfo_height()
        if w > 50 and h > 50 and self.page == "play":
            now = time.time()
            # Yüzen slime damlaları
            for p in self.blobs:
                p["y"] -= p["speed"]
                if p["y"] < -0.05:
                    p["y"] = 1.05
                    p["x"] = random.uniform(0.0, 1.0)
                cx = (p["x"] + math.sin(now * 0.7 + p["phase"]) * 0.01) * w
                cy = p["y"] * h
                r = p["r"]
                if p["id"] is None:
                    p["id"] = self.hero.create_oval(0, 0, 1, 1, fill="#0F2A1A", outline="#1A4D2E", tags="blob")
                self.hero.coords(p["id"], cx - r, cy - r, cx + r, cy + r)
            self.hero.tag_lower("blob")
            self.hero.tag_lower("bgimg")

            # Zıplayan slime küpü
            base = getattr(self, "logo_base", None)
            if base:
                t = now * 2.4
                hop = abs(math.sin(t))
                squash = 1.0 - 0.14 * (1 - hop) ** 6 + 0.10 * hop
                lift = hop * 26
                self.hero.delete("slime")
                draw_slime(self.hero, base[0], base[1] - lift + 40, 84, squash=squash, tag="slime")
        self.root.after(33, self.animate)

    # ------------------------------------------------------------ game launch
    def start_launch(self):
        if self.is_launching:
            return
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Uyarı", "Lütfen bir oyuncu adı girin.")
            self.show_page("settings")
            return

        self.save_config()
        self.is_launching = True
        self.play_btn.configure_button(text="\u23F3   HAZIRLANIYOR...", bg=ACCENT_DK, hover=ACCENT_DK,
                                       fg="#ECFDF5", enabled=False)
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
        self.play_btn.configure_button(text=PLAY_TEXT, bg=ACCENT, hover=ACCENT_HI, fg="#04130A", enabled=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = SlimeClientApp(root)
    root.mainloop()
