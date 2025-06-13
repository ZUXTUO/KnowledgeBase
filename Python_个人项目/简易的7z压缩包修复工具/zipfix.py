import zipfile
import struct
import sys
import os

data_descriptor = False
skip_size_check = False

structDataDescriptor = b"<4sL2L"
stringDataDescriptor = b"PK\x07\x08"
sizeDataDescriptor = struct.calcsize(structDataDescriptor)

_DD_SIGNATURE = 0
_DD_CRC = 1
_DD_COMPRESSED_SIZE = 2
_DD_UNCOMPRESSED_SIZE = 3

def write_data(filename, data):
    """
    将数据写入文件，如果文件名以 '/' 结尾则创建目录。
    """
    try:
        if filename.endswith(b'/'):
            os.makedirs(filename.decode('utf-8'), exist_ok=True)
            print(f"已创建目录: {filename.decode('utf-8')}")
        else:
            with open(filename.decode('utf-8'), 'wb') as f:
                f.write(data)
            print(f"已写入文件: {filename.decode('utf-8')}")
    except OSError as e:
        print(f"写入 {filename.decode('utf-8')} 时出错: {e}")

def fdescriptor_reader(file, initial_offset):
    """
    读取 ZIP 条目的数据描述符。
    """
    offset = initial_offset
    file.seek(offset)
    buffer_size = 4096 # 增加缓冲区大小以提高性能
    
    # 搜索数据描述符签名
    while True:
        temp = file.read(buffer_size)
        if not temp: # 文件结束
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


def main(filename):
    """
    处理 ZIP 文件的主函数。
    """
    print(f'正在手动尝试读取 {filename}。')

    try:
        # 首先，如果这是一个有效的 ZIP 文件，尝试读取中心目录
        with zipfile.ZipFile(filename, 'r') as myzip:
            files_from_cd = myzip.namelist()
            print(f'从中心目录找到 {len(files_from_cd)} 个文件:')
            print('- ' + '\n- '.join(files_from_cd))
    except zipfile.BadZipFile:
        print(f'警告: 根据 zipfile 模块，{filename} 不是有效的 zip 文件。将继续手动解析。')
    except Exception as e:
        print(f"读取中心目录时发生意外错误: {e}")

    print(f'正在手动读取 {filename} 的 ZIP 条目。')
    
    global data_descriptor # 确保我们修改全局变量
    data_descriptor = False # 为每个文件重置

    with open(filename, 'rb') as f:
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
                print('已找到中心目录的开头。所有文件条目已处理。')
                break

            if fheader[zipfile._FH_SIGNATURE] != zipfile.stringFileHeader:
                print(f'警告: 预期文件头签名 ({zipfile.stringFileHeader})，但在偏移量 {current_offset} 处得到 "{fheader[zipfile._FH_SIGNATURE].hex()}"。跳过此条目。')
                f.seek(current_offset + 1) # 尝试跳过一个字节并找到下一个头
                continue
            
            file_count += 1
            
            flag_bits = fheader[zipfile._FH_GENERAL_PURPOSE_FLAG_BITS]
            data_descriptor_in_use = bool(flag_bits & 0x8)
            
            fname_len = fheader[zipfile._FH_FILENAME_LENGTH]
            extra_field_len = fheader[zipfile._FH_EXTRA_FIELD_LENGTH]

            try:
                fname_raw = f.read(fname_len)
                fname = fname_raw.decode('utf-8', errors='replace') # 使用错误替换解码
            except UnicodeDecodeError:
                print(f"警告: 无法解码偏移量 {current_offset} 处的文件名。原始数据: {fname_raw}")
                fname = f"undecodable_filename_{file_count}"

            if extra_field_len:
                f.read(extra_field_len) # 跳过额外字段
            
            print(f'\n--- 找到条目: {fname} ---')
            print(f'偏移量: {current_offset}')
            print(f'压缩方法: {fheader[zipfile._FH_COMPRESSION_METHOD]}')
            print(f'压缩大小 (来自头部): {fheader[zipfile._FH_COMPRESSED_SIZE]}')
            print(f'未压缩大小 (来自头部): {fheader[zipfile._FH_UNCOMPRESSED_SIZE]}')
            print(f'CRC (来自头部): {fheader[zipfile._FH_CRC]:08x}')
            print(f'正在使用数据描述符: {data_descriptor_in_use}')

            # 伪造一个 zipinfo 记录
            zi = zipfile.ZipInfo()
            zi.filename = fname_raw
            zi.compress_type = fheader[zipfile._FH_COMPRESSION_METHOD]
            zi.flag_bits = flag_bits
            
            # 如果使用数据描述符，头部中的初始大小为 0。
            # 我们需要在压缩数据之后从数据描述符中读取它们。
            if data_descriptor_in_use:
                zi.compress_size = 0 # 将从数据描述符更新
                zi.file_size = 0     # 将从数据描述符更新
                zi.CRC = 0           # 将从数据描述符更新
            else:
                zi.compress_size = fheader[zipfile._FH_COMPRESSED_SIZE]
                zi.file_size = fheader[zipfile._FH_UNCOMPRESSED_SIZE]
                zi.CRC = fheader[zipfile._FH_CRC]

            # 读取文件内容
            try:
                # 在读取压缩数据之前存储当前文件指针
                data_start_offset = f.tell()
                
                # 如果使用数据描述符，我们读取直到找到数据描述符签名。
                # 否则，我们读取指定的压缩大小。
                if data_descriptor_in_use:
                    # 在这种情况下，zi.compress_size 最初为 0。我们将读取直到签名。
                    print("正在读取压缩数据直到数据描述符签名...")
                    temp_data = b''
                    while True:
                        chunk = f.read(4096) # 分块读取
                        if not chunk:
                            print("错误: 在找到数据描述符签名之前已达到文件末尾。")
                            raise EOFError("读取带数据描述符的压缩数据时文件提前结束。")
                        temp_data += chunk
                        if stringDataDescriptor in temp_data:
                            # 找到签名，提取其之前的数据
                            compressed_data = temp_data.split(stringDataDescriptor, 1)[0]
                            # 将文件指针移回签名之前
                            f.seek(data_start_offset + len(compressed_data))
                            break
                    zi.compress_size = len(compressed_data) # 更新压缩大小
                else:
                    compressed_data = f.read(zi.compress_size)
                    if len(compressed_data) != zi.compress_size:
                        print(f"警告: 为 {fname} 读取了 {len(compressed_data)} 字节，预期 {zi.compress_size} 字节。文件可能已截断。")
                        # 这可能表示损坏。我们可以尝试继续，但要标记它。
                
                # 重要提示: ZipExtFile 期望文件对象位于压缩数据的开头。
                # 由于我们已将其读入 compressed_data，因此我们将创建一个 BytesIO 对象。
                from io import BytesIO
                zef = zipfile.ZipExtFile(BytesIO(compressed_data), 'rb', zi)
                data = zef.read()

                # 如果正在使用数据描述符，请立即读取并更新 zi
                if data_descriptor_in_use:
                    ddescriptor = fdescriptor_reader(f, f.tell())
                    if ddescriptor:
                        zi.compress_size = ddescriptor[_DD_COMPRESSED_SIZE]
                        zi.file_size = ddescriptor[_DD_UNCOMPRESSED_SIZE]
                        zi.CRC = ddescriptor[_DD_CRC]
                        print(f'已从数据描述符更新大小: 压缩={zi.compress_size}, 未压缩={zi.file_size}, CRC={zi.CRC:08x}')
                    else:
                        print(f"警告: 无法读取 {fname} 的数据描述符。如果可用，将使用头部值。")
                        # 如果数据描述符丢失，请尝试推断或跳过。
                        # 目前，我们将让下面的健全性检查可能失败。

                # 健全性检查
                if not skip_size_check and len(data) != zi.file_size:
                    print(f"错误: {fname.decode('utf-8') if isinstance(fname, bytes) else fname} 的解压缩数据大小不匹配! 预期 {zi.file_size}，得到 {len(data)}。这表示已损坏。")
                    # 尝试写入我们拥有的内容，但警告用户
                    write_data(fname, data) 
                    continue # 移动到下一个条目，此条目可能已损坏
                
                calc_crc = zipfile.crc32(data) & 0xffffffff
                if calc_crc != zi.CRC:
                    print(f'错误: {fname.decode("utf-8") if isinstance(fname, bytes) else fname} 的 CRC 不匹配! 计算结果 {calc_crc:08x}，预期 {zi.CRC:08x}。这表示已损坏。')
                    # 尝试写入我们拥有的内容，但警告用户
                    write_data(fname, data)
                    continue # 移动到下一个条目
                
                print(f"已成功处理并验证 {fname.decode('utf-8') if isinstance(fname, bytes) else fname}")
                write_data(fname, data)

            except zipfile.BadZipFile as e:
                print(f"提取 {fname.decode('utf-8') if isinstance(fname, bytes) else fname} (错误的 ZIP 数据) 时出错: {e}。跳过此文件。")
                # 尝试将文件指针前进到下一个预期头部
                if data_descriptor_in_use:
                    # 如果是数据描述符，我们需要找到它的结尾，然后是下一个头部
                    # 在不知道其大小的情况下，这很棘手。我们将尝试找到下一个头部。
                    f.seek(f.tell() + sizeDataDescriptor) # 跳过潜在描述符
                else:
                    f.seek(data_start_offset + zi.compress_size)
                continue
            except Exception as e:
                print(f"处理 {fname.decode('utf-8') if isinstance(fname, bytes) else fname} 时发生意外错误: {e}。跳过此文件。")
                # 尝试通过猜测其结尾来移动到下一个条目。
                # 这是一个启发式方法，可能会失败。
                if data_descriptor_in_use:
                    f.seek(f.tell() + sizeDataDescriptor) # 跳过潜在描述符
                else:
                    f.seek(data_start_offset + zi.compress_size)
                continue

    print(f'\n已完成处理 {filename}。')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("用法: python zipfix.py <文件名>")
    else:
        main(sys.argv[1])
