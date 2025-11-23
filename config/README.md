# Konfiguracja Video Downloader

Ten katalog zawiera pliki konfiguracyjne dla systemu Video Downloader.

## Pliki

### `default_config.py`
Zawiera domyślną konfigurację systemu z następującymi sekcjami:

- **directories** - ścieżki do katalogów (pobrane pliki, backupy, logi)
- **download** - ustawienia pobierania (limity, timeouty, retry)
- **monitoring** - konfiguracja monitorowania (schowek, czaty)
- **backup** - ustawienia systemu backupów
- **security** - ustawienia bezpieczeństwa (czarna lista, skanowanie)
- **performance** - limity zasobów systemowych
- **video** - obsługiwane formaty i konwersja
- **gui** - ustawienia interfejsu graficznego
- **logging** - konfiguracja logowania

## Użycie

```python
from config.default_config import load_config, save_config

# Wczytaj konfigurację
config = load_config()

# Zmodyfikuj ustawienia
config['download']['max_concurrent'] = 5

# Zapisz konfigurację
save_config(config)
```

## Lokalizacja pliku użytkownika

Konfiguracja użytkownika jest przechowywana w:
- **Linux/Mac**: `~/.video_downloader/config.json`
- **Windows**: `C:\Users\Username\.video_downloader\config.json`
