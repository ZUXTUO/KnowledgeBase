#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct
import os
import subprocess
import shutil
import zlib
import hashlib
import tempfile
import re
import time
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any, Union, BinaryIO

class SevenZipAdvancedRecovery:
    """7z压缩包高级恢复工具"""
    
    # 7z文件格式常量
    SIGNATURE = b'\x37\x7A\xBC\xAF\x27\x1C'  # 7z签名
    SUPPORTED_VERSIONS = [b'\x00\x03', b'\x00\x04'] # 支持的版本号
    START_HEADER_SIZE = 32                    # 起始头大小
    END_HEADER_MIN_SIZE = 20                # 结束头最小参考尺寸 (实际可能更大)
    
    # 已知文件签名特征 (类型: (签名, 最大读取/检查大小 (字节)))
    # 对于ZIP等容器格式，这里的max_carve_size是尝试读取以找到结束标记的范围
    FILE_SIGNATURES = {
        'zip': (b'\x50\x4B\x03\x04', 1024 * 1024 * 10),  # ZIP文件 (如docx, xlsx, pptx等也是ZIP格式)
        'pdf': (b'\x25\x50\x44\x46', 1024 * 1024 * 5),    # PDF文件
        'jpg': (b'\xFF\xD8\xFF', 1024 * 1024 * 5),    # JPG文件
        'png': (b'\x89\x50\x4E\x47', 1024 * 1024 * 5),  # PNG文件
        'gif': (b'\x47\x49\x46\x38\x37\x61', 1024 * 1024 * 2),  # GIF87a
        'gif89': (b'\x47\x49\x46\x38\x39\x61', 1024 * 1024 * 2),  # GIF89a
        'rar': (b'\x52\x61\x72\x21\x1A\x07\x00', 1024 * 1024 * 5),  # RAR 1.5-4.x
        'rar5': (b'\x52\x61\x72\x21\x1A\x07\x01\x00', 1024 * 1024 * 5),  # RAR 5.0+
        '7z': (b'\x37\x7A\xBC\xAF\x27\x1C', 1024 * 1024 * 5),  # 7z 内部嵌套
        'gz': (b'\x1F\x8B\x08', 1024 * 1024 * 2),  # GZ文件
        'bz2': (b'\x42\x5A\x68', 1024 * 1024 * 2),  # BZ2文件
        'tar': (b'ustar\x0000', 512 + 1024 * 512),
        'iso': (b'\x43\x44\x30\x30\x31', 32768 + 1024 * 1024 * 10),
        # 增加较为齐全的图像和视频格式
        'webp': (b'RIFF', 1024 * 1024 * 5),       # WebP
        'tiff': (b'\x4D\x4D\x00\x2A', 1024 * 1024 * 5),  # TIFF (大端序)
        'tiff_le': (b'\x49\x49\x2A\x00', 1024 * 1024 * 5), # TIFF (小端序)
        'bmp': (b'\x42\x4D', 1024 * 1024 * 2),         # BMP
        'heif': (b'ftypheic', 1024 * 1024 * 5),        # HEIF
        'heic': (b'ftypheix', 1024 * 1024 * 5),        # HEIC
        'avif': (b'ftypavif', 1024 * 1024 * 5),        # AVIF
        'jxl': (b'\x0F\x02\x1A\x01', 1024 * 1024 * 5),       # JPEG XL
        'mp4': (b'\x00\x00\x00\x18ftypmp4', 1024 * 1024 * 10),  # MP4
        'mkv': (b'\x1A\x45\xDF\xA3', 1024 * 1024 * 10),  # Matroska (MKV, MKA, MKS)
        'webm': (b'\x1A\x45\xDF\xA3', 1024 * 1024 * 10), # WebM
        'mov': (b'\x00\x00\x00\x14moov', 1024 * 1024 * 10),  # QuickTime MOV
        'flv': (b'\x46\x4C\x56\x01', 1024 * 1024 * 5),    # Flash Video FLV
        'wmv': (b'\x30\x26\xB2\x75\x8E\x66\xCF\x11', 1024 * 1024 * 5),  # Windows Media Video
        'avi': (b'RIFF', 1024 * 1024 * 10),  # AVI
        'mpeg': (b'\x00\x00\x01\xB3', 1024 * 1024 * 10), #MPEG
        'mpg': (b'\x00\x00\x01\xB3', 1024 * 1024 * 10),  # MPEG
        # 'ts': (b'\x47', 1024 * 1024 * 10), # Transport Stream
        '3gp': (b'\x00\x00\x00\x14ftyp3gp', 1024 * 1024 * 10), # 3GP
        '3g2': (b'\x00\x00\x00\x14ftyp3g2', 1024 * 1024 * 10), # 3G2
        'm4v': (b'\x00\x00\x00\x14ftypM4V', 1024 * 1024 * 10), #M4V
    }
    
    # 文件结束标记 (部分，用于数据雕刻时精确文件大小)
    EOF_MARKERS = {
        'png': b'\x49\x45\x4E\x44\xAE\x42\x60\x82',
        'jpg': b'\xFF\xD9',
        'gif': b'\x00\x3B',
        'zip': b'\x50\x4B\x05\x06',
        'webp': b'RIFF',  # WebP 格式的结束标记比较复杂，这里简化了。实际应用中可能需要更精确的判断。
        'tiff': b'',  # TIFF 没有标准的结束标记，通常依赖于文件内部的标记和结构。
        'tiff_le': b'', # TIFF 没有标准的结束标记，通常依赖于文件内部的标记和结构。
        'bmp': b'',  # BMP 没有标准的结束标记，文件大小通常在文件头中指定。
        'heif': b'', # HEIF 没有标准的结束标记，依赖于文件结构。
        'heic': b'', # HEIC 没有标准的结束标记，依赖于文件结构。
        'avif': b'', # AVIF 没有标准的结束标记，依赖于文件结构。
        'jxl': b'\x0F\x02\x1A\x01', # JPEG XL 结束标记
        'mp4': b'',  # MP4 格式比较复杂，没有单一的结束标记。依赖于内部结构和box。
        'mkv': b'',  # Matroska (MKV, WebM) 格式使用EBML，没有简单的结束标记。
        'webm': b'',  # Matroska (MKV, WebM) 格式使用EBML，没有简单的结束标记。
        'mov': b'',  # MOV 格式依赖于内部的atom结构。
        'flv': b'',  # FLV 没有标准的结束标记。
        'wmv': b'',  # WMV 没有标准的结束标记。
        'avi': b'RIFF', # AVI 格式使用RIFF结构，结束标记是RIFF的结束
        'mpeg': b'', #  MPEG 没有标准的结束标记。
        'mpg': b'',  #   MPEG 没有标准的结束标记。
        # 'ts': b'',  #  TS 没有标准的结束标记。
        '3gp': b'',  # 3GP 格式基于ISO基本媒体文件格式，没有简单的结束标记。
        '3g2': b'',  # 3G2 格式基于ISO基本媒体文件格式，没有简单的结束标记。
        'm4v': b'',  # M4V 格式基于ISO基本媒体文件格式，没有简单的结束标记。
    }


    def __init__(self, file_path: str, recovery_dir: Optional[str] = None, verbose: bool = True):
        """
        初始化恢复工具
        
        参数:
            file_path (str): 待修复7z文件路径
            recovery_dir (Optional[str]): 恢复文件输出目录. 默认为源文件同级目录下的新文件夹.
            verbose (bool): 是否在控制台显示详细日志. 日志文件始终会创建.
        """
        self.file_path = os.path.abspath(file_path)
        if not os.path.exists(self.file_path):
            print(f"[错误] 文件不存在: {self.file_path}")
            raise FileNotFoundError(f"指定的7z文件未找到: {self.file_path}")
            
        self.file_name = os.path.basename(self.file_path)
        self.verbose = verbose
        self.file_size = os.path.getsize(self.file_path)
        
        # 初始化工作目录
        self.work_dir = recovery_dir or self._create_work_dir()
        self.extract_dir = os.path.join(self.work_dir, "recovered_files") # 提取的文件存放处
        self.temp_dir = os.path.join(self.work_dir, "temp_processing") # 临时处理文件
        os.makedirs(self.extract_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.log_file = os.path.join(self.work_dir, f"{self.file_name}.repair.log")
        self._init_log()
        
        self.headers = {
            'start_header': None,    # 解析后的起始头信息字典
            'end_header_data': None, # 原始的结束头数据 (如果找到)
            'end_header_pos': None   # 找到的结束头在文件中的偏移量
        }
        
        self.repair_status = {
            'backup_created': False,
            'start_header_valid_after_fix': False,
            'end_header_found_or_guessed': False,
            'file_size_consistent_with_header': False,
            'archive_verified_ok': False, # 原始文件是否通过7z t验证
            'data_extracted_from_rebuild': False, # 是否从重组的压缩包中提取了数据
            'data_recovered_via_carving': False, # 是否通过文件雕刻恢复了数据
            'data_recovered': False # 综合标志，表示任何形式的数据恢复
        }
        
    def _create_work_dir(self) -> str:
        """创建带时间戳的工作目录"""
        parent_dir = os.path.dirname(self.file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(parent_dir, f"7z_recovery_{self.file_name}_{timestamp}")

    def _init_log(self):
        """初始化日志文件"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"7z高级修复日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n")
            f.write(f"目标文件: {self.file_path}\n")
            f.write(f"文件大小: {self._format_size(self.file_size)} ({self.file_size} 字节)\n")
            f.write(f"工作目录: {self.work_dir}\n")
            f.write("="*70 + "\n\n")

    def _log(self, message: str, level: str = "INFO"):
        """记录带时间戳的日志条目"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level.upper()}] {message}"
        if self.verbose:
            print(log_entry)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            if self.verbose: # 如果日志写入失败，至少在控制台打印错误
                print(f"[{timestamp}] [CRITICAL] 日志写入失败: {e}")
                print(f"[{timestamp}] [CRITICAL] 原始消息: {message}")


    def _format_size(self, size_bytes: int) -> str:
        """将字节大小格式化为易读的字符串"""
        if size_bytes == 0:
            return "0 B"
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024 and i < len(units) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

    def backup_file(self) -> bool:
        """创建原始文件的安全备份，并验证备份的完整性"""
        self.backup_path = os.path.join(self.work_dir, f"{self.file_name}.bak")
        self._log(f"开始创建备份文件到: {self.backup_path}")
        try:
            shutil.copy2(self.file_path, self.backup_path)
            
            orig_hash = self._calculate_file_hash(self.file_path)
            backup_hash = self._calculate_file_hash(self.backup_path)
            
            if orig_hash == backup_hash and os.path.getsize(self.backup_path) == self.file_size:
                self._log("文件备份成功并通过哈希校验。", "SUCCESS")
                self.repair_status['backup_created'] = True
                return True
            else:
                self._log(f"备份文件哈希校验失败或大小不匹配。原始哈希: {orig_hash}, 备份哈希: {backup_hash}. 原始大小: {self.file_size}, 备份大小: {os.path.getsize(self.backup_path)}", "ERROR")
                return False
        except Exception as e:
            self._log(f"创建备份文件时发生严重错误: {str(e)}", "CRITICAL")
            return False

    def _calculate_file_hash(self, file_path_to_hash: str, algorithm: str = 'sha256') -> str:
        """计算指定文件的哈希值"""
        hash_func = hashlib.new(algorithm)
        try:
            with open(file_path_to_hash, 'rb') as f:
                while chunk := f.read(8192): # 读取8KB的块
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            self._log(f"计算文件 '{file_path_to_hash}' 的哈希值时出错: {e}", "ERROR")
            return ""

    def analyze_start_header(self) -> bool:
        """分析7z文件的起始头结构"""
        self._log("开始分析文件起始头...")
        
        header_data = self._read_bytes_from_original_file(0, self.START_HEADER_SIZE)
        if len(header_data) < self.START_HEADER_SIZE:
            self._log(f"文件大小 ({self.file_size}字节) 小于起始头所需大小 ({self.START_HEADER_SIZE}字节)。文件可能严重损坏或不完整。", "ERROR")
            return False
        
        try:
            signature = header_data[:6]
            version = header_data[6:8]
            # StartHeaderCRC 是后面20字节 (NextHeaderOffset, NextHeaderSize, NextHeaderCRC) 的CRC32
            start_header_crc_val = struct.unpack('<I', header_data[8:12])[0] 
            next_header_offset = struct.unpack('<Q', header_data[12:20])[0]
            next_header_size = struct.unpack('<Q', header_data[20:28])[0]
            next_header_crc_val = struct.unpack('<I', header_data[28:32])[0] # 这是指 EndHeader (或 Metadata block) 的CRC
            
            self.headers['start_header'] = {
                'signature': signature,
                'version': version,
                'start_header_crc': start_header_crc_val,
                'next_header_offset': next_header_offset, # 指向结束头/元数据块的相对偏移
                'next_header_size': next_header_size,     # 结束头/元数据块的大小
                'next_header_crc': next_header_crc_val,   # 结束头/元数据块的CRC
                'is_signature_valid': signature == self.SIGNATURE,
                'is_version_supported': version in self.SUPPORTED_VERSIONS
            }
            
            # 校验起始头的CRC (针对NextHeaderOffset, NextHeaderSize, NextHeaderCRC这20个字节)
            calculated_sh_crc = zlib.crc32(header_data[12:32]) & 0xFFFFFFFF
            self.headers['start_header']['is_sh_crc_valid'] = (calculated_sh_crc == start_header_crc_val)
            
            self.headers['start_header']['is_struct_valid'] = (
                self.headers['start_header']['is_signature_valid'] and
                self.headers['start_header']['is_version_supported'] and
                self.headers['start_header']['is_sh_crc_valid']
            )

            self._log(f"起始头解析: 签名={signature.hex()}, 版本={version.hex()}, SH_CRC={start_header_crc_val:08X} (校验{'通过' if self.headers['start_header']['is_sh_crc_valid'] else '失败'}), NextHeaderOffset={next_header_offset}, NextHeaderSize={next_header_size}, NextHeaderCRC={next_header_crc_val:08X}")

            if self.headers['start_header']['is_struct_valid']:
                self._log("起始头结构基本有效。", "INFO")
                # 尝试根据起始头信息定位结束头
                potential_end_header_pos = self.START_HEADER_SIZE + next_header_offset
                if 0 < potential_end_header_pos < self.file_size and next_header_size > 0:
                    if potential_end_header_pos + next_header_size <= self.file_size :
                        self.headers['end_header_pos'] = potential_end_header_pos
                        self.headers['end_header_data'] = self._read_bytes_from_original_file(potential_end_header_pos, next_header_size)
                        if len(self.headers['end_header_data']) == next_header_size:
                            # 校验结束头的CRC
                            calculated_eh_crc = zlib.crc32(self.headers['end_header_data']) & 0xFFFFFFFF
                            if calculated_eh_crc == next_header_crc_val:
                                self._log(f"根据起始头信息成功定位并验证结束头 @{potential_end_header_pos}, 大小={next_header_size}。CRC校验通过。", "SUCCESS")
                                self.repair_status['end_header_found_or_guessed'] = True
                            else:
                                self._log(f"根据起始头信息定位结束头 @{potential_end_header_pos}, 但CRC校验失败 (预期: {next_header_crc_val:08X}, 计算: {calculated_eh_crc:08X})。", "WARNING")
                        else:
                            self._log(f"根据起始头信息定位结束头 @{potential_end_header_pos}, 但读取大小 ({len(self.headers['end_header_data'])}) 与预期 ({next_header_size}) 不符。", "WARNING")
                            self.headers['end_header_data'] = None
                            self.headers['end_header_pos'] = None
                    else:
                        self._log(f"起始头指示的结束头范围 [{potential_end_header_pos} - {potential_end_header_pos+next_header_size-1}] 超出文件大小 ({self.file_size})。", "WARNING")
                elif next_header_offset == 0 and next_header_size == 0 and next_header_crc_val == 0:
                     self._log("起始头指示这是一个空归档 (所有NextHeader字段为0)。", "INFO")
                     self.repair_status['end_header_found_or_guessed'] = True
                else:
                    self._log(f"起始头指示的结束头偏移 ({next_header_offset}) 或大小 ({next_header_size}) 可能无效或超出文件范围。", "WARNING")

            else:
                self._log("起始头结构无效或损坏。", "WARNING")
            return True
        except struct.error as e:
            self._log(f"解析起始头时发生结构错误: {str(e)}", "ERROR")
            self.headers['start_header'] = {'is_struct_valid': False} # Mark as invalid
            return False
        except Exception as e:
            self._log(f"分析起始头时发生未知错误: {str(e)}", "ERROR")
            self.headers['start_header'] = {'is_struct_valid': False}
            return False

    def _read_bytes_from_original_file(self, offset: int, size: int) -> bytes:
        """安全地从原始文件中读取指定范围的字节"""
        # 从 self.file_path (可能是被修改过的) 读取
        return self._read_bytes_from_specific_file(self.file_path, offset, size)

    def _read_bytes_from_specific_file(self, file_to_read: str, offset: int, size: int) -> bytes:
        """安全地从指定文件中读取字节"""
        if size <= 0: return b''
        try:
            with open(file_to_read, 'rb') as f:
                f.seek(offset)
                return f.read(size)
        except FileNotFoundError:
            self._log(f"读取文件失败: {file_to_read} 未找到。", "ERROR")
            return b''
        except IOError as e:
            self._log(f"从文件 {file_to_read} 偏移量 {offset} 读取 {size} 字节时发生IO错误: {str(e)}", "ERROR")
            return b''
        except Exception as e:
            self._log(f"从文件 {file_to_read} 读取时发生未知错误: {str(e)}", "ERROR")
            return b''

    def _write_bytes_to_file(self, offset: int, data: bytes) -> bool:
        """安全地向当前操作文件 (self.file_path) 的指定偏移量写入字节"""
        try:
            # 操作 self.file_path, 确保备份存在
            if not self.repair_status['backup_created']:
                self._log("未创建备份，禁止写入操作以保护原始文件。", "CRITICAL")
                return False
            with open(self.file_path, 'r+b') as f: # 以读写二进制模式打开
                f.seek(offset)
                f.write(data)
                f.flush() # 确保写入磁盘
            self._log(f"成功向文件 {self.file_path} 偏移量 {offset} 写入 {len(data)} 字节。", "DEBUG")
            return True
        except Exception as e:
            self._log(f"向文件 {self.file_path} 偏移量 {offset} 写入数据时发生错误: {str(e)}", "ERROR")
            return False

    def fix_start_header(self) -> bool:
        """尝试修复起始头中的明显错误，如签名、版本号，或根据找到的结束头更新指针"""
        self._log("尝试修复起始头...")
        if not self.headers.get('start_header'):
            self._log("无起始头分析数据，请先运行 analyze_start_header。", "ERROR")
            return False
        
        sh = self.headers['start_header']
        original_sh_data = bytearray(self._read_bytes_from_original_file(0, self.START_HEADER_SIZE))
        if len(original_sh_data) < self.START_HEADER_SIZE:
             self._log("无法读取完整的起始头进行修复。", "ERROR")
             return False
        
        new_sh_data = bytearray(original_sh_data) # 创建副本进行修改
        made_changes = False

        # 1. 修复签名
        if not sh.get('is_signature_valid'):
            self._log("起始头签名损坏，尝试修复为标准7z签名...", "INFO")
            new_sh_data[:6] = self.SIGNATURE
            made_changes = True
        
        # 2. 修复版本号 (如果损坏，默认使用最新的支持版本)
        if not sh.get('is_version_supported'):
            self._log(f"起始头版本号 {sh.get('version', b'??').hex()} 不支持或损坏，尝试修复为 {self.SUPPORTED_VERSIONS[-1].hex()}...", "INFO")
            new_sh_data[6:8] = self.SUPPORTED_VERSIONS[-1] # 使用最新的已知版本
            made_changes = True

        # 3. 如果通过其他方式找到了结束头 (end_header_pos 已设定)，尝试更新起始头中的指针
        if self.headers.get('end_header_pos') is not None and self.headers.get('end_header_data') is not None: # Check for None explicitly
            eh_pos = self.headers['end_header_pos']
            eh_data = self.headers['end_header_data']
            
            if eh_pos >= self.START_HEADER_SIZE :
                new_next_header_offset = eh_pos - self.START_HEADER_SIZE
                new_next_header_size = len(eh_data)
                new_next_header_crc = zlib.crc32(eh_data) & 0xFFFFFFFF
                current_offset = struct.unpack('<Q', new_sh_data[12:20])[0]
                current_size = struct.unpack('<Q', new_sh_data[20:28])[0]
                current_crc = struct.unpack('<I', new_sh_data[28:32])[0]

                if current_offset != new_next_header_offset or \
                   current_size != new_next_header_size or \
                   current_crc != new_next_header_crc:
                    self._log(f"根据找到/扫描到的结束头信息 (位置: {eh_pos}, 大小: {new_next_header_size}, CRC: {new_next_header_crc:08X}) 更新起始头指针...", "INFO")
                    struct.pack_into('<Q', new_sh_data, 12, new_next_header_offset)
                    struct.pack_into('<Q', new_sh_data, 20, new_next_header_size)
                    struct.pack_into('<I', new_sh_data, 28, new_next_header_crc)
                    made_changes = True
            else:
                self._log(f"找到的结束头位置 ({eh_pos}) 无效，无法用于更新起始头指针。", "WARNING")

        
        if made_changes:
            # 4. 重新计算并更新起始头的CRC (针对NextHeaderOffset, NextHeaderSize, NextHeaderCRC这20字节)
            new_sh_crc_payload = new_sh_data[12:32]
            new_calculated_sh_crc = zlib.crc32(new_sh_crc_payload) & 0xFFFFFFFF
            struct.pack_into('<I', new_sh_data, 8, new_calculated_sh_crc)
            self._log(f"起始头已修改，重新计算SH_CRC为: {new_calculated_sh_crc:08X}", "INFO")
            
            # 5. 将修复后的起始头写回文件
            if self._write_bytes_to_file(0, bytes(new_sh_data)):
                self._log("修复后的起始头已成功写回文件。", "SUCCESS")
                # 更新内存中的分析结果
                self.analyze_start_header()
                self.repair_status['start_header_valid_after_fix'] = self.headers.get('start_header',{}).get('is_struct_valid', False)
                return True
            else:
                self._log("写回修复后的起始头失败。", "ERROR")
                return False
        else:
            self._log("起始头无需修复或未能确定修复方案。", "INFO")
            self.repair_status['start_header_valid_after_fix'] = sh.get('is_struct_valid', False)
            return True

    def adjust_file_size_to_header(self) -> bool:
        """根据（可能已修复的）起始头信息调整文件大小"""
        self._log("尝试根据头信息调整文件大小...")
        if not (self.headers.get('start_header') and self.headers['start_header'].get('is_struct_valid')):
            self._log("起始头无效或未分析，无法调整文件大小。", "WARNING")
            return False

        sh = self.headers['start_header']
        expected_archive_size = self.START_HEADER_SIZE + sh['next_header_offset'] + sh['next_header_size']
        current_file_size = os.path.getsize(self.file_path) # 获取当前实际大小

        if expected_archive_size < self.START_HEADER_SIZE :
            self._log(f"根据头信息计算出的预期文件大小 ({expected_archive_size}) 无效或过小。", "ERROR")
            return False

        self._log(f"头信息指示的预期文件大小: {self._format_size(expected_archive_size)} ({expected_archive_size} 字节)。当前文件大小: {self._format_size(current_file_size)} ({current_file_size} 字节)。")

        if current_file_size == expected_archive_size:
            self._log("文件大小与头信息一致，无需调整。", "INFO")
            self.repair_status['file_size_consistent_with_header'] = True
            return True
        
        if not self.repair_status['backup_created']:
            self._log("未创建备份，禁止修改文件大小。", "CRITICAL")
            return False

        try:
            with open(self.file_path, 'r+b') as f:
                if current_file_size < expected_archive_size:
                    bytes_to_pad = expected_archive_size - current_file_size
                    self._log(f"文件过小，尝试在末尾填充 {self._format_size(bytes_to_pad)} 的零字节...", "INFO")
                    f.seek(0, os.SEEK_END) #到文件尾部
                    f.write(b'\x00' * bytes_to_pad)
                else: # current_file_size > expected_archive_size
                    bytes_to_truncate = current_file_size - expected_archive_size
                    self._log(f"文件过大，尝试截断末尾 {self._format_size(bytes_to_truncate)}...", "INFO")
                    f.truncate(expected_archive_size)
            
            self.file_size = os.path.getsize(self.file_path) # 更新记录的文件大小
            if self.file_size == expected_archive_size:
                self._log(f"文件大小成功调整为 {self._format_size(self.file_size)}。", "SUCCESS")
                self.repair_status['file_size_consistent_with_header'] = True
                return True
            else:
                self._log(f"调整文件大小后，实际大小 ({self._format_size(self.file_size)})与预期 ({self._format_size(expected_archive_size)})仍不符。", "ERROR")
                return False
        except Exception as e:
            self._log(f"调整文件大小 ({self.file_path}) 时发生错误: {str(e)}", "ERROR")
            return False

    def scan_for_end_header(self) -> bool:
        """如果起始头未指向有效的结束头，则尝试扫描文件以定位结束头"""
        self._log("开始扫描文件以查找结束头...")
        if self.repair_status.get('end_header_found_or_guessed') and self.headers.get('end_header_data'):
             self._log("已通过起始头或之前步骤找到结束头，跳过扫描。", "INFO")
             return True

        scan_chunk_size = 1024 * 1024 * 2  # 每次扫描2MB
        potential_signatures = [ b'\x17', b'\x01' ]
        
        # 扫描文件末尾
        start_scan_offset = max(0, self.file_size - scan_chunk_size)
        data_chunk = self._read_bytes_from_original_file(start_scan_offset, scan_chunk_size)

        if not data_chunk:
            self._log("无法读取文件末尾数据进行扫描。", "WARNING")
            return False

        found_at = -1
        best_match_sig = None

        for sig_pattern in potential_signatures:
            pos_in_chunk = data_chunk.rfind(sig_pattern) 
            if pos_in_chunk != -1:
                current_found_at = start_scan_offset + pos_in_chunk
                # 结束头不应在文件最开始的32字节（起始头区域）
                if current_found_at >= self.START_HEADER_SIZE:
                    if current_found_at > found_at: # 优先选择更靠后的匹配
                        found_at = current_found_at
                        best_match_sig = sig_pattern
        
        if found_at != -1:
            self._log(f"在文件偏移量 {found_at} 附近找到潜在的结束头起始模式 {best_match_sig.hex()}。", "INFO")
            
            # 尝试确定结束头的大小并读取
            # 1. 如果起始头有效，使用其 next_header_size 和 next_header_crc
            # 2. 如果起始头无效，我们只能猜测大小或读取到文件末尾
            size_to_read = self.file_size - found_at
            expected_crc_from_sh = None
            sh_reliable_for_eh_info = False

            if self.headers.get('start_header') and self.headers['start_header'].get('is_sh_crc_valid'):
                sh = self.headers['start_header']
                # 只有当sh的next_header_offset大致指向我们找到的found_at时，才信任sh的size和crc
                # 允许一些小的偏差
                if abs((self.START_HEADER_SIZE + sh['next_header_offset']) - found_at) < 64 : # 64字节容差
                    if sh['next_header_size'] > 0 and sh['next_header_size'] <= size_to_read:
                        size_to_read = sh['next_header_size']
                        expected_crc_from_sh = sh['next_header_crc']
                        sh_reliable_for_eh_info = True
                        self._log(f"根据部分匹配的起始头信息，预期结束头大小为 {size_to_read}, CRC为 {expected_crc_from_sh:08X}", "DEBUG")
                    else:
                        self._log(f"起始头指示的大小 ({sh['next_header_size']}) 对于扫描位置无效或过大。", "DEBUG")
                else:
                    self._log(f"起始头指向的结束头位置 ({self.START_HEADER_SIZE + sh['next_header_offset']}) 与扫描位置 ({found_at}) 不符，不使用起始头的结束头大小/CRC。", "DEBUG")


            potential_eh_data = self._read_bytes_from_original_file(found_at, size_to_read)
            
            if len(potential_eh_data) == size_to_read and len(potential_eh_data) > 0 :
                if sh_reliable_for_eh_info and expected_crc_from_sh is not None:
                    calculated_crc = zlib.crc32(potential_eh_data) & 0xFFFFFFFF
                    if calculated_crc == expected_crc_from_sh:
                        self._log(f"扫描到的结束头 @{found_at} (大小 {len(potential_eh_data)}) 通过起始头CRC校验!", "SUCCESS")
                        self.headers['end_header_pos'] = found_at
                        self.headers['end_header_data'] = potential_eh_data
                        self.repair_status['end_header_found_or_guessed'] = True
                        return True
                    else:
                        self._log(f"扫描到的结束头 @{found_at} CRC校验失败 (预期: {expected_crc_from_sh:08X}, 计算: {calculated_crc:08X})。仍将其视为潜在结束头。", "WARNING")
                
                # 如果起始头不可靠或CRC不匹配，仍将此作为最佳猜测
                self._log(f"将偏移量 {found_at} (大小 {len(potential_eh_data)}) 标记为潜在结束头位置。CRC 未精确验证或起始头信息不足。", "INFO")
                self.headers['end_header_pos'] = found_at
                self.headers['end_header_data'] = potential_eh_data 
                self.repair_status['end_header_found_or_guessed'] = True 
                return True
            else:
                self._log(f"从潜在结束头位置 {found_at} 读取数据不足 (预期 {size_to_read}, 得到 {len(potential_eh_data)})。", "WARNING")

        self._log("未能在文件中扫描到明确的结束头模式。", "WARNING")
        return False

    def deep_recovery_rebuild(self) -> bool:
        """
        深度数据恢复（三明治/重组方法）
        """
        self._log("启动深度数据恢复（重组方法）...")
        
        template_archive_path = os.path.join(self.temp_dir, f"template_{self.file_name}.7z")
        rebuilt_archive_path = os.path.join(self.temp_dir, f"rebuilt_{self.file_name}.7z")

        estimated_data_size = self.file_size - self.START_HEADER_SIZE 
        if not self._build_template_archive(template_archive_path, estimated_data_size):
            self._log("创建模板压缩包失败，重组方法中止。", "ERROR")
            return False

        template_sh_data = self._read_bytes_from_specific_file(template_archive_path, 0, self.START_HEADER_SIZE)
        if len(template_sh_data) < self.START_HEADER_SIZE:
            self._log("读取模板起始头失败。", "ERROR")
            return False

        try:
            template_sh_sig = template_sh_data[:6]
            if template_sh_sig != self.SIGNATURE:
                 self._log(f"模板压缩包签名错误: {template_sh_sig.hex()}。中止。", "CRITICAL")
                 return False

            template_next_header_offset_val = struct.unpack('<Q', template_sh_data[12:20])[0]
            template_next_header_size_val = struct.unpack('<Q', template_sh_data[20:28])[0]
            template_next_header_crc_in_sh = struct.unpack('<I', template_sh_data[28:32])[0]

            template_meta_eh_actual_offset = self.START_HEADER_SIZE + template_next_header_offset_val
            template_meta_eh_data = self._read_bytes_from_specific_file(template_archive_path, template_meta_eh_actual_offset, template_next_header_size_val)

            if len(template_meta_eh_data) < template_next_header_size_val:
                self._log(f"读取模板元数据/结束头不完整 (预期 {template_next_header_size_val}, 得到 {len(template_meta_eh_data)})。", "ERROR")
                return False
            
            calculated_template_meta_eh_crc = zlib.crc32(template_meta_eh_data) & 0xFFFFFFFF
            if calculated_template_meta_eh_crc != template_next_header_crc_in_sh:
                self._log(f"模板自身的元数据/结束头CRC不匹配 (起始头记录: {template_next_header_crc_in_sh:08X}, 计算: {calculated_template_meta_eh_crc:08X})。将使用计算出的CRC。", "WARNING")
                template_next_header_crc_in_sh = calculated_template_meta_eh_crc
        except struct.error as e:
            self._log(f"解析模板起始头时发生结构错误: {e}", "ERROR")
            return False
        
        corrupted_data_offset = self.START_HEADER_SIZE
        corrupted_data_length = self.file_size - corrupted_data_offset
        
        # 如果起始头有效且指向了结束头，那么损坏数据体只到结束头之前
        if self.headers.get('start_header', {}).get('is_struct_valid') and \
           self.headers['start_header'].get('next_header_offset', 0) > 0 and \
           (self.START_HEADER_SIZE + self.headers['start_header']['next_header_offset'] <= self.file_size) :
            corrupted_data_length = self.headers['start_header']['next_header_offset']
            self._log(f"根据有效起始头，确定损坏数据体长度为: {corrupted_data_length}", "INFO")
        else:
            self._log(f"起始头无效或未明确指向结束头，将使用从 StartHeader 后到文件末尾的数据作为损坏数据体 (长度: {corrupted_data_length})", "INFO")


        if corrupted_data_length <= 0:
            self._log("计算出的损坏压缩包数据体长度为零或负数，无法提取。", "ERROR")
            return False
            
        corrupted_cd_data = self._read_bytes_from_specific_file(self.backup_path, corrupted_data_offset, corrupted_data_length)
        if not corrupted_cd_data:
            self._log(f"从备份文件读取损坏数据体失败 (偏移: {corrupted_data_offset}, 长度: {corrupted_data_length})。", "ERROR")
            return False
        self._log(f"提取的损坏数据体大小: {self._format_size(len(corrupted_cd_data))}")

        new_rebuilt_sh_data = bytearray(template_sh_data) 
        struct.pack_into('<Q', new_rebuilt_sh_data, 12, len(corrupted_cd_data))
        struct.pack_into('<Q', new_rebuilt_sh_data, 20, len(template_meta_eh_data))
        struct.pack_into('<I', new_rebuilt_sh_data, 28, template_next_header_crc_in_sh)

        new_rebuilt_sh_crc_payload = new_rebuilt_sh_data[12:32]
        new_rebuilt_header_crc = zlib.crc32(new_rebuilt_sh_crc_payload) & 0xFFFFFFFF
        struct.pack_into('<I', new_rebuilt_sh_data, 8, new_rebuilt_header_crc)
        self._log(f"重组后的新起始头: SH_CRC={new_rebuilt_header_crc:08X}, NextHeaderOffset={len(corrupted_cd_data)}, NextHeaderSize={len(template_meta_eh_data)}, NextHeaderCRC={template_next_header_crc_in_sh:08X}", "DEBUG")

        try:
            with open(rebuilt_archive_path, 'wb') as f:
                f.write(new_rebuilt_sh_data)
                f.write(corrupted_cd_data)
                f.write(template_meta_eh_data)
            self._log(f"成功构建重组压缩包: {rebuilt_archive_path} (大小: {self._format_size(os.path.getsize(rebuilt_archive_path))})", "SUCCESS")
        except IOError as e:
            self._log(f"写入重组压缩包 {rebuilt_archive_path} 失败: {e}", "ERROR")
            return False

        if self._extract_data_from_archive(rebuilt_archive_path):
            self.repair_status['data_extracted_from_rebuild'] = True
            self.repair_status['data_recovered'] = True
            return True
        
        self._log("从重组压缩包直接提取失败，尝试对其进行原始数据雕刻...", "INFO")
        if self._carve_data_for_known_signatures(rebuilt_archive_path):
             self.repair_status['data_recovered_via_carving'] = True
             self.repair_status['data_recovered'] = True
             return True
        
        return False

    def _build_template_archive(self, output_path: str, estimated_corrupted_data_size: int) -> bool:
        """构建一个健康的7z模板压缩包，用于提取头部和尾部信息"""
        self._log(f"正在构建模板压缩包: {output_path}")
        
        dummy_content_size = max(1024 * 256, estimated_corrupted_data_size // 10) # 至少256KB，或损坏数据体的10%
        dummy_content_size = min(dummy_content_size, 20 * 1024 * 1024) # 上限20MB
        
        dummy_file_path = os.path.join(self.temp_dir, "dummy_template_content.dat")
        try:
            with open(dummy_file_path, 'wb') as f:
                pattern = b"0123456789ABCDEF" * (1024 // 16)
                bytes_written = 0
                while bytes_written < dummy_content_size:
                    write_chunk = pattern[:dummy_content_size - bytes_written]
                    f.write(write_chunk)
                    bytes_written += len(write_chunk)

            self._log(f"创建临时模板内容文件 {dummy_file_path}，大小: {self._format_size(os.path.getsize(dummy_file_path))}")

            seven_zip_exe = "7z" 
            try:
                sp = subprocess.run([seven_zip_exe, "-h"], capture_output=True, timeout=5, check=False)
                if sp.returncode != 0 and not (b"7-Zip" in sp.stdout or b"7-Zip" in sp.stderr) :
                    self._log(f"7-Zip可执行文件 ({seven_zip_exe}) 似乎无效或未正确响应。输出: {sp.stdout.decode('utf-8', 'replace')[:200]}", "CRITICAL")
                    return False
            except FileNotFoundError:
                self._log(f"错误: 未找到7-Zip可执行文件 ({seven_zip_exe})。请确保它已安装并在系统PATH中。", "CRITICAL")
                return False
            except subprocess.TimeoutExpired:
                 self._log(f"错误: 检查7-Zip可执行文件 ({seven_zip_exe}) 超时。", "CRITICAL")
                 return False


            method_args = ['-mx=1']
            cmd = [seven_zip_exe, 'a', '-t7z'] + method_args + [output_path, dummy_file_path]
            self._log(f"执行7z命令创建模板: {' '.join(cmd)}")
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120) 
            except subprocess.TimeoutExpired:
                self._log(f"创建模板压缩包超时 ({' '.join(cmd)})。", "ERROR")
                return False

            if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > self.START_HEADER_SIZE:
                self._log(f"模板压缩包构建成功: {output_path} (大小: {self._format_size(os.path.getsize(output_path))})", "SUCCESS")
                return True
            else:
                self._log(f"构建模板压缩包失败。7z 返回码: {result.returncode}", "ERROR")
                self._log(f"7z 标准输出:\n{result.stdout}", "DEBUG")
                self._log(f"7z 标准错误:\n{result.stderr}", "DEBUG")
                return False
        except Exception as e:
            self._log(f"构建模板压缩包过程中发生严重异常: {str(e)}", "CRITICAL")
            return False
        finally:
            if os.path.exists(dummy_file_path):
                try:
                    os.remove(dummy_file_path)
                except Exception as e_rm:
                    self._log(f"删除临时模板内容文件 {dummy_file_path} 失败: {e_rm}", "WARNING")

    def _extract_data_from_archive(self, archive_path_to_extract: str) -> bool:
        """尝试从指定的压缩包中提取文件到self.extract_dir"""
        self._log(f"尝试从容器 {archive_path_to_extract} 中提取数据...")
        os.makedirs(self.extract_dir, exist_ok=True)
        
        seven_zip_exe = "7z"
        cmd = [seven_zip_exe, 'x', '-y', '-aoa', f'-o{self.extract_dir}', archive_path_to_extract]
        self._log(f"执行7z提取命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300) 
        except subprocess.TimeoutExpired:
            self._log(f"从 {archive_path_to_extract} 提取数据超时。", "ERROR")
            return False
        except FileNotFoundError:
            self._log(f"错误: 未找到7-Zip可执行文件 ({seven_zip_exe}) 进行提取。", "CRITICAL")
            return False

        files_in_extract_dir_before = set(os.listdir(self.extract_dir))

        if "Everything is Ok" in result.stdout or (result.returncode == 0 and "No files to process" not in result.stdout):
            files_in_extract_dir_after = set(os.listdir(self.extract_dir))
            newly_extracted_files = files_in_extract_dir_after - files_in_extract_dir_before
            
            if newly_extracted_files or "Everything is Ok" in result.stdout :
                self._log(f"成功从 {archive_path_to_extract} 提取数据到 {self.extract_dir} (7z报告OK)。提取了 {len(newly_extracted_files)} 个新项目。", "SUCCESS")
                return True
            else:
                 self._log(f"7z报告OK，但提取目录 {self.extract_dir} 中未发现新文件。可能压缩包内无文件或仅有空目录。", "WARNING")
                 self._log(f"7z 标准输出:\n{result.stdout}", "DEBUG")
                 self._log(f"7z 标准错误:\n{result.stderr}", "DEBUG")
                 return False
                 
        elif result.returncode == 0 and ("No files to process" in result.stdout or "0 files" in result.stdout):
            self._log(f"从 {archive_path_to_extract} 提取完成，但7z报告无文件处理或0文件。可能为空压缩包。", "INFO")
            return False

        else:
            self._log(f"从 {archive_path_to_extract} 提取数据失败。7z 返回码: {result.returncode}", "WARNING")
            self._log(f"7z 标准输出:\n{result.stdout}", "DEBUG")
            self._log(f"7z 标准错误:\n{result.stderr}", "DEBUG")
            return False

    def _carve_data_for_known_signatures(self, file_to_carve: str) -> bool:
        """对指定文件进行原始数据雕刻，查找已知文件类型的签名并提取"""
        self._log(f"对文件 {file_to_carve} 执行原始数据雕刻...")
        
        found_files_count = 0
        try:
            file_size_to_carve = os.path.getsize(file_to_carve)
            if file_size_to_carve < 1024:  # 检查文件大小是否小于 1KB
                self._log(f"文件 {file_to_carve} 小于 1KB ({self._format_size(file_size_to_carve)})，跳过雕刻。", "INFO")
                return False
            if file_size_to_carve == 0:
                self._log("待雕刻文件为空，跳过。", "INFO")
                return False

            with open(file_to_carve, 'rb') as f:
                content = f.read() # 读取整个文件内容进行雕刻
            if not content:
                self._log("无法读取待雕刻文件内容。", "ERROR")
                return False
            
            self._log(f"已读取 {self._format_size(len(content))} 用于雕刻。", "DEBUG")

            potential_hits = []
            for sig_type, (signature_bytes, max_len) in self.FILE_SIGNATURES.items():
                for match in re.finditer(re.escape(signature_bytes), content):
                    potential_hits.append({
                        'type': sig_type,
                        'start': match.start(),
                        'sig_len': len(signature_bytes),
                        'max_len': max_len,
                        'signature': signature_bytes
                    })
            
            potential_hits.sort(key=lambda x: x['start']) # 按起始位置排序

            current_scan_pos = 0
            for hit in potential_hits:
                if hit['start'] < current_scan_pos:
                    continue

                file_start_offset = hit['start']
                file_type = hit['type']
                signature_bytes = hit['signature']
                max_length_for_type = hit['max_len']

                self._log(f"在文件 {os.path.basename(file_to_carve)} 偏移量 {file_start_offset} 处找到 {file_type.upper()} 签名。", "INFO")

                # 确定文件结束位置
                # 1. 默认最大结束位置
                determined_file_end = min(file_start_offset + max_length_for_type, len(content))
                specific_eof_found = False

                # 2. 尝试查找特定类型的EOF标记
                eof_marker = self.EOF_MARKERS.get(file_type)
                if eof_marker:
                    # 搜索范围是从签名后到预期的最大结束位置
                    search_area_for_eof = content[file_start_offset + len(signature_bytes) : determined_file_end]
                    eof_pos_relative = -1
                    if file_type == 'zip' or file_type == 'jpg':
                        eof_pos_relative = search_area_for_eof.rfind(eof_marker)
                    else:
                        eof_pos_relative = search_area_for_eof.find(eof_marker)
                    
                    if eof_pos_relative != -1:
                        absolute_eof_end_pos = file_start_offset + len(signature_bytes) + eof_pos_relative + len(eof_marker)
                        determined_file_end = absolute_eof_end_pos
                        specific_eof_found = True
                        self._log(f"为 {file_type.upper()} @{file_start_offset} 找到EOF标记，精确文件结束于 {determined_file_end}", "DEBUG")

                # 3. 如果没有特定EOF，查找下一个（不重叠的）已知签名作为当前文件的结束边界
                if not specific_eof_found:
                    search_for_next_sig_from = file_start_offset + len(signature_bytes)
                    for next_hit in potential_hits:
                        if next_hit['start'] >= search_for_next_sig_from:
                            if next_hit['start'] < determined_file_end:
                                determined_file_end = next_hit['start']
                                self._log(f"下一个签名 {next_hit['type'].upper()} @{next_hit['start']} 限定了当前 {file_type.upper()} 文件结束于 {determined_file_end}", "DEBUG")
                            break

                data_to_save = content[file_start_offset:determined_file_end]
                
                if not data_to_save:
                    self._log(f"雕刻结果为空 @{file_start_offset} for {file_type.upper()}, 跳过。", "DEBUG")
                    continue

                # 使用检测到的类型作为扩展名
                output_filename = f"carved_{os.path.basename(file_to_carve)}_{file_start_offset:010x}.{file_type}"
                output_full_path = os.path.join(self.extract_dir, output_filename)
                
                try:
                    with open(output_full_path, 'wb') as out_f:
                        out_f.write(data_to_save)
                    self._log(f"已雕刻文件 {output_filename} ({self._format_size(len(data_to_save))}) 到 {self.extract_dir}", "SUCCESS")
                    found_files_count += 1
                except IOError as e_io:
                    self._log(f"保存雕刻的文件 {output_filename} 失败: {e_io}", "ERROR")
                
                current_scan_pos = determined_file_end
        
        except IOError as e:
            self._log(f"雕刻文件 {file_to_carve} 时发生IO错误: {e}", "ERROR")
            return False
        except Exception as e_gen:
            self._log(f"雕刻文件 {file_to_carve} 时发生未知错误: {e_gen}", "CRITICAL")
            return False
        
        if found_files_count > 0:
            self._log(f"原始数据雕刻完成，共找到并尝试保存 {found_files_count} 个潜在文件。", "SUCCESS")
        else:
            self._log(f"原始数据雕刻未在 {file_to_carve} 中找到已知文件签名。", "INFO")
        
        return found_files_count > 0

    def _verify_archive_integrity(self, archive_path_to_test: str) -> bool:
        """使用7z命令行工具测试指定压缩包的完整性"""
        self._log(f"开始使用7z测试压缩包 '{archive_path_to_test}' 的完整性...")
        seven_zip_exe = "7z"
        cmd = [seven_zip_exe, 't', archive_path_to_test] 
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180) 
        except subprocess.TimeoutExpired:
            self._log(f"测试压缩包 {archive_path_to_test} 超时。", "ERROR")
            return False
        except FileNotFoundError:
            self._log(f"错误: 未找到7-Zip可执行文件 ({seven_zip_exe}) 进行测试。", "CRITICAL")
            return False

        self._log(f"7z测试标准输出:\n{result.stdout}", "DEBUG")
        if result.stderr:
            self._log(f"7z测试标准错误:\n{result.stderr}", "DEBUG")

        if "Everything is Ok" in result.stdout or \
           (result.returncode == 0 and "No files to process" in result.stdout): 
            self._log(f"压缩包 '{archive_path_to_test}' 通过7z完整性测试。", "SUCCESS")
            return True
        
        self._log(f"压缩包 '{archive_path_to_test}' 未通过7z完整性测试。返回码: {result.returncode}", "WARNING")
        return False

    def repair(self) -> bool:
        """执行完整的修复流程"""
        self._log("启动7z压缩包修复流程...", "IMPORTANT")
        
        if not self.backup_file():
            self._log("关键步骤：创建文件备份失败。修复流程中止以保护原始数据。", "CRITICAL")
            return False
        
        self._log("阶段1: 分析并尝试就地修复原始压缩包...", "IMPORTANT")
        self.analyze_start_header()

        if not self.headers.get('start_header', {}).get('is_struct_valid', False):
            self._log("起始头初始分析无效，尝试修复起始头...", "INFO")
            if self.fix_start_header(): 
                 self._log("起始头修复尝试完成。", "INFO")
            else:
                 self._log("起始头修复失败。", "WARNING")
        
        if self.headers.get('start_header', {}).get('is_struct_valid', False):
            self.repair_status['start_header_valid_after_fix'] = True
            self._log("起始头有效或已成功修复。", "INFO")

            if not self.repair_status.get('end_header_found_or_guessed'):
                self._log("尝试扫描结束头...", "INFO")
                if self.scan_for_end_header():
                    self._log("结束头扫描完成。如果找到，将尝试再次更新起始头指针。", "INFO")
                    self.fix_start_header() 
            
            self.adjust_file_size_to_header()
            
            if self._verify_archive_integrity(self.file_path):
                self._log("原始压缩包 (可能已修复) 通过7z完整性验证。", "SUCCESS")
                self.repair_status['archive_verified_ok'] = True
                if self._extract_data_from_archive(self.file_path):
                    self._log("已从修复后的原始压缩包中提取文件。", "SUCCESS")
                    self.repair_status['data_recovered'] = True
                else:
                    self._log("原始压缩包验证通过，但提取文件失败或无文件提取。", "WARNING")
                return True 
            else:
                self._log("原始压缩包 (可能已修复) 未通过7z完整性验证。", "WARNING")
        else:
            self._log("起始头严重损坏且无法通过基本方法修复。", "WARNING")

        self._log("阶段2: 原始压缩包无法直接修复或验证，尝试深度数据恢复（重组方法）...", "IMPORTANT")
        if self.deep_recovery_rebuild(): 
            self._log("深度数据恢复（重组方法）完成。部分或全部文件可能已提取到恢复目录。", "SUCCESS")
            return True 
        else:
            self._log("深度数据恢复（重组方法）未能提取任何文件。", "WARNING")

        self._log("阶段3: 所有结构化修复尝试失败，对原始备份文件进行数据雕刻...", "IMPORTANT")
        if self._carve_data_for_known_signatures(self.backup_path): 
            self._log("数据雕刻过程完成。部分文件可能已提取到恢复目录。", "SUCCESS")
            self.repair_status['data_recovered_via_carving'] = True
            self.repair_status['data_recovered'] = True
            return True
        else:
            self._log("数据雕刻未能从原始备份文件中找到任何已知类型的文件。", "WARNING")
        
        self._log("所有修复尝试均已完成，未能通过7z验证原始压缩包，也未能通过深度方法提取确认的数据。", "FAILURE")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="7z压缩包高级修复工具。尝试修复损坏的7z压缩文件，并从中恢复数据。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("file", help="需要修复的7z文件路径。")
    parser.add_argument(
        "-o", "--output", 
        help="恢复文件和日志的输出目录。\n如果未指定，将在原始文件所在目录下创建一个带时间戳的新文件夹。"
    )
    parser.add_argument(
        "-q", "--quiet", 
        action="store_true", 
        help="静默模式。仅在控制台输出最关键的摘要信息，详细过程仍在日志文件中。"
    )
    
    args = parser.parse_args()
    
    try:
        tool = SevenZipAdvancedRecovery(
            args.file,
            recovery_dir=args.output,
            verbose=not args.quiet
        )
        
        overall_success = tool.repair()
        
        print("\n" + "="*30 + " 修复摘要 " + "="*30)
        if overall_success:
            if tool.repair_status.get('archive_verified_ok') and tool.repair_status.get('data_recovered'):
                print(f"成功: 原始压缩包 '{tool.file_path}' 已修复并通过7z完整性验证，文件已尝试提取。")
                print(f"      恢复的文件（如果有）位于: {tool.extract_dir}")
            elif tool.repair_status.get('archive_verified_ok'):
                 print(f"成功: 原始压缩包 '{tool.file_path}' 已修复并通过7z完整性验证。但可能未提取出文件（如空包或提取失败）。")
                 print(f"      请检查恢复目录: {tool.extract_dir}")
            elif tool.repair_status.get('data_extracted_from_rebuild'):
                print(f"成功: 通过重组方法从压缩包中提取了文件。")
                print(f"      恢复的文件位于: {tool.extract_dir}")
            elif tool.repair_status.get('data_recovered_via_carving'):
                print(f"成功: 通过数据雕刻从压缩包中恢复了文件。")
                print(f"      恢复的文件位于: {tool.extract_dir}")
            else: 
                print(f"操作完成: 修复过程已执行，但具体恢复状态未知或未标记。")
                print(f"      请检查恢复目录: {tool.extract_dir} 和详细日志。")
        else:
            print(f"失败: 未能成功修复或从中恢复可验证的数据。")

        print(f"详细修复日志请查看: {tool.log_file}")
        try:
            if os.path.exists(tool.extract_dir) and any(os.scandir(tool.extract_dir)):
                 print(f"在恢复目录中找到文件: {tool.extract_dir}")
            elif overall_success and not tool.repair_status.get('archive_verified_ok'): 
                 print(f"注意: 修复过程报告成功，但恢复目录 {tool.extract_dir} 为空。请仔细检查日志。")
        except Exception as e_scan_dir:
            print(f"检查恢复目录时发生错误: {e_scan_dir}")


        if tool.repair_status.get('backup_created'):
            print(f"原始文件的备份位于: {tool.backup_path}")
        print("="*72)

    except FileNotFoundError as e_fnf:
        print(f"[主程序错误] 文件未找到: {e_fnf}")
    except Exception as e_main:
        print(f"[主程序发生严重错误] {str(e_main)}")
        fallback_log_path = "7z_repair_tool_crash.log"
        with open(fallback_log_path, "a", encoding="utf-8") as flog:
            flog.write(f"[{datetime.now()}] CRITICAL ERROR in main: {e_main}\n")
            import traceback
            traceback.print_exc(file=flog)
        print(f"详细错误信息已记录到: {fallback_log_path}")
