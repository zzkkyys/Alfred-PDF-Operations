# %%
import os
from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from .base_processor import BaseProcessor


# %%
class PDFSplitPagesProcessor(BaseProcessor):
    """将PDF拆分为单页文件"""
    
    operation_id = "pdf_split_pages"
    title = "拆分PDF为单页"
    subtitle = "将PDF文件拆分为多个单页PDF文件"
    quicklook_url = os.path.join(os.path.dirname(__file__), '../docs', 'pdf_split_pages.html')
    
    def __init__(self):
        """初始化PDF拆分处理器"""
        super().__init__()
    
    def process_single(self, pdf_path: str, output_dir: Optional[str] = None) -> dict:
        """
        将单个PDF文件拆分为单页文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果为None则使用PDF所在目录
            
        Returns:
            dict: 包含status, message, output_files等信息
        """
        try:
            # 验证PDF文件
            self.validate_pdf(pdf_path)
            
            # 获取输出目录和基础文件名
            output_dir = self.get_output_dir(pdf_path, output_dir)
            base_name = self.get_base_filename(pdf_path)
            
            # 创建子目录存放拆分后的文件
            split_dir = os.path.join(output_dir, f"{base_name}_pages")
            os.makedirs(split_dir, exist_ok=True)
            
            self.log(f"开始拆分PDF: {pdf_path}")
            
            # 打开PDF文件
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            output_files = []
            
            for page_num in range(total_pages):
                # 创建新的单页PDF
                output_doc = fitz.open()
                output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                
                # 生成输出文件名（页码补零，如page_001.pdf）
                page_number = str(page_num + 1).zfill(len(str(total_pages)))
                output_path = os.path.join(split_dir, f"{base_name}_page_{page_number}.pdf")
                
                # 保存单页PDF
                output_doc.save(output_path)
                output_doc.close()
                
                output_files.append(output_path)
                self.log(f"已保存第 {page_num + 1}/{total_pages} 页: {output_path}")
            
            doc.close()
            
            return {
                'status': 'success',
                'file': pdf_path,
                'message': f'成功拆分为 {total_pages} 个单页文件',
                'output_files': output_files,
                'page_count': total_pages,
                'output_dir': split_dir
            }
            
        except Exception as e:
            self.log(f"拆分失败: {str(e)}")
            return {
                'status': 'error',
                'file': pdf_path,
                'message': str(e),
                'output_files': []
            }
