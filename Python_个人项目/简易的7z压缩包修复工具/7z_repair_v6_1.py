#!/usr/bin/env python3
import struct
import os
import subprocess
import shutil
import zlib
import hashlib
import tempfile
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, BinaryIO

class SevenZipRecovery:
    def __init__(self, file_path: str, output_dir: Optional[str] = None):
        self.file_path = Path(file_path).resolve()
        self.file_size = self.file_path.stat().st_size
        self.output_dir = Path(output_dir) if output_dir else self.file_path.parent / f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(exist_ok=True)
        self.backup_path = self.output_dir / f"{self.file_path.name}.bak"
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.SIG_7Z = b'\x37\x7A\xBC\xAF\x27\x1C'
        self.VERSION = b'\x00\x04'
        self.HEADER_SIZE = 32

        # 扩展文件签名，尽可能恢复更多文件格式
        self.file_sigs = {
            b'\x50\x4B\x03\x04': 'zip',      # ZIP文件头
            b'\x25\x50\x44\x46': 'pdf',      # PDF文件头
            b'\xFF\xD8\xFF': 'jpg',          # JPEG文件头
            b'\x89\x50\x4E\x47': 'png',      # PNG文件头
            b'\x1F\x8B\x08': 'gz',           # GZIP文件头
            b'\x42\x5A\x68': 'bz2',          # BZIP2文件头
            b'\x37\x7A\xBC\xAF': '7z',       # 7z文件头 (部分)
            b'\xFD\x37\x7A\x58\x5A': 'xz',   # XZ文件头
            b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'doc_xls_ppt', # Microsoft Office (OLE)
            b'\x50\x4B\x03\x04\x14\x00\x06\x00': 'docx_xlsx_pptx', # Office Open XML (docx, xlsx, pptx)
            b'\x47\x49\x46\x38': 'gif',      # GIF文件头
            b'\x49\x49\x2A\x00': 'tif',      # TIFF文件头 (Little-endian)
            b'\x4D\x4D\x00\x2A': 'tif',      # TIFF文件头 (Big-endian)
            b'\x00\x00\x01\x00': 'ico',      # ICO文件头
            # b'\x42\x4D': 'bmp',              # BMP文件头
            b'\x41\x56\x49\x20': 'avi',      # AVI文件头
            b'\x00\x00\x00\x18\x66\x74\x79\x70\x6D\x70\x34\x32': 'mp4', # MP4文件头 (部分)
            b'\x4F\x67\x67\x53': 'ogg',      # OGG文件头
            b'\x1A\x45\xDF\xA3': 'webm',     # WEBM文件头
            b'\x49\x44\x33': 'mp3',          # MP3文件头 (ID3v2)
            b'\x52\x49\x46\x46': 'wav',      # WAV文件头 (部分)
            b'\x7B\x5C\x72\x74\x66': 'rtf',  # RTF文件头
            b'\x3C\x3F\x78\x6D\x6C': 'xml',  # XML文件头 (部分)
            # b'\x7B\x22': 'json',             # JSON文件头 (部分)
            # b'\x43\x41\x46\x45': 'cafe',     # Java Class文件头
            # b'\xCA\xFE\xBA\xBE': 'class',    # Java Class文件头 (另一种)
            # b'\xDE\xC0\xAD\xDE': 'dex',      # Android Dalvik Executable
            # b'\x7F\x45\x4C\x46': 'elf',      # ELF可执行文件
            # b'\x4D\x5A': 'exe_dll',          # Windows PE (exe, dll)
            # b'\x23\x21': 'script',           # Shell Script (shebang)
            # b'\x0A': 'txt',                  # 纯文本文件 (换行符) - 慎用，可能误判
            # b'\x2F\x2A': 'c_cpp_comment',    # C/C++ 注释开始
            b'\x3C\x21\x44\x4F\x43\x54\x59\x50\x45': 'html', # HTML DOCTYPE
            b'\x3C\x68\x74\x6D\x6C': 'html', # HTML 标签
            b'\x3C\x62\x6F\x64\x79': 'html', # HTML 标签
            b'\x40\x63\x6C\x61\x73\x73': 'css', # CSS @class
            b'\x66\x75\x6E\x63\x74\x69\x6F\x6E': 'js', # JavaScript function
            b'\x69\x6D\x70\x6F\x72\x74': 'py', # Python import
            # b'\x64\x65\x66': 'py',           # Python def
            b'\x52\x61\x72\x21\x1A\x07\x00': 'rar', # RAR文件头 (RAR5)
            b'\x52\x61\x72\x21\x1A\x07\x01\x00': 'rar5', # RAR文件头 (RAR5)
            b'\x52\x61\x72\x21\x1A\x07\x00\xCF\x90\x73\x00\x00\x00': 'rar_old', # RAR文件头 (旧版)
            # b'\x00\x01\x00\x00': 'ttf_otf',  # TrueType/OpenType字体 (部分)
            # b'\x4F\x54\x54\x4F': 'otf',      # OpenType字体 (另一种)
            # b'\x77\x4F\x46\x46': 'woff',     # WOFF字体
            # b'\x77\x4F\x46\x32': 'woff2',    # WOFF2字体
            # b'\x45\x58\x49\x46': 'exif',     # EXIF数据 (部分)
            # b'\x4C\x5A\x49\x50': 'lzip',     # LZIP文件头
            # b'\x43\x52\x58\x31': 'crx',      # Chrome Extension
            b'\x53\x51\x4C\x69\x74\x65\x20\x66\x6F\x72\x6D\x61\x74\x20\x33\x00': 'sqlite', # SQLite3数据库
            b'\x4D\x53\x43\x46': 'cab',      # Microsoft Cabinet
            b'\x46\x4C\x56': 'flv',          # Flash Video
            b'\x4D\x54\x68\x64': 'mid',      # MIDI文件
            b'\x00\x00\x01\xB3': 'mpg',      # MPEG文件 (部分)
            b'\x00\x00\x01\xBA': 'mpg',      # MPEG文件 (部分)
            b'\x41\x43\x31\x30': 'dwg',      # AutoCAD Drawing
            # b'\x25\x21\x50\x53': 'ps',       # PostScript
            b'\x25\x21\x50\x53\x2D\x41\x64\x6F\x62\x65': 'eps', # Encapsulated PostScript
            b'\x04\x22\x4D\x18': 'swf',      # Shockwave Flash
            # b'\x42\x43': 'bzip',             # BZIP文件头 (旧版)
            # b'\x78\xDA': 'zlib',             # ZLIB压缩数据 (Deflate)
            # b'\x78\x9C': 'zlib',             # ZLIB压缩数据 (Deflate)
            # b'\x78\x01': 'zlib',             # ZLIB压缩数据 (Deflate)
            b'\x00\x00\x00\x0C\x6A\x50\x20\x20\x0D\x0A\x87\x0A': 'jp2', # JPEG 2000
        }
        self.temp_files: List[Path] = []
        
        # 初始化工具路径
        self._setup_tools()
        
        print(f"开始修复: {self.file_path.name} ({self._format_size(self.file_size)})")
        
    def _get_resource_path(self, relative_path: str) -> str:
        """获取资源文件路径，支持开发环境和PyInstaller打包环境"""
        try:
            # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        resource_path = os.path.join(base_path, relative_path)
        return resource_path
    
    def _setup_tools(self):
        """设置工具路径"""
        # 获取工具的绝对路径
        self.tool_7z = self._get_resource_path("7z.exe")
        self.tool_haozipc = self._get_resource_path("HaoZipC.exe")
        self.tool_funzip = self._get_resource_path("funzip.exe")
        self.tool_unzip = self._get_resource_path("unzip.exe")
        self.tool_zipinfo = self._get_resource_path("zipinfo.exe")
        
        # 验证工具是否存在
        tools = {
            "7z.exe": self.tool_7z,
            "HaoZipC.exe": self.tool_haozipc,
            "funzip.exe": self.tool_funzip,
            "unzip.exe": self.tool_unzip,
            "zipinfo.exe": self.tool_zipinfo
        }
        
        self.available_tools = {}
        for name, path in tools.items():
            if os.path.exists(path):
                self.available_tools[name] = path
                print(f"找到工具: {name} -> {path}")
            else:
                print(f"工具不存在: {name} -> {path}")
        
        # 确保至少有一个解压工具可用
        if not (self.tool_7z in self.available_tools.values() or 
                self.tool_haozipc in self.available_tools.values()):
            print("警告: 没有找到可用的解压工具(7z.exe或HaoZipC.exe)")
        
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def _backup(self) -> bool:
        try:
            shutil.copy2(self.file_path, self.backup_path)
            print(f"备份完成: {self.backup_path.name}")
            return True
        except Exception as e:
            print(f"备份失败: {e}")
            return False

    def _read_at(self, offset: int, size: int) -> bytes:
        try:
            with open(self.file_path, 'rb') as f:
                f.seek(offset)
                return f.read(size)
        except:
            return b''

    def _write_at(self, offset: int, data: bytes) -> bool:
        try:
            with open(self.file_path, 'r+b') as f:
                f.seek(offset)
                f.write(data)
                return True
        except:
            return False

    def _parse_header(self) -> Dict[str, Any]:
        data = self._read_at(0, self.HEADER_SIZE)
        if len(data) < self.HEADER_SIZE:
            return {}
        try:
            sig, ver, crc, end_off, end_size, end_crc = struct.unpack('<6s2sIQQI', data)
            return {
                'signature': sig,
                'version': ver,
                'header_crc': crc,
                'end_offset': end_off,
                'end_size': end_size,
                'end_crc': end_crc,
                'valid': sig == self.SIG_7Z and ver in (b'\x00\x03', b'\x00\x04'),
                'end_pos': self.HEADER_SIZE + end_off if end_off > 0 else 0
            }
        except:
            return {}

    def _fix_header(self) -> bool:
        print("修复文件头...")
        header = self._parse_header()
        if not header:
            print("尝试重建文件头...")
            # 如果找到结束头，使用它来重建头部
            pos = self._find_end_header()
            if pos is not None:
                print(f"根据结束头重建头部 (结束头偏移: {pos})")
                new_offset = pos - self.HEADER_SIZE
                new_size = self.file_size - pos
                end_crc = zlib.crc32(self._read_at(pos, new_size)) & 0xFFFFFFFF
                new_header = bytearray(self.HEADER_SIZE)
                new_header[:6] = self.SIG_7Z
                new_header[6:8] = self.VERSION
                new_header[12:20] = struct.pack('<Q', new_offset)
                new_header[20:28] = struct.pack('<Q', new_size)
                new_header[28:32] = struct.pack('<I', end_crc)
                header_crc = zlib.crc32(new_header[12:32]) & 0xFFFFFFFF
                new_header[8:12] = struct.pack('<I', header_crc)
                if self._write_at(0, bytes(new_header)):
                    print("文件头重建完成")
                    return True
            # 未找到结束头，则仅写入签名和版本
            new_header = bytearray(self.HEADER_SIZE)
            new_header[:6] = self.SIG_7Z
            new_header[6:8] = self.VERSION
            if self._write_at(0, bytes(new_header)):
                print("文件头重建完成")
                return True
            return False
        if header['valid']:
            print("文件头正常")
            # 压缩算法检测
            self._detect_compression()
            return True
        data = bytearray(self._read_at(0, self.HEADER_SIZE))
        fixed = False
        if data[:6] != self.SIG_7Z:
            data[:6] = self.SIG_7Z
            fixed = True
        if data[6:8] not in (b'\x00\x03', b'\x00\x04'):
            data[6:8] = self.VERSION
            fixed = True
        if fixed:
            crc = zlib.crc32(data[12:32]) & 0xFFFFFFFF
            data[8:12] = struct.pack('<I', crc)
            if self._write_at(0, bytes(data)):
                print("文件头修复完成")
                # 压缩算法检测
                self._detect_compression()
                return True
        return False

    def _find_end_header(self) -> Optional[int]:
        print("搜索结束头...")
        scan_size = min(1024*1024, self.file_size)
        data = self._read_at(max(0, self.file_size - scan_size), scan_size)
        for sig in [b'\x17\x06', b'\x01\x09', b'\x17\x05']:
            pos = data.rfind(sig)
            if pos != -1:
                end_pos = max(0, self.file_size - scan_size) + pos
                print(f"找到结束头候选位置: {end_pos}")
                return end_pos
        return None

    def _fix_size(self) -> bool:
        header = self._parse_header()
        if not header or not header.get('end_offset'):
            return False
        expected = self.HEADER_SIZE + header['end_offset'] + header['end_size']
        if self.file_size == expected:
            return True
        print(f"调整文件大小: {self.file_size} -> {expected}")
        try:
            with open(self.file_path, 'r+b') as f:
                if self.file_size < expected:
                    f.seek(expected - 1)
                    f.write(b'\x00')
                else:
                    f.truncate(expected)
            self.file_size = expected
            return True
        except:
            return False

    def _detect_compression(self) -> None:
        """检测压缩方法"""
        print("检测压缩方法...")
        data = self._read_at(self.HEADER_SIZE, 2)
        if not data:
            print("无法读取压缩数据")
            return
        first_byte = data[0]
        if first_byte == 0:
            print("压缩方法: LZMA (第一个字节为0):contentReference[oaicite:23]{index=23}")
        else:
            print("压缩方法: 非LZMA (可能是LZMA2或加密):contentReference[oaicite:24]{index=24}")

    def _test_archive(self) -> bool:
        """测试压缩包完整性"""
        # 优先使用7z
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 't', str(self.file_path)],
                                        capture_output=True, text=True, timeout=30)
                return b"Everything is Ok" in result.stdout.encode() or result.returncode == 0
            except:
                pass
        
        # 备用HaoZipC
        if "HaoZipC.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_haozipc, 't', str(self.file_path)],
                                        capture_output=True, text=True, timeout=30)
                return result.returncode == 0
            except:
                pass
        
        return False

    def _extract_archive(self) -> bool:
        extract_dir = self.output_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        # 优先使用7z
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 'x', '-y', f'-o{extract_dir}', str(self.file_path)],
                                        capture_output=True, timeout=60)
                if result.returncode == 0:
                    files = list(extract_dir.rglob('*'))
                    print(f"成功提取 {len([f for f in files if f.is_file()])} 个文件")
                    return True
            except:
                pass
        
        # 备用HaoZipC
        if "HaoZipC.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_haozipc, 'x', str(self.file_path), f'-o{extract_dir}'],
                                        capture_output=True, timeout=60)
                if result.returncode == 0:
                    files = list(extract_dir.rglob('*'))
                    print(f"成功提取 {len([f for f in files if f.is_file()])} 个文件")
                    return True
            except:
                pass
        
        return False

    def _create_recovery_container(self) -> Path:
        print("创建恢复容器...")
        container = self.temp_dir / "recovery.7z"
        dummy_file = self.temp_dir / "dummy.txt"
        dummy_file.write_text("recovery")
        
        if "7z.exe" in self.available_tools:
            try:
                subprocess.run([self.tool_7z, 'a', '-t7z', '-mx=1', str(container), str(dummy_file)],
                               check=True, capture_output=True)
                return container
            except:
                pass
        
        # 创建基本容器
        container.write_bytes(self.SIG_7Z + b'\x00' * 1000)
        return container

    def _data_transplant(self) -> bool:
        print("尝试数据移植恢复...")
        try:
            container = self._create_recovery_container()
            if not container.exists():
                return False
            with open(container, 'r+b') as cont, open(self.file_path, 'rb') as src:
                cont.seek(self.HEADER_SIZE)
                src.seek(self.HEADER_SIZE)
                chunk_size = 1024 * 1024
                while True:
                    chunk = src.read(chunk_size)
                    if not chunk:
                        break
                    cont.write(chunk)
            if self._test_archive_file(container):
                shutil.copy2(container, self.file_path)
                print("数据移植成功")
                return True
        except Exception as e:
            print(f"数据移植失败: {e}")
        return False

    def _test_archive_file(self, path: Path) -> bool:
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 't', str(path)], capture_output=True, timeout=10)
                return result.returncode == 0
            except:
                pass
        return False

    def _raw_recovery(self) -> bool:
        print("执行原始数据恢复...")
        try:
            raw_file = self.output_dir / "raw_data.bin"
            with open(self.file_path, 'rb') as src, open(raw_file, 'wb') as dst:
                src.seek(self.HEADER_SIZE)
                shutil.copyfileobj(src, dst)
            recovered_count = 0
            
            # 尝试用7z解析
            if "7z.exe" in self.available_tools:
                try:
                    result = subprocess.run([self.tool_7z, 'x', '-y', f'-o{self.output_dir}', str(raw_file)],
                                            capture_output=True, timeout=30)
                    if result.returncode == 0:
                        print("7z成功解析原始数据")
                        recovered_count += 1
                except:
                    pass
            
            recovered_count += self._scan_signatures(raw_file)
            if recovered_count > 0:
                print(f"原始恢复完成，恢复 {recovered_count} 个文件/片段")
                return True
        except Exception as e:
            print(f"原始恢复失败: {e}")
        return False

    def _scan_signatures(self, raw_file: Path) -> int:
        print("扫描文件签名...")
        recovered = 0
        try:
            with open(raw_file, 'rb') as f:
                data = f.read()
                for sig, ext in self.file_sigs.items():
                    pos = 0
                    while True:
                        pos = data.find(sig, pos)
                        if pos == -1:
                            break
                        end_pos = min(pos + 1024*1024, len(data))
                        file_data = data[pos:end_pos]
                        if len(file_data) > len(sig):
                            output_file = self.output_dir / f"recovered_{recovered:03d}_{pos:08x}.{ext}"
                            output_file.write_bytes(file_data)
                            recovered += 1
                        pos += 1
        except Exception as e:
            print(f"签名扫描失败: {e}")
        return recovered

    def _brute_force_repair(self) -> bool:
        print("暴力修复模式...")
        try:
            for offset in range(0, min(1024, self.file_size), 4):
                temp_file = self.temp_dir / f"brute_{offset}.7z"
                self.temp_files.append(temp_file)
                with open(self.file_path, 'rb') as src, open(temp_file, 'wb') as dst:
                    src.seek(offset)
                    dst.write(self.SIG_7Z)
                    dst.write(self.VERSION)
                    dst.write(b'\x00' * 24)
                    src.seek(self.HEADER_SIZE)
                    shutil.copyfileobj(src, dst)
                if self._can_list_archive(temp_file):
                    print(f"暴力修复成功 (偏移: {offset}) - 检测到可列出文件内容")
                    shutil.copy2(temp_file, self.file_path)
                    self._cleanup_temp_file(temp_file)
                    return True
                else:
                    print(f"偏移 {offset} 无效，无法列出文件内容")
                    # 删除无效的压缩包文件
                    self._cleanup_temp_file(temp_file)
        except Exception as e:
            print(f"暴力修复过程中发生错误: {e}")
        return False

    def _cleanup_temp_file(self, file_path: Path) -> None:
        try:
            if file_path.exists():
                file_path.unlink()
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
                print(f"已清理临时文件: {file_path.name}")
        except Exception as e:
            print(f"清理临时文件失败 {file_path.name}: {e}")

    def _cleanup_all_temp_files(self) -> None:
        print("清理所有临时文件...")
        for temp_file in list(self.temp_files):
            self._cleanup_temp_file(temp_file)
        try:
            if self.temp_dir.exists() and not list(self.temp_dir.iterdir()):
                self.temp_dir.rmdir()
                print(f"已清理临时目录: {self.temp_dir.name}")
        except Exception as e:
            print(f"清理临时目录失败 {self.temp_dir.name}: {e}")

    def _run_command_and_log(self, command: List[str], timeout: int = 30, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        cmd_str = " ".join(command)
        print(f"执行命令: {cmd_str}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=cwd)
            print(f"命令返回码: {result.returncode}")
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
            return result
        except FileNotFoundError:
            print(f"错误: 命令 '{command[0]}' 未找到。")
            raise
        except subprocess.TimeoutExpired:
            print(f"错误: 命令 '{cmd_str}' 执行超时 ({timeout} 秒)。")
            raise
        except Exception as e:
            print(f"执行命令 '{cmd_str}' 时发生未知错误: {e}")
            raise

    def _can_list_archive(self, file_path: Path) -> bool:
        print(f"检测压缩包内容列表: {file_path.name}")
        
        # 尝试7z
        if "7z.exe" in self.available_tools:
            try:
                result_7z = self._run_command_and_log([self.tool_7z, 'l', str(file_path)], timeout=15)
                if result_7z.returncode == 0 and ("Files:" in result_7z.stdout or "文件:" in result_7z.stdout):
                    print(f"[7z] 检测成功 - 可列出内容")
                    if self._extract_archive_with_specific_tool(file_path, '7z'):
                        return True
            except Exception as e:
                print(f"7z列表检测失败: {e}")
        
        # 尝试HaoZipC
        if "HaoZipC.exe" in self.available_tools:
            try:
                result_haozip = self._run_command_and_log([self.tool_haozipc, 'l', str(file_path)], timeout=15)
                if result_haozip.returncode == 0 and ("个文件" in result_haozip.stdout or "files" in result_haozip.stdout):
                    print(f"[HaoZipC] 检测成功 - 可列出内容")
                    return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
                elif result_haozip.returncode == 0 and len(result_haozip.stdout) > 200:
                    print(f"[HaoZipC] 检测成功 - 有详细输出")
                    return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
            except Exception as e:
                print(f"HaoZipC列表检测失败: {e}")
        
        print(f"无法列出 {file_path.name} 的内容")
        return False

    def _extract_archive_with_specific_tool(self, file_path: Path, tool: str) -> bool:
        extract_dir = self.output_dir / "OUTPUT"
        extract_dir.mkdir(exist_ok=True)
        command = []
        
        if tool == '7z' and "7z.exe" in self.available_tools:
            command = [self.tool_7z, 'x', '-y', f'-o{extract_dir}', str(file_path)]
        elif tool == 'HaoZipC' and "HaoZipC.exe" in self.available_tools:
            command = [self.tool_haozipc, 'x', str(file_path), f'-o{extract_dir}']
        else:
            print(f"不支持的解压工具或工具不可用: {tool}")
            return False
        
        try:
            print(f"正在使用 {tool} 解压 {file_path.name}...")
            result = self._run_command_and_log(command, timeout=120)
            if result.returncode == 0:
                files = list(extract_dir.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                print(f"{tool} 解压成功，提取了 {file_count} 个文件")
                return True
            else:
                print(f"{tool} 解压失败。")
                return False
        except Exception as e:
            print(f"{tool} 解压过程出错: {e}")
            return False

    def repair(self) -> bool:
        if not self._backup():
            return False
        if not self.available_tools:
            print("错误: 没有找到任何可用的解压工具")
            return False

        repair_methods = [
            ("基础修复", lambda: self._fix_header() and self._fix_size()),
            ("完整性测试", self._test_archive),
            ("数据移植", self._data_transplant),
            ("暴力修复", self._brute_force_repair),
            ("原始恢复", self._raw_recovery)
        ]
        success = False
        try:
            for name, method in repair_methods:
                print(f"\n执行 {name}...")
                try:
                    if method():
                        if name == "暴力修复":
                            print(f"修复成功 - {name}")
                            success = True
                            break
                        elif name != "原始恢复" and self._test_archive():
                            print(f"修复成功 - {name}")
                            self._extract_archive()
                            success = True
                            break
                        elif name == "原始恢复":
                            success = True
                            break
                except Exception as e:
                    print(f"{name} 失败: {e}")
                    continue
        finally:
            self._cleanup_all_temp_files()
        if not success:
            print("所有修复方法均失败")
        return success

def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python script.py <7z文件路径> [输出目录]")
        return
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    recovery = SevenZipRecovery(file_path, output_dir)
    success = recovery.repair()
    print(f"\n修复{'成功' if success else '失败'}")
    print(f"输出目录: {recovery.output_dir}")
    if success:
        print("请查看输出目录中的恢复文件")

if __name__ == "__main__":
    main()