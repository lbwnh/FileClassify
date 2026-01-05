"""
文本解析器实现。

本模块提供文本文件解析功能。
"""

from .base import BaseParser
from typing import Dict


class TextParser(BaseParser):
    """
    纯文本文件解析器（TXT, MD, 代码文件）。

    处理各种文本编码。
    """
    
    def extract_text(self) -> str:
        """
        从文本文件中提取文本内容。

        返回:
            str: 提取的文本内容
        """
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'gbk']
        
        for encoding in encodings:
            try:
                with open(self.file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception as e:
                return f"[文本解析器] 读取文件出错：{str(e)}\n文件：{self.file_path.name}"
        
        return f"[文本解析器] 无法使用常见编码解码文件。\n文件：{self.file_path.name}"
    
    def extract_metadata(self) -> Dict[str, any]:
        """
        从文本文件中提取元数据。

        返回:
            dict: 文本文件元数据
        """
        metadata = {
            'encoding': None,
            'line_count': 0,
            'word_count': 0,
            'char_count': 0
        }
        
        try:
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'gbk']
            
            for encoding in encodings:
                try:
                    with open(self.file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        
                        metadata['encoding'] = encoding
                        metadata['line_count'] = content.count('\n') + 1
                        metadata['word_count'] = len(content.split())
                        metadata['char_count'] = len(content)
                        
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
        
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
