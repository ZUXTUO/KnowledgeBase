import struct
import os
import subprocess
import shutil

# 辅助函数：从文件的特定偏移位置读取字节
def read_bytes(file_path, offset, size):
    """从文件的指定偏移位置读取字节数据。"""
    try:
        with open(file_path, "rb") as file:
            file.seek(offset)
            return file.read(size)
    except Exception as e:
        print(f"读取文件 {file_path} 时发生错误，偏移位置 {offset}: {e}")
        return None

# 辅助函数：向文件的特定偏移位置写入字节数据
def write_bytes(file_path, offset, data):
    """将数据写入文件的指定偏移位置。"""
    try:
        with open(file_path, "r+b") as file:
            file.seek(offset)
            file.write(data)
    except Exception as e:
        print(f"写入文件 {file_path} 时发生错误，偏移位置 {offset}: {e}")

# 备份文件
def backup_file(file_path):
    """备份文件到指定的备份文件路径。"""
    backup_path = file_path + ".backup"
    try:
        shutil.copy2(file_path, backup_path)  # 复制文件及其元数据
        print(f"文件已备份至 {backup_path}")
        return backup_path
    except Exception as e:
        print(f"备份文件时发生错误: {e}")
        return None

# 检查并修复档案的起始头部（Start Header）是否损坏
def check_and_fix_start_header(file_path):
    """检查7z档案的起始头部，并在必要时修复它。"""
    header = read_bytes(file_path, 0, 32)
    if header[:6] != b'\x37\x7A\xBC\xAF\x27\x1C':
        print("签名无效或缺失，尝试修复...")
        good_start_header = b'\x37\x7A\xBC\xAF\x27\x1C\x00\x04' + b'\x00' * 26
        write_bytes(file_path, 0, good_start_header)
        print("起始头部已修复。")
    else:
        print("起始头部有效。")

# 检查并修复档案的结束头部（End Header），如果损坏或缺失
def check_and_fix_end_header(file_path):
    """检查并修复7z档案的结束头部。"""
    expected_end_footer = b'\xDA\x01\x15\x06\x01\x00\x20\x00\x00\x00\x00\x00'

    file_size = os.path.getsize(file_path)
    if file_size < 32:
        print("文件太小，无法构成有效的7z档案。")
        return

    with open(file_path, "rb") as file:
        file.seek(-32, os.SEEK_END)
        end_header = file.read(32)

    # 检查尾部是否与预期尾部数据匹配，或者通过传统的尾部签名检查
    if end_header[:4] == b'\x17' and end_header[4:6] == b'\x06\x8D':
        print("结束头部有效（通过签名匹配）。")
    elif end_header.endswith(expected_end_footer):
        print("结束头部有效（通过尾部数据匹配）。")
    else:
        print("结束头部无效，尝试修复...")
        # 尾部修复
        fix_end_header(file_path, expected_end_footer)

# 修复结束头部的尾部数据，确保符合指定的格式
def fix_end_header(file_path, expected_end_footer):
    """修复7z档案的尾部数据，使其符合指定的格式。"""
    # 获取当前文件的最后64字节
    with open(file_path, "rb") as file:
        file.seek(-64, os.SEEK_END)
        end_data = file.read(64)

    # 查找尾部是否包含了部分匹配的内容
    found_pos = end_data.find(b'\xDA\x01\x15')

    if found_pos != -1:
        # 如果发现部分匹配，修复缺失的部分
        print(f"尾部发现部分匹配数据，修复为完整数据...")
        new_end_data = end_data[:found_pos + 3] + expected_end_footer[3:]

        # 将修复后的尾部数据写回文件
        with open(file_path, "r+b") as file:
            file.seek(-64 + found_pos, os.SEEK_END)
            file.write(new_end_data[found_pos:])
        print("尾部已修复。")
    else:
        # 如果未发现部分匹配，直接写入完整的尾部数据
        print("尾部数据无效，直接写入完整的尾部数据...")
        with open(file_path, "r+b") as file:
            file.seek(-len(expected_end_footer), os.SEEK_END)
            file.write(expected_end_footer)
        print("尾部已修复为预期格式。")

# 恢复档案缺失的部分（例如，由于截断导致的部分缺失）
def recover_missing_parts(file_path):
    """通过修复文件大小来尝试恢复档案缺失的部分。"""
    start_header = read_bytes(file_path, 0, 32)
    archive_size = struct.unpack("<I", start_header[20:24])[0]
    actual_size = os.path.getsize(file_path)
    if actual_size < archive_size:
        print(f"档案大小小于预期，尝试调整文件大小至 {archive_size} 字节。")
        with open(file_path, "ab") as file:
            file.write(b'\x00' * (archive_size - actual_size))  # 用零字节填充
        print(f"文件大小已调整为 {archive_size} 字节。")

# 使用7-Zip命令行工具验证档案的完整性
def verify_archive(file_path):
    """使用7-Zip命令行工具验证档案的完整性。"""
    try:
        result = subprocess.run(['7z', 't', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("档案有效并且可以提取。")
            return True
        else:
            print(f"档案已损坏，错误: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"验证档案时发生错误: {e}")
        return False

# 提取并显示档案的元数据（如文件名、大小、CRC等）
def extract_metadata(file_path):
    """提取并输出7z档案的元数据。"""
    try:
        with open(file_path, "rb") as file:
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            print(f"档案文件大小: {file_size} 字节")

            # 提取档案的起始部分来检查签名
            file.seek(0)
            header = file.read(32)
            signature = header[:6]
            print(f"文件签名: {signature}")

            # 获取档案的CRC校验值
            crc_offset = 28  # 假设CRC偏移量为28
            file.seek(crc_offset)
            crc = struct.unpack("<I", file.read(4))[0]
            print(f"CRC校验值: {crc:#010x}")

    except Exception as e:
        print(f"提取元数据时发生错误: {e}")

# 主要的修复流程，结合了各种步骤来修复档案
def repair_7z_archive(file_path):
    """修复7z档案的主函数。"""
    # 在修复之前先备份原文件
    backup_path = backup_file(file_path)
    if not backup_path:
        print("无法备份文件，终止修复过程。")
        return

    print("开始7z档案修复过程...")

    # 步骤1: 提取并显示元数据
    extract_metadata(file_path)

    # 步骤2: 检查并修复起始头部
    check_and_fix_start_header(file_path)

    # 步骤3: 检查并修复结束头部
    check_and_fix_end_header(file_path)

    # 步骤4: 恢复缺失的部分（通过修复文件大小）
    recover_missing_parts(file_path)

    # 步骤5: 验证修复后的档案
    if not verify_archive(file_path):
        print("修复后的档案无法打开，正在还原备份...")
        shutil.copy2(backup_path, file_path)  # 如果修复失败，恢复备份文件
        print(f"已将文件还原为备份文件 {backup_path}")
    else:
        print("7z档案修复完成并验证成功。")

# 示例用法：修复一个档案文件
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="修复损坏的7z档案。")
    parser.add_argument("file_path", help="需要修复的7z档案的路径。")
    args = parser.parse_args()

    repair_7z_archive(args.file_path)
