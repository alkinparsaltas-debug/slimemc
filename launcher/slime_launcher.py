import os
import sys
import json
import uuid
import shutil
import threading
import subprocess
import urllib.parse
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib

MC_VERSION = "26.2"
SLIME_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), ".slimeclient")
CONFIG_PATH = os.path.join(SLIME_DIR, "slime_config.json")
DEFAULT_MODS = ["fabric-api", "sodium", "lithium", "entityculling", "immediatelyfast", "ping-wheel", "zoomify"]


def get_bundled_jar() -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, "SlimeClient-26.2.jar")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"username": "SlimeOyuncu", "ram_gb": 4, "auto_mods": True}


def save_config(cfg: dict):
    os.makedirs(SLIME_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def download_modrinth_mod(slug: str, mods_dir: str):
    loaders = urllib.parse.quote('["fabric"]')
    game_versions = urllib.parse.quote(f'["{MC_VERSION}"]')
    url = f"https://api.modrinth.com/v2/project/{slug}/version?loaders={loaders}&game_versions={game_versions}"

    req = urllib.request.Request(url, headers={"User-Agent": "SlimeClientLauncher/26.2"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        versions = json.loads(resp.read().decode("utf-8"))

    if not versions:
        return

    primary_file = next((f for f in versions[0]["files"] if f.get("primary")), versions[0]["files"][0])
    dest_path = os.path.join(mods_dir, primary_file["filename"])

    if not os.path.exists(dest_path):
        file_req = urllib.request.Request(primary_file["url"], headers={"User-Agent": "SlimeClientLauncher/26.2"})
        with urllib.request.urlopen(file_req, timeout=30) as f_resp, open(dest_path, "wb") as out:
            shutil.copyfileobj(f_resp, out)


class SlimeLauncherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Slime Client 26.2")
        self.root.geometry("450x360")
        self.root.resizable(False, False)
        self.root.configure(bg="#111317")

        cfg = load_config()

        # Üst Başlık
        header = tk.Frame(root, bg="#171A20", height=78)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="SLIME CLIENT", font=("Segoe UI", 20, "bold"), fg="#55FF55", bg="#171A20").pack(pady=(12, 0))
        tk.Label(header, text="Minecraft 26.2  •  Fabric Performans & PvP İstemcisi", font=("Segoe UI", 9), fg="#9AA0A6", bg="#171A20").pack()

        # Ana Gövde
        body = tk.Frame(root, bg="#111317")
        body.pack(padx=36, pady=18, fill="both", expand=True)

        tk.Label(body, text="OYUNCU ADI (ÇEVRİMDIŞI / CRACKLİ)", font=("Segoe UI", 8, "bold"), fg="#8E96A0", bg="#111317").pack(anchor="w")
        self.username_var = tk.StringVar(value=cfg.get("username", "SlimeOyuncu"))
        entry = tk.Entry(
            body, textvariable=self.username_var, font=("Segoe UI", 11, "bold"),
            bg="#1C2026", fg="#FFFFFF", insertbackground="#55FF55", relief="flat"
        )
        entry.pack(fill="x", pady=(4, 14), ipady=7)

        ram_row = tk.Frame(body, bg="#111317")
        ram_row.pack(fill="x", pady=(0, 10))
        tk.Label(ram_row, text="Ayrılan RAM Miktarı:", font=("Segoe UI", 9, "bold"), fg="#E8EAED", bg="#111317").pack(side="left")
        self.ram_var = tk.IntVar(value=cfg.get("ram_gb", 4))
        ttk.Combobox(ram_row, textvariable=self.ram_var, values=[2, 3, 4, 6, 8, 12], width=6, state="readonly").pack(side="right")

        self.auto_mods_var = tk.BooleanVar(value=cfg.get("auto_mods", True))
        tk.Checkbutton(
            body, text="26.2 FPS & İşaretleme (Ping) modlarını otomatik güncelle",
            variable=self.auto_mods_var, font=("Segoe UI", 8), fg="#B0B7C0",
            bg="#111317", selectcolor="#1C2026", activebackground="#111317", activeforeground="#FFFFFF"
        ).pack(anchor="w", pady=(0, 16))

        self.launch_btn = tk.Button(
            body, text="OYNA  (26.2)", font=("Segoe UI", 12, "bold"),
            bg="#55FF55", fg="#0B0E11", activebackground="#3CE63C",
            relief="flat", cursor="hand2", command=self.start_thread
        )
        self.launch_btn.pack(fill="x", ipady=9)

        self.status_var = tk.StringVar(value="Hazır • Klasör: .slimeclient")
        tk.Label(root, textvariable=self.status_var, font=("Segoe UI", 8), fg="#8E96A0", bg="#111317").pack(side="bottom", pady=10)

    def set_status(self, text: str):
        self.root.after(0, lambda: self.status_var.set(text))

    def start_thread(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Uyarı", "Lütfen geçerli bir oyuncu adı girin.")
            return
        save_config({"username": username, "ram_gb": self.ram_var.get(), "auto_mods": self.auto_mods_var.get()})
        self.launch_btn.config(state="disabled", text="BAŞLATILIYOR...")
        threading.Thread(target=self.install_and_launch, args=(username, self.ram_var.get()), daemon=True).start()

    def install_and_launch(self, username: str, ram_gb: int):
        try:
            mods_dir = os.path.join(SLIME_DIR, "mods")
            os.makedirs(mods_dir, exist_ok=True)

            # 1. Gömülü SlimeClient-26.2.jar kopyalama
            bundled_jar = get_bundled_jar()
            if os.path.exists(bundled_jar):
                shutil.copy2(bundled_jar, os.path.join(mods_dir, "SlimeClient-26.2.jar"))

            # 2. Minecraft 26.2 & Fabric kurulumu
            self.set_status("Minecraft 26.2 ve Fabric kontrol ediliyor...")
            callback = {"setStatus": lambda s: self.set_status(s[:56])}
            minecraft_launcher_lib.fabric.install_fabric(MC_VERSION, SLIME_DIR, callback=callback)

            # 3. Modrinth üzerinden 26.2 modları
            if self.auto_mods_var.get():
                for mod in DEFAULT_MODS:
                    self.set_status(f"26.2 Modu kontrol ediliyor: {mod}...")
                    try:
                        download_modrinth_mod(mod, mods_dir)
                    except Exception:
                        pass

            # 4. Oyunu başlatma
            self.set_status("Slime Client 26.2 başlatılıyor...")
            installed = minecraft_launcher_lib.utils.get_installed_versions(SLIME_DIR)
            fabric_version = next(v["id"] for v in installed if "fabric-loader" in v["id"] and MC_VERSION in v["id"])
            offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}"))

            options = {
                "username": username,
                "uuid": offline_uuid,
                "token": "0",
                "jvmArguments": [
                    f"-Xmx{ram_gb}G",
                    f"-Xms{min(2, ram_gb)}G",
                    "-XX:+UseG1GC",
                    "-XX:+ParallelRefProcEnabled",
                    "-XX:MaxGCPauseMillis=200",
                    "-XX:+UnlockExperimentalVMOptions"
                ]
            }

            cmd = minecraft_launcher_lib.command.get_minecraft_command(fabric_version, SLIME_DIR, options)
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            self.root.after(1500, self.root.destroy)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Başlatma Hatası", str(e)))
            self.root.after(0, lambda: self.launch_btn.config(state="normal", text="OYNA  (26.2)"))
            self.set_status("Hata oluştu.")


if __name__ == "__main__":
    app_root = tk.Tk()
    SlimeLauncherApp(app_root)
    app_root.mainloop()
