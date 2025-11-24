#!/usr/bin/env python3
"""
Zaawansowany system zarządzania pobieraniem
- Kolejka pobierania z priorytetami
- Równoległe pobieranie z limitem
- Rate limiting - ochrona przed spamem
- Detekcja duplikatów
- Walidacja bezpieczeństwa
"""

import hashlib
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests


class DownloadManager:
    def __init__(self, max_concurrent=3, max_file_size=500*1024*1024):
        self.queue = []
        self.completed = []
        self.failed = []
        self.active_downloads = 0
        self.max_concurrent = max_concurrent
        self.max_file_size = max_file_size  # 500MB default
        self.lock = threading.Lock()
        self.running = False
        self.callbacks = {}
        
        # Rate limiting
        self.download_history = deque(maxlen=100)  # Ostatnie 100 pobrań
        self.rate_limit_per_minute = 10  # Max 10 pobrań na minutę
        self.rate_limit_per_hour = 50    # Max 50 pobrań na godzinę
        
        # Blacklisted domains for security
        self.blacklisted_domains = [
            "malicious.com",
            "phishing-site.net", 
            "suspicious-downloads.org",
            "fake-video-host.net"
        ]
        
        # Video file extensions
        self.video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
    
    def check_rate_limit(self):
        """Sprawdź czy nie przekroczono limitów rate limiting"""
        current_time = time.time()
        
        # Sprawdź limit na minutę
        downloads_last_minute = [
            t for t in self.download_history 
            if current_time - t < 60
        ]
        
        if len(downloads_last_minute) >= self.rate_limit_per_minute:
            return False, f"Przekroczono limit {self.rate_limit_per_minute} pobrań na minutę"
        
        # Sprawdź limit na godzinę
        downloads_last_hour = [
            t for t in self.download_history 
            if current_time - t < 3600
        ]
        
        if len(downloads_last_hour) >= self.rate_limit_per_hour:
            return False, f"Przekroczono limit {self.rate_limit_per_hour} pobrań na godzinę"
        
        return True, "OK"
    
    def record_download_attempt(self):
        """Zapisz próbę pobrania do historii rate limiting"""
        self.download_history.append(time.time())
    
    def add_callback(self, event, callback):
        """Dodaj callback dla wydarzeń (start, progress, complete, error)"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def trigger_callback(self, event, *args, **kwargs):
        """Wywołaj wszystkie callbacki dla danego wydarzenia"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def is_valid_url(self, url):
        """Walidacja URL pod kątem bezpieczeństwa"""
        try:
            result = urlparse(url)
            
            # Sprawdź podstawową strukturę
            if not all([result.scheme, result.netloc]):
                return False, "Nieprawidłowa struktura URL"
            
            # Sprawdź czy to HTTP/HTTPS
            if result.scheme not in ['http', 'https']:
                return False, "Obsługiwane są tylko protokoły HTTP/HTTPS"
            
            # Sprawdź blacklistę domen
            for domain in self.blacklisted_domains:
                if domain in result.netloc.lower():
                    return False, f"Domena na czarnej liście: {domain}"
            
            # Sprawdź czy wygląda na plik wideo
            url_lower = url.lower()
            if not any(ext in url_lower for ext in self.video_extensions):
                # Sprawdź popularne serwisy wideo
                video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'twitch.tv']
                if not any(domain in url_lower for domain in video_domains):
                    return False, "URL nie wygląda na link do wideo"
            
            return True, "OK"
            
        except Exception as e:
            return False, f"Błąd walidacji: {str(e)}"
    
    def calculate_file_hash(self, file_path):
        """Oblicz hash pliku dla detekcji duplikatów"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return None
    
    def sanitize_filename(self, name):
        """Oczyść nazwę pliku z niebezpiecznych znaków"""
        # Usuń niebezpieczne znaki
        name = re.sub(r'[\\/*?:"<>|]', "", name)
        # Usuń wiodące/końcowe spacje i kropki
        name = name.strip('. ')
        # Ogranicz długość
        if len(name) > 100:
            name = name[:97] + "..."
        # Jeśli nazwa jest pusta, użyj domyślnej
        if not name:
            name = f"video_{int(time.time())}"
        return name
    
    def get_filename_from_url(self, url):
        """Określ nazwę pliku na podstawie URL"""
        try:
            parsed = urlparse(url)
            filename = parsed.path.split("/")[-1]
            
            if filename and '.' in filename:
                return self.sanitize_filename(filename)
            
            # Użyj domyślnej nazwy z timestamp
            timestamp = int(time.time())
            return f"video_{timestamp}.mp4"
            
        except Exception:
            timestamp = int(time.time())
            return f"video_{timestamp}.mp4"
    
    def check_file_size(self, url):
        """Sprawdź rozmiar pliku przed pobraniem"""
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            file_size = int(response.headers.get('content-length', 0))
            
            if file_size > self.max_file_size:
                size_mb = file_size // (1024 * 1024)
                max_mb = self.max_file_size // (1024 * 1024)
                return False, f"Plik zbyt duży ({size_mb}MB > {max_mb}MB)"
            
            return True, file_size
            
        except Exception:
            # Jeśli nie można sprawdzić rozmiaru, pozwól na pobieranie
            return True, 0
    
    def add_to_queue(self, url, download_dir, priority=0):
        """Dodaj URL do kolejki pobierania"""
        # Sprawdź rate limiting
        rate_ok, rate_message = self.check_rate_limit()
        if not rate_ok:
            self.trigger_callback('error', url, f"Rate limit: {rate_message}")
            return False
        
        # Walidacja URL
        is_valid, message = self.is_valid_url(url)
        if not is_valid:
            self.trigger_callback('error', url, f"Nieprawidłowy URL: {message}")
            return False
        
        with self.lock:
            # Sprawdź czy URL już jest w kolejce
            for item in self.queue:
                if item['url'] == url:
                    return False  # Już w kolejce
            
            # Sprawdź czy już został pobrany
            for item in self.completed:
                if item['url'] == url:
                    return False  # Już pobrany
            
            download_item = {
                'url': url,
                'download_dir': Path(download_dir),
                'priority': priority,
                'added_time': datetime.now(),
                'attempts': 0,
                'max_attempts': 3
            }
            
            # Dodaj z zachowaniem priorytetu
            self.queue.append(download_item)
            self.queue.sort(key=lambda x: x['priority'], reverse=True)
            
            # Zapisz próbę pobrania dla rate limiting
            self.record_download_attempt()
            
            self.trigger_callback('queued', url)
            return True
    
    def start_processing(self):
        """Uruchom przetwarzanie kolejki"""
        if self.running:
            return
        
        self.running = True
        threading.Thread(target=self._process_queue, daemon=True).start()
        print(f"📥 Uruchomiono menedżer pobierania (max {self.max_concurrent} równoległych)")
    
    def stop_processing(self):
        """Zatrzymaj przetwarzanie kolejki"""
        self.running = False
        print("⏹️ Zatrzymano menedżer pobierania")
    
    def _process_queue(self):
        """Główna pętla przetwarzania kolejki"""
        while self.running:
            with self.lock:
                if (self.active_downloads < self.max_concurrent and 
                    self.queue and 
                    self.running):
                    
                    item = self.queue.pop(0)
                    self.active_downloads += 1
                    
                    # Uruchom pobieranie w osobnym wątku
                    threading.Thread(
                        target=self._download_file_worker,
                        args=(item,),
                        daemon=True
                    ).start()
            
            time.sleep(0.5)  # Sprawdzaj co 0.5 sekundy
    
    def _download_file_worker(self, item):
        """Worker do pobierania pojedynczego pliku"""
        try:
            success = self._download_file(item)
            
            with self.lock:
                self.active_downloads -= 1
                
                if success:
                    self.completed.append(item)
                    self.trigger_callback('complete', item['url'], item.get('file_path'))
                else:
                    item['attempts'] += 1
                    if item['attempts'] < item['max_attempts']:
                        # Ponów próbę
                        self.queue.append(item)
                        print(f"🔄 Ponawiam próbę ({item['attempts']}/{item['max_attempts']}): {item['url']}")
                    else:
                        self.failed.append(item)
                        self.trigger_callback('error', item['url'], "Przekroczono maksymalną liczbę prób")
                        
        except Exception as e:
            with self.lock:
                self.active_downloads -= 1
                self.failed.append(item)
            self.trigger_callback('error', item['url'], str(e))
    
    def _download_file(self, item):
        """Pobierz pojedynczy plik"""
        url = item['url']
        download_dir = item['download_dir']
        
        try:
            self.trigger_callback('start', url)
            
            # Sprawdź rozmiar pliku
            size_ok, file_size = self.check_file_size(url)
            if not size_ok:
                self.trigger_callback('error', url, file_size)
                return False
            
            # Przygotuj ścieżkę pliku
            filename = self.get_filename_from_url(url)
            download_dir.mkdir(exist_ok=True, parents=True)
            file_path = download_dir / filename
            
            # Sprawdź duplikaty
            if file_path.exists():
                existing_size = file_path.stat().st_size
                if existing_size > 0:
                    print(f"📄 Plik już istnieje: {filename}")
                    item['file_path'] = str(file_path)
                    return True
            
            # Pobieranie
            print(f"⬇️ Pobieranie: {filename}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk and self.running:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Sprawdź limit rozmiaru podczas pobierania
                        if downloaded > self.max_file_size:
                            f.close()
                            file_path.unlink()  # Usuń niepełny plik
                            raise Exception(f"Plik przekroczył limit {self.max_file_size//1024//1024}MB")
                        
                        # Callback postępu
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.trigger_callback('progress', url, progress, downloaded, total_size)
            
            # Sprawdź integralność pobranego pliku
            if total_size > 0 and downloaded != total_size:
                file_path.unlink()
                raise Exception("Pobrano niepełny plik")
            
            item['file_path'] = str(file_path)
            print(f"✅ Pobrano: {filename} ({downloaded//1024//1024}MB)")
            return True
            
        except requests.exceptions.RequestException as e:
            error_messages = {
                requests.exceptions.ConnectionError: "Błąd połączenia",
                requests.exceptions.Timeout: "Przekroczono czas oczekiwania", 
                requests.exceptions.TooManyRedirects: "Zbyt wiele przekierowań",
                requests.exceptions.HTTPError: f"Błąd HTTP: {e.response.status_code if hasattr(e, 'response') else 'unknown'}"
            }
            
            error_msg = error_messages.get(type(e), f"Błąd sieci: {str(e)}")
            self.trigger_callback('error', url, error_msg)
            return False
            
        except Exception as e:
            self.trigger_callback('error', url, f"Nieoczekiwany błąd: {str(e)[:100]}")
            return False
    
    def get_queue_status(self):
        """Pobierz status kolejki"""
        with self.lock:
            return {
                'queue_size': len(self.queue),
                'active_downloads': self.active_downloads,
                'completed': len(self.completed),
                'failed': len(self.failed),
                'running': self.running
            }
    
    def get_rate_limit_status(self):
        """Pobierz status rate limiting"""
        current_time = time.time()
        
        downloads_last_minute = len([
            t for t in self.download_history 
            if current_time - t < 60
        ])
        
        downloads_last_hour = len([
            t for t in self.download_history 
            if current_time - t < 3600
        ])
        
        return {
            'last_minute': downloads_last_minute,
            'last_hour': downloads_last_hour,
            'limit_per_minute': self.rate_limit_per_minute,
            'limit_per_hour': self.rate_limit_per_hour,
            'total_history': len(self.download_history)
        }
    
    def clear_completed(self):
        """Wyczyść listę ukończonych pobierań"""
        with self.lock:
            self.completed.clear()
    
    def clear_failed(self):
        """Wyczyść listę nieudanych pobierań"""
        with self.lock:
            self.failed.clear()
    
    def retry_failed(self):
        """Ponów pobieranie nieudanych plików"""
        with self.lock:
            for item in self.failed[:]:
                item['attempts'] = 0
                self.queue.append(item)
                self.failed.remove(item)
            
            self.queue.sort(key=lambda x: x['priority'], reverse=True)
        
        print(f"🔄 Dodano {len(self.failed)} nieudanych pobierań z powrotem do kolejki")

# Singleton instance
download_manager = DownloadManager()
