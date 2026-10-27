"""Intelligent file management and sorting"""
import os
import shutil
import hashlib
import logging
from pathlib import Path
from datetime import datetime
import json

class FileManager:
    def __init__(self, config):
        self.config = config['files']
        self.base_dir = Path("managed_files")
        self.base_dir.mkdir(exist_ok=True)
        
        # File categories
        self.categories = {
            "documents": ["pdf", "doc", "docx", "txt", "rtf", "odt"],
            "images": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"],
            "videos": ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"],
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            "archives": ["zip", "rar", "7z", "tar", "gz", "bz2"],
            "code": ["py", "js", "html", "css", "cpp", "java", "c", "php"],
            "executables": ["exe", "msi", "deb", "rpm", "dmg", "app"]
        }
        
        # Create category directories
        for category in self.categories:
            (self.base_dir / category).mkdir(exist_ok=True)
        
        self.available = True
        logging.info("File manager initialized")
    
    def classify_file(self, file_path):
        """Classify file by extension"""
        extension = Path(file_path).suffix.lower().lstrip('.')
        
        for category, extensions in self.categories.items():
            if extension in extensions:
                return category
        
        return "other"
    
    def get_file_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logging.error(f"Hash calculation error: {e}")
            return None
    
    async def auto_sort(self, source_dir=None):
        """Auto-sort files in directory"""
        if source_dir is None:
            source_dir = Path.home() / "Downloads"
        
        source_path = Path(source_dir)
        
        if not source_path.exists():
            return {"error": "Source directory not found", "total": 0}
        
        try:
            sorted_files = {}
            total_files = 0
            duplicates = 0
            errors = 0
            
            for file_path in source_path.iterdir():
                if file_path.is_file():
                    try:
                        # Classify file
                        category = self.classify_file(file_path)
                        
                        # Check for duplicates
                        file_hash = self.get_file_hash(file_path)
                        dest_dir = self.base_dir / category
                        
                        # Create unique filename if needed
                        dest_path = dest_dir / file_path.name
                        counter = 1
                        original_dest = dest_path
                        
                        while dest_path.exists():
                            # Check if it's actually a duplicate
                            existing_hash = self.get_file_hash(dest_path)
                            if existing_hash == file_hash:
                                logging.info(f"Duplicate file skipped: {file_path.name}")
                                duplicates += 1
                                break
                            
                            # Create new name
                            stem = original_dest.stem
                            suffix = original_dest.suffix
                            dest_path = dest_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                        else:
                            # Move file
                            if self.config.get('backup_before_sort', True):
                                backup_dir = self.base_dir / "backup"
                                backup_dir.mkdir(exist_ok=True)
                                shutil.copy2(file_path, backup_dir / file_path.name)
                            
                            shutil.move(str(file_path), str(dest_path))
                            
                            if category not in sorted_files:
                                sorted_files[category] = []
                            sorted_files[category].append(str(dest_path))
                            total_files += 1
                            
                    except Exception as e:
                        logging.error(f"Error sorting file {file_path}: {e}")
                        errors += 1
            
            result = {
                "sorted_files": sorted_files,
                "total": total_files,
                "duplicates": duplicates,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save sorting log
            log_file = self.base_dir / "sort_log.json"
            try:
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        log_data = json.load(f)
                else:
                    log_data = []
                
                log_data.append(result)
                
                with open(log_file, 'w') as f:
                    json.dump(log_data, f, indent=2)
            except Exception as e:
                logging.error(f"Error saving sort log: {e}")
            
            return result
            
        except Exception as e:
            logging.error(f"File sorting error: {e}")
            return {"error": str(e), "total": 0}
    
    def get_statistics(self):
        """Get file management statistics"""
        try:
            stats = {
                "categories": {},
                "total_files": 0,
                "total_size": 0
            }
            
            for category in self.categories:
                category_dir = self.base_dir / category
                if category_dir.exists():
                    files = list(category_dir.iterdir())
                    file_count = len([f for f in files if f.is_file()])
                    
                    category_size = sum(
                        f.stat().st_size for f in files 
                        if f.is_file()
                    )
                    
                    stats["categories"][category] = {
                        "count": file_count,
                        "size": category_size
                    }
                    
                    stats["total_files"] += file_count
                    stats["total_size"] += category_size
            
            return stats
            
        except Exception as e:
            logging.error(f"Statistics error: {e}")
            return {"error": str(e)}
    
    def is_available(self):
        return self.available
