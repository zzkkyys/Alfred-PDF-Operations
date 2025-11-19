# %%
import os
import subprocess
from pathlib import Path
from typing import Optional
from .base_processor import BaseProcessor


# %%
class PDFCropMarginsProcessor(BaseProcessor):
    """裁剪PDF边缘空白"""
    
    operation_id = "pdf_crop_margins"
    title = "裁剪PDF边缘空白"
    subtitle = "自动检测并裁剪PDF页面的空白边距"
    quicklook_url = os.path.join(os.path.dirname(__file__), '../docs', 'pdf_crop_margins.html')
    
    def __init__(self, margin: str = "0"):
        """
        初始化PDF裁剪处理器
        
        Args:
            margin: 保留的边距，可以是单个数值或四个数值（左 上 右 下），默认"10"
        """
        super().__init__()
        self.margin = margin
    
    def _find_pdfcrop(self) -> Optional[str]:
        """
        查找pdfcrop命令的完整路径
        
        Returns:
            str: pdfcrop的完整路径，如果未找到则返回None
        """
        # 常见的TeX路径
        tex_paths = [
            '/Library/TeX/texbin/pdfcrop',
            '/usr/local/texlive/2024/bin/universal-darwin/pdfcrop',
            '/usr/local/texlive/2023/bin/universal-darwin/pdfcrop',
            '/usr/local/bin/pdfcrop',
            '/opt/homebrew/bin/pdfcrop',
        ]
        
        # 首先尝试直接从PATH中找
        try:
            result = subprocess.run(['which', 'pdfcrop'], 
                                  capture_output=True, 
                                  text=True,
                                  check=True)
            pdfcrop_path = result.stdout.strip()
            if pdfcrop_path and os.path.exists(pdfcrop_path):
                return pdfcrop_path
        except:
            pass
        
        # 然后尝试常见路径
        for path in tex_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def process_single(self, pdf_path: str, output_dir: Optional[str] = None) -> dict:
        """
        裁剪单个PDF文件的边缘空白
        
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
            
            # 生成输出文件路径
            output_path = os.path.join(output_dir, f"{base_name}_cropped.pdf")
            
            self.log(f"开始裁剪PDF: {pdf_path}")
            
            # 查找pdfcrop命令
            pdfcrop_cmd = self._find_pdfcrop()
            if not pdfcrop_cmd:
                raise RuntimeError(
                    "pdfcrop命令未找到。请安装: brew install texlive 或 brew install basictex"
                )
            
            self.log(f"使用pdfcrop: {pdfcrop_cmd}")
            
            # 设置环境变量，添加TeX bin目录到PATH
            env = os.environ.copy()
            tex_bin_dir = os.path.dirname(pdfcrop_cmd)
            
            # 将TeX bin目录添加到PATH的最前面
            if 'PATH' in env:
                env['PATH'] = f"{tex_bin_dir}:{env['PATH']}"
            else:
                env['PATH'] = tex_bin_dir
            
            self.log(f"设置PATH: {env['PATH']}")
            
            # 构建pdfcrop命令
            # pdfcrop会自动检测并裁剪所有页面的空白边距
            cmd = [
                pdfcrop_cmd,  # 使用完整路径
                '--margins', self.margin,  # 保留的边距
                pdf_path,
                output_path
            ]
            
            self.log(f"执行命令: {' '.join(cmd)}")
            
            # 执行pdfcrop命令，传入修改后的环境变量
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env  # 使用包含TeX路径的环境变量
            )
            
            # 记录输出
            if result.stdout:
                self.log(f"pdfcrop输出: {result.stdout}")
            
            # 检查输出文件是否生成
            if not os.path.exists(output_path):
                raise RuntimeError("裁剪后的PDF文件未生成")
            
            # 获取页数（使用简单的方法）
            page_count = self._count_pdf_pages(pdf_path)
            
            self.log(f"已保存: {output_path}")
            
            return {
                'status': 'success',
                'file': pdf_path,
                'message': f'成功裁剪 {page_count} 页',
                'output_files': [output_path],
                'page_count': page_count
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"pdfcrop执行失败: {e.stderr if e.stderr else str(e)}"
            self.log(error_msg)
            return {
                'status': 'error',
                'file': pdf_path,
                'message': error_msg,
                'output_files': []
            }
        except Exception as e:
            self.log(f"裁剪失败: {str(e)}")
            return {
                'status': 'error',
                'file': pdf_path,
                'message': str(e),
                'output_files': []
            }
    
    def _count_pdf_pages(self, pdf_path: str) -> int:
        """
        统计PDF页数（使用pdfinfo或其他方法）
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            int: 页数
        """
        try:
            # 尝试使用pdfinfo
            result = subprocess.run(
                ['pdfinfo', pdf_path],
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    return int(line.split(':')[1].strip())
        except:
            pass
        
        # 如果pdfinfo不可用，返回未知
        return 0
