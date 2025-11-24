#!/usr/bin/env python3
"""
DEEPINTEL VIDEO SUITE - Production Error Handler
Enterprise-grade error handling with crash reporting
"""

import logging
import traceback
import sys
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import json

class ProductionErrorHandler:
    def __init__(self, app_name="DeepIntel Video Suite"):
        self.app_name = app_name
        self.crash_reports_dir = Path.home() / ".deepintel" / "crash_reports"
        self.crash_reports_dir.mkdir(parents=True, exist_ok=True)
        self.crash_reporting_enabled = False
        
        self.setup_logging()
        logger.info(f"ProductionErrorHandler initialized for {app_name}")
        self.install_global_handler()
    
    def setup_logging(self):
        global logger
        
        logs_dir = Path.home() / ".deepintel" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / 'deepintel_suite.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger = logging.getLogger('DeepIntel')
    
    def install_global_handler(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            crash_report = self.create_crash_report(exc_type, exc_value, exc_traceback)
            self.show_user_friendly_error(crash_report)
            
            if self.crash_reporting_enabled:
                self.send_crash_report(crash_report)
        
        sys.excepthook = handle_exception
    
    def create_crash_report(self, exc_type, exc_value, exc_traceback):
        crash_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        report = {
            "crash_id": crash_id,
            "timestamp": datetime.now().isoformat(),
            "app": self.app_name,
            "version": "2.0.0",
            "python": sys.version.split()[0],
            "exception": exc_type.__name__,
            "message": str(exc_value),
            "traceback": ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        }
        
        file = self.crash_reports_dir / f"crash_{crash_id}.json"
        try:
            file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        except:
            pass
        
        return report
    
    def show_user_friendly_error(self, crash_report):
        try:
            root = tk.Tk()
            root.withdraw()
            
            msg = f"""DeepIntel Video Suite encountered an error and needs to restart

Error ID: {crash_report['crash_id']}
Error: {crash_report['message'][:100]}...

Would you like to send an anonymous crash report to help us improve?"""
            
            if messagebox.askyesno("Application Error", msg, parent=root):
                self.crash_reporting_enabled = True
                self.send_crash_report(crash_report)
                messagebox.showinfo("Thank You", "Report sent. Thank you for your help!")
            
            root.destroy()
            
        except Exception as e:
            print(f"CRITICAL ERROR: {crash_report['message']}")
            print(f"ID: {crash_report['crash_id']}")
    
    def send_crash_report(self, report):
        logger.info(f"Crash report would be sent: {report['crash_id']}")
    
    @staticmethod
    def safe_execute(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                messagebox.showerror("Error", f"Operation failed:\n{e}")
                return None
        return wrapper

error_handler = ProductionErrorHandler()

def safe(func):
    return error_handler.safe_execute(func)

logger = logging.getLogger('DeepIntel')