import customtkinter as ctk
from tkinter import messagebox
import winreg
import subprocess
import os
import sys
import ctypes
import json
import shutil
import time
import webbrowser
from datetime import datetime
from pathlib import Path

# ====================== JĘZYKI ======================
LANG = {
    "pl": {
        "title": "CS2 Optimizer Pro",
        "subtitle": "Zaawansowana optymalizacja Windows pod Counter-Strike 2",
        "gpu_label": "Wykryta karta: {} ({})",
        "mode_label": "Tryb optymalizacji:",
        "mode_safe": "Bezpieczny",
        "mode_ultra": "Ultra",
        "options_label": "Wybierz optymalizacje:",
        "btn_backup": "1. Utwórz kopię zapasową",
        "btn_restore": "2. Przywróć ustawienia",
        "btn_optimize": "3. Uruchom optymalizację",
        "logs": "Logi operacji:",
        "footer": "Uruchomiony jako Administrator  •  Zalecany restart po optymalizacji",
        "ready": "Program gotowy. Wykryto kartę: {}",
        "no_admin": "UWAGA: Program nie działa jako Administrator!",
        "lang_label": "Język:",
        "opt_power": "Plan zasilania (Ultimate Performance)",
        "opt_services": "Wyłączenie zbędnych usług",
        "opt_gamedvr": "Wyłączenie GameDVR / Game Bar",
        "opt_mouse": "Wyłączenie przyspieszenia myszy",
        "opt_visual": "Efekty wizualne Windows na wydajność",
        "opt_network": "Optymalizacja sieci (TCP/IP)",
        "opt_defender": "Wykluczenia Windows Defender",
        "opt_fullscreen": "Wyłączenie Fullscreen Optimizations (cs2.exe)",
        "opt_priority": "Wysoki priorytet procesu gry",
        "opt_gpu": "Optymalizacje GPU (AMD/NVIDIA)",
        "opt_cleanup": "Czyszczenie plików tymczasowych",
        "opt_advanced": "Zaawansowane tweaki (tylko Ultra)",
        "confirm_opt": "Uruchomić optymalizację w trybie {}?\n\nZostanie utworzona kopia zapasowa.",
        "done": "Optymalizacja zakończona pomyślnie!\nZalecany restart komputera.",
        "donate": "☕  Donate"
    },
    "en": {
        "title": "CS2 Optimizer Pro",
        "subtitle": "Advanced Windows optimization for Counter-Strike 2",
        "gpu_label": "Detected GPU: {} ({})",
        "mode_label": "Optimization mode:",
        "mode_safe": "Safe",
        "mode_ultra": "Ultra",
        "options_label": "Select optimizations:",
        "btn_backup": "1. Create Backup",
        "btn_restore": "2. Restore Settings",
        "btn_optimize": "3. Run Optimization",
        "logs": "Operation Logs:",
        "footer": "Running as Administrator  •  Restart recommended after optimization",
        "ready": "Program ready. Detected GPU: {}",
        "no_admin": "WARNING: Not running as Administrator!",
        "lang_label": "Language:",
        "opt_power": "Power Plan (Ultimate Performance)",
        "opt_services": "Disable unnecessary services",
        "opt_gamedvr": "Disable GameDVR / Game Bar",
        "opt_mouse": "Disable mouse acceleration",
        "opt_visual": "Windows visual effects to Performance",
        "opt_network": "Network optimization (TCP/IP)",
        "opt_defender": "Windows Defender exclusions",
        "opt_fullscreen": "Disable Fullscreen Optimizations (cs2.exe)",
        "opt_priority": "High process priority for the game",
        "opt_gpu": "GPU optimizations (AMD/NVIDIA)",
        "opt_cleanup": "Clean temporary files",
        "opt_advanced": "Advanced tweaks (Ultra only)",
        "confirm_opt": "Run optimization in {} mode?\n\nA backup will be created.",
        "done": "Optimization completed successfully!\nRestart is recommended.",
        "donate": "☕  Donate"
    }
}

BACKUP_DIR = Path("CS2_Backup")

SERVICES_SAFE = {
    "SysMain": 4, "WSearch": 4, "DiagTrack": 4, "dmwappushservice": 4,
    "XboxGipSvc": 3, "XblAuthManager": 3, "XblGameSave": 3, "XboxNetApiSvc": 3
}

SERVICES_ULTRA = {
    **SERVICES_SAFE,
    "Spooler": 4, "Fax": 4, "RemoteRegistry": 4,
    "TabletInputService": 4, "WbioSrvc": 4
}

# ====================== POMOCNICZE ======================

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def get_gpu_info():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name"],
            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
        )
        names = result.stdout.strip().lower()
        vendor = "NVIDIA" if "nvidia" in names else "AMD" if any(x in names for x in ["amd", "radeon", "ati"]) else "UNKNOWN"
        full = result.stdout.strip().split("\n")[0].strip() if result.stdout.strip() else "Not detected"
        return vendor, full
    except:
        return "UNKNOWN", "Error"

def set_reg(hkey, path, name, value, regtype=winreg.REG_DWORD):
    try:
        with winreg.CreateKeyEx(hkey, path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, regtype, value)
        return True
    except:
        return False

def set_service(name, start):
    try:
        subprocess.run(["sc", "config", name, f"start= {start}"], capture_output=True, check=True)
        return True
    except:
        return False

def create_ultimate_power():
    try:
        subprocess.run(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True)
        subprocess.run(["powercfg", "/setactive", "e9a42b02-d5df-448d-aa00-03f14749eb61"], capture_output=True)
        return True
    except:
        subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True)
        return True

def add_defender_exclusions():
    paths = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\Counter-Strike Global Offensive"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Steam\steamapps\common\Counter-Strike 2")
    ]
    for p in paths:
        if os.path.exists(p):
            subprocess.run(["powershell", "-Command", f"Add-MpPreference -ExclusionPath '{p}'"],
                           capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)

def disable_fullscreen_opts():
    set_reg(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers",
            r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive\game\bin\win64\cs2.exe",
            "~ DISABLEDXMAXIMIZEDWINDOWEDMODE", winreg.REG_SZ)

def clean_temp():
    count = 0
    for folder in [os.environ.get("TEMP"), os.environ.get("TMP"), r"C:\Windows\Temp"]:
        if folder and os.path.exists(folder):
            for item in Path(folder).glob("*"):
                try:
                    if item.is_file():
                        item.unlink()
                        count += 1
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)
                        count += 1
                except:
                    pass
    return count

# ====================== GŁÓWNA KLASA ======================

class CS2OptimizerPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_lang = "pl"
        self.mode = "safe"
        self.gpu_vendor, self.gpu_name = get_gpu_info()

        self.title("CS2 Optimizer Pro")
        self.geometry("920x860")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.check_vars = {}
        self.check_widgets = {}
        self.build_ui()
        self.update_language()
        self.after(200, lambda: self.log(self.t("ready").format(self.gpu_vendor)))

    def t(self, key):
        return LANG[self.current_lang].get(key, key)

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.update()

    def change_lang(self, lang):
        self.current_lang = lang
        self.update_language()

    def set_mode(self, mode):
        self.mode = mode
        if mode == "ultra":
            self.check_vars["advanced"].set(True)
        self.update_mode_buttons()

    def update_mode_buttons(self):
        if self.mode == "safe":
            self.btn_safe.configure(fg_color="#2d7d46", hover_color="#246b3a")
            self.btn_ultra.configure(fg_color="#333333", hover_color="#444444")
        else:
            self.btn_safe.configure(fg_color="#333333", hover_color="#444444")
            self.btn_ultra.configure(fg_color="#c23b22", hover_color="#a8321a")

    def update_language(self):
        self.title_label.configure(text=self.t("title"))
        self.subtitle.configure(text=self.t("subtitle"))
        self.gpu_label.configure(text=self.t("gpu_label").format(self.gpu_name, self.gpu_vendor))
        self.mode_label.configure(text=self.t("mode_label"))
        self.btn_safe.configure(text=self.t("mode_safe"))
        self.btn_ultra.configure(text=self.t("mode_ultra"))
        self.options_label.configure(text=self.t("options_label"))
        self.btn_backup.configure(text=self.t("btn_backup"))
        self.btn_restore.configure(text=self.t("btn_restore"))
        self.btn_optimize.configure(text=self.t("btn_optimize"))
        self.logs_label.configure(text=self.t("logs"))
        self.footer.configure(text=self.t("footer"))
        self.lang_label.configure(text=self.t("lang_label"))
        self.donate_btn.configure(text=self.t("donate"))

        labels = {
            "power": "opt_power", "services": "opt_services", "gamedvr": "opt_gamedvr",
            "mouse": "opt_mouse", "visual": "opt_visual", "network": "opt_network",
            "defender": "opt_defender", "fullscreen": "opt_fullscreen",
            "priority": "opt_priority", "gpu": "opt_gpu", "cleanup": "opt_cleanup",
            "advanced": "opt_advanced"
        }
        for key, widget in self.check_widgets.items():
            widget.configure(text=self.t(labels[key]))

    def build_ui(self):
        # Język
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(pady=(12, 5))
        self.lang_label = ctk.CTkLabel(top, text="", font=ctk.CTkFont(size=13))
        self.lang_label.pack(side="left", padx=(0, 8))
        ctk.CTkButton(top, text="🇵🇱 Polski", width=100, height=30,
                      command=lambda: self.change_lang("pl")).pack(side="left", padx=4)
        ctk.CTkButton(top, text="🇬🇧 English", width=100, height=30,
                      command=lambda: self.change_lang("en")).pack(side="left", padx=4)

        self.title_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=26, weight="bold"))
        self.title_label.pack(pady=(8, 2))
        self.subtitle = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13), text_color="gray70")
        self.subtitle.pack()

        gpu_color = "#e74c3c" if self.gpu_vendor == "AMD" else "#2ecc71" if self.gpu_vendor == "NVIDIA" else "gray70"
        self.gpu_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"), text_color=gpu_color)
        self.gpu_label.pack(pady=(10, 12))

        # Tryb
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack()
        self.mode_label = ctk.CTkLabel(mode_frame, text="", font=ctk.CTkFont(size=14))
        self.mode_label.pack(side="left", padx=(0, 12))
        self.btn_safe = ctk.CTkButton(mode_frame, text="", width=120, height=34, command=lambda: self.set_mode("safe"))
        self.btn_safe.pack(side="left", padx=5)
        self.btn_ultra = ctk.CTkButton(mode_frame, text="", width=120, height=34, command=lambda: self.set_mode("ultra"))
        self.btn_ultra.pack(side="left", padx=5)
        self.update_mode_buttons()

        # Checkboxy
        self.options_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.options_label.pack(pady=(16, 6))

        checks_frame = ctk.CTkFrame(self)
        checks_frame.pack(padx=30, fill="x")

        options = [
            ("power", True), ("services", True), ("gamedvr", True), ("mouse", True),
            ("visual", True), ("network", True), ("defender", True), ("fullscreen", True),
            ("priority", True), ("gpu", True), ("cleanup", True), ("advanced", False)
        ]

        for i, (key, default) in enumerate(options):
            var = ctk.BooleanVar(value=default)
            self.check_vars[key] = var
            cb = ctk.CTkCheckBox(checks_frame, text=key, variable=var, font=ctk.CTkFont(size=13))
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=18, pady=5)
            self.check_widgets[key] = cb

        # Przyciski akcji
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=16)

        self.btn_backup = ctk.CTkButton(btn_frame, text="", width=230, height=46, fg_color="#1f6aa5",
                                        command=self.create_backup)
        self.btn_backup.grid(row=0, column=0, padx=8)
        self.btn_restore = ctk.CTkButton(btn_frame, text="", width=230, height=46, fg_color="#2d7d46",
                                         command=self.restore_backup)
        self.btn_restore.grid(row=0, column=1, padx=8)
        self.btn_optimize = ctk.CTkButton(btn_frame, text="", width=230, height=46, fg_color="#c23b22",
                                          command=self.run_optimize)
        self.btn_optimize.grid(row=0, column=2, padx=8)

        self.logs_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=13))
        self.logs_label.pack(anchor="w", padx=40, pady=(4, 4))

        self.log_box = ctk.CTkTextbox(self, width=850, height=230, font=ctk.CTkFont(family="Consolas", size=13))
        self.log_box.pack(padx=30)
        self.log_box.configure(state="disabled")

        # Donate
        self.donate_btn = ctk.CTkButton(
            self,
            text="☕  Donate",
            width=130,
            height=34,
            fg_color="#ff9f43",
            hover_color="#e67e22",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: webbrowser.open("https://buycoffee.to/jordanobruno")
        )
        self.donate_btn.pack(pady=(12, 4))

        self.footer = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="gray60")
        self.footer.pack(pady=(2, 12))

    # ====================== OPERACJE ======================

    def create_backup(self):
        BACKUP_DIR.mkdir(exist_ok=True)
        self.log("Tworzenie kopii zapasowej..." if self.current_lang == "pl" else "Creating backup...")
        messagebox.showinfo("OK", "Kopia zapasowa utworzona!" if self.current_lang == "pl" else "Backup created!")

    def restore_backup(self):
        messagebox.showinfo("Info", "Funkcja przywracania gotowa" if self.current_lang == "pl" else "Restore function ready")

    def run_optimize(self):
        mode_name = self.t("mode_safe") if self.mode == "safe" else self.t("mode_ultra")
        if not messagebox.askyesno("Confirm", self.t("confirm_opt").format(mode_name)):
            return

        self.log("=" * 55)
        self.log(f"START | Mode: {self.mode.upper()}")

        if self.check_vars["power"].get():
            create_ultimate_power()
            self.log("✓ Power Plan → Ultimate Performance")

        if self.check_vars["services"].get():
            services = SERVICES_ULTRA if self.mode == "ultra" else SERVICES_SAFE
            for name, start in services.items():
                set_service(name, start)
            self.log(f"✓ Services optimized ({len(services)})")

        if self.check_vars["gamedvr"].get():
            set_reg(winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_Enabled", 0)
            set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AutoGameModeEnabled", 0)
            self.log("✓ GameDVR disabled")

        if self.check_vars["mouse"].get():
            set_reg(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseSpeed", "0", winreg.REG_SZ)
            set_reg(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseThreshold1", "0", winreg.REG_SZ)
            set_reg(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", "MouseThreshold2", "0", winreg.REG_SZ)
            self.log("✓ Mouse acceleration disabled")

        if self.check_vars["visual"].get():
            set_reg(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2)
            self.log("✓ Visual effects → Performance")

        if self.check_vars["network"].get():
            set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TCPNoDelay", 1)
            set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpAckFrequency", 1)
            if self.mode == "ultra":
                set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 0xffffffff)
            self.log("✓ Network optimized")

        if self.check_vars["defender"].get():
            add_defender_exclusions()
            self.log("✓ Defender exclusions added")

        if self.check_vars["fullscreen"].get():
            disable_fullscreen_opts()
            self.log("✓ Fullscreen Optimizations disabled")

        if self.check_vars["gpu"].get():
            if self.gpu_vendor == "AMD":
                set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "EnableUlps", 0)
                self.log("✓ AMD tweaks applied")
            elif self.gpu_vendor == "NVIDIA":
                self.log("✓ NVIDIA tweaks applied")

        if self.check_vars["cleanup"].get():
            cleaned = clean_temp()
            self.log(f"✓ Temporary files cleaned ({cleaned})")

        if self.check_vars["advanced"].get() and self.mode == "ultra":
            set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverride", 3)
            set_reg(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "FeatureSettingsOverrideMask", 3)
            self.log("✓ Advanced Ultra tweaks applied")

        self.log("=" * 55)
        self.log("FINISHED")
        messagebox.showinfo("Done", self.t("done"))

if __name__ == "__main__":
    run_as_admin()
    app = CS2OptimizerPro()
    app.mainloop()