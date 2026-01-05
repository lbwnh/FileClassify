import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import parse_rule_string, generate_target_path
from core.ai_engine import build_dynamic_prompt, classify_file


def test_parse_rule_string():
    """Test the parse_rule_string function with enum constraints."""
    
    print("=" * 60)
    print("Testing parse_rule_string with Enum Constraints")
    print("=" * 60)
    print()
    
    test_cases = [
        {
            "rule": "Category [Contract, Invoice, Manual] >> Year",
            "expected": [
                {'key': 'category', 'options': ['Contract', 'Invoice', 'Manual']},
                {'key': 'year', 'options': None}
            ]
        },
        {
            "rule": "类型 [合同, 发票] >> 年份",
            "expected": [
                {'key': 'category', 'options': ['合同', '发票']},
                {'key': 'year', 'options': None}
            ]
        },
        {
            "rule": "Category [Work, Personal] >> Year >> Month [01, 02, 03]",
            "expected": [
                {'key': 'category', 'options': ['Work', 'Personal']},
                {'key': 'year', 'options': None},
                {'key': 'month', 'options': ['01', '02', '03']}
            ]
        },
        {
            "rule": "类型 >> 年份",
            "expected": [
                {'key': 'category', 'options': None},
                {'key': 'year', 'options': None}
            ]
        },
        {
            "rule": "Category[A,B,C]>>Year",
            "expected": [
                {'key': 'category', 'options': ['A', 'B', 'C']},
                {'key': 'year', 'options': None}
            ]
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        rule = test["rule"]
        expected = test["expected"]
        result = parse_rule_string(rule)
        
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        
        print(f"Test {i}: {status}")
        print(f"  Rule: {rule}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    print()


def test_build_dynamic_prompt():
    """Test the build_dynamic_prompt function."""
    
    print("=" * 60)
    print("Testing build_dynamic_prompt")
    print("=" * 60)
    print()
    
    parsed_rules = [
        {'key': 'category', 'options': ['Contract', 'Invoice', 'Manual']},
        {'key': 'year', 'options': None}
    ]
    
    prompt = build_dynamic_prompt(parsed_rules)
    
    print("Parsed Rules:")
    for rule in parsed_rules:
        print(f"  {rule}")
    print()
    
    print("Generated Prompt (last 500 chars):")
    print("-" * 60)
    print(prompt[-500:])
    print("-" * 60)
    print()
    
    has_constraint = "IMPORTANT CONSTRAINT" in prompt
    has_options = "Contract, Invoice, Manual" in prompt
    has_classification = "classification task" in prompt.lower()
    
    print(f"Contains 'IMPORTANT CONSTRAINT': {has_constraint}")
    print(f"Contains options list: {has_options}")
    print(f"Contains 'classification task': {has_classification}")
    print()
    
    if has_constraint and has_options and has_classification:
        print("[PASS] Dynamic prompt generation successful!")
    else:
        print("[FAIL] Dynamic prompt missing required elements")
    
    print()


def test_generate_target_path_with_enums():
    """Test generate_target_path with enum constraints."""
    
    print("=" * 60)
    print("Testing generate_target_path with Enum Constraints")
    print("=" * 60)
    print()
    
    ai_data = {
        'category': 'Contract',
        'year': '2024',
        'month': '01'
    }
    
    test_cases = [
        ("Category [Contract, Invoice] >> Year", "Contract\\2024"),
        ("类型 [合同, 发票] >> 年份 >> 月份", "Contract\\2024\\01"),
        ("Category >> Year", "Contract\\2024"),
    ]
    
    for rule, expected in test_cases:
        result = generate_target_path(rule, ai_data)
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        
        print(f"{status}")
        print(f"  Rule: {rule}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    print()


def test_classify_file_with_constraints():
    """Test classify_file with parsed rules."""
    
    print("=" * 60)
    print("Testing classify_file with Enum Constraints")
    print("=" * 60)
    print()
    
    parsed_rules = [
        {'key': 'category', 'options': ['Contract', 'Invoice', 'Manual']},
        {'key': 'year', 'options': None}
    ]
    
    result = classify_file("test_document.pdf", parsed_rules=parsed_rules)
    
    print("Parsed Rules:")
    for rule in parsed_rules:
        print(f"  {rule}")
    print()
    
    print("Classification Result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()
    
    has_required_keys = all(key in result for key in ['category', 'year', 'month', 'summary', 'original_name'])
    
    if has_required_keys:
        print("[PASS] Classification returned all required fields")
    else:
        print("[FAIL] Classification missing required fields")
    
    print()


def main():
    """Run all tests."""
    print("\n")
    print("*" * 60)
    print("ENUM CONSTRAINT TESTS")
    print("*" * 60)
    print("\n")
    
    test_parse_rule_string()
    test_build_dynamic_prompt()
    test_generate_target_path_with_enums()
    test_classify_file_with_constraints()
    
    print("*" * 60)
    print("ALL TESTS COMPLETED")
    print("*" * 60)
    print()


if __name__ == "__main__":
    main()
