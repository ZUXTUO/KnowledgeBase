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

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import threading
import time


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

        self.file_sigs = {
            b'\x50\x4B\x03\x04': 'zip',
            b'\x25\x50\x44\x46': 'pdf',
            b'\xFF\xD8\xFF': 'jpg',
            b'\x89\x50\x4E\x47': 'png',
            b'\x1F\x8B\x08': 'gz',
            b'\x42\x5A\x68': 'bz2',
            b'\x37\x7A\xBC\xAF': '7z',
            b'\xFD\x37\x7A\x58\x5A': 'xz',
            b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1': 'doc_xls_ppt',
            b'\x50\x4B\x03\x04\x14\x00\x06\x00': 'docx_xlsx_pptx',
            b'\x47\x49\x46\x38': 'gif',
            b'\x49\x49\x2A\x00': 'tif',
            b'\x4D\x4D\x00\x2A': 'tif',
            b'\x00\x00\x01\x00': 'ico',
            b'\x41\x56\x49\x20': 'avi',
            b'\x00\x00\x00\x18\x66\x74\x79\x70\x6D\x70\x34\x32': 'mp4',
            b'\x4F\x67\x67\x53': 'ogg',
            b'\x1A\x45\xDF\xA3': 'webm',
            b'\x49\x44\x33': 'mp3',
            b'\x52\x49\x46\x46': 'wav',
            b'\x7B\x5C\x72\x74\x66': 'rtf',
            b'\x3C\x3F\x78\x6D\x6C': 'xml',
            b'\x3C\x21\x44\x4F\x43\x54\x59\x50\x45': 'html',
            b'\x3C\x68\x74\x6D\x6C': 'html',
            b'\x3C\x62\x6F\x64\x79': 'html',
            b'\x40\x63\x6C\x61\x73\x73': 'css',
            b'\x66\x75\x6E\x63\x74\x69\x6F\x6E': 'js',
            b'\x69\x6D\x70\x6F\x72\x74': 'py',
            b'\x52\x61\x72\x21\x1A\x07\x00': 'rar',
            b'\x52\x61\x72\x21\x1A\x07\x01\x00': 'rar5',
            b'\x52\x61\x72\x21\x1A\x07\x00\xCF\x90\x73\x00\x00\x00': 'rar_old',
            b'\x00\x00\x00\x0C\x6A\x50\x20\x20\x0D\x0A\x87\x0A': 'jp2',
        }
        self.temp_files: List[Path] = []
        
        self._setup_tools()
        
        sys.stdout.write(f"开始修复: {self.file_path.name} ({self._format_size(self.file_size)})\n")
        
    def _get_resource_path(self, relative_path: str) -> str:
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        resource_path = os.path.join(base_path, relative_path)
        return resource_path
    
    def _setup_tools(self):
        self.tool_7z = self._get_resource_path("7z.exe")
        self.tool_haozipc = self._get_resource_path("HaoZipC.exe")
        self.tool_funzip = self._get_resource_path("funzip.exe")
        self.tool_unzip = self._get_resource_path("unzip.exe")
        self.tool_zipinfo = self._get_resource_path("zipinfo.exe")
        
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
                sys.stdout.write(f"找到工具: {name} -> {path}\n")
            else:
                sys.stdout.write(f"工具不存在: {name} -> {path}\n")
        
        if not (self.tool_7z in self.available_tools.values() or 
                self.tool_haozipc in self.available_tools.values()):
            sys.stdout.write("警告: 没有找到可用的解压工具(7z.exe或HaoZipC.exe)\n", tag="warning")
        
    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"

    def _backup(self) -> bool:
        try:
            shutil.copy2(self.file_path, self.backup_path)
            sys.stdout.write(f"备份完成: {self.backup_path.name}\n")
            return True
        except Exception as e:
            sys.stdout.write(f"备份失败: {e}\n", tag="error")
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
        sys.stdout.write("修复文件头...\n")
        header = self._parse_header()
        if not header:
            sys.stdout.write("尝试重建文件头...\n")
            pos = self._find_end_header()
            if pos is not None:
                sys.stdout.write(f"根据结束头重建头部 (结束头偏移: {pos})\n")
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
                    sys.stdout.write("文件头重建完成\n")
                    return True
            new_header = bytearray(self.HEADER_SIZE)
            new_header[:6] = self.SIG_7Z
            new_header[6:8] = self.VERSION
            if self._write_at(0, bytes(new_header)):
                sys.stdout.write("文件头重建完成\n")
                return True
            return False
        if header['valid']:
            sys.stdout.write("文件头正常\n")
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
                sys.stdout.write("文件头修复完成\n")
                self._detect_compression()
                return True
        return False

    def _find_end_header(self) -> Optional[int]:
        sys.stdout.write("搜索结束头...\n")
        scan_size = min(1024*1024, self.file_size)
        data = self._read_at(max(0, self.file_size - scan_size), scan_size)
        for sig in [b'\x17\x06', b'\x01\x09', b'\x17\x05']:
            pos = data.rfind(sig)
            if pos != -1:
                end_pos = max(0, self.file_size - scan_size) + pos
                sys.stdout.write(f"找到结束头候选位置: {end_pos}\n")
                return end_pos
        return None

    def _fix_size(self) -> bool:
        header = self._parse_header()
        if not header or not header.get('end_offset'):
            return False
        expected = self.HEADER_SIZE + header['end_offset'] + header['end_size']
        if self.file_size == expected:
            return True
        sys.stdout.write(f"调整文件大小: {self.file_size} -> {expected}\n")
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
        sys.stdout.write("检测压缩方法...\n")
        data = self._read_at(self.HEADER_SIZE, 2)
        if not data:
            sys.stdout.write("无法读取压缩数据\n")
            return
        first_byte = data[0]
        if first_byte == 0:
            sys.stdout.write("压缩方法: LZMA (第一个字节为0)\n")
        else:
            sys.stdout.write("压缩方法: 非LZMA (可能是LZMA2或加密)\n")

    def _test_archive(self) -> bool:
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 't', str(self.file_path)],
                                        capture_output=True, text=True, timeout=30)
                return b"Everything is Ok" in result.stdout.encode() or result.returncode == 0
            except:
                pass
        
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
        
        if "7z.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_7z, 'x', '-y', f'-o{extract_dir}', str(self.file_path)],
                                        capture_output=True, timeout=60)
                if result.returncode == 0:
                    files = list(extract_dir.rglob('*'))
                    sys.stdout.write(f"成功提取 {len([f for f in files if f.is_file()])} 个文件\n")
                    return True
            except:
                pass
        
        if "HaoZipC.exe" in self.available_tools:
            try:
                result = subprocess.run([self.tool_haozipc, 'x', str(self.file_path), f'-o{extract_dir}'],
                                        capture_output=True, timeout=60)
                if result.returncode == 0:
                    files = list(extract_dir.rglob('*'))
                    sys.stdout.write(f"成功提取 {len([f for f in files if f.is_file()])} 个文件\n")
                    return True
            except:
                pass
        
        return False

    def _create_recovery_container(self) -> Path:
        sys.stdout.write("创建恢复容器...\n")
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
        
        container.write_bytes(self.SIG_7Z + b'\x00' * 1000)
        return container

    def _data_transplant(self) -> bool:
        sys.stdout.write("尝试数据移植恢复...\n")
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
                sys.stdout.write("数据移植成功\n")
                return True
        except Exception as e:
            sys.stdout.write(f"数据移植失败: {e}\n", tag="error")
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
        sys.stdout.write("执行原始数据恢复...\n")
        try:
            raw_file = self.output_dir / "raw_data.bin"
            with open(self.file_path, 'rb') as src, open(raw_file, 'wb') as dst:
                src.seek(self.HEADER_SIZE)
                shutil.copyfileobj(src, dst)
            recovered_count = 0
            
            if "7z.exe" in self.available_tools:
                try:
                    result = subprocess.run([self.tool_7z, 'x', '-y', f'-o{self.output_dir}', str(raw_file)],
                                            capture_output=True, timeout=30)
                    if result.returncode == 0:
                        sys.stdout.write("7z成功解析原始数据\n")
                        recovered_count += 1
                except:
                    pass
            
            recovered_count += self._scan_signatures(raw_file)
            if recovered_count > 0:
                sys.stdout.write(f"原始恢复完成，恢复 {recovered_count} 个文件/片段\n")
                return True
        except Exception as e:
            sys.stdout.write(f"原始恢复失败: {e}\n", tag="error")
        return False

    def _scan_signatures(self, raw_file: Path) -> int:
        sys.stdout.write("扫描文件签名...\n")
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
            sys.stdout.write(f"签名扫描失败: {e}\n", tag="error")
        return recovered

    def _brute_force_repair(self) -> bool:
        sys.stdout.write("暴力修复模式...\n")
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
                    sys.stdout.write(f"暴力修复成功 (偏移: {offset}) - 检测到可列出文件内容\n")
                    shutil.copy2(temp_file, self.file_path)
                    self._cleanup_temp_file(temp_file)
                    return True
                else:
                    sys.stdout.write(f"偏移 {offset} 无效，无法列出文件内容\n")
                    self._cleanup_temp_file(temp_file)
        except Exception as e:
            sys.stdout.write(f"暴力修复过程中发生错误: {e}\n", tag="error")
        return False

    def _cleanup_temp_file(self, file_path: Path) -> None:
        try:
            if file_path.exists():
                file_path.unlink()
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
                sys.stdout.write(f"已清理临时文件: {file_path.name}\n")
        except Exception as e:
            sys.stdout.write(f"清理临时文件失败 {file_path.name}: {e}\n", tag="error")

    def _cleanup_all_temp_files(self) -> None:
        sys.stdout.write("清理所有临时文件...\n")
        for temp_file in list(self.temp_files):
            self._cleanup_temp_file(temp_file)
        try:
            if self.temp_dir.exists() and not list(self.temp_dir.iterdir()):
                self.temp_dir.rmdir()
                sys.stdout.write(f"已清理临时目录: {self.temp_dir.name}\n")
        except Exception as e:
            sys.stdout.write(f"清理临时目录失败 {self.temp_dir.name}: {e}\n", tag="error")

    def _run_command_and_log(self, command: List[str], timeout: int = 30, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        cmd_str = " ".join(command)
        sys.stdout.write(f"执行命令: {cmd_str}\n")
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, cwd=cwd)
            sys.stdout.write(f"命令返回码: {result.returncode}\n")
            if result.stdout:
                sys.stdout.write(f"STDOUT:\n{result.stdout}\n")
            if result.stderr:
                sys.stdout.write(f"STDERR:\n{result.stderr}\n")
            return result
        except FileNotFoundError:
            sys.stdout.write(f"错误: 命令 '{command[0]}' 未找到。\n", tag="error")
            raise
        except subprocess.TimeoutExpired:
            sys.stdout.write(f"错误: 命令 '{cmd_str}' 执行超时 ({timeout} 秒)。\n", tag="error")
            raise
        except Exception as e:
            sys.stdout.write(f"执行命令 '{cmd_str}' 时发生未知错误: {e}\n", tag="error")
            raise

    def _can_list_archive(self, file_path: Path) -> bool:
        sys.stdout.write(f"检测压缩包内容列表: {file_path.name}\n")
        
        if "7z.exe" in self.available_tools:
            try:
                result_7z = self._run_command_and_log([self.tool_7z, 'l', str(file_path)], timeout=15)
                if result_7z.returncode == 0 and ("Files:" in result_7z.stdout or "文件:" in result_7z.stdout):
                    sys.stdout.write(f"[7z] 检测成功 - 可列出内容\n")
                    if self._extract_archive_with_specific_tool(file_path, '7z'):
                        return True
            except Exception as e:
                sys.stdout.write(f"7z列表检测失败: {e}\n", tag="error")
        
        if "HaoZipC.exe" in self.available_tools:
            try:
                result_haozip = self._run_command_and_log([self.tool_haozipc, 'l', str(file_path)], timeout=15)
                if result_haozip.returncode == 0 and ("个文件" in result_haozip.stdout or "files" in result_haozip.stdout):
                    sys.stdout.write(f"[HaoZipC] 检测成功 - 可列出内容\n")
                    return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
                elif result_haozip.returncode == 0 and len(result_haozip.stdout) > 200:
                    sys.stdout.write(f"[HaoZipC] 检测成功 - 有详细输出\n")
                    return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
            except Exception as e:
                sys.stdout.write(f"HaoZipC列表检测失败: {e}\n", tag="error")
        
        sys.stdout.write(f"无法列出 {file_path.name} 的内容\n")
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
            sys.stdout.write(f"不支持的解压工具或工具不可用: {tool}\n", tag="error")
            return False
        
        try:
            sys.stdout.write(f"正在使用 {tool} 解压 {file_path.name}...\n")
            result = self._run_command_and_log(command, timeout=120)
            if result.returncode == 0:
                files = list(extract_dir.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                sys.stdout.write(f"{tool} 解压成功，提取了 {file_count} 个文件\n")
                return True
            else:
                sys.stdout.write(f"{tool} 解压失败。\n", tag="error")
                return False
        except Exception as e:
            sys.stdout.write(f"{tool} 解压过程出错: {e}\n", tag="error")
            return False

    def repair(self) -> bool:
        if not self._backup():
            return False
        if not self.available_tools:
            sys.stdout.write("错误: 没有找到任何可用的解压工具\n", tag="error")
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
                sys.stdout.write(f"\n执行 {name}...\n")
                try:
                    if method():
                        if name == "暴力修复":
                            sys.stdout.write(f"修复成功 - {name}\n")
                            success = True
                            break
                        elif name != "原始恢复" and self._test_archive():
                            sys.stdout.write(f"修复成功 - {name}\n")
                            self._extract_archive()
                            success = True
                            break
                        elif name == "原始恢复":
                            success = True
                            break
                except Exception as e:
                    sys.stdout.write(f"{name} 失败: {e}\n", tag="error")
                    continue
        finally:
            self._cleanup_all_temp_files()
        if not success:
            sys.stdout.write("所有修复方法均失败\n")
        return success


class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str_val, tag=None): # 允许通过 tag 参数指定标签
        if tag is None:
            tag = self.tag # 如果未指定，使用默认标签
        self.widget.insert(tk.END, str_val, (tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass


class SevenZipRepairGUI:
    def __init__(self, master):
        self.master = master
        master.title("7z 压缩包修复工具")
        master.geometry("850x650")
        master.resizable(True, True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#e0e0e0')
        style.configure('TLabelFrame', background='#e0e0e0', foreground='#333333', font=('Helvetica', 10, 'bold'))
        style.configure('TLabel', background='#e0e0e0', foreground='#333333', font=('Helvetica', 10))
        style.configure('TEntry', fieldbackground='#ffffff', foreground='#333333', font=('Consolas', 10))
        style.configure('TButton', font=('Helvetica', 10, 'bold'), background='#607D8B', foreground='white', borderwidth=0, focusthickness=3, focuscolor='none')
        style.map('TButton', background=[('active', '#78909C')])
        style.configure('TProgressbar', background='#4CAF50', troughcolor='#CFD8DC', borderwidth=0)


        master.grid_rowconfigure(0, weight=0)
        master.grid_rowconfigure(1, weight=0)
        master.grid_rowconfigure(2, weight=0)
        master.grid_rowconfigure(3, weight=0)
        master.grid_rowconfigure(4, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=0)

        file_frame = ttk.LabelFrame(master, text="选择文件", padding=(15, 10))
        file_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        file_frame.grid_columnconfigure(0, weight=1)

        self.file_path_label = ttk.Label(file_frame, text="7z 文件路径:")
        self.file_path_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.file_path_entry = ttk.Entry(file_frame)
        self.file_path_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        self.browse_file_button = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        self.browse_file_button.grid(row=1, column=1, sticky="e")

        output_frame = ttk.LabelFrame(master, text="输出目录", padding=(15, 10))
        output_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_dir_label = ttk.Label(output_frame, text="输出目录 (可选):")
        self.output_dir_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.output_dir_entry = ttk.Entry(output_frame)
        self.output_dir_entry.grid(row=1, column=0, padx=(0, 10), sticky="ew")
        self.browse_output_button = ttk.Button(output_frame, text="浏览...", command=self.browse_output_dir)
        self.browse_output_button.grid(row=1, column=1, sticky="e")

        button_frame = ttk.Frame(master, padding=(10, 5))
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        self.repair_button = ttk.Button(button_frame, text="开始修复", command=self.start_repair,
                                       style='Green.TButton')
        self.repair_button.grid(row=0, column=0, padx=10, pady=5, ipadx=10, ipady=5)

        self.cancel_button = ttk.Button(button_frame, text="取消修复", command=self.cancel_repair,
                                       style='Red.TButton', state=tk.DISABLED)
        self.cancel_button.grid(row=0, column=1, padx=10, pady=5, ipadx=10, ipady=5)
        
        style.configure('Green.TButton', background='#4CAF50', foreground='white')
        style.map('Green.TButton', background=[('active', '#45a049')])
        style.configure('Red.TButton', background='#F44336', foreground='white')
        style.map('Red.TButton', background=[('active', '#D32F2F')])

        progress_frame = ttk.Frame(master, padding=(10, 5))
        progress_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(progress_frame, text="准备就绪", anchor="w", font=('Helvetica', 10, 'italic'))
        self.status_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew")
        self.progress_bar['value'] = 0


        log_frame = ttk.LabelFrame(master, text="修复日志", padding=(15, 10))
        log_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=20,
                                                 bg="#ffffff", fg="#333333", font=("Consolas", 10), relief=tk.FLAT, bd=0)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        self.log_text.tag_config("stdout", foreground="#424242")
        self.log_text.tag_config("error", foreground="#D32F2F", font=("Consolas", 10, "bold"))
        self.log_text.tag_config("info", foreground="#1976D2")
        self.log_text.tag_config("success", foreground="#388E3C", font=("Consolas", 10, "bold"))
        self.log_text.tag_config("warning", foreground="#F57C00")


        sys.stdout = TextRedirector(self.log_text, "stdout")
        sys.stderr = TextRedirector(self.log_text, "error")

        self.cancel_flag = threading.Event()

        sys.stdout.write("欢迎使用 7z 压缩包修复工具！\n", tag="info")
        sys.stdout.write("请选择要修复的 7z 文件和输出目录，然后点击 '开始修复'。\n", tag="info")
        sys.stdout.write("确保 '7z.exe' 和 'HaoZipC.exe' 等工具与此脚本在同一目录或在系统 PATH 中。\n", tag="warning")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择 7z 压缩文件",
            filetypes=[("7z files", "*.7z"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.status_label.config(text="文件已选择，准备就绪。")
            self.progress_bar['value'] = 0

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, dir_path)
            self.status_label.config(text="输出目录已选择。")

    def start_repair(self):
        file_path = self.file_path_entry.get()
        output_dir = self.output_dir_entry.get()

        if not file_path:
            messagebox.showwarning("警告", "请选择要修复的 7z 文件！")
            return
        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件不存在: {file_path}")
            return

        self.log_text.delete(1.0, tk.END)
        sys.stdout.write(f"开始修复文件: {file_path}\n", tag="info")
        if output_dir:
            sys.stdout.write(f"输出目录: {output_dir}\n", tag="info")
        else:
            sys.stdout.write("输出目录: 默认 (与源文件同目录下的 'recovery_YYYYMMDD_HHMMSS' 文件夹)\n", tag="info")

        self.repair_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        self.status_label.config(text="修复进行中...")
        self.cancel_flag.clear()

        repair_thread = threading.Thread(target=self.run_repair, args=(file_path, output_dir))
        repair_thread.start()

    def cancel_repair(self):
        self.cancel_flag.set()
        self.status_label.config(text="正在请求中断修复...")
        self.cancel_button.config(state=tk.DISABLED)
        sys.stdout.write("\n用户请求中断修复。当前操作完成后将停止。\n", tag="warning")
        messagebox.showinfo("中断请求", "已发送中断请求。当前正在执行的修复步骤完成后，修复过程将停止。")

    def run_repair(self, file_path, output_dir):
        repair_methods_names = [
            "基础修复", "完整性测试", "数据移植", "暴力修复", "原始恢复"
        ]
        total_steps = len(repair_methods_names)
        current_step = 0

        try:
            recovery = SevenZipRecovery(file_path, output_dir if output_dir else None)
            
            if not recovery._backup():
                sys.stdout.write("备份失败，修复中止。\n", tag="error")
                return False
            self.update_progress(10, f"备份完成")
            if self.cancel_flag.is_set():
                sys.stdout.write("修复已中断。\n", tag="warning")
                messagebox.showinfo("修复中断", "修复过程已被用户中断。")
                return

            if not recovery.available_tools:
                sys.stdout.write("错误: 没有找到任何可用的解压工具\n", tag="error")
                return False
            self.update_progress(15, f"检查工具")
            if self.cancel_flag.is_set():
                sys.stdout.write("修复已中断。\n", tag="warning")
                messagebox.showinfo("修复中断", "修复过程已被用户中断。")
                return

            repair_methods = [
                ("基础修复", lambda: recovery._fix_header() and recovery._fix_size()),
                ("完整性测试", recovery._test_archive),
                ("数据移植", recovery._data_transplant),
                ("暴力修复", recovery._brute_force_repair),
                ("原始恢复", recovery._raw_recovery)
            ]
            
            success = False
            for i, (name, method) in enumerate(repair_methods):
                if self.cancel_flag.is_set():
                    sys.stdout.write("\n修复已中断。\n", tag="warning")
                    break
                
                self.update_progress(20 + i * (60 / total_steps), f"执行 {name}...")
                sys.stdout.write(f"\n执行 {name}...\n", tag="info")
                try:
                    if method():
                        if name == "暴力修复":
                            sys.stdout.write(f"修复成功 - {name}\n", tag="success")
                            success = True
                            break
                        elif name != "原始恢复" and recovery._test_archive():
                            sys.stdout.write(f"修复成功 - {name}\n", tag="success")
                            recovery._extract_archive()
                            success = True
                            break
                        elif name == "原始恢复":
                            success = True
                            break
                except Exception as e:
                    sys.stdout.write(f"{name} 失败: {e}\n", tag="error")
                    continue
            
            if self.cancel_flag.is_set():
                sys.stdout.write("修复过程被用户中断。\n", tag="warning")
                messagebox.showinfo("修复中断", "修复过程已被用户中断。")
            elif success:
                sys.stdout.write("\n修复成功！请查看输出目录中的恢复文件。\n", tag="success")
                messagebox.showinfo("修复完成", f"修复成功！\n输出目录: {recovery.output_dir}")
            else:
                sys.stdout.write("\n修复失败。所有修复方法均未成功。\n", tag="error")
                messagebox.showinfo("修复完成", f"修复失败。\n请检查日志获取更多信息。")

        except Exception as e:
            sys.stdout.write(f"\n修复过程中发生意外错误: {e}\n", tag="error")
            messagebox.showerror("修复错误", f"修复过程中发生意外错误: {e}")
        finally:
            self.update_progress(100, "修复完成或已中断。")
            recovery._cleanup_all_temp_files()
            self.repair_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)


    def update_progress(self, value: int, status_text: str):
        self.master.after(0, lambda: self.progress_bar.config(value=value))
        self.master.after(0, lambda: self.status_label.config(text=status_text))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SevenZipRepairGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("应用程序启动错误", f"应用程序启动失败: {e}\n请确保您的Python环境已正确安装Tkinter。")
        sys.exit(1)
