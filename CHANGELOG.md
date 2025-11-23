# Changelog

Wszystkie istotne zmiany w projekcie będą dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.0.0/),
projekt używa [Semantic Versioning](https://semver.org/lang/pl/).

## [1.0.0] - 2025-11-23

### Dodane
- 🎬 Główna aplikacja GUI z pełnym interfejsem użytkownika
- 📥 System pobierania z kolejkowaniem i priorytetami
- 📋 Automatyczne monitorowanie schowka dla linków wideo
- 💬 Monitor czatów (Telegram, Discord, WhatsApp)
- 🔄 Konwersja formatów wideo (MOV → MP4)
- 💾 Automatyczny system backupów (dzienny i manualny)
- 🔒 Walidacja bezpieczeństwa URL-i i plików
- 📊 Monitor wydajności systemu
- 🔍 System diagnostyki środowiska
- 🧪 Kompleksowy zestaw testów (60+ testów)
- 📦 Instalator setup.py
- 📁 System konfiguracji (config/)
- 📖 Pełna dokumentacja (README.md, INSTALLATION.md)
- ⚖️ Licencja MIT

### Funkcje
- Równoległe pobieranie (do 3 jednocześnie)
- System retry dla nieudanych pobrań
- Detekcja duplikatów
- Czarna lista niebezpiecznych domen
- Limity rozmiaru plików (500MB default)
- Timeout dla długich operacji
- Sanityzacja nazw plików
- Historia przetworzonych linków
- Rotacja backupów (7 dni/30 dni)
- Monitorowanie CPU i RAM
- Logowanie do plików
- Powiadomienia GUI

### Techniczne
- Python 3.8+ support
- Tkinter GUI
- Wielowątkowe operacje
- Thread-safe download manager
- Async monitoring
- SQLite dla historii czatów
- JSON dla konfiguracji
- ZIP dla backupów

### Testy
- 80% pokrycia testami
- Testy jednostkowe (test_video_downloader.py)
- Testy kompleksowe (comprehensive_test.py)
- Testy importów, backupów, pobierania
- Testy bezpieczeństwa i wydajności
- Testy operacji sieciowych i na plikach

### Dokumentacja
- README.md - główna dokumentacja
- INSTALLATION.md - instalacja na wszystkich platformach
- config/README.md - konfiguracja systemu
- tests/README.md - dokumentacja testów
- CHANGELOG.md - historia zmian
- LICENSE - licencja MIT

## [Planowane] - Roadmap

### [1.1.0] - Q1 2026
- [ ] Wsparcie dla większej liczby platform (TikTok, Twitter, Instagram)
- [ ] Pobieranie list odtwarzania
- [ ] Wybór jakości wideo przy pobieraniu
- [ ] Dark mode w GUI
- [ ] Eksport/Import ustawień
- [ ] Wielojęzyczność (EN, PL, DE, ES)

### [1.2.0] - Q2 2026
- [ ] Harmonogram pobierania (cron-like)
- [ ] Limit przepustowości
- [ ] Kategorie i tagi dla pobranych plików
- [ ] Zaawansowane statystyki (wykresy, raporty)
- [ ] Wtyczka do przeglądarki
- [ ] Integracja z cloud storage (Dropbox, Google Drive)

### [2.0.0] - Q3-Q4 2026
- [ ] Aplikacja webowa (Flask/FastAPI)
- [ ] API REST
- [ ] Synchronizacja między urządzeniami
- [ ] System wtyczek i rozszerzeń
- [ ] Docker support
- [ ] Mobile app (React Native)
- [ ] Współdzielenie list pobierania
- [ ] Premium features

---

## Legenda

- `Dodane` - nowe funkcje
- `Zmienione` - zmiany w istniejących funkcjach
- `Przestarzałe` - funkcje do usunięcia w przyszłości
- `Usunięte` - usunięte funkcje
- `Naprawione` - poprawki błędów
- `Bezpieczeństwo` - poprawki bezpieczeństwa
