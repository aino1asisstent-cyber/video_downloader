# 🎬 Video Downloader & Converter

**Zaawansowany system pobierania i konwersji wideo z automatycznym monitorowaniem czatów i schowka.**

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-beta-yellow)

## ✨ Funkcje

### 🔽 Pobieranie Wideo
- **Automatyczne wykrywanie** linków wideo w schowku
- **Wsparcie dla popularnych platform**: YouTube, Vimeo, i innych
- **Kolejkowanie pobierania** z priorytetami
- **Równoległe pobieranie** (do 3 jednocześnie)
- **System retry** dla nieudanych pobrań
- **Walidacja bezpieczeństwa** URL-i i plików

### 💬 Monitoring Czatów
- **Automatyczne skanowanie** czatów: Telegram, Discord, WhatsApp
- **Wykrywanie linków** do wideo i archiwów ZIP
- **Automatyczne pobieranie** znalezionych plików
- **Historia przetworzonych** linków

### 🔄 Konwersja Wideo
- Konwersja między formatami (MOV → MP4, itp.)
- Obsługa FFmpeg
- Zachowanie jakości wideo

### 💾 System Backupów
- **Automatyczne backupy** codzienne
- **Backupy manualne** na żądanie
- **Przechowywanie metadanych** (data, rozmiar, hash)
- **Rotacja backupów** (7 dni dziennych, 30 dni manualnych)

### 🔒 Bezpieczeństwo
- **Czarna lista** niebezpiecznych domen
- **Skanowanie plików** po pobraniu
- **Walidacja URL-i** przed pobieraniem
- **Kwarantanna** podejrzanych plików

### 📊 Monitoring Wydajności
- Śledzenie użycia CPU i RAM
- Statystyki pobierania (prędkość, czas, rozmiar)
- Logi wydajności
- Alerty przy przekroczeniu limitów

## 📁 Struktura Projektu

```
video-downloader/
├── main.py                    # Główna aplikacja GUI
├── setup.py                   # Instalator
├── requirements.txt           # Zależności
├── pyproject.toml            # Konfiguracja projektu
│
├── config/                    # Konfiguracja
│   ├── __init__.py
│   ├── default_config.py      # Domyślne ustawienia
│   └── README.md
│
├── tests/                     # Testy
│   ├── __init__.py
│   ├── test_video_downloader.py        # Testy jednostkowe
│   ├── comprehensive_test.py           # Testy kompleksowe
│   └── README.md
│
├── Core Modules/
│   ├── download_manager.py    # Menedżer pobierania
│   ├── chat_monitor.py        # Monitor czatów
│   ├── backup_system.py       # System backupów
│   ├── security_validator.py  # Walidacja bezpieczeństwa
│   ├── performance_monitor.py # Monitor wydajności
│   └── system_diagnostics.py  # Diagnostyka systemu
│
├── run_with_tests.py          # Uruchomienie z testami
├── generated-icon.png         # Ikona aplikacji
│
└── attached_assets/           # Dokumentacja i plany
    └── *.txt                  # Plany rozwoju i instrukcje
```

## 🚀 Instalacja

### Metoda 1: Użycie setup.py (Zalecana)

```bash
# Sklonuj repozytorium
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader

# Instaluj pakiet
pip install -e .

# Lub z zależnościami deweloperskimi
pip install -e ".[dev]"
```

### Metoda 2: Ręczna instalacja

```bash
# Instaluj zależności
pip install -r requirements.txt

# Uruchom aplikację
python main.py
```

## 📦 Wymagania

### Python
- Python 3.8 lub nowszy

### Zależności (automatycznie instalowane)
- `pyperclip>=1.9.0` - Monitorowanie schowka
- `requests>=2.32.0` - Pobieranie HTTP
- `schedule>=1.2.0` - Automatyczne backupy
- `psutil>=5.9.0` - Monitoring systemu

### Opcjonalnie
- **FFmpeg** - Do konwersji wideo
  - Linux: `sudo apt install ffmpeg`
  - Mac: `brew install ffmpeg`
  - Windows: [Pobierz tutaj](https://www.gyan.dev/ffmpeg/builds/)

## 🎮 Użycie

### Podstawowe uruchomienie

```bash
# Uruchom aplikację GUI
python main.py

# Lub użyj zainstalowanego polecenia
video-downloader
```

### Uruchomienie z testami

```bash
# Pełne testy przed uruchomieniem
python run_with_tests.py

# Tylko testy
python tests/comprehensive_test.py

# Testy jednostkowe
python -m unittest tests/test_video_downloader.py
```

### Diagnostyka systemu

```bash
# Sprawdź środowisko
python system_diagnostics.py

# Lub użyj zainstalowanego polecenia
vd-diagnostics
```

### Konfiguracja

```python
from config import load_config, save_config

# Wczytaj konfigurację
config = load_config()

# Modyfikuj ustawienia
config['download']['max_concurrent'] = 5
config['monitoring']['clipboard_interval_seconds'] = 2

# Zapisz
save_config(config)
```

## 🖥️ Interfejs Graficzny

### Główne funkcje GUI:
1. **Monitorowanie schowka** - Automatyczne wykrywanie linków
2. **Lista pobranych plików** - Przegląd i zarządzanie
3. **Konwersja wideo** - Zmiana formatów
4. **Monitoring czatów** - Konfiguracja i status
5. **Pasek statusu** - Aktualne operacje i statystyki

### Skróty klawiszowe:
- `Ctrl+V` - Wklej link do pobrania
- `Ctrl+Q` - Zamknij aplikację
- `F5` - Odśwież listę plików

## 🔧 Konfiguracja

Plik konfiguracji znajduje się w:
- **Linux/Mac**: `~/.video_downloader/config.json`
- **Windows**: `C:\Users\Username\.video_downloader\config.json`

### Główne sekcje konfiguracji:
- `directories` - Ścieżki katalogów
- `download` - Ustawienia pobierania
- `monitoring` - Monitorowanie schowka i czatów
- `backup` - System backupów
- `security` - Bezpieczeństwo
- `video` - Formaty i konwersja
- `gui` - Interfejs użytkownika

Zobacz `config/README.md` dla szczegółów.

## 🧪 Testy

### Status testów: 80% ✅

Komponenty przetestowane:
- ✅ Importy modułów
- ✅ System backupów
- ✅ Menedżer pobierania
- ✅ Walidator bezpieczeństwa
- ✅ Monitor czatów
- ✅ Diagnostyka systemu
- ✅ Główna aplikacja
- ✅ Operacje na plikach

Zobacz `tests/README.md` dla szczegółów.

## 📊 Statystyki

- **Linie kodu**: ~3000+
- **Moduły**: 8 głównych
- **Testy**: 60+ testów jednostkowych
- **Pokrycie kodu**: 80%
- **Wspierane platformy**: Linux, macOS, Windows

## 🛠️ Rozwój

### Wymagania deweloperskie

```bash
pip install -e ".[dev]"
```

### Uruchamianie testów

```bash
# Wszystkie testy
pytest tests/

# Z pokryciem kodu
pytest tests/ --cov

# Verbose mode
pytest tests/ -v
```

### Formatowanie kodu

```bash
# Black
black *.py config/ tests/

# Flake8
flake8 *.py config/ tests/
```

## 🗺️ Roadmap

### Wersja 1.1 (Planowana)
- [ ] Wsparcie dla większej liczby platform wideo
- [ ] Pobieranie list odtwarzania
- [ ] Wybór jakości wideo
- [ ] Dark mode w GUI

### Wersja 1.2 (Planowana)
- [ ] Harmonogram pobierania
- [ ] Limit przepustowości
- [ ] Kategorie i tagi dla plików
- [ ] Eksport statystyk

### Wersja 2.0 (Przyszłość)
- [ ] Aplikacja webowa
- [ ] Synchronizacja między urządzeniami
- [ ] Wtyczki i rozszerzenia
- [ ] API REST

## 📝 Licencja

MIT License - Zobacz plik LICENSE

## 👥 Autorzy

Video Downloader Team

## 🤝 Współpraca

Zgłoszenia błędów i pull requesty są mile widziane!

1. Fork projektu
2. Stwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmian (`git commit -m 'Add AmazingFeature'`)
4. Push do brancha (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📞 Wsparcie

- **Issues**: [GitHub Issues](https://github.com/yourusername/video-downloader/issues)
- **Email**: support@videodownloader.example.com
- **Discord**: [Dołącz do serwera](https://discord.gg/example)

## ⚠️ Zastrzeżenia

Używaj tej aplikacji zgodnie z prawem autorskim i regulacjami dotyczącymi pobierania treści. Szanuj prawa twórców i przestrzegaj warunków korzystania platform, z których pobierasz treści.

---

**Zbudowane z ❤️ przy użyciu Python i Tkinter**
