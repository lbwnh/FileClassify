"""
File Parser Plugin System.

This module provides a plugin-based architecture for parsing different file types.
"""

from .base import BaseParser
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .excel_parser import ExcelParser
from .pptx_parser import PPTXParser
from .text_parser import TextParser


class ParserFactory:
    """
    Factory class for creating appropriate parser instances based on file extension.
    """
    
    _parsers = {
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.doc': DOCXParser,
        '.xlsx': ExcelParser,
        '.xls': ExcelParser,
        '.csv': ExcelParser,
        '.pptx': PPTXParser,
        '.ppt': PPTXParser,
        '.txt': TextParser,
        '.md': TextParser,
        '.py': TextParser,
        '.js': TextParser,
        '.java': TextParser,
        '.cpp': TextParser,
        '.c': TextParser,
        '.h': TextParser,
        '.json': TextParser,
        '.xml': TextParser,
        '.html': TextParser,
        '.css': TextParser,
    }
    
    @classmethod
    def get_parser(cls, file_path):
        """
        Get appropriate parser for the given file.
        
        Args:
            file_path: Path to the file (str or Path object)
        
        Returns:
            BaseParser: Instance of appropriate parser
        
        Raises:
            ValueError: If file extension is not supported
        
        Example:
            >>> parser = ParserFactory.get_parser("document.pdf")
            >>> content = parser.extract_text()
        """
        from pathlib import Path
        
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        parser_class = cls._parsers.get(extension)
        
        if parser_class is None:
            raise ValueError(f"No parser available for file extension: {extension}")
        
        return parser_class(file_path)
    
    @classmethod
    def register_parser(cls, extension, parser_class):
        """
        Register a new parser for a file extension.
        
        Args:
            extension: File extension (e.g., '.pdf')
            parser_class: Parser class (must inherit from BaseParser)
        
        Example:
            >>> class CustomParser(BaseParser):
            ...     pass
            >>> ParserFactory.register_parser('.custom', CustomParser)
        """
        if not issubclass(parser_class, BaseParser):
            raise TypeError("Parser class must inherit from BaseParser")
        
        cls._parsers[extension.lower()] = parser_class
    
    @classmethod
    def get_supported_extensions(cls):
        """
        Get list of supported file extensions.
        
        Returns:
            list: List of supported extensions
        """
        return list(cls._parsers.keys())


__all__ = [
    'BaseParser',
    'PDFParser',
    'DOCXParser',
    'ExcelParser',
    'PPTXParser',
    'TextParser',
    'ParserFactory'
]
