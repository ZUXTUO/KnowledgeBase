#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录对比工具 - 生成类似GitHub的diff报告
比较两个目录的所有文件，生成Markdown格式的差异报告
"""

import os
import difflib
from pathlib import Path
from datetime import datetime


class DirectoryComparator:
    def __init__(self, input1_path, input2_path, output_path="diff_report.md"):
        self.input1 = Path(input1_path)
        self.input2 = Path(input2_path)
        self.output_path = output_path
        self.results = []
        
    def get_all_files(self, directory):
        """获取目录下所有文件的相对路径"""
        files = set()
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                full_path = Path(root) / filename
                rel_path = full_path.relative_to(directory)
                files.add(rel_path)
        return files
    
    def read_file_lines(self, filepath):
        """读取文件内容，尝试多种编码"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.readlines()
            except (UnicodeDecodeError, UnicodeError):
                continue
        # 如果都失败，返回二进制标识
        return ["[Binary file or unsupported encoding]\n"]
    
    def generate_diff(self, file1_lines, file2_lines, filename):
        """生成文件的diff内容"""
        diff = difflib.unified_diff(
            file1_lines,
            file2_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=''
        )
        return list(diff)
    
    def format_diff_markdown(self, diff_lines, filename):
        """将diff格式化为Markdown"""
        md_content = [f"\n## 📄 {filename}\n"]
        
        if not diff_lines:
            md_content.append("*文件内容相同*\n")
            return md_content
        
        md_content.append("```diff")
        
        for line in diff_lines:
            # 移除行尾的换行符
            line = line.rstrip('\n')
            md_content.append(line)
        
        md_content.append("```\n")
        return md_content
    
    def compare_directories(self):
        """比较两个目录"""
        print(f"📂 开始比较目录:")
        print(f"  Input1: {self.input1}")
        print(f"  Input2: {self.input2}")
        
        # 获取所有文件
        files1 = self.get_all_files(self.input1)
        files2 = self.get_all_files(self.input2)
        
        # 分类文件
        only_in_1 = files1 - files2
        only_in_2 = files2 - files1
        common_files = files1 & files2
        
        # 创建Markdown报告
        md_report = []
        md_report.append(f"# 📊 目录对比报告\n")
        md_report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_report.append(f"**Input1:** `{self.input1}`\n")
        md_report.append(f"**Input2:** `{self.input2}`\n")
        md_report.append("\n---\n")
        
        # 统计信息
        md_report.append("## 📈 统计摘要\n")
        md_report.append(f"- 仅存在于 Input1: **{len(only_in_1)}** 个文件\n")
        md_report.append(f"- 仅存在于 Input2: **{len(only_in_2)}** 个文件\n")
        md_report.append(f"- 共同文件: **{len(common_files)}** 个文件\n")
        md_report.append("\n---\n")
        
        # 仅在Input1中的文件（已删除）
        if only_in_1:
            md_report.append("## 🗑️ 仅存在于 Input1 的文件（在Input2中已删除）\n")
            for file in sorted(only_in_1):
                md_report.append(f"- ❌ `{file}`\n")
                file1_path = self.input1 / file
                file1_lines = self.read_file_lines(file1_path)
                
                md_report.append(f"\n### 文件内容: {file}\n")
                md_report.append("```diff")
                for line in file1_lines[:50]:  # 限制显示前50行
                    md_report.append(f"- {line.rstrip()}")
                if len(file1_lines) > 50:
                    md_report.append(f"... (共 {len(file1_lines)} 行，仅显示前50行)")
                md_report.append("```\n")
            md_report.append("\n---\n")
        
        # 仅在Input2中的文件（新增）
        if only_in_2:
            md_report.append("## ✨ 仅存在于 Input2 的文件（新增）\n")
            for file in sorted(only_in_2):
                md_report.append(f"- ✅ `{file}`\n")
                file2_path = self.input2 / file
                file2_lines = self.read_file_lines(file2_path)
                
                md_report.append(f"\n### 文件内容: {file}\n")
                md_report.append("```diff")
                for line in file2_lines[:50]:  # 限制显示前50行
                    md_report.append(f"+ {line.rstrip()}")
                if len(file2_lines) > 50:
                    md_report.append(f"... (共 {len(file2_lines)} 行，仅显示前50行)")
                md_report.append("```\n")
            md_report.append("\n---\n")
        
        # 共同文件的差异对比
        modified_files = []
        identical_files = []
        
        for file in sorted(common_files):
            file1_path = self.input1 / file
            file2_path = self.input2 / file
            
            file1_lines = self.read_file_lines(file1_path)
            file2_lines = self.read_file_lines(file2_path)
            
            if file1_lines != file2_lines:
                modified_files.append(file)
                diff_lines = self.generate_diff(file1_lines, file2_lines, str(file))
                self.results.extend(self.format_diff_markdown(diff_lines, str(file)))
            else:
                identical_files.append(file)
        
        # 修改的文件
        if modified_files:
            md_report.append(f"## 🔄 已修改的文件 ({len(modified_files)} 个)\n")
            for file in modified_files:
                md_report.append(f"- 📝 `{file}`\n")
            md_report.append("\n---\n")
            md_report.append("# 📝 详细差异内容\n")
            md_report.extend(self.results)
        
        # 相同的文件
        if identical_files:
            md_report.append("\n## ✔️ 内容完全相同的文件\n")
            for file in identical_files:
                md_report.append(f"- `{file}`\n")
        
        # 写入文件
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_report))
        
        print(f"\n✅ 对比完成！报告已生成: {self.output_path}")
        print(f"   - 已修改: {len(modified_files)} 个文件")
        print(f"   - 相同: {len(identical_files)} 个文件")
        print(f"   - 仅在Input1: {len(only_in_1)} 个文件")
        print(f"   - 仅在Input2: {len(only_in_2)} 个文件")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 3:
        print("使用方法:")
        print("  python dir_compare.py <input1_path> <input2_path> [output_file.md]")
        print("\n示例:")
        print("  python dir_compare.py ./input1 ./input2")
        print("  python dir_compare.py ./input1 ./input2 custom_report.md")
        sys.exit(1)
    
    input1 = sys.argv[1]
    input2 = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "diff_report.md"
    
    # 检查目录是否存在
    if not os.path.isdir(input1):
        print(f"❌ 错误: Input1 目录不存在: {input1}")
        sys.exit(1)
    
    if not os.path.isdir(input2):
        print(f"❌ 错误: Input2 目录不存在: {input2}")
        sys.exit(1)
    
    # 执行对比
    comparator = DirectoryComparator(input1, input2, output)
    comparator.compare_directories()


if __name__ == "__main__":
    main()