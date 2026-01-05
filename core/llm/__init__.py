"""
LLM Abstraction Layer.

This module provides a plugin-based architecture for different LLM backends.
"""

from .base import BaseLLM
from .local_llama import LocalLlamaLLM


__all__ = ['BaseLLM', 'LocalLlamaLLM']
