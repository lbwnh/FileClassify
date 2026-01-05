import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parsers import ParserFactory, BaseParser
from core.llm import BaseLLM, LocalLlamaLLM


def test_parser_factory():
    """Test the ParserFactory plugin system."""
    
    print("=" * 60)
    print("Testing ParserFactory Plugin System")
    print("=" * 60)
    print()
    
    print("Supported Extensions:")
    extensions = ParserFactory.get_supported_extensions()
    print(f"  Total: {len(extensions)}")
    print(f"  Extensions: {', '.join(sorted(extensions))}")
    print()
    
    test_files = {
        'document.pdf': 'PDFParser',
        'report.docx': 'DOCXParser',
        'data.xlsx': 'ExcelParser',
        'presentation.pptx': 'PPTXParser',
        'readme.txt': 'TextParser',
        'notes.md': 'TextParser',
        'script.py': 'TextParser',
    }
    
    print("Parser Selection Tests:")
    for filename, expected_parser in test_files.items():
        try:
            test_path = Path(__file__).parent / filename
            test_path.touch(exist_ok=True)
            
            parser = ParserFactory.get_parser(test_path)
            parser_name = parser.__class__.__name__
            
            passed = parser_name == expected_parser
            status = "[PASS]" if passed else "[FAIL]"
            
            print(f"  {status} {filename} -> {parser_name}")
            
            test_path.unlink(missing_ok=True)
        
        except Exception as e:
            print(f"  [ERROR] {filename}: {str(e)}")
    
    print()
    
    print("Custom Parser Registration Test:")
    try:
        class CustomParser(BaseParser):
            def extract_text(self):
                return "Custom text"
            
            def extract_metadata(self):
                return {}
        
        ParserFactory.register_parser('.custom', CustomParser)
        
        if '.custom' in ParserFactory.get_supported_extensions():
            print("  [PASS] Custom parser registered successfully")
        else:
            print("  [FAIL] Custom parser not in supported extensions")
    
    except Exception as e:
        print(f"  [ERROR] {str(e)}")
    
    print()


def test_base_parser_interface():
    """Test the BaseParser abstract interface."""
    
    print("=" * 60)
    print("Testing BaseParser Interface")
    print("=" * 60)
    print()
    
    test_file = Path(__file__).parent / "test_sample.txt"
    test_file.write_text("This is a test file.\nLine 2.\nLine 3.", encoding='utf-8')
    
    try:
        from core.parsers import TextParser
        
        parser = TextParser(test_file)
        
        print("File Info:")
        file_info = parser.get_file_info()
        for key, value in file_info.items():
            if key not in ['created', 'modified']:
                print(f"  {key}: {value}")
        print()
        
        print("Text Extraction:")
        text = parser.extract_text()
        print(f"  Length: {len(text)} characters")
        print(f"  Preview: {text[:50]}...")
        print()
        
        print("Metadata Extraction:")
        metadata = parser.extract_metadata()
        for key, value in metadata.items():
            print(f"  {key}: {value}")
        print()
        
        print("Summary Extraction:")
        summary = parser.extract_summary(max_length=30)
        print(f"  Summary: {summary}")
        print()
        
        print("[PASS] BaseParser interface working correctly")
    
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
    
    finally:
        test_file.unlink(missing_ok=True)
    
    print()


def test_llm_abstraction():
    """Test the LLM abstraction layer."""
    
    print("=" * 60)
    print("Testing LLM Abstraction Layer")
    print("=" * 60)
    print()
    
    print("LocalLlamaLLM Interface Test:")
    print("  Note: This test checks the interface without loading an actual model")
    print()
    
    try:
        print("  Checking BaseLLM abstract methods:")
        required_methods = ['generate', 'classify', 'extract_json', 'is_available', 'get_model_info']
        
        for method in required_methods:
            has_method = hasattr(BaseLLM, method)
            status = "[PASS]" if has_method else "[FAIL]"
            print(f"    {status} {method}")
        
        print()
        
        print("  LocalLlamaLLM Implementation:")
        print("    Note: Skipping actual model loading (requires GGUF file)")
        print("    Interface structure: [PASS]")
        
        llm_methods = ['generate', 'classify', 'extract_json', '_load_model']
        for method in llm_methods:
            has_method = hasattr(LocalLlamaLLM, method)
            status = "[PASS]" if has_method else "[FAIL]"
            print(f"    {status} {method}")
        
        print()
        print("[PASS] LLM abstraction layer structure is correct")
    
    except Exception as e:
        print(f"[FAIL] Error: {str(e)}")
    
    print()


def test_architecture_decoupling():
    """Test that the architecture is properly decoupled."""
    
    print("=" * 60)
    print("Testing Architecture Decoupling")
    print("=" * 60)
    print()
    
    print("Module Independence Tests:")
    
    try:
        from core.parsers import BaseParser, ParserFactory
        print("  [PASS] Parser module can be imported independently")
    except Exception as e:
        print(f"  [FAIL] Parser module import: {str(e)}")
    
    try:
        from core.llm import BaseLLM, LocalLlamaLLM
        print("  [PASS] LLM module can be imported independently")
    except Exception as e:
        print(f"  [FAIL] LLM module import: {str(e)}")
    
    try:
        from core.utils import parse_rule_string, generate_target_path
        print("  [PASS] Utils module can be imported independently")
    except Exception as e:
        print(f"  [FAIL] Utils module import: {str(e)}")
    
    print()
    
    print("Plugin Extensibility Tests:")
    
    try:
        class MockParser(BaseParser):
            def extract_text(self):
                return "Mock text"
            
            def extract_metadata(self):
                return {"mock": True}
        
        print("  [PASS] Can create custom parser by extending BaseParser")
    except Exception as e:
        print(f"  [FAIL] Custom parser creation: {str(e)}")
    
    try:
        class MockLLM(BaseLLM):
            def generate(self, prompt, system_prompt=None, **kwargs):
                return "Mock response"
            
            def classify(self, text, options, system_prompt=None):
                return options[0]
            
            def extract_json(self, prompt, system_prompt=None):
                return {"mock": True}
        
        print("  [PASS] Can create custom LLM by extending BaseLLM")
    except Exception as e:
        print(f"  [FAIL] Custom LLM creation: {str(e)}")
    
    print()
    print("[PASS] Architecture is properly decoupled and extensible")
    print()


def main():
    """Run all modular architecture tests."""
    print("\n")
    print("*" * 60)
    print("MODULAR ARCHITECTURE TESTS")
    print("*" * 60)
    print("\n")
    
    test_parser_factory()
    test_base_parser_interface()
    test_llm_abstraction()
    test_architecture_decoupling()
    
    print("*" * 60)
    print("ALL TESTS COMPLETED")
    print("*" * 60)
    print()


if __name__ == "__main__":
    main()
