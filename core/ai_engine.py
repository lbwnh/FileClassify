"""
使用 LLM 进行文件分类的 AI 引擎。
"""

SYSTEM_PROMPT = """You are a professional file classification assistant. Your task is to analyze file names and extract structured information.

You must ALWAYS return a valid JSON object with the following fields:
- category: The category/type of the file (e.g., "Work", "Personal", "Study", "Finance", etc.)
- year: The year associated with the file (4-digit format, e.g., "2024")
- month: The month associated with the file (2-digit format, e.g., "01", "12")
- summary: A brief summary or description of the file content
- original_name: The original file name without extension

Rules:
1. If you cannot determine a field, use "Unknown" as the value.
2. For year: Try to extract from file name, if not found, use current year.
3. For month: Try to extract from file name, if not found, use "Unknown".
4. For category: Infer from file name and context. Common categories: Work, Personal, Study, Finance, Photos, Documents, Contract, Report, Invoice, Manual, etc.
5. For Chinese file names, understand the context and extract information accordingly.
   - 工作/会议/报告 → Work
   - 财务/发票/账单 → Finance
   - 合同/协议 → Contract
   - 个人/私人 → Personal
   - 学习/课程 → Study
6. Always return valid JSON format.
7. Field names must be in lowercase English.

Example 1 (Chinese file):
Input: "2024年度财务报告_Q1.pdf"
Output:
{
    "category": "Finance",
    "year": "2024",
    "month": "Unknown",
    "summary": "Q1 Financial Report",
    "original_name": "2024年度财务报告_Q1"
}

Example 2 (English file):
Input: "meeting_notes_2023_12_15.docx"
Output:
{
    "category": "Work",
    "year": "2023",
    "month": "12",
    "summary": "Meeting notes from December 15",
    "original_name": "meeting_notes_2023_12_15"
}

Example 3 (Chinese contract):
Input: "采购合同_2024_03.pdf"
Output:
{
    "category": "Contract",
    "year": "2024",
    "month": "03",
    "summary": "Purchase contract",
    "original_name": "采购合同_2024_03"
}
"""


def get_system_prompt():
    """获取用于 AI 分类的系统提示。
    
    返回:
        str: 系统提示文本
    """
    return SYSTEM_PROMPT


def build_dynamic_prompt(parsed_rules):
    """基于带有枚举约束的解析规则构建动态系统提示。
    
    参数:
        parsed_rules: 包含 'key' 和 'options' 字段的字典列表
                     示例: [{'key': 'category', 'options': ['Contract', 'Invoice']},
                              {'key': 'year', 'options': None}]
    
    返回:
        str: 带有枚举约束的增强系统提示
    
    示例:
        >>> rules = [{'key': 'category', 'options': ['Contract', 'Invoice', 'Manual']}]
        >>> prompt = build_dynamic_prompt(rules)
        # 提示将包含："字段 'category' 必须是以下之一：Contract, Invoice, Manual"
    """
    base_prompt = SYSTEM_PROMPT
    
    constraints = []
    
    for rule in parsed_rules:
        field_key = rule['key']
        options = rule.get('options')
        
        if options and len(options) > 0:
            options_str = ', '.join(options)
            constraint = f"\n\n'{field_key}' 字段的重要约束：\n"
            constraint += f"字段 '{field_key}' 必须是以下值之一：{options_str}。\n"
            constraint += f"如果不确定，请从这些选项中选择最接近的匹配项。不要使用任何其他值。\n"
            constraint += f"这是一个分类任务（多选），而不是开放式生成。"
            constraints.append(constraint)
    
    if constraints:
        enhanced_prompt = base_prompt + '\n' + '\n'.join(constraints)
        return enhanced_prompt
    
    return base_prompt


def classify_file(file_name, parsed_rules=None, llm_client=None):
    """使用 LLM 对文件进行分类，支持可选的枚举约束。
    
    参数:
        file_name: 要分类的文件名
        parsed_rules: 可选的带有枚举约束的解析规则字典列表
        llm_client: LLM 客户端实例（可选，用于未来实现）
    
    返回:
        dict: 分类结果，包含键：category, year, month, summary, original_name
    
    注意:
        这是一个占位符。实际的 LLM 集成将在稍后实现。
        当 LLM 集成后，使用 build_dynamic_prompt(parsed_rules) 生成
        带有枚举约束的系统提示。
    """
    import json
    from pathlib import Path
    
    file_path = Path(file_name)
    name_without_ext = file_path.stem
    
    if parsed_rules:
        system_prompt = build_dynamic_prompt(parsed_rules)
    else:
        system_prompt = get_system_prompt()
    
    result = {
        "category": "Unknown",
        "year": "Unknown",
        "month": "Unknown",
        "summary": f"File: {name_without_ext}",
        "original_name": name_without_ext
    }
    
    return result
