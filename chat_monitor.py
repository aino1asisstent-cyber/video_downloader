
#!/usr/bin/env python3
"""
System monitorowania czatów i automatycznego pobierania plików
- Monitoring popularnych aplikacji czatowych
- Automatyczne wykrywanie linków i plików ZIP
- Integracja z głównym systemem pobierania
"""

import os
import time
import re
import threading
import sqlite3
from pathlib import Path
from datetime import datetime
import requests
import zipfile
import tempfile
from urllib.parse import urlparse
import json

class ChatMonitor:
    def __init__(self, download_manager):
        self.download_manager = download_manager
        self.monitoring = False
        self.monitored_apps = {
            'telegram': {
                'enabled': True,
                'db_path': self.find_telegram_db(),
                'last_message_id': 0
            },
            'discord': {
                'enabled': True,
                'log_paths': self.find_discord_logs(),
                'last_check': datetime.now()
            },
            'whatsapp': {
                'enabled': True,
                'db_path': self.find_whatsapp_db(),
                'last_message_id': 0
            }
        }
        self.callbacks = []
        
        # Patterns do wykrywania linków
        self.url_patterns = [
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(?:zip|rar|7z|tar\.gz|mp4|mov|avi|mkv|webm|flv)',
            r'https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s<>"{}|\\^`\[\]]+',
            r'https?://(?:www\.)?vimeo\.com/[^\s<>"{}|\\^`\[\]]+',
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(mp4|mov|avi|mkv|webm|flv)',
            r'https?://[^\s<>"{}|\\^`\[\]]+\.(zip|rar|7z|tar\.gz)'
        ]
        
        # Historia przetworzonych linków
        self.processed_links = set()
        self.history_file = Path.home() / ".video_downloader" / "chat_history.json"
        self.load_history()
    
    def add_callback(self, callback):
        """Dodaj callback dla wydarzeń"""
        self.callbacks.append(callback)
    
    def notify(self, message, level="info"):
        """Powiadom wszystkie callbacki"""
        for callback in self.callbacks:
            try:
                callback(message, level)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def find_telegram_db(self):
        """Znajdź bazę danych Telegram"""
        possible_paths = [
            Path.home() / "AppData" / "Roaming" / "Telegram Desktop" / "tdata" / "user_data" / "media_cache" / "cache.db",
            Path.home() / ".local" / "share" / "TelegramDesktop" / "tdata" / "user_data" / "media_cache" / "cache.db",
            Path.home() / "Library" / "Application Support" / "Telegram Desktop" / "tdata" / "user_data" / "media_cache" / "cache.db"
        ]
        
        for path in possible_paths:
            if path.exists():
                return str(path)
        return None
    
    def find_discord_logs(self):
        """Znajdź logi Discord"""
        possible_paths = [
            Path.home() / "AppData" / "Roaming" / "discord" / "logs",
            Path.home() / ".config" / "discord" / "logs",
            Path.home() / "Library" / "Application Support" / "discord" / "logs"
        ]
        
        valid_paths = []
        for path in possible_paths:
            if path.exists():
                valid_paths.append(str(path))
        return valid_paths
    
    def find_whatsapp_db(self):
        """Znajdź bazę danych WhatsApp Web (przybliżone)"""
        # WhatsApp Web przechowuje dane w przeglądarce
        chrome_paths = [
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "databases",
            Path.home() / ".config" / "google-chrome" / "Default" / "databases",
            Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "databases"
        ]
        
        for path in chrome_paths:
            if path.exists():
                whatsapp_dbs = list(path.glob("*whatsapp*"))
                if whatsapp_dbs:
                    return str(whatsapp_dbs[0])
        return None
    
    def extract_links_from_text(self, text):
        """Wyodrębnij linki z tekstu"""
        links = []
        for pattern in self.url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    link = match[0] if match[0].startswith('http') else f"http://{match[0]}"
                else:
                    link = match if match.startswith('http') else f"http://{match}"
                
                if link not in self.processed_links:
                    links.append(link)
        return links
    
    def monitor_telegram(self):
        """Monitoruj Telegram"""
        db_path = self.monitored_apps['telegram']['db_path']
        if not db_path or not Path(db_path).exists():
            return []
        
        try:
            # Telegram używa szyfrowanej bazy danych, więc monitorujemy pliki tymczasowe
            telegram_temp = Path(tempfile.gettempdir())
            new_links = []
            
            for temp_file in telegram_temp.glob("*telegram*"):
                if temp_file.is_file() and temp_file.stat().st_mtime > time.time() - 60:
                    try:
                        content = temp_file.read_text(encoding='utf-8', errors='ignore')
                        links = self.extract_links_from_text(content)
                        new_links.extend(links)
                    except:
                        continue
            
            return new_links
            
        except Exception as e:
            self.notify(f"Błąd monitorowania Telegram: {e}", "error")
            return []
    
    def monitor_discord(self):
        """Monitoruj Discord"""
        log_paths = self.monitored_apps['discord']['log_paths']
        if not log_paths:
            return []
        
        new_links = []
        try:
            for log_dir in log_paths:
                log_path = Path(log_dir)
                if not log_path.exists():
                    continue
                
                # Szukaj najnowszych logów
                for log_file in log_path.glob("*.log"):
                    if log_file.stat().st_mtime > time.time() - 300:  # Ostatnie 5 minut
                        try:
                            content = log_file.read_text(encoding='utf-8', errors='ignore')
                            links = self.extract_links_from_text(content)
                            new_links.extend(links)
                        except:
                            continue
            
            return new_links
            
        except Exception as e:
            self.notify(f"Błąd monitorowania Discord: {e}", "error")
            return []
    
    def monitor_whatsapp(self):
        """Monitoruj WhatsApp Web"""
        # WhatsApp Web jest trudny do monitorowania bezpośrednio
        # Implementujemy podstawowe monitorowanie schowka dla linków WhatsApp
        new_links = []
        
        try:
            import pyperclip
            clipboard = pyperclip.paste()
            
            if "chat.whatsapp.com" in clipboard or "wa.me" in clipboard:
                links = self.extract_links_from_text(clipboard)
                new_links.extend(links)
                
        except Exception as e:
            self.notify(f"Błąd monitorowania WhatsApp: {e}", "error")
        
        return new_links
    
    def download_zip_file(self, url, download_dir):
        """Pobierz i rozpakuj plik ZIP"""
        try:
            self.notify(f"📦 Pobieranie ZIP: {url}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Zapisz tymczasowy plik ZIP
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                temp_zip_path = temp_file.name
            
            # Rozpakuj ZIP
            extract_dir = download_dir / f"extracted_{int(time.time())}"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Usuń tymczasowy plik
            os.unlink(temp_zip_path)
            
            self.notify(f"✅ Rozpakowano ZIP do: {extract_dir}")
            return True
            
        except Exception as e:
            self.notify(f"❌ Błąd pobierania ZIP: {e}", "error")
            return False
    
    def process_discovered_link(self, link, source="chat"):
        """Przetwórz wykryty link"""
        if link in self.processed_links:
            return
        
        self.processed_links.add(link)
        self.save_history()
        
        self.notify(f"🔗 Znaleziono link w {source}: {link[:50]}...")
        
        # Określ typ pliku
        link_lower = link.lower()
        
        if any(ext in link_lower for ext in ['.zip', '.rar', '.7z', '.tar.gz']):
            # Plik archiwum
            download_dir = Path.home() / "Downloads" / "ChatArchives"
            download_dir.mkdir(exist_ok=True)
            self.download_zip_file(link, download_dir)
            
        elif any(ext in link_lower for ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']):
            # Plik wideo
            download_dir = Path.home() / "Downloads" / "ChatVideos"
            download_dir.mkdir(exist_ok=True)
            success = self.download_manager.add_to_queue(link, download_dir, priority=2)
            if success:
                self.notify(f"➕ Dodano wideo do kolejki: {link[:50]}...")
            
        elif any(domain in link_lower for domain in ['youtube.com', 'youtu.be', 'vimeo.com']):
            # Serwis wideo
            download_dir = Path.home() / "Downloads" / "ChatVideos"
            download_dir.mkdir(exist_ok=True)
            success = self.download_manager.add_to_queue(link, download_dir, priority=2)
            if success:
                self.notify(f"➕ Dodano wideo z serwisu do kolejki: {link[:50]}...")
    
    def start_monitoring(self):
        """Uruchom monitoring czatów"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.notify("🚀 Uruchomiono monitoring czatów")
        
        # Uruchom wątki dla każdej aplikacji
        threading.Thread(target=self._monitoring_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Zatrzymaj monitoring czatów"""
        self.monitoring = False
        self.notify("⏹️ Zatrzymano monitoring czatów")
    
    def _monitoring_loop(self):
        """Główna pętla monitorowania"""
        while self.monitoring:
            try:
                all_links = []
                
                # Monitoruj każdą aplikację
                if self.monitored_apps['telegram']['enabled']:
                    telegram_links = self.monitor_telegram()
                    for link in telegram_links:
                        self.process_discovered_link(link, "Telegram")
                
                if self.monitored_apps['discord']['enabled']:
                    discord_links = self.monitor_discord()
                    for link in discord_links:
                        self.process_discovered_link(link, "Discord")
                
                if self.monitored_apps['whatsapp']['enabled']:
                    whatsapp_links = self.monitor_whatsapp()
                    for link in whatsapp_links:
                        self.process_discovered_link(link, "WhatsApp")
                
                # Monitoring schowka systemowego (dla wszystkich aplikacji)
                try:
                    import pyperclip
                    clipboard = pyperclip.paste().strip()
                    if clipboard.startswith(('http://', 'https://')):
                        clipboard_links = self.extract_links_from_text(clipboard)
                        for link in clipboard_links:
                            self.process_discovered_link(link, "Schowek")
                except:
                    pass
                
            except Exception as e:
                self.notify(f"❌ Błąd monitorowania: {e}", "error")
            
            time.sleep(5)  # Sprawdzaj co 5 sekund
    
    def load_history(self):
        """Wczytaj historię przetworzonych linków"""
        try:
            self.history_file.parent.mkdir(exist_ok=True)
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_links = set(data.get('processed_links', []))
        except Exception as e:
            print(f"Błąd wczytywania historii: {e}")
            self.processed_links = set()
    
    def save_history(self):
        """Zapisz historię przetworzonych linków"""
        try:
            data = {
                'processed_links': list(self.processed_links),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Błąd zapisywania historii: {e}")
    
    def get_stats(self):
        """Pobierz statystyki monitorowania"""
        return {
            'monitoring': self.monitoring,
            'processed_links': len(self.processed_links),
            'monitored_apps': {name: app['enabled'] for name, app in self.monitored_apps.items()},
            'history_file': str(self.history_file)
        }

# Singleton instance
chat_monitor = None

def get_chat_monitor(download_manager):
    """Pobierz instancję chat monitora"""
    global chat_monitor
    if chat_monitor is None:
        chat_monitor = ChatMonitor(download_manager)
    return chat_monitor
