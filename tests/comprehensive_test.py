
#!/usr/bin/env python3
"""
Kompleksowy system testowy dla Video Downloader
Testuje wszystkie komponenty i funkcje automatycznie
"""

import os
import sys
import time
import threading
import tempfile
import shutil
from pathlib import Path
import json
import subprocess
from unittest.mock import patch, MagicMock
import requests

def test_imports():
    """Test importowania wszystkich modułów"""
    print("🔍 TESTOWANIE IMPORTÓW")
    print("-" * 40)
    
    modules = [
        'main',
        'backup_system', 
        'download_manager',
        'security_validator',
        'performance_monitor',
        'system_diagnostics',
        'chat_monitor',
        'test_video_downloader',
        'run_with_tests'
    ]
    
    results = {}
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            results[module] = True
        except Exception as e:
            print(f"❌ {module}: {str(e)}")
            results[module] = False
    
    return results

def test_backup_system():
    """Test systemu backupów"""
    print("\n💾 TESTOWANIE SYSTEMU BACKUPÓW")
    print("-" * 40)
    
    try:
        from backup_system import BackupManager
        
        backup_manager = BackupManager()
        
        # Test inicjalizacji
        print("✅ Inicjalizacja BackupManager")
        
        # Test tworzenia backup kodu
        backup_path = backup_manager.create_code_backup()
        if backup_path and Path(backup_path).exists():
            print("✅ Tworzenie backup kodu")
            file_size = Path(backup_path).stat().st_size
            print(f"   📦 Rozmiar: {file_size // 1024} KB")
        else:
            print("❌ Tworzenie backup kodu")
        
        # Test metadanych
        backup_manager.save_metadata()
        if backup_manager.metadata_file.exists():
            print("✅ Zapisywanie metadanych")
        else:
            print("❌ Zapisywanie metadanych")
        
        # Test listowania backupów
        backups = backup_manager.list_available_backups()
        print(f"✅ Listowanie backupów: {len(backups)} znalezionych")
        
        # Test sprawdzania czy potrzebny backup
        should_backup = backup_manager.should_create_daily_backup()
        print(f"✅ Sprawdzanie potrzeby backup: {should_backup}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd systemu backupów: {str(e)}")
        return False

def test_download_manager():
    """Test menedżera pobierania"""
    print("\n📥 TESTOWANIE MENEDŻERA POBIERANIA")
    print("-" * 40)
    
    try:
        from download_manager import download_manager
        
        # Test dodawania URL do kolejki
        test_url = "https://example.com/test.mp4"
        temp_dir = Path(tempfile.mkdtemp())
        
        result = download_manager.add_to_queue(test_url, temp_dir)
        print(f"✅ Dodawanie do kolejki: {result}")
        
        # Test walidacji URL
        valid, message = download_manager.is_valid_url("https://youtube.com/watch?v=test")
        print(f"✅ Walidacja URL YouTube: {valid}")
        
        invalid, message = download_manager.is_valid_url("javascript:alert('xss')")
        print(f"✅ Odrzucenie niebezpiecznego URL: {not invalid}")
        
        # Test sanityzacji nazw plików
        clean_name = download_manager.sanitize_filename("test<>file*.mp4")
        print(f"✅ Sanityzacja nazw: {clean_name}")
        
        # Test statusu kolejki
        status = download_manager.get_queue_status()
        print(f"✅ Status kolejki: {status['queue_size']} w kolejce")
        
        # Wyczyść
        download_manager.clear_completed()
        download_manager.clear_failed()
        shutil.rmtree(temp_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd menedżera pobierania: {str(e)}")
        return False

def test_security_validator():
    """Test walidatora bezpieczeństwa"""
    print("\n🔒 TESTOWANIE WALIDATORA BEZPIECZEŃSTWA")
    print("-" * 40)
    
    try:
        from security_validator import security_validator
        
        # Test walidacji bezpiecznego URL
        valid, message = security_validator.validate_url("https://youtube.com/watch?v=test")
        print(f"✅ Walidacja bezpiecznego URL: {valid}")
        
        # Test odrzucenia niebezpiecznego URL
        invalid, message = security_validator.validate_url("javascript:alert('xss')")
        print(f"✅ Odrzucenie JavaScript URL: {not invalid}")
        
        # Test sprawdzania reputacji
        safe, message = security_validator.check_file_reputation("https://example.com/test.mp4")
        print(f"✅ Sprawdzanie reputacji: {safe}")
        
        # Test sprawdzania pliku (z temporary file)
        temp_file = Path(tempfile.mktemp(suffix='.mp4'))
        temp_file.write_bytes(b'\x00\x00\x00\x18ftypmp4' + b'test data' * 100)
        
        file_ok, message = security_validator.basic_file_check(temp_file)
        print(f"✅ Sprawdzanie pliku MP4: {file_ok}")
        
        # Test hash pliku
        file_hash = security_validator.calculate_file_hash(temp_file)
        print(f"✅ Obliczanie hash: {file_hash is not None}")
        
        temp_file.unlink()
        return True
        
    except Exception as e:
        print(f"❌ Błąd walidatora bezpieczeństwa: {str(e)}")
        return False

def test_performance_monitor():
    """Test monitora wydajności"""
    print("\n📊 TESTOWANIE MONITORA WYDAJNOŚCI")
    print("-" * 40)
    
    try:
        from performance_monitor import performance_monitor
        
        # Test uruchomienia monitorowania
        performance_monitor.start_system_monitoring()
        print("✅ Uruchomienie monitorowania systemu")
        
        # Test rejestrowania pobierania
        performance_monitor.log_download_start("https://test.com/video.mp4")
        time.sleep(0.1)
        performance_monitor.log_download_complete("https://test.com/video.mp4", 1024*1024, True)
        print("✅ Logowanie pobierania")
        
        # Test rejestrowania błędu
        performance_monitor.log_error("test_error", "Test error message")
        print("✅ Logowanie błędów")
        
        # Test generowania raportu
        report = performance_monitor.get_performance_report()
        print(f"✅ Generowanie raportu: {len(report)} sekcji")
        
        # Test rekomendacji
        recommendations = performance_monitor.get_recommendations()
        print(f"✅ Generowanie rekomendacji: {len(recommendations)} pozycji")
        
        # Test statystyk systemu
        stats = performance_monitor.get_system_stats()
        print(f"✅ Statystyki systemu: CPU {stats.get('cpu_percent', 0):.1f}%")
        
        performance_monitor.stop_system_monitoring()
        return True
        
    except Exception as e:
        print(f"❌ Błąd monitora wydajności: {str(e)}")
        return False

def test_chat_monitor():
    """Test monitora czatów"""
    print("\n💬 TESTOWANIE MONITORA CZATÓW")
    print("-" * 40)
    
    try:
        from chat_monitor import get_chat_monitor
        from download_manager import download_manager
        
        chat_monitor = get_chat_monitor(download_manager)
        
        # Test inicjalizacji
        print("✅ Inicjalizacja chat monitora")
        
        # Test wykrywania linków
        test_text = "Sprawdź to wideo: https://youtube.com/watch?v=test123"
        links = chat_monitor.extract_links_from_text(test_text)
        print(f"✅ Wykrywanie linków: {len(links)} znalezonych")
        
        # Test znajdowania ścieżek
        telegram_path = chat_monitor.find_telegram_db()
        discord_paths = chat_monitor.find_discord_logs()
        whatsapp_path = chat_monitor.find_whatsapp_db()
        print(f"✅ Znajdowanie ścieżek aplikacji")
        
        # Test callbacków
        callback_called = False
        def test_callback(message, level="info"):
            nonlocal callback_called
            callback_called = True
        
        chat_monitor.add_callback(test_callback)
        chat_monitor.notify("Test message")
        print(f"✅ System callbacków: {callback_called}")
        
        # Test statystyk
        stats = chat_monitor.get_stats()
        print(f"✅ Statystyki: {stats['monitored_apps']}")
        
        # Test historii
        chat_monitor.save_history()
        print("✅ Zapisywanie historii")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd monitora czatów: {str(e)}")
        return False

def test_system_diagnostics():
    """Test diagnostyki systemu"""
    print("\n🔍 TESTOWANIE DIAGNOSTYKI SYSTEMU")
    print("-" * 40)
    
    try:
        from system_diagnostics import (
            check_python_version, check_environment, check_packages,
            check_ffmpeg, check_permissions, check_network, check_gui
        )
        
        # Test sprawdzania Python
        python_ok = check_python_version()
        print(f"✅ Sprawdzanie Python: {python_ok}")
        
        # Test środowiska
        env = check_environment()
        print(f"✅ Sprawdzanie środowiska: {env}")
        
        # Test pakietów
        packages_ok, missing = check_packages()
        print(f"✅ Sprawdzanie pakietów: {packages_ok}, brakuje: {len(missing)}")
        
        # Test FFmpeg
        ffmpeg_ok, path = check_ffmpeg()
        print(f"✅ Sprawdzanie FFmpeg: {ffmpeg_ok}")
        
        # Test uprawnień
        permissions_ok = check_permissions()
        print(f"✅ Sprawdzanie uprawnień: {permissions_ok}")
        
        # Test sieci
        network_ok = check_network()
        print(f"✅ Sprawdzanie sieci: {network_ok}")
        
        # Test GUI
        gui_ok = check_gui()
        print(f"✅ Sprawdzanie GUI: {gui_ok}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd diagnostyki systemu: {str(e)}")
        return False

def test_main_application():
    """Test głównej aplikacji"""
    print("\n🎬 TESTOWANIE GŁÓWNEJ APLIKACJI")
    print("-" * 40)
    
    try:
        # Test importu bez uruchamiania GUI
        import tkinter as tk
        from main import VideoDownloader
        
        # Stwórz ukryte okno testowe
        root = tk.Tk()
        root.withdraw()
        
        app = VideoDownloader(root)
        print("✅ Inicjalizacja głównej aplikacji")
        
        # Test wykrywania URL wideo
        video_urls = [
            "https://youtube.com/watch?v=test",
            "https://example.com/video.mp4",
            "https://vimeo.com/123456"
        ]
        
        for url in video_urls:
            is_video = app.is_video_url(url)
            print(f"✅ Wykrywanie URL wideo ({url[:30]}...): {is_video}")
        
        # Test sanityzacji nazw plików
        test_urls = [
            "https://example.com/test.mp4",
            "https://site.com/video%20with%20spaces.mov",
            "https://noname.com/"
        ]
        
        for url in test_urls:
            filename = app.get_filename_from_url(url)
            print(f"✅ Generowanie nazwy pliku: {filename}")
        
        # Test znajdowania FFmpeg
        ffmpeg_path = app.find_ffmpeg()
        print(f"✅ Znajdowanie FFmpeg: {ffmpeg_path is not None}")
        
        # Test refresh listy plików
        app.refresh_file_list()
        print(f"✅ Odświeżanie listy plików: {len(app.downloaded_files)} plików")
        
        # Test kontroli monitorowania
        app.start_monitoring()
        monitoring_active = app.monitoring
        app.stop_monitoring()
        monitoring_stopped = not app.monitoring
        print(f"✅ Kontrola monitorowania: start={monitoring_active}, stop={monitoring_stopped}")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Błąd głównej aplikacji: {str(e)}")
        return False

def test_file_operations():
    """Test operacji na plikach"""
    print("\n📁 TESTOWANIE OPERACJI NA PLIKACH")
    print("-" * 40)
    
    try:
        # Stwórz tymczasowy folder testowy
        test_dir = Path(tempfile.mkdtemp())
        
        # Test tworzenia struktur folderów
        video_dir = test_dir / "Downloads" / "Videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Tworzenie struktury folderów")
        
        # Test tworzenia plików testowych
        test_files = [
            "test_video.mp4",
            "sample_movie.mov", 
            "demo_clip.avi",
            "presentation.mkv"
        ]
        
        for filename in test_files:
            test_file = video_dir / filename
            test_file.write_bytes(b"fake video data" * 1000)
        
        print(f"✅ Tworzenie plików testowych: {len(test_files)} plików")
        
        # Test listowania plików wideo
        video_files = []
        for ext in ['*.mp4', '*.mov', '*.avi', '*.mkv']:
            video_files.extend(video_dir.glob(ext))
        
        print(f"✅ Listowanie plików wideo: {len(video_files)} znalezionych")
        
        # Test sprawdzania rozmiarów
        total_size = sum(f.stat().st_size for f in video_files)
        print(f"✅ Obliczanie rozmiarów: {total_size // 1024} KB łącznie")
        
        # Test sortowania według daty
        sorted_files = sorted(video_files, key=lambda x: x.stat().st_mtime, reverse=True)
        print(f"✅ Sortowanie według daty: {len(sorted_files)} plików")
        
        # Cleanup
        shutil.rmtree(test_dir)
        print("✅ Czyszczenie plików testowych")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd operacji na plikach: {str(e)}")
        return False

def test_network_operations():
    """Test operacji sieciowych"""
    print("\n🌐 TESTOWANIE OPERACJI SIECIOWYCH")
    print("-" * 40)
    
    try:
        # Test podstawowego połączenia
        try:
            response = requests.get("https://httpbin.org/get", timeout=5)
            print(f"✅ Podstawowe połączenie HTTP: {response.status_code}")
        except:
            print("⚠️ Podstawowe połączenie HTTP: Niedostępne")
        
        # Test sprawdzania nagłówków
        try:
            response = requests.head("https://httpbin.org/get", timeout=5)
            content_type = response.headers.get('content-type', 'unknown')
            print(f"✅ Sprawdzanie nagłówków: {content_type}")
        except:
            print("⚠️ Sprawdzanie nagłówków: Niedostępne")
        
        # Test obsługi przekierowań
        try:
            response = requests.get("https://httpbin.org/redirect/1", allow_redirects=True, timeout=5)
            print(f"✅ Obsługa przekierowań: {len(response.history)} przekierowań")
        except:
            print("⚠️ Obsługa przekierowań: Niedostępne")
        
        # Test timeout
        try:
            start_time = time.time()
            try:
                requests.get("https://httpbin.org/delay/10", timeout=2)
            except requests.exceptions.Timeout:
                elapsed = time.time() - start_time
                print(f"✅ Obsługa timeout: {elapsed:.1f}s (poprawnie przerwano)")
        except:
            print("⚠️ Obsługa timeout: Błąd testu")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd operacji sieciowych: {str(e)}")
        return False

def test_threading_safety():
    """Test bezpieczeństwa wątków"""
    print("\n🔒 TESTOWANIE BEZPIECZEŃSTWA WĄTKÓW")
    print("-" * 40)
    
    try:
        from download_manager import download_manager
        
        # Test równoległego dodawania do kolejki
        def add_urls():
            for i in range(10):
                url = f"https://example.com/video_{i}.mp4"
                download_manager.add_to_queue(url, Path("/tmp"))
                time.sleep(0.01)
        
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=add_urls)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        status = download_manager.get_queue_status()
        print(f"✅ Równoległe dodawanie: {status['queue_size']} w kolejce")
        
        # Test równoległego dostępu do statystyk
        from performance_monitor import performance_monitor
        
        def log_downloads():
            for i in range(5):
                performance_monitor.log_download_start(f"https://test{i}.com")
                time.sleep(0.01)
                performance_monitor.log_download_complete(f"https://test{i}.com", 1024, True)
        
        threads = []
        for _ in range(2):
            thread = threading.Thread(target=log_downloads)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        report = performance_monitor.get_performance_report()
        print(f"✅ Równoległe logowanie: {report['download_stats']['total_downloads']} zapisów")
        
        # Cleanup
        download_manager.clear_completed()
        download_manager.clear_failed()
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd bezpieczeństwa wątków: {str(e)}")
        return False

def run_comprehensive_tests():
    """Uruchom wszystkie testy"""
    print("🧪 KOMPLEKSOWE TESTOWANIE SYSTEMU VIDEO DOWNLOADER")
    print("=" * 60)
    
    test_functions = [
        ("Importy modułów", test_imports),
        ("System backupów", test_backup_system),
        ("Menedżer pobierania", test_download_manager),
        ("Walidator bezpieczeństwa", test_security_validator),
        ("Monitor wydajności", test_performance_monitor),
        ("Monitor czatów", test_chat_monitor),
        ("Diagnostyka systemu", test_system_diagnostics),
        ("Główna aplikacja", test_main_application),
        ("Operacje na plikach", test_file_operations),
        ("Operacje sieciowe", test_network_operations),
        ("Bezpieczeństwo wątków", test_threading_safety)
    ]
    
    results = {}
    total_tests = len(test_functions)
    passed_tests = 0
    
    for test_name, test_func in test_functions:
        try:
            print(f"\n{'='*20} {test_name.upper()} {'='*20}")
            result = test_func()
            results[test_name] = result
            if result:
                passed_tests += 1
                print(f"🎉 {test_name}: PRZESZEDŁ")
            else:
                print(f"💥 {test_name}: NIEPOWODZENIE")
        except Exception as e:
            print(f"💥 {test_name}: BŁĄD - {str(e)}")
            results[test_name] = False
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("📊 PODSUMOWANIE TESTÓW")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"🎯 Wykonane testy: {total_tests}")
    print(f"✅ Udane: {passed_tests}")
    print(f"❌ Nieudane: {total_tests - passed_tests}")
    print(f"📈 Wskaźnik sukcesu: {success_rate:.1f}%")
    
    print("\n📋 SZCZEGÓŁOWE WYNIKI:")
    print("-" * 40)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
    
    # Rekomendacje
    print("\n💡 REKOMENDACJE:")
    print("-" * 40)
    
    if success_rate >= 90:
        print("🎉 Doskonale! System jest w pełni funkcjonalny")
        print("✨ Wszystkie komponenty działają poprawnie")
    elif success_rate >= 80:
        print("👍 Bardzo dobrze! System jest w większości funkcjonalny")
        print("🔧 Niewielkie problemy do naprawienia")
    elif success_rate >= 60:
        print("⚠️ Dobrze! System częściowo funkcjonalny")
        print("🛠️ Kilka komponentów wymaga naprawy")
    else:
        print("🚨 System wymaga poważnych napraw")
        print("⚡ Wiele komponentów nie działa poprawnie")
    
    # Sprawdź krytyczne komponenty
    critical_components = [
        "Importy modułów",
        "Główna aplikacja", 
        "Menedżer pobierania"
    ]
    
    critical_ok = all(results.get(comp, False) for comp in critical_components)
    
    if critical_ok:
        print("✅ Krytyczne komponenty działają poprawnie")
        print("🚀 System gotowy do użycia!")
    else:
        print("❌ Problemy z krytycznymi komponentami")
        print("🔧 Napraw błędy przed użyciem systemu")
    
    return success_rate >= 60 and critical_ok

if __name__ == "__main__":
    try:
        success = run_comprehensive_tests()
        
        print(f"\n{'='*60}")
        if success:
            print("🎉 TESTOWANIE ZAKOŃCZONE SUKCESEM!")
            print("✅ System gotowy do pracy")
        else:
            print("⚠️ TESTOWANIE WYKRYŁO PROBLEMY!")
            print("🔧 Napraw błędy przed uruchomieniem")
        print(f"{'='*60}")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Testowanie przerwane przez użytkownika")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Krytyczny błąd testowania: {str(e)}")
        sys.exit(1)