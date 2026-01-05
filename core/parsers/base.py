"""\n文件解析器抽象基类。\n\n本模块定义了所有文件解析器必须实现的接口。\n"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class BaseParser(ABC):
    """\n    文件解析器抽象基类。\n    \n    所有解析器实现都必须继承此类并实现必需的抽象方法。\n    """
    
    def __init__(self, file_path):
        """\n        使用文件路径初始化解析器。\n        \n        参数:\n            file_path: 要解析的文件路径（字符串或 Path 对象）\n        """
        self.file_path = Path(file_path)
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件未找到: {self.file_path}")
    
    @abstractmethod
    def extract_text(self) -> str:
        """\n        从文件中提取文本内容。\n        \n        返回:\n            str: 提取的文本内容\n        \n        异常:\n            Exception: 如果提取失败\n        """
        pass
    
    @abstractmethod
    def extract_metadata(self) -> Dict[str, any]:
        """\n        从文件中提取元数据。\n        \n        返回:\n            dict: 元数据字典，包含以下键：\n                  - title: 文档标题\n                  - author: 文档作者\n                  - created_date: 创建日期\n                  - modified_date: 最后修改日期\n                  - page_count: 页数（如果适用）\n                  - word_count: 字数（如果适用）\n        """
        pass
    
    def get_file_info(self) -> Dict[str, any]:
        """\n        获取基本文件信息。\n        \n        返回:\n            dict: 文件信息，包括名称、大小、扩展名等\n        """
        stat = self.file_path.stat()
        
        return {
            'name': self.file_path.name,
            'stem': self.file_path.stem,
            'extension': self.file_path.suffix,
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'path': str(self.file_path.absolute())
        }
    
    def extract_summary(self, max_length: int = 500) -> str:
        """\n        提取文件内容摘要。\n        \n        参数:\n            max_length: 摘要的最大长度\n        \n        返回:\n            str: 摘要文本（必要时截断）\n        """
        text = self.extract_text()
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length] + "..."
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.file_path.name}')"
