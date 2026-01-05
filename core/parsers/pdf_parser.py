"""
PDF 解析器实现。

本模块提供 PDF 文件解析功能，支持 OCR 处理扫描版 PDF。
"""

from .base import BaseParser
from typing import Dict
import io

class PDFParser(BaseParser):
    """
    PDF 文件解析器。

    使用混合策略：
    1. 优先使用 pymupdf (fitz) 进行快速文本提取
    2. 如果文本过少，自动使用 RapidOCR 处理扫描版 PDF
    """
    
    MIN_TEXT_LENGTH = 50
    MAX_OCR_PAGES = 7
    SAMPLE_PAGES = 5
    _ocr_engine = None
    
    def extract_text(self) -> str:
        """
        从 PDF 文件中提取文本内容。

        使用混合策略：
        1. 步骤 A：尝试直接提取（快速）
        2. 步骤 B：如果文本过少，使用 OCR（慢但强大）
        3. 步骤 C：返回结果

        返回:
            str: 提取的文本内容
        """
        try:
            import fitz
            
            doc = fitz.open(self.file_path)
            total_pages = len(doc)
            text_content = []
            
            for page_num in range(min(self.SAMPLE_PAGES, total_pages)):
                page = doc[page_num]
                text = page.get_text()
                if text:
                    text_content.append(text)
            
            extracted_text = '\n'.join(text_content)
            
            if len(extracted_text.strip()) < self.MIN_TEXT_LENGTH and total_pages > 0:
                print(f"[PDF Parser] 检测到扫描版 PDF，启动 OCR... 文件: {self.file_path.name}")
                ocr_text = self._extract_with_ocr(doc)
                if ocr_text:
                    extracted_text = ocr_text
            
            if total_pages > self.SAMPLE_PAGES:
                for page_num in range(self.SAMPLE_PAGES, total_pages):
                    page = doc[page_num]
                    text = page.get_text()
                    if text:
                        extracted_text += '\n' + text
            
            doc.close()
            
            return extracted_text
        
        except ImportError:
            try:
                import PyPDF2
                
                text_content = []
                
                with open(self.file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_content.append(text)
                
                return '\n'.join(text_content)
            
            except ImportError:
                return f"[PDF 解析器] 无法提取文本：pymupdf 或 PyPDF2 未安装。\n文件：{self.file_path.name}"
        
        except Exception as e:
            return f"[PDF 解析器] 提取文本出错：{str(e)}\n文件：{self.file_path.name}"
    
    def _extract_with_ocr(self, doc) -> str:
        """
        使用 OCR 从扫描版 PDF 中提取文本。

        参数:
            doc: fitz.Document 对象

        返回:
            str: OCR 提取的文本
        """
        try:
            from rapidocr_onnxruntime import RapidOCR
            
            if self._ocr_engine is None:
                PDFParser._ocr_engine = RapidOCR()
            
            ocr_text_parts = []
            
            for page_num in range(min(self.MAX_OCR_PAGES, len(doc))):
                page = doc[page_num]
                
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_data = pix.tobytes("png")
                
                result, _ = self._ocr_engine(img_data)
                
                if result:
                    page_text = '\n'.join([line[1] for line in result])
                    ocr_text_parts.append(f"[第 {page_num + 1} 页]\n{page_text}")
            
            return '\n\n'.join(ocr_text_parts)
        
        except ImportError:
            print(f"[PDF 解析器] 警告：rapidocr-onnxruntime 未安装，无法进行 OCR。")
            return ""
        
        except Exception as e:
            print(f"[PDF 解析器] OCR 出错：{str(e)}")
            return ""
    
    def extract_metadata(self) -> Dict[str, any]:
        """
        从 PDF 文件中提取元数据。

        返回:
            dict: PDF 元数据
        """
        metadata = {
            'title': None,
            'author': None,
            'subject': None,
            'creator': None,
            'producer': None,
            'created_date': None,
            'modified_date': None,
            'page_count': 0
        }
        
        try:
            import PyPDF2
            
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata['page_count'] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    pdf_meta = pdf_reader.metadata
                    metadata['title'] = pdf_meta.get('/Title')
                    metadata['author'] = pdf_meta.get('/Author')
                    metadata['subject'] = pdf_meta.get('/Subject')
                    metadata['creator'] = pdf_meta.get('/Creator')
                    metadata['producer'] = pdf_meta.get('/Producer')
                    metadata['created_date'] = pdf_meta.get('/CreationDate')
                    metadata['modified_date'] = pdf_meta.get('/ModDate')
        
        except Exception as e:
            metadata['error'] = str(e)
        
        return metadata
