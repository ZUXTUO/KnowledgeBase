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
import numpy as np
import mmap

try:
    from numba import cuda, int32, uint8
    NUMBA_CUDA_AVAILABLE = True
    if not cuda.is_available():
        print("Numba CUDA: CUDA 在此系统上不可用。GPU 加速将被禁用。")
        NUMBA_CUDA_AVAILABLE = False
except ImportError:
    print("未找到 Numba 库。GPU 加速将被禁用。请使用以下命令安装: pip install numba numpy")
    NUMBA_CUDA_AVAILABLE = False

SIGNATURE = b'\x37\x7A\xBC\xAF\x27\x1C'
CHUNK_SIZE = 50 * 1024 * 1024
USE_GPU_SCAN = NUMBA_CUDA_AVAILABLE

def find_headers(data_mmap, file_size_to_check):
    positions = []
    idx = 0
    while idx < file_size_to_check:
        idx = data_mmap.find(SIGNATURE, idx)
        if idx == -1:
            break
        positions.append(idx)
        idx += 1 
    return positions

def parse_start_header(data_mmap, pos):
    try:
        header_data = data_mmap[pos : pos + 32]
        if len(header_data) < 32:
            return None
        next_offset = struct.unpack_from('<Q', header_data, 0x0C)[0]
        next_size = struct.unpack_from('<Q', header_data, 0x14)[0]
        next_crc = struct.unpack_from('<I', header_data, 0x1C)[0]
    except struct.error:
        return None
    return next_offset, next_size, next_crc

def compute_crc32(buf):
    return binascii.crc32(buf) & 0xFFFFFFFF

if NUMBA_CUDA_AVAILABLE:
    @cuda.jit
    def find_potential_lzma_starts_gpu_kernel(chunk_data_gpu, out_indices, out_count):
        idx = cuda.grid(1)
        if idx < chunk_data_gpu.shape[0] - 1:
            byte = chunk_data_gpu[idx]
            if byte <= 40:
                ctrl = chunk_data_gpu[idx+1]
                if not (ctrl == 0 or (0x03 <= ctrl <= 0x7F)):
                    slot = cuda.atomic.add(out_count, 0, 1)
                    if slot < out_indices.shape[0]:
                        out_indices[slot] = idx

    def find_potential_lzma_starts_gpu(chunk_data_np):
        potential_indices_gpu = cuda.device_array(len(chunk_data_np), dtype=np.int32)
        count_gpu = cuda.device_array(1, dtype=np.int32)
        count_gpu.copy_to_device(np.array([0], dtype=np.int32))
        threads_per_block = 256
        blocks_per_grid = (chunk_data_np.shape[0] + (threads_per_block - 1)) // threads_per_block
        find_potential_lzma_starts_gpu_kernel[blocks_per_grid, threads_per_block](
            chunk_data_np, potential_indices_gpu, count_gpu
        )
        cuda.synchronize()
        actual_count = count_gpu.copy_to_host()[0]
        if actual_count > 0:
            host_indices = potential_indices_gpu.copy_to_host()[:actual_count]
            return host_indices
        return np.array([], dtype=np.int32)

def scan_lzma2_chunk(chunk_data_bytes, file_offset_of_chunk_start, use_gpu=False):
    recovered = []
    length = len(chunk_data_bytes)
    potential_starts = []

    if use_gpu and NUMBA_CUDA_AVAILABLE and length > 0:
        try:
            chunk_data_np = np.frombuffer(chunk_data_bytes, dtype=np.uint8)
            device_chunk_data = cuda.to_device(chunk_data_np)
            potential_starts_gpu = find_potential_lzma_starts_gpu(device_chunk_data)
            del device_chunk_data 
            cuda.synchronize()
            potential_starts = [int(idx) for idx in potential_starts_gpu]
        except Exception as e:
            print(f"块偏移 {file_offset_of_chunk_start} 处的 GPU 扫描失败: {e}。回退到 CPU 扫描。")
            use_gpu = False
            potential_starts = []

    if not (use_gpu and NUMBA_CUDA_AVAILABLE and potential_starts) or (use_gpu and not potential_starts and NUMBA_CUDA_AVAILABLE and length > 0) : # Ensure CPU scan runs if GPU was skipped or failed and cleared potential_starts
        for i in range(length - 1):
            byte = chunk_data_bytes[i]
            if byte > 40:
                continue
            ctrl = chunk_data_bytes[i+1]
            if ctrl == 0 or (0x03 <= ctrl <= 0x7F):
                continue
            potential_starts.append(i)

    for i in potential_starts:
        byte = chunk_data_bytes[i]
        if byte == 40:
            dict_size = 2**32 - 1
        else:
            if byte % 2 == 0:
                dict_size = 1 << (byte//2 + 12)
            else:
                dict_size = 3 * (1 << ((byte-1)//2 + 11))
        try:
            dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "dict_size": dict_size}])
            out = dec.decompress(chunk_data_bytes[i+1:])
            if out and len(out) > 100: 
                real_pos = file_offset_of_chunk_start + i
                recovered.append((real_pos, dict_size, out))
        except Exception:
            continue
    return recovered

def process_chunk(chunk_idx, filepath, chunk_size, use_gpu_for_scan, total_file_size):
    results = []
    try:
        with open(filepath, 'rb') as f_proc:
            with mmap.mmap(f_proc.fileno(), 0, access=mmap.ACCESS_READ) as data_mmap:
                start_pos_in_chunk_logic = chunk_idx * chunk_size 
                overlap = 1024 
                
                read_start_offset = max(0, start_pos_in_chunk_logic - overlap)
                read_end_offset = min(start_pos_in_chunk_logic + chunk_size + overlap, total_file_size)

                if read_start_offset >= read_end_offset:
                    return []

                chunk_data_bytes = data_mmap[read_start_offset:read_end_offset]
                
                print(f"处理块 {chunk_idx+1}: 从文件位置 {read_start_offset} 到 {read_end_offset} (读取大小: {len(chunk_data_bytes)/1024:.1f} KB)")
                
                # 完全修改为GPU处理流程，不在scan_lzma2_chunk中混合处理
                if use_gpu_for_scan and NUMBA_CUDA_AVAILABLE and len(chunk_data_bytes) > 0:
                    try:
                        # 直接使用GPU寻找潜在的LZMA起始点
                        chunk_data_np = np.frombuffer(chunk_data_bytes, dtype=np.uint8)
                        device_chunk_data = cuda.to_device(chunk_data_np)
                        
                        # 这里是关键 - 确保GPU负载更高
                        threads_per_block = 1024  # 增加每块线程数
                        blocks_per_grid = (chunk_data_np.shape[0] + (threads_per_block - 1)) // threads_per_block
                        
                        # 确保启动足够的GPU线程
                        potential_indices_gpu = cuda.device_array(min(10000000, len(chunk_data_np)), dtype=np.int32)
                        count_gpu = cuda.device_array(1, dtype=np.int32)
                        count_gpu.copy_to_device(np.array([0], dtype=np.int32))
                        
                        print(f"  启动GPU内核: {blocks_per_grid} 块 x {threads_per_block} 线程")
                        
                        # 直接在这里调用GPU内核，而不是通过scan_lzma2_chunk函数
                        find_potential_lzma_starts_gpu_kernel[blocks_per_grid, threads_per_block](
                            device_chunk_data, potential_indices_gpu, count_gpu
                        )
                        cuda.synchronize()  # 确保GPU计算完成
                        
                        actual_count = count_gpu.copy_to_host()[0]
                        print(f"  GPU找到 {actual_count} 个潜在LZMA起始点")
                        
                        # 只有在GPU找到潜在点时才进行处理
                        if actual_count > 0:
                            host_indices = potential_indices_gpu.copy_to_host()[:min(actual_count, 10000000)]
                            
                            # 并行处理潜在的LZMA起始点
                            sub_results = []
                            # 为避免处理太多点，可以限制点的数量
                            max_points_to_process = min(actual_count, 5000)  # 限制处理点数
                            
                            for i in sorted(host_indices[:max_points_to_process]):
                                byte = chunk_data_bytes[i]
                                if byte == 40:
                                    dict_size = 2**32 - 1
                                else:
                                    if byte % 2 == 0:
                                        dict_size = 1 << (byte//2 + 12)
                                    else:
                                        dict_size = 3 * (1 << ((byte-1)//2 + 11))
                                try:
                                    dec = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "dict_size": dict_size}])
                                    out = dec.decompress(chunk_data_bytes[i+1:i+1+100000])  # 限制解压长度
                                    if out and len(out) > 100: 
                                        real_pos = read_start_offset + i
                                        sub_results.append((real_pos, dict_size, out))
                                except Exception:
                                    continue
                            
                            results = sub_results
                            print(f"  块 {chunk_idx+1} GPU处理: 成功提取 {len(results)} 个LZMA块")
                        else:
                            print("  GPU未找到潜在LZMA起始点")
                            
                        # 释放GPU内存
                        del device_chunk_data
                        del potential_indices_gpu
                        del count_gpu
                        cuda.synchronize()
                        
                    except Exception as e:
                        print(f"  块 {chunk_idx+1} GPU处理失败: {e}。回退到CPU扫描。")
                        results = scan_lzma2_chunk(chunk_data_bytes, read_start_offset, use_gpu=False)
                else:
                    # 回退到CPU处理
                    results = scan_lzma2_chunk(chunk_data_bytes, read_start_offset, use_gpu=False)
    except Exception as e:
        print(f"处理块 {chunk_idx+1} 时发生错误: {e}")
    return results

# def process_chunk(chunk_idx, filepath, chunk_size, use_gpu_for_scan, total_file_size):
#     results = []
#     try:
#         with open(filepath, 'rb') as f_proc:
#             with mmap.mmap(f_proc.fileno(), 0, access=mmap.ACCESS_READ) as data_mmap:
#                 start_pos_in_chunk_logic = chunk_idx * chunk_size 
#                 overlap = 1024 
                
#                 read_start_offset = max(0, start_pos_in_chunk_logic - overlap)
#                 read_end_offset = min(start_pos_in_chunk_logic + chunk_size + overlap, total_file_size)

#                 if read_start_offset >= read_end_offset:
#                     return []

#                 chunk_data_bytes = data_mmap[read_start_offset:read_end_offset]
                
#                 print(f"处理块 {chunk_idx+1}: 从文件位置 {read_start_offset} 到 {read_end_offset} (读取大小: {len(chunk_data_bytes)/1024:.1f} KB)")
#                 results = scan_lzma2_chunk(chunk_data_bytes, read_start_offset, use_gpu=use_gpu_for_scan)
#     except Exception as e:
#         print(f"处理块 {chunk_idx+1} 时发生错误: {e}")
#     return results

def identify_file_type(data):
    signatures = {
        b'\x89PNG\r\n\x1a\n': ("PNG 图像", 8, ".png"),
        b'\xFF\xD8\xFF': ("JPEG 图像", 3, ".jpg"),
        b'GIF87a': ("GIF 图像 (87a)", 6, ".gif"),
        b'GIF89a': ("GIF 图像 (89a)", 6, ".gif"),
        b'BM': ("BMP 图像", 2, ".bmp"),
        b'\x00\x00\x01\x00': ("ICO 图标", 4, ".ico"),
        b'\x00\x00\x02\x00': ("CUR 光标", 4, ".cur"),
        b'II\x2A\x00': ("TIFF 图像 (小端)", 4, ".tiff"),
        b'MM\x00\x2A': ("TIFF 图像 (大端)", 4, ".tiff"),
        b'8BPS': ("Photoshop 文档", 4, ".psd"),
        b'P1': ("PBM 图像 (ASCII)", 2, ".pbm"),
        b'P2': ("PGM 图像 (ASCII)", 2, ".pgm"),
        b'P3': ("PPM 图像 (ASCII)", 2, ".ppm"),
        b'P4': ("PBM 图像 (二进制)", 2, ".pbm"),
        b'P5': ("PGM 图像 (二进制)", 2, ".pgm"),
        b'P6': ("PPM 图像 (二进制)", 2, ".ppm"),
        b'\x25\x50\x44\x46\x2D': ("Adobe PDF 文档", 5, ".pdf"),
        b'AI\x00': ("Adobe Illustrator 文件", 2, ".ai"),
        b'<?xml version="1.0" encoding="utf-8"?>\n<svg': ("SVG 矢量图像 (带声明)", 38, ".svg"),
        b'<svg': ("SVG 矢量图像", 4, ".svg"),
        b'\x1A\x45\xDF\xA3': ("MKV/WEBM 视频", 4, ".mkv"),
        b'\x00\x00\x01\xBA': ("MPEG-PS 视频 (节目流)", 4, ".mpg"),
        b'\x00\x00\x01\xB3': ("MPEG-TS 视频 (传输流)", 4, ".ts"),
        b'FLV\x01': ("Flash 视频 (FLV)", 4, ".flv"),
        b'RIFF': ("RIFF 容器 (AVI/WAV等)", 4, ".avi"),
        b'MOVI': ("QuickTime 影片 (MOOV atom)", 4, ".mov"),
        b'mdat': ("ISO Base Media File Data (mdat atom)", 4, ".mp4"),
        b'WMV1': ("Windows Media Video", 4, ".wmv"),
        b'ASF ': ("Advanced Systems Format (ASF/WMV/WMA)", 4, ".asf"),
        b'OggS': ("Ogg 容器 (音频/视频)", 4, ".ogg"),
        b'ID3': ("MP3 音频 (ID3 Tag)", 3, ".mp3"),
        b'\xFF\xFB': ("MP3 音频 (帧同步)", 2, ".mp3"),
        b'\xFF\xF3': ("MP3 音频 (帧同步, MPEG2.5 Layer3)", 2, ".mp3"),
        b'\xFF\xF2': ("MP3 音频 (帧同步, MPEG2 Layer3)", 2, ".mp3"),
        b'fLaC': ("FLAC 音频", 4, ".flac"),
        b'MAC ': ("Monkey's Audio (APE)", 4, ".ape"),
        b'APETAGEX': ("APE Tag", 8, ".ape"),
        b'FORM': ("IFF 容器 (AIFF/8SVX等)", 4, ".aiff"),
        b'AU\x00': ("NeXT/Sun AU 音频", 2, ".au"),
        b'.snd': ("NeXT/Sun AU 音频 (另一种)",4, ".au"),
        b'OpusHead': ("Opus 音频", 8, ".opus"),
        b'AMR\n': ("Adaptive Multi-Rate Codec", 4, ".amr"),
        b'#!AMR\n': ("Adaptive Multi-Rate Codec (带shebang)", 6, ".amr"),
        b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': ("MS Office 文档 (OLECF)", 8, ".doc/.xls/.ppt"),
        b'PK\x03\x04': ("ZIP 压缩包 / Office XML (docx, xlsx, pptx)", 4, ".zip"),
        b'PK\x05\x06': ("ZIP 空归档或结束记录", 4, ".zip"),
        b'PK\x07\x08': ("ZIP 分卷归档", 4, ".zip"),
        b'{\\rtf1': ("RTF 文档", 5, ".rtf"),
        b'{\\fonttbl':("RTF 文档 (字体表)",8,".rtf"),
        b'%%EOF': ("PostScript/EPS 文件结束", 5, ".ps"),
        b'\x25\x21\x50\x53\x2D\x41\x64\x6F\x62\x65': ("PostScript 文件 (Adobe)", 10, ".ps"),
        b'FWS': ("SWF (Flash) 未压缩", 3, ".swf"),
        b'CWS': ("SWF (Flash) ZLIB压缩", 3, ".swf"),
        b'ZWS': ("SWF (Flash) LZMA压缩", 3, ".swf"),
        b'Rar!\x1A\x07\x00': ("RAR 压缩包 (v1.5-4.x)", 7, ".rar"),
        b'Rar!\x1A\x07\x01\x00': ("RAR 压缩包 (v5.0+)", 8, ".rar"),
        b'\x37\x7A\xBC\xAF\x27\x1C': ("7z 压缩包", 6, ".7z"),
        b'BZh': ("BZIP2 压缩文件", 3, ".bz2"),
        b'\x1F\x8B\x08': ("GZIP 压缩文件", 3, ".gz"),
        b'\x1F\x9D': ("Lempel-Ziv Compress (LZC)", 2, ".Z"),
        b'\x1F\xA0': ("Lempel-Ziv-Welch (LZW)", 2, ".Z"),
        b'\xFD\x37\x7A\x58\x5A\x00': ("XZ 压缩文件", 6, ".xz"),
        b'\x5D\x00\x00\x80': ("LZMA Alone 压缩 (旧格式)", 4, ".lzma"),
        b'MSCF': ("Microsoft Cabinet (CAB)", 4, ".cab"),
        b'ustar\x00': ("TAR 归档 (ustar)", 6, ".tar"),
        b'ustar  \x00': ("TAR 归档 (POSIX ustar)", 8, ".tar"),
        b'MZ': ("Windows PE 可执行文件 (EXE/DLL)", 2, ".exe"),
        b'\x7FELF': ("ELF 可执行/共享库", 4, ""),
        b'\xCA\xFE\xBA\xBE': ("Java Class 文件 / Mach-O Fat Binary", 4, ".class"),
        b'\xFE\xED\xFA\xCE': ("Mach-O 32位 (macOS/iOS)", 4, ""),
        b'\xFE\xED\xFA\xCF': ("Mach-O 64位 (macOS/iOS)", 4, ""),
        b'\xCE\xFA\xED\xFE': ("Mach-O 32位 (小端)", 4, ""),
        b'\xCF\xFA\xED\xFE': ("Mach-O 64位 (小端)", 4, ""),
        b'dex\n035\x00': ("Android DEX 文件", 8, ".dex"),
        b'dey\n036\x00': ("Android ODEX 文件", 8, ".dey"),
        b'#!/': ("Shell 脚本 (Shebang)", 3, ".sh"),
        b'regf': ("Windows Registry 文件", 4, ".reg"),
        b'SQLite format 3\x00': ("SQLite 数据库", 16, ".sqlite"),
        b'Standard Jet DB': ("Microsoft Access MDB/ACCDB", 15, ".mdb"),
        b'**CR**': ("MySQL FRM 文件", 6, ".frm"),
        b'\x00\x01\x00\x00\x00': ("TrueType 字体 (TTF)", 5, ".ttf"),
        b'OTTO': ("OpenType 字体 (OTF)", 4, ".otf"),
        b'true': ("TrueType 字体 (另一种)", 4, ".ttf"),
        b'typ1': ("Type 1 字体", 4, ".pfa"),
        b'LWFN': ("Mac Font Suitcase", 4, ".suit"),
        b'FFIL': ("Mac Font Suitcase (FFIL)", 4, ".suit"),
        b'wOFF': ("Web Open Font Format (WOFF)", 4, ".woff"),
        b'wOF2': ("Web Open Font Format 2.0 (WOFF2)", 4, ".woff2"),
        b'NES\x1A': ("Nintendo NES ROM", 4, ".nes"),
        b'VMCI': ("VMware VMCI Saved State File", 4, ".vmss"),
        b'KDMV': ("VMware VMDK Sparse Disk", 4, ".vmdk"),
        b'VBOX': ("VirtualBox Hard Disk Image", 4, ".vdi"),
        b'<<<_EOF_>>>': ("Virtual PC VHD Disk Image", 12, ".vhd"),
        b'ebml': ("EBML (基石, 如MKV)", 4, ".mkv"),
        b'-----BEGIN CERTIFICATE-----': ("PEM 证书", 27, ".pem"),
        b'-----BEGIN RSA PRIVATE KEY-----': ("PEM RSA 私钥", 29, ".key"),
        b'-----BEGIN PGP PUBLIC KEY BLOCK-----': ("PGP 公钥块",35,".asc"),
        b'-----BEGIN PGP PRIVATE KEY BLOCK-----':("PGP 私钥块",36,".asc"),
        b'CR2\x00': ("Canon RAW 2 图像", 4, ".cr2"),
        b'SRF\x00': ("Sony RAW 图像", 4, ".srf"),
        b'NEF\x00': ("Nikon RAW 图像", 4, ".nef"),
        b'ORF\x00': ("Olympus RAW 图像", 4, ".orf"),
        b'ARW\x00': ("Sony Alpha RAW 图像",4,".arw"),
        b'RW2\x00': ("Panasonic RAW 图像",4,".rw2"),
        b'torr': ("BitTorrent 元数据文件", 4, ".torrent"),
        b'd8:announce': ("BitTorrent 元数据文件 (更具体)", 11, ".torrent"),
        b'PROP': ("Subversion 属性文件", 4, ".prop"),
        b'\xAC\xED\x00\x05': ("Java 序列化对象", 4, ".ser"),
        b'INDX': ("NTFS $I30 Index Allocation Entry", 4, ""),
        b'FILE': ("NTFS FILE Record Segment", 4, ""),
        b'8SSD': ("Palm OS 数据库", 4, ".pdb"),
        b'DICM': ("DICOM 医学图像", 4, ".dcm"),
        b'gsf ': ("Ghostscript 文件", 4, ".ps"),
        b'Cues': ("APE Cue Sheet", 4, ".cue"),
        b'FLAC': ("Free Lossless Audio Codec (Stream marker)", 4, ".flac"),
        b'WAVE': ("Waveform Audio File Format (Chunk ID)", 4, ".wav"),
        b'AVI ': ("Audio Video Interleave (List Type)", 4, ".avi"),
        b'WEBP': ("WebP Image (RIFF Subtype)", 4, ".webp"),
        b'ftyp': ("ISO Base Media File Type Box", 4, ".mp4"),
    }

    data_len = len(data)
    data_lower_case_prefix = data[:50].lower()

    if data_len >= 12:
        if data[:4] == b'RIFF':
            if data[8:12] == b'WAVE': return "WAV 音频", ".wav"
            if data[8:12] == b'AVI ': return "AVI 视频", ".avi"
            if data[8:12] == b'WEBP': return "WebP 图像", ".webp"
            if data[8:12] == b'ACON': return "RIFF ACON (Amiga)", ".acon"
        if data[4:8] == b'ftyp':
            brand = data[8:12].decode('latin-1', errors='ignore').strip()
            major_brand = data[8:12]
            
            if major_brand in [b'isom', b'iso2', b'iso3', b'iso4', b'iso5', b'iso6', b'mp41', b'mp42', b'avc1', b'qt  ']:
                return f"MP4/MOV 视频 (ftyp: {brand})", ".mp4"
            if major_brand == b'm4a ': return f"Apple M4A 音频 (ftyp: {brand})", ".m4a"
            if major_brand == b'm4v ': return f"Apple M4V 视频 (ftyp: {brand})", ".m4v"
            if major_brand == b'3gp': return f"3GPP 移动视频 (ftyp: {brand})", ".3gp"
            if major_brand == b'heic': return f"HEIC 图像 (ftyp: {brand})", ".heic"
            if major_brand == b'crx ': return f"Canon CR3 RAW 图像 (ftyp: {brand})", ".cr3"
            return f"ISO 基础媒体文件 (ftyp: {brand})", ".mov"

    if data_len >= 262:
        if data[257:262] == b'ustar':
            return "TAR 归档 (ustar)", ".tar"

    if data_len >= 132 and data[128:132] == b'DICM':
        return "DICOM 医学图像文件", ".dcm"
        
    if data_len > 4 and data[4:].startswith(b'Standard Jet DB'):
        return "Microsoft Access 数据库", ".mdb"

    for signature, (desc, min_len, ext) in signatures.items():
        sig_len = len(signature)
        if data_len >= sig_len and data_len >= min_len:
            if signature.startswith(b"<html") or signature.startswith(b"<!doctype html") or signature.startswith(b"<?xml") or signature.startswith(b"<svg"):
                if data_lower_case_prefix.startswith(signature):
                    return desc, ext
            elif data[:sig_len] == signature:
                return desc, ext
    
    if data_len > 100:
        is_likely_text = False
        try:
            data[:200].decode('utf-8')
            ascii_text_chars = 0
            for byte_val in data[:200]:
                if 32 <= byte_val <= 126 or byte_val in (9, 10, 13):
                    ascii_text_chars +=1
            if ascii_text_chars / min(200, data_len) > 0.80:
                is_likely_text = True
        except UnicodeDecodeError:
            is_likely_text = False

        if is_likely_text:
            content_sample_lower = data[:500].lower()
            stripped_data_start = data.lstrip()
            if stripped_data_start.startswith(b'{') and (b'"' in data[:100] or b':' in data[:100]):
                 return "JSON 数据", ".json"
            if stripped_data_start.startswith(b'[') and (b'"' in data[:100] or b'{' in data[:100] or b']' == stripped_data_start[-1:]):
                 return "JSON 数组", ".json"
            
            if stripped_data_start.startswith(b'<'):
                if b'<?xml' in content_sample_lower[:50] or b'<xsl' in content_sample_lower[:50]:
                    return "XML 数据", ".xml"
                if b'<svg' in content_sample_lower[:50] and b'</svg>' in content_sample_lower:
                    return "SVG 矢量图像", ".svg"
                if (b'<!doctype html' in content_sample_lower[:50] or \
                    b'<html' in content_sample_lower[:50]) and \
                    (b'</html' in content_sample_lower or b'<body' in content_sample_lower):
                    return "HTML 文档", ".html"

            if (data.startswith(b'#!') and (b'python' in data[:50] or b'env python' in data[:50])) or \
               any(kw in content_sample_lower for kw in [b'def ', b'import ', b'class ', b'print(', b'from ']):
                return "Python 脚本", ".py"
            if any(kw in content_sample_lower for kw in [b'function', b'var ', b'const ', b'let ', b'console.log', b'document.getelementbyid', b'=>', b'async ']):
                return "JavaScript 代码", ".js"
            if b'{' in content_sample_lower and b':' in content_sample_lower and b';' in content_sample_lower and \
               any(kw in content_sample_lower for kw in [b'body', b'div', b'margin', b'color:', b'font-size', b'background:', b'@media']):
                return "CSS 样式表", ".css"
            if data.startswith(b'#!') and (b'/bin/sh' in data[:50] or b'/bin/bash' in data[:50] or b'/usr/bin/env sh' in data[:50]):
                return "Shell 脚本", ".sh"
            if b'SELECT ' in data[:100].upper() and b'FROM ' in data[:200].upper() and (b'WHERE ' in data[:300].upper() or data.endswith(b';')):
                return "SQL 脚本", ".sql"
            if b'---' == data[:3] and (b'\n...' in data or b'\r\n...' in data):
                return "YAML 数据", ".yaml"
            if b'#include' in content_sample_lower[:100] and (b'int main(' in content_sample_lower or b'void main(' in content_sample_lower):
                return "C/C++ 源代码", ".c"
            if b'package ' in content_sample_lower[:50] and b'import "fmt"' in content_sample_lower:
                return "Go 源代码", ".go"
            if b'public class' in content_sample_lower[:100] and b'static void main' in content_sample_lower:
                return "Java 源代码", ".java"
            if b'namespace ' in content_sample_lower[:100] and b'class ' in content_sample_lower and (b'static void Main' in data or b'Console.WriteLine' in data):
                 return "C# 源代码", ".cs"
            if b'Sub Main()' in data[:100] or b'Function ' in data[:100] and b'End Function' in data:
                return "VB.NET / VBScript 代码", ".vb"
            if data.startswith(b'<?php'):
                return "PHP 脚本", ".php"

            return "文本文件", ".txt"
    
    return "未知格式", ".bin"

def save_recovered_file(output_dir_base, idx, pos, data):
    file_type_desc, extension = identify_file_type(data)
    category = "其他"
    if "图像" in file_type_desc: category = "图像"
    elif "视频" in file_type_desc: category = "视频"
    elif "音频" in file_type_desc: category = "音频"
    elif any(x in file_type_desc for x in ["文档", "PDF", "Office", "文本", "JSON", "XML", "脚本", "代码", "样式表", "数据", "源代码"]):
        category = "文档与代码"
    elif "压缩包" in file_type_desc or "归档" in file_type_desc: category = "压缩包与归档"
    elif any(x in file_type_desc for x in ["可执行", "ELF", "Mach-O", "DLL", "库"]):
        category = "可执行与库"
    elif "数据库" in file_type_desc: category = "数据库"
    elif "证书" in file_type_desc or "密钥" in file_type_desc : category = "证书与密钥"
    elif "字体" in file_type_desc: category = "字体"
    elif "ROM" in file_type_desc or "映像" in file_type_desc or "VM" in file_type_desc: category = "磁盘映像与ROM"

    category_dir = os.path.join(output_dir_base, category)
    os.makedirs(category_dir, exist_ok=True)
    outfile = os.path.join(category_dir, f"已恢复_{idx}_{pos}{extension}")
    counter = 1
    base_outfile = outfile
    while os.path.exists(outfile):
        outfile = f"{os.path.splitext(base_outfile)[0]}_({counter}){os.path.splitext(base_outfile)[1]}"
        counter += 1
    with open(outfile, 'wb') as f:
        f.write(data)
    return outfile, file_type_desc, category

def main():
    if len(sys.argv) < 2:
        print("请提供待修复的 7z 文件路径。")
        print("用法: python script.py <filepath.7z> [--no-gpu]")
        return
        
    filepath = sys.argv[1]
    
    global USE_GPU_SCAN
    if len(sys.argv) > 2 and sys.argv[2] == '--no-gpu':
        print("用户通过 --no-gpu 参数明确禁用 GPU 扫描。")
        USE_GPU_SCAN = False
    elif not NUMBA_CUDA_AVAILABLE:
        print("GPU 扫描已禁用，因为 Numba CUDA 不可用或无法正常工作。")
        USE_GPU_SCAN = False
    else:
        print("Numba CUDA 可用。将尝试使用 GPU 进行 LZMA 块搜索。")
        USE_GPU_SCAN = True

    cpu_count = multiprocessing.cpu_count()
    print(f"检测到系统有 {cpu_count} 个 CPU 核心，将使用并行处理。")
    print(f"开始读取文件: {filepath}")
    start_time = time.time()
    
    file_size = 0
    try:
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            print(f"错误：文件 '{filepath}' 为空。")
            return
    except FileNotFoundError:
        print(f"错误：文件 '{filepath}' 不存在。")
        return
    except Exception as e:
        print(f"获取文件大小 '{filepath}' 时发生错误: {e}")
        return
        
    recovered_via_header = False
    try:
        with open(filepath, 'rb') as f_header_check:
            with mmap.mmap(f_header_check.fileno(), 0, access=mmap.ACCESS_READ) as mmap_data_for_headers:
                headers = find_headers(mmap_data_for_headers, file_size)
                if headers:
                    for pos in headers:
                        print(f"检测到 7z 签名头，位置: {pos}。尝试解析头部...")
                        parsed = parse_start_header(mmap_data_for_headers, pos)
                        if parsed:
                            next_offset, next_size, next_crc = parsed
                            end_header_start_pos = pos + 32 + next_offset 
                            print(f"起始头 (位置 {pos}) 指示的结束头预期位置: {end_header_start_pos}, 预期长度: {next_size}")
                            
                            if end_header_start_pos + next_size <= file_size and next_size > 0 :
                                end_header_data_bytes = mmap_data_for_headers[end_header_start_pos : end_header_start_pos + next_size]
                                crc_val = compute_crc32(end_header_data_bytes)
                                
                                if crc_val == next_crc:
                                    print(f"结束头 CRC (0x{next_crc:08X}) 校验通过 (计算值: 0x{crc_val:08X})，头部信息有效。")
                                    try:
                                        import py7zr
                                        print("尝试使用 py7zr 解压所有文件...")
                                        output_dir_py7zr = "恢复输出_py7zr"
                                        os.makedirs(output_dir_py7zr, exist_ok=True)
                                        with py7zr.SevenZipFile(filepath, 'r') as archive:
                                            archive.extractall(path=output_dir_py7zr)
                                        print(f"py7zr 提取成功，文件已恢复到 '{output_dir_py7zr}/' 目录。")
                                        recovered_via_header = True
                                        break 
                                    except ImportError:
                                        print("py7zr 模块未安装。如果头部有效，请尝试手动使用 7-Zip 或安装 'pip install py7zr'。")
                                    except Exception as e:
                                        print(f"py7zr 提取失败: {e}")
                                else:
                                    print(f"结束头 CRC (0x{next_crc:08X}) 校验失败 (计算值: 0x{crc_val:08X})，头部可能损坏。")
                            else:
                                print(f"结束头位置或大小 ({end_header_start_pos}, {next_size}) 超出文件范围 ({file_size})。")
                        else:
                            print(f"无法解析位置 {pos} 处的起始头。")
                else:
                    print("未检测到 7z 头部签名。")
    except Exception as e:
        print(f"处理文件头部时发生错误: {e}")


    if recovered_via_header:
        print("\n由于通过标准 7z 头部成功提取，深度扫描将被跳过。")
        print(f"总用时: {time.time() - start_time:.2f} 秒")
        return

    print("\n开始多核并行扫描文件以尝试恢复 LZMA2 压缩数据块...")
    num_chunks = max(1, (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE)
    print(f"文件大小: {file_size/1024/1024:.2f} MB，将被分为 {num_chunks} 个块进行处理 (每块约 {CHUNK_SIZE/1024/1024:.1f} MB)")
    
    all_results = []
    tasks = [(idx, filepath, CHUNK_SIZE, USE_GPU_SCAN, file_size) for idx in range(num_chunks)]

    try:
        with Pool(processes=cpu_count) as pool:
            results_from_pool = pool.starmap(process_chunk, tasks)
            for chunk_results in results_from_pool:
                if chunk_results:
                    all_results.extend(chunk_results)
    except Exception as e:
        print(f"多进程处理时发生错误: {e}")
        print("尝试单进程回退...")
        all_results = []
        for task_args in tasks:
            chunk_results = process_chunk(*task_args)
            if chunk_results:
                all_results.extend(chunk_results)

    unique_results = []
    seen_positions = set()
    for res_item in all_results:
        pos, dict_size, out_data = res_item
        if pos not in seen_positions:
            seen_positions.add(pos)
            unique_results.append(res_item)
    
    unique_results.sort(key=lambda x: x[0])
    elapsed_time = time.time() - start_time
    
    if unique_results:
        print(f"\n处理完成，共用时 {elapsed_time:.2f} 秒")
        print(f"检测到 {len(unique_results)} 个可能的 LZMA2 压缩块。")
        
        output_dir_base = "已恢复文件_深度扫描"
        os.makedirs(output_dir_base, exist_ok=True)
        
        type_count = {}
        category_stats = {}
        
        for idx, (pos, dict_size, out_data) in enumerate(unique_results, 1):
            outfile, file_type_desc, category = save_recovered_file(output_dir_base, idx, pos, out_data)
            type_count[file_type_desc] = type_count.get(file_type_desc, 0) + 1
            category_stats[category] = category_stats.get(category, 0) + 1
            print(f"成功恢复块 {idx}: 位置 {pos}, 字典大小 {dict_size}, 数据大小 {len(out_data)} 字节")
            print(f"  文件类型: {file_type_desc}")
            print(f"  保存到: {outfile} (分类: {category})")
            
        print("\n恢复文件统计 (按具体类型):")
        for file_type, count in sorted(type_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  {file_type}: {count} 个文件")

        print("\n恢复文件统计 (按分类):")
        for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} 个文件")
            
        print(f"\n恢复的文件已按类型分类保存到 '{output_dir_base}/' 目录下的相应子文件夹中。")
    else:
        print(f"\n处理完成，共用时 {elapsed_time:.2f} 秒")
        print("未能通过深度扫描检测到有效的 LZMA2 压缩块，恢复失败。")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            current_start_method = multiprocessing.get_start_method(allow_none=True)
            if current_start_method != 'spawn':
                 multiprocessing.set_start_method('spawn', force=True)
        elif sys.platform.startswith('win32'):
            pass
    except RuntimeError as e:
        print(f"警告: 设置多处理启动方法时发生运行时错误: {e}。GPU 加速可能无法按预期工作。")
    except Exception as e:
        print(f"警告: 设置多处理启动方法时发生未知错误: {e}。")
    main()
