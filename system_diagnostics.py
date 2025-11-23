
#!/usr/bin/env python3
"""
Narzędzia diagnostyczne dla Video Downloader
Sprawdza stan systemu i konfiguracji
"""

import os
import sys
import subprocess
import platform
import tkinter as tk
from pathlib import Path
import requests
import importlib

def check_python_version():
    """Sprawdź wersję Python"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  Zalecana wersja Python 3.8+")
        return False
    else:
        print("✅ Wersja Python OK")
        return True

def check_environment():
    """Sprawdź środowisko uruchomieniowe"""
    print(f"💻 System: {platform.system()} {platform.release()}")
    print(f"🏗️  Architektura: {platform.machine()}")
    
    if "REPLIT" in os.environ:
        print("🌐 Środowisko: Replit")
        print(f"📍 Repl ID: {os.environ.get('REPL_ID', 'Unknown')}")
        print(f"👤 Użytkownik: {os.environ.get('REPL_OWNER', 'Unknown')}")
        return "replit"
    else:
        print("🖥️  Środowisko: Lokalne")
        return "local"

def check_packages():
    """Sprawdź zainstalowane pakiety"""
    required_packages = {
        'requests': 'Pobieranie plików HTTP',
        'pyperclip': 'Monitorowanie schowka',
        'tkinter': 'Interfejs graficzny',
        'schedule': 'Automatyczne backupy (opcjonalne)'
    }
    
    missing = []
    
    for package, description in required_packages.items():
        try:
            if package == 'tkinter':
                import tkinter
            else:
                importlib.import_module(package)
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} - BRAKUJE")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_ffmpeg():
    """Sprawdź dostępność FFmpeg"""
    possible_paths = [
        "ffmpeg",
        "ffmpeg.exe", 
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg"
    ]
    
    for path in possible_paths:
        try:
            result = subprocess.run([path, "-version"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  timeout=5)
            if result.returncode == 0:
                output = result.stdout.decode()
                version_line = output.split('\n')[0]
                print(f"✅ FFmpeg: {version_line}")
                return True, path
        except Exception:
            continue
    
    print("❌ FFmpeg: Niedostępny")
    print("💡 Instalacja FFmpeg:")
    print("   - Replit: Automatycznie dostępny")
    print("   - Linux: sudo apt install ffmpeg") 
    print("   - Mac: brew install ffmpeg")
    print("   - Windows: https://www.gyan.dev/ffmpeg/builds/")
    
    return False, None

def check_permissions():
    """Sprawdź uprawnienia do zapisu"""
    test_dirs = [
        Path.home() / "Downloads",
        Path.home() / "Videos", 
        Path.cwd() / "downloads",
        Path.cwd() / "backups"
    ]
    
    permissions_ok = True
    
    for test_dir in test_dirs:
        try:
            test_dir.mkdir(exist_ok=True, parents=True)
            test_file = test_dir / "test_write.tmp"
            
            with open(test_file, 'w') as f:
                f.write("test")
            
            test_file.unlink()
            print(f"✅ Uprawnienia zapisu: {test_dir}")
            
        except Exception as e:
            print(f"❌ Brak uprawnień: {test_dir} - {str(e)}")
            permissions_ok = False
    
    return permissions_ok

def check_network():
    """Sprawdź połączenie sieciowe"""
    test_urls = [
        "https://httpbin.org/get",
        "https://example.com",
        "https://www.google.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Połączenie sieciowe: OK ({url})")
                return True
        except Exception as e:
            print(f"⚠️  Błąd połączenia z {url}: {str(e)}")
    
    print("❌ Brak połączenia sieciowego")
    return False

def check_gui():
    """Sprawdź dostępność GUI"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        print("✅ GUI (Tkinter): Dostępne")
        return True
    except Exception as e:
        print(f"❌ GUI (Tkinter): Niedostępne - {str(e)}")
        print("💡 W Replit GUI może być ograniczone")
        return False

def run_comprehensive_check():
    """Uruchom kompletną diagnostykę"""
    print("🔍 DIAGNOSTYKA SYSTEMU VIDEO DOWNLOADER")
    print("=" * 50)
    
    checks = []
    
    print("\n📋 SPRAWDZANIE PODSTAWOWYCH KOMPONENTÓW")
    print("-" * 40)
    checks.append(("Python", check_python_version()))
    
    env = check_environment()
    checks.append(("Środowisko", True))
    
    packages_ok, missing = check_packages()
    checks.append(("Pakiety", packages_ok))
    
    ffmpeg_ok, ffmpeg_path = check_ffmpeg()
    checks.append(("FFmpeg", ffmpeg_ok))
    
    print("\n🔒 SPRAWDZANIE UPRAWNIEŃ I DOSTĘPU")
    print("-" * 40)
    checks.append(("Uprawnienia", check_permissions()))
    checks.append(("Sieć", check_network()))
    checks.append(("GUI", check_gui()))
    
    print("\n📊 PODSUMOWANIE DIAGNOSTYKI")
    print("=" * 50)
    
    total_checks = len(checks)
    passed_checks = sum(1 for name, result in checks if result)
    
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:15} {status}")
    
    success_rate = (passed_checks / total_checks) * 100
    print(f"\n🎯 Wynik: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 System gotowy do pracy!")
    elif success_rate >= 60:
        print("⚠️  System częściowo gotowy - niektóre funkcje mogą nie działać")
    else:
        print("🚨 System wymaga konfiguracji - wiele funkcji nie będzie działać")
    
    # Rekomendacje
    print(f"\n💡 REKOMENDACJE DLA {env.upper()}")
    print("-" * 40)
    
    if env == "replit":
        if not packages_ok:
            print("📦 Zainstaluj brakujące pakiety w zakładce Packages")
        if not ffmpeg_ok:
            print("🔧 FFmpeg powinien być automatycznie dostępny w Replit")
        print("🖥️  Użyj trybu konsolowego jeśli GUI nie działa")
        print("💾 Pliki będą zapisywane w folderze ./downloads")
    else:
        if not packages_ok:
            print(f"📦 Zainstaluj brakujące pakiety: pip install {' '.join(missing)}")
        if not ffmpeg_ok:
            print("🔧 Zainstaluj FFmpeg dla konwersji wideo")
        print("🖥️  GUI powinno działać normalnie")
        print("💾 Pliki będą zapisywane w folderze ~/Downloads/Videos")
    
    return success_rate >= 60

if __name__ == "__main__":
    try:
        run_comprehensive_check()
    except KeyboardInterrupt:
        print("\n\n👋 Diagnostyka przerwana przez użytkownika")
    except Exception as e:
        print(f"\n\n❌ Błąd podczas diagnostyki: {e}")
