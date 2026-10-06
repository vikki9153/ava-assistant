from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import subprocess
import threading
import webbrowser
from typing import Callable
from urllib.parse import quote

try:
    import tkinter as tk
except ModuleNotFoundError:  # pragma: no cover
    tk = None

try:
    import pyttsx3
except ModuleNotFoundError:  # pragma: no cover
    pyttsx3 = None

try:
    import speech_recognition as sr
except ModuleNotFoundError:  # pragma: no cover
    sr = None


USER_PROFILE = os.path.expanduser("~")

COMMON_APP_PATHS = {
    "whatsapp": [
        os.path.join(USER_PROFILE, "AppData", "Local", "Programs", "WhatsApp", "WhatsApp.exe"),
        os.path.join(USER_PROFILE, "AppData", "Local", "WhatsApp", "WhatsApp.exe"),
        "WhatsApp.exe",
    ],
    "teams": [
        os.path.join(USER_PROFILE, "AppData", "Local", "Microsoft", "Teams", "current", "Teams.exe"),
        os.path.join(USER_PROFILE, "AppData", "Local", "Microsoft", "Teams", "Update.exe"),
        "Teams.exe",
    ],
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome.exe",
    ],
    "vscode": [
        os.path.join(USER_PROFILE, "AppData", "Local", "Programs", "Microsoft VS Code", "Code.exe"),
        "code.exe",
        "code.cmd",
    ],
    "notepad": ["notepad.exe"],
    "calculator": ["calc.exe"],
    "cmd": ["cmd.exe"],
    "explorer": ["explorer.exe"],
}

CUSTOM_HINDI_SCRIPTS: dict[str, Callable[[], str]] = {
    "study mode": lambda: "Study mode active hai. Chrome aur VS Code khul gaye hain.",
    "focus mode": lambda: "Focus mode active hai. Aapka kaam aaj ke liye tayyar hai.",
    "work mode": lambda: "Work mode shuru ho gaya. Teams aur browser ready hain.",
}

DEFAULT_CUSTOM_COMMANDS = {
    "my project": "vscode",
    "my workspace": "vscode",
    "study time": "study mode",
    "office mode": "work mode",
    "my browser": "chrome",
    "my chats": "whatsapp",
}

WAKE_PHRASES = [
    "hey assistant",
    "hello assistant",
    "namaste assistant",
    "assistant",
    "hey alexa",
    "alexa",
]


def normalize_command(command: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", command.strip().lower())
    return " ".join(text.split())


def load_custom_commands(path: str | None = None) -> dict[str, str]:
    config_path = path or os.path.join(os.path.dirname(__file__), "custom_commands.json")
    commands = DEFAULT_CUSTOM_COMMANDS.copy()
    if not os.path.exists(config_path):
        return commands

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            for key, value in data.items():
                commands[str(key).strip().lower()] = str(value).strip().lower()
    except (json.JSONDecodeError, OSError):
        pass

    return commands


def install_startup_shortcut(startup_dir: str | None = None, script_path: str | None = None) -> str:
    startup_path = startup_dir or os.path.join(os.environ.get("APPDATA", USER_PROFILE), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    os.makedirs(startup_path, exist_ok=True)

    script_target = script_path or os.path.abspath(__file__)
    script_dir = os.path.dirname(script_target) or os.getcwd()
    shortcut_name = "voice_assistant_startup.cmd"
    shortcut_path = os.path.join(startup_path, shortcut_name)

    command = (
        '@echo off\n'
        f'cd /d "{script_dir}"\n'
        'py voice_assistant.py\n'
    )

    with open(shortcut_path, "w", encoding="utf-8") as file:
        file.write(command)

    return shortcut_path


def save_custom_commands(commands: dict[str, str], path: str | None = None) -> str:
    config_path = path or os.path.join(os.path.dirname(__file__), "custom_commands.json")
    normalized = {str(key).strip().lower(): str(value).strip().lower() for key, value in commands.items()}
    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(normalized, file, indent=2, ensure_ascii=False)
    return config_path


def add_custom_command(name: str, target: str, path: str | None = None) -> bool:
    config_path = path or os.path.join(os.path.dirname(__file__), "custom_commands.json")
    commands = load_custom_commands(config_path)
    commands[name.strip().lower()] = target.strip().lower()
    save_custom_commands(commands, config_path)
    return os.path.exists(config_path)


def build_welcome_page() -> dict[str, str]:
    return {
        "title": "Ava",
        "subtitle": "Your personal AI assistant",
        "tagline": "Smart. Calm. Always ready.",
        "theme": "Premium AI Dashboard",
        "persona": "Neural Voice • Private Mode",
        "button": "Start Listening",
    }


# Simple settings persistence for UI preferences
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "va_settings.json")


def load_settings(path: str | None = None) -> dict:
    cfg = path or SETTINGS_PATH
    defaults = {"voice_type": "Zira", "pitch": 0, "rate_percent": 100}
    try:
        if os.path.exists(cfg):
            with open(cfg, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                defaults.update(data)
    except Exception:
        pass
    return defaults


def save_settings(settings: dict, path: str | None = None) -> str:
    cfg = path or SETTINGS_PATH
    try:
        with open(cfg, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return cfg


# Load settings at module import
SETTINGS = load_settings()


def launch_welcome_window() -> tk.Tk | None:
    if tk is None:
        return None

    page = build_welcome_page()
    root = tk.Tk()
    root.title(page["title"])
    root.geometry("900x560")
    root.configure(bg="#070B17")
    root.resizable(False, False)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (900 // 2)
    y = (screen_height // 2) - (560 // 2)
    root.geometry(f"900x560+{x}+{y}")
    root.overrideredirect(True)

    bg = tk.Canvas(root, width=900, height=560, bg="#070B17", highlightthickness=0)
    bg.pack(fill="both", expand=True)

    bg.create_rectangle(0, 0, 900, 560, fill="#070B17", outline="")
    bg.create_oval(-120, -80, 420, 360, fill="#1D4ED8", outline="", stipple="gray50")
    bg.create_oval(520, -80, 1040, 360, fill="#8B5CF6", outline="", stipple="gray50")
    bg.create_oval(620, 320, 980, 700, fill="#10B981", outline="", stipple="gray50")
    bg.create_oval(350, 110, 550, 310, fill="#0B1020", outline="#22D3EE", width=2)

    panel = tk.Frame(root, bg="#0F172A", bd=0, highlightthickness=0)
    panel.place(x=65, y=50, width=770, height=460)
    panel.configure(relief="flat")

    glow = tk.Canvas(panel, width=770, height=460, bg="#0F172A", highlightthickness=0)
    glow.place(x=0, y=0)
    glow.create_rectangle(10, 10, 760, 450, fill="#111827", outline="#8B5CF6", width=2)

    status_chip = tk.Label(
        panel,
        text="  ONLINE  ",
        fg="#DCFCE7",
        bg="#14532D",
        font=("Segoe UI", 10, "bold"),
        padx=10,
        pady=5,
    )
    status_chip.place(x=50, y=40)

    splash_arc = tk.Canvas(panel, width=160, height=160, bg="#111827", highlightthickness=0)
    splash_arc.place(x=610, y=90)
    splash_arc.create_oval(20, 20, 140, 140, outline="#38BDF8", width=2)
    splash_arc.create_oval(35, 35, 125, 125, outline="#A78BFA", width=2)
    splash_arc.create_oval(55, 55, 105, 105, fill="#10B981", outline="#10B981")

    title_shadow = tk.Label(
        panel,
        text=page["title"],
        font=("Segoe UI", 40, "bold"),
        fg="#020617",
        bg="#111827",
    )
    title_shadow.place(x=53, y=93)

    title_label = tk.Label(
        panel,
        text=page["title"],
        font=("Segoe UI", 40, "bold"),
        fg="#F8FAFC",
        bg="#111827",
    )
    title_label.place(x=50, y=90)

    subtitle = tk.Label(
        panel,
        text=page["subtitle"],
        font=("Segoe UI", 16),
        fg="#C7D2FE",
        bg="#111827",
    )
    subtitle.place(x=52, y=170)

    tagline = tk.Label(
        panel,
        text=page["tagline"],
        font=("Segoe UI", 12),
        fg="#A5B4FC",
        bg="#111827",
    )
    tagline.place(x=52, y=210)

    theme_badge = tk.Label(
        panel,
        text=page.get("theme", "Premium AI Dashboard"),
        font=("Segoe UI", 10, "bold"),
        fg="#E9D5FF",
        bg="#312E81",
        padx=12,
        pady=6,
    )
    theme_badge.place(x=52, y=250)

    persona_badge = tk.Label(
        panel,
        text=page.get("persona", "Neural Voice • Private Mode"),
        font=("Segoe UI", 9, "bold"),
        fg="#CFFAFE",
        bg="#0F766E",
        padx=10,
        pady=5,
    )
    persona_badge.place(x=220, y=250)

    button = tk.Button(
        panel,
        text=page["button"],
        width=22,
        height=2,
        bg="#8B5CF6",
        fg="white",
        activebackground="#7C3AED",
        font=("Segoe UI", 12, "bold"),
        borderwidth=0,
        command=root.destroy,
    )
    button.place(x=52, y=310)

    def preview_voice():
        speak("Namaste, main Ava hoon. Aap kaise ho?")

    preview_btn = tk.Button(
        panel,
        text="Preview Voice",
        width=14,
        height=1,
        bg="#06B6D4",
        fg="white",
        activebackground="#0891B2",
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
        command=preview_voice,
    )
    preview_btn.place(x=300, y=310)

    # Voice type dropdown
    voice_label = tk.Label(panel, text="Voice:", fg="#C7D2FE", bg="#111827", font=("Segoe UI", 10))
    voice_label.place(x=52, y=340)

    voice_var = tk.StringVar(value=SETTINGS.get("voice_type", "Zira"))
    voice_options = ["Zira", "Samantha", "Neural"]
    voice_menu = tk.OptionMenu(panel, voice_var, *voice_options)
    voice_menu.configure(bg="#0F172A", fg="#E6E6E6", highlightthickness=0)
    voice_menu.place(x=100, y=336)

    def save_voice_pref():
        SETTINGS["voice_type"] = voice_var.get()
        save_settings(SETTINGS)
        speak(f"Voice preference {voice_var.get()} saved")

    # Pitch and rate controls
    pitch_label = tk.Label(panel, text="Pitch:", fg="#C7D2FE", bg="#111827", font=("Segoe UI", 10))
    pitch_label.place(x=52, y=370)
    pitch_var = tk.IntVar(value=int(SETTINGS.get("pitch", 0)))
    pitch_scale = tk.Scale(panel, from_=-10, to=10, orient="horizontal", variable=pitch_var, bg="#111827", fg="#E6E6E6", highlightthickness=0, length=200)
    pitch_scale.place(x=100, y=360)

    rate_label = tk.Label(panel, text="Rate %:", fg="#C7D2FE", bg="#111827", font=("Segoe UI", 10))
    rate_label.place(x=320, y=370)
    rate_var = tk.IntVar(value=int(SETTINGS.get("rate_percent", 100)))
    rate_scale = tk.Scale(panel, from_=50, to=150, orient="horizontal", variable=rate_var, bg="#111827", fg="#E6E6E6", highlightthickness=0, length=200)
    rate_scale.place(x=390, y=360)

    def save_voice_tuning():
        SETTINGS["pitch"] = int(pitch_var.get())
        SETTINGS["rate_percent"] = int(rate_var.get())
        save_settings(SETTINGS)
        speak("Voice tuning saved")

    tune_btn = tk.Button(panel, text="Save Tuning", width=12, bg="#334155", fg="white", command=save_voice_tuning, borderwidth=0)
    tune_btn.place(x=610, y=360)

    save_btn = tk.Button(panel, text="Save", width=8, bg="#334155", fg="white", command=save_voice_pref, borderwidth=0)
    save_btn.place(x=220, y=336)

    status = tk.Label(
        panel,
        text="Listening for your command...",
        font=("Segoe UI", 11),
        fg="#94A3B8",
        bg="#111827",
    )
    status.place(x=52, y=380)

    card1 = tk.Label(panel, text="Voice Control", bg="#1E293B", fg="#E2E8F0", font=("Segoe UI", 11, "bold"), padx=12, pady=8)
    card1.place(x=520, y=110, width=170)

    card2 = tk.Label(panel, text="Smart Tasks", bg="#1E293B", fg="#E2E8F0", font=("Segoe UI", 11, "bold"), padx=12, pady=8)
    card2.place(x=520, y=175, width=170)

    card3 = tk.Label(panel, text="Personal Mode", bg="#1E293B", fg="#E2E8F0", font=("Segoe UI", 11, "bold"), padx=12, pady=8)
    card3.place(x=520, y=240, width=170)

    waveform = tk.Canvas(panel, width=170, height=80, bg="#111827", highlightthickness=0)
    waveform.place(x=520, y=310)
    waveform_bars = []
    for index in range(8):
        x1 = 10 + index * 18
        x2 = x1 + 10
        bar = waveform.create_rectangle(x1, 52, x2, 60, fill="#22D3EE", outline="#22D3EE")
        waveform_bars.append(bar)

    pulse = tk.Canvas(panel, width=140, height=140, bg="#111827", highlightthickness=0)
    pulse.place(x=590, y=300)
    pulse.create_oval(10, 10, 130, 130, outline="#22D3EE", width=2)
    pulse.create_oval(28, 28, 112, 112, outline="#A78BFA", width=2)
    pulse.create_oval(48, 48, 92, 92, fill="#22D3EE", outline="#22D3EE")

    def animate_pulse(index: int = 0) -> None:
        sizes = [18, 26, 34, 26, 18]
        pulse.itemconfig(1, outline="#A78BFA", width=2)
        pulse.itemconfig(2, outline="#22D3EE", width=2)
        pulse.itemconfig(3, fill="#22D3EE", outline="#22D3EE")
        pulse.coords(1, 10 + index, 10 + index, 130 - index, 130 - index)
        pulse.coords(2, 28 + index, 28 + index, 112 - index, 112 - index)
        splash_arc.coords(2, 35 + index, 35 + index, 125 - index, 125 - index)

        for bar_index, bar in enumerate(waveform_bars):
            height = 18 + ((bar_index + index) % 5) * 8
            waveform.coords(bar, 10 + bar_index * 18, 70 - height, 18 + bar_index * 18, 70)

        root.after(180, lambda: animate_pulse((index + 1) % len(sizes)))

    root.after(180, animate_pulse)
    return root


def strip_wake_phrase(command: str) -> str:
    text = normalize_command(command)
    for phrase in sorted(WAKE_PHRASES, key=len, reverse=True):
        if phrase in text:
            text = text.replace(phrase, " ", 1)
    return " ".join(text.split())


def is_wake_word(command: str) -> bool:
    text = normalize_command(command)
    return any(phrase in text for phrase in WAKE_PHRASES)


def find_app_path(app_name: str) -> str | None:
    candidates = COMMON_APP_PATHS.get(app_name.lower(), [])
    for candidate in candidates:
        expanded = os.path.expandvars(os.path.expanduser(candidate))
        if os.path.exists(expanded):
            return expanded
        if shutil.which(candidate):
            return shutil.which(candidate)
    return None


def open_app(app_name: str) -> str:
    path = find_app_path(app_name)
    if path:
        try:
            if app_name.lower() == "teams":
                subprocess.Popen([path])
            else:
                os.startfile(path)
            return f"{app_name.title()} khul gaya."
        except Exception:
            return f"{app_name.title()} kholne mein dikkat hui."
    return f"{app_name.title()} system par nahi mila."


def speak(text: str) -> None:
    """Speak through a polished female-style voice when available."""
    print(f"Assistant: {text}")
    # Prefer pyttsx3 when available for offline TTS and voice selection
    if pyttsx3 is not None:
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)
            voices = engine.getProperty("voices") or []
            chosen = None
            # Respect user-selected voice type when possible
            preferred = SETTINGS.get("voice_type", "Zira").lower()
            preferred_keywords = []
            if "zira" in preferred or "zira" == preferred:
                preferred_keywords = ["zira"]
            elif "samantha" in preferred or "samantha" == preferred:
                preferred_keywords = ["samantha"]
            elif "neural" in preferred or "neural" == preferred:
                # Neural is not a local pyttsx3 voice; try to prefer any female voice
                preferred_keywords = ["zira", "samantha", "victoria", "female", "woman"]

            for voice in voices:
                name = (getattr(voice, "name", "") or "").lower()
                if any(k in name for k in preferred_keywords):
                    chosen = voice.id
                    break
            # Fallback: prefer voices with gender metadata if present
            if not chosen:
                for voice in voices:
                    try:
                        if getattr(voice, "gender", "").lower() == "female":
                            chosen = voice.id
                            break
                    except Exception:
                        continue
            if chosen:
                try:
                    engine.setProperty("voice", chosen)
                except Exception:
                    pass
            engine.say(text)
            engine.runAndWait()
            return
        except Exception:
            # If pyttsx3 failed for any reason, fallback to platform tools
            pass

    # Windows SAPI fallback using PowerShell (works offline on Windows)
    if os.name == "nt":
        try:
            # Enumerate installed voices and prefer common female names (Zira/Samantha/etc.)
            # Escape double-quotes for PowerShell by replacing " with `"
            # Build SSML using saved pitch/rate settings and escape for PowerShell
            # Escape XML special chars first
            xml_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            pitch = int(SETTINGS.get("pitch", 0))
            rate_percent = int(SETTINGS.get("rate_percent", 100))
            pitch_str = f"{('+' if pitch>0 else '')}{pitch}%"
            ssml = f'<speak version="1.0" xml:lang="en-US"><prosody pitch="{pitch_str}" rate="{rate_percent}%">{xml_text}</prosody></speak>'
            # Escape double quotes for PowerShell string literal
            ssml_escaped = ssml.replace('"', '`"')
            # Prepare PowerShell command to select a female voice and speak SSML
            ps = (
                "Add-Type -AssemblyName System.Speech;"
                "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                "$voices = $speak.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name };"
                "$female = $voices | Where-Object { $_ -match 'zira|samantha|victoria|katherine|kathleen|helen|aria|female' } | Select-Object -First 1;"
                "if (-not $female) { $female = $voices | Select-Object -First 1 };"
                "$speak.SelectVoice($female);"
                f"$speak.SpeakSsml(\"{ssml_escaped}\");"
            )
            # Run PowerShell SSML; fall back to plain Speak if SpeakSsml isn't supported
            try:
                subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False, capture_output=True)
            except Exception:
                escaped = text.replace('"', '`"')
                ps2 = (
                    "Add-Type -AssemblyName System.Speech;"
                    "$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
                    "$voices = $speak.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name };"
                    "$female = $voices | Where-Object { $_ -match 'zira|samantha|victoria|katherine|kathleen|helen|aria|female' } | Select-Object -First 1;"
                    "if (-not $female) { $female = $voices | Select-Object -First 1 };"
                    "$speak.SelectVoice($female);"
                    f"$speak.Speak(\"{escaped}\");"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps2], check=False, capture_output=True)
            return
        except Exception:
            pass

    # Last resort: print the text (already printed above)


def contains_word(text: str, *words: str) -> bool:
    for word in words:
        if re.search(rf"(^|\s){re.escape(word)}(\s|$)", text):
            return True
    return False


def run_custom_script(command_text: str) -> str | None:
    text = command_text.strip().lower()
    for script_name, script_handler in CUSTOM_HINDI_SCRIPTS.items():
        if script_name in text:
            return script_handler()

    if "study mode" in text or "study" in text or "padho" in text:
        launch_app_if_known("vscode")
        launch_app_if_known("chrome")
        return "Study mode shuru ho gaya. Aap ready hain."

    if "work mode" in text or "kaam mode" in text or "office" in text:
        launch_app_if_known("teams")
        launch_app_if_known("chrome")
        return "Work mode active hai. Teams aur browser ready hain."

    custom_commands = load_custom_commands()
    for pattern, action in custom_commands.items():
        if pattern in text:
            if action in COMMON_APP_PATHS:
                response = open_app(action)
                if "project" in pattern or "workspace" in pattern:
                    return f"Project ready hai. {response}"
                return response
            if action in CUSTOM_HINDI_SCRIPTS:
                return run_custom_script(action)
            if action.startswith("http"):
                webbrowser.open(action)
                return f"Website {action} khul gaya."
            if action == "study mode":
                return run_custom_script(action)
            if action == "work mode":
                return run_custom_script(action)
    return None


def launch_app_if_known(app_name: str) -> None:
    if app_name.lower() in COMMON_APP_PATHS:
        open_app(app_name)


def handle_command(command: str) -> str:
    if not command or not command.strip():
        return "Koi command nahi suna gaya."

    text = strip_wake_phrase(command)
    if not text:
        return "Ji, main sun rahi hoon. Aapka command boliye."

    custom_script = run_custom_script(text)
    if custom_script:
        return custom_script

    if contains_word(text, "hello", "hi", "namaste", "hey", "hii", "namastey"):
        return "Namaste! Main aapke liye ready hoon. Aap kya kaam karna chahte ho?"

    if contains_word(text, "samay", "time", "time kya hai", "samay kya hai"):
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"Abhi samay aur time hai {current_time}."

    if contains_word(text, "date", "tareekh", "aaj ki tareekh", "date kya hai"):
        current_date = datetime.datetime.now().strftime("%d %B %Y")
        return f"Aaj ki tareekh hai {current_date}."

    custom_commands = load_custom_commands()
    for pattern, action in custom_commands.items():
        if pattern in text:
            if action in COMMON_APP_PATHS:
                response = open_app(action)
                if "project" in pattern or "workspace" in pattern:
                    return f"Project ready hai. {response}"
                return response
            if action in CUSTOM_HINDI_SCRIPTS:
                return run_custom_script(action)
            if action.startswith("http"):
                webbrowser.open(action)
                return f"Website {action} khul gaya."
            if action == "study mode":
                return run_custom_script(action)
            if action == "work mode":
                return run_custom_script(action)

    if "whatsapp" in text or "wa" in text or "whats app" in text:
        return open_app("whatsapp")

    if "teams" in text or "microsoft teams" in text:
        return open_app("teams")

    if "vscode" in text or "visual studio code" in text or "code" in text:
        return open_app("vscode")

    if "chrome" in text or "google chrome" in text or "browser" in text:
        return open_app("chrome")

    if "notepad" in text or "note pad" in text:
        return open_app("notepad")

    if "calculator" in text or "kalkulator" in text or "calc" in text:
        return open_app("calculator")

    if "command prompt" in text or "cmd" in text or "terminal" in text:
        return open_app("cmd")

    if "file explorer" in text or "explorer" in text or "folder" in text:
        return open_app("explorer")

    if "youtube" in text or "you tube" in text:
        webbrowser.open("https://www.youtube.com")
        return "YouTube khul gaya."

    if any(word in text for word in ["search", "khoj", "google karo", "search karo"]):
        query = text
        for marker in ["search", "khoj", "search karo", "google karo"]:
            if marker in text:
                query = text.replace(marker, "", 1).strip()
                break
        if not query:
            return "Aapko kya search karna hai?"
        webbrowser.open(f"https://www.google.com/search?q={quote(query)}")
        return f"Google par '{query}' ke liye search kar raha hoon."

    if "open" in text and "website" in text:
        match = text.replace("open", "", 1).replace("website", "", 1).strip()
        if match:
            url = match if match.startswith("http") else f"https://{match}"
            webbrowser.open(url)
            return f"Website {match} khul gaya."

    if any(word in text for word in ["shutdown", "band kar do", "shut down", "laptop band kar do"]):
        subprocess.run("shutdown /s /t 0", shell=True)
        return "Laptop shut down ho raha hai."

    if any(word in text for word in ["restart", "reboot", "restart kar do", "laptop reboot"]):
        subprocess.run("shutdown /r /t 0", shell=True)
        return "Laptop restart ho raha hai."

    if any(word in text for word in ["lock", "lock kar do", "screen lock", "laptop lock"]):
        subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        return "Laptop lock kar diya gaya."

    if any(word in text for word in ["startup", "start on boot", "auto start", "startup install", "laptop start par"]):
        target = install_startup_shortcut()
        return f"Startup shortcut install ho gaya. File: {target}"

    if any(word in text for word in ["bye", "exit", "stop", "close", "alvida", "ruk ja", "band kar do", "goodbye"]):
        return "Alvida! Main aapke liye ready hoon, kabhi bhi bula lena."

    return "Mujhe samajh nahi aaya. Aap phir se clear boliye."


def listen_for_command() -> str:
    if sr is None:
        raise RuntimeError("SpeechRecognition package install nahi hai. Requirements install karo.")

    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 350
    with sr.Microphone() as source:
        print("Sun raha hoon...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    for language in ["hi-IN", "en-IN"]:
        try:
            return recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            continue
    return ""


def main() -> None:
    speak("Namaste, main aapki assistant hoon. Wake word ke liye 'Hey assistant' boliye.")

    while True:
        try:
            command = listen_for_command()
        except RuntimeError as exc:
            print(exc)
            break

        if not command:
            continue

        if not is_wake_word(command):
            continue

        print(f"Wake word detect hua: {command}")
        speak("Ji, main sun rahi hoon. Aapka command boliye.")

        while True:
            try:
                command = listen_for_command()
            except RuntimeError as exc:
                print(exc)
                raise

            if not command:
                speak("Koi command suna nahi gaya. Fir se boliye.")
                continue

            print(f"Aapne kaha: {command}")
            if is_wake_word(command):
                speak("Ji, main sun rahi hoon.")
                continue

            response = handle_command(command)
            speak(response)

            if any(word in command.lower() for word in ["bye", "exit", "stop", "close", "alvida", "ruk ja", "band kar do", "goodbye"]):
                return


if __name__ == "__main__":
    window = launch_welcome_window()
    if window is not None:
        thread = threading.Thread(target=main, daemon=True)
        thread.start()
        window.mainloop()
    else:
        main()
