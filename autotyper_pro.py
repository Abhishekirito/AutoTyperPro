import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import pyautogui
import keyboard
import re
import time

CONFIG_FILE = "config.json"
typing = False

# ---------------- CONFIG HANDLING (Your Code) ---------------- #
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    # Default config
    return {"start_key": "f12", "stop_key": "f11", "line_delay": 0}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# ---------------- AUTO TYPER LOGIC (Your Code) ---------------- #
def auto_type(text):
    global typing
    typing = True

    lines = text.splitlines()
    time.sleep(2.5)  # Give time to switch to target window

    for line in lines:
        if not typing:
            break
        pyautogui.write(line, interval=0.07)
        pyautogui.press("enter")
        time.sleep(0.05)

    typing = False
    root.after(0, lambda: label_status.config(text="Typing finished ✅", foreground="#004080"))

def start_typing():
    global typing
    if typing:
        return

    text = text_box.get("1.0", tk.END)
    if not text.strip():
        messagebox.showwarning("Warning", "Please enter text/code to type.")
        return

    label_status.config(text="Typing started...", foreground="#008000")
    threading.Thread(target=auto_type, args=(text,), daemon=True).start()

def stop_typing():
    global typing
    if typing:
        typing = False
        label_status.config(text="Auto Typer stopped ❌", foreground="red")
    else:
        label_status.config(text="Not running", foreground="gray")

# ---------------- CLEAR BUTTON (Your Code) ---------------- #
def clear_text():
    text_box.delete("1.0", tk.END)
    label_status.config(text="Text cleared", foreground="gray")

# ---------------- HOTKEYS (Your Code) ---------------- #
def bind_hotkeys():
    try:
        keyboard.add_hotkey(config["start_key"], start_typing)
        keyboard.add_hotkey(config["stop_key"], stop_typing)
    except Exception as e:
        messagebox.showerror("Hotkey Error", str(e))

def update_hotkeys():
    config["start_key"] = entry_start_key.get().lower().strip() or "f12"
    config["stop_key"] = entry_stop_key.get().lower().strip() or "f11"
    save_config(config)
    keyboard.unhook_all_hotkeys()
    bind_hotkeys()
    label_status.config(
        text=f"Hotkeys updated: Start [{config['start_key'].upper()}], Stop [{config['stop_key'].upper()}]",
        foreground="#008000"
    )

# ---------------- CODE HIGHLIGHTING (Your Code) ---------------- #
def highlight_code(event=None): # Added event=None to allow binding
    text_box.tag_remove("keyword", "1.0", "end")
    text_box.tag_remove("function", "1.0", "end")
    text_box.tag_remove("string", "1.0", "end")
    text_box.tag_remove("comment", "1.0", "end")
    text_box.tag_remove("number", "1.0", "end")

    keywords = r"\b(def|class|if|else|elif|import|from|return|for|while|try|except|finally|with|as|in|is|lambda|None|True|False)\b"
    functions = r"\b\w+(?=\()"
    strings = r"(['\"].*?['\"])"
    comments = r"#.*"
    # --- Add this line here ---
    numbers = r"\b\d+(\.\d*)?\b"  # Regex for integers and floats

    apply_tag_to_pattern(keywords, "keyword", "#0000ff")
    apply_tag_to_pattern(functions, "function", "purple")
    apply_tag_to_pattern(strings, "string", "#008000")
    apply_tag_to_pattern(comments, "comment", "#888888")
    apply_tag_to_pattern(numbers, "number", "red")

def apply_tag_to_pattern(pattern, tag_name, color):
    # Minor improvement for efficiency, still your logic
    content = text_box.get("1.0", "end")
    text_box.tag_config(tag_name, foreground=color)
    for match in re.finditer(pattern, content):
        start_index = f"1.0 + {match.start()} chars"
        end_index = f"1.0 + {match.end()} chars"
        text_box.tag_add(tag_name, start_index, end_index)


# ---------------- UI (Improved Version) ---------------- #
root = tk.Tk()
root.title("Auto Typer Pro — by Abhishek")
root.geometry("850x650")
root.minsize(300, 900)

# --- Theme and Styling ---
COLOR_BG = "#e8f1fc"
COLOR_HEADER = "#b0c8f0"
COLOR_ACCENT = "#003366"
COLOR_TEXT_BOX_BG = "#ffffff"
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_BUTTON = ("Segoe UI", 11, "bold")
FONT_CODE = ("Consolas", 12)

root.configure(bg=COLOR_BG)

# --- Header Frame ---
header_frame = tk.Frame(root, bg=COLOR_HEADER, pady=15)
header_frame.pack(fill=tk.X)
title = tk.Label(header_frame, text="💻 Auto Typer Pro", font=FONT_TITLE, bg=COLOR_HEADER, fg=COLOR_ACCENT)
title.pack()

# --- Main Content Frame ---
content_frame = tk.Frame(root, bg=COLOR_BG, padx=20, pady=10)
content_frame.pack(fill=tk.BOTH, expand=True)

# --- Text Box with Scrollbar ---
text_frame = tk.Frame(content_frame)
text_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 15))

text_scroll = ttk.Scrollbar(text_frame)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

text_box = tk.Text(text_frame, wrap="word", yscrollcommand=text_scroll.set, font=FONT_CODE,
                   bg=COLOR_TEXT_BOX_BG, fg="#002244", relief="solid", bd=1,
                   insertbackground=COLOR_ACCENT, undo=True, padx=10, pady=10)
text_box.pack(fill=tk.BOTH, expand=True)
text_scroll.config(command=text_box.yview)
# Bind key release to trigger highlighting dynamically
text_box.bind("<KeyRelease>", highlight_code)


# --- Controls Frame (Buttons) ---
controls_frame = tk.Frame(content_frame, bg=COLOR_BG)
controls_frame.pack(fill=tk.X, pady=10)
controls_frame.columnconfigure((0, 1, 2), weight=1) # Make columns expand equally

style = ttk.Style()
style.configure("TButton", font=FONT_BUTTON, padding=8)

btn_start = ttk.Button(controls_frame, text="▶ Start Typing", command=start_typing)
btn_start.grid(row=0, column=0, sticky="ew", padx=5)

btn_stop = ttk.Button(controls_frame, text="■ Stop Typing", command=stop_typing)
btn_stop.grid(row=0, column=1, sticky="ew", padx=5)

btn_clear = ttk.Button(controls_frame, text="🧹 Clear All", command=clear_text)
btn_clear.grid(row=0, column=2, sticky="ew", padx=5)


# --- Hotkey Settings Frame ---
hotkey_frame = ttk.LabelFrame(content_frame, text=" Hotkey Settings ", padding=15)
hotkey_frame.pack(fill=tk.X, pady=10)

tk.Label(hotkey_frame, text="Start Key:", font=FONT_BODY).pack(side=tk.LEFT, padx=(0, 5))
entry_start_key = ttk.Entry(hotkey_frame, width=10, font=FONT_BODY)
entry_start_key.insert(0, config["start_key"])
entry_start_key.pack(side=tk.LEFT)

tk.Label(hotkey_frame, text="Stop Key:", font=FONT_BODY).pack(side=tk.LEFT, padx=(20, 5))
entry_stop_key = ttk.Entry(hotkey_frame, width=10, font=FONT_BODY)
entry_stop_key.insert(0, config["stop_key"])
entry_stop_key.pack(side=tk.LEFT)

# Spacer to push update button to the right
spacer = tk.Frame(hotkey_frame)
spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

btn_update_hotkeys = ttk.Button(hotkey_frame, text="Update Hotkeys", command=update_hotkeys)
btn_update_hotkeys.pack(side=tk.RIGHT)


# --- Status Bar ---
label_status = tk.Label(content_frame,
                        text=f"Hotkeys ready: Start [{config['start_key'].upper()}], Stop [{config['stop_key'].upper()}]",
                        bg=COLOR_BG, fg=COLOR_ACCENT, font=("Segoe UI", 10, "italic"))
label_status.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))


# --- Finalization ---
bind_hotkeys()
highlight_code() # Initial highlight
root.mainloop()