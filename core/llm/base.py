"""
LLM 实现的抽象基类。

本模块定义了所有 LLM 实现必须遵循的接口。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseLLM(ABC):
    """
    大语言模型实现的抽象基类。

    所有 LLM 适配器都必须继承此类并实现必需的抽象方法。
    """
    
    def __init__(self, model_path: Optional[str] = None, **kwargs):
        """
        初始化 LLM。

        参数:
            model_path: 模型文件路径（如果适用）
            **kwargs: 额外的配置参数
        """
        self.model_path = model_path
        self.config = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        基于给定提示生成文本。

        参数:
            prompt: 用户提示/查询
            system_prompt: 可选的系统提示用于上下文
            **kwargs: 额外的生成参数（temperature, max_tokens 等）

        返回:
            str: 生成的文本响应

        异常:
            Exception: 如果生成失败
        """
        pass
    
    @abstractmethod
    def classify(self, text: str, options: List[str], system_prompt: Optional[str] = None) -> str:
        """
        将文本分类到提供的选项之一。

        参数:
            text: 要分类的文本
            options: 可能的分类选项列表
            system_prompt: 可选的系统提示用于上下文

        返回:
            str: 从选项列表中选择的选项
        """
        pass
    
    @abstractmethod
    def extract_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict:
        """
        从文本中提取结构化 JSON 数据。

        参数:
            prompt: 用户提示/查询
            system_prompt: 可选的系统提示用于上下文

        返回:
            dict: 提取的 JSON 数据

        异常:
            ValueError: 如果响应不是有效的 JSON
        """
        pass
    
    def is_available(self) -> bool:
        """
        检查 LLM 是否可用并准备就绪。

        返回:
            bool: 如果 LLM 准备就绪则为 True，否则为 False
        """
        return True
    
    def get_model_info(self) -> Dict[str, any]:
        """
        获取已加载模型的信息。

        返回:
            dict: 模型信息（名称、大小、参数等）
        """
        return {
            'model_path': self.model_path,
            'config': self.config
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(model_path='{self.model_path}')"
