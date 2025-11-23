
#!/usr/bin/env python3
"""
System kopii bezpieczeństwa dla Video Downloader
Automatyczne tworzenie backupów kodu i danych
Przywracanie z linii komend
"""

import os
import shutil
import datetime
import zipfile
from pathlib import Path
import schedule
import time
import sys
import argparse
import json

class BackupManager:
    def __init__(self):
        # Główny folder backupów
        if "REPLIT" in os.environ:
            self.backup_dir = Path(os.getcwd()) / "backups"
        else:
            self.backup_dir = Path.home() / ".video_downloader" / "backups"
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Podfoldery dla różnych typów backupów
        self.daily_backup_dir = self.backup_dir / "daily"
        self.update_backup_dir = self.backup_dir / "updates"
        self.manual_backup_dir = self.backup_dir / "manual"
        
        for dir_path in [self.daily_backup_dir, self.update_backup_dir, self.manual_backup_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Plik z metadanymi backupów
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Załaduj metadane backupów"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    "last_daily_backup": None,
                    "last_update_backup": None,
                    "version": "1.0.0",
                    "backups": []
                }
        except Exception:
            self.metadata = {
                "last_daily_backup": None,
                "last_update_backup": None,
                "version": "1.0.0",
                "backups": []
            }
    
    def save_metadata(self):
        """Zapisz metadane backupów"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Błąd zapisywania metadanych: {e}")
    
    def should_create_daily_backup(self):
        """Sprawdź czy należy utworzyć dzienny backup"""
        if not self.metadata["last_daily_backup"]:
            return True
        
        last_backup = datetime.datetime.fromisoformat(self.metadata["last_daily_backup"])
        now = datetime.datetime.now()
        return (now - last_backup).days >= 1
    
    def create_version_backup(self, version_from, version_to):
        """Utwórz backup przed aktualizacją wersji"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"v{version_from}_to_v{version_to}_{timestamp}.zip"
            backup_path = self.update_backup_dir / backup_name
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # Pliki systemu
                system_files = [
                    "main.py", "backup_system.py", "download_manager.py",
                    "security_validator.py", "performance_monitor.py",
                    "system_diagnostics.py", "test_video_downloader.py",
                    "run_with_tests.py", "pyproject.toml", ".replit"
                ]
                
                for file_name in system_files:
                    file_path = Path(file_name)
                    if file_path.exists():
                        backup_zip.write(file_path, f"system/{file_name}")
                
                # Ustawienia użytkownika
                settings_dir = Path.home() / ".video_downloader"
                if settings_dir.exists():
                    for file_path in settings_dir.rglob("*"):
                        if file_path.is_file():
                            relative_path = file_path.relative_to(settings_dir)
                            backup_zip.write(file_path, f"settings/{relative_path}")
                
                # Informacje o backupie
                backup_info = {
                    "created": datetime.datetime.now().isoformat(),
                    "version_from": version_from,
                    "version_to": version_to,
                    "type": "version_update",
                    "system": "Replit" if "REPLIT" in os.environ else "Local"
                }
                
                backup_zip.writestr("backup_info.json", json.dumps(backup_info, indent=2))
            
            # Aktualizuj metadane
            self.metadata["last_update_backup"] = datetime.datetime.now().isoformat()
            self.metadata["version"] = version_to
            self.metadata["backups"].append({
                "path": str(backup_path),
                "created": backup_info["created"],
                "type": "version_update",
                "version_from": version_from,
                "version_to": version_to
            })
            self.save_metadata()
            
            print(f"📦 Utworzono backup aktualizacji: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Błąd tworzenia backup aktualizacji: {e}")
            return None
    
    def create_automatic_daily_backup(self):
        """Utwórz automatyczny dzienny backup"""
        if not self.should_create_daily_backup():
            return None
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"daily_backup_{timestamp}.zip"
            backup_path = self.daily_backup_dir / backup_name
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # Kod aplikacji
                code_files = [
                    "main.py", "backup_system.py", "download_manager.py",
                    "security_validator.py", "performance_monitor.py",
                    "system_diagnostics.py", "test_video_downloader.py",
                    "run_with_tests.py"
                ]
                
                for file_name in code_files:
                    file_path = Path(file_name)
                    if file_path.exists():
                        backup_zip.write(file_path, f"code/{file_name}")
                
                # Ustawienia użytkownika
                settings_dir = Path.home() / ".video_downloader"
                if settings_dir.exists():
                    for file_path in settings_dir.rglob("*"):
                        if file_path.is_file() and file_path.suffix in ['.json', '.txt', '.conf']:
                            relative_path = file_path.relative_to(settings_dir)
                            backup_zip.write(file_path, f"settings/{relative_path}")
                
                # Lista pobranych plików (tylko nazwy i ścieżki)
                downloads_dir = Path.home() / "Downloads" / "Videos"
                if "REPLIT" in os.environ:
                    downloads_dir = Path(os.getcwd()) / "downloads"
                
                if downloads_dir.exists():
                    file_list = []
                    for video_file in downloads_dir.rglob("*"):
                        if video_file.is_file():
                            file_list.append({
                                "name": video_file.name,
                                "path": str(video_file),
                                "size": video_file.stat().st_size,
                                "modified": video_file.stat().st_mtime
                            })
                    
                    backup_zip.writestr("downloads_list.json", json.dumps(file_list, indent=2))
                
                # Informacje o backupie
                backup_info = {
                    "created": datetime.datetime.now().isoformat(),
                    "type": "daily_automatic",
                    "system": "Replit" if "REPLIT" in os.environ else "Local",
                    "code_files": len(code_files),
                    "downloads_count": len(file_list) if 'file_list' in locals() else 0
                }
                
                backup_zip.writestr("backup_info.json", json.dumps(backup_info, indent=2))
            
            # Aktualizuj metadane
            self.metadata["last_daily_backup"] = datetime.datetime.now().isoformat()
            self.metadata["backups"].append({
                "path": str(backup_path),
                "created": backup_info["created"],
                "type": "daily_automatic"
            })
            self.save_metadata()
            
            print(f"📦 Utworzono automatyczny dzienny backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Błąd tworzenia dziennego backupu: {e}")
            return None

    def create_code_backup(self):
        """Utwórz backup kodu aplikacji (manualny)"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"manual_code_backup_{timestamp}.zip"
            backup_path = self.manual_backup_dir / backup_name
            
            # Pliki do backup
            files_to_backup = [
                "main.py",
                "test_video_downloader.py", 
                "run_with_tests.py",
                "backup_system.py",
                "pyproject.toml",
                ".replit"
            ]
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                for file_name in files_to_backup:
                    file_path = Path(file_name)
                    if file_path.exists():
                        backup_zip.write(file_path, file_name)
                        print(f"✅ Dodano do backup: {file_name}")
                
                # Dodaj informacje o backup
                info = f"""Backup created: {datetime.datetime.now()}
System: {'Replit' if 'REPLIT' in os.environ else 'Local'}
Files: {len(files_to_backup)}
"""
                backup_zip.writestr("backup_info.txt", info)
            
            print(f"📦 Utworzono backup kodu: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Błąd podczas tworzenia backup kodu: {e}")
            return None
    
    def create_data_backup(self):
        """Utwórz backup danych użytkownika"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"data_backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            # Foldery z danymi
            data_dirs = [
                Path.home() / "Downloads" / "Videos",
                Path(os.getcwd()) / "downloads" if "REPLIT" in os.environ else None,
                Path.home() / "Videos"
            ]
            
            # Usuń None values
            data_dirs = [d for d in data_dirs if d and d.exists()]
            
            if not data_dirs:
                print("📂 Brak folderów z danymi do backup")
                return None
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                file_count = 0
                
                for data_dir in data_dirs:
                    if data_dir.exists():
                        for file_path in data_dir.rglob("*"):
                            if file_path.is_file():
                                # Sprawdź czy to plik wideo
                                video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']
                                if any(file_path.suffix.lower() == ext for ext in video_extensions):
                                    relative_path = file_path.relative_to(data_dir.parent)
                                    backup_zip.write(file_path, str(relative_path))
                                    file_count += 1
                                    print(f"✅ Dodano do backup: {file_path.name}")
                
                # Dodaj informacje o backup
                info = f"""Data backup created: {datetime.datetime.now()}
System: {'Replit' if 'REPLIT' in os.environ else 'Local'}
Video files: {file_count}
Directories scanned: {len(data_dirs)}
"""
                backup_zip.writestr("data_backup_info.txt", info)
            
            print(f"📦 Utworzono backup danych: {backup_path} ({file_count} plików)")
            return backup_path
            
        except Exception as e:
            print(f"❌ Błąd podczas tworzenia backup danych: {e}")
            return None
    
    def cleanup_old_backups(self, max_backups=10):
        """Usuń stare backupy, zostaw tylko najnowsze"""
        try:
            backup_files = list(self.backup_dir.glob("*.zip"))
            if len(backup_files) > max_backups:
                # Sortuj według daty modyfikacji
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Usuń najstarsze
                to_remove = backup_files[:-max_backups]
                for backup_file in to_remove:
                    backup_file.unlink()
                    print(f"🗑️  Usunięto stary backup: {backup_file.name}")
                    
        except Exception as e:
            print(f"❌ Błąd podczas czyszczenia backupów: {e}")
    
    def list_available_backups(self):
        """Wyświetl dostępne backupy"""
        all_backups = []
        
        for backup_dir in [self.daily_backup_dir, self.update_backup_dir, self.manual_backup_dir]:
            for backup_file in backup_dir.glob("*.zip"):
                backup_info = {
                    "path": backup_file,
                    "name": backup_file.name,
                    "type": backup_dir.name,
                    "size": backup_file.stat().st_size / (1024 * 1024),  # MB
                    "modified": datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
                }
                all_backups.append(backup_info)
        
        # Sortuj według daty modyfikacji
        all_backups.sort(key=lambda x: x["modified"], reverse=True)
        return all_backups
    
    def restore_from_backup(self, backup_path, restore_type="full"):
        """Przywróć dane z backupu"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                print(f"❌ Backup nie istnieje: {backup_path}")
                return False
            
            print(f"🔄 Przywracanie z backupu: {backup_path.name}")
            
            # Utwórz backup aktualnego stanu przed przywracaniem
            current_backup = self.create_code_backup()
            if current_backup:
                print(f"💾 Utworzono backup aktualnego stanu: {Path(current_backup).name}")
            
            with zipfile.ZipFile(backup_path, 'r') as backup_zip:
                # Sprawdź zawartość backupu
                file_list = backup_zip.namelist()
                
                if restore_type == "code_only":
                    # Przywróć tylko kod
                    for file_name in file_list:
                        if file_name.startswith("code/") or file_name.startswith("system/"):
                            extracted_path = Path(file_name).name
                            if extracted_path.endswith(".py") or extracted_path in [".replit", "pyproject.toml"]:
                                backup_zip.extract(file_name, Path.cwd())
                                # Przenieś plik do właściwego miejsca
                                extracted_file = Path(file_name)
                                if extracted_file.exists():
                                    shutil.move(str(extracted_file), extracted_path)
                                    print(f"  ✅ Przywrócono: {extracted_path}")
                
                elif restore_type == "settings_only":
                    # Przywróć tylko ustawienia
                    settings_dir = Path.home() / ".video_downloader"
                    settings_dir.mkdir(exist_ok=True)
                    
                    for file_name in file_list:
                        if file_name.startswith("settings/"):
                            backup_zip.extract(file_name, settings_dir.parent)
                            print(f"  ✅ Przywrócono ustawienia: {file_name}")
                
                else:
                    # Pełne przywracanie
                    backup_zip.extractall(Path.cwd())
                    print(f"✅ Przywrócono wszystkie dane z: {backup_path}")
                
                return True
                
        except Exception as e:
            print(f"❌ Błąd podczas przywracania: {e}")
            return False
    
    def restore_by_date(self, date_str):
        """Przywróć backup z określonej daty"""
        try:
            target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Znajdź backupy z danej daty
            matching_backups = []
            for backup_info in self.list_available_backups():
                backup_date = backup_info["modified"].date()
                if backup_date == target_date:
                    matching_backups.append(backup_info)
            
            if not matching_backups:
                print(f"❌ Nie znaleziono backupów z daty: {date_str}")
                return False
            
            # Użyj najnowszego backupu z danej daty
            latest_backup = max(matching_backups, key=lambda x: x["modified"])
            print(f"🔍 Znaleziono backup z {date_str}: {latest_backup['name']}")
            
            return self.restore_from_backup(latest_backup["path"])
            
        except ValueError:
            print(f"❌ Nieprawidłowy format daty: {date_str}. Użyj YYYY-MM-DD")
            return False
        except Exception as e:
            print(f"❌ Błąd przywracania z daty: {e}")
            return False
    
    def schedule_backups(self):
        """Zaplanuj automatyczne backupy"""
        print("⏰ Planowanie automatycznych backupów...")
        
        # Backup kodu codziennie o 2:00
        schedule.every().day.at("02:00").do(self.create_code_backup)
        
        # Backup danych co tydzień w niedzielę o 3:00
        schedule.every().sunday.at("03:00").do(self.create_data_backup)
        
        # Czyszczenie starych backupów co miesiąc
        schedule.every().month.do(self.cleanup_old_backups)
        
        print("✅ Zaplanowano automatyczne backupy")
        
        # Pętla uruchamiania zadań
        while True:
            schedule.run_pending()
            time.sleep(60)  # Sprawdzaj co minutę

def run_automatic_backups():
    """Uruchom automatyczne backupy w tle"""
    backup_manager = BackupManager()
    
    # Sprawdź czy należy utworzyć dzienny backup
    if backup_manager.should_create_daily_backup():
        backup_manager.create_automatic_daily_backup()
    
    print("🔄 Automatyczne backupy uruchomione")

def handle_command_line():
    """Obsługa argumentów linii komend"""
    parser = argparse.ArgumentParser(description="Video Downloader Backup System")
    parser.add_argument("--restore-backup", metavar="DATE", 
                       help="Przywróć backup z określonej daty (YYYY-MM-DD)")
    parser.add_argument("--list-backups", action="store_true",
                       help="Wyświetl dostępne backupy")
    parser.add_argument("--create-backup", action="store_true",
                       help="Utwórz natychmiastowy backup")
    parser.add_argument("--auto-backup", action="store_true",
                       help="Uruchom automatyczne backupy")
    parser.add_argument("--restore-type", choices=["full", "code_only", "settings_only"],
                       default="full", help="Typ przywracania")
    
    args = parser.parse_args()
    backup_manager = BackupManager()
    
    if args.restore_backup:
        print(f"🔄 Przywracanie backupu z daty: {args.restore_backup}")
        success = backup_manager.restore_by_date(args.restore_backup)
        sys.exit(0 if success else 1)
    
    elif args.list_backups:
        backups = backup_manager.list_available_backups()
        if backups:
            print("📦 DOSTĘPNE BACKUPY")
            print("=" * 50)
            for backup in backups:
                print(f"📁 {backup['name']}")
                print(f"   Typ: {backup['type']}")
                print(f"   Data: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Rozmiar: {backup['size']:.1f} MB")
                print()
        else:
            print("📂 Brak dostępnych backupów")
        sys.exit(0)
    
    elif args.create_backup:
        print("💾 Tworzenie backupu...")
        backup_path = backup_manager.create_code_backup()
        if backup_path:
            print(f"✅ Backup utworzony: {Path(backup_path).name}")
        sys.exit(0 if backup_path else 1)
    
    elif args.auto_backup:
        run_automatic_backups()
        sys.exit(0)
    
    else:
        # Uruchom interaktywny tryb
        interactive_mode()

def interactive_mode():
    """Interaktywny tryb zarządzania backupami"""
    backup_manager = BackupManager()
    
    print("🔄 SYSTEM KOPII BEZPIECZEŃSTWA")
    print("=" * 40)
    print("1. Backup kodu")
    print("2. Backup danych")
    print("3. Przywróć z backup")
    print("4. Uruchom automatyczne backupy")
    print("5. Pokaż istniejące backupy")
    print("6. Przywróć z daty")
    print("0. Wyjście")
    
    while True:
        try:
            choice = input("\n🔢 Wybierz opcję: ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                backup_manager.create_code_backup()
            elif choice == "2":
                backup_manager.create_data_backup()
            elif choice == "3":
                backups = backup_manager.list_available_backups()
                if backups:
                    print("📦 Dostępne backupy:")
                    for i, backup in enumerate(backups):
                        print(f"  {i+1}. {backup['name']} ({backup['type']}, {backup['size']:.1f} MB)")
                    
                    try:
                        idx = int(input("Wybierz numer: ")) - 1
                        if 0 <= idx < len(backups):
                            restore_type = input("Typ przywracania (full/code_only/settings_only) [full]: ").strip() or "full"
                            backup_manager.restore_from_backup(backups[idx]["path"], restore_type)
                    except ValueError:
                        print("❌ Nieprawidłowy numer")
                else:
                    print("📂 Brak dostępnych backupów")
            elif choice == "4":
                backup_manager.schedule_backups()
            elif choice == "5":
                backups = backup_manager.list_available_backups()
                if backups:
                    print("📦 Istniejące backupy:")
                    for backup in backups:
                        print(f"  📁 {backup['name']}")
                        print(f"     Typ: {backup['type']} | Rozmiar: {backup['size']:.1f} MB")
                        print(f"     Data: {backup['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                        print()
                else:
                    print("📂 Brak backupów")
            elif choice == "6":
                date_str = input("Podaj datę (YYYY-MM-DD): ").strip()
                if date_str:
                    backup_manager.restore_by_date(date_str)
            else:
                print("❓ Nieprawidłowa opcja")
                
        except KeyboardInterrupt:
            print("\n👋 Do widzenia!")
            break
        except Exception as e:
            print(f"❌ Błąd: {e}")

def main():
    """Główna funkcja - sprawdź argumenty linii komend"""
    if len(sys.argv) > 1:
        handle_command_line()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
