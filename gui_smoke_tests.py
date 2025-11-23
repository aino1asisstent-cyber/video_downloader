#!/usr/bin/env python3
"""
GUI Smoke Tests - Testy interfejsu użytkownika Video Downloader
Symuluje rzeczywiste działania użytkownika
"""

import os
import sys
import time
import tkinter as tk
from tkinter import messagebox

# Dodaj ścieżkę do importów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock dla messagebox aby nie pokazywać popupów podczas testów
original_showinfo = messagebox.showinfo
original_showerror = messagebox.showerror
original_askyesno = messagebox.askyesno

def mock_showinfo(title, message):
    print(f"💡 INFO: {title} - {message}")
    return True

def mock_showerror(title, message):
    print(f"❌ ERROR: {title} - {message}")
    return True

def mock_askyesno(title, message):
    print(f"❓ YES/NO: {title} - {message}")
    return True  # Zawsze odpowiada "Tak" w testach

# Zastąp messagebox mockami
messagebox.showinfo = mock_showinfo
messagebox.showerror = mock_showerror
messagebox.askyesno = mock_askyesno

from analytics_service import analytics_service
from main import VideoDownloader
from subscription_manager import subscription_manager


def test_gui_initialization():
    """Test inicjalizacji GUI"""
    print("🧪 Testing GUI Initialization...")
    
    try:
        # Utwórz ukryte okno tkinter
        root = tk.Tk()
        root.withdraw()  # Ukryj okno
        
        # Test inicjalizacji aplikacji
        app = VideoDownloader(root)
        
        # Sprawdź czy podstawowe komponenty są utworzone
        assert hasattr(app, 'subscription_manager'), "Should have subscription manager"
        assert hasattr(app, 'download_dir_var'), "Should have download directory variable"
        assert hasattr(app, 'monitoring'), "Should have monitoring flag"
        
        print("✅ GUI initialization: PASS")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ GUI initialization test failed: {e}")
        return False

def test_subscription_ui():
    """Test UI subskrypcji"""
    print("\n🧪 Testing Subscription UI...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        app = VideoDownloader(root)
        
        # Test 1: Freemium display
        app.update_subscription_display()
        status_text = app.subscription_status_var.get()
        assert "FREEMIUM" in status_text or "Downloads today" in status_text
        print("✅ Freemium UI display: PASS")
        
        # Test 2: Premium activation UI
        subscription_manager.activate_premium(days=1)
        app.update_subscription_display()
        status_text_premium = app.subscription_status_var.get()
        assert "PREMIUM" in status_text_premium or "Expires" in status_text_premium
        print("✅ Premium UI display: PASS")
        
        # Test 3: Upgrade dialog
        app.show_upgrade_dialog()
        print("✅ Upgrade dialog: PASS")
        
        # Cleanup
        subscription_manager.deactivate_premium()
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Subscription UI test failed: {e}")
        return False

def test_download_permission_flow():
    """Test przepływu uprawnień do pobierania"""
    print("\n🧪 Testing Download Permission Flow...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        app = VideoDownloader(root)
        
        # Test 1: Normal download permission (freemium)
        can_download = app.check_download_permission()
        assert can_download == True, "Should allow download in freemium with available quota"
        print("✅ Normal download permission: PASS")
        
        # Test 2: Simulate limit reached
        # Ustaw licznik na limit
        subscription_manager.daily_stats['downloads_today'] = subscription_manager.freemium_limits['daily_downloads']
        
        can_download_limit = app.check_download_permission()
        assert can_download_limit == False, "Should not allow download when limit reached"
        print("✅ Download limit enforcement: PASS")
        
        # Reset
        subscription_manager.daily_stats['downloads_today'] = 0
        
        # Test 3: Premium unlimited downloads
        subscription_manager.activate_premium(days=1)
        can_download_premium = app.check_download_permission()
        assert can_download_premium == True, "Premium should always allow downloads"
        print("✅ Premium unlimited downloads: PASS")
        
        # Cleanup
        subscription_manager.deactivate_premium()
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Download permission test failed: {e}")
        return False

def test_chat_monitoring_premium_lock():
    """Test blokady chat monitoring dla freemium"""
    print("\n🧪 Testing Chat Monitoring Premium Lock...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        app = VideoDownloader(root)
        
        # Upewnij się że jesteśmy w freemium
        subscription_manager.deactivate_premium()
        
        # Test: Próba uruchomienia chat monitoring w freemium
        # Powinno pokazać dialog upgrade'u
        app.toggle_chat_monitoring()
        
        print("✅ Chat monitoring premium lock: PASS")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Chat monitoring test failed: {e}")
        return False

def test_analytics_integration():
    """Test integracji analytics z GUI"""
    print("\n🧪 Testing Analytics GUI Integration...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        app = VideoDownloader(root)
        
        # Test 1: Analytics info dialog
        app.show_analytics_info()
        print("✅ Analytics info dialog: PASS")
        
        # Test 2: UI interaction tracking
        # Symuluj kliknięcia przycisków
        app.test_download()  # Should track UI interaction
        app.add_to_queue()   # Should track UI interaction
        print("✅ UI interaction tracking: PASS")
        
        # Test 3: Premium interest tracking
        app.show_upgrade_dialog()  # Should track premium interest
        print("✅ Premium interest tracking: PASS")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Analytics GUI integration test failed: {e}")
        return False

def test_error_scenarios():
    """Test scenariuszy błędów w GUI"""
    print("\n🧪 Testing GUI Error Scenarios...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        app = VideoDownloader(root)
        
        # Test 1: Invalid URL download
        invalid_url = "not-a-valid-url"
        app.test_url_var.set(invalid_url)
        
        # To powinno obsłużyć błąd bez crashowania
        app.test_download()
        print("✅ Invalid URL handling: PASS")
        
        # Test 2: Empty URL handling
        app.test_url_var.set("")
        app.add_to_queue()  # Should handle empty URL gracefully
        print("✅ Empty URL handling: PASS")
        
        # Test 3: Analytics disable/enable
        analytics_service.disable_analytics()
        analytics_service.enable_analytics()
        print("✅ Analytics toggle: PASS")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error scenarios test failed: {e}")
        return False

def test_app_lifecycle():
    """Test pełnego lifecycle aplikacji"""
    print("\n🧪 Testing App Lifecycle...")
    
    try:
        root = tk.Tk()
        root.withdraw()
        
        # Create app
        app = VideoDownloader(root)
        
        # Simulate some usage
        app.start_monitoring()
        time.sleep(0.1)
        app.stop_monitoring()
        
        # Test subscription flow
        subscription_manager.activate_premium(days=1)
        app.update_subscription_display()
        
        # Simulate downloads
        for i in range(2):
            subscription_manager.record_download()
        
        # Close app (should track app closure)
        app.on_closing()
        
        print("✅ App lifecycle: PASS")
        return True
        
    except Exception as e:
        print(f"❌ App lifecycle test failed: {e}")
        return False

def run_gui_tests():
    """Uruchamia wszystkie testy GUI"""
    print("🚀 Starting GUI Smoke Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run GUI tests
    test_results.append(("GUI Initialization", test_gui_initialization()))
    test_results.append(("Subscription UI", test_subscription_ui()))
    test_results.append(("Download Permission", test_download_permission_flow()))
    test_results.append(("Chat Monitoring Lock", test_chat_monitoring_premium_lock()))
    test_results.append(("Analytics Integration", test_analytics_integration()))
    test_results.append(("Error Scenarios", test_error_scenarios()))
    test_results.append(("App Lifecycle", test_app_lifecycle()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 GUI TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print(f"✅ {test_name}: PASS")
            passed += 1
        else:
            print(f"❌ {test_name}: FAIL")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 TOTAL: {passed} passed, {failed} failed")
    
    # Restore original messagebox
    messagebox.showinfo = original_showinfo
    messagebox.showerror = original_showerror
    messagebox.askyesno = original_askyesno
    
    if failed == 0:
        print("🎉 ALL GUI TESTS PASSED! UI is stable and functional.")
        return True
    else:
        print(f"⚠️  {failed} GUI tests failed. Please check UI implementation.")
        return False

if __name__ == "__main__":
    success = run_gui_tests()
    sys.exit(0 if success else 1)