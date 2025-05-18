#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
7z压缩包高级修复工具
基于7z官方技术文档深度开发，支持结构修复和原始数据恢复
版本: 2
更新日期: 2025-04-20
"""

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
    VERSION = b'\x00\x04'                     # 支持版本号
    HEADER_SIZE = 32                          # 起始头大小
    END_HEADER_MIN_SIZE = 20                  # 结束头最小尺寸
    
    # 已知文件签名特征
    FILE_SIGNATURES = {
        'zip': (b'\x50\x4B\x03\x04', 30),      # ZIP文件，最少检查30字节
        'pdf': (b'\x25\x50\x44\x46', 1024),    # PDF文件，检查1KB范围
        'jpg': (b'\xFF\xD8\xFF', 4096),        # JPG文件，检查4KB
        'png': (b'\x89\x50\x4E\x47', 4096),
        '7z': (SIGNATURE, 1024),
        'gz': (b'\x1F\x8B\x08', 512),
        'bz2': (b'\x42\x5A\x68', 512)
    }
    
    def __init__(self, file_path: str, recovery_dir: Optional[str] = None, verbose: bool = True):
        """
        初始化恢复工具
        
        参数:
            file_path: 待修复7z文件路径
            recovery_dir: 恢复文件输出目录
            verbose: 显示详细日志
        """
        self.file_path = os.path.abspath(file_path)
        self.file_name = os.path.basename(file_path)
        self.verbose = verbose

        # 文件元数据 (先获取文件大小，供日志初始化使用)
        self.file_size = os.path.getsize(self.file_path)
        
        # 初始化工作目录
        self.work_dir = recovery_dir or self._create_work_dir()
        self.extract_dir = os.path.join(self.work_dir, "extracted")
        self.temp_dir = os.path.join(self.work_dir, "temp")
        os.makedirs(self.extract_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # 日志系统初始化
        self.log_file = os.path.join(self.work_dir, f"{self.file_name}.repair.log")
        self._init_log()
        
        # 解析结构所需的头信息存储
        self.headers = {
            'start_header': None,    # 起始头解析结果
            'end_header': None,      # 结束头数据
            'end_header_pos': None   # 结束头位置
        }
        
        # 修复状态跟踪
        self.repair_status = {
            'start_header_fixed': False,
            'end_header_found': False,
            'file_size_adjusted': False,
            'data_recovered': False
        }
        
    def _create_work_dir(self) -> str:
        """创建带时间戳的工作目录"""
        parent_dir = os.path.dirname(self.file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(parent_dir, f"7z_recovery_{timestamp}")

    def _init_log(self):
        """初始化日志文件"""
        with open(self.log_file, "w", encoding="utf-8") as f:
            f.write(f"7z高级修复日志 - {datetime.now()}\n")
            f.write("="*60 + "\n")
            f.write(f"目标文件: {self.file_path}\n")
            f.write(f"文件大小: {self._format_size(self.file_size)}\n")
            f.write("="*60 + "\n\n")

    def _log(self, message: str, level: str = "INFO"):
        """记录带时间戳的日志"""
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {message}"
        if self.verbose:
            print(log_entry)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def _format_size(self, size: int) -> str:
        """格式化文件大小"""
        units = ['B', 'KB', 'MB', 'GB']
        for unit in units:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

    def backup_file(self) -> bool:
        """创建安全备份并验证完整性"""
        self.backup_path = os.path.join(self.work_dir, f"{self.file_name}.bak")
        try:
            self._log(f"创建备份文件: {self.backup_path}")
            shutil.copy2(self.file_path, self.backup_path)
            
            # 哈希验证
            orig_hash = self._calc_hash(self.file_path)
            backup_hash = self._calc_hash(self.backup_path)
            
            if orig_hash == backup_hash:
                self._log("备份验证成功", "SUCCESS")
                return True
            self._log(f"备份哈希不匹配: {orig_hash} vs {backup_hash}", "ERROR")
            return False
        except Exception as e:
            self._log(f"备份失败: {str(e)}", "ERROR")
            return False

    def _calc_hash(self, path: str) -> str:
        """计算文件SHA256哈希"""
        sha = hashlib.sha256()
        with open(path, 'rb') as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    def analyze_structure(self) -> bool:
        """分析7z文件结构"""
        self._log("开始分析文件结构...")
        
        # 读取起始头
        header_data = self._read_bytes(0, self.HEADER_SIZE)
        if len(header_data) < self.HEADER_SIZE:
            self._log("文件过小，可能已损坏", "ERROR")
            return False
        
        # 解析起始头
        try:
            signature = header_data[:6]
            version = header_data[6:8]
            header_crc = struct.unpack('<I', header_data[8:12])[0]
            end_offset = struct.unpack('<Q', header_data[12:20])[0]
            end_size = struct.unpack('<Q', header_data[20:28])[0]
            end_crc = struct.unpack('<I', header_data[28:32])[0]
            
            self.headers['start_header'] = {
                'signature': signature,
                'version': version,
                'header_crc': header_crc,
                'end_offset': end_offset,
                'end_size': end_size,
                'end_crc': end_crc,
                'valid': signature == self.SIGNATURE and version in (b'\x00\x03', b'\x00\x04')
            }
            
            # 验证CRC
            calc_crc = zlib.crc32(header_data[12:32]) & 0xFFFFFFFF
            self.headers['start_header']['crc_valid'] = calc_crc == header_crc
            
            # 计算预期结束头位置
            expected_end_pos = self.HEADER_SIZE + end_offset
            if 0 < expected_end_pos < self.file_size:
                self.headers['end_header_pos'] = expected_end_pos
                self.headers['end_header'] = self._read_bytes(expected_end_pos, end_size)
            
            return True
        except Exception as e:
            self._log(f"解析起始头失败: {str(e)}", "ERROR")
            return False

    def _read_bytes(self, offset: int, size: int) -> bytes:
        """安全读取指定字节"""
        try:
            with open(self.file_path, 'rb') as f:
                f.seek(offset)
                return f.read(size)
        except Exception as e:
            self._log(f"读取失败 @{offset}: {str(e)}", "ERROR")
            return b''

    def fix_start_header(self) -> bool:
        """修复起始头"""
        self._log("尝试修复起始头...")
        if not self.headers['start_header']:
            self._log("无起始头信息，请先运行analyze_structure", "ERROR")
            return False
        
        header = self.headers['start_header']
        needs_fix = False
        
        # 构建新起始头
        new_header = bytearray(self._read_bytes(0, self.HEADER_SIZE))
        
        # 修复签名
        if new_header[:6] != self.SIGNATURE:
            self._log("修复签名...")
            new_header[:6] = self.SIGNATURE
            needs_fix = True
        
        # 修复版本号
        if new_header[6:8] not in (b'\x00\x03', b'\x00\x04'):
            self._log("修复版本号...")
            new_header[6:8] = self.VERSION
            needs_fix = True
        
        # 更新结束头位置
        if self.headers['end_header_pos']:
            end_offset = self.headers['end_header_pos'] - self.HEADER_SIZE
            new_header[12:20] = struct.pack('<Q', end_offset)
            needs_fix = True
        
        if needs_fix:
            # 计算新CRC
            new_crc = zlib.crc32(new_header[12:32]) & 0xFFFFFFFF
            new_header[8:12] = struct.pack('<I', new_crc)
            
            # 写入文件
            if self._write_bytes(0, bytes(new_header)):
                self.repair_status['start_header_fixed'] = True
                self._log("起始头修复成功", "SUCCESS")
                return True
            return False
        self._log("起始头无需修复")
        return True

    def _write_bytes(self, offset: int, data: bytes) -> bool:
        """安全写入字节"""
        try:
            with open(self.file_path, 'r+b') as f:
                f.seek(offset)
                f.write(data)
                return True
        except Exception as e:
            self._log(f"写入失败 @{offset}: {str(e)}", "ERROR")
            return False

    def fix_file_size(self) -> bool:
        """调整文件大小匹配头部信息"""
        if not self.headers['start_header']:
            return False
        
        expected_size = self.HEADER_SIZE + self.headers['start_header']['end_offset'] + self.headers['start_header']['end_size']
        actual_size = self.file_size
        
        if actual_size == expected_size:
            self._log("文件大小正确")
            return True
        
        try:
            with open(self.file_path, 'r+b') as f:
                if actual_size < expected_size:
                    self._log(f"填充 {expected_size - actual_size} 字节")
                    f.seek(expected_size - 1)
                    f.write(b'\x00')
                else:
                    self._log(f"截断 {actual_size - expected_size} 字节")
                    f.truncate(expected_size)
            
            self.file_size = expected_size
            self.repair_status['file_size_adjusted'] = True
            return True
        except Exception as e:
            self._log(f"调整文件大小失败: {str(e)}", "ERROR")
            return False

    def recover_end_header(self) -> bool:
        """扫描并恢复结束头"""
        self._log("扫描结束头...")
        
        # 优先扫描文件末尾区域
        scan_size = min(1024 * 1024, self.file_size)  # 扫描最后1MB
        scan_data = self._read_bytes(max(0, self.file_size - scan_size), scan_size)
        
        # 查找结束头签名
        for sig in (b'\x17\x06\x8D', b'\x01\x09\x80', b'\x17\x05\x00'):
            pos = scan_data.rfind(sig)
            if pos != -1:
                end_pos = max(0, self.file_size - scan_size) + pos
                if self._validate_end_header(end_pos):
                    self.headers['end_header_pos'] = end_pos
                    self.repair_status['end_header_found'] = True
                    self._log(f"找到有效结束头 @{end_pos}", "SUCCESS")
                    return True
        self._log("未找到有效结束头", "WARNING")
        return False

    def _validate_end_header(self, pos: int) -> bool:
        """验证结束头有效性"""
        header = self._read_bytes(pos, 24)
        if len(header) < 24:
            return False
        
        # 检查CRC是否匹配
        if self.headers['start_header']:
            stored_crc = self.headers['start_header']['end_crc']
            calc_crc = zlib.crc32(header) & 0xFFFFFFFF
            if stored_crc != calc_crc:
                return False
        return True

    def deep_recovery(self) -> bool:
        """深度数据恢复模式"""
        self._log("启动深度数据恢复...")
        
        try:
            # 创建临时容器
            with tempfile.NamedTemporaryFile(dir=self.temp_dir, delete=False) as tmp:
                container = tmp.name
            
            # 构建大文件容器
            self._build_recovery_container(container)
            
            # 替换数据段
            self._replace_data_segment(container)
            
            # 提取数据
            return self._extract_recovered_data(container)
        except Exception as e:
            self._log(f"深度恢复失败: {str(e)}", "ERROR")
            return False

    def _build_recovery_container(self, output_path: str):
        """构建恢复容器"""
        # 使用7z创建大文件容器
        subprocess.run([
            '7z', 'a', '-t7z', '-mx=9', output_path,
            os.devnull  # 空文件
        ], check=True)

    def _replace_data_segment(self, container: str):
        """替换容器数据段"""
        # 计算需要替换的数据大小
        data_size = self.file_size - self.HEADER_SIZE
        
        # 分割容器
        split_point = os.path.getsize(container) - 1024  # 保留尾部1KB
        with open(container, 'r+b') as f:
            f.truncate(split_point)
        
        # 写入原始数据
        with open(self.file_path, 'rb') as src, open(container, 'ab') as dest:
            src.seek(self.HEADER_SIZE)
            dest.write(src.read(data_size))

    def _extract_recovered_data(self, container: str) -> bool:
        """从容器提取数据"""
        # 使用7z尝试提取
        result = subprocess.run([
            '7z', 'x', '-y', f'-o{self.extract_dir}', container
        ], capture_output=True)
        
        if result.returncode == 0:
            self._log("成功提取原始数据", "SUCCESS")
            self._scan_raw_data()
            return True
        self._log("提取失败，尝试原始扫描...")
        return self._raw_scan()

    def _raw_scan(self) -> bool:
        """原始数据扫描"""
        raw_file = os.path.join(self.extract_dir, "raw_data.bin")
        shutil.copyfile(self.file_path, raw_file)
        
        found_files = 0
        with open(raw_file, 'rb') as f:
            while True:
                chunk = f.read(1024 * 1024)  # 1MB块
                if not chunk:
                    break
                
                # 多签名扫描
                for sig_type, (signature, check_size) in self.FILE_SIGNATURES.items():
                    pos = chunk.find(signature)
                    if pos != -1:
                        self._extract_file(f, f.tell() - len(chunk) + pos, sig_type, check_size)
                        found_files += 1
        
        self._log(f"发现 {found_files} 个潜在文件")
        return found_files > 0

    def _extract_file(self, f: BinaryIO, offset: int, file_type: str, check_size: int):
        """提取检测到的文件"""
        f.seek(offset)
        data = f.read(check_size)
        
        # 简单验证
        if not data.startswith(self.FILE_SIGNATURES[file_type][0]):
            return
        
        # 保存文件
        filename = f"recovered_{offset:08x}.{file_type}"
        with open(os.path.join(self.extract_dir, filename), 'wb') as out:
            out.write(data)
        self._log(f"恢复 {file_type.upper()} 文件 @{offset}")

    def repair(self) -> bool:
        """执行完整修复流程"""
        self._log("启动修复流程...")
        
        if not self.backup_file():
            return False
        
        # 执行修复步骤
        steps = [
            ("结构分析", self.analyze_structure),
            ("修复起始头", self.fix_start_header),
            ("调整文件大小", self.fix_file_size),
            ("恢复结束头", self.recover_end_header),
            ("深度数据恢复", self.deep_recovery)
        ]
        
        success = False
        for name, step in steps:
            self._log(f"执行步骤: {name}")
            if step():
                if name != "深度数据恢复" and self._verify_archive():
                    success = True
                    break
        return success

    def _verify_archive(self) -> bool:
        """验证压缩包完整性"""
        self._log("运行7z验证...")
        result = subprocess.run(['7z', 't', self.file_path], capture_output=True)
        
        if b"Everything is Ok" in result.stdout:
            self._log("验证成功!", "SUCCESS")
            return True
        self._log("验证失败", "WARNING")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="7z高级修复工具")
    parser.add_argument("file", help="需要修复的7z文件路径")
    parser.add_argument("-o", "--output", help="恢复文件输出目录")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    tool = SevenZipAdvancedRecovery(
        args.file,
        recovery_dir=args.output,
        verbose=not args.quiet
    )
    
    if tool.repair():
        print(f"修复成功！恢复文件位于: {tool.extract_dir}")
    else:
        print("修复失败，请查看日志:", tool.log_file)
