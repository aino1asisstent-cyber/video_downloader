
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

from chat_monitor import get_chat_monitor
from download_manager import download_manager
from performance_monitor import performance_monitor


class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader & Converter")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Konfiguracja
        self.monitoring = False
        self.last_clip = ""
        self.downloaded_files = []
        self.ffmpeg_path = self.find_ffmpeg()
        
        # Uruchom automatyczne backupy przy starcie
        self.init_automatic_backups()
        
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
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # Główny frame
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Panel monitorowania
        monitor_frame = tk.LabelFrame(main_frame, text="🎬 Pobieranie Wideo", padx=10, pady=10)
        monitor_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(monitor_frame, text="🚀 Start Monitoring", command=self.start_monitoring,
                 bg="#4CAF50", fg="white", height=1, width=15).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(monitor_frame, text="⏹️ Stop", command=self.stop_monitoring,
                 bg="#F44336", fg="white", height=1, width=15).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(monitor_frame, text="💬 Chat Monitor", command=self.toggle_chat_monitoring,
                 bg="#9C27B0", fg="white", height=1, width=15).grid(row=0, column=2, padx=5, pady=5)
        
        self.monitor_status = tk.Label(monitor_frame, text="Status: Nieaktywny", fg="red")
        self.monitor_status.grid(row=0, column=3, padx=10)
        
        self.chat_monitor_status = tk.Label(monitor_frame, text="Czaty: Nieaktywne", fg="red")
        self.chat_monitor_status.grid(row=0, column=4, padx=10)
        
        # Panel testowania
        test_frame = tk.Frame(monitor_frame)
        test_frame.grid(row=1, column=0, columnspan=5, pady=10)
        
        tk.Label(test_frame, text="Test URL:").pack(side="left", padx=5)
        self.test_url_var = tk.StringVar()
        tk.Entry(test_frame, textvariable=self.test_url_var, width=40).pack(side="left", padx=5)
        tk.Button(test_frame, text="Dodaj do kolejki", command=self.add_to_queue,
                 bg="#2196F3", fg="white").pack(side="left", padx=5)
        tk.Button(test_frame, text="Pobierz teraz", command=self.test_download,
                 bg="#4CAF50", fg="white").pack(side="left", padx=5)
        
        # Panel kolejki pobierania
        queue_frame = tk.LabelFrame(monitor_frame, text="📥 Kolejka pobierania", padx=5, pady=5)
        queue_frame.grid(row=2, column=0, columnspan=5, pady=10, sticky="ew")
        
        # Status kolejki
        self.queue_status_var = tk.StringVar(value="Kolejka: 0 | Aktywne: 0 | Ukończone: 0")
        tk.Label(queue_frame, textvariable=self.queue_status_var).pack(pady=2)
        
        # Przyciski zarządzania kolejką
        queue_buttons = tk.Frame(queue_frame)
        queue_buttons.pack(fill="x", pady=2)
        
        tk.Button(queue_buttons, text="▶️ Start", command=self.start_queue,
                 bg="#4CAF50", fg="white", width=8).pack(side="left", padx=2)
        tk.Button(queue_buttons, text="⏸️ Pauza", command=self.pause_queue,
                 bg="#FF9800", fg="white", width=8).pack(side="left", padx=2)
        tk.Button(queue_buttons, text="🔄 Ponów", command=self.retry_failed,
                 bg="#9C27B0", fg="white", width=8).pack(side="left", padx=2)
        tk.Button(queue_buttons, text="🗑️ Wyczyść", command=self.clear_queue,
                 bg="#F44336", fg="white", width=8).pack(side="left", padx=2)
        
        # Konfiguracja
        config_frame = tk.Frame(main_frame)
        config_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(config_frame, text="Folder pobierania:").grid(row=0, column=0, padx=5, sticky="w")
        self.download_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "Videos"))
        tk.Entry(config_frame, textvariable=self.download_dir_var, width=50).grid(row=0, column=1, padx=5)
        tk.Button(config_frame, text="Przeglądaj", command=self.browse_directory).grid(row=0, column=2, padx=5)
        
        # Panel konwersji
        convert_frame = tk.LabelFrame(main_frame, text="🔧 Konwersja Wideo", padx=10, pady=10)
        convert_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(convert_frame, text="Plik źródłowy:").grid(row=0, column=0, padx=5, sticky="w")
        self.video_path_var = tk.StringVar()
        tk.Entry(convert_frame, textvariable=self.video_path_var, width=50).grid(row=0, column=1, padx=5)
        tk.Button(convert_frame, text="Wybierz", command=self.browse_video_file).grid(row=0, column=2, padx=5)
        
        tk.Label(convert_frame, text="Bitrate (kbps):").grid(row=1, column=0, padx=5, sticky="w")
        self.bitrate_var = tk.StringVar(value="800")
        tk.Entry(convert_frame, textvariable=self.bitrate_var, width=10).grid(row=1, column=1, padx=5, sticky="w")
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(convert_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        
        tk.Button(convert_frame, text="Konwertuj do MP4", command=self.convert_video,
                 bg="#2196F3", fg="white", height=1, width=15).grid(row=1, column=2, padx=5, pady=5)
        
        # Panel ustawień jakości
        quality_frame = tk.LabelFrame(main_frame, text="⚙️ Ustawienia jakości", padx=10, pady=10)
        quality_frame.pack(fill="x", pady=(0, 10))
        
        self.auto_convert_var = tk.BooleanVar(value=True)
        tk.Checkbutton(quality_frame, text="Automatyczna konwersja MOV → MP4", 
                      variable=self.auto_convert_var).pack(anchor="w")
        
        self.optimize_web_var = tk.BooleanVar(value=True)
        tk.Checkbutton(quality_frame, text="Optymalizacja dla web (fast start)", 
                      variable=self.optimize_web_var).pack(anchor="w")
        
        # Presets jakości
        preset_frame = tk.Frame(quality_frame)
        preset_frame.pack(fill="x", pady=5)
        
        tk.Label(preset_frame, text="Preset jakości:").pack(side="left", padx=5)
        self.quality_preset_var = tk.StringVar(value="web")
        
        quality_presets = [
            ("Web (800k)", "web"),
            ("HD (1500k)", "hd"),
            ("Full HD (3000k)", "fullhd"),
            ("Niestandardowy", "custom")
        ]
        
        for text, value in quality_presets:
            tk.Radiobutton(preset_frame, text=text, variable=self.quality_preset_var, 
                          value=value, command=self.update_bitrate_preset).pack(side="left", padx=5)
        
        # Lista pobranych plików
        file_frame = tk.LabelFrame(main_frame, text="📂 Pobrane Pliki", padx=10, pady=10)
        file_frame.pack(fill="both", expand=True)
        
        # Frame z listboxem i scrollbarem
        listbox_frame = tk.Frame(file_frame)
        listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.file_listbox = tk.Listbox(listbox_frame)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox.bind("<Double-Button-1>", self.open_selected_file)
        
        # Info o pliku
        self.file_info_var = tk.StringVar(value="Wybierz plik aby zobaczyć informacje")
        tk.Label(file_frame, textvariable=self.file_info_var, fg="gray").pack(fill="x", padx=5)
        self.file_listbox.bind("<<ListboxSelect>>", self.show_file_info)
        
        # Przyciski zarządzania
        btn_frame = tk.Frame(file_frame)
        btn_frame.pack(fill="x", pady=5)
        
        tk.Button(btn_frame, text="📁 Otwórz folder", command=self.open_download_directory,
                 bg="#FF9800", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="📋 Kopiuj ścieżkę", command=self.copy_file_path,
                 bg="#9C27B0", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="▶️ Odtwórz", command=self.play_selected_file,
                 bg="#4CAF50", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="🗑️ Usuń", command=self.delete_selected_file,
                 bg="#F44336", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="🔄 Odśwież", command=self.refresh_file_list,
                 bg="#607D8B", fg="white").pack(side="left", padx=2)
        
        # Menu diagnostyki
        diagnostics_frame = tk.LabelFrame(main_frame, text="📊 Diagnostyka i Statystyki", padx=10, pady=10)
        diagnostics_frame.pack(fill="x", pady=(0, 10))
        
        diag_buttons = tk.Frame(diagnostics_frame)
        diag_buttons.pack(fill="x")
        
        tk.Button(diag_buttons, text="📈 Raport wydajności", command=self.show_performance_report,
                 bg="#3F51B5", fg="white").pack(side="left", padx=2)
        tk.Button(diag_buttons, text="🔍 Diagnostyka systemu", command=self.run_system_diagnostics,
                 bg="#673AB7", fg="white").pack(side="left", padx=2)
        tk.Button(diag_buttons, text="💾 Backup danych", command=self.create_backup,
                 bg="#795548", fg="white").pack(side="left", padx=2)
        tk.Button(diag_buttons, text="🧹 Czyszczenie", command=self.cleanup_system,
                 bg="#607D8B", fg="white").pack(side="left", padx=2)
        tk.Button(diag_buttons, text="💬 Statystyki czatów", command=self.show_chat_stats,
                 bg="#4CAF50", fg="white").pack(side="left", padx=2)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Gotowy - FFmpeg: " + ("✅ Dostępny" if self.ffmpeg_path else "❌ Niedostępny"), 
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Ładuj istniejące pliki
        self.refresh_file_list()
    
    def update_bitrate_preset(self):
        presets = {
            "web": "800",
            "hd": "1500", 
            "fullhd": "3000",
            "custom": self.bitrate_var.get()
        }
        preset = self.quality_preset_var.get()
        if preset != "custom":
            self.bitrate_var.set(presets[preset])
    
    def show_file_info(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = Path(self.downloaded_files[index])
            if file_path.exists():
                size = file_path.stat().st_size
                size_mb = size / (1024 * 1024)
                modified = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                self.file_info_var.set(f"Rozmiar: {size_mb:.1f} MB | Zmodyfikowany: {modified}")
            else:
                self.file_info_var.set("Plik nie istnieje")
    
    def test_download(self):
        url = self.test_url_var.get().strip()
        if url:
            threading.Thread(target=self.download_video, args=(url,), daemon=True).start()
    
    def add_to_queue(self):
        url = self.test_url_var.get().strip()
        if url:
            download_dir = Path(self.download_dir_var.get())
            success = download_manager.add_to_queue(url, download_dir)
            if success:
                self.update_status(f"➕ Dodano do kolejki: {url[:50]}...")
                self.test_url_var.set("")
            else:
                self.update_status(f"⚠️ URL już w kolejce lub pobrany: {url[:50]}...")
    
    def start_queue(self):
        download_manager.start_processing()
        self.update_status("▶️ Uruchomiono kolejkę pobierania")
    
    def pause_queue(self):
        download_manager.stop_processing()
        self.update_status("⏸️ Wstrzymano kolejkę pobierania")
    
    def retry_failed(self):
        download_manager.retry_failed()
        self.update_status("🔄 Ponawiam nieudane pobierania")
    
    def clear_queue(self):
        if messagebox.askyesno("Potwierdzenie", "Czy wyczyścić kolejkę pobierania?"):
            download_manager.clear_completed()
            download_manager.clear_failed()
            self.update_status("🗑️ Wyczyszczono kolejkę")
    
    def update_queue_status(self):
        """Aktualizuj status kolejki"""
        try:
            status = download_manager.get_queue_status()
            status_text = (f"Kolejka: {status['queue_size']} | "
                          f"Aktywne: {status['active_downloads']} | "
                          f"Ukończone: {status['completed']} | "
                          f"Błędy: {status['failed']}")
            self.queue_status_var.set(status_text)
        except Exception as e:
            self.queue_status_var.set(f"Błąd: {str(e)}")
        
        # Odśwież co 2 sekundy
        self.root.after(2000, self.update_queue_status)
    
    # Callbacki download managera
    def on_url_queued(self, url):
        self.root.after(0, lambda: self.update_status(f"📥 Dodano do kolejki: {url[:50]}..."))
    
    def on_download_start(self, url):
        self.root.after(0, lambda: self.update_status(f"🚀 Rozpoczynam pobieranie: {url[:50]}..."))
    
    def on_download_progress(self, url, progress, downloaded, total):
        if total > 0:
            self.root.after(0, lambda: self.progress_var.set(progress))
    
    def on_download_complete(self, url, file_path):
        self.root.after(0, lambda: self._handle_download_complete(url, file_path))
    
    def on_download_error(self, url, error):
        self.root.after(0, lambda: self.update_status(f"❌ Błąd pobierania: {error[:100]}"))
        self.root.after(0, lambda: self.progress_var.set(0))
    
    def _handle_download_complete(self, url, file_path):
        self.update_status(f"✅ Pobrano: {Path(file_path).name}")
        if file_path and str(file_path) not in self.downloaded_files:
            self.downloaded_files.append(str(file_path))
            self.refresh_file_list()
        self.progress_var.set(0)
        
        # Automatyczna konwersja dla plików MOV
        if (Path(file_path).suffix.lower() == ".mov" and 
            self.auto_convert_var.get() and 
            self.ffmpeg_path):
            self.update_status("🔄 Rozpoczynam automatyczną konwersję MOV → MP4")
            threading.Thread(target=self.convert_video, args=(str(file_path),), daemon=True).start()
    
    def start_monitoring(self):
        self.monitoring = True
        self.monitor_status.config(text="Status: Aktywny", fg="green")
        self.update_status("🚀 Rozpoczęto monitorowanie schowka - szukam linków wideo")
    
    def stop_monitoring(self):
        self.monitoring = False
        self.monitor_status.config(text="Status: Nieaktywny", fg="red")
        self.update_status("⏹️ Zatrzymano monitorowanie schowka")
    
    def toggle_chat_monitoring(self):
        """Przełącz monitoring czatów"""
        if self.chat_monitor.monitoring:
            self.chat_monitor.stop_monitoring()
            self.chat_monitor_status.config(text="Czaty: Nieaktywne", fg="red")
        else:
            self.chat_monitor.start_monitoring()
            self.chat_monitor_status.config(text="Czaty: Aktywne", fg="green")
            # Automatycznie uruchom kolejkę pobierania
            download_manager.start_processing()
    
    def on_chat_event(self, message, level="info"):
        """Obsłuż wydarzenia z chat monitora"""
        if level == "error":
            self.update_status(f"❌ Chat Monitor: {message}")
        else:
            self.update_status(f"💬 Chat Monitor: {message}")
    
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_dir_var.set(directory)
    
    def browse_video_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Pliki wideo", "*.mp4 *.mov *.avi *.mkv *.webm *.flv"),
                ("Wszystkie pliki", "*.*")
            ]
        )
        if file_path:
            self.video_path_var.set(file_path)
    
    def update_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_message = f"[{timestamp}] {message}"
        self.status_bar.config(text=status_message)
        print(status_message)
    
    def is_video_url(self, url):
        """Sprawdza czy URL prowadzi do pliku wideo"""
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        url_lower = url.lower()
        
        # Sprawdź rozszerzenie w URL
        for ext in video_extensions:
            if ext in url_lower:
                return True
        
        # Sprawdź popularne serwisy wideo
        video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'twitch.tv']
        for domain in video_domains:
            if domain in url_lower:
                return True
                
        return False
    
    def download_video(self, url):
        try:
            # Sprawdź czy to link do wideo
            if not self.is_video_url(url):
                self.update_status(f"❌ To nie wygląda na link do wideo: {url[:50]}...")
                return False
            
            self.update_status(f"📡 Sprawdzanie linku: {url[:50]}...")
            
            # Pobierz nagłówki
            try:
                headers = requests.head(url, allow_redirects=True, timeout=10)
                content_type = headers.get('content-type', '').lower()
                
                # Sprawdź Content-Type
                if not any(vid_type in content_type for vid_type in ['video/', 'application/octet-stream']):
                    # Spróbuj GET dla małego fragmentu
                    response = requests.get(url, stream=True, timeout=10)
                    content_type = response.headers.get('content-type', '').lower()
                    response.close()
                    
            except Exception:
                # Jeśli nagłówki nie działają, spróbuj pobrać
                pass
            
            # Określ nazwę pliku
            filename = self.get_filename_from_url(url)
            if not any(ext in filename.lower() for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm']):
                filename += '.mp4'  # Domyślne rozszerzenie
            
            # Tworzenie folderu pobierania
            download_dir = Path(self.download_dir_var.get())
            download_dir.mkdir(exist_ok=True, parents=True)
            file_path = download_dir / filename
            
            # Sprawdź czy plik już istnieje
            if file_path.exists():
                self.update_status(f"📄 Plik już istnieje: {filename}")
                if str(file_path) not in self.downloaded_files:
                    self.downloaded_files.append(str(file_path))
                    self.refresh_file_list()
                return True
            
            # Pobieranie pliku
            self.update_status(f"⬇️ Pobieranie wideo: {filename}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Aktualizuj progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.root.after(0, lambda p=progress: self.progress_var.set(p))
            
            self.update_status(f"✅ Pobrano wideo: {filename}")
            self.downloaded_files.append(str(file_path))
            self.refresh_file_list()
            
            # Reset progress bar
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Automatyczna konwersja dla plików MOV
            if (file_path.suffix.lower() == ".mov" and 
                self.auto_convert_var.get() and 
                self.ffmpeg_path):
                self.update_status("🔄 Rozpoczynam automatyczną konwersję MOV → MP4")
                threading.Thread(target=self.convert_video, args=(str(file_path),), daemon=True).start()
            
            return True
            
        except Exception as e:
            self.update_status(f"❌ Błąd pobierania: {str(e)}")
            self.root.after(0, lambda: self.progress_var.set(0))
            return False
    
    def get_filename_from_url(self, url):
        """Określa nazwę pliku na podstawie URL"""
        try:
            parsed = urlparse(url)
            filename = unquote(parsed.path.split("/")[-1])
            
            if filename and '.' in filename:
                return filename
            
            # Jeśli brak nazwy, użyj domyślnej
            timestamp = int(time.time())
            return f"video_{timestamp}"
            
        except Exception:
            timestamp = int(time.time())
            return f"video_{timestamp}"
    
    def refresh_file_list(self):
        """Odświeża listę plików"""
        self.file_listbox.delete(0, tk.END)
        
        download_dir = Path(self.download_dir_var.get())
        if download_dir.exists():
            video_files = []
            for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv', '*.webm', '*.flv']:
                video_files.extend(download_dir.glob(ext))
            
            # Sortuj według daty modyfikacji (najnowsze pierwsze)
            video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            self.downloaded_files = [str(f) for f in video_files]
            
            for file_path in video_files:
                self.file_listbox.insert(tk.END, file_path.name)
    
    def open_download_directory(self):
        download_dir = Path(self.download_dir_var.get())
        download_dir.mkdir(exist_ok=True, parents=True)
        
        try:
            if sys.platform == "win32":
                os.startfile(str(download_dir))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(download_dir)])
            else:
                subprocess.Popen(["xdg-open", str(download_dir)])
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się otworzyć folderu: {str(e)}")
    
    def open_selected_file(self, event):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = Path(self.downloaded_files[index])
            
            if file_path.exists():
                try:
                    if sys.platform == "win32":
                        os.startfile(str(file_path))
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", str(file_path)])
                    else:
                        subprocess.Popen(["xdg-open", str(file_path)])
                except Exception as e:
                    messagebox.showerror("Błąd", f"Nie udało się otworzyć pliku: {str(e)}")
            else:
                messagebox.showerror("Błąd", "Plik nie istnieje!")
    
    def play_selected_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz plik z listy")
            return
            
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = Path(self.downloaded_files[index])
            
            if file_path.exists():
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
                if file_path.suffix.lower() in video_extensions:
                    try:
                        if sys.platform == "win32":
                            os.startfile(str(file_path))
                        elif sys.platform == "darwin":
                            subprocess.Popen(["open", str(file_path)])
                        else:
                            subprocess.Popen(["xdg-open", str(file_path)])
                    except Exception as e:
                        messagebox.showerror("Błąd", f"Nie udało się odtworzyć pliku: {str(e)}")
                else:
                    messagebox.showinfo("Info", "To nie jest plik wideo")
            else:
                messagebox.showerror("Błąd", "Plik nie istnieje!")
    
    def copy_file_path(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz plik z listy")
            return
            
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = self.downloaded_files[index]
            try:
                pyperclip.copy(file_path)
                self.update_status(f"📋 Skopiowano ścieżkę: {Path(file_path).name}")
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie udało się skopiować: {str(e)}")
    
    def delete_selected_file(self):
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showinfo("Info", "Wybierz plik z listy")
            return
            
        index = selection[0]
        if index < len(self.downloaded_files):
            file_path = Path(self.downloaded_files[index])
            
            if messagebox.askyesno("Potwierdzenie", f"Czy na pewno chcesz usunąć plik:\n{file_path.name}?"):
                try:
                    if file_path.exists():
                        file_path.unlink()
                        self.update_status(f"🗑️ Usunięto plik: {file_path.name}")
                        self.refresh_file_list()
                    else:
                        messagebox.showerror("Błąd", "Plik nie istnieje!")
                except Exception as e:
                    messagebox.showerror("Błąd", f"Nie udało się usunąć pliku: {str(e)}")
    
    def init_automatic_backups(self):
        """Inicjalizuj automatyczne backupy"""
        try:
            from backup_system import BackupManager
            
            def run_auto_backup():
                backup_manager = BackupManager()
                if backup_manager.should_create_daily_backup():
                    backup_path = backup_manager.create_automatic_daily_backup()
                    if backup_path:
                        self.update_status("💾 Utworzono automatyczny backup")
            
            # Uruchom w tle
            threading.Thread(target=run_auto_backup, daemon=True).start()
            
        except Exception as e:
            print(f"⚠️ Błąd inicjalizacji automatycznych backupów: {e}")
    
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
    
    def convert_video(self, input_path=None):
        if not self.ffmpeg_path:
            messagebox.showerror("Błąd", "FFmpeg nie jest dostępny!\nZainstaluj FFmpeg aby używać konwersji.")
            return
            
        if not input_path:
            input_path = self.video_path_var.get()
        
        if not input_path:
            messagebox.showerror("Błąd", "Wybierz plik wideo do konwersji!")
            return
            
        input_path = Path(input_path)
        download_dir = Path(self.download_dir_var.get())
        
        if not input_path.exists():
            messagebox.showerror("Błąd", "Plik wejściowy nie istnieje!")
            return
        
        # Przygotuj nazwę pliku wyjściowego
        output_path = download_dir / f"{input_path.stem}_converted.mp4"
        
        # Jeśli plik już jest MP4, dodaj suffix
        if input_path.suffix.lower() == '.mp4':
            output_path = download_dir / f"{input_path.stem}_optimized.mp4"
        
        # Przygotuj polecenie ffmpeg
        bitrate = self.bitrate_var.get()
        
        cmd = [
            self.ffmpeg_path,
            "-i", str(input_path),
            "-c:v", "libx264",
            "-b:v", f"{bitrate}k",
            "-c:a", "aac",
            "-preset", "medium"
        ]
        
        # Dodaj optymalizację dla web jeśli włączona
        if self.optimize_web_var.get():
            cmd.extend(["-movflags", "+faststart"])
        
        cmd.extend(["-y", str(output_path)])  # Nadpisz istniejący plik
        
        # Uruchom konwersję w osobnym wątku
        threading.Thread(target=self.run_conversion, 
                        args=(cmd, input_path, output_path), daemon=True).start()
    
    def run_conversion(self, cmd, input_path, output_path):
        try:
            self.update_status(f"🔄 Rozpoczęto konwersję: {input_path.name} → {output_path.name}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            # Monitoruj postęp
            duration_pattern = re.compile(r"Duration: (\d+):(\d+):(\d+\.\d+)")
            time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")
            total_seconds = 0
            
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                
                # Wykryj całkowity czas trwania
                duration_match = duration_pattern.search(line)
                if duration_match and total_seconds == 0:
                    h, m, s = duration_match.groups()
                    total_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                
                # Wykryj aktualny postęp
                time_match = time_pattern.search(line)
                if time_match and total_seconds > 0:
                    h, m, s = time_match.groups()
                    current_seconds = int(h) * 3600 + int(m) * 60 + float(s)
                    progress = (current_seconds / total_seconds) * 100
                    
                    self.root.after(0, lambda p=progress: self.progress_var.set(min(p, 100)))
                    self.update_status(f"🔄 Konwersja... {progress:.1f}%")
            
            process.wait()
            
            if process.returncode == 0:
                self.update_status(f"✅ Konwersja zakończona: {output_path.name}")
                self.downloaded_files.append(str(output_path))
                self.root.after(0, self.refresh_file_list)
                self.root.after(0, lambda: messagebox.showinfo("Sukces", 
                    f"Wideo skonwertowane do:\n{output_path.name}"))
            else:
                self.update_status(f"❌ Błąd konwersji! Kod: {process.returncode}")
                self.root.after(0, lambda: messagebox.showerror("Błąd", "Konwersja nie powiodła się"))
        
        except Exception as e:
            self.update_status(f"❌ Błąd konwersji: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Błąd", 
                f"Nie udało się przekonwertować wideo: {str(e)}"))
        finally:
            # Reset progress bar
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def update_clipboard(self):
        try:
            if self.monitoring:
                current_clip = pyperclip.paste().strip()
                
                if (current_clip != self.last_clip and 
                    current_clip.startswith(('http://', 'https://')) and
                    self.is_video_url(current_clip)):
                    
                    self.update_status(f"🔗 Wykryto link do wideo: {current_clip[:50]}...")
                    download_dir = Path(self.download_dir_var.get())
                    success = download_manager.add_to_queue(current_clip, download_dir, priority=1)
                    if success:
                        self.update_status(f"➕ Automatycznie dodano do kolejki: {current_clip[:50]}...")
                    self.last_clip = current_clip
        
        except Exception as e:
            self.update_status(f"❌ Błąd monitorowania: {str(e)}")
        
        self.root.after(1000, self.update_clipboard)
    
    def show_performance_report(self):
        """Pokaż raport wydajności"""
        try:
            report = performance_monitor.get_performance_report()
            recommendations = performance_monitor.get_recommendations()
            
            # Utwórz okno raportu
            report_window = tk.Toplevel(self.root)
            report_window.title("📈 Raport Wydajności")
            report_window.geometry("800x600")
            
            # Tekst raportu
            text_area = scrolledtext.ScrolledText(report_window, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Formatuj raport
            report_text = "📊 RAPORT WYDAJNOŚCI VIDEO DOWNLOADER\n"
            report_text += "=" * 50 + "\n\n"
            
            # Informacje o sesji
            session = report['session_info']
            report_text += f"🕐 Czas działania: {session['uptime_hours']:.1f} godzin\n"
            report_text += f"🚀 Start sesji: {session['start_time']}\n\n"
            
            # Statystyki pobierania
            downloads = report['download_stats']
            report_text += "📥 STATYSTYKI POBIERANIA\n"
            report_text += "-" * 30 + "\n"
            report_text += f"Łącznie pobierań: {downloads['total_downloads']}\n"
            report_text += f"Udanych: {downloads['successful_downloads']}\n"
            report_text += f"Nieudanych: {downloads['failed_downloads']}\n"
            report_text += f"Współczynnik sukcesu: {downloads['success_rate_percent']:.1f}%\n"
            report_text += f"Łączne dane: {downloads['total_data_mb']:.1f} MB\n"
            report_text += f"Średnia prędkość: {downloads['average_speed_mbps']:.2f} MB/s\n\n"
            
            # Statystyki systemowe
            system = report['system_stats']
            report_text += "💻 ZASOBY SYSTEMOWE\n"
            report_text += "-" * 30 + "\n"
            report_text += f"CPU: {system['cpu_usage_percent']:.1f}%\n"
            report_text += f"Pamięć: {system['memory_usage_percent']:.1f}%\n"
            report_text += f"Dysk: {system['disk_usage_percent']:.1f}%\n\n"
            
            # Top domeny
            if report['top_domains']:
                report_text += "🌐 NAJPOPULARNIEJSZE DOMENY\n"
                report_text += "-" * 30 + "\n"
                for domain, count in report['top_domains'].items():
                    report_text += f"{domain}: {count} pobierań\n"
                report_text += "\n"
            
            # Typy plików
            if report['file_types']:
                report_text += "📁 TYPY PLIKÓW\n"
                report_text += "-" * 30 + "\n"
                for file_type, count in report['file_types'].items():
                    report_text += f"{file_type}: {count}\n"
                report_text += "\n"
            
            # Błędy
            if report['error_summary']:
                report_text += "❌ PODSUMOWANIE BŁĘDÓW\n"
                report_text += "-" * 30 + "\n"
                for error_type, count in report['error_summary'].items():
                    report_text += f"{error_type}: {count}\n"
                report_text += "\n"
            
            # Rekomendacje
            if recommendations:
                report_text += "💡 REKOMENDACJE\n"
                report_text += "-" * 30 + "\n"
                for rec in recommendations:
                    priority_icon = {"critical": "🚨", "high": "⚠️", "medium": "ℹ️"}.get(rec['priority'], "💡")
                    report_text += f"{priority_icon} {rec['message']}\n"
            
            text_area.insert(tk.END, report_text)
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można wygenerować raportu: {str(e)}")
    
    def run_system_diagnostics(self):
        """Uruchom diagnostykę systemu"""
        try:
            from system_diagnostics import run_comprehensive_check
            
            # Uruchom w osobnym wątku
            def run_diagnostics():
                self.update_status("🔍 Uruchamiam diagnostykę systemu...")
                success = run_comprehensive_check()
                result = "✅ System gotowy" if success else "⚠️ System wymaga konfiguracji"
                self.root.after(0, lambda: self.update_status(f"🔍 Diagnostyka zakończona: {result}"))
            
            threading.Thread(target=run_diagnostics, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można uruchomić diagnostyki: {str(e)}")
    
    def create_backup(self):
        """Utwórz backup systemu"""
        try:
            from backup_system import BackupManager
            
            def run_backup():
                self.update_status("💾 Tworzenie backupu...")
                backup_manager = BackupManager()
                code_backup = backup_manager.create_code_backup()
                data_backup = backup_manager.create_data_backup()
                
                if code_backup or data_backup:
                    self.root.after(0, lambda: self.update_status("✅ Backup utworzony pomyślnie"))
                    self.root.after(0, lambda: messagebox.showinfo("Sukces", "Backup został utworzony pomyślnie!"))
                else:
                    self.root.after(0, lambda: self.update_status("❌ Błąd tworzenia backupu"))
            
            threading.Thread(target=run_backup, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można utworzyć backupu: {str(e)}")
    
    def cleanup_system(self):
        """Wyczyść system z niepotrzebnych plików"""
        if messagebox.askyesno("Potwierdzenie", "Czy wyczyścić tymczasowe pliki i statystyki?"):
            try:
                # Wyczyść statystyki
                performance_monitor.reset_stats()
                
                # Wyczyść logi
                log_dir = Path.home() / ".video_downloader"
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        log_file.unlink()
                
                # Wyczyść tymczasowe pliki
                temp_dir = Path.home() / "Downloads" / "temp"
                if temp_dir.exists():
                    import shutil
                    shutil.rmtree(temp_dir)
                
                self.update_status("🧹 System wyczyszczony")
                messagebox.showinfo("Sukces", "System został wyczyszczony!")
                
            except Exception as e:
                messagebox.showerror("Błąd", f"Nie można wyczyścić systemu: {str(e)}")
    
    def show_chat_stats(self):
        """Pokaż statystyki monitorowania czatów"""
        try:
            stats = self.chat_monitor.get_stats()
            
            stats_window = tk.Toplevel(self.root)
            stats_window.title("💬 Statystyki Monitorowania Czatów")
            stats_window.geometry("600x400")
            
            text_area = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
            text_area.pack(fill="both", expand=True, padx=10, pady=10)
            
            stats_text = "💬 STATYSTYKI MONITOROWANIA CZATÓW\n"
            stats_text += "=" * 50 + "\n\n"
            
            stats_text += f"🟢 Status: {'Aktywny' if stats['monitoring'] else 'Nieaktywny'}\n"
            stats_text += f"🔗 Przetworzonych linków: {stats['processed_links']}\n"
            stats_text += f"📱 Plik historii: {stats['history_file']}\n\n"
            
            stats_text += "📱 MONITOROWANE APLIKACJE:\n"
            stats_text += "-" * 30 + "\n"
            for app_name, enabled in stats['monitored_apps'].items():
                status_icon = "✅" if enabled else "❌"
                stats_text += f"{status_icon} {app_name.capitalize()}: {'Włączone' if enabled else 'Wyłączone'}\n"
            
            stats_text += "\n📁 FOLDERY POBIERANIA:\n"
            stats_text += "-" * 30 + "\n"
            chat_videos = Path.home() / "Downloads" / "ChatVideos"
            chat_archives = Path.home() / "Downloads" / "ChatArchives"
            
            if chat_videos.exists():
                video_count = len(list(chat_videos.glob("*")))
                stats_text += f"🎬 Wideo z czatów: {video_count} plików\n"
            
            if chat_archives.exists():
                archive_count = len(list(chat_archives.glob("*")))
                stats_text += f"📦 Archiwa z czatów: {archive_count} plików\n"
            
            stats_text += "\n💡 INSTRUKCJE:\n"
            stats_text += "-" * 30 + "\n"
            stats_text += "• System automatycznie wykrywa linki w czatach\n"
            stats_text += "• Pliki wideo są pobierane do ~/Downloads/ChatVideos\n"
            stats_text += "• Archiwa ZIP są pobierane do ~/Downloads/ChatArchives\n"
            stats_text += "• Historia linków jest zapisywana aby unikać duplikatów\n"
            
            text_area.insert(tk.END, stats_text)
            text_area.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można pobrać statystyk: {str(e)}")
    
    def on_closing(self):
        if self.monitoring:
            self.stop_monitoring()
        
        # Zatrzymaj chat monitoring
        if hasattr(self, 'chat_monitor') and self.chat_monitor.monitoring:
            self.chat_monitor.stop_monitoring()
        
        # Zatrzymaj monitoring wydajności
        performance_monitor.stop_system_monitoring()
        
        self.root.destroy()

def console_mode():
    """Tryb konsolowy dla Replit"""
    print("🎬 VIDEO DOWNLOADER - TRYB KONSOLOWY")
    print("=" * 50)
    print("Dostępne komendy:")
    print("  monitor    - Uruchom monitorowanie schowka")
    print("  download   - Pobierz wideo z URL")
    print("  convert    - Konwertuj plik wideo")
    print("  list       - Pokaż pobrane pliki")
    print("  status     - Sprawdź status FFmpeg")
    print("  exit       - Zakończ aplikację")
    print("=" * 50)
    
    # Utworz fałszywy root dla aplikacji konsolowej
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Ukryj okno
    app = VideoDownloader(root)
    
    # Ustaw folder pobierania na bieżący katalog w Replit
    app.download_dir_var.set(os.getcwd() + "/downloads")
    os.makedirs(app.download_dir_var.get(), exist_ok=True)
    
    while True:
        try:
            command = input("\n💻 Komenda: ").strip().lower()
            
            if command == "exit":
                print("👋 Do widzenia!")
                break
                
            elif command == "monitor":
                if not app.monitoring:
                    app.start_monitoring()
                    print("🚀 Uruchomiono monitorowanie schowka")
                    print("📋 Skopiuj link do wideo do schowka aby go pobrać")
                    print("⏹️  Wpisz 'stop' aby zatrzymać lub 'exit' aby wyjść")
                    
                    while app.monitoring:
                        try:
                            stop_cmd = input().strip().lower()
                            if stop_cmd in ['stop', 'exit']:
                                app.stop_monitoring()
                                print("⏹️  Zatrzymano monitorowanie")
                                if stop_cmd == 'exit':
                                    return
                                break
                        except KeyboardInterrupt:
                            app.stop_monitoring()
                            print("\n⏹️  Zatrzymano monitorowanie")
                            break
                else:
                    print("⚠️  Monitorowanie już jest aktywne")
                    
            elif command == "download":
                url = input("🔗 Podaj URL wideo: ").strip()
                if url:
                    print("⬇️  Pobieranie...")
                    success = app.download_video(url)
                    if success:
                        print("✅ Pobieranie zakończone!")
                    else:
                        print("❌ Pobieranie nie powiodło się")
                        
            elif command == "convert":
                app.refresh_file_list()
                if not app.downloaded_files:
                    print("📂 Brak plików do konwersji")
                    continue
                    
                print("📁 Dostępne pliki:")
                for i, file_path in enumerate(app.downloaded_files):
                    filename = Path(file_path).name
                    print(f"  {i+1}. {filename}")
                
                try:
                    choice = int(input("🔢 Wybierz numer pliku: ")) - 1
                    if 0 <= choice < len(app.downloaded_files):
                        file_path = app.downloaded_files[choice]
                        print("🔄 Konwersja w toku...")
                        app.convert_video(file_path)
                        print("✅ Konwersja zakończona!")
                    else:
                        print("❌ Nieprawidłowy numer")
                except ValueError:
                    print("❌ Podaj prawidłowy numer")
                    
            elif command == "list":
                app.refresh_file_list()
                if app.downloaded_files:
                    print("📁 Pobrane pliki:")
                    for i, file_path in enumerate(app.downloaded_files):
                        file = Path(file_path)
                        if file.exists():
                            size = file.stat().st_size / (1024 * 1024)
                            print(f"  {i+1}. {file.name} ({size:.1f} MB)")
                        else:
                            print(f"  {i+1}. {file.name} (nie istnieje)")
                else:
                    print("📂 Brak pobranych plików")
                    
            elif command == "status":
                print(f"🔧 FFmpeg: {'✅ Dostępny' if app.ffmpeg_path else '❌ Niedostępny'}")
                print(f"📁 Folder pobierania: {app.download_dir_var.get()}")
                print(f"👁️  Monitorowanie: {'🟢 Aktywne' if app.monitoring else '🔴 Nieaktywne'}")
                print(f"📊 Pobrane pliki: {len(app.downloaded_files)}")
                
            elif command == "help":
                print("📚 Lista komend:")
                print("  monitor, download, convert, list, status, exit")
                
            else:
                print("❓ Nieznana komenda. Wpisz 'help' aby zobaczyć listę komend.")
                
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break
        except Exception as e:
            print(f"❌ Błąd: {str(e)}")

def main():
    # Sprawdź czy jesteśmy w Replit
    if "REPLIT" in os.environ:
        # Konfiguracja dla Replit
        os.environ.setdefault('DISPLAY', ':0')
        os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
        
        print("🌐 Wykryto środowisko Replit")
        print("🖥️  Uruchamianie w trybie konsolowym...")
        
        try:
            # Sprawdź czy GUI jest dostępne
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.destroy()
            
            # Jeśli GUI działa, zapytaj użytkownika
            choice = input("🎮 Wybierz tryb (g=GUI, c=Konsolowy): ").lower().strip()
            if choice.startswith('c'):
                console_mode()
            else:
                print("🖼️  Uruchamianie GUI...")
                root = tk.Tk()
                app = VideoDownloader(root)
                root.mainloop()
                
        except Exception as e:
            print(f"⚠️  GUI niedostępne ({str(e)}), przełączanie na tryb konsolowy")
            console_mode()
    else:
        # Lokalne uruchomienie z GUI
        root = tk.Tk()
        app = VideoDownloader(root)
        root.mainloop()

if __name__ == "__main__":
    main()
