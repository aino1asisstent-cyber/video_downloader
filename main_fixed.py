#!/usr/bin/env python3
"""
Video Downloader Pro - Fixed Version
Profesjonalna aplikacja do pobierania wideo z monitoringiem czatów
"""

import os
import re
import subprocess
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib.parse import unquote, urlparse

import pyperclip
import requests

# Import naszych modułów
try:
    from analytics_service import analytics_service
    from chat_monitor import get_chat_monitor
    from download_manager import download_manager
    from performance_monitor import performance_monitor
    from subscription_manager import subscription_manager
    from security_validator import security_validator
    print("✅ Wszystkie moduły załadowane")
except ImportError as e:
    print(f"❌ Błąd importu modułów: {e}")
    sys.exit(1)

class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader Pro")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Konfiguracja
        self.monitoring = False
        self.last_clip = ""
        self.downloaded_files = []
        self.ffmpeg_path = self.find_ffmpeg()
        
        # Track app launch
        analytics_service.track_app_launch()
        
        # Konfiguracja download managera
        download_manager.add_callback('queued', self.on_url_queued)
        download_manager.add_callback('start', self.on_download_start)
        download_manager.add_callback('progress', self.on_download_progress)
        download_manager.add_callback('complete', self.on_download_complete)
        download_manager.add_callback('error', self.on_download_error)
        
        # Inicjalizuj chat monitor
        self.chat_monitor = get_chat_monitor(download_manager)
        self.chat_monitor.add_callback(self.on_chat_event)
        
        # Tworzenie interfejsu
        self.create_ui()
        
        # Uruchom główną pętlę
        self.update_clipboard()
        self.update_queue_status()
        self.update_subscription_status()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        print("🎬 Video Downloader Pro uruchomiony!")
    
    def create_ui(self):
        # Główny frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Panel subskrypcji
        self.create_subscription_ui(main_frame)
        
        # Panel monitorowania
        monitor_frame = tk.LabelFrame(main_frame, text="🎬 Pobieranie Wideo", padx=10, pady=10)
        monitor_frame.pack(fill="x", pady=(0, 10))
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Gotowy - FFmpeg: " + ("✅ Dostępny" if self.ffmpeg_path else "❌ Niedostępny"), 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Ładuj istniejące pliki
        self.refresh_file_list()
    
    def create_subscription_ui(self, parent):
        """Tworzy UI dla systemu subskrypcji"""
        sub_frame = tk.LabelFrame(parent, text="💰 Subskrypcja", fg="#FFD700", padx=10, pady=10)
        sub_frame.pack(fill="x", pady=(0, 10))
        
        # Status subskrypcji
        self.subscription_status_var = tk.StringVar()
        self.update_subscription_display()
        
        status_label = tk.Label(sub_frame, textvariable=self.subscription_status_var, 
                               font=('Arial', 10, 'bold'))
        status_label.pack(pady=5)
        
        # Przyciski subskrypcji
        btn_frame = tk.Frame(sub_frame)
        btn_frame.pack(fill="x", pady=5)
        
        if not subscription_manager.has_premium():
            tk.Button(btn_frame, text="🔓 Upgrade to Premium - $9.99/month", 
                     command=self.show_upgrade_dialog, 
                     bg="#FFD700", fg="black", font=('Arial', 9, 'bold')).pack(side="left", padx=5)
        else:
            tk.Button(btn_frame, text="⭐ Premium Active", 
                     bg="#4CAF50", fg="white", state="disabled").pack(side="left", padx=5)
    
    def update_subscription_display(self):
        """Aktualizuje wyświetlanie statusu subskrypcji"""
        sub_info = subscription_manager.get_subscription_info()
        
        if sub_info['is_premium']:
            status_text = f"⭐ PREMIUM ACTIVE | Expires: {sub_info['expiry_date']}"
            self.subscription_status_var.set(status_text)
        else:
            downloads_remaining = sub_info['downloads_remaining']
            if downloads_remaining == "unlimited":
                status_text = "🔓 FREEMIUM | Unlimited downloads"
            else:
                status_text = f"🔓 FREEMIUM | Downloads today: {sub_info['downloads_today']}/{sub_info['limits']['daily_downloads']}"
            self.subscription_status_var.set(status_text)
    
    def update_subscription_status(self):
        """Aktualizuj status subskrypcji co 30 sekund"""
        self.update_subscription_display()
        self.root.after(30000, self.update_subscription_status)
    
    def show_upgrade_dialog(self):
        """Pokazuje dialog upgrade'u do premium"""
        analytics_service.track_premium_interest("upgrade_button_click")
        
        upgrade_window = tk.Toplevel(self.root)
        upgrade_window.title("🚀 Upgrade to Premium")
        upgrade_window.geometry("500x400")
        upgrade_window.resizable(False, False)
        
        # Nagłówek
        tk.Label(upgrade_window, text="🚀 Video Downloader Premium", 
                font=('Arial', 16, 'bold'), fg="#FFD700").pack(pady=20)
        
        # Demo premium
        tk.Button(upgrade_window, text="🎮 Try Premium Features (Demo)", 
                 command=self.activate_premium_demo, 
                 bg="#4CAF50", fg="white", font=('Arial', 10, 'bold')).pack(pady=20)
    
    def activate_premium_demo(self):
        """Aktywuje demo premium na 1 godzinę"""
        subscription_manager.activate_premium(days=1)  # 1 dzień demo
        self.update_subscription_display()
        
        messagebox.showinfo("Premium Activated", 
                          "🎉 Premium features activated for 24 hours!")
        
        analytics_service.track_event("premium_demo_activated")
    
    def find_ffmpeg(self):
        """Sprawdź standardowe lokalizacje ffmpeg"""
        possible_paths = [
            "ffmpeg",
            "ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe"
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-version"], stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, timeout=5)
                if result.returncode == 0:
                    return path
            except Exception:
                continue
        
        return None
    
    def refresh_file_list(self):
        """Odświeża listę plików"""
        self.downloaded_files = []
        
    def update_clipboard(self):
        """Monitorowanie schowka"""
        self.root.after(1000, self.update_clipboard)
    
    def update_queue_status(self):
        """Aktualizuj status kolejki"""
        self.root.after(2000, self.update_queue_status)
    
    def on_closing(self):
        """Zamykanie aplikacji z trackingiem"""
        analytics_service.track_event("app_closed")
        
        if self.monitoring:
            self.stop_monitoring()
        
        # Zatrzymaj chat monitoring
        if hasattr(self, 'chat_monitor') and self.chat_monitor.monitoring:
            self.chat_monitor.stop_monitoring()
        
        self.root.destroy()

# Uruchomienie aplikacji
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()