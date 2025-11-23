
#!/usr/bin/env python3
"""
System monitorowania wydajności Video Downloader
- Metryki pobierania
- Statystyki użycia
- Optymalizacja wydajności
"""

import time
import threading
import psutil
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque

class PerformanceMonitor:
    def __init__(self):
        self.stats = {
            'downloads': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'total_size': 0,
                'total_time': 0,
                'average_speed': 0
            },
            'system': {
                'cpu_usage': deque(maxlen=60),  # Ostatnie 60 pomiarów
                'memory_usage': deque(maxlen=60),
                'disk_usage': deque(maxlen=60)
            },
            'errors': defaultdict(int),
            'urls_by_domain': defaultdict(int),
            'file_types': defaultdict(int)
        }
        
        self.monitoring = False
        self.start_time = time.time()
        self.data_file = Path.home() / ".video_downloader" / "performance.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Załaduj istniejące dane
        self.load_stats()
        
        # Uruchom monitoring systemu
        self.start_system_monitoring()
    
    def start_system_monitoring(self):
        """Uruchom monitoring zasobów systemowych"""
        self.monitoring = True
        threading.Thread(target=self._monitor_system, daemon=True).start()
    
    def stop_system_monitoring(self):
        """Zatrzymaj monitoring"""
        self.monitoring = False
        self.save_stats()
    
    def _monitor_system(self):
        """Monitoruj zasoby systemowe"""
        while self.monitoring:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.stats['system']['cpu_usage'].append({
                    'timestamp': time.time(),
                    'value': cpu_percent
                })
                
                # Pamięć
                memory = psutil.virtual_memory()
                self.stats['system']['memory_usage'].append({
                    'timestamp': time.time(),
                    'value': memory.percent
                })
                
                # Dysk
                disk = psutil.disk_usage('/')
                self.stats['system']['disk_usage'].append({
                    'timestamp': time.time(),
                    'value': disk.percent
                })
                
            except Exception as e:
                print(f"Błąd monitorowania systemu: {e}")
            
            time.sleep(10)  # Sprawdzaj co 10 sekund
    
    def record_download_start(self, url):
        """Zapisz rozpoczęcie pobierania"""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc
        self.stats['urls_by_domain'][domain] += 1
        
        return {
            'start_time': time.time(),
            'url': url,
            'domain': domain
        }
    
    def record_download_complete(self, download_info, file_path, file_size):
        """Zapisz ukończenie pobierania"""
        end_time = time.time()
        download_time = end_time - download_info['start_time']
        
        # Aktualizuj statystyki
        self.stats['downloads']['total'] += 1
        self.stats['downloads']['successful'] += 1
        self.stats['downloads']['total_size'] += file_size
        self.stats['downloads']['total_time'] += download_time
        
        # Oblicz średnią prędkość
        if download_time > 0:
            speed = file_size / download_time  # bytes per second
            # Aktualizuj średnią prędkość (moving average)
            current_avg = self.stats['downloads']['average_speed']
            total_downloads = self.stats['downloads']['successful']
            self.stats['downloads']['average_speed'] = (
                (current_avg * (total_downloads - 1) + speed) / total_downloads
            )
        
        # Typ pliku
        file_ext = Path(file_path).suffix.lower()
        self.stats['file_types'][file_ext] += 1
        
        print(f"📊 Pobieranie ukończone: {file_size//1024//1024}MB w {download_time:.1f}s "
              f"({(file_size/download_time/1024/1024):.1f} MB/s)")
    
    def record_download_error(self, download_info, error_message):
        """Zapisz błąd pobierania"""
        self.stats['downloads']['total'] += 1
        self.stats['downloads']['failed'] += 1
        
        # Kategoryzuj błędy
        error_type = self._categorize_error(error_message)
        self.stats['errors'][error_type] += 1
    
    def _categorize_error(self, error_message):
        """Kategoryzuj typ błędu"""
        error_lower = error_message.lower()
        
        if 'connection' in error_lower or 'network' in error_lower:
            return 'network_error'
        elif 'timeout' in error_lower:
            return 'timeout_error'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        elif 'disk' in error_lower or 'space' in error_lower:
            return 'disk_error'
        elif 'size' in error_lower or 'large' in error_lower:
            return 'size_error'
        else:
            return 'other_error'
    
    def get_performance_report(self):
        """Wygeneruj raport wydajności"""
        uptime = time.time() - self.start_time
        
        # Podstawowe statystyki
        downloads = self.stats['downloads']
        success_rate = (downloads['successful'] / max(downloads['total'], 1)) * 100
        avg_speed_mbps = downloads['average_speed'] / 1024 / 1024
        
        # Statystyki systemowe (ostatnie wartości)
        system = self.stats['system']
        current_cpu = system['cpu_usage'][-1]['value'] if system['cpu_usage'] else 0
        current_memory = system['memory_usage'][-1]['value'] if system['memory_usage'] else 0
        current_disk = system['disk_usage'][-1]['value'] if system['disk_usage'] else 0
        
        report = {
            'session_info': {
                'uptime_hours': uptime / 3600,
                'start_time': datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')
            },
            'download_stats': {
                'total_downloads': downloads['total'],
                'successful_downloads': downloads['successful'],
                'failed_downloads': downloads['failed'],
                'success_rate_percent': success_rate,
                'total_data_mb': downloads['total_size'] / 1024 / 1024,
                'average_speed_mbps': avg_speed_mbps
            },
            'system_stats': {
                'cpu_usage_percent': current_cpu,
                'memory_usage_percent': current_memory,
                'disk_usage_percent': current_disk
            },
            'top_domains': dict(sorted(self.stats['urls_by_domain'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]),
            'file_types': dict(self.stats['file_types']),
            'error_summary': dict(self.stats['errors'])
        }
        
        return report
    
    def get_recommendations(self):
        """Wygeneruj rekomendacje optymalizacji"""
        recommendations = []
        
        system = self.stats['system']
        downloads = self.stats['downloads']
        
        # Sprawdź CPU
        if system['cpu_usage']:
            avg_cpu = sum(item['value'] for item in system['cpu_usage']) / len(system['cpu_usage'])
            if avg_cpu > 80:
                recommendations.append({
                    'type': 'performance',
                    'priority': 'high',
                    'message': f'Wysokie użycie CPU ({avg_cpu:.1f}%). Rozważ zmniejszenie liczby równoległych pobierań.'
                })
        
        # Sprawdź pamięć
        if system['memory_usage']:
            avg_memory = sum(item['value'] for item in system['memory_usage']) / len(system['memory_usage'])
            if avg_memory > 85:
                recommendations.append({
                    'type': 'performance', 
                    'priority': 'high',
                    'message': f'Wysokie użycie pamięci ({avg_memory:.1f}%). Zamknij inne aplikacje lub zmniejsz liczbę równoległych pobierań.'
                })
        
        # Sprawdź dysk
        if system['disk_usage']:
            current_disk = system['disk_usage'][-1]['value']
            if current_disk > 90:
                recommendations.append({
                    'type': 'storage',
                    'priority': 'critical',
                    'message': f'Mało miejsca na dysku ({current_disk:.1f}%). Usuń stare pliki lub przenieś je w inne miejsce.'
                })
        
        # Sprawdź współczynnik sukcesu
        if downloads['total'] > 10:
            success_rate = (downloads['successful'] / downloads['total']) * 100
            if success_rate < 80:
                recommendations.append({
                    'type': 'reliability',
                    'priority': 'medium',
                    'message': f'Niski współczynnik sukcesu ({success_rate:.1f}%). Sprawdź połączenie internetowe lub jakość linków.'
                })
        
        # Sprawdź błędy sieciowe
        network_errors = self.stats['errors'].get('network_error', 0) + self.stats['errors'].get('timeout_error', 0)
        if network_errors > downloads['total'] * 0.3:
            recommendations.append({
                'type': 'network',
                'priority': 'medium', 
                'message': 'Dużo błędów sieciowych. Sprawdź stabilność połączenia internetowego.'
            })
        
        return recommendations
    
    def save_stats(self):
        """Zapisz statystyki do pliku"""
        try:
            # Konwertuj deque na listę dla JSON
            stats_copy = self.stats.copy()
            for key in stats_copy['system']:
                stats_copy['system'][key] = list(stats_copy['system'][key])
            
            with open(self.data_file, 'w') as f:
                json.dump(stats_copy, f, indent=2)
                
        except Exception as e:
            print(f"Nie można zapisać statystyk: {e}")
    
    def load_stats(self):
        """Załaduj statystyki z pliku"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    saved_stats = json.load(f)
                
                # Przywróć dane (zachowaj aktualne deque)
                if 'downloads' in saved_stats:
                    self.stats['downloads'].update(saved_stats['downloads'])
                
                if 'errors' in saved_stats:
                    self.stats['errors'].update(saved_stats['errors'])
                
                if 'urls_by_domain' in saved_stats:
                    self.stats['urls_by_domain'].update(saved_stats['urls_by_domain'])
                
                if 'file_types' in saved_stats:
                    self.stats['file_types'].update(saved_stats['file_types'])
                    
        except Exception as e:
            print(f"Nie można załadować statystyk: {e}")
    
    def reset_stats(self):
        """Resetuj wszystkie statystyki"""
        self.stats = {
            'downloads': {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'total_size': 0,
                'total_time': 0,
                'average_speed': 0
            },
            'system': {
                'cpu_usage': deque(maxlen=60),
                'memory_usage': deque(maxlen=60),
                'disk_usage': deque(maxlen=60)
            },
            'errors': defaultdict(int),
            'urls_by_domain': defaultdict(int),
            'file_types': defaultdict(int)
        }
        
        self.start_time = time.time()
        print("📊 Zresetowano statystyki wydajności")

# Singleton instance
performance_monitor = PerformanceMonitor()
