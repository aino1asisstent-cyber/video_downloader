#!/usr/bin/env python3
"""
System zarządzania subskrypcjami dla Video Downloader
Freemium model z limitami i funkcjami premium
"""

import json
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from analytics_service import analytics_service

class SubscriptionManager:
    def __init__(self):
        self.license_file = Path.home() / ".video_downloader" / "subscription.json"
        self.user_id = analytics_service.user_id  # Użyj tego samego ID co analytics
        
        # Limity dla wersji freemium
        self.freemium_limits = {
            'daily_downloads': 10,           # 10 pobrań dziennie
            'max_concurrent': 2,             # 2 równoległe pobierania
            'queue_size': 5,                 # 5 pozycji w kolejce
            'chat_monitoring': False,        # Premium feature
            'batch_download': False,         # Premium feature
            'auto_conversion': True,         # Podstawowa konwersja
            'quality_presets': ['web'],      # Tylko podstawowa jakość
            'download_speed': 'normal',      # Normalna prędkość
            'ads_enabled': True              # Reklamy w freemium
        }
        
        # Funkcje premium
        self.premium_features = {
            'unlimited_downloads': True,     # Nielimitowane pobieranie
            'max_concurrent': 5,             # 5 równoległych pobierań
            'queue_size': 20,                # 20 pozycji w kolejce
            'chat_monitoring': True,         # Monitoring czatów
            'batch_download': True,          # Pobieranie playlist
            'auto_conversion': True,         # Pełna automatyzacja
            'quality_presets': ['web', 'hd', 'fullhd', 'custom'],
            'download_speed': 'unlimited',   # Pełna prędkość
            'ads_enabled': False,            # Brak reklam
            'priority_support': True,        # Priorytetowe wsparcie
            'cloud_backup': True             # Backup w chmurze
        }
        
        self.daily_stats = {
            'downloads_today': 0,
            'last_reset_date': datetime.now().date().isoformat()
        }
        
        self.load_subscription()
        self.reset_daily_counter_if_needed()
    
    def load_subscription(self):
        """Wczytaj dane subskrypcji"""
        try:
            if self.license_file.exists():
                with open(self.license_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Sprawdź czy subskrypcja jest aktywna
                if data.get('subscription_active', False):
                    expiry_date = datetime.fromisoformat(data.get('expiry_date', '2000-01-01'))
                    if datetime.now() < expiry_date:
                        self.subscription_data = data
                        self.is_premium = True
                        print("✅ Premium subscription active")
                        analytics_service.track_event('premium_subscription_active')
                        return
            
        except Exception as e:
            print(f"❌ Error loading subscription: {e}")
        
        # Domyślnie freemium
        self.subscription_data = {
            'subscription_active': False,
            'tier': 'freemium',
            'expiry_date': None,
            'user_id': self.user_id,
            'created_at': datetime.now().isoformat()
        }
        self.is_premium = False
        print("🔓 Running in freemium mode")
        analytics_service.track_event('freemium_mode_active')
    
    def save_subscription(self):
        """Zapisz dane subskrypcji"""
        try:
            self.license_file.parent.mkdir(exist_ok=True)
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscription_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving subscription: {e}")
    
    def reset_daily_counter_if_needed(self):
        """Zresetuj licznik dzienny jeśli minął dzień"""
        today = datetime.now().date().isoformat()
        if self.daily_stats['last_reset_date'] != today:
            self.daily_stats['downloads_today'] = 0
            self.daily_stats['last_reset_date'] = today
            print("🔄 Daily download counter reset")
    
    def has_premium(self):
        """Sprawdź czy użytkownik ma premium"""
        return self.is_premium
    
    def get_limits(self):
        """Pobierz aktualne limity"""
        return self.premium_features if self.is_premium else self.freemium_limits
    
    def can_download(self):
        """Sprawdź czy użytkownik może pobrać kolejny plik"""
        self.reset_daily_counter_if_needed()
        
        if self.is_premium:
            return True
        
        limits = self.get_limits()
        return self.daily_stats['downloads_today'] < limits['daily_downloads']
    
    def record_download(self):
        """Zarejestruj pobranie"""
        self.reset_daily_counter_if_needed()
        self.daily_stats['downloads_today'] += 1
        
        # Track analytics
        analytics_service.track_event('download_recorded', {
            'is_premium': self.is_premium,
            'downloads_today': self.daily_stats['downloads_today'],
            'daily_limit': self.get_limits()['daily_downloads']
        })
        
        # Sprawdź czy osiągnięto limit freemium
        if not self.is_premium and not self.can_download():
            analytics_service.track_event('freemium_limit_reached')
    
    def get_downloads_remaining(self):
        """Pobierz liczbę pozostałych pobrań"""
        self.reset_daily_counter_if_needed()
        
        if self.is_premium:
            return "unlimited"
        
        limits = self.get_limits()
        remaining = limits['daily_downloads'] - self.daily_stats['downloads_today']
        return max(0, remaining)
    
    def activate_premium(self, days=30):
        """Aktywuj subskrypcję premium"""
        expiry_date = datetime.now() + timedelta(days=days)
        
        self.subscription_data.update({
            'subscription_active': True,
            'tier': 'premium',
            'expiry_date': expiry_date.isoformat(),
            'activated_at': datetime.now().isoformat(),
            'duration_days': days
        })
        
        self.is_premium = True
        self.save_subscription()
        
        print(f"🎉 Premium activated until {expiry_date.strftime('%Y-%m-%d')}")
        analytics_service.track_event('premium_activated', {
            'duration_days': days,
            'expiry_date': expiry_date.isoformat()
        })
    
    def deactivate_premium(self):
        """Dezaktywuj subskrypcję premium"""
        self.subscription_data.update({
            'subscription_active': False,
            'tier': 'freemium',
            'expiry_date': None
        })
        
        self.is_premium = False
        self.save_subscription()
        
        print("🔓 Premium deactivated")
        analytics_service.track_event('premium_deactivated')
    
    def get_subscription_info(self):
        """Pobierz informacje o subskrypcji"""
        info = {
            'is_premium': self.is_premium,
            'tier': self.subscription_data.get('tier', 'freemium'),
            'downloads_today': self.daily_stats['downloads_today'],
            'downloads_remaining': self.get_downloads_remaining(),
            'limits': self.get_limits()
        }
        
        if self.is_premium:
            expiry_date = datetime.fromisoformat(self.subscription_data['expiry_date'])
            info['expiry_date'] = expiry_date.strftime('%Y-%m-%d')
            info['days_remaining'] = (expiry_date - datetime.now()).days
        
        return info
    
    def show_upgrade_prompt(self):
        """Pokaż prompt zachęcający do upgrade'u"""
        if self.is_premium:
            return
        
        downloads_remaining = self.get_downloads_remaining()
        
        # Track interest
        analytics_service.track_premium_interest('limit_near')
        
        if downloads_remaining == 0:
            return "❌ Osiągnięto dzienny limit pobrań! Upgrade do Premium dla nielimitowanego dostępu."
        elif downloads_remaining <= 3:
            return f"⚠️ Zostało Ci tylko {downloads_remaining} pobrań dzisiaj. Rozważ upgrade do Premium!"
        
        return None

# Singleton instance
subscription_manager = SubscriptionManager()