import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.utils import generate_target_path


def test_generate_target_path():
    """Test the generate_target_path function."""
    
    print("Testing generate_target_path function...\n")
    
    ai_data = {
        'category': 'Work',
        'year': '2024',
        'month': '01',
        'summary': 'Financial Report',
        'original_name': 'report_2024_Q1'
    }
    
    test_cases = [
        ("类型 >> 年份", "Work/2024"),
        ("类型 >> 年份 >> 月份", "Work/2024/01"),
        ("Category >> Year", "Work/2024"),
        ("year >> month", "2024/01"),
        ("类型", "Work"),
        ("", "Unknown"),
        ("InvalidField", "Unknown"),
    ]
    
    for rule, expected in test_cases:
        result = generate_target_path(rule, ai_data)
        expected_normalized = expected.replace('/', os.sep)
        status = "[PASS]" if result == expected_normalized else "[FAIL]"
        print(f"{status} Rule: '{rule}'")
        print(f"  Expected: {expected_normalized}")
        print(f"  Got:      {result}")
        print()
    
    print("\nTest with missing data:")
    incomplete_data = {
        'category': 'Personal',
        'year': 'Unknown'
    }
    
    result = generate_target_path("类型 >> 年份 >> 月份", incomplete_data)
    print(f"Rule: '类型 >> 年份 >> 月份'")
    print(f"Result: {result}")
    print()
    
    print("All tests completed!")


if __name__ == "__main__":
    test_generate_target_path()
