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
        self.file_sigs = {
            b'\x50\x4B\x03\x04': 'zip', b'\x25\x50\x44\x46': 'pdf', b'\xFF\xD8\xFF': 'jpg',
            b'\x89\x50\x4E\x47': 'png', b'\x1F\x8B\x08': 'gz', b'\x42\x5A\x68': 'bz2',
            b'\x37\x7A\xBC\xAF': '7z', b'\xFD\x37\x7A\x58\x5A': 'xz'
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
            new_header = bytearray(32)
            new_header[:6] = self.SIG_7Z
            new_header[6:8] = self.VERSION
            if self._write_at(0, bytes(new_header)):
                print("文件头重建完成")
                return True
            return False
        if header['valid']:
            print("文件头正常")
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

    def _create_dummy_archive(self, min_body_size: int) -> Optional[Path]:
        """创建一个比目标压缩体更大的哑文件压缩包"""
        print("创建辅助修复容器...耗时较长，请耐心等待···")
        dummy_data_path = self.temp_dir / "dummy_source.bin"
        container_path = self.temp_dir / "dummy_container.7z"
        
        # 1. 创建源文件
        # 为了确保压缩后的数据足够大，我们使用随机数据+重复数据
        # 目标是压缩后的body部分要大于 min_body_size
        # 由于我们不知道压缩率，我们创建一个 2 * min_body_size + 1MB 的文件，且包含难以压缩的数据
        target_size = max(min_body_size * 2, 1024 * 1024) # 至少1MB
        
        try:
            with open(dummy_data_path, 'wb') as f:
                # 写入一些随机头，防止完全相同的模式被优化
                f.write(os.urandom(1024))
                # 填充剩余部分
                remaining = target_size - 1024
                # 使用当前文件作为填充源，因为它本身就是压缩数据，很难再被压缩
                # 如果当前文件太小，就循环写入
                if self.file_size > 0:
                    with open(self.file_path, 'rb') as src:
                        while remaining > 0:
                            chunk = src.read(min(remaining, 1024*1024))
                            if not chunk:
                                src.seek(0)
                                chunk = src.read(min(remaining, 1024*1024))
                            f.write(chunk)
                            remaining -= len(chunk)
                else:
                    # 只有随机数据
                    f.write(os.urandom(min(remaining, 1024*1024)))
            
            # 2. 压缩
            # 按照教程，使用LZMA算法，大字典
            if "7z.exe" in self.available_tools:
                # -m0=lzma -md=64m (64MB字典)
                cmd = [self.tool_7z, 'a', str(container_path), str(dummy_data_path), '-m0=lzma', '-mx=9', '-md=64m']
                subprocess.run(cmd, capture_output=True, check=True)
                return container_path
                
        except Exception as e:
            print(f"创建辅助容器失败: {e}")
            
        return None

    def _data_transplant(self) -> bool:
        """
        实现官方教程中的'移植'修复法 (Split & Stitch)
        构造: [Good Header] + [Bad Compressed Data] + [Good Footer]
        """
        print("尝试高级数据移植恢复 (Official Method)...")
        try:
            # 1. 计算坏文件的压缩数据大小
            header = self._parse_header()
            if not header:
                print("无法解析文件头，尝试使用标准头大小")
            
            # 假设Start Header总是32字节
            bad_body_start = 32
            bad_body_size = self.file_size - bad_body_start
            
            if bad_body_size <= 0:
                print("文件太小，无法进行移植修复")
                return False

            # 2. 创建辅助容器 (Dummy Archive)
            # 它的压缩体必须大于 bad_body_size
            dummy_7z = self._create_dummy_archive(bad_body_size)
            if not dummy_7z or not dummy_7z.exists():
                print("无法创建辅助容器")
                return False
                
            dummy_size = dummy_7z.stat().st_size
            if dummy_size <= self.file_size:
                print(f"警告: 辅助容器 ({dummy_size}) 不比原文件 ({self.file_size}) 大，修复可能失败")
            
            # 3. 拼接
            # New 7z = [Dummy Header (32)] + [Bad Body] + [Dummy Footer (Offset adjusted)]
            # 实际上，我们需要截取 Dummy Archive 的尾部
            # Dummy Archive 结构: [Header 32] + [Dummy Body] + [Footer]
            # 我们需要保留 [Footer]，且它在 Dummy Body 之后。
            # 我们要做的就是把 Bad Body 塞进去，替换掉 Dummy Body 的前 Bad Body Size 字节。
            # 教程的方法是：利用 Header 中的 Offset 指向 Footer。
            # Header 里的 EndOffset 是相对于 Header 结尾的。
            # 原始 Dummy Header 说：Footer 在 X 位置。
            # 如果我们把中间数据换成了较短的 Bad Body，Footer 就必须移动到 Bad Body 之后。
            # 但如果我们不修改 Header，Header 还是指向 X 位置。
            # 所以我们需要填充数据，或者截取 Footer 并拼接到 Bad Body 后面？
            
            # 教程原意：
            # raw.7z.001 (Header)
            # raw.7z.002 (Body part 1, size = size of Bad Body) -> REPLACE with Bad Body
            # raw.7z.003 (Body part 2 + Footer)
            # Result = Header + Bad Body + (Body part 2 + Footer)
            # 这样总大小 = Dummy Archive 大小。
            # 解压时，7z读取 Header，跳转到 Footer，读取 Metadata。
            # Metadata 描述了一个大文件 (dummy_source.bin)。
            # 7z 开始解压数据流。前 N 字节来自 Bad Body (我们替换进去的)。
            # 7z 会以为这是 dummy_source.bin 的开头。
            # 解压出来的 raw.dat 前半部分就是 Bad Body 解压后的数据 (即原始文件的内容)。
            
            repaired_path = self.output_dir / "transplant_repaired.7z"
            
            with open(dummy_7z, 'rb') as f_dummy, open(self.file_path, 'rb') as f_bad, open(repaired_path, 'wb') as f_out:
                # 3.1 写入 Dummy Header
                f_dummy.seek(0)
                header_data = f_dummy.read(32)
                f_out.write(header_data)
                
                # 3.2 写入 Bad Body
                f_bad.seek(32)
                bad_body_data = f_bad.read() # 读取所有剩余数据
                f_out.write(bad_body_data)
                
                # 3.3 写入 Dummy Archive 剩余部分
                # 跳过 Dummy Archive 中对应 Bad Body 大小的部分
                f_dummy.seek(32 + len(bad_body_data))
                # 写入剩余所有数据 (Body part 2 + Footer)
                shutil.copyfileobj(f_dummy, f_out)
                
            print(f"移植完成，生成: {repaired_path.name}")
            
            # 4. 尝试提取 'raw' 数据
            # 这会解压出一个大文件，其中包含我们想要的数据
            extract_dir = self.output_dir / "transplant_out"
            extract_dir.mkdir(exist_ok=True)
            
            print("正在提取恢复流 (这可能会报告数据错误，是正常的)...")
            # 忽略错误提取
            cmd = [self.tool_7z, 'x', '-y', f'-o{extract_dir}', str(repaired_path)]
            self._run_command_and_log(cmd, timeout=300)
            
            # 查找提取出的文件 (dummy_source.bin)
            recovered_files = list(extract_dir.rglob('*'))
            target_file = None
            for f in recovered_files:
                if f.is_file() and f.stat().st_size > 0:
                    target_file = f
                    break
            
            if target_file:
                print(f"提取出数据流文件: {target_file.name} ({self._format_size(target_file.stat().st_size)})")
                # 5. 智能解析这个流
                recovered_raw_path = self.output_dir / "recovered_stream.raw"
                shutil.move(str(target_file), str(recovered_raw_path))
                
                # 再次尝试用7z打开这个raw流 (如果是Solid压缩，里面可能包含文件)
                # 教程提到: Select raw.dat and call "7-Zip > Open Archive > #"
                if self._try_extract_inner_archive(recovered_raw_path):
                    return True
                
                # 如果7z无法识别内部结构，进行文件雕刻
                self._smart_carve(recovered_raw_path)
                return True
                
        except Exception as e:
            print(f"数据移植失败: {e}")
            import traceback
            traceback.print_exc()
            
        return False

    def _try_extract_inner_archive(self, raw_path: Path) -> bool:
        print("尝试将恢复流作为归档打开...")
        out_dir = self.output_dir / "final_extracted"
        out_dir.mkdir(exist_ok=True)
        
        # 尝试使用 # 解析器 (Parser)
        # 7z x raw.dat -t# (不完全支持命令行指定 parser，但可以尝试 -t7z 或 -tzip 或自动检测)
        # 教程说 "Open Archive > #"，命令行对应可能是自动检测
        
        if "7z.exe" in self.available_tools:
            # 尝试直接解压
            cmd = [self.tool_7z, 'x', '-y', f'-o{out_dir}', str(raw_path)]
            res = self._run_command_and_log(cmd)
            if res.returncode == 0 or "Everything is Ok" in res.stdout:
                print("成功从恢复流中解压出文件！")
                return True
        return False

    def _smart_carve(self, raw_file: Path) -> int:
        print("执行智能文件雕刻...")
        recovered_count = 0
        
        # 扩展签名库
        signatures = {
            b'\x50\x4B\x03\x04': 'zip', 
            b'\x25\x50\x44\x46': 'pdf', 
            b'\xFF\xD8\xFF': 'jpg',
            b'\x89\x50\x4E\x47': 'png',
            b'\x00\x00\x00\x18\x66\x74\x79\x70': 'mp4', # ftyp mp4
            b'\x00\x00\x00\x20\x66\x74\x79\x70': 'mp4', # ftyp isom
            b'\x1A\x45\xDF\xA3': 'mkv', # EBML
            b'\x52\x49\x46\x46': 'avi', # RIFF
            b'ID3': 'mp3'
        }
        
        carve_dir = self.output_dir / "carved_files"
        carve_dir.mkdir(exist_ok=True)
        
        try:
            with open(raw_file, 'rb') as f:
                # 使用缓冲读取，避免内存溢出，但为了简化搜索，这里还是分块处理
                # 对于视频文件，我们主要寻找头部。
                # 读取前 100MB 寻找头部? 视频文件可能很大。
                # 简单的全文件扫描
                
                file_size = raw_file.stat().st_size
                chunk_size = 10 * 1024 * 1024 # 10MB buffer
                overlap = 1024 # Overlap for signatures
                
                offset = 0
                while offset < file_size:
                    f.seek(offset)
                    data = f.read(chunk_size + overlap)
                    if not data: break
                    
                    for sig, ext in signatures.items():
                        # 在当前块中搜索
                        pos = 0
                        while True:
                            pos = data.find(sig, pos)
                            if pos == -1: break
                            
                            # 找到了签名
                            abs_pos = offset + pos
                            
                            # 过滤无效的短文件 (比如jpg误报)
                            # 如果是 jpg/png，检查紧接着的数据
                            
                            # 提取逻辑
                            # 如果是视频，尝试提取大块数据
                            is_video = ext in ['mp4', 'mkv', 'avi']
                            extract_size = 100 * 1024 * 1024 if is_video else 5 * 1024 * 1024
                            
                            # 限制在文件末尾
                            extract_size = min(extract_size, file_size - abs_pos)
                            
                            if extract_size > 0:
                                out_name = carve_dir / f"recovered_{abs_pos:08x}.{ext}"
                                print(f"发现 {ext} 签名在 {abs_pos:08x}，提取 {extract_size} 字节...")
                                
                                # 保存当前位置
                                curr = f.tell()
                                f.seek(abs_pos)
                                content = f.read(extract_size)
                                with open(out_name, 'wb') as fout:
                                    fout.write(content)
                                f.seek(curr) # 恢复
                                
                                recovered_count += 1
                            
                            pos += 1
                    
                    offset += chunk_size
                    
        except Exception as e:
            print(f"文件雕刻出错: {e}")
            
        return recovered_count


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

    def _raw_scan(self) -> bool:
        print("执行直接文件扫描...")
        # 直接对源文件进行雕刻
        count = self._smart_carve(self.file_path)
        return count > 0

    def repair(self) -> bool:
        if not self._backup():
            return False
        
        # 检查可用工具
        if not self.available_tools:
            print("错误: 没有找到任何可用的解压工具")
            return False
        
        repair_methods = [
            ("基础修复", lambda: self._fix_header() and self._fix_size()),
            ("完整性测试", self._test_archive),
            ("数据移植", self._data_transplant),
            ("暴力修复", self._brute_force_repair),
            ("直接扫描", self._raw_scan)
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
                        elif name == "直接扫描":
                            success = True
                            break
                        elif name != "直接扫描" and self._test_archive():
                            print(f"修复成功 - {name}")
                            self._extract_archive()
                            success = True
                            break
                        # 数据移植可能返回True但无法通过test_archive(因为它解压出了流文件)
                        if name == "数据移植":
                             # 数据移植如果返回True，说明已经生成了recovered stream并尝试了解压/雕刻
                             success = True
                             # 我们不break，继续尝试其他方法？不，移植是最高级的方法。
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