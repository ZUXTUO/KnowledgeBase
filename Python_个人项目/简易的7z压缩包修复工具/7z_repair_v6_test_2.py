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
        self.output_dir = Path(output_dir) if output_dir else self.file_path.parent / f"recovery_{self.file_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(exist_ok=True)
        self.backup_path = self.output_dir / f"{self.file_path.name}.bak"
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.SIG_7Z = b'\x37\x7A\xBC\xAF\x27\x1C'
        self.VERSION = b'\x00\x04'
        self.HEADER_SIZE = 32
        self.header_info: Dict[str, Any] = {} # 用于存储详细解析后的头部信息

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
        
        # 初始化工具路径 (保留v6的多工具逻辑)
        self._setup_tools()
        
        print(f"开始修复: {self.file_path.name} ({self._format_size(self.file_size)})")
        print(f"所有恢复的文件和日志将保存在: {self.output_dir}")
        
    def _get_resource_path(self, relative_path: str) -> str:
        """获取资源文件路径，支持开发环境和PyInstaller打包环境"""
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)
    
    def _setup_tools(self):
        """设置工具路径 (来自v6)"""
        self.tool_7z = self._get_resource_path("7z.exe")
        self.tool_haozipc = self._get_resource_path("HaoZipC.exe")
        
        self.available_tools = {}
        tools = {"7z.exe": self.tool_7z, "HaoZipC.exe": self.tool_haozipc}
        for name, path in tools.items():
            if os.path.exists(path):
                self.available_tools[name] = path
                print(f"找到工具: {name} -> {path}")
            else:
                print(f"工具不存在: {name} -> {path}")
        
        if not self.available_tools:
            print("警告: 没有找到任何可用的解压工具(7z.exe或HaoZipC.exe)，修复能力将受限。")
        
    def _format_size(self, size: int) -> str:
        if size == 0: return "0B"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024: return f"{size:.2f}{unit}"
            size /= 1024
        return f"{size:.2f}PB"

    def _backup(self) -> bool:
        try:
            shutil.copy2(self.file_path, self.backup_path)
            print(f"成功创建备份文件: {self.backup_path.name}")
            return True
        except Exception as e:
            print(f"错误: 创建备份文件失败: {e}")
            return False

    def _read_at(self, offset: int, size: int, file_handle: Optional[BinaryIO] = None) -> bytes:
        target_file = file_handle.name if file_handle else self.file_path
        fh = file_handle or open(self.file_path, 'rb')
        try:
            fh.seek(offset)
            return fh.read(size)
        except Exception as e:
            print(f"警告: 读取文件 {target_file} 偏移 {offset} 处 {size} 字节失败: {e}")
            return b''
        finally:
            if not file_handle: # 如果是临时打开的，就关闭它
                fh.close()

    def _write_at(self, file_path: Path, offset: int, data: bytes) -> bool:
        try:
            with open(file_path, 'r+b') as f:
                f.seek(offset)
                f.write(data)
                return True
        except Exception as e:
            print(f"错误: 写入文件 {file_path.name} 偏移 {offset} 失败: {e}")
            return False

    # --- 保留v6的核心方法 ---
    def _parse_header_v6(self) -> Dict[str, Any]:
        """解析头部 (来自v6的原始方法)"""
        data = self._read_at(0, self.HEADER_SIZE)
        if len(data) < self.HEADER_SIZE:
            return {}
        try:
            sig, ver, crc, end_off, end_size, end_crc = struct.unpack('<6s2sIQQI', data)
            return {
                'signature': sig, 'version': ver, 'header_crc': crc,
                'end_offset': end_off, 'end_size': end_size, 'end_crc': end_crc,
                'valid': sig == self.SIG_7Z and ver in (b'\x00\x03', b'\x00\x04'),
                'end_pos': self.HEADER_SIZE + end_off if end_off > 0 else 0
            }
        except:
            return {}

    def _fix_header_v6(self) -> bool:
        """修复文件头 (来自v6的原始方法)"""
        print("执行v6基础修复: 修复文件头...")
        header = self._parse_header_v6()
        if not header:
            # v6的逻辑是如果头不存在就重建一个空的
            print("  - 尝试重建空文件头...")
            new_header = self.SIG_7Z + self.VERSION + b'\x00' * 24
            if self._write_at(self.file_path, 0, new_header):
                print("  - 空文件头重建完成。")
                return True
            return False
        if header['valid']:
            print("  - v6视角: 文件头有效，无需修复。")
            return True
        # v6的修复逻辑
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
            if self._write_at(self.file_path, 0, bytes(data)):
                print("  - v6文件头修复完成。")
                return True
        return False

    def _fix_size_v6(self) -> bool:
        """调整文件大小 (来自v6的原始方法)"""
        header = self._parse_header_v6()
        if not header or not header.get('end_offset'):
            return False
        expected = self.HEADER_SIZE + header['end_offset'] + header['end_size']
        if self.file_size == expected:
            return True
        print(f"  - v6调整文件大小: {self.file_size} -> {expected}")
        try:
            with open(self.file_path, 'r+b') as f:
                f.truncate(expected)
            self.file_size = expected
            return True
        except:
            return False

    def _data_transplant_v6(self) -> bool:
        """数据移植恢复 (来自v6的原始方法)"""
        print("执行v6数据移植...")
        if "7z.exe" not in self.available_tools: return False
        try:
            container = self.temp_dir / "recovery_v6.7z"
            dummy_file = self.temp_dir / "dummy_v6.txt"
            dummy_file.write_text("recovery_v6")
            
            subprocess.run([self.tool_7z, 'a', '-t7z', '-mx=1', str(container), str(dummy_file)], check=True, capture_output=True)
            if not container.exists(): return False

            with open(container, 'r+b') as cont, open(self.file_path, 'rb') as src:
                cont.seek(self.HEADER_SIZE)
                src.seek(self.HEADER_SIZE)
                shutil.copyfileobj(src, cont)
            
            if self._test_archive_file(container):
                shutil.copy2(container, self.file_path)
                print("  - v6数据移植成功。")
                return True
        except Exception as e:
            print(f"  - v6数据移植失败: {e}")
        return False

    def _raw_recovery_v6(self) -> bool:
        """原始数据恢复 (来自v6的原始方法)"""
        print("执行v6原始恢复 (文件签名扫描)...")
        try:
            raw_file = self.output_dir / "raw_data_v6.bin"
            with open(self.file_path, 'rb') as src, open(raw_file, 'wb') as dst:
                src.seek(self.HEADER_SIZE)
                shutil.copyfileobj(src, dst)
            
            recovered_count = self._scan_signatures(raw_file, "v6_raw_recovered_files")
            if recovered_count > 0:
                print(f"  - v6原始恢复完成，恢复 {recovered_count} 个文件/片段。")
                return True
        except Exception as e:
            print(f"  - v6原始恢复失败: {e}")
        return False

    def _brute_force_repair_v6(self) -> bool:
        """暴力修复 (来自v6的原始方法)"""
        print("执行v6暴力修复...")
        if not self.available_tools: return False
        try:
            for offset in range(0, min(1024, self.file_size), 4):
                temp_file = self.temp_dir / f"brute_v6_{offset}.7z"
                self.temp_files.append(temp_file)
                with open(self.file_path, 'rb') as src, open(temp_file, 'wb') as dst:
                    src.seek(offset)
                    dst.write(self.SIG_7Z + self.VERSION + b'\x00' * 24)
                    src.seek(self.HEADER_SIZE)
                    shutil.copyfileobj(src, dst)
                
                # v6的暴力修复依赖于_can_list_archive
                if self._can_list_archive_v6(temp_file):
                    print(f"  - v6暴力修复成功 (偏移: {offset})")
                    final_path = self.output_dir / f"bruteforce_v6_success_offset_{offset}.7z"
                    shutil.copy2(temp_file, final_path)
                    self._extract_archive(final_path, f"bruteforce_v6_success_offset_{offset}")
                    return True
        except Exception as e:
            print(f"  - v6暴力修复失败: {e}")
        return False

    def _can_list_archive_v6(self, file_path: Path) -> bool:
        """检测内容列表 (来自v6的原始方法)"""
        print(f"  - v6检测列表: {file_path.name}")
        for tool_name, tool_path in self.available_tools.items():
            command = []
            if tool_name == "7z.exe":
                command = [tool_path, 'l', str(file_path)]
            elif tool_name == "HaoZipC.exe":
                command = [tool_path, 'l', str(file_path)]
            
            if command:
                try:
                    result = self._run_command_and_log(command, timeout=15)
                    if result.returncode == 0 and len(result.stdout) > 100:
                        print(f"  - [{tool_name}] 检测到可列出内容。")
                        return True
                except:
                    continue
        return False

    # --- 新增的拓展方法 (来自v7) ---
    def _parse_header_detailed(self) -> bool:
        """详细解析起始头并存储信息 (新增)"""
        data = self._read_at(0, self.HEADER_SIZE)
        if len(data) < self.HEADER_SIZE:
            self.header_info = {'error': '文件太小'}
            return False
        try:
            sig, ver, crc, end_off, end_size, end_crc = struct.unpack('<6s2sIQQI', data)
            header_chunk_for_crc = data[12:12+8] + data[20:20+8] + data[28:28+4]
            calculated_crc = zlib.crc32(header_chunk_for_crc)
            self.header_info = {
                'signature': sig, 'version': ver, 'header_crc': crc,
                'end_header_offset': end_off, 'end_header_size': end_size, 'end_header_crc': end_crc,
                'is_valid_sig': sig == self.SIG_7Z, 'is_valid_ver': ver in (b'\x00\x02', b'\x00\x03', b'\x00\x04'),
                'is_valid_crc': crc == calculated_crc, 'calculated_crc': calculated_crc,
                'is_interrupted': end_off == 0 and end_size == 0 and end_crc == 0,
                'calculated_size': self.HEADER_SIZE + end_off + end_size if end_off > 0 else 0
            }
            return True
        except struct.error:
            self.header_info = {'error': '结构解析失败'}
            return False

    def _find_and_rebuild_from_end_header(self) -> bool:
        """从文件末尾搜索有效的结尾头，并用其信息重建起始头 (新增)"""
        print("执行拓展修复: 从结尾头重建...")
        if "7z.exe" not in self.available_tools: return False
        scan_size = min(1024 * 1024 * 2, self.file_size)
        data = self._read_at(self.file_size - scan_size, scan_size)
        if not data: return False
        
        pos = data.rfind(b'\x17') # 寻找 kEncodedHeader
        if pos != -1:
            end_header_offset = (self.file_size - scan_size) + pos
            end_header_size = self.file_size - end_header_offset
            print(f"  - 在偏移 {end_header_offset} 处找到潜在结尾头。")
            
            temp_repair_file = self.output_dir / f"{self.file_path.stem}_rebuilt_header.7z"
            shutil.copy2(self.file_path, temp_repair_file)

            new_header = bytearray(self.HEADER_SIZE)
            new_header[:6] = self.SIG_7Z
            new_header[6:8] = self.VERSION
            struct.pack_into('<Q', new_header, 12, end_header_offset - self.HEADER_SIZE)
            struct.pack_into('<Q', new_header, 20, end_header_size)
            end_header_data = self._read_at(end_header_offset, end_header_size)
            struct.pack_into('<I', new_header, 28, zlib.crc32(end_header_data))
            header_chunk_for_crc = new_header[12:12+8] + new_header[20:20+8] + new_header[28:28+4]
            struct.pack_into('<I', new_header, 8, zlib.crc32(header_chunk_for_crc))

            if self._write_at(temp_repair_file, 0, bytes(new_header)):
                print("  - 重建的起始头已写入。")
                if self._test_archive_file(temp_repair_file):
                    print("  - 重建的压缩包通过测试！应用修复。")
                    shutil.move(temp_repair_file, self.file_path)
                    return True
        return False

    def _header_transplant_recovery(self) -> bool:
        """高级头部移植恢复法 (新增)"""
        print("执行拓展修复: 高级头部移植...")
        if "7z.exe" not in self.available_tools: return False
        
        healthy_template = self.temp_dir / "healthy_template.7z"
        dummy_data = self.temp_dir / "dummy.dat"
        dummy_size = int(self.file_size * 1.2) + 1024 * 1024
        
        try:
            with open(dummy_data, 'wb') as f: f.seek(dummy_size - 1); f.write(b'\0')
            self._run_command_and_log([self.tool_7z, 'a', '-t7z', '-mx=1', str(healthy_template), str(dummy_data)], timeout=180)
            if not healthy_template.exists(): raise IOError("宿主文件创建失败")

            with open(healthy_template, 'rb') as f:
                healthy_header_data = self._read_at(0, self.HEADER_SIZE, f)
                _, _, _, h_end_off, h_end_size, _ = struct.unpack('<6s2sIQQI', healthy_header_data)
                healthy_end_header_pos = self.HEADER_SIZE + h_end_off
                healthy_end_header = self._read_at(healthy_end_header_pos, h_end_size, f)
            
            corrupted_data_payload = self._read_at(self.HEADER_SIZE, self.file_size - self.HEADER_SIZE)
            
            transplanted_file = self.output_dir / f"{self.file_path.stem}_transplanted.7z"
            with open(transplanted_file, 'wb') as f:
                f.write(healthy_header_data)
                f.write(corrupted_data_payload)
                f.write(healthy_end_header)
            
            new_end_header_offset = self.HEADER_SIZE + len(corrupted_data_payload)
            final_size = new_end_header_offset + len(healthy_end_header)
            
            with open(transplanted_file, 'r+b') as f:
                f.truncate(final_size)
                transplanted_data = bytearray(self._read_at(0, self.HEADER_SIZE, f))
                struct.pack_into('<Q', transplanted_data, 12, new_end_header_offset - self.HEADER_SIZE)
                struct.pack_into('<I', transplanted_data, 28, zlib.crc32(healthy_end_header))
                header_chunk_for_crc = transplanted_data[12:12+8] + transplanted_data[20:20+8] + transplanted_data[28:28+4]
                struct.pack_into('<I', transplanted_data, 8, zlib.crc32(header_chunk_for_crc))
                self._write_at(transplanted_file, 0, bytes(transplanted_data))
            
            print("  - 头部移植完成。")
            if self._extract_archive(transplanted_file, "transplanted_extraction"):
                print("  - 高级头部移植恢复成功！")
                return True
            else:
                print("  - 直接解压移植文件失败，尝试作为原始数据流解析。")
                extract_dir = self.output_dir / "transplanted_extraction"
                streams = [p for p in extract_dir.glob('*') if p.is_file() and p.stat().st_size > 0]
                if streams:
                    raw_stream = max(streams, key=lambda p: p.stat().st_size)
                    return self._parse_raw_stream(raw_stream)
        except Exception as e:
            print(f"  - 高级头部移植失败: {e}")
        return False

    def _parse_raw_stream(self, stream_file: Path) -> bool:
        """使用7z的'#'类型解析器和文件签名扫描来解析原始数据流 (新增)"""
        print(f"执行拓展修复: 深度解析原始数据流 {stream_file.name}...")
        success = False
        if "7z.exe" in self.available_tools:
            parser_dir = self.output_dir / "parsed_from_stream"
            parser_dir.mkdir(exist_ok=True)
            try:
                result = self._run_command_and_log([self.tool_7z, 'x', '-y', f'-o{parser_dir}', '-t#', str(stream_file)], timeout=300)
                if result.returncode == 0 and any(parser_dir.iterdir()):
                    print(f"  - 7z流解析器成功提取了文件。")
                    success = True
            except Exception as e:
                print(f"  - 7z流解析器执行出错: {e}")
        
        recovered_count = self._scan_signatures(stream_file, "raw_stream_files")
        if recovered_count > 0:
            print(f"  - 文件签名扫描从数据流中恢复了 {recovered_count} 个文件。")
            success = True
        return success

    # --- 通用辅助函数 ---
    def _scan_signatures(self, file_to_scan: Path, sub_dir: str) -> int:
        """扫描文件以查找已知的文件签名"""
        scan_output_dir = self.output_dir / sub_dir
        scan_output_dir.mkdir(exist_ok=True)
        recovered_count = 0
        try:
            with open(file_to_scan, 'rb') as f: data = f.read()
            sorted_sigs = sorted(self.file_sigs.items(), key=lambda x: len(x[0]), reverse=True)
            found_positions = []
            for sig, ext in sorted_sigs:
                pos = 0
                while (pos := data.find(sig, pos)) != -1:
                    if not any(p[0] == pos for p in found_positions):
                        found_positions.append((pos, ext))
                    pos += 1
            found_positions.sort(key=lambda x: x[0])
            
            for i, (pos, ext) in enumerate(found_positions):
                start_offset = pos
                end_offset = found_positions[i+1][0] if i + 1 < len(found_positions) else len(data)
                file_data = data[start_offset:end_offset]
                if file_data:
                    output_file = scan_output_dir / f"recovered_{recovered_count:04d}_offset_{start_offset:08x}.{ext}"
                    output_file.write_bytes(file_data)
                    recovered_count += 1
        except Exception as e:
            print(f"  - 签名扫描失败: {e}")
        return recovered_count

    def _cleanup_all_temp_files(self) -> None:
        print("清理所有临时文件...")
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print("已清理临时目录。")
        except Exception as e:
            print(f"清理临时目录失败: {e}")

    def _run_command_and_log(self, command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        cmd_str = " ".join(f'"{c}"' if " " in c else c for c in command)
        print(f"  - 执行命令: {cmd_str}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore', timeout=timeout)
            if result.stdout.strip(): print(f"    - STDOUT: {result.stdout.strip()[:200]}...")
            if result.stderr.strip(): print(f"    - STDERR: {result.stderr.strip()[:200]}...")
            return result
        except Exception as e:
            print(f"    - 执行命令时发生错误: {e}")
            raise

    def _test_archive_file(self, path: Path) -> bool:
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 't', '-ba', str(path)], capture_output=True, text=True, timeout=30)
                return "Everything is Ok" in (result.stdout + result.stderr)
            except: pass
        return False

    def _test_archive(self) -> bool:
        """测试压缩包完整性 (v6多工具版)"""
        print("执行v6完整性测试...")
        for tool_name, tool_path in self.available_tools.items():
            command = [tool_path, 't', str(self.file_path)]
            try:
                result = self._run_command_and_log(command, timeout=60)
                if tool_name == "7z.exe" and "Everything is Ok" in result.stdout: return True
                if tool_name == "HaoZipC.exe" and result.returncode == 0: return True
            except: continue
        return False

    def _extract_archive(self, file_to_extract: Optional[Path] = None, sub_dir: str = "extracted") -> bool:
        """解压压缩包 (v6多工具版)"""
        target_file = file_to_extract or self.file_path
        extract_dir = self.output_dir / sub_dir
        extract_dir.mkdir(exist_ok=True)
        print(f"尝试解压 {target_file.name} 到 {extract_dir}...")
        
        for tool_name, tool_path in self.available_tools.items():
            command = []
            if tool_name == "7z.exe":
                command = [tool_path, 'x', '-y', f'-o{extract_dir}', str(target_file)]
            elif tool_name == "HaoZipC.exe":
                command = [tool_path, 'x', str(target_file), f'-o{extract_dir}']
            
            if command:
                try:
                    result = self._run_command_and_log(command, timeout=300)
                    if result.returncode == 0 and any(extract_dir.iterdir()):
                        print(f"  - 使用 {tool_name} 成功提取了文件。")
                        return True
                except: continue
        return False

    def repair(self) -> bool:
        if not self._backup(): return False
        if not self.available_tools:
            print("错误: 未找到任何可用工具，无法修复。")
            return False
        
        # 在开始时进行一次详细的头部解析，供新方法使用
        self._parse_header_detailed()
        
        # 融合v6和v7的修复方法列表
        repair_methods = [
            ("v6基础修复", lambda: self._fix_header_v6() and self._fix_size_v6()),
            ("v6完整性测试", self._test_archive),
            ("拓展:从结尾头重建", self._find_and_rebuild_from_end_header),
            ("v6数据移植", self._data_transplant_v6),
            ("拓展:高级头部移植", self._header_transplant_recovery),
            ("v6暴力修复", self._brute_force_repair_v6),
            ("v6原始恢复(签名)", self._raw_recovery_v6),
            ("拓展:原始恢复(流解析)", lambda: self._parse_raw_stream(self.file_path))
        ]
        
        success = False
        try:
            for name, method in repair_methods:
                print(f"\n--- 尝试方法: {name} ---")
                try:
                    if method():
                        # 如果是直接产生文件的恢复方法，就认为成功
                        if name in ["拓展:高级头部移植", "v6原始恢复(签名)", "拓展:原始恢复(流解析)"]:
                            print(f"修复成功 - {name} 已产出文件。")
                            success = True
                            break
                        # 其他方法需要通过测试来验证
                        elif self._test_archive():
                            print(f"修复成功 - {name} 后通过了完整性测试。")
                            self._extract_archive()
                            success = True
                            break
                        else:
                            print(f"  - {name} 执行完毕，但压缩包仍未通过测试。")
                except Exception as e:
                    import traceback
                    print(f"方法 {name} 执行时发生意外错误: {e}")
                    traceback.print_exc()
        finally:
            self._cleanup_all_temp_files()

        if success:
             print("\n*** 修复流程成功结束 ***")
        else:
            print("\n--- 所有修复方法均告失败 ---")
        
        # 最终检查输出目录是否有任何恢复的文件
        output_files = [p for p in self.output_dir.rglob('*') if p.is_file() and p.name != self.backup_path.name]
        if output_files:
            print(f"虽然压缩包本身可能无法完全复原，但在输出目录中找到了 {len(output_files)} 个恢复的文件/片段。")
            return True
        elif success:
            return True
        else:

            print("非常抱歉，未能恢复任何文件。损坏可能过于严重。")
            return False

def main():
    if len(sys.argv) < 2:
        print("一个强大的7z压缩包修复工具 (v6+v7 融合增强版)")
        print("用法: python 7z_repair_final.py <损坏的7z文件路径> [可选的输出目录]")
        print("示例: python 7z_repair_final.py C:\\downloads\\archive.7z C:\\recovery_output")
        return
        
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 -> {file_path}")
        return
    if os.path.getsize(file_path) == 0:
        print(f"错误: 文件为空 -> {file_path}")
        return

    recovery = None
    try:
        recovery = SevenZipRecovery(file_path, output_dir)
        recovery.repair()
    except Exception as e:
        print(f"\n！！！在修复过程中发生意外的致命错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if recovery:
            print(f"\n修复流程已结束。所有产出（包括日志和恢复的文件）均位于: {recovery.output_dir}")

if __name__ == "__main__":
    main()
