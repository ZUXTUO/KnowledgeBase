import os
import librosa
import numpy as np
import json
import soundfile as sf
import sys
from spleeter.separator import Separator

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
    n_fft = 4096
    hop_length = 512
    D = librosa.stft(audio_channel, n_fft=n_fft, hop_length=hop_length)
    magnitude, phase = librosa.magphase(D)
    
    freq_bins = np.fft.fftfreq(n_fft, 1 / sr)[:n_fft // 2 + 1]

    for band, settings in eq_settings.items():
        lower_freq = settings['lower_freq']
        upper_freq = settings['upper_freq']
        gain = settings['gain']
        
        band_mask = (freq_bins >= lower_freq) & (freq_bins <= upper_freq)
        gain_linear = 10 ** (gain / 20)
        magnitude[band_mask] *= gain_linear

    D_new = magnitude * phase
    audio_channel_d = librosa.istft(D_new, hop_length=hop_length)
    
    return audio_channel_d

def enhance_bass(D, bass_boost_factor=1.3):
    """增强低频部分"""
    frequencies = librosa.fft_frequencies()
    low_freq_indexes = np.where(frequencies < 135)[0]
    D[low_freq_indexes] *= bass_boost_factor
    return D

def enhance_treble(D, treble_boost_factor=1.25):
    """增强高频部分"""
    frequencies = librosa.fft_frequencies()
    high_freq_indexes = np.where(frequencies > 3000)[0]
    D[high_freq_indexes] *= treble_boost_factor
    return D

def enhance_vocals(vocals, vocal_boost_factor=1.2):
    """增强人声部分"""
    # 将人声的幅度增益进行放大
    return vocals * vocal_boost_factor

def apply_stereo_widening(D_left, D_right, shift_amount=0.3):
    """应用立体声扩展"""
    phase_left = np.angle(D_left)
    phase_right = np.angle(D_right)

    phase_right_shifted = phase_right + shift_amount
    D_left_shifted = np.abs(D_left) * np.exp(1j * phase_left)
    D_right_shifted = np.abs(D_right) * np.exp(1j * phase_right_shifted)

    return D_left_shifted, D_right_shifted

def save_audio(audio, output_file, sr):
    """保存生成的音频文件"""
    audio = np.asarray(audio, dtype=np.float32)
    
    if len(audio.shape) == 1:
        audio = np.expand_dims(audio, axis=0)
    
    sf.write(output_file, audio.T, sr)

def generate_output_filename(input_file):
    base_name = os.path.splitext(input_file)[0]
    return f"{base_name}_he1_max.wav"

def separate_vocals(input_file):
    """使用 Spleeter 分离人声"""
    separator = Separator('spleeter:2stems')  # 2stems 模型: 人声 + 音乐伴奏
    output_dir = os.path.join(os.path.dirname(input_file), 'separated')
    os.makedirs(output_dir, exist_ok=True)
    
    # Print the output directory for debugging
    print(f"Output directory for separated files: {output_dir}")
    
    separator.separate_to_file(input_file, output_dir)
    
    # Extract base name and form the full path for vocals and accompaniment
    base_name = os.path.basename(input_file).split('.')[0]
    vocal_file = os.path.join(output_dir, base_name, 'vocals.wav')
    accompaniment_file = os.path.join(output_dir, base_name, 'accompaniment.wav')
    
    # Print paths for debugging
    print(f"Vocal file path: {vocal_file}")
    print(f"Accompaniment file path: {accompaniment_file}")
    
    return vocal_file, accompaniment_file

def match_audio_length(audio1, audio2):
    """将两个音频信号的长度匹配"""
    max_len = max(len(audio1), len(audio2))
    audio1 = np.pad(audio1, (0, max_len - len(audio1)), 'constant')
    audio2 = np.pad(audio2, (0, max_len - len(audio2)), 'constant')
    return audio1, audio2

def main(eq_file, audio_file_C, output_file_D):
    eq_settings = load_eq_settings(eq_file)
    
    # 分离人声
    vocal_file, accompaniment_file = separate_vocals(audio_file_C)
    
    # 加载原音频文件（左右声道）
    original_audio, sr = load_audio(audio_file_C)  # 加载原始音频文件，保持立体声
    left_channel = original_audio[0, :]  # 左声道
    right_channel = original_audio[1, :]  # 右声道
    
    # 加载分离出的人声
    vocals, _ = librosa.load(vocal_file, sr=sr, mono=False)
    
    # 应用均衡器
    left_channel_eq = apply_eq_to_channel(left_channel, eq_settings, sr)
    right_channel_eq = apply_eq_to_channel(right_channel, eq_settings, sr)
    
    # 转换为频谱
    n_fft = 4096
    hop_length = 512
    D_left = librosa.stft(left_channel_eq, n_fft=n_fft, hop_length=hop_length)
    D_right = librosa.stft(right_channel_eq, n_fft=n_fft, hop_length=hop_length)
    
    # 增强低频和高频
    D_left = enhance_bass(D_left)
    D_right = enhance_bass(D_right)
    D_left = enhance_treble(D_left)
    D_right = enhance_treble(D_right)
    
    # 立体声扩展
    D_left_shifted, D_right_shifted = apply_stereo_widening(D_left, D_right)
    
    # 重建左右声道
    left_channel_final = librosa.istft(D_left_shifted, hop_length=hop_length)
    right_channel_final = librosa.istft(D_right_shifted, hop_length=hop_length)
    
    # 将左右声道和人声的长度匹配
    left_channel_final, right_channel_final = match_audio_length(left_channel_final, right_channel_final)
    vocals[0, :], left_channel_final = match_audio_length(vocals[0, :], left_channel_final)
    vocals[0, :], right_channel_final = match_audio_length(vocals[0, :], right_channel_final)
    
    # 创建最终输出音频（包含左右声道和增强的人声）
    audio_D = np.stack([left_channel_final, right_channel_final, vocals[0, :]], axis=0)
    
    # 保存输出音频文件
    save_audio(audio_D, output_file_D, sr)
    print(f"音频 D 已保存到 {output_file_D}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("请提供均衡器设置文件和音频文件路径。")
        sys.exit(1)
    
    eq_file = sys.argv[1]
    audio_file_C = sys.argv[2]
    output_file_D = generate_output_filename(audio_file_C)
    
    main(eq_file, audio_file_C, output_file_D)
