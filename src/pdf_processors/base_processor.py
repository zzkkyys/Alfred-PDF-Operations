# %%
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union, Optional


# %%
class BaseProcessor(ABC):
    """PDF处理器基类"""
    
    # 子类需要定义这些类属性
    operation_id: str = None
    title: str = None
    subtitle: str = None
    quicklook_url: str = None  # 指向说明文档的本地HTML文件
    
    def __init__(self):
        self.processor_name = self.__class__.__name__
    
    @abstractmethod
    def process_single(self, pdf_path: str, output_dir: Optional[str] = None) -> dict:
        """
        处理单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录，如果为None则使用PDF所在目录
            
        Returns:
            dict: 包含status, message, output_files等信息
        """
        pass
    
    def process_multiple(self, pdf_paths: List[str], output_dir: Optional[str] = None) -> List[dict]:
        """
        处理多个PDF文件
        
        Args:
            pdf_paths: PDF文件路径列表
            output_dir: 输出目录，如果为None则使用各PDF所在目录
            
        Returns:
            List[dict]: 每个文件的处理结果
        """
        results = []
        for pdf_path in pdf_paths:
            try:
                result = self.process_single(pdf_path, output_dir)
                results.append(result)
            except Exception as e:
                results.append({
                    'status': 'error',
                    'file': pdf_path,
                    'message': str(e)
                })
        return results
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        验证PDF文件是否存在且有效
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            bool: 文件是否有效
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"不是有效的PDF文件: {pdf_path}")
        
        return True
    
    def get_output_dir(self, pdf_path: str, output_dir: Optional[str] = None) -> str:
        """
        获取输出目录
        
        Args:
            pdf_path: PDF文件路径
            output_dir: 指定的输出目录
            
        Returns:
            str: 输出目录路径
        """
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def get_base_filename(self, pdf_path: str) -> str:
        """
        获取不含扩展名的文件名
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            str: 不含扩展名的文件名
        """
        return Path(pdf_path).stem
    
    def log(self, message: str):
        """
        输出日志信息到stderr（Alfred调试窗口可见）
        
        Args:
            message: 日志信息
        """
        print(f"[{self.processor_name}] {message}", file=sys.stderr)
