#!/usr/bin/env python3
"""
Bezpieczny system analityki użytkowników dla Video Downloader
Integracja z PostHog do śledzenia zachowań i optymalizacji
"""

import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

try:
    import posthog
    from dotenv import load_dotenv
    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False
    print("⚠️ PostHog nie zainstalowany - analytics będą zapisywane lokalnie")

load_dotenv()  # Wczytaj zmienne z .env

class AnalyticsService:
    def __init__(self):
        self.api_key = os.getenv('POSTHOG_API_KEY')
        self.host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
        self.enabled = os.getenv('ANALYTICS_ENABLED', 'true').lower() == 'true'
        self.app_version = os.getenv('APP_VERSION', '1.0.0')
        
        # Anonimowy identyfikator użytkownika
        self.user_id = self._get_anonymous_user_id()
        
        # Lokalne zapisywanie eventów (backup)
        self.local_events_file = Path.home() / ".video_downloader" / "analytics_events.json"
        self.local_events_file.parent.mkdir(exist_ok=True)
        
        # Inicjalizacja PostHog
        if POSTHOG_AVAILABLE and self.api_key and self.enabled:
            try:
                posthog.api_key = self.api_key
                posthog.host = self.host
                self.posthog_initialized = True
                print("✅ Analytics service initialized with PostHog")
            except Exception as e:
                print(f"❌ PostHog initialization failed: {e}")
                self.posthog_initialized = False
        else:
            self.posthog_initialized = False
            print("⚠️ Analytics running in local mode only")
    
    def _get_anonymous_user_id(self):
        """Generuj anonimowy identyfikator użytkownika"""
        try:
            # Spróbuj wczytać istniejący ID
            id_file = Path.home() / ".video_downloader" / "user_id.txt"
            if id_file.exists():
                return id_file.read_text().strip()
            
            # Generuj nowy anonimowy ID
            anonymous_id = hashlib.md5(str(uuid.getnode()).encode()).hexdigest()[:12]
            id_file.parent.mkdir(exist_ok=True)
            id_file.write_text(anonymous_id)
            return anonymous_id
            
        except Exception:
            return "anonymous_user"
    
    def _get_system_info(self):
        """Pobierz podstawowe informacje o systemie"""
        import platform
        return {
            'os': platform.system(),
            'os_version': platform.release(),
            'python_version': platform.python_version(),
            'architecture': platform.architecture()[0]
        }
    
    def _save_event_locally(self, event_data):
        """Zapisz event lokalnie (backup)"""
        try:
            events = []
            if self.local_events_file.exists():
                with open(self.local_events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
            
            events.append(event_data)
            
            # Ogranicz do ostatnich 1000 eventów
            if len(events) > 1000:
                events = events[-1000:]
            
            with open(self.local_events_file, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error saving event locally: {e}")
    
    def track_event(self, event_name, properties=None):
        """
        Śledź event użytkownika
        
        Args:
            event_name (str): Nazwa eventu
            properties (dict): Dodatkowe właściwości eventu
        """
        if not self.enabled:
            return
            
        event_data = {
            'event': event_name,
            'timestamp': datetime.now().isoformat(),
            'user_id': self.user_id,
            'app_version': self.app_version,
            'properties': properties or {},
            'system_info': self._get_system_info()
        }
        
        # 1. Zapisz lokalnie (zawsze)
        self._save_event_locally(event_data)
        
        # 2. Wyślij do PostHog (jeśli dostępne)
        if self.posthog_initialized:
            try:
                posthog.capture(
                    distinct_id=self.user_id,
                    event=event_name,
                    properties={
                        'timestamp': event_data['timestamp'],
                        'app_version': self.app_version,
                        **event_data['system_info'],
                        **(properties or {})
                    }
                )
                print(f"📊 Tracked: {event_name}")
            except Exception as e:
                print(f"❌ PostHog tracking failed: {e}")
        else:
            print(f"📊 Event saved locally: {event_name}")
    
    # Metody do konkretnych eventów
    def track_app_launch(self):
        """Śledź uruchomienie aplikacji"""
        self.track_event('app_launched')
    
    def track_download_start(self, url, file_type):
        """Śledź rozpoczęcie pobierania"""
        self.track_event('download_started', {
            'url_hash': hashlib.md5(url.encode()).hexdigest()[:8],  # Anonimowy hash
            'file_type': file_type,
            'domain': self._extract_domain(url)
        })
    
    def track_download_complete(self, url, file_size, download_time):
        """Śledź ukończenie pobierania"""
        self.track_event('download_completed', {
            'url_hash': hashlib.md5(url.encode()).hexdigest()[:8],
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'download_time_seconds': round(download_time, 2),
            'download_speed_mbps': round((file_size / download_time) / (1024 * 1024), 2) if download_time > 0 else 0
        })
    
    def track_download_error(self, url, error_type, error_message):
        """Śledź błąd pobierania"""
        self.track_event('download_error', {
            'url_hash': hashlib.md5(url.encode()).hexdigest()[:8],
            'error_type': error_type,
            'error_message': error_message[:100]  # Ogranicz długość
        })
    
    def track_conversion_start(self, input_format, output_format):
        """Śledź rozpoczęcie konwersji"""
        self.track_event('conversion_started', {
            'input_format': input_format,
            'output_format': output_format
        })
    
    def track_conversion_complete(self, input_format, output_format, conversion_time):
        """Śledź ukończenie konwersji"""
        self.track_event('conversion_completed', {
            'input_format': input_format,
            'output_format': output_format,
            'conversion_time_seconds': round(conversion_time, 2)
        })
    
    def track_conversion_error(self, input_format, output_format, error_message):
        """Śledź błąd konwersji"""
        self.track_event('conversion_error', {
            'input_format': input_format,
            'output_format': output_format,
            'error_message': error_message[:100]
        })
    
    def track_premium_interest(self, source):
        """Śledź zainteresowanie wersją premium"""
        self.track_event('premium_interest', {
            'source': source  # 'button_click', 'popup', etc.
        })
    
    def track_ui_interaction(self, element_name, action):
        """Śledź interakcje z UI"""
        self.track_event('ui_interaction', {
            'element': element_name,
            'action': action
        })
    
    def _extract_domain(self, url):
        """Wyodrębnij domenę z URL (anonimowo)"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Zwróć tylko domenę główną dla prywatności
            return '.'.join(domain.split('.')[-2:]) if '.' in domain else domain
        except:
            return 'unknown'
    
    def get_analytics_status(self):
        """Pobierz status systemu analytics"""
        return {
            'enabled': self.enabled,
            'posthog_initialized': self.posthog_initialized,
            'user_id': self.user_id,
            'local_events_count': self._get_local_events_count(),
            'app_version': self.app_version
        }
    
    def _get_local_events_count(self):
        """Pobierz liczbę eventów zapisanych lokalnie"""
        try:
            if self.local_events_file.exists():
                with open(self.local_events_file, 'r', encoding='utf-8') as f:
                    events = json.load(f)
                return len(events)
            return 0
        except:
            return 0
    
    def disable_analytics(self):
        """Wyłącz system analytics"""
        self.enabled = False
        print("🔇 Analytics disabled")
    
    def enable_analytics(self):
        """Włącz system analytics"""
        self.enabled = True
        print("🔊 Analytics enabled")

# Singleton instance
analytics_service = AnalyticsService()