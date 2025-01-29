import tkinter as tk
from tkinter import messagebox, PhotoImage, font, ttk
from PIL import Image, ImageTk
import webbrowser
import json
import os
import keyboard
import sys
import ctypes
import winreg
import datetime
import subprocess

# Application Constants
APP_NAME = "Web Shortcut Creator"
APP_VERSION = "1.1.1"
APP_COMPANY = "SandaruAbey"
SHORTCUT_FILE = os.path.join(os.getenv('APPDATA'), 'WebShortcutCreator', 'shortcuts.json')
LOGO_PATH = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), 
                        "asserts", "logo.png")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def ensure_app_directory():
    app_dir = os.path.dirname(SHORTCUT_FILE)
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

# def add_to_startup():
#     try:
#         key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
#                             r"Software\Microsoft\Windows\CurrentVersion\Run", 
#                             0, winreg.KEY_SET_VALUE)
#         executable_path = sys.executable if getattr(sys, 'frozen', False) else __file__
#         winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, f'"{executable_path}"')
#         winreg.CloseKey(key)
#     except Exception as e:
#         print(f"Error adding to startup: {e}")
def add_to_startup():
    """Add the application to Windows startup with improved error handling"""
    try:
        # Get the startup folder path
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        
        # Create shortcut name
        shortcut_path = os.path.join(startup_folder, f'{APP_NAME}.bat')
        
        # Get the executable path
        if getattr(sys, 'frozen', False):
            # If running as exe
            app_path = sys.executable
        else:
            # If running as script
            app_path = sys.executable
            script_path = os.path.abspath(__file__)
            app_path = f'"{app_path}" "{script_path}"'

        # Create batch file content
        batch_content = f'@echo off\nstart "" {app_path}'
        
        # Create the batch file
        with open(shortcut_path, 'w') as f:
            f.write(batch_content)
            
        # Also add to registry for redundancy
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
        except Exception as reg_error:
            print(f"Registry startup entry failed (non-critical): {reg_error}")
            
        return True
            
    except Exception as e:
        print(f"Error adding to startup: {str(e)}")
        messagebox.showwarning(
            "Startup Warning",
            "Could not add to startup automatically.\n"
            "To start automatically with Windows:\n"
            "1. Press Win + R\n"
            "2. Type 'shell:startup'\n"
            "3. Drag this program into the folder that opens"
        )
        return False
def detect_installed_browsers():
    browsers = {"Default Browser": ""}
    
    # Common browser registry paths
    browser_paths = {
        "Chrome": r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        "Firefox": r"Software\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
        "Edge": r"Software\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
        "Opera": r"Software\Microsoft\Windows\CurrentVersion\App Paths\opera.exe",
        "Brave": r"Software\Microsoft\Windows\CurrentVersion\App Paths\brave.exe"
    }
    
    for browser_name, reg_path in browser_paths.items():
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
            browser_path = winreg.QueryValue(key, None)
            winreg.CloseKey(key)
            if os.path.exists(browser_path):
                browsers[browser_name] = browser_path
        except:
            continue
            
    return browsers


class WebShortcutCreator:
    def __init__(self, root):
        self.root = root
        ensure_app_directory()
        self.shortcuts = self.load_shortcuts()
        self.installed_browsers = detect_installed_browsers()
        self.setup_gui()
        self.bind_existing_shortcuts()
        add_to_startup()

    def load_shortcuts(self):
        if os.path.exists(SHORTCUT_FILE):
            try:
                with open(SHORTCUT_FILE, "r") as file:
                    return json.load(file)
            except:
                return {}
        return {}

    def save_shortcuts(self):
        with open(SHORTCUT_FILE, "w") as file:
            json.dump(self.shortcuts, file)

    def open_url(self, url, browser_path=None):
        try:
            if browser_path:
                subprocess.Popen([browser_path, url])
            else:
                webbrowser.open(url)
        except Exception as e:
            print(f"Error opening URL: {e}")
            # Fallback to default browser
            webbrowser.open(url)

    def add_shortcut(self):
        key = self.key_entry.get().strip().upper()
        url = self.url_entry.get().strip()
        selected_browser = self.browser_var.get()
        browser_path = self.installed_browsers.get(selected_browser, "")

        if not key or not url:
            messagebox.showwarning("Warning", "Please fill in both fields.")
            return

        if len(key) != 1 or not key.isalnum():
            messagebox.showerror("Error", "Shortcut key must be a single letter or digit.")
            return

        try:
            shortcut = f"ctrl+alt+{key.lower()}"
            try:
                keyboard.remove_hotkey(shortcut)
            except:
                pass
            
            keyboard.add_hotkey(shortcut, lambda: self.open_url(url, browser_path))
            self.shortcuts[shortcut] = {
                "url": url,
                "browser": selected_browser,
                "browser_path": browser_path
            }
            self.save_shortcuts()
            self.refresh_shortcut_list()
            messagebox.showinfo("Success", f"Shortcut {shortcut} added successfully!")
            self.key_entry.delete(0, tk.END)
            self.url_entry.delete(0, tk.END)
            self.browser_var.set("Default Browser")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add shortcut. Error: {str(e)}\nTry running as administrator.")

    def bind_existing_shortcuts(self):
        for shortcut, data in self.shortcuts.items():
            try:
                try:
                    keyboard.remove_hotkey(shortcut)
                except:
                    pass
                if isinstance(data, dict):
                    keyboard.add_hotkey(shortcut, lambda u=data["url"], b=data["browser_path"]: self.open_url(u, b))
                else:
                    # Handle old format shortcuts
                    keyboard.add_hotkey(shortcut, lambda u=data: self.open_url(u))
            except Exception as e:
                print(f"Error binding shortcut {shortcut}: {e}")

    def remove_shortcut(self):
        selected = self.shortcut_listbox.curselection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a shortcut to remove.")
            return

        full_text = self.shortcut_listbox.get(selected)
        shortcut = full_text.split(" -> ")[0].strip()
        
        try:
            keyboard.remove_hotkey(shortcut)
            del self.shortcuts[shortcut]
            self.save_shortcuts()
            self.refresh_shortcut_list()
            messagebox.showinfo("Success", f"Shortcut {shortcut} removed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove shortcut: {str(e)}")

    def refresh_shortcut_list(self):
        self.shortcut_listbox.delete(0, tk.END)
        for shortcut, data in self.shortcuts.items():
            if isinstance(data, dict):
                browser_name = data.get("browser", "Default Browser")
                self.shortcut_listbox.insert(tk.END, f"{shortcut} -> {data['url']} ({browser_name})")
            else:
                # Handle old format shortcuts
                self.shortcut_listbox.insert(tk.END, f"{shortcut} -> {data} (Default Browser)")

    def setup_gui(self):
        self.root.title(APP_NAME)
        self.root.geometry("1000x700")
        self.root.configure(bg="#000000")

        # Center window
        window_width = 1200
        window_height = 700
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Custom Fonts
        title_font = ("Segoe UI Black", 32, "bold")
        label_font = ("Segoe UI", 14, "bold")
        button_font = ("Segoe UI", 12, "bold")
        list_font = ("Segoe UI", 12)

        # Title Section
        title_frame = tk.Frame(self.root, bg="#000000")
        title_frame.pack(pady=(30, 20))

        try:
            original_image = Image.open(LOGO_PATH)
            resized_image = original_image.resize((150, 150))
            self.logo_image = ImageTk.PhotoImage(resized_image)
            logo_label = tk.Label(title_frame, image=self.logo_image, bg="#000000")
            logo_label.pack()
        except Exception as e:
            print(f"Error loading logo: {e}")

        title_label = tk.Label(title_frame, text="WEB SHORTCUT CREATOR", 
                             font=title_font, fg="white", bg="#000000")
        title_label.pack(pady=(20, 30))

        # Input Section
        input_frame = tk.Frame(self.root, bg="#000000")
        input_frame.pack(pady=30)

        # First row - Key and URL
        key_label = tk.Label(input_frame, text="SHORT KEY : Ctrl + Alt +", 
                           font=label_font, fg="white", bg="#000000")
        key_label.grid(row=0, column=0, padx=(0, 10), pady=10)

        self.key_entry = tk.Entry(input_frame, width=8, font=label_font, 
                                bg="#DDDDDD", relief="flat")
        self.key_entry.grid(row=0, column=1, padx=(0, 20))

        url_label = tk.Label(input_frame, text="URL :", 
                           font=label_font, fg="white", bg="#000000")
        url_label.grid(row=0, column=2, padx=(0, 10))

        self.url_entry = tk.Entry(input_frame, width=40, font=label_font, 
                                bg="#DDDDDD", relief="flat")
        self.url_entry.grid(row=0, column=3, padx=(0, 20))

        # Second row - Browser selection and Add button
        browser_label = tk.Label(input_frame, text="Browser:", 
                               font=label_font, fg="white", bg="#000000")
        browser_label.grid(row=1, column=0, padx=(0, 10), pady=10)

        self.browser_var = tk.StringVar(value="Default Browser")
        browser_dropdown = ttk.Combobox(input_frame, 
                                      textvariable=self.browser_var,
                                      values=list(self.installed_browsers.keys()),
                                      state="readonly",
                                      width=20,
                                      font=label_font)
        browser_dropdown.grid(row=1, column=1, columnspan=2, padx=(0, 20))

        add_button = tk.Button(input_frame, text="ADD SHORTCUT", 
                             font=button_font,
                             command=self.add_shortcut, 
                             bg="#44C767", fg="white",
                             relief="flat", padx=20, pady=10)
        add_button.grid(row=1, column=3, padx=10)

        # Listbox Section
        list_frame = tk.Frame(self.root, bg="#000000")
        list_frame.pack(pady=30, expand=True, fill="both", padx=50)

        self.shortcut_listbox = tk.Listbox(list_frame, 
                                         font=list_font,
                                         bg="#DDDDDD",
                                         relief="flat",
                                         selectmode="single",
                                         height=12)
        self.shortcut_listbox.pack(side="left", fill="both", expand=True, padx=(0, 20))

        # Add scrollbar to listbox
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="left", fill="y")
        
        # Configure scrollbar
        self.shortcut_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.shortcut_listbox.yview)

        remove_button = tk.Button(list_frame, text="REMOVE", 
                                font=button_font,
                                command=self.remove_shortcut,
                                bg="#FF0000", fg="white",
                                relief="flat", padx=20, pady=10)
        remove_button.pack(side="left", anchor="n")

        # Version and Copyright
        version_label = tk.Label(self.root, 
                               text=f"Version {APP_VERSION}",
                               font=("Segoe UI", 10), 
                               fg="white", bg="#000000")
        version_label.pack(pady=(10, 0))

        copyright_label = tk.Label(self.root, 
                                 text=f"Copyright © {datetime.datetime.now().year} {APP_COMPANY}",
                                 font=("Segoe UI", 10), 
                                 fg="white", bg="#000000")
        copyright_label.pack(pady=(5, 20))

def main():
    if not is_admin():
        if messagebox.askyesno("Administrator Rights Required", 
                             "This app needs administrator rights to create global shortcuts.\nDo you want to restart as administrator?"):
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit()
            except:
                messagebox.showerror("Error", "Failed to restart as administrator.")
    
    root = tk.Tk()
    app = WebShortcutCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()