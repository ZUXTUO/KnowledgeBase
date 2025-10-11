#!/bin/bash

# 音频音量自动归一化脚本
# 功能：查找目录下所有音频文件并自动调节音量到最佳水平

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查ffmpeg是否安装
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}错误: 未找到ffmpeg，请先安装ffmpeg${NC}"
    exit 1
fi

# 检查bc是否安装
if ! command -v bc &> /dev/null; then
    echo -e "${RED}错误: 未找到bc计算器，请安装bc${NC}"
    echo "Ubuntu/Debian: sudo apt install bc"
    echo "CentOS/RHEL: sudo yum install bc"
    exit 1
fi

# 获取脚本运行目录
WORK_DIR=$(pwd)
echo -e "${GREEN}开始处理目录: $WORK_DIR${NC}"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 统计变量
total_files=0
processed_files=0
failed_files=0

echo -e "${YELLOW}正在递归扫描所有音频文件...${NC}"

# 使用更简单可靠的方式查找音频文件
declare -a audio_files

# 使用find命令一次性查找所有常见音频格式
while IFS= read -r -d '' file; do
    audio_files+=("$file")
done < <(find "$WORK_DIR" -type f \( \
    -iname "*.mp3" -o \
    -iname "*.wav" -o \
    -iname "*.flac" -o \
    -iname "*.aac" -o \
    -iname "*.m4a" -o \
    -iname "*.ogg" -o \
    -iname "*.wma" -o \
    -iname "*.opus" -o \
    -iname "*.ac3" -o \
    -iname "*.dts" -o \
    -iname "*.ape" -o \
    -iname "*.alac" \
    \) -print0 2>/dev/null)

total_files=${#audio_files[@]}

if [ $total_files -eq 0 ]; then
    echo -e "${RED}未找到任何音频文件${NC}"
    echo -e "${BLUE}支持的格式: mp3, wav, flac, aac, m4a, ogg, wma, opus, ac3, dts, ape, alac${NC}"
    exit 0
fi

echo -e "${GREEN}找到 $total_files 个音频文件${NC}"
echo -e "${BLUE}列出所有找到的文件:${NC}"
for file in "${audio_files[@]}"; do
    echo "  $(realpath --relative-to="$WORK_DIR" "$file")"
done

echo -e "\n${GREEN}开始处理...${NC}"

# 处理每个音频文件
for file in "${audio_files[@]}"; do
    echo -e "\n${YELLOW}处理文件: $(basename "$file")${NC}"
    echo -e "${BLUE}完整路径: $(realpath --relative-to="$WORK_DIR" "$file")${NC}"
    
    # 获取文件扩展名
    file_ext="${file##*.}"
    file_ext_lower=$(echo "$file_ext" | tr '[:upper:]' '[:lower:]')
    
    # 临时输出文件
    temp_output="$TEMP_DIR/temp_normalized.${file_ext_lower}"
    
    # 第一步：分析音频获取音量信息
    echo "  分析音频音量..."
    volume_info=$(ffmpeg -i "$file" -af "volumedetect" -f null /dev/null 2>&1 | grep -E "(max_volume|mean_volume)")
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}  错误: 无法分析音频文件${NC}"
        ((failed_files++))
        continue
    fi
    
    # 提取最大音量值
    max_volume=$(echo "$volume_info" | grep "max_volume" | sed 's/.*max_volume: \(-*[0-9.]*\) dB.*/\1/')
    
    if [ -z "$max_volume" ]; then
        echo -e "${RED}  错误: 无法获取音量信息${NC}"
        ((failed_files++))
        continue
    fi
    
    echo "  当前最大音量: ${max_volume} dB"
    
    # 计算需要增益的dB值（目标是接近0dB但不削峰）
    # 目标音量设为-1dB以避免削峰
    target_volume=-1.0
    gain_needed=$(echo "$target_volume - ($max_volume)" | bc -l)
    
    echo "  需要增益: ${gain_needed} dB"
    
    # 第二步：应用音量调节
    echo "  应用音量调节..."
    
    # 根据原始文件格式选择合适的编码器和参数
    case "$file_ext_lower" in
        "mp3")
            codec_params="-c:a libmp3lame -b:a 320k"
            ;;
        "wav")
            codec_params="-c:a pcm_s16le"
            ;;
        "flac")
            codec_params="-c:a flac -compression_level 5"
            ;;
        "aac"|"m4a")
            codec_params="-c:a aac -b:a 256k"
            ;;
        "ogg")
            codec_params="-c:a libvorbis -q:a 6"
            ;;
        "opus")
            codec_params="-c:a libopus -b:a 192k"
            ;;
        *)
            # 默认转换为mp3
            codec_params="-c:a libmp3lame -b:a 320k"
            temp_output="$TEMP_DIR/temp_normalized.mp3"
            ;;
    esac
    
    # 构建音频滤镜
    if (( $(echo "$gain_needed > 3" | bc -l) )); then
        # 需要显著增益时，分步处理避免过度失真
        audio_filter="volume=${gain_needed}dB,dynaudnorm=p=0.95:m=10:s=12:g=3:n=0:c=0"
    elif (( $(echo "$gain_needed < -6" | bc -l) )); then
        # 需要显著衰减时，先标准化再调节
        audio_filter="dynaudnorm=p=0.95:m=10:s=12:g=3:n=0:c=0,volume=${gain_needed}dB"
    else
        # 音量相对合适时，主要进行标准化
        combined_gain=$(echo "$gain_needed * 0.8" | bc -l)
        audio_filter="dynaudnorm=p=0.95:m=10:s=12:g=3:n=0:c=0,volume=${combined_gain}dB"
    fi
    
    # 执行FFmpeg处理
    ffmpeg_cmd="ffmpeg -i \"$file\" -af \"$audio_filter\" $codec_params \"$temp_output\" -y"
    
    if eval $ffmpeg_cmd 2>/dev/null; then
        # 检查输出文件是否有效且不为空
        if [ -f "$temp_output" ] && [ -s "$temp_output" ]; then
            # 验证输出文件的音频流
            if ffmpeg -v error -i "$temp_output" -f null - 2>/dev/null; then
                # 创建备份（可选）
                # cp "$file" "${file}.bak"
                
                # 替换原文件
                if mv "$temp_output" "$file"; then
                    echo -e "${GREEN}  ✓ 处理完成并已替换原文件${NC}"
                    ((processed_files++))
                else
                    echo -e "${RED}  错误: 无法替换原文件${NC}"
                    rm -f "$temp_output"
                    ((failed_files++))
                fi
            else
                echo -e "${RED}  错误: 输出文件音频流无效${NC}"
                rm -f "$temp_output"
                ((failed_files++))
            fi
        else
            echo -e "${RED}  错误: 输出文件为空或不存在${NC}"
            rm -f "$temp_output"
            ((failed_files++))
        fi
    else
        echo -e "${RED}  错误: FFmpeg处理失败${NC}"
        echo -e "${RED}  命令: $ffmpeg_cmd${NC}"
        rm -f "$temp_output"
        ((failed_files++))
    fi
    
    # 清理可能存在的临时文件
    rm -f "$temp_output"
done

# 显示处理结果
echo -e "\n${GREEN}======== 处理完成 ========${NC}"
echo -e "总文件数: $total_files"
echo -e "${GREEN}成功处理: $processed_files${NC}"
if [ $failed_files -gt 0 ]; then
    echo -e "${RED}处理失败: $failed_files${NC}"
fi

if [ $processed_files -gt 0 ]; then
    echo -e "\n${GREEN}✓ 成功处理 $processed_files 个音频文件！${NC}"
else
    echo -e "\n${YELLOW}没有成功处理任何文件，请检查文件格式和权限${NC}"
fi