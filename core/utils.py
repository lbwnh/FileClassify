import os
import re
from pathlib import Path


def parse_rule_string(rule_string):
    """
    解析规则字符串以提取字段键和可选的枚举约束。
    
    参数:
        rule_string: 带有 '>>' 分隔符和可选枚举约束的规则字符串
                    示例: "Category [Contract, Invoice] >> Year"
    
    返回:
        list: 包含 'key' 和 'options' 字段的字典列表
              示例: [{'key': 'category', 'options': ['Contract', 'Invoice']},
                       {'key': 'year', 'options': None}]
    
    示例:
        >>> parse_rule_string("类型 [合同, 发票] >> 年份")
        [{'key': 'category', 'options': ['合同', '发票']}, {'key': 'year', 'options': None}]
    """
    if not rule_string or not rule_string.strip():
        return []
    
    field_mapping = {
        '类型': 'category',
        'category': 'category',
        '年份': 'year',
        'year': 'year',
        '月份': 'month',
        'month': 'month',
        '原文件名': 'original_name',
        'original name': 'original_name',
        '摘要': 'summary',
        'summary': 'summary'
    }
    
    parts = [part.strip() for part in rule_string.split('>>')]
    parsed_rules = []
    
    pattern = r'^([^\[]+)(?:\s*\[([^\]]+)\])?$'
    
    for part in parts:
        match = re.match(pattern, part.strip())
        
        if match:
            field_name = match.group(1).strip()
            options_str = match.group(2)
            
            field_key = field_mapping.get(field_name.lower(), field_name.lower())
            
            options = None
            if options_str:
                options = [opt.strip() for opt in re.split(r'[,，]', options_str) if opt.strip()]
            
            parsed_rules.append({
                'key': field_key,
                'options': options
            })
        else:
            field_key = field_mapping.get(part.lower(), part.lower())
            parsed_rules.append({
                'key': field_key,
                'options': None
            })
    
    return parsed_rules


def generate_target_path(rule_string, ai_data_dict):
    """
    基于规则字符串和 AI 数据生成目标路径。
    
    参数:
        rule_string: 带有 '>>' 分隔符的规则字符串（例如："类型 >> 年份"）
        ai_data_dict: 包含 AI 提取数据的字典
    
    返回:
        str: 相对路径字符串
    
    示例:
        >>> ai_data = {'category': 'Work', 'year': '2024', 'month': '01'}
        >>> generate_target_path("类型 >> 年份 >> 月份", ai_data)
        'Work/2024/01'
    """
    parsed_rules = parse_rule_string(rule_string)
    
    if not parsed_rules:
        return "Unknown"
    
    path_parts = []
    
    for rule in parsed_rules:
        field_key = rule['key']
        
        if field_key in ai_data_dict:
            value = ai_data_dict.get(field_key, 'Unknown')
            if value and str(value).strip():
                path_parts.append(str(value).strip())
            else:
                path_parts.append('Unknown')
        else:
            path_parts.append('Unknown')
    
    if not path_parts:
        return "Unknown"
    
    return os.path.join(*path_parts)
