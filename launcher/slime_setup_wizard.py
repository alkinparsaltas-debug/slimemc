import os
import sys
import json
import shutil
import threading
import subprocess
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import minecraft_launcher_lib

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
        self.root.title("Slime Client 26.2 Kurulum Sihirbazı")
        self.root.geometry("560x390")
        self.root.resizable(False, False)
        self.root.configure(bg="#13161A")

        self.install_dir = tk.StringVar(value=DEFAULT_DIR)
        self.opt_perf = tk.BooleanVar(value=True)
        self.opt_ping = tk.BooleanVar(value=True)
        self.opt_shortcut = tk.BooleanVar(value=True)
        self.opt_launch_after = tk.BooleanVar(value=True)

        # Sol Yan Banner
        sidebar = tk.Frame(root, bg="#1A1F26", width=165)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="SLIME\nCLIENT", font=("Segoe UI", 19, "bold"), fg="#55FF55", bg="#1A1F26", justify="left").pack(anchor="w", padx=18, pady=(26, 8))
        tk.Label(sidebar, text="Sürüm 1.0\nMinecraft 26.2\nFabric Altyapısı\nCrackli Destekli", font=("Segoe UI", 9), fg="#8E96A0", bg="#1A1F26", justify="left").pack(anchor="w", padx=18)

        # Sağ İçerik Alanı
        self.content = tk.Frame(root, bg="#13161A")
        self.content.pack(side="right", fill="both", expand=True, padx=22, pady=20)

        self.show_welcome_step()

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_welcome_step(self):
        self.clear_content()
        tk.Label(self.content, text="Slime Client 26.2 Kurulumuna Hoş Geldiniz", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#13161A").pack(anchor="w", pady=(6, 12))
        desc = (
            "Bu sihirbaz bilgisayarınıza yüksek FPS odaklı Slime Client\n"
            "26.2 paketini ve çevrimdışı destekli başlatıcıyı kuracaktır.\n\n"
            "Kurulacak Bileşenler:\n"
            "• Minecraft 26.2 & Fabric Loader\n"
            "• Slime Client Özel HUD (FPS, CPS, Koordinat)\n"
            "• Sodium, Lithium & Entity Culling FPS Paketi\n"
            "• Ping Wheel (Oyun İçi İşaretleme) & Zoomify"
        )
        tk.Label(self.content, text=desc, font=("Segoe UI", 9), fg="#C5CBD3", bg="#13161A", justify="left").pack(anchor="w")

        nav = tk.Frame(self.content, bg="#13161A")
        nav.pack(side="bottom", fill="x")
        tk.Button(nav, text="İleri >", font=("Segoe UI", 9, "bold"), bg="#55FF55", fg="#0D1117", width=12, relief="flat", cursor="hand2", command=self.show_options_step).pack(side="right")

    def show_options_step(self):
        self.clear_content()
        tk.Label(self.content, text="Kurulum Ayarları", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#13161A").pack(anchor="w", pady=(6, 10))

        tk.Label(self.content, text="Hedef Klasör:", font=("Segoe UI", 9, "bold"), fg="#E8EAED", bg="#13161A").pack(anchor="w")
        dir_row = tk.Frame(self.content, bg="#13161A")
        dir_row.pack(fill="x", pady=(4, 14))
        tk.Entry(dir_row, textvariable=self.install_dir, font=("Segoe UI", 9), bg="#1E2228", fg="#FFFFFF", relief="flat").pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(dir_row, text="Gözat...", font=("Segoe UI", 8), bg="#2B313A", fg="#FFFFFF", relief="flat", command=self.browse_dir).pack(side="right", padx=(6, 0), ipady=3)

        tk.Label(self.content, text="Ek Paketler ve Kısayollar:", font=("Segoe UI", 9, "bold"), fg="#E8EAED", bg="#13161A").pack(anchor="w", pady=(0, 4))
        for text, var in [
            ("26.2 FPS Paketi (Sodium, Lithium, Entity Culling, ImmediatelyFast)", self.opt_perf),
            ("Oyun İçi İşaretleme (Ping Wheel) ve Yakınlaştırma (Zoomify)", self.opt_ping),
            ("Masaüstüne Slime Client kısayolu oluştur", self.opt_shortcut),
        ]:
            tk.Checkbutton(self.content, text=text, variable=var, font=("Segoe UI", 9), fg="#C5CBD3", bg="#13161A", selectcolor="#1E2228", activebackground="#13161A", activeforeground="#FFFFFF").pack(anchor="w", pady=2)

        nav = tk.Frame(self.content, bg="#13161A")
        nav.pack(side="bottom", fill="x")
        tk.Button(nav, text="Kur >", font=("Segoe UI", 9, "bold"), bg="#55FF55", fg="#0D1117", width=12, relief="flat", cursor="hand2", command=self.show_install_step).pack(side="right")
        tk.Button(nav, text="< Geri", font=("Segoe UI", 9), bg="#2B313A", fg="#FFFFFF", width=10, relief="flat", command=self.show_welcome_step).pack(side="right", padx=(0, 8))

    def browse_dir(self):
        selected = filedialog.askdirectory(initialdir=self.install_dir.get())
        if selected:
            self.install_dir.set(selected)

    def show_install_step(self):
        self.clear_content()
        tk.Label(self.content, text="Slime Client 26.2 Kuruluyor...", font=("Segoe UI", 13, "bold"), fg="#FFFFFF", bg="#13161A").pack(anchor="w", pady=(6, 8))
        tk.Label(self.content, text="Gerekli dosyalar indiriliyor ve yapılandırılıyor. Lütfen bekleyin.", font=("Segoe UI", 9), fg="#9AA0A6", bg="#13161A").pack(anchor="w", pady=(0, 16))

        self.status_label = tk.Label(self.content, text="Hazırlanıyor...", font=("Segoe UI", 9, "bold"), fg="#55FF55", bg="#13161A")
        self.status_label.pack(anchor="w", pady=(0, 6))

        self.progress = ttk.Progressbar(self.content, mode="determinate", maximum=100)
        self.progress.pack(fill="x", ipady=4)

        self.log_box = tk.Text(self.content, height=8, font=("Consolas", 8), bg="#0E1013", fg="#9AA0A6", relief="flat", state="disabled")
        self.log_box.pack(fill="both", expand=True, pady=(12, 0))

        threading.Thread(target=self.run_installation, daemon=True).start()

    def update_ui(self, status: str, pct: int, log_line: str = ""):
        def _update():
            self.status_label.config(text=status)
            self.progress["value"] = pct
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
        self.clear_content()
        tk.Label(self.content, text="Kurulum Tamamlandı", font=("Segoe UI", 14, "bold"), fg="#55FF55", bg="#13161A").pack(anchor="w", pady=(6, 12))
        tk.Label(
            self.content,
            text="Slime Client 26.2 bilgisayarınıza başarıyla kuruldu.\nMasaüstündeki kısayoldan veya aşağıdaki seçenekle oyunu başlatabilirsiniz.",
            font=("Segoe UI", 9), fg="#C5CBD3", bg="#13161A", justify="left"
        ).pack(anchor="w", pady=(0, 16))

        tk.Checkbutton(
            self.content, text="Slime Client Başlatıcısını şimdi aç",
            variable=self.opt_launch_after, font=("Segoe UI", 9, "bold"),
            fg="#FFFFFF", bg="#13161A", selectcolor="#1E2228",
            activebackground="#13161A", activeforeground="#FFFFFF"
        ).pack(anchor="w")

        def finish():
            if self.opt_launch_after.get() and os.path.exists(launcher_exe):
                subprocess.Popen([launcher_exe])
            self.root.destroy()

        nav = tk.Frame(self.content, bg="#13161A")
        nav.pack(side="bottom", fill="x")
        tk.Button(nav, text="Bitir", font=("Segoe UI", 9, "bold"), bg="#55FF55", fg="#0D1117", width=12, relief="flat", cursor="hand2", command=finish).pack(side="right")


if __name__ == "__main__":
    app = tk.Tk()
    SlimeSetupWizard(app)
    app.mainloop()
