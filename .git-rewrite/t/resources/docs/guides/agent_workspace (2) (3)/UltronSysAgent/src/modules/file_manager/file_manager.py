"""
File Manager for UltronSysAgent
Handles file operations, document processing, and file indexing
"""

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import mimetypes
import hashlib

try:
    import PyPDF2
    import docx
    from PIL import Image
    import pytesseract
    PDF_PROCESSING_AVAILABLE = True
except ImportError:
    PDF_PROCESSING_AVAILABLE = False
    print("⚠️  File processing dependencies not available")

from ...core.event_bus import EventBus, EventTypes
from ...core.logger import command_logger

class FileManager:
    """File management and processing module"""
    
    def __init__(self, config, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # File processing capabilities
        self.supported_formats = {
            'text': ['.txt', '.md', '.log', '.json', '.xml', '.csv'],
            'document': ['.pdf', '.docx', '.doc', '.rtf'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'audio': ['.mp3', '.wav', '.m4a', '.flac'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv']
        }
        
        # File index for quick search
        self.file_index = {}
        
        # Setup event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event bus handlers"""
        self.event_bus.subscribe(EventTypes.FILE_DROPPED, self._handle_file_dropped)
    
    async def start(self):
        """Start the file manager"""
        self.logger.info("📁 Starting File Manager...")
        
        await self.event_bus.publish(EventTypes.MODULE_STARTED, 
                                    {"module": "file_manager"}, 
                                    source="file_manager")
    
    async def stop(self):
        """Stop the file manager"""
        self.logger.info("📁 Stopping File Manager...")
        
        await self.event_bus.publish(EventTypes.MODULE_STOPPED, 
                                    {"module": "file_manager"}, 
                                    source="file_manager")
    
    async def _handle_file_dropped(self, event):
        """Handle file drop events"""
        try:
            file_path = event.data.get('file_path')
            if file_path and os.path.exists(file_path):
                await self.process_file(file_path)
        except Exception as e:
            self.logger.error(f"Error handling file drop: {e}")
    
    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file and extract content"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Get file info
            file_info = self._get_file_info(file_path)
            
            # Extract content based on file type
            content = await self._extract_content(file_path, file_info['type'])
            
            # Store in file index
            self.file_index[str(file_path)] = {
                **file_info,
                'content_preview': content[:500] if content else '',
                'processed_at': asyncio.get_event_loop().time()
            }
            
            # Log file access
            command_logger.log_file_access(str(file_path), "process")
            
            # Publish file processed event
            await self.event_bus.publish(EventTypes.FILE_PROCESSED, 
                                       {
                                           'file_path': str(file_path),
                                           'content': content,
                                           'type': file_info['type'],
                                           'info': file_info
                                       }, 
                                       source="file_manager")
            
            self.logger.info(f"✅ Processed file: {file_path.name}")
            
            return {
                'success': True,
                'content': content,
                'info': file_info
            }
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            
            # Determine file type
            file_type = self._determine_file_type(file_path)
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            return {
                'name': file_path.name,
                'path': str(file_path),
                'size': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'type': file_type,
                'mime_type': mime_type,
                'extension': file_path.suffix.lower(),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_readable': os.access(file_path, os.R_OK),
                'is_writable': os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {'error': str(e)}
    
    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the category of a file"""
        extension = file_path.suffix.lower()
        
        for file_type, extensions in self.supported_formats.items():
            if extension in extensions:
                return file_type
        
        return 'unknown'
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    async def _extract_content(self, file_path: Path, file_type: str) -> str:
        """Extract text content from file based on type"""
        try:
            if file_type == 'text':
                return await self._extract_text_content(file_path)
            elif file_type == 'document':
                return await self._extract_document_content(file_path)
            elif file_type == 'image':
                return await self._extract_image_content(file_path)
            else:
                return f"File type '{file_type}' not supported for content extraction"
                
        except Exception as e:
            self.logger.error(f"Error extracting content from {file_path}: {e}")
            return f"Error extracting content: {e}"
    
    async def _extract_text_content(self, file_path: Path) -> str:
        """Extract content from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Limit content size
            max_size = 10000  # 10KB limit
            if len(content) > max_size:
                content = content[:max_size] + "\n\n... (content truncated)"
            
            return content
            
        except Exception as e:
            return f"Error reading text file: {e}"
    
    async def _extract_document_content(self, file_path: Path) -> str:
        """Extract content from document files"""
        if not PDF_PROCESSING_AVAILABLE:
            return "Document processing dependencies not available"
        
        try:
            extension = file_path.suffix.lower()
            
            if extension == '.pdf':
                return await self._extract_pdf_content(file_path)
            elif extension in ['.docx', '.doc']:
                return await self._extract_docx_content(file_path)
            else:
                return f"Document type {extension} not supported"
                
        except Exception as e:
            return f"Error extracting document content: {e}"
    
    async def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Limit to first 10 pages
                max_pages = min(10, len(pdf_reader.pages))
                
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip() if text.strip() else "No text content found in PDF"
            
        except Exception as e:
            return f"Error extracting PDF content: {e}"
    
    async def _extract_docx_content(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            doc = docx.Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip() if text.strip() else "No text content found in document"
            
        except Exception as e:
            return f"Error extracting DOCX content: {e}"
    
    async def _extract_image_content(self, file_path: Path) -> str:
        """Extract text from images using OCR"""
        try:
            if not PDF_PROCESSING_AVAILABLE:
                return "OCR dependencies not available"
            
            # Open image
            image = Image.open(file_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            if text.strip():
                return f"OCR extracted text:\n{text.strip()}"
            else:
                return "No text found in image"
                
        except Exception as e:
            return f"Error performing OCR: {e}"
    
    async def create_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Create a new file with content"""
        try:
            path = Path(file_path)
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Log file creation
            command_logger.log_file_access(str(path), "create")
            
            self.logger.info(f"✅ Created file: {path}")
            
            return {
                'success': True,
                'message': f"File created: {path}",
                'path': str(path)
            }
            
        except Exception as e:
            self.logger.error(f"Error creating file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy a file to another location"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source file not found: {source}")
            
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Log file operation
            command_logger.log_file_access(f"{source} -> {destination}", "copy")
            
            self.logger.info(f"✅ Copied file: {source} -> {destination}")
            
            return {
                'success': True,
                'message': f"File copied to: {destination}",
                'source': source,
                'destination': destination
            }
            
        except Exception as e:
            self.logger.error(f"Error copying file {source} to {destination}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Remove from index
            if str(path) in self.file_index:
                del self.file_index[str(path)]
            
            # Delete file
            path.unlink()
            
            # Log file deletion
            command_logger.log_file_access(str(path), "delete")
            
            self.logger.info(f"✅ Deleted file: {path}")
            
            return {
                'success': True,
                'message': f"File deleted: {file_path}",
                'path': file_path
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_files(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search files in the index"""
        try:
            results = []
            query_lower = query.lower()
            
            for file_path, info in self.file_index.items():
                # Search in filename and content preview
                if (query_lower in info.get('name', '').lower() or 
                    query_lower in info.get('content_preview', '').lower()):
                    results.append(info)
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get file manager status"""
        return {
            "indexed_files": len(self.file_index),
            "supported_formats": self.supported_formats,
            "processing_available": PDF_PROCESSING_AVAILABLE
        }
