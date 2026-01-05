"""
本地 Llama LLM 实现。

本模块提供与 llama-cpp-python 的集成，用于本地 LLM 推理。
"""

import json
import re
from typing import Dict, List, Optional
from .base import BaseLLM


class LocalLlamaLLM(BaseLLM):
    """
    使用 llama-cpp-python 进行本地推理的 LLM 实现。

    支持 GGUF 模型文件，提供高效的 CPU/GPU 推理。
    """
    
    def __init__(self, model_path: str, n_ctx: int = 2048, n_gpu_layers: int = 0, **kwargs):
        """
        初始化本地 Llama LLM。

        参数:
            model_path: GGUF 模型文件路径
            n_ctx: 上下文窗口大小（默认：2048）
            n_gpu_layers: 卸载到 GPU 的层数（默认：0 表示仅 CPU）
            **kwargs: 额外的 llama-cpp-python 参数
        """
        super().__init__(model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, **kwargs)
        
        self.llm = None
        self._load_model()
    
    def _load_model(self):
        """加载 llama 模型。"""
        try:
            from llama_cpp import Llama
            
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.config.get('n_ctx', 2048),
                n_gpu_layers=self.config.get('n_gpu_layers', 0),
                verbose=self.config.get('verbose', False)
            )
        
        except ImportError:
            raise ImportError(
                "llama-cpp-python 未安装。 "
                "使用 pip install llama-cpp-python 安装"
            )
        
        except Exception as e:
            raise RuntimeError(f"模型加载失败：{str(e)}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        基于给定提示生成文本。

        参数:
            prompt: 用户提示/查询
            system_prompt: 可选的系统提示用于上下文
            **kwargs: 额外的生成参数

        返回:
            str: 生成的文本响应
        """
        if not self.llm:
            raise RuntimeError("模型未加载")
        
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 512),
                top_p=kwargs.get('top_p', 0.95),
                stop=kwargs.get('stop', None)
            )
            
            return response['choices'][0]['message']['content']
        
        except Exception as e:
            raise RuntimeError(f"生成失败：{str(e)}")
    
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
        options_str = ', '.join(options)
        
        classification_prompt = f"""将以下文本分类到以下类别之一：{options_str}

文本：{text}

您必须只响应一个选项，不要添加任何解释或额外文本。

类别："""
        
        response = self.generate(
            prompt=classification_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=50
        )
        
        response_clean = response.strip()
        
        for option in options:
            if option.lower() in response_clean.lower():
                return option
        
        return options[0]
    
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
        json_prompt = f"""{prompt}

您必须只响应有效的 JSON，不要在 JSON 对象外添加任何解释或额外文本。

JSON："""
        
        response = self.generate(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=512
        )
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"响应中的 JSON 无效：{str(e)}")
        
        raise ValueError("响应中没有找到 JSON 对象")
    
    def is_available(self) -> bool:
        """
        检查 LLM 是否可用并准备就绪。

        返回:
            bool: 如果 LLM 准备就绪则为 True，否则为 False
        """
        return self.llm is not None
    
    def get_model_info(self) -> Dict[str, any]:
        """
        获取已加载模型的信息。

        返回:
            dict: 模型信息
        """
        info = super().get_model_info()
        
        if self.llm:
            info['status'] = 'loaded'
            info['context_size'] = self.config.get('n_ctx', 2048)
            info['gpu_layers'] = self.config.get('n_gpu_layers', 0)
        else:
            info['status'] = 'not_loaded'
        
        return info
