
#!/usr/bin/env python3
"""
Skrypt uruchamiający testy przed główną aplikacją
Automatycznie sprawdza funkcjonalność przed uruchomieniem
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Sprawdza czy wszystkie wymagane pakiety są zainstalowane"""
    required_packages = ['requests', 'pyperclip']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - BRAKUJE")
    
    if missing_packages:
        print(f"\n🚨 Brakujące pakiety: {', '.join(missing_packages)}")
        print("💡 Zainstaluj je w zakładce Packages w Replit")
        return False
    
    return True

def check_environment():
    """Sprawdza środowisko uruchomieniowe"""
    print("\n🔍 SPRAWDZANIE ŚRODOWISKA")
    print("-" * 30)
    
    # Sprawdź Python
    python_version = sys.version_info
    print(f"🐍 Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Sprawdź czy jesteśmy w Replit
    if "REPLIT" in os.environ:
        print("🌐 Środowisko: Replit")
        # Ustaw DISPLAY dla GUI
        os.environ.setdefault('DISPLAY', ':0')
    else:
        print("💻 Środowisko: Lokalne")
    
    # Sprawdź dostęp do folderu home
    home_dir = Path.home()
    downloads_dir = home_dir / "Downloads"
    
    try:
        downloads_dir.mkdir(exist_ok=True)
        print(f"📁 Folder Downloads: {downloads_dir} - OK")
    except Exception as e:
        print(f"📁 Folder Downloads: BŁĄD - {e}")
        return False
    
    return True

def run_tests():
    """Uruchamia testy"""
    print("\n🧪 URUCHAMIANIE TESTÓW")
    print("-" * 30)
    
    try:
        # Import i uruchom testy
        from test_video_downloader import run_all_tests
        return run_all_tests()
    except ImportError:
        print("❌ Nie można zaimportować testów")
        print("💡 Upewnij się, że plik test_video_downloader.py istnieje")
        return False
    except Exception as e:
        print(f"❌ Błąd podczas testów: {e}")
        return False

def run_main_app():
    """Uruchamia główną aplikację"""
    print("\n🚀 URUCHAMIANIE GŁÓWNEJ APLIKACJI")
    print("-" * 40)
    
    try:
        # Import i uruchom aplikację
        from main import main
        print("✅ Uruchamianie Video Downloader...")
        main()
    except ImportError:
        print("❌ Nie można zaimportować głównej aplikacji")
        print("💡 Upewnij się, że plik main.py istnieje")
        return False
    except Exception as e:
        print(f"❌ Błąd podczas uruchamiania: {e}")
        return False

def main():
    """Główna funkcja"""
    print("🎬 VIDEO DOWNLOADER - SYSTEM STARTOWY")
    print("=" * 50)
    
    # Sprawdź zależności
    print("📦 SPRAWDZANIE ZALEŻNOŚCI")
    print("-" * 30)
    if not check_dependencies():
        print("\n❌ Błędy zależności - przerywanie")
        sys.exit(1)
    
    # Sprawdź środowisko
    if not check_environment():
        print("\n❌ Błędy środowiska - przerywanie")
        sys.exit(1)
    
    # Uruchom testy
    print("\n🔍 Czy uruchomić testy przed startem aplikacji? (y/n): ", end="")
    
    # W Replit automatycznie uruchom testy
    if "REPLIT" in os.environ:
        print("y (automatycznie w Replit)")
        run_tests_choice = True
    else:
        try:
            choice = input().lower().strip()
            run_tests_choice = choice in ['y', 'yes', 'tak', 't', '']
        except:
            run_tests_choice = True
    
    if run_tests_choice:
        tests_passed = run_tests()
        if not tests_passed:
            print("\n⚠️  TESTY NIE PRZESZŁY POMYŚLNIE")
            print("🤔 Czy mimo to uruchomić aplikację? (y/n): ", end="")
            
            if "REPLIT" in os.environ:
                print("n (automatycznie w Replit)")
                print("🛑 Aplikacja nie zostanie uruchomiona z powodu błędów testów")
                sys.exit(1)
            else:
                choice = input().lower().strip()
                if choice not in ['y', 'yes', 'tak', 't']:
                    print("🛑 Anulowano uruchomienie")
                    sys.exit(1)
    
    # Uruchom aplikację
    print("\n" + "=" * 50)
    run_main_app()

if __name__ == "__main__":
    main()
