import os
import sys
import json
import shutil
import threading
import subprocess
import urllib.parse
import urllib.request
import math
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import minecraft_launcher_lib

from slime_ui import (
    BG, SIDEBAR, CARD, BORDER, ACCENT, ACCENT_HI, ACCENT_DK, TEXT, MUTED, DIM, FONT,
    rrect, RButton, Card, Toggle, ProgressBar, draw_slime,
)

MC_VERSION = "26.2"
DEFAULT_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), ".slimeclient")


def resource_path(filename: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def download_modrinth(slug: str, mods_dir: str) -> bool:
    loaders = urllib.parse.quote('["fabric"]')
    versions_q = urllib.parse.quote(f'["{MC_VERSION}"]')
    api_url = f"https://api.modrinth.com/v2/project/{slug}/version?loaders={loaders}&game_versions={versions_q}"

    req = urllib.request.Request(api_url, headers={"User-Agent": "SlimeClientSetup/26.2"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if not data:
        return False

    file_info = next((f for f in data[0]["files"] if f.get("primary")), data[0]["files"][0])
    target_path = os.path.join(mods_dir, file_info["filename"])

    if not os.path.exists(target_path):
        dl_req = urllib.request.Request(file_info["url"], headers={"User-Agent": "SlimeClientSetup/26.2"})
        with urllib.request.urlopen(dl_req, timeout=40) as f_resp, open(target_path, "wb") as out:
            shutil.copyfileobj(f_resp, out)
    return True


def create_desktop_shortcut(target_exe: str, shortcut_name: str = "Slime Client"):
    if os.name != "nt":
        return
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    lnk_path = os.path.join(desktop, f"{shortcut_name}.lnk")
    ps_cmd = (
        f'$ws = New-Object -ComObject WScript.Shell; '
        f'$s = $ws.CreateShortcut("{lnk_path}"); '
        f'$s.TargetPath = "{target_exe}"; '
        f'$s.WorkingDirectory = "{os.path.dirname(target_exe)}"; '
        f'$s.Save()'
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)


class SlimeSetupWizard:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Slime Client 26.2 Kurulum")
        self.root.geometry("720x480")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.install_dir = tk.StringVar(value=DEFAULT_DIR)
        self.opt_perf = tk.BooleanVar(value=True)
        self.opt_ping = tk.BooleanVar(value=True)
        self.opt_shortcut = tk.BooleanVar(value=True)
        self.opt_launch_after = tk.BooleanVar(value=True)
        self.step_index = 0

        # Sol banner
        self.side = tk.Canvas(root, width=210, bg=SIDEBAR, highlightthickness=0)
        self.side.pack(side="left", fill="y")
        self.side.bind("<Configure>", lambda e: self.draw_side())

        self.content = tk.Frame(root, bg=BG)
        self.content.pack(side="right", fill="both", expand=True, padx=30, pady=26)

        self.show_welcome_step()
        self.animate_logo()

    # ------------------------------------------------------------------ side
    def draw_side(self):
        c = self.side
        c.delete("static")
        h = c.winfo_height()
        c.create_text(26, 40, text="SLIME", anchor="w", fill=TEXT, font=(FONT, 20, "bold"), tags="static")
        c.create_text(26, 66, text="CLIENT", anchor="w", fill=ACCENT, font=(FONT, 20, "bold"), tags="static")
        c.create_text(26, h - 74, text="Sürüm 1.0", anchor="w", fill=MUTED, font=(FONT, 9), tags="static")
        c.create_text(26, h - 54, text="Minecraft 26.2", anchor="w", fill=MUTED, font=(FONT, 9), tags="static")
        c.create_text(26, h - 34, text="Fabric altyapısı", anchor="w", fill=MUTED, font=(FONT, 9), tags="static")
        self.logo_pos = (105, h / 2 + 20)
        # adım noktaları
        for i in range(4):
            on = i == self.step_index
            x = 26 + i * 22
            c.create_oval(x, h - 100, x + 10, h - 90, fill=ACCENT if on else "#1E2C24", outline="", tags="static")

    def animate_logo(self):
        pos = getattr(self, "logo_pos", None)
        if pos:
            t = time.time() * 2.4
            hop = abs(math.sin(t))
            squash = 1.0 - 0.14 * (1 - hop) ** 6 + 0.10 * hop
            self.side.delete("slime")
            draw_slime(self.side, pos[0], pos[1] - hop * 18, 70, squash=squash, tag="slime")
        self.root.after(33, self.animate_logo)

    def set_step(self, i: int):
        self.step_index = i
        self.draw_side()

    # --------------------------------------------------------------- helpers
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def heading(self, title, sub=None):
        tk.Label(self.content, text=title, font=(FONT, 18, "bold"), fg=TEXT, bg=BG).pack(anchor="w")
        if sub:
            tk.Label(self.content, text=sub, font=(FONT, 10), fg=MUTED, bg=BG,
                     justify="left").pack(anchor="w", pady=(4, 0))

    def nav_bar(self):
        nav = tk.Frame(self.content, bg=BG)
        nav.pack(side="bottom", fill="x")
        return nav

    def primary(self, parent, text, cmd, width=130):
        return RButton(parent, text, cmd, width=width, height=40, radius=12, parent_bg=BG,
                       font=(FONT, 10, "bold"))

    def secondary(self, parent, text, cmd, width=100):
        return RButton(parent, text, cmd, width=width, height=40, radius=12, bg="#1A251F",
                       hover="#223229", fg=MUTED, parent_bg=BG, font=(FONT, 10, "bold"))

    def toggle_row(self, parent, text, var):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", pady=5)
        tk.Label(row, text=text, font=(FONT, 10), fg=TEXT, bg=CARD, wraplength=330,
                 justify="left").pack(side="left")
        Toggle(row, var, parent_bg=CARD).pack(side="right")

    # ----------------------------------------------------------------- steps
    def show_welcome_step(self):
        self.set_step(0)
        self.clear_content()
        self.heading("Hoş geldin!", "Slime Client 26.2 kurulum sihirbazı birkaç adımda\nher şeyi senin için hazırlayacak.")

        card = Card(self.content)
        card.pack(fill="x", pady=(20, 0))
        tk.Label(card.inner, text="KURULACAKLAR", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w", pady=(0, 6))
        for line in (
            "Minecraft 26.2 ve Fabric Loader",
            "Slime Client HUD (FPS, CPS, koordinat)",
            "Sodium, Lithium ve Entity Culling FPS paketi",
            "Ping Wheel (işaretleme) ve Zoomify",
        ):
            r = tk.Frame(card.inner, bg=CARD)
            r.pack(fill="x", pady=2)
            tk.Label(r, text="\u2713", font=(FONT, 10, "bold"), fg=ACCENT, bg=CARD).pack(side="left", padx=(0, 10))
            tk.Label(r, text=line, font=(FONT, 10), fg=TEXT, bg=CARD).pack(side="left")

        nav = self.nav_bar()
        self.primary(nav, "İleri  \u203A", self.show_options_step).pack(side="right")

    def show_options_step(self):
        self.set_step(1)
        self.clear_content()
        self.heading("Kurulum ayarları")

        dir_card = Card(self.content)
        dir_card.pack(fill="x", pady=(16, 12))
        tk.Label(dir_card.inner, text="HEDEF KLASÖR", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w")
        row = tk.Frame(dir_card.inner, bg=CARD)
        row.pack(fill="x", pady=(8, 0))
        RButton(row, "Gözat", self.browse_dir, width=80, height=36, radius=10, bg="#1A251F",
                hover="#223229", fg=TEXT, parent_bg=CARD, font=(FONT, 9, "bold")).pack(side="right", padx=(8, 0))
        entry_card = Card(row, parent_bg=CARD, fill="#0D1511", outline=BORDER, radius=10, pad=3)
        entry_card.pack(side="left", fill="x", expand=True)
        e = tk.Entry(entry_card.inner, textvariable=self.install_dir, font=(FONT, 10), bg="#0D1511",
                     fg=TEXT, insertbackground=ACCENT, relief="flat", bd=5, highlightthickness=0)
        e.pack(fill="x")
        e.bind("<FocusIn>", lambda ev: entry_card.set_outline(ACCENT))
        e.bind("<FocusOut>", lambda ev: entry_card.set_outline(BORDER))

        opt_card = Card(self.content)
        opt_card.pack(fill="x")
        tk.Label(opt_card.inner, text="EK PAKETLER", font=(FONT, 8, "bold"), fg=ACCENT, bg=CARD).pack(anchor="w", pady=(0, 2))
        self.toggle_row(opt_card.inner, "FPS paketi (Sodium, Lithium, Entity Culling, ImmediatelyFast)", self.opt_perf)
        self.toggle_row(opt_card.inner, "İşaretleme (Ping Wheel) ve yakınlaştırma (Zoomify)", self.opt_ping)
        self.toggle_row(opt_card.inner, "Masaüstüne kısayol oluştur", self.opt_shortcut)

        nav = self.nav_bar()
        self.primary(nav, "Kur  \u203A", self.show_install_step).pack(side="right")
        self.secondary(nav, "\u2039  Geri", self.show_welcome_step).pack(side="right", padx=(0, 8))

    def browse_dir(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir.get())
        if selected:
            self.install_dir.set(selected)

    def show_install_step(self):
        self.set_step(2)
        self.clear_content()
        self.heading("Kuruluyor...", "Gerekli dosyalar indiriliyor, lütfen bekle.")

        self.status_label = tk.Label(self.content, text="Hazırlanıyor...", font=(FONT, 10, "bold"),
                                     fg=ACCENT, bg=BG)
        self.status_label.pack(anchor="w", pady=(18, 8))

        self.progress = ProgressBar(self.content, width=300, height=10, parent_bg=BG)
        self.progress.pack(fill="x")

        log_card = Card(self.content, fill="#0B120E", pad=10, radius=14)
        log_card.pack(fill="both", expand=True, pady=(16, 0))
        self.log_box = tk.Text(log_card.inner, height=8, font=("Consolas", 9), bg="#0B120E", fg=MUTED,
                               relief="flat", state="disabled", highlightthickness=0, bd=0)
        self.log_box.pack(fill="both", expand=True)

        threading.Thread(target=self.run_installation, daemon=True).start()

    def update_ui(self, status: str, pct: int, log_line: str = ""):
        def _update():
            self.status_label.config(text=status)
            self.progress.set(pct)
            if log_line:
                self.log_box.config(state="normal")
                self.log_box.insert("end", log_line + "\n")
                self.log_box.see("end")
                self.log_box.config(state="disabled")
        self.root.after(0, _update)

    def run_installation(self):
        try:
            target_dir = self.install_dir.get().strip()
            mods_dir = os.path.join(target_dir, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            self.update_ui("Çekirdek dosyalar kopyalanıyor...", 15, "[+] Kurulum klasörü oluşturuldu.")
            bundled_mod = resource_path("SlimeClient-26.2.jar")
            if os.path.exists(bundled_mod):
                shutil.copy2(bundled_mod, os.path.join(mods_dir, "SlimeClient-26.2.jar"))
                self.update_ui("Çekirdek dosyalar kopyalanıyor...", 20, "[+] SlimeClient-26.2.jar eklendi.")

            bundled_launcher = resource_path("SlimeLauncher.exe")
            installed_launcher = os.path.join(target_dir, "SlimeLauncher.exe")
            if os.path.exists(bundled_launcher):
                shutil.copy2(bundled_launcher, installed_launcher)
                self.update_ui("Çekirdek dosyalar kopyalanıyor...", 25, "[+] SlimeLauncher.exe kopyalandı.")

            self.update_ui("Minecraft 26.2 ve Fabric kuruluyor...", 35, "[*] Fabric Loader 26.2 indiriliyor...")
            cb = {"setStatus": lambda s: self.update_ui(s[:50], 50)}
            minecraft_launcher_lib.fabric.install_fabric(MC_VERSION, target_dir, callback=cb)
            self.update_ui("Fabric 26.2 kurulumu tamamlandı.", 65, "[+] Minecraft 26.2 + Fabric hazır.")

            mods_queue = ["fabric-api"]
            if self.opt_perf.get():
                mods_queue.extend(["sodium", "lithium", "entityculling", "immediatelyfast"])
            if self.opt_ping.get():
                mods_queue.extend(["ping-wheel", "zoomify"])

            step_inc = 25 // max(len(mods_queue), 1)
            current_pct = 65
            for slug in mods_queue:
                self.update_ui(f"26.2 Modu kontrol ediliyor: {slug}...", current_pct, f"[*] Modrinth (26.2): {slug}...")
                ok = download_modrinth(slug, mods_dir)
                current_pct += step_inc
                if ok:
                    self.update_ui(f"{slug} kuruldu.", current_pct, f"[+] {slug} kuruldu.")
                else:
                    self.update_ui(f"{slug} atlandı.", current_pct, f"[-] {slug} için 26.2 sürümü henüz yok, atlandı.")

            if self.opt_shortcut.get() and os.path.exists(installed_launcher):
                self.update_ui("Masaüstü kısayolu oluşturuluyor...", 95, "[+] Masaüstü kısayolu eklendi.")
                create_desktop_shortcut(installed_launcher, "Slime Client")

            self.update_ui("Kurulum başarıyla tamamlandı!", 100, "[✓] Slime Client 26.2 hazır.")
            self.root.after(800, lambda: self.show_finish_step(installed_launcher))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Kurulum Hatası", f"Kurulum sırasında hata oluştu:\n{e}"))

    def show_finish_step(self, launcher_exe: str):
        self.set_step(3)
        self.clear_content()
        self.heading("Kurulum tamamlandı!", "Slime Client 26.2 bilgisayarına başarıyla kuruldu.\nMasaüstündeki kısayoldan ya da aşağıdan oyunu açabilirsin.")

        card = Card(self.content)
        card.pack(fill="x", pady=(20, 0))
        self.toggle_row(card.inner, "Başlatıcıyı şimdi aç", self.opt_launch_after)

        def finish():
            if self.opt_launch_after.get() and os.path.exists(launcher_exe):
                subprocess.Popen([launcher_exe])
            self.root.destroy()

        nav = self.nav_bar()
        self.primary(nav, "Bitir", finish).pack(side="right")


if __name__ == "__main__":
    app = tk.Tk()
    SlimeSetupWizard(app)
    app.mainloop()
