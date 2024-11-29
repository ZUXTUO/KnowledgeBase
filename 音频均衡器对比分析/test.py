import librosa
import numpy as np
import json
import soundfile as sf
import os
import sys

def load_audio(file_path):
    """加载音频文件并返回左右声道"""
    audio, sr = librosa.load(file_path, sr=None, mono=False)  # 保持立体声
    return audio, sr

def load_eq_settings(eq_file):
    """加载均衡器设置（JSON文件）"""
    with open(eq_file, 'r') as f:
        eq_settings = json.load(f)
    return eq_settings

def apply_eq_to_channel(audio_channel, eq_settings, sr):
    """根据均衡器设置调整单个声道的频谱"""
    # 计算音频的STFT
    n_fft = 4096
    hop_length = 512
    D = librosa.stft(audio_channel, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = librosa.magphase(D)

    # 获取频率 bin 的值
    freq_bins = np.fft.fftfreq(n_fft, 1 / sr)[:n_fft // 2 + 1]  # 限制到前 n_fft//2 + 1 个频率

    # 根据频带增益调整频谱
    for band, settings in eq_settings.items():
        lower_freq = settings['lower_freq']
        upper_freq = settings['upper_freq']
        gain = settings['gain']

        # 计算每个频段的对应索引
        band_mask = (freq_bins >= lower_freq) & (freq_bins <= upper_freq)

        # 获取该频段的增益系数（线性增益）
        gain_linear = 10 ** (gain / 20)  # 转换为线性增益

        # 应用增益
        magnitude[band_mask] *= gain_linear

    # 重建时域信号
    D_new = magnitude * phase
    audio_channel_d = librosa.istft(D_new, hop_length=hop_length)
    
    return audio_channel_d

def save_audio(audio, output_file, sr):
    """保存生成的音频文件"""
    # 确保音频数据是 float32 类型
    audio = np.asarray(audio, dtype=np.float32)
    
    # 确保音频数据的维度为 (channels, samples)
    if len(audio.shape) == 1:  # 如果是单声道
        audio = np.expand_dims(audio, axis=0)
    
    # 保存音频
    sf.write(output_file, audio.T, sr)  # 转置，以确保维度正确

def main(eq_file, audio_file_C, output_file_D):
    # 加载均衡器设置和音频文件
    eq_settings = load_eq_settings(eq_file)
    audio_C, sr_C = load_audio(audio_file_C)

    # 分别处理左右声道
    left_channel = audio_C[0, :]
    right_channel = audio_C[1, :]

    # 应用均衡器调整
    left_channel_d = apply_eq_to_channel(left_channel, eq_settings, sr_C)
    right_channel_d = apply_eq_to_channel(right_channel, eq_settings, sr_C)

    # 合并左右声道
    audio_D = np.stack([left_channel_d, right_channel_d], axis=0)

    # 保存生成的 D 音频
    save_audio(audio_D, output_file_D, sr_C)

    print(f"音频 D 已保存到 {output_file_D}")

# 生成输出文件名，去除文件扩展名并加上 "_he1.wav"
def generate_output_filename(input_file):
    base_name = os.path.splitext(input_file)[0]  # 去除文件扩展名
    return f"{base_name}_he1.wav"  # 加上 "_he1" 并保存为 .wav 格式

# 运行代码
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("请提供均衡器设置文件和音频文件路径。")
        sys.exit(1)
    
    eq_file = sys.argv[1]  # 均衡器设置的 JSON 文件路径
    audio_file_C = sys.argv[2]  # 输入音频文件路径
    output_file_D = generate_output_filename(audio_file_C)  # 生成输出文件名

    main(eq_file, audio_file_C, output_file_D)
