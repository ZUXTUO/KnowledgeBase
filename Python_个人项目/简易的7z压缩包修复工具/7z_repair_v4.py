#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import lzma
import binascii
import sys
import os
import time
import multiprocessing
from multiprocessing import Pool
from functools import partial

SIGNATURE = b'\x37\x7A\xBC\xAF\x27\x1C'
CHUNK_SIZE = 5 * 1024 * 1024  # 每个处理块的大小（5MB）

def find_headers(data):
    """在数据中查找所有7z头签名位置"""
    positions = []
    idx = data.find(SIGNATURE)
    while idx != -1:
        positions.append(idx)
        idx = data.find(SIGNATURE, idx+1)
    return positions

def parse_start_header(data, pos):
    """解析Start Header，返回(NextHeaderOffset, NextHeaderSize, CRC)"""
    try:
        # Start Header 在偏移 pos 处。Next Header offset/size/CRC 分别在 pos+0x0C, pos+0x14, pos+0x1C。
        next_offset = struct.unpack_from('<Q', data, pos+0x0C)[0]
        next_size   = struct.unpack_from('<Q', data, pos+0x14)[0]
        next_crc    = struct.unpack_from('<I', data, pos+0x1C)[0]
    except struct.error:
        return None
    return next_offset, next_size, next_crc

def compute_crc32(buf):
    """计算CRC32校验值"""
    return binascii.crc32(buf) & 0xFFFFFFFF

def scan_lzma2_chunk(chunk_data, start_offset=0):
    """扫描并尝试从任意位置恢复LZMA2压缩数据块（处理数据块的一部分）"""
    recovered = []
    length = len(chunk_data)
    
    for i in range(length - 1):
        byte = chunk_data[i]
        # LZMA2 字典大小标识应在 0-40 之间
        if byte > 40:
            continue
            
        if i + 1 >= length:
            continue
            
        ctrl = chunk_data[i+1]
        # 控制字节不能是 0（文件结束）或无效范围 0x03-0x7F
        if ctrl == 0 or (0x03 <= ctrl <= 0x7F):
            continue
            
        # 计算字典大小
        if byte == 40:
            dict_size = 2**32 - 1
        else:
            if byte % 2 == 0:
                dict_size = 1 << (byte//2 + 12)
            else:
                dict_size = 3 * (1 << ((byte-1)//2)) + 11
                
        try:
            # 尝试使用LZMA2 RAW格式解压余下数据
            dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "dict_size": dict_size}])
            out = dec.decompress(chunk_data[i+1:])
            if out and len(out) > 100:  # 只保留有意义的数据块（至少100字节）
                real_pos = start_offset + i
                recovered.append((real_pos, dict_size, out))
        except Exception:
            continue
            
    return recovered

def process_chunk(chunk_idx, data, chunk_size):
    """处理单个数据块，用于并行执行"""
    start_pos = chunk_idx * chunk_size
    # 为了确保不遗漏跨块边界的数据，从前一个块末尾多取一些数据
    overlap = 1024  # 1KB 重叠区域
    if start_pos > 0:
        start_pos -= overlap
        
    end_pos = min(start_pos + chunk_size + overlap, len(data))
    chunk_data = data[start_pos:end_pos]
    
    print(f"处理块 {chunk_idx+1}: 从位置 {start_pos} 到 {end_pos} (大小: {len(chunk_data)/1024:.1f} KB)")
    results = scan_lzma2_chunk(chunk_data, start_pos)
    return results

def identify_file_type(data):
    """识别文件类型，基于文件头部特征"""
    # 字典格式：{文件魔数: (文件类型描述, 最小长度, 文件扩展名)}
    signatures = {
        # 图像格式
        b'\x89PNG\r\n\x1a\n': ("PNG图像", 8, ".png"),
        b'\xff\xd8\xff': ("JPEG图像", 3, ".jpg"),
        b'GIF8': ("GIF图像", 4, ".gif"),
        b'BM': ("BMP图像", 2, ".bmp"),
        b'\x00\x00\x01\x00': ("ICO图标", 4, ".ico"),
        b'\x52\x49\x46\x46': ("WEBP图像", 4, ".webp"),
        b'\x49\x49\x2A\x00': ("TIFF图像(小端)", 4, ".tiff"),
        b'\x4D\x4D\x00\x2A': ("TIFF图像(大端)", 4, ".tiff"),
        
        # 视频格式
        b'\x00\x00\x00\x18\x66\x74\x79\x70': ("MP4视频", 8, ".mp4"),
        b'\x00\x00\x00\x1C\x66\x74\x79\x70': ("MP4视频", 8, ".mp4"),
        b'\x00\x00\x00\x20\x66\x74\x79\x70': ("MP4视频", 8, ".mp4"),
        b'\x1A\x45\xDF\xA3': ("MKV/WEBM视频", 4, ".mkv"),
        b'RIFF': ("AVI视频", 4, ".avi"),
        b'\x00\x00\x01\xBA': ("MPEG视频", 4, ".mpg"),
        b'\x00\x00\x01\xB3': ("MPEG视频", 4, ".mpg"),
        b'FLV\x01': ("Flash视频", 4, ".flv"),
        
        # 音频格式
        b'ID3': ("MP3音频", 3, ".mp3"),
        b'\xFF\xFB': ("MP3音频", 2, ".mp3"),
        b'RIFF....WAVE': ("WAV音频", 12, ".wav"),
        b'OggS': ("OGG音频", 4, ".ogg"),
        b'fLaC': ("FLAC音频", 4, ".flac"),
        
        # 文档格式
        b'%PDF-': ("PDF文档", 5, ".pdf"),
        b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': ("MS Office文档", 8, ".doc"),
        b'PK\x03\x04': ("ZIP/Office XML文档", 4, ".zip"),
        b'PK\x05\x06': ("ZIP空文档", 4, ".zip"),
        b'PK\x07\x08': ("ZIP拆分文档", 4, ".zip"),
        b'{\\\rtf1': ("RTF文档", 5, ".rtf"),
        
        # 压缩与打包格式
        b'Rar!\x1A\x07': ("RAR压缩包 v1.5+", 6, ".rar"),
        b'Rar!\x1A\x07\x00': ("RAR压缩包 v5.0+", 7, ".rar"),
        b'7z\xBC\xAF\x27\x1C': ("7Z压缩包", 6, ".7z"),
        b'BZh': ("BZIP2压缩文件", 3, ".bz2"),
        b'\x1F\x8B\x08': ("GZIP压缩文件", 3, ".gz"),
        
        # 可执行格式
        b'MZ': ("EXE可执行文件", 2, ".exe"),
        b'\x7FELF': ("ELF可执行文件", 4, ""),
        b'\xCA\xFE\xBA\xBE': ("Java Class文件", 4, ".class"),
        
        # 其他格式
        b'\x25\x21\x50\x53': ("PostScript文件", 4, ".ps"),
        b'\x46\x4F\x52\x4D': ("AIFF音频", 4, ".aiff"),
        b'SQLite format': ("SQLite数据库", 13, ".sqlite"),
        b'SQLite': ("SQLite数据库", 6, ".sqlite"),
        b'IHDR': ("PNG图像数据块", 4, ".png"),
        b'<!DOCTYPE html': ("HTML文档", 14, ".html"),
        b'<html': ("HTML文档", 5, ".html"),
        b'dex\n': ("DEX文件", 4, ".dex"),
        b'-----BEGIN ': ("PEM证书", 11, ".pem"),
    }
    
    # 对于特殊格式的处理
    if len(data) >= 4 and data[:4] == b'\x00\x00\x00':
        # 可能是MP4格式，尝试查找ftyp标记
        for i in range(4, min(20, len(data)-4)):
            if data[i:i+4] == b'ftyp':
                return "MP4视频", ".mp4"

    # 检查文件头部是否匹配已知格式
    for signature, (desc, min_len, ext) in signatures.items():
        sig_len = len(signature)
        if len(data) >= sig_len:
            # 对于需要特殊处理的格式
            if signature == b'RIFF....WAVE' and len(data) >= 12:
                if data[:4] == b'RIFF' and data[8:12] == b'WAVE':
                    return desc, ext
            # 普通格式检查
            elif len(data) >= min_len and data[:sig_len] == signature:
                return desc, ext
    
    # 进一步检查文件内容中的特征
    if len(data) > 500:
        # 检查HTML文件
        content_sample = data[:500].lower()
        if b'<!doctype html' in content_sample or b'<html' in content_sample:
            return "HTML文档", ".html"
        # 检查文本文件
        if all(c < 128 and c >= 32 or c in (9, 10, 13) for c in data[:100]):
            # 检查JSON
            if data[0:1] == b'{' and b'"' in data[:20]:
                return "JSON数据", ".json"
            # 检查XML
            if data[0:1] == b'<' and b'?xml' in data[:20]:
                return "XML数据", ".xml"
            # 检查Python脚本
            if (data[:3] == b'#!/' or 
                b'def ' in content_sample or 
                b'import ' in content_sample or 
                b'class ' in content_sample):
                return "Python脚本", ".py"
            # 检查JavaScript
            if (b'function' in content_sample or 
                b'var ' in content_sample or 
                b'const ' in content_sample or
                b'let ' in content_sample):
                return "JavaScript代码", ".js"
            # 检查CSS
            if b'{' in content_sample and b':' in content_sample and b';' in content_sample:
                if (b'body' in content_sample or 
                    b'div' in content_sample or 
                    b'margin' in content_sample):
                    return "CSS样式表", ".css"
            
            return "文本文件", ".txt"
    
    return "未知格式", ".bin"

def save_recovered_file(output_dir, idx, pos, data):
    """保存恢复的文件，自动添加适当的扩展名"""
    file_type, extension = identify_file_type(data)
    outfile = f"{output_dir}/recovered_{idx}_{pos}{extension}"
    
    with open(outfile, 'wb') as f:
        f.write(data)
    
    return outfile, file_type

def main():
    if len(sys.argv) < 2:
        print("请提供待修复的7z文件路径。")
        return
        
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"错误：文件 '{filepath}' 不存在。")
        return
        
    # 获取CPU核心数
    cpu_count = multiprocessing.cpu_count()
    print(f"检测到系统有 {cpu_count} 个CPU核心，将使用并行处理。")
    
    print(f"开始读取文件: {filepath}")
    start_time = time.time()
    
    with open(filepath, 'rb') as f:
        data = f.read()
        
    # 尝试查找7z头签名
    headers = find_headers(data)
    if headers:
        for pos in headers:
            print(f"检测到7z签名头，位置: {pos}。尝试解析头部...")
            parsed = parse_start_header(data, pos)
            if parsed:
                next_offset, next_size, next_crc = parsed
                end_pos = pos + 32 + next_offset
                print(f"Head 指示的 End Header 位置: {end_pos}, 长度: {next_size}")
                if end_pos+next_size <= len(data):
                    end_data = data[end_pos:end_pos+next_size]
                    crc_val = compute_crc32(end_data)
                    if crc_val == next_crc:
                        print("End Header CRC 校验通过，头部信息有效。")
                        # 尝试使用 py7zr 提取
                        try:
                            import py7zr
                            print("尝试使用 py7zr 解压所有文件...")
                            output_dir = "恢复输出"
                            with py7zr.SevenZipFile(filepath, 'r') as archive:
                                archive.extractall(path=output_dir)
                            print(f"提取成功，文件已恢复到 '{output_dir}/' 目录。")
                            return
                        except Exception as e:
                            print(f"py7zr 提取失败: {e}")
                    else:
                        print("End Header CRC 校验失败，头部可能损坏。")
    else:
        print("未检测到完整的7z头部签名，尝试其他恢复方法...")

    # 如果头部恢复失败，使用多进程扫描文件内容以尝试恢复压缩数据块
    print("\n开始多核并行扫描文件以尝试恢复压缩数据块...")
    file_size = len(data)
    
    # 计算需要处理的块数
    num_chunks = max(1, file_size // CHUNK_SIZE)
    print(f"文件大小: {file_size/1024/1024:.2f} MB，将被分为 {num_chunks} 个块进行处理")
    
    # 使用进程池并行处理各个块
    all_results = []
    with Pool(processes=cpu_count) as pool:
        chunk_processor = partial(process_chunk, data=data, chunk_size=CHUNK_SIZE)
        results = pool.map(chunk_processor, range(num_chunks))
        
        # 合并所有结果
        for chunk_results in results:
            all_results.extend(chunk_results)
    
    # 去重（可能会在重叠区域重复发现相同的压缩块）
    unique_results = []
    seen_positions = set()
    for pos, dict_size, out in all_results:
        if pos not in seen_positions:
            seen_positions.add(pos)
            unique_results.append((pos, dict_size, out))
    
    # 按位置排序
    unique_results.sort(key=lambda x: x[0])
    
    elapsed_time = time.time() - start_time
    
    if unique_results:
        print(f"\n处理完成，共用时 {elapsed_time:.2f} 秒")
        print(f"检测到 {len(unique_results)} 个可能的 LZMA2 压缩块。")
        
        # 创建输出目录
        output_dir = "recovered_files"
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建按类型分类的目录
        type_dirs = {
            "图像": f"{output_dir}/图像",
            "视频": f"{output_dir}/视频",
            "音频": f"{output_dir}/音频",
            "文档": f"{output_dir}/文档",
            "压缩包": f"{output_dir}/压缩包",
            "可执行文件": f"{output_dir}/可执行文件",
            "其他": f"{output_dir}/其他"
        }
        
        for dir_path in type_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # 分类统计
        type_count = {}
        
        for idx, (pos, dict_size, out) in enumerate(unique_results, 1):
            outfile, file_type = save_recovered_file(output_dir, idx, pos, out)
            
            # 更新统计信息
            if file_type not in type_count:
                type_count[file_type] = 0
            type_count[file_type] += 1
            
            # 按类型分类存储
            category_dir = None
            if "图像" in file_type:
                category_dir = type_dirs["图像"]
            elif "视频" in file_type:
                category_dir = type_dirs["视频"]
            elif "音频" in file_type:
                category_dir = type_dirs["音频"]
            elif any(x in file_type for x in ["文档", "PDF", "Office", "文本"]):
                category_dir = type_dirs["文档"]
            elif "压缩包" in file_type:
                category_dir = type_dirs["压缩包"]
            elif "可执行文件" in file_type:
                category_dir = type_dirs["可执行文件"]
            else:
                category_dir = type_dirs["其他"]
            
            if category_dir:
                # 复制文件到分类目录
                import shutil
                category_file = os.path.join(category_dir, os.path.basename(outfile))
                shutil.copy2(outfile, category_file)
            
            print(f"成功恢复块 {idx}: 位置 {pos}, 字典大小 {dict_size}, 数据大小 {len(out)} 字节")
            print(f"  文件类型: {file_type}")
            print(f"  保存为: {outfile}")
            
        # 输出恢复统计信息
        print("\n恢复文件统计:")
        for file_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {file_type}: {count} 个文件")
            
        print(f"\n恢复的文件已按类型分类保存到 '{output_dir}/' 目录下的相应子文件夹中。")
    else:
        print(f"\n处理完成，共用时 {elapsed_time:.2f} 秒")
        print("未能检测到有效的 LZMA2 压缩块，恢复失败。")

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Windows上打包exe时需要
    main()