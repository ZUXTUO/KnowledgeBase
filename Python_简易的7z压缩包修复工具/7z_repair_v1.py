import struct
import os
import subprocess
import shutil
import zlib
import hashlib
from datetime import datetime

class SevenZipRepair:
    def __init__(self, file_path):
        self.file_path = file_path
        self.backup_path = None
        self.log_file = f"{file_path}.repair.log"
        self._init_log()

    def _init_log(self):
        """初始化日志文件"""
        with open(self.log_file, "w") as f:
            f.write(f"7z Archive Repair Log - {datetime.now()}\n")
            f.write("="*50 + "\n")

    def _log(self, message, level="INFO"):
        """记录日志到文件和屏幕"""
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{level}] {message}\n"
        print(log_entry.strip())
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def backup_file(self):
        """创建安全备份"""
        self.backup_path = self.file_path + ".backup"
        try:
            self._log(f"开始备份文件到 {self.backup_path}")
            shutil.copy2(self.file_path, self.backup_path)
            
            # 验证备份完整性
            orig_hash = self._file_hash(self.file_path)
            backup_hash = self._file_hash(self.backup_path)
            if orig_hash == backup_hash:
                self._log("备份验证成功，哈希值: " + orig_hash)
                return True
            raise ValueError("备份文件哈希不匹配")
        except Exception as e:
            self._log(f"备份失败: {str(e)}", "ERROR")
            self.backup_path = None
            return False

    def _file_hash(self, path):
        """计算文件哈希"""
        sha = hashlib.sha256()
        with open(path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()

    def _detect_ThSoft(self, header):
        """检测第三方压缩软件特征"""
        # 检测特征1：特定版本号组合
        if header[6:8] == b'\x00\x03':  # 非标准版本号
            return True
        
        # 检测特征2：特定CRC填充模式
        if header[8:12] == b'\x00'*4:  # 无效CRC
            return True
        
        # 检测特征3：保留字段使用
        if header[28:32] != b'\x00'*4:  # 保留字段非零
            return True
            
        return False

    def check_and_fix_start_header(self):
        """增强版起始头修复"""
        header = self._read_bytes(0, 32)
        if not header:
            self._log("无法读取起始头", "ERROR")
            return False

        # 检测第三方压缩软件特征
        if self._detect_ThSoft(header):
            self._log("检测到可能是由第三方压缩软件压缩的7z文件", "WARNING")

        repair_steps = [
            self._fix_signature,
            self._fix_header_crc,
            self._dynamic_end_header_fix
        ]

        for step in repair_steps:
            if step(header):
                if self.verify_archive():
                    return True
        return False

    def _fix_signature(self, header):
        """修复签名和版本号"""
        if header[:6] != b'\x37\x7A\xBC\xAF\x27\x1C':
            self._log("起始头签名无效，尝试修复...")
            new_header = bytearray(header)
            new_header[0:6] = b'\x37\x7A\xBC\xAF\x27\x1C'
            new_header[6:8] = b'\x00\x04'  # 强制标准版本号
            self._write_bytes(0, bytes(new_header))
            self._log("签名已修复，写入新头: " + str(new_header[:8]))
            return True
        return False

    def _fix_header_crc(self, header):
        """修复CRC校验"""
        self._log("尝试修复起始头CRC...")
        crc_data = header[12:32]
        new_crc = zlib.crc32(crc_data, 0) & 0xFFFFFFFF
        self._write_bytes(8, struct.pack('<I', new_crc))
        self._log(f"更新CRC为: {new_crc:#010x}")
        return True

    def _dynamic_end_header_fix(self, header):
        """动态定位结束头"""
        self._log("开始动态定位结束头...")
        end_pos = self._find_end_header()
        if end_pos:
            start_header_size = 32
            end_header_offset = end_pos - start_header_size
            self._log(f"发现结束头在位置: {end_pos}")
            
            # 更新起始头中的偏移量
            new_offset = struct.pack('<Q', end_header_offset)
            self._write_bytes(12, new_offset)
            self._log(f"更新结束头偏移量为: {end_header_offset}")
            return True
        return False

    def _find_end_header(self):
        """智能查找结束头"""
        signatures = [
            b'\x17\x06\x8D\xAD',
            b'\x01\x04',
            b'\xDA\x01\x15'
        ]
        chunk_size = 4096
        file_size = os.path.getsize(self.file_path)
        
        self._log(f"扫描结束头，文件大小: {file_size} 字节")
        with open(self.file_path, 'rb') as f:
            for offset in range(max(0, file_size-10240), file_size, chunk_size):
                f.seek(offset)
                data = f.read(chunk_size)
                for sig in signatures:
                    pos = data.find(sig)
                    if pos != -1:
                        found = offset + pos
                        self._log(f"找到候选结束头在: {found} (签名: {sig.hex()})")
                        if self._validate_end_header(found):
                            return found
        return None

    def _validate_end_header(self, position):
        """验证结束头有效性"""
        end_header = self._read_bytes(position, 32)
        if not end_header:
            return False
            
        # 基本结构验证
        if len(end_header) < 12:
            return False
            
        # 检查结束头CRC
        header_crc = struct.unpack('<I', self._read_bytes(0x1C, 4))[0]
        current_crc = zlib.crc32(end_header, 0) & 0xFFFFFFFF
        if header_crc != current_crc:
            self._log(f"结束头CRC不匹配: 头中{header_crc:#x} vs 计算{current_crc:#x}")
            return False
            
        return True

    def recover_missing_parts(self):
        """智能文件大小修复"""
        header = self._read_bytes(0, 32)
        if not header:
            return False

        try:
            end_header_offset = struct.unpack('<Q', header[12:20])[0]
            end_header_length = struct.unpack('<Q', header[20:28])[0]
            expected_size = 32 + end_header_offset + end_header_length
        except:
            self._log("解析起始头字段失败", "ERROR")
            return False

        actual_size = os.path.getsize(self.file_path)
        self._log(f"当前大小: {actual_size}, 预期大小: {expected_size}")

        if actual_size == expected_size:
            self._log("文件大小正确，无需调整")
            return True

        try:
            with open(self.file_path, 'r+b') as f:
                if actual_size < expected_size:
                    self._log(f"填充 {expected_size - actual_size} 个零字节")
                    f.seek(expected_size-1)
                    f.write(b'\x00')
                else:
                    self._log(f"截断 {actual_size - expected_size} 字节")
                    f.truncate(expected_size)
            return True
        except Exception as e:
            self._log(f"调整大小失败: {str(e)}", "ERROR")
            return False

    def _read_bytes(self, offset, size):
        """带日志的安全读取"""
        try:
            with open(self.file_path, 'rb') as f:
                f.seek(offset)
                data = f.read(size)
                self._log(f"读取 {len(data)} 字节 @{offset}")
                return data
        except Exception as e:
            self._log(f"读取失败 @{offset}: {str(e)}", "ERROR")
            return None

    def _write_bytes(self, offset, data):
        """带日志的安全写入"""
        try:
            with open(self.file_path, 'r+b') as f:
                f.seek(offset)
                f.write(data)
                self._log(f"写入 {len(data)} 字节 @{offset}")
                return True
        except Exception as e:
            self._log(f"写入失败 @{offset}: {str(e)}", "ERROR")
            return False

    def verify_archive(self):
        """增强版验证"""
        self._log("开始7z完整性验证...")
        try:
            result = subprocess.run(
                ['7z', 't', self.file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
            
            log_msg = [
                "验证结果:",
                f"退出码: {result.returncode}",
                "标准输出:",
                result.stdout.decode(errors='ignore'),
                "标准错误:",
                result.stderr.decode(errors='ignore')
            ]
            self._log('\n'.join(log_msg))
            
            return result.returncode == 0
        except Exception as e:
            self._log(f"验证异常: {str(e)}", "ERROR")
            return False

    def repair(self):
        """主修复流程"""
        if not self.backup_file():
            return False

        repair_steps = [
            ("起始头修复", self.check_and_fix_start_header),
            ("文件大小修复", self.recover_missing_parts),
            ("结束头修复", self.check_and_fix_start_header)  # 复用起始头修复逻辑
        ]

        success = False
        for step_name, step_func in repair_steps:
            self._log(f"执行修复步骤: {step_name}")
            if step_func():
                self._log(f"{step_name} 成功")
                if self.verify_archive():
                    success = True
                    break
            else:
                self._log(f"{step_name} 失败")

        if not success:
            self._log("所有修复尝试失败，开始还原...")
            self._restore_backup()
            return False
        return True

    def _restore_backup(self):
        """从备份恢复"""
        if self.backup_path:
            try:
                self._log("开始还原备份...")
                shutil.copy2(self.backup_path, self.file_path)
                self._log("备份还原成功")
                return True
            except Exception as e:
                self._log(f"还原失败: {str(e)}", "ERROR")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="7z档案修复工具")
    parser.add_argument("file_path", help="需要修复的7z文件路径")
    args = parser.parse_args()

    repair = SevenZipRepair(args.file_path)
    if repair.repair():
        print("修复成功！详细日志见:", repair.log_file)
    else:
        print("修复失败，请检查日志:", repair.log_file)
