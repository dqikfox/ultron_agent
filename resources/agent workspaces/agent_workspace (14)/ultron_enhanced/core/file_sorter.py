"""
ULTRON File System AI Sorting - Intelligent File Classification and Organization
Implements AI-based file sorting strategies from the developer guide.
"""

import os
import shutil
import hashlib
import mimetypes
import threading
import time
import logging
import json
import magic
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import asyncio

try:
    import textract
    TEXTRACT_AVAILABLE = True
except ImportError:
    TEXTRACT_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.linear_model import LogisticRegression
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("Scikit-learn not available for ML classification")

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class FileSorter:
    """Intelligent file sorting system with AI classification"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger("FileSorter")
        
        # Base directories
        self.source_dir = Path("D:/ULTRON/Downloads")  # Default monitoring directory
        self.target_base = Path("D:/ULTRON/Sorted")
        self.quarantine_dir = Path("D:/ULTRON/Quarantine")
        
        # Create directories
        self.target_base.mkdir(exist_ok=True)
        self.quarantine_dir.mkdir(exist_ok=True)
        
        # File classification
        self.categories = {
            "Documents": {
                "path": self.target_base / "Documents",
                "subcategories": ["PDFs", "Word", "Excel", "Text", "Presentations"]
            },
            "Media": {
                "path": self.target_base / "Media",
                "subcategories": ["Images", "Videos", "Audio"]
            },
            "Archives": {
                "path": self.target_base / "Archives",
                "subcategories": ["ZIP", "RAR", "7Z", "TAR"]
            },
            "Code": {
                "path": self.target_base / "Code",
                "subcategories": ["Python", "JavaScript", "HTML", "Other"]
            },
            "Executables": {
                "path": self.target_base / "Executables",
                "subcategories": ["Installers", "Programs", "Scripts"]
            },
            "Temporary": {
                "path": self.target_base / "Temporary",
                "subcategories": ["Cache", "Logs", "Temp"]
            },
            "Unknown": {
                "path": self.target_base / "Unknown",
                "subcategories": []
            }
        }
        
        # Create category directories
        for category, info in self.categories.items():
            info["path"].mkdir(exist_ok=True)
            for subcat in info["subcategories"]:
                (info["path"] / subcat).mkdir(exist_ok=True)
        
        # File classification rules
        self.extension_rules = {
            # Documents
            '.pdf': ('Documents', 'PDFs'),
            '.doc': ('Documents', 'Word'),
            '.docx': ('Documents', 'Word'),
            '.xls': ('Documents', 'Excel'),
            '.xlsx': ('Documents', 'Excel'),
            '.ppt': ('Documents', 'Presentations'),
            '.pptx': ('Documents', 'Presentations'),
            '.txt': ('Documents', 'Text'),
            '.rtf': ('Documents', 'Text'),
            '.odt': ('Documents', 'Text'),
            
            # Media
            '.jpg': ('Media', 'Images'),
            '.jpeg': ('Media', 'Images'),
            '.png': ('Media', 'Images'),
            '.gif': ('Media', 'Images'),
            '.bmp': ('Media', 'Images'),
            '.svg': ('Media', 'Images'),
            '.mp4': ('Media', 'Videos'),
            '.avi': ('Media', 'Videos'),
            '.mkv': ('Media', 'Videos'),
            '.mov': ('Media', 'Videos'),
            '.wmv': ('Media', 'Videos'),
            '.mp3': ('Media', 'Audio'),
            '.wav': ('Media', 'Audio'),
            '.flac': ('Media', 'Audio'),
            '.m4a': ('Media', 'Audio'),
            
            # Archives
            '.zip': ('Archives', 'ZIP'),
            '.rar': ('Archives', 'RAR'),
            '.7z': ('Archives', '7Z'),
            '.tar': ('Archives', 'TAR'),
            '.gz': ('Archives', 'TAR'),
            '.bz2': ('Archives', 'TAR'),
            
            # Code
            '.py': ('Code', 'Python'),
            '.js': ('Code', 'JavaScript'),
            '.html': ('Code', 'HTML'),
            '.htm': ('Code', 'HTML'),
            '.css': ('Code', 'HTML'),
            '.php': ('Code', 'Other'),
            '.cpp': ('Code', 'Other'),
            '.c': ('Code', 'Other'),
            '.java': ('Code', 'Other'),
            '.cs': ('Code', 'Other'),
            
            # Executables
            '.exe': ('Executables', 'Programs'),
            '.msi': ('Executables', 'Installers'),
            '.app': ('Executables', 'Programs'),
            '.deb': ('Executables', 'Installers'),
            '.rpm': ('Executables', 'Installers'),
            '.bat': ('Executables', 'Scripts'),
            '.sh': ('Executables', 'Scripts'),
            
            # Temporary
            '.tmp': ('Temporary', 'Temp'),
            '.temp': ('Temporary', 'Temp'),
            '.log': ('Temporary', 'Logs'),
            '.cache': ('Temporary', 'Cache')
        }
        
        # Machine learning components
        self.text_classifier = None
        self.vectorizer = None
        self.file_hash_cache = {}
        
        # Statistics
        self.sort_stats = {
            'files_processed': 0,
            'files_moved': 0,
            'duplicates_found': 0,
            'errors': 0,
            'malware_detected': 0
        }
        
        # Monitoring
        self.monitoring = False
        self.monitor_thread = None
        
        # Initialize ML components
        if SKLEARN_AVAILABLE:
            self._initialize_ml_classifier()
        
        self.logger.info("File sorter initialized")
    
    def _initialize_ml_classifier(self):
        """Initialize machine learning classifier for text files"""
        try:
            # Simple classifier to distinguish code vs documents
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.text_classifier = LogisticRegression()
            
            # Training data (simplified)
            training_texts = [
                # Code samples
                "def function(): import os class MyClass: if __name__ == '__main__':",
                "function myFunction() { var x = 0; return x; } console.log();",
                "<?php echo 'hello'; $variable = array(); foreach($arr as $item) ?>",
                "#include <stdio.h> int main() { printf('hello'); return 0; }",
                
                # Document samples  
                "The quick brown fox jumps over the lazy dog. This is a sample document.",
                "Meeting notes: Today we discussed the quarterly results and future plans.",
                "Recipe for chocolate cake: Mix flour, sugar, eggs and bake for 30 minutes.",
                "Dear Sir/Madam, I am writing to inquire about your services. Regards,"
            ]
            
            training_labels = [0, 0, 0, 0, 1, 1, 1, 1]  # 0=code, 1=document
            
            # Train the classifier
            X = self.vectorizer.fit_transform(training_texts)
            self.text_classifier.fit(X, training_labels)
            
            self.logger.info("ML text classifier initialized")
            
        except Exception as e:
            self.logger.error(f"ML classifier initialization failed: {e}")
            self.text_classifier = None
    
    async def start_monitoring(self, directory: Optional[Path] = None):
        """Start monitoring directory for new files"""
        if self.monitoring:
            return
        
        monitor_dir = directory or self.source_dir
        monitor_dir.mkdir(exist_ok=True)
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_directory, 
            args=(monitor_dir,), 
            daemon=True
        )
        self.monitor_thread.start()
        
        self.logger.info(f"Started monitoring: {monitor_dir}")
    
    def stop_monitoring(self):
        """Stop directory monitoring"""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
        self.logger.info("Stopped directory monitoring")
    
    def _monitor_directory(self, directory: Path):
        """Monitor directory for file changes"""
        processed_files = set()
        
        while self.monitoring:
            try:
                # Scan for new files
                current_files = set()
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        current_files.add(file_path)
                
                # Find new files
                new_files = current_files - processed_files
                
                # Process new files
                for file_path in new_files:
                    try:
                        asyncio.run(self.classify_and_move_file(file_path))
                        processed_files.add(file_path)
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Directory monitoring error: {e}")
                time.sleep(10)
    
    async def sort_directory(self, directory: Optional[Path] = None):
        """Sort all files in a directory"""
        try:
            sort_dir = directory or self.source_dir
            if not sort_dir.exists():
                return {"success": False, "error": "Directory does not exist"}
            
            files_processed = 0
            errors = 0
            
            self.logger.info(f"Starting directory sort: {sort_dir}")
            
            # Process all files
            for file_path in sort_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        await self.classify_and_move_file(file_path)
                        files_processed += 1
                    except Exception as e:
                        self.logger.error(f"Error sorting {file_path}: {e}")
                        errors += 1
            
            self.logger.info(f"Directory sort completed: {files_processed} files, {errors} errors")
            
            return {
                "success": True,
                "files_processed": files_processed,
                "errors": errors,
                "stats": self.sort_stats
            }
            
        except Exception as e:
            self.logger.error(f"Directory sort error: {e}")
            return {"success": False, "error": str(e)}
    
    async def classify_and_move_file(self, file_path: Path):
        """Classify and move a single file"""
        try:
            # Skip if file is too large (> 1GB)
            if file_path.stat().st_size > 1024 * 1024 * 1024:
                self.logger.warning(f"Skipping large file: {file_path}")
                return
            
            # Check for duplicates
            if await self._is_duplicate(file_path):
                self.logger.info(f"Duplicate file found: {file_path}")
                self.sort_stats['duplicates_found'] += 1
                return
            
            # Malware scanning
            if await self._scan_for_malware(file_path):
                await self._quarantine_file(file_path, "Potential malware detected")
                self.sort_stats['malware_detected'] += 1
                return
            
            # Classify file
            category, subcategory = await self._classify_file(file_path)
            
            # Move file
            await self._move_file(file_path, category, subcategory)
            
            self.sort_stats['files_processed'] += 1
            self.sort_stats['files_moved'] += 1
            
            self.logger.info(f"Moved {file_path.name} to {category}/{subcategory}")
            
        except Exception as e:
            self.logger.error(f"File classification error for {file_path}: {e}")
            self.sort_stats['errors'] += 1
    
    async def _classify_file(self, file_path: Path) -> Tuple[str, str]:
        """Classify file into category and subcategory"""
        try:
            # Get file extension
            extension = file_path.suffix.lower()
            
            # Check extension rules first
            if extension in self.extension_rules:
                category, subcategory = self.extension_rules[extension]
                
                # Additional content-based classification for ambiguous files
                if extension in ['.txt', '.log'] and TEXTRACT_AVAILABLE:
                    content_category = await self._classify_by_content(file_path)
                    if content_category:
                        return content_category
                
                return category, subcategory
            
            # Fallback to MIME type detection
            mime_type = self._get_mime_type(file_path)
            category, subcategory = self._classify_by_mime_type(mime_type)
            
            # Content-based classification for unknown files
            if category == "Unknown" and file_path.stat().st_size < 10 * 1024 * 1024:  # < 10MB
                content_category = await self._classify_by_content(file_path)
                if content_category:
                    return content_category
            
            return category, subcategory
            
        except Exception as e:
            self.logger.error(f"Classification error for {file_path}: {e}")
            return "Unknown", ""
    
    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type of file"""
        try:
            # Try python-magic first
            mime_type = magic.from_file(str(file_path), mime=True)
            return mime_type
        except:
            # Fallback to mimetypes
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or "application/octet-stream"
    
    def _classify_by_mime_type(self, mime_type: str) -> Tuple[str, str]:
        """Classify file by MIME type"""
        if mime_type.startswith('text/'):
            return "Documents", "Text"
        elif mime_type.startswith('image/'):
            return "Media", "Images"
        elif mime_type.startswith('video/'):
            return "Media", "Videos"
        elif mime_type.startswith('audio/'):
            return "Media", "Audio"
        elif 'pdf' in mime_type:
            return "Documents", "PDFs"
        elif 'msword' in mime_type or 'officedocument' in mime_type:
            return "Documents", "Word"
        elif 'zip' in mime_type or 'compressed' in mime_type:
            return "Archives", "ZIP"
        elif 'executable' in mime_type:
            return "Executables", "Programs"
        else:
            return "Unknown", ""
    
    async def _classify_by_content(self, file_path: Path) -> Optional[Tuple[str, str]]:
        """Classify file by analyzing content"""
        try:
            # Read file content
            if file_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                return None
            
            # Try to read as text
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except:
                # Try binary read for specific formats
                if TEXTRACT_AVAILABLE:
                    try:
                        content = textract.process(str(file_path)).decode('utf-8', errors='ignore')
                    except:
                        return None
                else:
                    return None
            
            if not content or len(content) < 50:
                return None
            
            # Use ML classifier if available
            if self.text_classifier and self.vectorizer:
                prediction = self._predict_text_type(content)
                if prediction == 0:  # Code
                    return self._classify_code_by_content(content, file_path)
                else:  # Document
                    return "Documents", "Text"
            
            # Rule-based classification
            return self._classify_by_content_rules(content, file_path)
            
        except Exception as e:
            self.logger.error(f"Content classification error for {file_path}: {e}")
            return None
    
    def _predict_text_type(self, content: str) -> int:
        """Predict if content is code (0) or document (1)"""
        try:
            X = self.vectorizer.transform([content])
            prediction = self.text_classifier.predict(X)[0]
            return prediction
        except Exception as e:
            self.logger.error(f"Text prediction error: {e}")
            return 1  # Default to document
    
    def _classify_code_by_content(self, content: str, file_path: Path) -> Tuple[str, str]:
        """Classify code files by content analysis"""
        content_lower = content.lower()
        
        # Python indicators
        if any(keyword in content_lower for keyword in ['def ', 'import ', 'class ', 'if __name__']):
            return "Code", "Python"
        
        # JavaScript indicators
        if any(keyword in content_lower for keyword in ['function', 'var ', 'let ', 'const ', 'console.log']):
            return "Code", "JavaScript"
        
        # HTML indicators
        if any(keyword in content_lower for keyword in ['<html>', '<body>', '<div>', '<script>']):
            return "Code", "HTML"
        
        # SQL indicators
        if any(keyword in content_lower for keyword in ['select ', 'from ', 'where ', 'insert ']):
            return "Code", "Other"
        
        return "Code", "Other"
    
    def _classify_by_content_rules(self, content: str, file_path: Path) -> Tuple[str, str]:
        """Rule-based content classification"""
        content_lower = content.lower()
        
        # Programming language detection
        code_indicators = [
            'function', 'class', 'import', 'include', 'def ', 'var ', 'let ', 'const',
            'if (', 'for (', 'while (', 'switch (', 'try {', 'catch {',
            '#!/bin/', '<?php', '<%', 'SELECT', 'INSERT', 'UPDATE'
        ]
        
        if any(indicator in content_lower for indicator in code_indicators):
            return self._classify_code_by_content(content, file_path)
        
        # Log file detection
        log_indicators = ['error', 'warning', 'info', 'debug', 'timestamp', 'log level']
        if any(indicator in content_lower for indicator in log_indicators):
            return "Temporary", "Logs"
        
        # Configuration file detection
        config_indicators = ['[settings]', '[config]', 'configuration', '=', 'key=value']
        if any(indicator in content_lower for indicator in config_indicators):
            return "Documents", "Text"
        
        # Default to document
        return "Documents", "Text"
    
    async def _is_duplicate(self, file_path: Path) -> bool:
        """Check if file is a duplicate"""
        try:
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_path)
            
            # Check if hash exists in cache
            if file_hash in self.file_hash_cache:
                existing_file = self.file_hash_cache[file_hash]
                if existing_file.exists() and existing_file != file_path:
                    return True
            
            # Add to cache
            self.file_hash_cache[file_hash] = file_path
            return False
            
        except Exception as e:
            self.logger.error(f"Duplicate check error for {file_path}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    async def _scan_for_malware(self, file_path: Path) -> bool:
        """Basic malware scanning"""
        try:
            # Simple heuristic checks
            extension = file_path.suffix.lower()
            file_size = file_path.stat().st_size
            
            # Suspicious extensions
            suspicious_extensions = ['.scr', '.pif', '.vbs', '.bat', '.cmd', '.com']
            if extension in suspicious_extensions:
                return True
            
            # Suspicious file names
            suspicious_names = ['autorun.inf', 'desktop.ini', 'thumbs.db']
            if file_path.name.lower() in suspicious_names:
                return True
            
            # Check for executable with fake extension
            if extension in ['.pdf', '.doc', '.jpg'] and file_size > 0:
                try:
                    # Read first few bytes to check for PE header
                    with open(file_path, 'rb') as f:
                        header = f.read(2)
                        if header == b'MZ':  # PE executable header
                            return True
                except:
                    pass
            
            # TODO: Integrate with real antivirus engine (ClamAV, etc.)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Malware scan error for {file_path}: {e}")
            return False
    
    async def _quarantine_file(self, file_path: Path, reason: str):
        """Move file to quarantine"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_name = f"{timestamp}_{file_path.name}"
            quarantine_path = self.quarantine_dir / quarantine_name
            
            shutil.move(str(file_path), str(quarantine_path))
            
            # Log quarantine action
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "original_file": str(file_path),
                "quarantine_file": str(quarantine_path),
                "reason": reason
            }
            
            log_file = self.quarantine_dir / "quarantine_log.json"
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            self.logger.warning(f"File quarantined: {file_path} -> {quarantine_path} ({reason})")
            
        except Exception as e:
            self.logger.error(f"Quarantine error for {file_path}: {e}")
    
    async def _move_file(self, file_path: Path, category: str, subcategory: str):
        """Move file to appropriate category folder"""
        try:
            # Determine target directory
            target_dir = self.categories[category]["path"]
            if subcategory:
                target_dir = target_dir / subcategory
            
            target_dir.mkdir(exist_ok=True)
            
            # Handle filename conflicts
            target_path = target_dir / file_path.name
            counter = 1
            while target_path.exists():
                name_parts = file_path.stem, counter, file_path.suffix
                target_path = target_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                counter += 1
            
            # Move file
            shutil.move(str(file_path), str(target_path))
            
            # Log the move
            self._log_file_move(file_path, target_path, category, subcategory)
            
        except Exception as e:
            self.logger.error(f"File move error: {file_path} -> {category}/{subcategory}: {e}")
            raise
    
    def _log_file_move(self, source: Path, target: Path, category: str, subcategory: str):
        """Log file movement"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "source": str(source),
                "target": str(target),
                "category": category,
                "subcategory": subcategory,
                "file_size": target.stat().st_size
            }
            
            log_file = self.target_base / "sort_log.json"
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        except Exception as e:
            self.logger.error(f"Move logging error: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sorting statistics"""
        # Count files in each category
        category_counts = {}
        total_files = 0
        
        for category, info in self.categories.items():
            count = 0
            if info["path"].exists():
                for file_path in info["path"].rglob("*"):
                    if file_path.is_file():
                        count += 1
                        total_files += 1
            category_counts[category] = count
        
        return {
            "monitoring_active": self.monitoring,
            "total_files_sorted": total_files,
            "category_counts": category_counts,
            "processing_stats": self.sort_stats,
            "quarantine_files": len(list(self.quarantine_dir.glob("*"))) if self.quarantine_dir.exists() else 0,
            "ml_classifier_available": self.text_classifier is not None,
            "cache_size": len(self.file_hash_cache)
        }
    
    async def restore_from_quarantine(self, quarantine_file: str) -> bool:
        """Restore file from quarantine"""
        try:
            quarantine_path = self.quarantine_dir / quarantine_file
            if not quarantine_path.exists():
                return False
            
            # Move back to source directory
            restore_path = self.source_dir / quarantine_file.split("_", 1)[1]  # Remove timestamp
            shutil.move(str(quarantine_path), str(restore_path))
            
            self.logger.info(f"Restored from quarantine: {quarantine_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Quarantine restore error: {e}")
            return False
