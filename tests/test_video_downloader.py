
import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import tkinter as tk
import sys
import time
import threading

# Import głównej aplikacji
try:
    from main import VideoDownloader
except ImportError:
    print("Błąd: Nie można zaimportować głównej aplikacji")
    sys.exit(1)

class TestVideoDownloader(unittest.TestCase):
    """Testy jednostkowe głównych funkcji"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()  # Ukryj okno podczas testów
        self.app = VideoDownloader(self.root)
        self.app.download_dir_var.set(self.temp_dir)
    
    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test inicjalizacji aplikacji"""
        self.assertFalse(self.app.monitoring)
        self.assertEqual(self.app.last_clip, "")
        self.assertEqual(self.app.downloaded_files, [])
        self.assertIsNotNone(self.app.root)
    
    def test_is_video_url(self):
        """Test wykrywania URL-i wideo"""
        # Pozytywne przypadki
        video_urls = [
            "https://example.com/video.mp4",
            "http://test.com/movie.mov",
            "https://youtube.com/watch?v=abc123",
            "https://youtu.be/abc123",
            "https://vimeo.com/123456"
        ]
        
        for url in video_urls:
            with self.subTest(url=url):
                self.assertTrue(self.app.is_video_url(url), f"Should detect video URL: {url}")
        
        # Negatywne przypadki
        non_video_urls = [
            "https://example.com/document.pdf",
            "https://test.com/image.jpg",
            "https://random.com/page.html"
        ]
        
        for url in non_video_urls:
            with self.subTest(url=url):
                self.assertFalse(self.app.is_video_url(url), f"Should not detect video URL: {url}")
    
    def test_get_filename_from_url(self):
        """Test wyodrębniania nazwy pliku z URL"""
        test_cases = [
            ("https://example.com/video.mp4", "video.mp4"),
            ("https://test.com/path/movie.mov", "movie.mov"),
            ("https://site.com/video%20with%20spaces.mp4", "video with spaces.mp4"),
            ("https://nofilename.com/", "video_")  # Sprawdź czy generuje nazwę
        ]
        
        for url, expected in test_cases:
            with self.subTest(url=url):
                result = self.app.get_filename_from_url(url)
                if expected.endswith("_"):
                    self.assertTrue(result.startswith("video_"))
                else:
                    self.assertEqual(result, expected)
    
    @patch('subprocess.run')
    def test_find_ffmpeg(self, mock_run):
        """Test znajdowania FFmpeg"""
        # Test sukcesu
        mock_run.return_value = MagicMock(returncode=0)
        result = self.app.find_ffmpeg()
        self.assertIsNotNone(result)
        
        # Test niepowodzenia
        mock_run.side_effect = Exception("Command not found")
        result = self.app.find_ffmpeg()
        self.assertIsNone(result)
    
    @patch('requests.head')
    @patch('requests.get')
    def test_download_video_success(self, mock_get, mock_head):
        """Test udanego pobierania wideo"""
        # Setup mocks
        mock_head.return_value = MagicMock(
            headers={'content-type': 'video/mp4'},
            status_code=200
        )
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content.return_value = [b'test video data'] * 10
        mock_get.return_value = mock_response
        
        # Test
        url = "https://example.com/test.mp4"
        result = self.app.download_video(url)
        
        # Assertions
        self.assertTrue(result)
        expected_file = Path(self.temp_dir) / "test.mp4"
        self.assertTrue(expected_file.exists())
    
    @patch('requests.head')
    def test_download_video_failure(self, mock_head):
        """Test niepowodzenia pobierania"""
        mock_head.side_effect = Exception("Network error")
        
        url = "https://example.com/test.mp4"
        result = self.app.download_video(url)
        
        self.assertFalse(result)
    
    def test_monitoring_controls(self):
        """Test kontroli monitorowania"""
        # Test start
        self.app.start_monitoring()
        self.assertTrue(self.app.monitoring)
        
        # Test stop
        self.app.stop_monitoring()
        self.assertFalse(self.app.monitoring)
    
    def test_file_list_management(self):
        """Test zarządzania listą plików"""
        # Utwórz testowe pliki
        test_files = ["video1.mp4", "video2.mov", "video3.avi"]
        for filename in test_files:
            test_file = Path(self.temp_dir) / filename
            test_file.write_text("test content")
        
        # Test odświeżania listy
        self.app.refresh_file_list()
        
        # Sprawdź czy pliki zostały dodane
        self.assertEqual(len(self.app.downloaded_files), len(test_files))
        
        # Sprawdź czy listbox został zaktualizowany
        self.assertEqual(self.app.file_listbox.size(), len(test_files))

class TestIntegration(unittest.TestCase):
    """Testy integracyjne"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = VideoDownloader(self.root)
        self.app.download_dir_var.set(self.temp_dir)
    
    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('pyperclip.paste')
    @patch('requests.head')
    @patch('requests.get')
    def test_clipboard_monitoring_workflow(self, mock_get, mock_head, mock_paste):
        """Test pełnego workflow monitorowania schowka"""
        # Setup
        mock_paste.return_value = "https://example.com/test.mp4"
        mock_head.return_value = MagicMock(headers={'content-type': 'video/mp4'})
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-length': '100'}
        mock_response.iter_content.return_value = [b'test'] * 5
        mock_get.return_value = mock_response
        
        # Start monitoring
        self.app.start_monitoring()
        
        # Trigger clipboard check
        self.app.update_clipboard()
        
        # Wait for download to complete
        time.sleep(0.1)
        
        # Verify
        self.assertTrue(any("test.mp4" in f for f in self.app.downloaded_files))

class TestPerformance(unittest.TestCase):
    """Testy wydajnościowe"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = VideoDownloader(self.root)
    
    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()
    
    @patch('pyperclip.paste')
    def test_clipboard_check_performance(self, mock_paste):
        """Test wydajności sprawdzania schowka"""
        mock_paste.return_value = "https://example.com/not-a-video.txt"
        
        start_time = time.time()
        for _ in range(100):
            try:
                self.app.update_clipboard()
            except:
                pass  # Ignoruj błędy w testach wydajnościowych
        
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 1.0, "100 clipboard checks should take less than 1 second")

class TestSecurity(unittest.TestCase):
    """Testy bezpieczeństwa"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = VideoDownloader(self.root)
        self.app.download_dir_var.set(self.temp_dir)
    
    def tearDown(self):
        if hasattr(self, 'root'):
            self.root.destroy()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_malicious_url_rejection(self):
        """Test odrzucania podejrzanych URL-i"""
        suspicious_urls = [
            "javascript:alert('xss')",
            "file:///etc/passwd",
            "ftp://malicious.com/virus.exe"
        ]
        
        for url in suspicious_urls:
            with self.subTest(url=url):
                result = self.app.is_video_url(url)
                self.assertFalse(result, f"Should reject suspicious URL: {url}")
    
    def test_filename_sanitization(self):
        """Test sanityzacji nazw plików"""
        dangerous_urls = [
            "https://example.com/../../../etc/passwd",
            "https://example.com/file%00.mp4",
            "https://example.com/con.mp4"  # Reserved name on Windows
        ]
        
        for url in dangerous_urls:
            with self.subTest(url=url):
                filename = self.app.get_filename_from_url(url)
                # Sprawdź czy nazwa nie zawiera niebezpiecznych znaków
                self.assertNotIn("..", filename)
                self.assertNotIn("\x00", filename)

def run_all_tests():
    """Uruchamia wszystkie testy i generuje raport"""
    print("🧪 URUCHAMIANIE TESTÓW VIDEO DOWNLOADER")
    print("=" * 50)
    
    # Konfiguruj środowisko testowe
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"
    
    # Utwórz suite testów
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Dodaj klasy testów
    test_classes = [
        TestVideoDownloader,
        TestIntegration,
        TestPerformance,
        TestSecurity
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        print(f"✅ Załadowano testy: {test_class.__name__}")
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    print("\n" + "=" * 50)
    print("🚀 WYKONYWANIE TESTÓW...")
    print("=" * 50)
    
    result = runner.run(suite)
    
    # Raport końcowy
    print("\n" + "=" * 50)
    print("📊 RAPORT KOŃCOWY")
    print("=" * 50)
    print(f"🎯 Wykonane testy: {result.testsRun}")
    print(f"✅ Udane: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Nieudane: {len(result.failures)}")
    print(f"🔥 Błędy: {len(result.errors)}")
    
    if result.failures:
        print("\n🚨 NIEUDANE TESTY:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 BŁĘDY TESTÓW:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n🎖️  WSKAŹNIK SUKCESU: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎉 WSZYSTKIE TESTY PRZESZŁY POMYŚLNIE!")
        print("✅ Aplikacja gotowa do uruchomienia")
    else:
        print("\n⚠️  NIEKTÓRE TESTY NIE POWIODŁY SIĘ")
        print("🔧 Sprawdź błędy przed uruchomieniem aplikacji")
    
    sys.exit(0 if success else 1)
