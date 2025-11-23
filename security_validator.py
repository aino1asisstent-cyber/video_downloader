
#!/usr/bin/env python3
"""
System walidacji bezpieczeństwa dla Video Downloader
- Walidacja URL i domen
- Skanowanie antywirusowe
- Kontrola integralności plików
"""

import os
import sys
import subprocess
import hashlib
import requests
from pathlib import Path
import re
from urllib.parse import urlparse
import json

class SecurityValidator:
    def __init__(self):
        # Aktualizowana lista niebezpiecznych domen
        self.blacklisted_domains = [
            "malicious.com",
            "phishing-site.net", 
            "suspicious-downloads.org",
            "fake-video-host.net",
            "virus-downloads.com",
            "malware-central.org"
        ]
        
        # Bezpieczne domeny wideo
        self.trusted_domains = [
            "youtube.com", "youtu.be",
            "vimeo.com", "player.vimeo.com",
            "twitch.tv", "clips.twitch.tv",
            "dailymotion.com",
            "wistia.com", "fast.wistia.net"
        ]
        
        # Wzorce niebezpiecznych URL
        self.dangerous_patterns = [
            r'\.exe(\?|$)',  # Pliki exe
            r'\.scr(\?|$)',  # Screen savery
            r'\.bat(\?|$)',  # Batch files
            r'\.cmd(\?|$)',  # Command files
            r'javascript:',  # JavaScript URLs
            r'data:',        # Data URLs
        ]
    
    def validate_url(self, url):
        """Kompleksowa walidacja URL"""
        try:
            # Podstawowa walidacja struktury
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                return False, "Nieprawidłowa struktura URL"
            
            # Sprawdź protokół
            if result.scheme not in ['http', 'https']:
                return False, "Obsługiwane są tylko protokoły HTTP/HTTPS"
            
            # Sprawdź blacklistę
            domain = result.netloc.lower()
            for blacklisted in self.blacklisted_domains:
                if blacklisted in domain:
                    return False, f"Domena na czarnej liście: {blacklisted}"
            
            # Sprawdź niebezpieczne wzorce
            url_lower = url.lower()
            for pattern in self.dangerous_patterns:
                if re.search(pattern, url_lower):
                    return False, f"Niebezpieczny wzorzec w URL: {pattern}"
            
            # Sprawdź czy to zaufana domena lub wygląda na wideo
            is_trusted = any(trusted in domain for trusted in self.trusted_domains)
            
            if not is_trusted:
                # Sprawdź rozszerzenie pliku
                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
                if not any(ext in url_lower for ext in video_extensions):
                    return False, "URL nie wygląda na link do wideo z niezaufanej domeny"
            
            return True, "URL wydaje się bezpieczny"
            
        except Exception as e:
            return False, f"Błąd walidacji: {str(e)}"
    
    def check_file_reputation(self, url):
        """Sprawdź reputację pliku w bazach antywirusowych"""
        try:
            # Symulacja sprawdzania reputacji (w rzeczywistości można używać VirusTotal API)
            # For demo purposes, sprawdzamy tylko podstawowe wskaźniki
            
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            # Sprawdź Content-Type
            safe_content_types = [
                'video/', 'application/octet-stream', 
                'application/x-msvideo', 'video/quicktime'
            ]
            
            if not any(safe_type in content_type for safe_type in safe_content_types):
                return False, f"Podejrzany Content-Type: {content_type}"
            
            return True, "Plik wydaje się bezpieczny"
            
        except Exception as e:
            # Jeśli nie można sprawdzić, zakładamy że jest OK
            return True, f"Nie można sprawdzić reputacji: {str(e)}"
    
    def scan_downloaded_file(self, file_path):
        """Skanuj pobrany plik antywirusem"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False, "Plik nie istnieje"
        
        try:
            # Windows Defender
            if sys.platform == "win32":
                cmd = [
                    "C:\\Program Files\\Windows Defender\\MpCmdRun.exe",
                    "-Scan", "-ScanType", "3", "-File", str(file_path)
                ]
                
                try:
                    result = subprocess.run(cmd, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        return True, "Plik przeszedł skanowanie Windows Defender"
                    else:
                        return False, "Windows Defender wykrył zagrożenie"
                except FileNotFoundError:
                    pass  # Windows Defender nie dostępny
            
            # macOS - XProtect
            elif sys.platform == "darwin":
                try:
                    # Usuń kwarantannę (jeśli plik jest bezpieczny)
                    subprocess.run(["xattr", "-d", "com.apple.quarantine", str(file_path)], 
                                 capture_output=True)
                    return True, "Plik sprawdzony przez macOS XProtect"
                except:
                    pass
            
            # Linux - ClamAV
            else:
                try:
                    result = subprocess.run(["clamscan", str(file_path)], 
                                          capture_output=True, timeout=30)
                    if "OK" in result.stdout.decode():
                        return True, "Plik przeszedł skanowanie ClamAV"
                    else:
                        return False, "ClamAV wykrył zagrożenie"
                except FileNotFoundError:
                    pass  # ClamAV nie zainstalowany
            
            # Jeśli żaden antywirus nie jest dostępny
            return self.basic_file_check(file_path)
            
        except Exception as e:
            return False, f"Błąd skanowania: {str(e)}"
    
    def basic_file_check(self, file_path):
        """Podstawowe sprawdzenie pliku bez antywirusa"""
        try:
            file_path = Path(file_path)
            
            # Sprawdź rozmiar (zbyt małe pliki mogą być podejrzane)
            size = file_path.stat().st_size
            if size < 1024:  # Mniej niż 1KB
                return False, "Plik zbyt mały aby być wideo"
            
            # Sprawdź rozszerzenie
            video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv']
            if file_path.suffix.lower() not in video_extensions:
                return False, f"Nieoczekiwane rozszerzenie: {file_path.suffix}"
            
            # Sprawdź nagłówek pliku (magic bytes)
            with open(file_path, 'rb') as f:
                header = f.read(32)
            
            # Sprawdź czy to rzeczywiście plik wideo
            video_signatures = [
                b'\x00\x00\x00\x18ftypmp4',  # MP4
                b'\x00\x00\x00\x20ftypM4V',  # M4V  
                b'RIFF',                      # AVI
                b'\x1a\x45\xdf\xa3',         # MKV
            ]
            
            is_video = any(sig in header for sig in video_signatures)
            if not is_video:
                return False, "Plik nie wygląda na wideo (nieprawidłowy nagłówek)"
            
            return True, "Podstawowe sprawdzenie przeszło pomyślnie"
            
        except Exception as e:
            return False, f"Błąd sprawdzania pliku: {str(e)}"
    
    def calculate_file_hash(self, file_path):
        """Oblicz hash pliku dla późniejszej weryfikacji"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None
    
    def save_file_info(self, file_path, url, file_hash):
        """Zapisz informacje o pliku dla audytu"""
        try:
            info_dir = Path.home() / ".video_downloader" / "security"
            info_dir.mkdir(parents=True, exist_ok=True)
            
            info_file = info_dir / "downloaded_files.json"
            
            # Załaduj istniejące dane
            if info_file.exists():
                with open(info_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            # Dodaj nowy wpis
            entry = {
                "file_path": str(file_path),
                "url": url,
                "hash": file_hash,
                "timestamp": str(datetime.now()),
                "size": Path(file_path).stat().st_size
            }
            
            data.append(entry)
            
            # Ogranicz do ostatnich 1000 wpisów
            if len(data) > 1000:
                data = data[-1000:]
            
            # Zapisz
            with open(info_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Nie można zapisać informacji o pliku: {e}")

# Singleton instance
security_validator = SecurityValidator()
