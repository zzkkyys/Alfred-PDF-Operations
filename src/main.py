# %%
# %load_ext autoreload
# %autoreload 2

# %%
import argparse
import os
import sys
import json
from base.alfred import Alfred, Alfred_Item
from pdf_processors import PDFToPNGProcessor, PDFCropMarginsProcessor, PDFSplitPagesProcessor


# 所有可用的处理器类
PROCESSOR_CLASSES = [
    PDFToPNGProcessor,
    PDFCropMarginsProcessor,
    PDFSplitPagesProcessor,
]

# 构建操作字典（从处理器类的元数据生成）
PDF_OPERATIONS = {
    processor_class.operation_id: processor_class
    for processor_class in PROCESSOR_CLASSES
}


# %% tags=[]
def list_operations(query: str = ""):
    """
    列出所有可用的PDF操作
    
    Args:
        query: 搜索查询字符串
    """
    alfred = Alfred()
    
    for operation_id, processor_class in PDF_OPERATIONS.items():
        # 简单的搜索过滤
        if query and query.lower() not in processor_class.title.lower():
            continue
        
        # 获取quicklook_url的绝对路径
        quicklook_url = None
        if processor_class.quicklook_url:
            quicklook_path = os.path.abspath(processor_class.quicklook_url)
            if os.path.exists(quicklook_path):
                quicklook_url = f"{quicklook_path}"
        
        alfred.add_item(
            title=processor_class.title,
            subtitle=processor_class.subtitle,
            arg=operation_id,
            valid=True,
            quicklookurl=quicklook_url
        )
    
    alfred.output_items()


# %% tags=[]
def process_files(operation: str, pdf_files: list):
    """
    处理PDF文件
    
    Args:
        operation: 操作类型
        pdf_files: PDF文件路径列表
    """
    if operation not in PDF_OPERATIONS:
        sys.stderr.write(f"错误: 未知操作: {operation}\n")
        sys.exit(1)
    
    # 创建处理器实例
    processor_class = PDF_OPERATIONS[operation]
    processor = processor_class()
    
    # 处理文件
    results = processor.process_multiple(pdf_files)
    
    # 统计结果
    success_count = sum(1 for r in results if r['status'] == 'success')
    error_count = len(results) - success_count
    
    # 输出结果摘要到stderr
    if error_count == 0:
        message = f"✓ 成功处理 {success_count} 个文件"
    else:
        message = f"⚠ 成功 {success_count} 个，失败 {error_count} 个"
    
    sys.stderr.write(f"\n{message}\n")
    
    # 输出详细结果
    for result in results:
        if result['status'] == 'success':
            sys.stderr.write(f"  ✓ {result['file']}: {result['message']}\n")
            if result.get('output_files'):
                for out_file in result['output_files'][:3]:  # 最多显示3个
                    sys.stderr.write(f"    → {out_file}\n")
                if len(result['output_files']) > 3:
                    sys.stderr.write(f"    ... 和其他 {len(result['output_files']) - 3} 个文件\n")
        else:
            sys.stderr.write(f"  ✗ {result['file']}: {result['message']}\n")


# %% tags=[]
def main(args):
    """
    主函数
    
    Args:
        args: 命令行参数
    """
    if args.mode == "list":
        # 列出所有操作供用户选择
        list_operations(args.query or "")
    
    elif args.mode == "process":
        # 处理文件
        if not args.operation:
            sys.stderr.write("错误: 未指定操作类型\n")
            sys.exit(1)
        
        if not args.files:
            sys.stderr.write("错误: 未指定文件\n")
            sys.exit(1)
        
        # 解析文件列表（可能是以换行符分隔的字符串）
        if isinstance(args.files, str):
            pdf_files = [f.strip() for f in args.files.split('\n') if f.strip()]
        else:
            pdf_files = args.files
        
        process_files(args.operation, pdf_files)


# %% tags=[]
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alfred PDF Operations Workflow")
    parser.add_argument("--mode", type=str, required=True, 
                       choices=["list", "process"],
                       help="运行模式: list(列出操作) 或 process(处理文件)")
    parser.add_argument("--query", type=str, default="",
                       help="搜索查询（仅在list模式下使用）")
    parser.add_argument("--operation", type=str,
                       help="要执行的操作ID（在process模式下使用）")
    
    args = parser.parse_args()
    
    args.files = os.environ.get("files", "").splitlines()
    print(args.files, file=sys.stderr)
    
    main(args)

