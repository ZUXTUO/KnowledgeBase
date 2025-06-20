#!/usr/bin/env python3
import struct
import os
import subprocess
import shutil
import zlib
import hashlib
import tempfile
import re
import zipfile
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, BinaryIO
from io import BytesIO

data_descriptor = False
skip_size_check = False

structDataDescriptor = b"<4sL2L"
stringDataDescriptor = b"PK\x07\x08"
sizeDataDescriptor = struct.calcsize(structDataDescriptor)

_DD_SIGNATURE = 0
_DD_CRC = 1
_DD_COMPRESSED_SIZE = 2
_DD_UNCOMPRESSED_SIZE = 3

class ArchiveRecovery:
    def __init__(self, file_path: str, output_dir: Optional[str] = None):
        self.file_path = Path(file_path).resolve()
        self.file_size = self.file_path.stat().st_size
        self.output_dir = Path(output_dir) if output_dir else self.file_path.parent / f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.output_dir.mkdir(exist_ok=True)
        self.backup_path = self.output_dir / f"{self.file_path.name}.bak"
        self.temp_dir = self.output_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True)
        self.SIG_7Z = b'\x37\x7A\xBC\xAF\x27\x1C'
        self.SIG_ZIP = b'\x50\x4B\x03\x04'
        self.VERSION = b'\x00\x04'
        self.HEADER_SIZE = 32
        self.file_sigs = {
            b'\x50\x4B\x03\x04': 'zip', b'\x25\x50\x44\x46': 'pdf', b'\xFF\xD8\xFF': 'jpg',
            b'\x89\x50\x4E\x47': 'png', b'\x1F\x8B\x08': 'gz', b'\x42\x5A\x68': 'bz2',
            b'\x37\x7A\xBC\xAF': '7z', b'\xFD\x37\x7A\x58\x5A': 'xz'
        }
        self.temp_files: List[Path] = []
        self.archive_type = self._detect_archive_type()
        print(f"开始修复: {self.file_path.name} ({self._format_size(self.file_size)}) - 类型: {self.archive_type}")

    def _detect_archive_type(self) -> str:
        try:
            with open(self.file_path, 'rb') as f:
                header = f.read(8)
                if header.startswith(self.SIG_7Z):
                    return '7z'
                elif header.startswith(self.SIG_ZIP):
                    return 'zip'
                else:
                    return 'unknown'
        except:
            return 'unknown'

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
        try:
            result = subprocess.run(['7z', 't', str(self.file_path)],
                                    capture_output=True, text=True, timeout=30)
            return b"Everything is Ok" in result.stdout.encode() or result.returncode == 0
        except:
            return False

    def _extract_archive(self) -> bool:
        extract_dir = self.output_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        try:
            result = subprocess.run(['7z', 'x', '-y', f'-o{extract_dir}', str(self.file_path)],
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
        try:
            subprocess.run(['7z', 'a', '-t7z', '-mx=1', str(container), str(dummy_file)],
                           check=True, capture_output=True)
            return container
        except:
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
        try:
            result = subprocess.run(['7z', 't', str(path)], capture_output=True, timeout=10)
            return result.returncode == 0
        except:
            return False

    def _raw_recovery(self) -> bool:
        print("执行原始数据恢复...")
        try:
            raw_file = self.output_dir / "raw_data.bin"
            with open(self.file_path, 'rb') as src, open(raw_file, 'wb') as dst:
                src.seek(self.HEADER_SIZE)
                shutil.copyfileobj(src, dst)
            recovered_count = 0
            try:
                result = subprocess.run(['7z', 'x', '-y', f'-o{self.output_dir}', str(raw_file)],
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
            print(f"错误: 命令 '{command[0]}' 未找到。请确保7z或HaoZipC.exe已安装并添加到系统PATH中。")
            raise
        except subprocess.TimeoutExpired:
            print(f"错误: 命令 '{cmd_str}' 执行超时 ({timeout} 秒)。")
            raise
        except Exception as e:
            print(f"执行命令 '{cmd_str}' 时发生未知错误: {e}")
            raise

    def _can_list_archive(self, file_path: Path) -> bool:
        print(f"检测压缩包内容列表: {file_path.name}")
        try:
            result_7z = self._run_command_and_log(['7z', 'l', str(file_path)], timeout=15)
            if result_7z.returncode == 0 and ("Files:" in result_7z.stdout or "文件:" in result_7z.stdout):
                print(f"[7z] 检测成功 - 可列出内容")
                if self._extract_archive_with_specific_tool(file_path, '7z'):
                    return True
            result_haozip = self._run_command_and_log(['HaoZipC.exe', 'l', str(file_path)], timeout=15, cwd='.')
            if result_haozip.returncode == 0 and ("个文件" in result_haozip.stdout or "files" in result_haozip.stdout):
                print(f"[HaoZipC] 检测成功 - 可列出内容")
                return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
            elif result_haozip.returncode == 0 and len(result_haozip.stdout) > 200:
                print(f"[HaoZipC] 检测成功 - 有详细输出")
                return self._extract_archive_with_specific_tool(file_path, 'HaoZipC')
        except Exception as e:
            print(f"列表检测失败: {e}")
        print(f"无法列出 {file_path.name} 的内容")
        return False

    def _extract_archive_with_specific_tool(self, file_path: Path, tool: str) -> bool:
        extract_dir = self.output_dir / "OUTPUT"
        extract_dir.mkdir(exist_ok=True)
        command = []
        if tool == '7z':
            command = ['7z', 'x', '-y', f'-o{extract_dir}', str(file_path)]
        elif tool == 'HaoZipC':
            command = ['HaoZipC.exe', 'x', str(file_path), f'-o{extract_dir}']
        else:
            print(f"不支持的解压工具: {tool}")
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

    def _write_data(self, filename, data):
        try:
            if filename.endswith(b'/'):
                os.makedirs(filename.decode('utf-8'), exist_ok=True)
                print(f"已创建目录: {filename.decode('utf-8')}")
            else:
                output_path = self.output_dir / "extracted" / filename.decode('utf-8')
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(data)
                print(f"已写入文件: {output_path}")
        except OSError as e:
            print(f"写入 {filename.decode('utf-8')} 时出错: {e}")

    def _fdescriptor_reader(self, file, initial_offset):
        offset = initial_offset
        file.seek(offset)
        buffer_size = 4096
        
        while True:
            temp = file.read(buffer_size)
            if not temp:
                print('已找到文件末尾。在搜索数据描述符时跳过了一些条目。')
                return None

            parts = temp.split(stringDataDescriptor)
            if len(parts) > 1:
                offset += len(parts[0])
                break
            else:
                offset += buffer_size
        
        file.seek(offset)
        ddescriptor_raw = file.read(sizeDataDescriptor)
        if len(ddescriptor_raw) < sizeDataDescriptor:
            print('已找到文件末尾。数据描述符不完整。')
            return None
        
        try:
            ddescriptor = struct.unpack(structDataDescriptor, ddescriptor_raw)
            if ddescriptor[_DD_SIGNATURE] != stringDataDescriptor:
                print(f'警告: 数据描述符签名在偏移量 {offset} 处不匹配。预期 {stringDataDescriptor}，得到 {ddescriptor[_DD_SIGNATURE]}')
                return None
            return ddescriptor
        except struct.error as e:
            print(f"在偏移量 {offset} 处解包数据描述符时出错: {e}")
            return None

    def _repair_zip(self) -> bool:
        print(f'正在手动尝试读取 {self.file_path}。')

        try:
            with zipfile.ZipFile(self.file_path, 'r') as myzip:
                files_from_cd = myzip.namelist()
                print(f'从中央目录找到 {len(files_from_cd)} 个文件:')
                print('- ' + '\n- '.join(files_from_cd))
        except zipfile.BadZipFile:
            print(f'警告: 根据 zipfile 模块，{self.file_path} 不是有效的 zip 文件。将继续手动解析。')
        except Exception as e:
            print(f"读取中央目录时发生意外错误: {e}")

        print(f'正在手动读取 {self.file_path} 的 ZIP 条目。')
        
        global data_descriptor
        data_descriptor = False

        with open(self.file_path, 'rb') as f:
            file_count = 0
            while True:
                current_offset = f.tell()
                fheader_raw = f.read(zipfile.sizeFileHeader)
                
                if len(fheader_raw) < zipfile.sizeFileHeader:
                    print('已达到文件末尾或文件头不完整。停止。')
                    break
                
                try:
                    fheader = struct.unpack(zipfile.structFileHeader, fheader_raw)
                except struct.error as e:
                    print(f"在偏移量 {current_offset} 处解包文件头时出错: {e}。停止。")
                    break

                if fheader[zipfile._FH_SIGNATURE] == zipfile.stringCentralDir:
                    print('已找到中央目录的开头。所有文件条目已处理。')
                    break

                if fheader[zipfile._FH_SIGNATURE] != zipfile.stringFileHeader:
                    print(f'警告: 预期文件头签名 ({zipfile.stringFileHeader})，但在偏移量 {current_offset} 处得到 "{fheader[zipfile._FH_SIGNATURE].hex()}"。跳过此条目。')
                    f.seek(current_offset + 1)
                    continue
                
                file_count += 1
                
                flag_bits = fheader[zipfile._FH_GENERAL_PURPOSE_FLAG_BITS]
                data_descriptor_in_use = bool(flag_bits & 0x8)
                
                fname_len = fheader[zipfile._FH_FILENAME_LENGTH]
                extra_field_len = fheader[zipfile._FH_EXTRA_FIELD_LENGTH]

                try:
                    fname_raw = f.read(fname_len)
                    fname = fname_raw.decode('utf-8', errors='replace')
                except UnicodeDecodeError:
                    print(f"警告: 无法解码偏移量 {current_offset} 处的文件名。原始数据: {fname_raw}")
                    fname = f"undecodable_filename_{file_count}"

                if extra_field_len:
                    f.read(extra_field_len)
                
                print(f'\n--- 找到条目: {fname} ---')
                print(f'偏移量: {current_offset}')
                print(f'压缩方法: {fheader[zipfile._FH_COMPRESSION_METHOD]}')
                print(f'压缩大小 (来自头部): {fheader[zipfile._FH_COMPRESSED_SIZE]}')
                print(f'未压缩大小 (来自头部): {fheader[zipfile._FH_UNCOMPRESSED_SIZE]}')
                print(f'CRC (来自头部): {fheader[zipfile._FH_CRC]:08x}')
                print(f'正在使用数据描述符: {data_descriptor_in_use}')

                zi = zipfile.ZipInfo()
                zi.filename = fname_raw
                zi.compress_type = fheader[zipfile._FH_COMPRESSION_METHOD]
                zi.flag_bits = flag_bits
                
                if data_descriptor_in_use:
                    zi.compress_size = 0
                    zi.file_size = 0
                    zi.CRC = 0
                else:
                    zi.compress_size = fheader[zipfile._FH_COMPRESSED_SIZE]
                    zi.file_size = fheader[zipfile._FH_UNCOMPRESSED_SIZE]
                    zi.CRC = fheader[zipfile._FH_CRC]

                try:
                    data_start_offset = f.tell()
                    
                    if data_descriptor_in_use:
                        print("正在读取压缩数据直到数据描述符签名...")
                        temp_data = b''
                        while True:
                            chunk = f.read(4096)
                            if not chunk:
                                print("错误: 在找到数据描述符签名之前已达到文件末尾。")
                                raise EOFError("读取带数据描述符的压缩数据时文件提前结束。")
                            temp_data += chunk
                            if stringDataDescriptor in temp_data:
                                compressed_data = temp_data.split(stringDataDescriptor, 1)[0]
                                f.seek(data_start_offset + len(compressed_data))
                                break
                        zi.compress_size = len(compressed_data)
                    else:
                        compressed_data = f.read(zi.compress_size)
                        if len(compressed_data) != zi.compress_size:
                            print(f"警告: 为 {fname} 读取了 {len(compressed_data)} 字节，预期 {zi.compress_size} 字节。文件可能已截断。")
                    
                    zef = zipfile.ZipExtFile(BytesIO(compressed_data), 'rb', zi)
                    data = zef.read()

                    if data_descriptor_in_use:
                        ddescriptor = self._fdescriptor_reader(f, f.tell())
                        if ddescriptor:
                            zi.compress_size = ddescriptor[_DD_COMPRESSED_SIZE]
                            zi.file_size = ddescriptor[_DD_UNCOMPRESSED_SIZE]
                            zi.CRC = ddescriptor[_DD_CRC]
                            print(f'已从数据描述符更新大小: 压缩={zi.compress_size}, 未压缩={zi.file_size}, CRC={zi.CRC:08x}')
                        else:
                            print(f"警告: 无法读取 {fname} 的数据描述符。如果可用，将使用头部值。")

                    if not skip_size_check and len(data) != zi.file_size:
                        print(f"错误: {fname.decode('utf-8') if isinstance(fname, bytes) else fname} 的解压缩数据大小不匹配! 预期 {zi.file_size}，得到 {len(data)}。这表示已损坏。")
                        self._write_data(fname, data) 
                        continue
                    
                    calc_crc = zipfile.crc32(data) & 0xffffffff
                    if calc_crc != zi.CRC:
                        print(f'错误: {fname.decode("utf-8") if isinstance(fname, bytes) else fname} 的 CRC 不匹配! 计算结果 {calc_crc:08x}，预期 {zi.CRC:08x}。这表示已损坏。')
                        self._write_data(fname, data)
                        continue
                    
                    print(f"已成功处理并验证 {fname.decode('utf-8') if isinstance(fname, bytes) else fname}")
                    self._write_data(fname, data)

                except zipfile.BadZipFile as e:
                    print(f"提取 {fname.decode('utf-8') if isinstance(fname, bytes) else fname} (错误的 ZIP 数据) 时出错: {e}。跳过此文件。")
                    if data_descriptor_in_use:
                        f.seek(f.tell() + sizeDataDescriptor)
                    else:
                        f.seek(data_start_offset + zi.compress_size)
                    continue
                except Exception as e:
                    print(f"处理 {fname.decode('utf-8') if isinstance(fname, bytes) else fname} 时发生意外错误: {e}。跳过此文件。")
                    if data_descriptor_in_use:
                        f.seek(f.tell() + sizeDataDescriptor)
                    else:
                        f.seek(data_start_offset + zi.compress_size)
                    continue
        print(f'\n已完成处理 {self.file_path}。')
        return True

    def repair(self) -> bool:
        if not self._backup():
            return False
        
        repair_methods = []
        if self.archive_type == '7z':
            repair_methods = [
                ("基础修复", lambda: self._fix_header() and self._fix_size()),
                ("完整性测试", self._test_archive),
                ("数据移植", self._data_transplant),
                ("暴力修复", self._brute_force_repair),
                ("原始恢复", self._raw_recovery)
            ]
        elif self.archive_type == 'zip':
            repair_methods = [
                ("ZIP 修复", self._repair_zip),
                ("原始恢复", self._raw_recovery)
            ]
        else:
            print("不支持的压缩文件类型，尝试原始恢复。")
            repair_methods = [("原始恢复", self._raw_recovery)]

        success = False
        try:
            for name, method in repair_methods:
                print(f"\n执行 {name}...")
                try:
                    if method():
                        if name == "暴力修复" or name == "ZIP 修复":
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
        print("用法: python script.py <文件路径> [输出目录]")
        return
    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    recovery = ArchiveRecovery(file_path, output_dir)
    success = recovery.repair()
    print(f"\n修复{'成功' if success else '失败'}")
    print(f"输出目录: {recovery.output_dir}")
    if success:
        print("请查看输出目录中的恢复文件")

if __name__ == "__main__":
    main()
