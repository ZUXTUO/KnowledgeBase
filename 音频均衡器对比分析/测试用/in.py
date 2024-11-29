import librosa
import numpy as np
import json
import matplotlib.pyplot as plt

def load_audio(file_path):
    """加载音频文件并转换为单声道"""
    audio, sr = librosa.load(file_path, sr=None, mono=True)
    return audio, sr

def calculate_spectrum(audio, sr, n_fft=4096, hop_length=512):
    """计算更高分辨率的频谱图（使用STFT）"""
    D = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
    magnitude, _ = librosa.magphase(D)
    return np.mean(magnitude, axis=1)

def compare_spectra(spectrum_A, spectrum_B):
    """比较原音频和调过均衡器音频的频谱差异"""
    spectrum_A = spectrum_A + 1e-6  # 防止除零错误
    spectrum_B = spectrum_B + 1e-6
    ratio = np.log10(spectrum_B / spectrum_A)  # 使用对数尺度来计算增益差异
    return ratio

def estimate_eq_settings(ratio, num_bands=31, min_freq=20, max_freq=20000):
    """根据频谱差异估计均衡器的调整"""
    eq_settings = {}
    band_width = (max_freq - min_freq) / num_bands
    for i in range(num_bands):
        lower_freq = min_freq + i * band_width
        upper_freq = lower_freq + band_width
        eq_settings[f"band_{i+1}"] = {
            "lower_freq": lower_freq,
            "upper_freq": upper_freq,
            "gain": float(ratio[i])  # 使用对数增益作为均衡器的增益
        }
    return eq_settings

def save_eq_settings(eq_settings, output_file):
    """将均衡器设置保存为JSON文件"""
    # 确保所有的值都是可序列化的
    eq_settings = {
        k: {
            'lower_freq': v['lower_freq'],
            'upper_freq': v['upper_freq'],
            'gain': float(v['gain'])  # 转换为Python的float类型
        }
        for k, v in eq_settings.items()
    }
    
    with open(output_file, 'w') as f:
        json.dump(eq_settings, f, indent=4)

def main(audio_file_A, audio_file_B, output_file):
    # 加载原音频和调过均衡器的音频
    audio_A, sr_A = load_audio(audio_file_A)
    audio_B, sr_B = load_audio(audio_file_B)

    # 计算更高分辨率的频谱
    spectrum_A = calculate_spectrum(audio_A, sr_A)
    spectrum_B = calculate_spectrum(audio_B, sr_B)

    # 对比频谱，估算均衡器的调整
    spectrum_diff = compare_spectra(spectrum_A, spectrum_B)
    eq_settings = estimate_eq_settings(spectrum_diff)

    # 保存均衡器设置到JSON文件
    save_eq_settings(eq_settings, output_file)

    print(f"均衡器设置已保存到 {output_file}")

# 运行代码
if __name__ == "__main__":
    audio_file_A = 'audio_A.wav'  # 原音频文件路径
    audio_file_B = 'audio_B.wav'  # 调整后的音频文件路径
    output_file = 'eq_settings.json'  # 输出的JSON文件路径
    main(audio_file_A, audio_file_B, output_file)
