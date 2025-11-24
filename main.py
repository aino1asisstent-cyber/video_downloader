#!/usr/bin/env python3
"""
DEEPINTEL VIDEO SUITE - Professional Video Downloader & Converter
Enterprise-grade video processing with bulletproof error handling
"""

import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, unquote
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import pyperclip
from concurrent.futures import ThreadPoolExecutor

# Import our bulletproof error handler
from error_handler import error_handler, logger

class DeepIntelVideoSuite:
    def __init__(self, root):
        self.root = root
        self.root.title("DeepIntel Video Suite v2.0 - Professional")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Production configuration
        self.max_concurrent_downloads = 3
        self.max_file_size_mb = 2000  # 2GB limit
        self.supported_formats = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v']
        
        # Application state
        self.downloading = False
        self.converting = False
        self.downloaded_files = []
        self.active_downloads = {}
        self.ffmpeg_available = self.check_ffmpeg()
        
        # Thread management
        self.thread_pool = ThreadPoolExecutor(max_workers=5)
        
        # Initialize components
        self.setup_ui()
        self.start_background_tasks()
        
        logger.info("DeepIntel Video Suite initialized successfully")
    
    def setup_ui(self):
        """Setup professional enterprise UI"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Header
        header_frame = ttk.LabelFrame(main_frame, text="DeepIntel Video Suite", padding="10")
        header_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(header_frame, text="Professional Video Downloader & Converter", 
                 font=('Arial', 12, 'bold')).pack()
        ttk.Label(header_frame, text="Enterprise-grade video processing with AI optimization",
                 font=('Arial', 9)).pack()
        
        # Download Section
        download_frame = ttk.LabelFrame(main_frame, text="Download Management", padding="10")
        download_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # URL Input
        ttk.Label(download_frame, text="Video URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(download_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        download_buttons = ttk.Frame(download_frame)
        download_buttons.grid(row=0, column=2, padx=5)
        
        ttk.Button(download_buttons, text="Download", 
                  command=self.safe_start_download).pack(side=tk.LEFT, padx=2)
        ttk.Button(download_buttons, text="Add to Queue", 
                  command=self.safe_add_to_queue).pack(side=tk.LEFT, padx=2)
        ttk.Button(download_buttons, text="Paste URL", 
                  command=self.safe_paste_url).pack(side=tk.LEFT, padx=2)
        
        # Download Directory
        ttk.Label(download_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.download_dir_var = tk.StringVar(value=str(Path.home() / "Downloads" / "DeepIntelVideos"))
        ttk.Entry(download_frame, textvariable=self.download_dir_var, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=(10, 0))
        ttk.Button(download_frame, text="Browse", 
                  command=self.safe_browse_directory).grid(row=1, column=2, padx=5, pady=(10, 0))
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5)
        
        self.status_var = tk.StringVar(value="Ready to download")
        ttk.Label(progress_frame, textvariable=self.status_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=(5, 0))
        
        # File List
        files_frame = ttk.LabelFrame(main_frame, text="Downloaded Files", padding="10")
        files_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)
        
        # File list with scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(list_frame, height=10)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # File actions
        actions_frame = ttk.Frame(files_frame)
        actions_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(actions_frame, text="Open File", command=self.safe_open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Open Folder", command=self.safe_open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Convert", command=self.safe_convert_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Delete", command=self.safe_delete_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Refresh", command=self.safe_refresh_file_list).pack(side=tk.LEFT, padx=2)
        
        # Conversion Settings
        convert_frame = ttk.LabelFrame(main_frame, text="Conversion Settings", padding="10")
        convert_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(convert_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.format_var = tk.StringVar(value="mp4")
        format_combo = ttk.Combobox(convert_frame, textvariable=self.format_var, 
                                   values=["mp4", "avi", "mov", "mkv"], state="readonly")
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(convert_frame, text="Quality:").grid(row=0, column=2, sticky=tk.W, padx=(20, 5))
        self.quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(convert_frame, textvariable=self.quality_var,
                                    values=["high", "medium", "low"], state="readonly")
        quality_combo.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        # System Info
        info_frame = ttk.LabelFrame(main_frame, text="System Information", padding="10")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        ffmpeg_status = "Available" if self.ffmpeg_available else "Not Available"
        ttk.Label(info_frame, text=f"FFmpeg: {ffmpeg_status}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"Active Downloads: 0/{self.max_concurrent_downloads}").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Bind events
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.safe_open_file())
        url_entry.bind('<Return>', lambda e: self.safe_start_download())
        
        # Initial setup
        self.safe_refresh_file_list()
    
    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"FFmpeg not available: {e}")
            return False
    
    def start_background_tasks(self):
        """Start background monitoring tasks"""
        # Clipboard monitoring
        self.safe_monitor_clipboard()
        
        # Auto-refresh file list
        self.safe_auto_refresh_files()
    
    def safe_monitor_clipboard(self):
        """Safely monitor clipboard for video URLs"""
        try:
            import pyperclip
            clipboard_content = pyperclip.paste().strip()
            if (clipboard_content.startswith(('http://', 'https://')) and
                self.is_video_url(clipboard_content) and
                clipboard_content != getattr(self, 'last_clipboard_url', '')):
                
                self.last_clipboard_url = clipboard_content
                self.url_var.set(clipboard_content)
                self.update_status(f"URL detected in clipboard: {clipboard_content[:50]}...")
                
        except Exception as e:
            pass  # Silently handle clipboard errors
        
        # Auto-restart on error
        self.root.after(3000, self.safe_monitor_clipboard)
    
    def safe_auto_refresh_files(self):
        """Safely auto-refresh file list"""
        self.safe_refresh_file_list()
        # Auto-restart on error
        self.root.after(5000, self.safe_auto_refresh_files)
    
    def is_video_url(self, url):
        """Check if URL points to a video file"""
        try:
            parsed = urlparse(url)
            path_lower = parsed.path.lower()
            
            # Check file extension
            if any(path_lower.endswith(ext) for ext in self.supported_formats):
                return True
            
            # Check video platforms
            video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com']
            if any(domain in parsed.netloc for domain in video_domains):
                return True
                
            return False
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def safe_paste_url(self):
        """Safely paste URL from clipboard"""
        try:
            import pyperclip
            clipboard_content = pyperclip.paste().strip()
            self.url_var.set(clipboard_content)
        except Exception as e:
            error_handler.show_operation_error("paste_url", str(e))
    
    def safe_browse_directory(self):
        """Safely browse for download directory"""
        try:
            directory = filedialog.askdirectory()
            if directory:
                self.download_dir_var.set(directory)
                self.safe_refresh_file_list()
        except Exception as e:
            error_handler.show_operation_error("browse_directory", str(e))
    
    def safe_start_download(self):
        """Safely start download process"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Input Required", "Please enter a URL")
            return
        
        if not self.is_video_url(url):
            messagebox.showwarning("Invalid URL", "This doesn't appear to be a video URL")
            return
        
        # Run download in thread with error handling
        # Run download in thread
        self.thread_pool.submit(self.download_video, url)






    
    def safe_add_to_queue(self):
        """Safely add URL to download queue"""
        url = self.url_var.get().strip()
        if url and self.is_video_url(url):
            self.update_status(f"Added to queue: {url[:50]}...")
            self.safe_start_download()
    
    def download_video(self, url):
        """Download video file with comprehensive error handling"""
        try:
            self.downloading = True
            self.update_status(f"Starting download: {url[:50]}...")
            
            # Create download directory
            download_dir = Path(self.download_dir_var.get())
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Get filename from URL
            filename = self.get_filename_from_url(url)
            file_path = download_dir / filename
            
            # Check if file already exists
            if file_path.exists():
                # This would need to be handled in main thread
                self.root.after(0, lambda: self.prompt_overwrite(file_path, url))
                return
            
            # Download file
            self.update_status(f"Downloading: {filename}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            self.root.after(0, lambda: self.progress_var.set(progress))
            
            # Add to file list
            self.downloaded_files.append(str(file_path))
            self.root.after(0, self.safe_refresh_file_list)
            
            self.update_status(f"Download completed: {filename}")
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # Auto-convert if enabled and FFmpeg available
            if self.ffmpeg_available:
                self.root.after(1000, lambda: self.auto_convert_file(str(file_path)))
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)  # Re-raise for error handler
        finally:
            self.downloading = False
    
    def prompt_overwrite(self, file_path, url):
        """Prompt user about file overwrite"""
        response = messagebox.askyesno("File Exists", 
                                      f"File {file_path.name} already exists. Overwrite?")
        if response:
            # Restart download with overwrite
            self.thread_pool.submit(self.download_video, url)





        else:
            self.update_status("Download cancelled")
    
    def get_filename_from_url(self, url):
        """Extract filename from URL"""
        try:
            parsed = urlparse(url)
            filename = unquote(parsed.path.split('/')[-1])
            
            if not filename or '.' not in filename:
                filename = f"video_{int(time.time())}.mp4"
            
            # Ensure valid filename
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            return filename
        except Exception as e:
            logger.warning(f"Failed to extract filename, using default: {e}")
            return f"video_{int(time.time())}.mp4"
    
    def safe_refresh_file_list(self):
        """Safely refresh file list display"""
        try:
            download_dir = Path(self.download_dir_var.get())
            if not download_dir.exists():
                return
            
            self.file_listbox.delete(0, tk.END)
            
            # Find video files
            video_files = []
            for ext in self.supported_formats:
                video_files.extend(download_dir.glob(f"*{ext}"))
            
            # Sort by modification time (newest first)
            video_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            self.downloaded_files = [str(f) for f in video_files]
            
            for file_path in video_files:
                self.file_listbox.insert(tk.END, file_path.name)
                
        except Exception as e:
            logger.error(f"Error refreshing file list: {e}")
    
    def safe_open_file(self):
        """Safely open selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a file")
            return
        
        file_path = self.downloaded_files[selection[0]]
        
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                os.system(f"open '{file_path}'")
            else:
                os.system(f"xdg-open '{file_path}'")
        except Exception as e:
            error_handler.show_operation_error("open_file", str(e))
    
    def safe_open_folder(self):
        """Safely open download folder"""
        download_dir = Path(self.download_dir_var.get())
        download_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if sys.platform == "win32":
                os.startfile(str(download_dir))
            elif sys.platform == "darwin":
                os.system(f"open '{download_dir}'")
            else:
                os.system(f"xdg-open '{download_dir}'")
        except Exception as e:
            error_handler.show_operation_error("open_folder", str(e))
    
    def safe_convert_file(self):
        """Safely convert selected file"""
        if not self.ffmpeg_available:
            self.prompt_ffmpeg_install()
            return
        
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a file to convert")
            return
        
        file_path = self.downloaded_files[selection[0]]
        
        # Run conversion in thread
        self.thread_pool.submit(self.convert_video, file_path)






    
    def auto_convert_file(self, file_path):
        """Auto-convert file after download"""
        if self.ffmpeg_available:
            file_ext = Path(file_path).suffix.lower()
            if file_ext in ['.mov', '.avi', '.mkv']:
                self.update_status("Auto-converting to MP4...")
                
                self.thread_pool.submit(self.convert_video, file_path)





    
    def convert_video(self, input_path):
        """Convert video file using FFmpeg"""
        try:
            self.converting = True
            self.update_status("Starting conversion...")
            
            input_path = Path(input_path)
            output_format = self.format_var.get()
            output_path = input_path.parent / f"{input_path.stem}_converted.{output_format}"
            
            # FFmpeg command
            quality_preset = {
                'high': 'slow',
                'medium': 'medium', 
                'low': 'fast'
            }[self.quality_var.get()]
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libx264', '-preset', quality_preset,
                '-c:a', 'aac', '-movflags', '+faststart',
                '-y', str(output_path)
            ]
            
            import subprocess
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True)
            
            # Monitor conversion progress
            for line in process.stdout:
                if 'time=' in line:
                    # Extract time information for progress (simplified)
                    pass
            
            process.wait()
            
            if process.returncode == 0:
                self.update_status(f"Conversion completed: {output_path.name}")
                self.root.after(0, self.safe_refresh_file_list)
            else:
                raise Exception("FFmpeg conversion failed")
                
        except Exception as e:
            error_msg = f"Conversion failed: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        finally:
            self.converting = False
    
    def safe_delete_file(self):
        """Safely delete selected file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Selection Required", "Please select a file")
            return
        
        file_path = Path(self.downloaded_files[selection[0]])
        
        if messagebox.askyesno("Confirm Delete", f"Delete {file_path.name}?"):
            try:
                file_path.unlink()
                self.update_status(f"Deleted: {file_path.name}")
                self.safe_refresh_file_list()
            except Exception as e:
                error_handler.show_operation_error("delete_file", str(e))
    
    def prompt_ffmpeg_install(self):
        """Prompt user to install FFmpeg"""
        message = """FFmpeg is required for video conversion.
        
Would you like to:
1. Download FFmpeg automatically (Recommended)
2. Install manually from ffmpeg.org
3. Continue without conversion"""
        
        result = messagebox.askyesnocancel("FFmpeg Required", message)
        
        if result:  # Yes - auto download
            self.download_ffmpeg()
        elif result is False:  # No - manual install
            self.open_ffmpeg_website()
    
    def download_ffmpeg(self):
        """Download and install FFmpeg"""
        self.update_status("Downloading FFmpeg...")
        messagebox.showinfo("Coming Soon", "Auto-download feature coming soon. Please install FFmpeg manually from ffmpeg.org")
    
    def open_ffmpeg_website(self):
        """Open FFmpeg download page"""
        try:
            import webbrowser
            webbrowser.open("https://ffmpeg.org/download.html")
        except Exception as e:
            messagebox.showerror("Browser Error", "Please visit https://ffmpeg.org to download FFmpeg")
    
    def update_status(self, message):
        """Update status message"""
        logger.info(message)
        self.root.after(0, lambda: self.status_var.set(message))
    
    def on_closing(self):
        """Handle application closing safely"""
        try:
            self.thread_pool.shutdown(wait=False)
            self.root.destroy()
            logger.info("Application closed successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            self.root.destroy()

def main():
    """Main application entry point with comprehensive error handling"""
    try:
        # Import tkinter at the top of main function
        import tkinter as tk
        from tkinter import messagebox
        
        # Create and run application
        root = tk.Tk()
        app = DeepIntelVideoSuite(root)
        
        # Handle window closing
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start application
        logger.info("Starting DeepIntel Video Suite")
        root.mainloop()
        
    except Exception as e:
        # This should be caught by our global exception handler
        logger.critical(f"Application failed to start: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {e}")

if __name__ == "__main__":
    main()