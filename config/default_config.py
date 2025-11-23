#!/usr/bin/env python3
"""
Domyślna konfiguracja systemu Video Downloader
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
HOME_DIR = Path.home()

DEFAULT_CONFIG = {
    "directories": {
        "downloads": HOME_DIR / "Downloads",
        "videos": HOME_DIR / "Videos",
        "backups": HOME_DIR / ".video_downloader" / "backups",
        "temp": HOME_DIR / ".video_downloader" / "temp",
        "logs": HOME_DIR / ".video_downloader" / "logs",
    },
    
    "download": {
        "max_concurrent": 3,
        "max_file_size_mb": 500,
        "timeout_seconds": 300,
        "retry_attempts": 3,
        "retry_delay_seconds": 5,
        "chunk_size": 8192,
    },
    
    "monitoring": {
        "clipboard_interval_seconds": 1,
        "chat_scan_interval_seconds": 30,
        "enabled_chats": ["telegram", "discord", "whatsapp"],
        "auto_download": True,
    },
    
    "backup": {
        "enabled": True,
        "daily_backup_time": "02:00",
        "keep_daily_backups": 7,
        "keep_manual_backups": 30,
        "max_backup_size_mb": 100,
    },
    
    "security": {
        "blacklisted_domains": [
            "malicious.com",
            "phishing-site.net",
            "suspicious-downloads.org",
        ],
        "scan_downloads": True,
        "quarantine_suspicious": True,
        "max_url_length": 2048,
    },
    
    "performance": {
        "monitor_system": True,
        "log_interval_seconds": 60,
        "max_cpu_percent": 80,
        "max_memory_mb": 1024,
    },
    
    "video": {
        "supported_formats": [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv", ".m4v"],
        "default_output_format": "mp4",
        "ffmpeg_path": None,
        "quality_preset": "medium",
    },
    
    "gui": {
        "theme": "default",
        "window_size": "900x700",
        "show_notifications": True,
        "minimize_to_tray": False,
    },
    
    "logging": {
        "level": "INFO",
        "file_enabled": True,
        "console_enabled": True,
        "max_log_size_mb": 10,
        "backup_count": 5,
    }
}

def get_config():
    """Zwraca domyślną konfigurację"""
    return DEFAULT_CONFIG.copy()

def save_config(config, config_file=None):
    """Zapisuje konfigurację do pliku JSON"""
    import json
    
    if config_file is None:
        config_file = HOME_DIR / ".video_downloader" / "config.json"
    
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False, default=str)
    
    return config_file

def load_config(config_file=None):
    """Wczytuje konfigurację z pliku JSON"""
    import json
    
    if config_file is None:
        config_file = HOME_DIR / ".video_downloader" / "config.json"
    
    if not config_file.exists():
        return get_config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
        
        config = get_config()
        deep_update(config, user_config)
        return config
        
    except Exception as e:
        print(f"Błąd wczytywania konfiguracji: {e}")
        return get_config()

def deep_update(base_dict, update_dict):
    """Rekurencyjnie aktualizuje słownik"""
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict:
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict
