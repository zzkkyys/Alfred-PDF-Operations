# %%
import os
from pathlib import Path
from typing import Optional
from pdf2image import convert_from_path
from .base_processor import BaseProcessor


# %%
class PDFToPNGProcessor(BaseProcessor):
    """将PDF转换为PNG图片"""
    
    operation_id = "pdf_to_png"
    title = "PDF转PNG图片"
    subtitle = "将PDF的每一页转换为PNG图片（300 DPI）"
    quicklook_url = os.path.join(os.path.dirname(__file__), '../docs', 'pdf_to_png.html')
    
    def __init__(self, dpi: int = 300, fmt: str = 'PNG'):
        """
        初始化PDF转PNG处理器
        
        Args:
            dpi: 输出图片的DPI，默认300
            fmt: 输出格式，默认PNG
        """
        super().__init__()
        self.dpi = dpi
        self.fmt = fmt
    
    def process_single(self, pdf_path: str, output_dir: Optional[str] = None) -> dict:
        """
        将单个PDF文件转换为PNG图片
        
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
            
            self.log(f"开始转换PDF: {pdf_path}")
            
            # 转换PDF为图片
            images = convert_from_path(pdf_path, dpi=self.dpi)
            
            output_files = []
            for i, image in enumerate(images, start=1):
                # 生成输出文件名
                if len(images) == 1:
                    output_path = os.path.join(output_dir, f"{base_name}.png")
                else:
                    output_path = os.path.join(output_dir, f"{base_name}_page_{i}.png")
                
                # 保存图片
                image.save(output_path, self.fmt)
                output_files.append(output_path)
                self.log(f"已保存: {output_path}")
            
            return {
                'status': 'success',
                'file': pdf_path,
                'message': f'成功转换 {len(images)} 页',
                'output_files': output_files,
                'page_count': len(images)
            }
            
        except Exception as e:
            self.log(f"转换失败: {str(e)}")
            return {
                'status': 'error',
                'file': pdf_path,
                'message': str(e),
                'output_files': []
            }
