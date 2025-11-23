# 📥 Instrukcja Instalacji - Video Downloader

Szczegółowa instrukcja instalacji dla różnych systemów operacyjnych.

## 📋 Spis Treści

1. [Wymagania systemowe](#wymagania-systemowe)
2. [Instalacja na Windows](#instalacja-na-windows)
3. [Instalacja na macOS](#instalacja-na-macos)
4. [Instalacja na Linux](#instalacja-na-linux)
5. [Instalacja na Replit](#instalacja-na-replit)
6. [Weryfikacja instalacji](#weryfikacja-instalacji)
7. [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## 🖥️ Wymagania Systemowe

### Minimalne
- **System**: Windows 7+, macOS 10.12+, lub Linux (Ubuntu 18.04+)
- **Python**: 3.8 lub nowszy
- **RAM**: 512 MB
- **Dysk**: 100 MB wolnego miejsca

### Zalecane
- **System**: Windows 10+, macOS 12+, lub Linux (Ubuntu 20.04+)
- **Python**: 3.11 lub nowszy
- **RAM**: 2 GB
- **Dysk**: 500 MB wolnego miejsca
- **Połączenie**: Szybki internet (dla pobierania wideo)

---

## 🪟 Instalacja na Windows

### Krok 1: Instalacja Python

1. Pobierz Python ze strony: https://www.python.org/downloads/
2. Uruchom instalator
3. **WAŻNE**: Zaznacz opcję "Add Python to PATH"
4. Kliknij "Install Now"
5. Po instalacji sprawdź w CMD:
   ```cmd
   python --version
   ```

### Krok 2: Instalacja Git (opcjonalnie)

1. Pobierz ze strony: https://git-scm.com/download/win
2. Zainstaluj z domyślnymi opcjami

### Krok 3: Pobranie projektu

**Opcja A: Przez Git**
```cmd
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader
```

**Opcja B: Pobierz ZIP**
1. Pobierz `video_downloader_complete.zip`
2. Rozpakuj do wybranego folderu
3. Otwórz CMD w tym folderze

### Krok 4: Instalacja zależności

```cmd
pip install -r requirements.txt
```

### Krok 5: Instalacja FFmpeg (opcjonalnie)

1. Pobierz ze strony: https://www.gyan.dev/ffmpeg/builds/
2. Wybierz "ffmpeg-release-essentials.zip"
3. Rozpakuj do `C:\ffmpeg\`
4. Dodaj do PATH:
   - Otwórz "Zmienne środowiskowe"
   - Edytuj zmienną "Path"
   - Dodaj: `C:\ffmpeg\bin`

### Krok 6: Uruchomienie

```cmd
python main.py
```

---

## 🍎 Instalacja na macOS

### Krok 1: Instalacja Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Krok 2: Instalacja Python

```bash
brew install python@3.11
python3 --version
```

### Krok 3: Pobranie projektu

```bash
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader
```

### Krok 4: Utworzenie środowiska wirtualnego

```bash
python3 -m venv venv
source venv/bin/activate
```

### Krok 5: Instalacja zależności

```bash
pip install -r requirements.txt
```

### Krok 6: Instalacja FFmpeg

```bash
brew install ffmpeg
```

### Krok 7: Uruchomienie

```bash
python main.py
```

---

## 🐧 Instalacja na Linux

### Ubuntu/Debian

#### Krok 1: Aktualizacja systemu

```bash
sudo apt update
sudo apt upgrade -y
```

#### Krok 2: Instalacja Python i pip

```bash
sudo apt install python3 python3-pip python3-tk git -y
python3 --version
```

#### Krok 3: Pobranie projektu

```bash
git clone https://github.com/yourusername/video-downloader.git
cd video-downloader
```

#### Krok 4: Utworzenie środowiska wirtualnego

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Krok 5: Instalacja zależności

```bash
pip install -r requirements.txt
```

#### Krok 6: Instalacja FFmpeg

```bash
sudo apt install ffmpeg -y
```

#### Krok 7: Uruchomienie

```bash
python main.py
```

### Fedora/RHEL

```bash
# Instalacja Python i zależności
sudo dnf install python3 python3-pip python3-tkinter git -y

# Instalacja FFmpeg
sudo dnf install ffmpeg -y

# Dalsze kroki jak w Ubuntu
```

### Arch Linux

```bash
# Instalacja Python i zależności
sudo pacman -S python python-pip tk git

# Instalacja FFmpeg
sudo pacman -S ffmpeg

# Dalsze kroki jak w Ubuntu
```

---

## ☁️ Instalacja na Replit

### Krok 1: Stwórz nowy Repl

1. Zaloguj się na https://replit.com
2. Kliknij "+ Create Repl"
3. Wybierz "Python"
4. Nazwij projekt "video-downloader"

### Krok 2: Upload plików

**Opcja A: Import z GitHub**
```bash
# W Shell Replit
git clone https://github.com/yourusername/video-downloader.git .
```

**Opcja B: Upload ZIP**
1. Pobierz `video_downloader_complete.zip`
2. W Replit kliknij ikone trzech kropek przy Files
3. Wybierz "Upload folder"
4. Wybierz rozpakowany folder

### Krok 3: Instalacja zależności

Replit automatycznie wykryje `requirements.txt` i zainstaluje pakiety.

Lub ręcznie:
```bash
pip install -r requirements.txt
```

### Krok 4: Konfiguracja

W pliku `.replit` upewnij się, że masz:
```toml
run = "python main.py"
```

### Krok 5: Uruchomienie

Kliknij przycisk "Run" w Replit.

---

## ✅ Weryfikacja Instalacji

### Test 1: Sprawdzenie Python

```bash
python --version
# Powinno pokazać: Python 3.8.x lub wyżej
```

### Test 2: Sprawdzenie zależności

```bash
python -c "import pyperclip; import requests; import schedule; print('✅ Wszystkie pakiety zainstalowane')"
```

### Test 3: Diagnostyka systemu

```bash
python system_diagnostics.py
```

Powinieneś zobaczyć:
- ✅ Python version OK
- ✅ Packages check: True
- ✅ Network check: True
- ✅ GUI check: True

### Test 4: Uruchomienie testów

```bash
python tests/comprehensive_test.py
```

Oczekiwany wynik: **80%+ testów przeszło**

### Test 5: Uruchomienie aplikacji

```bash
python main.py
```

Powinieneś zobaczyć okno GUI aplikacji.

---

## 🔧 Rozwiązywanie Problemów

### Problem: "python: command not found"

**Windows:**
```cmd
# Użyj py zamiast python
py main.py
```

**Linux/Mac:**
```bash
# Użyj python3 zamiast python
python3 main.py
```

### Problem: "No module named 'tkinter'"

**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

### Problem: "ModuleNotFoundError: No module named 'pyperclip'"

```bash
# Upewnij się, że zainstalowałeś zależności
pip install -r requirements.txt

# Lub ręcznie
pip install pyperclip requests schedule psutil
```

### Problem: FFmpeg nie działa

**Sprawdź instalację:**
```bash
ffmpeg -version
```

**Windows:**
- Sprawdź czy FFmpeg jest w PATH
- Uruchom CMD jako Administrator i dodaj do PATH

**Linux:**
```bash
which ffmpeg
# Powinno zwrócić ścieżkę
```

### Problem: Brak uprawnień do zapisu

**Linux/Mac:**
```bash
# Nadaj uprawnienia
chmod +x main.py
chmod -R 755 .
```

**Windows:**
- Uruchom CMD jako Administrator
- Lub zmień katalog instalacji na folder użytkownika

### Problem: GUI się nie wyświetla na Replit

Replit nie wspiera aplikacji GUI przez VNC. Użyj:

**Opcja 1:** Uruchom lokalnie na swoim komputerze

**Opcja 2:** Użyj tylko funkcji CLI bez GUI

### Problem: Błąd przy pobieraniu

1. Sprawdź połączenie z internetem
2. Sprawdź czy URL jest poprawny
3. Sprawdź logi w `~/.video_downloader/logs/`

### Problem: Testy nie przechodzą

```bash
# Sprawdź brakujące zależności
pip install --upgrade -r requirements.txt

# Uruchom diagnostykę
python system_diagnostics.py

# Sprawdź konkretny test
python -m unittest tests.test_video_downloader -v
```

---

## 📞 Pomoc

Jeśli nadal masz problemy:

1. **Sprawdź logi**: `~/.video_downloader/logs/`
2. **Uruchom diagnostykę**: `python system_diagnostics.py`
3. **Zgłoś problem**: [GitHub Issues](https://github.com/yourusername/video-downloader/issues)
4. **Kontakt**: support@videodownloader.example.com

---

## 🎉 Gotowe!

Jeśli wszystkie testy przeszły, możesz zacząć korzystać z Video Downloader!

Przejdź do [README.md](README.md) aby poznać funkcje i sposób użycia.
