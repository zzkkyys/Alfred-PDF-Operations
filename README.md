# Alfred PDF Operations Workflow

一个用于对 PDF 文件执行常用操作的 Alfred Workflow。


Created by [zzkkyys](https://github.com/zzkkyys) | [Github](https://github.com/zzkkyys/Alfred-PDF-Operations) 




## 功能

通过 Finder 选中 PDF 文件后，使用 Universal Action 可以执行以下操作：

1. **PDF 转 PNG 图片** - 将 PDF 的每一页转换为 PNG 图片（300 DPI）
2. **裁剪 PDF 边缘空白** - 自动检测并裁剪 PDF 页面的空白边距
3. **拆分 PDF 为单页** - 将 PDF 文件拆分为多个单页 PDF 文件



## 依赖项

### Python 包

```bash
pip3 install PyMuPDF pdf2image pillow
```

### 系统工具

使用 Homebrew 安装必要的命令行工具：

```bash
# PDF转PNG所需 (poppler提供pdftoppm)
brew install poppler

# PDF裁剪所需 (可选择其一)
# 方案1: 完整的TeX Live (较大，约7GB)
brew install texlive

# 方案2: 轻量级的BasicTeX (推荐，约100MB)
brew install basictex
# 安装后需要更新PATH
eval "$(/usr/libexec/path_helper)"
```

**注意**: `pdfcrop` 工具需要 TeX Live 或 BasicTeX。如果只需要 PDF 转 PNG 和拆分功能，可以不安装。

## 使用方法

### 通过 Universal Action

1. 在 Finder 中选中一个或多个 PDF 文件
2. 按下 Universal Action 快捷键（默认是 `⌘ + ⇧ + A`）
3. 选择 "PDF Operations"
4. 选择要执行的操作
5. 处理后的文件将保存在与原文件相同的目录中

### 输出说明

- **PDF 转 PNG**: 
  - 单页 PDF：生成 `原文件名.png`
  - 多页 PDF：生成 `原文件名_page_1.png`, `原文件名_page_2.png` 等

- **裁剪 PDF 边缘空白**: 
  - 生成 `原文件名_cropped.pdf`

- **拆分 PDF 为单页**: 
  - 在原文件目录下创建 `原文件名_pages` 文件夹
  - 生成 `原文件名_page_001.pdf`, `原文件名_page_002.pdf` 等


## 扩展

要添加新的 PDF 操作：

1. 在 `pdf_processors/` 目录下创建新的处理器类，继承 `BaseProcessor`
2. 实现 `process_single()` 方法
3. 在 `main.py` 的 `PDF_OPERATIONS` 字典中添加新操作
4. 在 `pdf_processors/__init__.py` 中导出新处理器
4. Use `⌘ + L` to preview search results
5. Press `Enter` to open file in Obsidian