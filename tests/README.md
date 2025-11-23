# Testy Video Downloader

Ten katalog zawiera testy dla systemu Video Downloader.

## Struktura testów

### `test_video_downloader.py`
Testy jednostkowe głównych funkcji aplikacji:
- Inicjalizacja aplikacji
- Wykrywanie URL-i wideo
- Pobieranie plików
- Kontrola monitorowania
- Zarządzanie listą plików

### `comprehensive_test.py`
Kompleksowe testy wszystkich komponentów:
- Importy modułów
- System backupów
- Menedżer pobierania
- Walidator bezpieczeństwa
- Monitor wydajności
- Monitor czatów
- Diagnostyka systemu
- Główna aplikacja
- Operacje na plikach
- Operacje sieciowe
- Bezpieczeństwo wątków

## Uruchamianie testów

### Wszystkie testy
```bash
python tests/comprehensive_test.py
```

### Testy jednostkowe
```bash
python -m unittest tests/test_video_downloader.py
```

### Z pytest (jeśli zainstalowany)
```bash
pytest tests/
pytest tests/ -v  # tryb verbose
pytest tests/ --cov  # z pokryciem kodu
```

## Wymagania

Podstawowe zależności są wymienione w `requirements.txt`. Dla pełnej funkcjonalności testów:

```bash
pip install -r requirements.txt
```

Dla testów deweloperskich:
```bash
pip install pytest pytest-cov black flake8
```

## Wyniki testów

Testy sprawdzają:
- ✅ **Importy modułów** - czy wszystkie komponenty się importują
- ✅ **System backupów** - tworzenie i zarządzanie kopiami zapasowymi
- ✅ **Pobieranie** - kolejkowanie, walidacja, retry
- ✅ **Bezpieczeństwo** - skanowanie URL-i i plików
- ✅ **Wydajność** - monitoring zasobów systemowych
- ✅ **Chat monitoring** - wykrywanie linków w czatach
- ✅ **Diagnostyka** - sprawdzanie środowiska
- ✅ **GUI** - interfejs użytkownika
- ✅ **Operacje na plikach** - tworzenie, listowanie, sortowanie
- ✅ **Sieć** - HTTP, timeouty, przekierowania
- ✅ **Threading** - bezpieczeństwo wielowątkowe

## Status

Obecny wskaźnik sukcesu: **80%** (8/10 komponentów działa poprawnie)

Komponenty wymagające uwagi:
- Monitor wydajności (brak metody `log_download_start`)
- Dodatkowe testy GUI (wymaga pełnego środowiska graficznego)
