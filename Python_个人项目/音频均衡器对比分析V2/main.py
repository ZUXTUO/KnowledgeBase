import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import json
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# 配置matplotlib以支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

class AudioEQAnalyzer:
    def __init__(self, num_bands=31, min_freq=20, max_freq=20000, 
                 n_fft=8192, hop_length=256, smoothing_sigma=2.0):
        self.num_bands = num_bands
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.smoothing_sigma = smoothing_sigma
        self.freq_bands = self._calculate_freq_bands()
        
    def _calculate_freq_bands(self):
        log_min = np.log10(self.min_freq)
        log_max = np.log10(self.max_freq)
        log_freqs = np.linspace(log_min, log_max, self.num_bands + 1)
        return 10 ** log_freqs
    
    def load_audio(self, file_path):
        audio, sr = librosa.load(file_path, sr=None, mono=True)
        audio = self._preprocess_audio(audio)
        return audio, sr
    
    def _preprocess_audio(self, audio):
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        audio = librosa.effects.trim(audio, top_db=30)[0]
        return audio
    
    def calculate_detailed_spectrum(self, audio, sr):
        window = 'hann'
        D = librosa.stft(audio, n_fft=self.n_fft, hop_length=self.hop_length, window=window)
        magnitude = np.abs(D)
        spectrum = np.exp(np.mean(np.log(magnitude + 1e-10), axis=1))
        spectrum = gaussian_filter1d(spectrum, sigma=self.smoothing_sigma)
        freqs = np.fft.fftfreq(self.n_fft, 1/sr)[:self.n_fft//2 + 1]
        return spectrum, freqs
    
    def compare_spectra_advanced(self, spectrum_A, spectrum_B, freqs):
        spectrum_A = spectrum_A + 1e-10
        spectrum_B = spectrum_B + 1e-10
        gain_ratio = 20 * np.log10(spectrum_B / spectrum_A)
        eq_gains = self._map_spectrum_to_bands(gain_ratio, freqs)
        return eq_gains
    
    def _map_spectrum_to_bands(self, gain_spectrum, freqs):
        eq_gains = []
        for i in range(self.num_bands):
            lower_freq = self.freq_bands[i]
            upper_freq = self.freq_bands[i + 1]
            mask = (freqs >= lower_freq) & (freqs <= upper_freq)
            if np.any(mask):
                band_gains = gain_spectrum[mask]
                weights = np.abs(gain_spectrum[mask]) + 1e-10
                weighted_gain = np.average(band_gains, weights=weights)
                eq_gains.append(weighted_gain)
            else:
                eq_gains.append(np.interp((lower_freq + upper_freq) / 2, freqs, gain_spectrum))
        return np.array(eq_gains)
    
    def create_eq_settings(self, eq_gains):
        eq_settings = {
            "metadata": {
                "num_bands": self.num_bands,
                "min_freq": self.min_freq,
                "max_freq": self.max_freq,
                "analysis_method": "advanced_spectral_analysis",
                "frequency_distribution": "logarithmic"
            },
            "bands": {}
        }
        for i in range(self.num_bands):
            center_freq = np.sqrt(self.freq_bands[i] * self.freq_bands[i + 1])
            eq_settings["bands"][f"band_{i+1:02d}"] = {
                "center_freq": float(center_freq),
                "lower_freq": float(self.freq_bands[i]),
                "upper_freq": float(self.freq_bands[i + 1]),
                "gain_db": float(eq_gains[i]),
                "q_factor": 1.0
            }
        return eq_settings
    
    def save_eq_settings(self, eq_settings, output_file):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(eq_settings, f, indent=4, ensure_ascii=False)
    
    def plot_comparison(self, spectrum_A, spectrum_B, freqs, eq_gains, ax1, ax2):
        ax1.clear()
        ax2.clear()

        ax1.semilogx(freqs[1:], 20*np.log10(spectrum_A[1:] + 1e-10), 
                     label='原始音频 A', alpha=0.7, linewidth=1.5)
        ax1.semilogx(freqs[1:], 20*np.log10(spectrum_B[1:] + 1e-10), 
                     label='处理音频 B', alpha=0.7, linewidth=1.5)
        ax1.set_xlabel('频率 (Hz)')
        ax1.set_ylabel('幅度 (dB)')
        ax1.set_title('音频频谱对比')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(20, 20000)
        
        band_centers = [np.sqrt(self.freq_bands[i] * self.freq_bands[i + 1]) 
                       for i in range(self.num_bands)]
        ax2.semilogx(band_centers, eq_gains, 'o-', linewidth=2, markersize=6)
        ax2.set_xlabel('频率 (Hz)')
        ax2.set_ylabel('增益 (dB)')
        ax2.set_title('估算的均衡器响应')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.5)
        ax2.set_xlim(20, 20000)
        
        plt.tight_layout()
    
    def analyze_audio_pair(self, audio_A_path, audio_B_path, output_json_path, 
                          ax1=None, ax2=None):
        audio_A, sr_A = self.load_audio(audio_A_path)
        audio_B, sr_B = self.load_audio(audio_B_path)
        
        if sr_A != sr_B:
            target_sr = min(sr_A, sr_B)
            if sr_A != target_sr:
                audio_A = librosa.resample(audio_A, orig_sr=sr_A, target_sr=target_sr)
            if sr_B != target_sr:
                audio_B = librosa.resample(audio_B, orig_sr=sr_B, target_sr=target_sr)
            sr_A = sr_B = target_sr
        
        spectrum_A, freqs = self.calculate_detailed_spectrum(audio_A, sr_A)
        spectrum_B, _ = self.calculate_detailed_spectrum(audio_B, sr_B)
        
        eq_gains = self.compare_spectra_advanced(spectrum_A, spectrum_B, freqs)
        eq_settings = self.create_eq_settings(eq_gains)
        self.save_eq_settings(eq_settings, output_json_path)
        
        if ax1 and ax2:
            self.plot_comparison(spectrum_A, spectrum_B, freqs, eq_gains, ax1, ax2)
        
        return eq_settings

class AudioEQApplicator:
    def __init__(self, n_fft=8192, hop_length=256, overlap_add_method=True):
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.overlap_add_method = overlap_add_method
        self.window = signal.windows.hann(self.n_fft, sym=False)
        
    def load_audio(self, file_path, target_sr=None):
        audio, sr = librosa.load(file_path, sr=target_sr, mono=False)
        is_stereo = len(audio.shape) > 1 and audio.shape[0] == 2
        if not is_stereo and len(audio.shape) == 1:
            audio = audio[np.newaxis, :]
        return audio, sr, is_stereo
    
    def load_eq_settings(self, eq_file):
        with open(eq_file, 'r', encoding='utf-8') as f:
            eq_settings = json.load(f)
        if 'bands' not in eq_settings:
            raise ValueError("均衡器设置文件格式错误：缺少 'bands' 字段")
        return eq_settings
    
    def apply_eq_to_channel_advanced(self, audio_channel, eq_settings, sr):
        if self.overlap_add_method:
            return self._apply_eq_overlap_add(audio_channel, eq_settings, sr)
        else:
            return self._apply_eq_direct(audio_channel, eq_settings, sr)
    
    def _apply_eq_overlap_add(self, audio_channel, eq_settings, sr):
        freq_bins = np.fft.fftfreq(self.n_fft, 1/sr)[:self.n_fft//2 + 1]
        eq_response = self._create_eq_response(eq_settings, freq_bins)
        f, t, Zxx = signal.stft(audio_channel, fs=sr, window=self.window, nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        magnitude = np.abs(Zxx)
        phase = np.exp(1j * np.angle(Zxx))
        magnitude_eq = magnitude * eq_response[:, np.newaxis]
        Zxx_eq = magnitude_eq * phase
        t, audio_eq = signal.istft(Zxx_eq, fs=sr, window=self.window, nperseg=self.n_fft, noverlap=self.n_fft - self.hop_length)
        if len(audio_eq) > len(audio_channel):
            audio_eq = audio_eq[:len(audio_channel)]
        elif len(audio_eq) < len(audio_channel):
            audio_eq = np.pad(audio_eq, (0, len(audio_channel) - len(audio_eq)), 'constant')
        return audio_eq
    
    def _apply_eq_direct(self, audio_channel, eq_settings, sr):
        D = librosa.stft(audio_channel, n_fft=self.n_fft, hop_length=self.hop_length, window=self.window)
        magnitude, phase = librosa.magphase(D)
        freq_bins = np.fft.fftfreq(self.n_fft, 1/sr)[:self.n_fft//2 + 1]
        eq_response = self._create_eq_response(eq_settings, freq_bins)
        magnitude_eq = magnitude * eq_response[:, np.newaxis]
        D_eq = magnitude_eq * phase
        audio_eq = librosa.istft(D_eq, hop_length=self.hop_length, window=self.window)
        if len(audio_eq) > len(audio_channel):
            audio_eq = audio_eq[:len(audio_channel)]
        elif len(audio_eq) < len(audio_channel):
            audio_eq = np.pad(audio_eq, (0, len(audio_channel) - len(audio_eq)), 'constant')
        return audio_eq
    
    def _create_eq_response(self, eq_settings, freq_bins):
        eq_response = np.ones(len(freq_bins))
        bands = list(eq_settings['bands'].values())
        for band in bands:
            lower_freq = band['lower_freq']
            upper_freq = band['upper_freq']
            gain_db = band['gain_db']
            gain_linear = 10 ** (gain_db / 20)
            lower_bin_idx = np.searchsorted(freq_bins, lower_freq, side='left')
            upper_bin_idx = np.searchsorted(freq_bins, upper_freq, side='right')
            lower_bin_idx = max(0, lower_bin_idx)
            upper_bin_idx = min(len(freq_bins) - 1, upper_bin_idx)
            if lower_bin_idx < upper_bin_idx:
                if 'q_factor' in band and band['q_factor'] > 0:
                    center_freq = band.get('center_freq', np.sqrt(lower_freq * upper_freq))
                    q = band['q_factor']
                    for i in range(lower_bin_idx, upper_bin_idx + 1):
                        freq = freq_bins[i]
                        if freq > 0 and center_freq > 1e-6:
                            omega_ratio = freq / center_freq
                            if omega_ratio == 0:
                                response_factor = 0
                            else:
                                response_factor = 1 / np.sqrt(1 + (q * (omega_ratio - 1/omega_ratio))**2)
                            eq_response[i] *= (1 + (gain_linear - 1) * response_factor)
                        elif freq > 0:
                            eq_response[i] *= gain_linear
                else:
                    eq_response[lower_bin_idx:upper_bin_idx + 1] *= gain_linear
        eq_response = gaussian_filter1d(eq_response, sigma=1.0)
        return eq_response
    
    def save_audio(self, audio, output_file, sr, bit_depth=24):
        if len(audio.shape) == 1:
            audio_to_save = audio
        else:
            audio_to_save = audio.T
        max_val = np.max(np.abs(audio_to_save))
        if max_val > 0.95:
            audio_to_save = audio_to_save * (0.95 / max_val)
        if bit_depth == 16:
            subtype = 'PCM_16'
        elif bit_depth == 24:
            subtype = 'PCM_24'
        else:
            subtype = 'PCM_32'
        sf.write(output_file, audio_to_save, sr, subtype=subtype)
    
    def apply_eq_to_audio(self, eq_file, input_audio_path, output_audio_path, 
                         bit_depth=24, master_gain_db=0.0):
        eq_settings = self.load_eq_settings(eq_file)
        audio, sr, is_stereo = self.load_audio(input_audio_path)
        if is_stereo:
            left_channel = audio[0, :]
            right_channel = audio[1, :]
            left_processed = self.apply_eq_to_channel_advanced(left_channel, eq_settings, sr)
            right_processed = self.apply_eq_to_channel_advanced(right_channel, eq_settings, sr)
            processed_audio = np.stack([left_processed, right_processed], axis=0)
        else:
            mono_channel = audio[0, :] if len(audio.shape) > 1 else audio
            processed_audio = self.apply_eq_to_channel_advanced(mono_channel, eq_settings, sr)

        # 应用主增益
        master_gain_linear = 10 ** (master_gain_db / 20)
        processed_audio *= master_gain_linear

        self.save_audio(processed_audio, output_audio_path, sr, bit_depth)
        return processed_audio
    
    def batch_process(self, eq_file, input_folder, output_folder, 
                     file_extension='wav', bit_depth=24, log_callback=None):
        import os
        import glob
        os.makedirs(output_folder, exist_ok=True)
        pattern = os.path.join(input_folder, f"*.{file_extension}")
        audio_files = glob.glob(pattern)
        if not audio_files:
            if log_callback: log_callback(f"未找到任何 .{file_extension} 文件")
            return
        if log_callback: log_callback(f"找到 {len(audio_files)} 个音频文件")
        success_count = 0
        for i, input_file in enumerate(audio_files, 1):
            filename = os.path.basename(input_file)
            name, ext = os.path.splitext(filename)
            output_file = os.path.join(output_folder, f"eq_{name}{ext}")
            if log_callback: log_callback(f"[{i}/{len(audio_files)}] 处理文件: {filename}")
            try:
                self.apply_eq_to_audio(eq_file, input_file, output_file, bit_depth)
                success_count += 1
                if log_callback: log_callback(f"✓ 完成: {filename}")
            except Exception as e:
                if log_callback: log_callback(f"✗ 失败: {filename} - {e}")
        if log_callback: log_callback(f"批量处理完成！共处理 {len(audio_files)} 个文件，成功 {success_count} 个")

class AudioEQSystem:
    def __init__(self, config=None):
        default_config = {
            'num_bands': 31, 'min_freq': 20, 'max_freq': 20000,
            'n_fft': 8192, 'hop_length': 256, 'smoothing_sigma': 1.5,
            'overlap_add_method': True, 'bit_depth': 24
        }
        if config:
            default_config.update(config)
        self.config = default_config
        self.analyzer = AudioEQAnalyzer(
            num_bands=self.config['num_bands'], min_freq=self.config['min_freq'],
            max_freq=self.config['max_freq'], n_fft=self.config['n_fft'],
            hop_length=self.config['hop_length'], smoothing_sigma=self.config['smoothing_sigma']
        )
        self.applicator = AudioEQApplicator(
            n_fft=self.config['n_fft'], hop_length=self.config['hop_length'],
            overlap_add_method=self.config['overlap_add_method']
        )
    
    def analyze_and_extract_eq(self, original_audio, processed_audio, 
                              output_json, ax1=None, ax2=None, log_callback=None):
        if log_callback: log_callback("开始均衡器设置提取...")
        if not os.path.exists(original_audio):
            raise FileNotFoundError(f"原始音频文件不存在: {original_audio}")
        if not os.path.exists(processed_audio):
            raise FileNotFoundError(f"处理后音频文件不存在: {processed_audio}")
        eq_settings = self.analyzer.analyze_audio_pair(
            original_audio, processed_audio, output_json, ax1, ax2
        )
        if log_callback: log_callback(f"均衡器设置已提取并保存到: {output_json}")
        return eq_settings
    
    def apply_eq_to_audio(self, eq_json, input_audio, output_audio, master_gain_db=0.0, log_callback=None):
        if log_callback: log_callback("开始应用均衡器设置...")
        if not os.path.exists(eq_json):
            raise FileNotFoundError(f"均衡器设置文件不存在: {eq_json}")
        if not os.path.exists(input_audio):
            raise FileNotFoundError(f"输入音频文件不存在: {input_audio}")
        processed_audio = self.applicator.apply_eq_to_audio(
            eq_json, input_audio, output_audio, bit_depth=self.config['bit_depth'],
            master_gain_db=master_gain_db
        )
        if log_callback: log_callback(f"处理后的音频已保存到: {output_audio}")
        return processed_audio
    
    def full_workflow(self, original_audio, processed_audio, target_audio, 
                     output_audio, temp_dir="temp", ax1=None, ax2=None, log_callback=None, master_gain_db=0.0):
        if log_callback: log_callback("开始完整的音频均衡器工作流程")
        os.makedirs(temp_dir, exist_ok=True)
        eq_json = os.path.join(temp_dir, "extracted_eq_settings.json")
        try:
            if log_callback: log_callback("步骤1: 分析音频对并提取均衡器设置")
            eq_settings = self.analyze_and_extract_eq(
                original_audio, processed_audio, eq_json, ax1, ax2, log_callback
            )
            if log_callback: log_callback("步骤2: 将均衡器设置应用到目标音频")
            processed_audio_data = self.apply_eq_to_audio(
                eq_json, target_audio, output_audio, master_gain_db=master_gain_db, log_callback=log_callback
            )
            if log_callback: log_callback("完整工作流程执行成功！")
            if log_callback: log_callback(f"EQ设置: {eq_json}")
            if log_callback: log_callback(f"输出音频: {output_audio}")
            return {'eq_settings': eq_settings, 'eq_json_path': eq_json, 'output_audio_path': output_audio}
        except Exception as e:
            if log_callback: log_callback(f"工作流程执行失败: {e}")
            raise
    
    def batch_apply_eq(self, eq_json, input_folder, output_folder, 
                      file_extensions=['wav', 'flac', 'mp3'], log_callback=None):
        if log_callback: log_callback("开始批量应用均衡器设置")
        if not os.path.exists(eq_json):
            raise FileNotFoundError(f"均衡器设置文件不存在: {eq_json}")
        os.makedirs(output_folder, exist_ok=True)
        audio_files = []
        import glob
        for ext in file_extensions:
            pattern = os.path.join(input_folder, f"*.{ext}")
            audio_files.extend(glob.glob(pattern))
        if not audio_files:
            if log_callback: log_callback(f"在 {input_folder} 中未找到任何音频文件")
            return
        if log_callback: log_callback(f"找到 {len(audio_files)} 个音频文件")
        self.applicator.batch_process(eq_json, input_folder, output_folder, 
                                      file_extension='wav', bit_depth=self.config['bit_depth'],
                                      log_callback=log_callback)
        if log_callback: log_callback("批量处理完成！")
    
    def create_preset_eq(self, preset_name, output_json, log_callback=None):
        if log_callback: log_callback(f"创建预设均衡器: {preset_name}")
        presets = {
            'rock': {'description': '摇滚音乐增强 - 突出低频和高频', 'gains': [3, 2, 1, 0, -1, -1, 0, 2, 4, 3]},
            'pop': {'description': '流行音乐增强 - 平衡的频率响应', 'gains': [1, 0, -1, 0, 1, 2, 1, 0, 1, 2]},
            'classical': {'description': '古典音乐增强 - 自然的频率响应', 'gains': [0, 0, 0, 0, 0, 1, 1, 1, 0, 0]},
            'vocal': {'description': '人声增强 - 突出中频', 'gains': [-1, -1, 0, 2, 3, 3, 2, 0, -1, -1]},
            'bass_boost': {'description': '低频增强 - 强化低音', 'gains': [6, 4, 2, 0, -1, -1, 0, 0, 0, 0]}
        }
        if preset_name not in presets:
            available = ', '.join(presets.keys())
            raise ValueError(f"未知预设: {preset_name}. 可用预设: {available}")
        preset = presets[preset_name]
        eq_settings = {
            "metadata": {
                "num_bands": len(preset['gains']), "min_freq": 20, "max_freq": 20000,
                "analysis_method": f"preset_{preset_name}", "frequency_distribution": "logarithmic",
                "description": preset['description']
            },
            "bands": {}
        }
        num_bands = len(preset['gains'])
        log_freqs = np.logspace(np.log10(20), np.log10(20000), num_bands + 1)
        for i, gain in enumerate(preset['gains']):
            center_freq = np.sqrt(log_freqs[i] * log_freqs[i + 1])
            eq_settings["bands"][f"band_{i+1:02d}"] = {
                "center_freq": float(center_freq), "lower_freq": float(log_freqs[i]),
                "upper_freq": float(log_freqs[i + 1]), "gain_db": float(gain), "q_factor": 1.0
            }
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(eq_settings, f, indent=4, ensure_ascii=False)
        if log_callback: log_callback(f"预设均衡器已保存到: {output_json}")
        if log_callback: log_callback(f"描述: {preset['description']}")
        return eq_settings

class AudioEQApp:
    def __init__(self, master):
        self.master = master
        master.title("高精度音频均衡器生成系统 v0.1")
        master.geometry("1000x800")

        self.eq_system = AudioEQSystem()

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_analyze_tab()
        self.create_apply_tab()
        self.create_workflow_tab()
        self.create_batch_tab()
        self.create_preset_tab()
        self.create_settings_frame()
        self.create_log_frame()

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def select_file(self, entry_widget, file_type="audio"):
        file_path = ""
        if file_type == "audio":
            file_path = filedialog.askopenfilename(filetypes=[("音频文件", "*.wav *.flac *.mp3"), ("所有文件", "*.*")])
        elif file_type == "json":
            file_path = filedialog.askopenfilename(filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        elif file_type == "save_audio":
            file_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV文件", "*.wav"), ("FLAC文件", "*.flac"), ("MP3文件", "*.mp3")])
        elif file_type == "save_json":
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON文件", "*.json")])
        
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
            # 如果是EQ JSON文件选择，则立即触发可视化更新
            if entry_widget == self.apply_eq_json_entry:
                self.load_and_plot_eq_json()

    def select_folder(self, entry_widget):
        folder_path = filedialog.askdirectory()
        if folder_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_path)

    def create_settings_frame(self):
        settings_frame = ttk.LabelFrame(self.master, text="全局设置")
        settings_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(settings_frame, text="频段数量:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.num_bands_var = tk.IntVar(value=self.eq_system.config['num_bands'])
        ttk.Spinbox(settings_frame, from_=5, to_=61, increment=2, textvariable=self.num_bands_var, width=5).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        tk.Label(settings_frame, text="位深度:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.bit_depth_var = tk.IntVar(value=self.eq_system.config['bit_depth'])
        ttk.Spinbox(settings_frame, values=[16, 24, 32], textvariable=self.bit_depth_var, width=5).grid(row=0, column=3, padx=5, pady=2, sticky="w")
        
        ttk.Button(settings_frame, text="应用设置", command=self.update_system_config).grid(row=0, column=4, padx=10, pady=2)

    def update_system_config(self):
        try:
            new_num_bands = self.num_bands_var.get()
            new_bit_depth = self.bit_depth_var.get()
            self.eq_system.config['num_bands'] = new_num_bands
            self.eq_system.config['bit_depth'] = new_bit_depth
            
            # 重新初始化分析器和应用器以应用新配置
            self.eq_system = AudioEQSystem(self.eq_system.config)
            self.log_message(f"系统配置已更新: 频段={new_num_bands}, 位深度={new_bit_depth}")
        except Exception as e:
            self.log_message(f"更新设置失败: {e}")

    def create_log_frame(self):
        log_frame = ttk.LabelFrame(self.master, text="日志输出")
        log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_text = tk.Text(log_frame, height=10, wrap="word", bg="#f0f0f0")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)

    def create_analyze_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="分析")

        input_frame = ttk.LabelFrame(tab, text="输入文件")
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="原始音频:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.analyze_original_audio_entry = ttk.Entry(input_frame, width=50)
        self.analyze_original_audio_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.analyze_original_audio_entry, "audio")).grid(row=0, column=2, padx=5, pady=2)

        tk.Label(input_frame, text="处理后音频:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.analyze_processed_audio_entry = ttk.Entry(input_frame, width=50)
        self.analyze_processed_audio_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.analyze_processed_audio_entry, "audio")).grid(row=1, column=2, padx=5, pady=2)

        output_frame = ttk.LabelFrame(tab, text="输出设置")
        output_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="输出EQ JSON:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.analyze_output_json_entry = ttk.Entry(output_frame, width=50)
        self.analyze_output_json_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="保存为", command=lambda: self.select_file(self.analyze_output_json_entry, "save_json")).grid(row=0, column=2, padx=5, pady=2)

        analyze_button = ttk.Button(tab, text="开始分析", command=self.run_analyze)
        analyze_button.pack(pady=10)

        # 绘图区域
        self.analyze_fig, (self.analyze_ax1, self.analyze_ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.analyze_canvas = FigureCanvasTkAgg(self.analyze_fig, master=tab)
        self.analyze_canvas_widget = self.analyze_canvas.get_tk_widget()
        self.analyze_canvas_widget.pack(fill="both", expand=True, padx=10, pady=5)
        self.analyze_toolbar = NavigationToolbar2Tk(self.analyze_canvas, tab)
        self.analyze_toolbar.update()
        self.analyze_canvas_widget.pack()

    def run_analyze(self):
        original_audio = self.analyze_original_audio_entry.get()
        processed_audio = self.analyze_processed_audio_entry.get()
        output_json = self.analyze_output_json_entry.get()

        if not original_audio or not processed_audio or not output_json:
            messagebox.showerror("错误", "请填写所有必填文件路径！")
            return

        try:
            self.log_message("开始分析...")
            self.eq_system.analyze_and_extract_eq(
                original_audio, processed_audio, output_json, 
                ax1=self.analyze_ax1, ax2=self.analyze_ax2, log_callback=self.log_message
            )
            self.analyze_canvas.draw()
            messagebox.showinfo("成功", "分析完成！")
        except Exception as e:
            self.log_message(f"分析失败: {e}")
            messagebox.showerror("错误", f"分析失败: {e}")

    def create_apply_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="应用")

        input_frame = ttk.LabelFrame(tab, text="输入文件")
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="EQ JSON文件:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.apply_eq_json_entry = ttk.Entry(input_frame, width=50)
        self.apply_eq_json_entry.grid(row=0, column=1, padx=5, pady=2)
        # 修改：直接在lambda中调用select_file，并在select_file中处理可视化更新
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.apply_eq_json_entry, "json")).grid(row=0, column=2, padx=5, pady=2)
        # 绑定EQ JSON文件选择事件，用于可视化 (保留，因为用户可能手动输入路径)
        self.apply_eq_json_entry.bind("<FocusOut>", self.load_and_plot_eq_json)
        self.apply_eq_json_entry.bind("<Return>", self.load_and_plot_eq_json)


        tk.Label(input_frame, text="输入音频:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.apply_input_audio_entry = ttk.Entry(input_frame, width=50)
        self.apply_input_audio_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.apply_input_audio_entry, "audio")).grid(row=1, column=2, padx=5, pady=2)

        output_frame = ttk.LabelFrame(tab, text="输出设置")
        output_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="输出音频:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.apply_output_audio_entry = ttk.Entry(output_frame, width=50)
        self.apply_output_audio_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="保存为", command=lambda: self.select_file(self.apply_output_audio_entry, "save_audio")).grid(row=0, column=2, padx=5, pady=2)

        # 新增主增益输入项
        tk.Label(output_frame, text="主增益 (dB):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.master_gain_var = tk.DoubleVar(value=0.0) # 默认0dB
        ttk.Spinbox(output_frame, from_=-20.0, to_=20.0, increment=0.5, textvariable=self.master_gain_var, width=8, format="%.1f").grid(row=1, column=1, padx=5, pady=2, sticky="w")

        apply_button = ttk.Button(tab, text="开始应用", command=self.run_apply)
        apply_button.pack(pady=10)

        # EQ可视化区域
        self.apply_fig, self.apply_ax = plt.subplots(figsize=(8, 4))
        self.apply_canvas = FigureCanvasTkAgg(self.apply_fig, master=tab)
        self.apply_canvas_widget = self.apply_canvas.get_tk_widget()
        self.apply_canvas_widget.pack(fill="both", expand=True, padx=10, pady=5)
        self.apply_toolbar = NavigationToolbar2Tk(self.apply_canvas, tab)
        self.apply_toolbar.update()
        self.apply_canvas_widget.pack()


    def load_and_plot_eq_json(self, event=None):
        eq_json_path = self.apply_eq_json_entry.get()
        if not eq_json_path or not os.path.exists(eq_json_path):
            self.apply_ax.clear()
            self.apply_ax.set_title("EQ 曲线 (未加载或文件不存在)")
            self.apply_ax.set_xlabel("频率 (Hz)")
            self.apply_ax.set_ylabel("增益 (dB)")
            self.apply_ax.grid(True, alpha=0.3)
            self.apply_canvas.draw()
            return

        try:
            eq_settings = self.eq_system.applicator.load_eq_settings(eq_json_path)
            bands = eq_settings.get('bands', {})
            
            if not bands:
                self.log_message("EQ JSON文件中没有找到频段信息。")
                self.apply_ax.clear()
                self.apply_ax.set_title("EQ 曲线 (无频段信息)")
                self.apply_ax.set_xlabel("频率 (Hz)")
                self.apply_ax.set_ylabel("增益 (dB)")
                self.apply_ax.grid(True, alpha=0.3)
                self.apply_canvas.draw()
                return

            center_freqs = []
            gains_db = []
            for band_name, band_data in bands.items():
                center_freqs.append(band_data['center_freq'])
                gains_db.append(band_data['gain_db'])
            
            center_freqs = np.array(center_freqs)
            gains_db = np.array(gains_db)

            # 绘制EQ曲线
            self.apply_ax.clear()
            self.apply_ax.semilogx(center_freqs, gains_db, 'o-', linewidth=2, markersize=6, label='EQ 增益')
            self.apply_ax.set_xlabel('频率 (Hz)')
            self.apply_ax.set_ylabel('增益 (dB)')
            self.apply_ax.set_title('EQ 曲线可视化')
            self.apply_ax.grid(True, alpha=0.3)
            self.apply_ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
            self.apply_ax.set_xlim(20, 20000)
            self.apply_ax.legend()
            self.apply_canvas.draw()
            self.log_message(f"已加载并可视化EQ JSON文件: {eq_json_path}")

        except Exception as e:
            self.log_message(f"加载或可视化EQ JSON失败: {e}")
            self.apply_ax.clear()
            self.apply_ax.set_title("EQ 曲线 (加载失败)")
            self.apply_ax.set_xlabel("频率 (Hz)")
            self.apply_ax.set_ylabel("增益 (dB)")
            self.apply_ax.grid(True, alpha=0.3)
            self.apply_canvas.draw()


    def run_apply(self):
        eq_json = self.apply_eq_json_entry.get()
        input_audio = self.apply_input_audio_entry.get()
        output_audio = self.apply_output_audio_entry.get()
        master_gain_db = self.master_gain_var.get()

        if not eq_json or not input_audio or not output_audio:
            messagebox.showerror("错误", "请填写所有必填文件路径！")
            return

        try:
            self.log_message("开始应用均衡器...")
            self.eq_system.apply_eq_to_audio(
                eq_json, input_audio, output_audio, 
                master_gain_db=master_gain_db, # 传递主增益参数
                log_callback=self.log_message
            )
            messagebox.showinfo("成功", "应用完成！")
        except Exception as e:
            self.log_message(f"应用失败: {e}")
            messagebox.showerror("错误", f"应用失败: {e}")

    def create_workflow_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="工作流")

        input_frame = ttk.LabelFrame(tab, text="输入文件")
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="原始音频 (分析用):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.workflow_original_audio_entry = ttk.Entry(input_frame, width=50)
        self.workflow_original_audio_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.workflow_original_audio_entry, "audio")).grid(row=0, column=2, padx=5, pady=2)

        tk.Label(input_frame, text="处理后音频 (分析用):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.workflow_processed_audio_entry = ttk.Entry(input_frame, width=50)
        self.workflow_processed_audio_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.workflow_processed_audio_entry, "audio")).grid(row=1, column=2, padx=5, pady=2)

        tk.Label(input_frame, text="目标音频 (应用用):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.workflow_target_audio_entry = ttk.Entry(input_frame, width=50)
        self.workflow_target_audio_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.workflow_target_audio_entry, "audio")).grid(row=2, column=2, padx=5, pady=2)

        output_frame = ttk.LabelFrame(tab, text="输出设置")
        output_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="输出音频:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.workflow_output_audio_entry = ttk.Entry(output_frame, width=50)
        self.workflow_output_audio_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="保存为", command=lambda: self.select_file(self.workflow_output_audio_entry, "save_audio")).grid(row=0, column=2, padx=5, pady=2)

        tk.Label(output_frame, text="临时目录:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.workflow_temp_dir_entry = ttk.Entry(output_frame, width=50)
        self.workflow_temp_dir_entry.insert(0, "temp_workflow")
        self.workflow_temp_dir_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="选择", command=lambda: self.select_folder(self.workflow_temp_dir_entry)).grid(row=1, column=2, padx=5, pady=2)

        # 新增工作流中的主增益输入项
        tk.Label(output_frame, text="主增益 (dB):").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.workflow_master_gain_var = tk.DoubleVar(value=0.0) # 默认0dB
        ttk.Spinbox(output_frame, from_=-20.0, to_=20.0, increment=0.5, textvariable=self.workflow_master_gain_var, width=8, format="%.1f").grid(row=2, column=1, padx=5, pady=2, sticky="w")


        workflow_button = ttk.Button(tab, text="运行工作流", command=self.run_workflow)
        workflow_button.pack(pady=10)

        # 绘图区域 (复用分析页面的绘图逻辑)
        self.workflow_fig, (self.workflow_ax1, self.workflow_ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.workflow_canvas = FigureCanvasTkAgg(self.workflow_fig, master=tab)
        self.workflow_canvas_widget = self.workflow_canvas.get_tk_widget()
        self.workflow_canvas_widget.pack(fill="both", expand=True, padx=10, pady=5)
        self.workflow_toolbar = NavigationToolbar2Tk(self.workflow_canvas, tab)
        self.workflow_toolbar.update()
        self.workflow_canvas_widget.pack()

    def run_workflow(self):
        original_audio = self.workflow_original_audio_entry.get()
        processed_audio = self.workflow_processed_audio_entry.get()
        target_audio = self.workflow_target_audio_entry.get()
        output_audio = self.workflow_output_audio_entry.get()
        temp_dir = self.workflow_temp_dir_entry.get()
        master_gain_db = self.workflow_master_gain_var.get() # 获取主增益

        if not all([original_audio, processed_audio, target_audio, output_audio, temp_dir]):
            messagebox.showerror("错误", "请填写所有必填文件/文件夹路径！")
            return

        try:
            self.log_message("开始运行工作流...")
            self.eq_system.full_workflow(
                original_audio, processed_audio, target_audio, output_audio, temp_dir,
                ax1=self.workflow_ax1, ax2=self.workflow_ax2, log_callback=self.log_message,
                master_gain_db=master_gain_db # 传递主增益参数
            )
            self.workflow_canvas.draw()
            messagebox.showinfo("成功", "工作流完成！")
        except Exception as e:
            self.log_message(f"工作流失败: {e}")
            messagebox.showerror("错误", f"工作流失败: {e}")

    def create_batch_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="批量处理")

        input_frame = ttk.LabelFrame(tab, text="输入设置")
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="EQ JSON文件:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.batch_eq_json_entry = ttk.Entry(input_frame, width=50)
        self.batch_eq_json_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="浏览", command=lambda: self.select_file(self.batch_eq_json_entry, "json")).grid(row=0, column=2, padx=5, pady=2)

        tk.Label(input_frame, text="输入文件夹:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.batch_input_folder_entry = ttk.Entry(input_frame, width=50)
        self.batch_input_folder_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(input_frame, text="选择", command=lambda: self.select_folder(self.batch_input_folder_entry)).grid(row=1, column=2, padx=5, pady=2)

        output_frame = ttk.LabelFrame(tab, text="输出设置")
        output_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="输出文件夹:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.batch_output_folder_entry = ttk.Entry(output_frame, width=50)
        self.batch_output_folder_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="选择", command=lambda: self.select_folder(self.batch_output_folder_entry)).grid(row=0, column=2, padx=5, pady=2)

        batch_button = ttk.Button(tab, text="开始批量处理", command=self.run_batch)
        batch_button.pack(pady=10)

    def run_batch(self):
        eq_json = self.batch_eq_json_entry.get()
        input_folder = self.batch_input_folder_entry.get()
        output_folder = self.batch_output_folder_entry.get()

        if not eq_json or not input_folder or not output_folder:
            messagebox.showerror("错误", "请填写所有必填文件/文件夹路径！")
            return

        try:
            self.log_message("开始批量处理...")
            self.eq_system.batch_apply_eq(
                eq_json, input_folder, output_folder, log_callback=self.log_message
            )
            messagebox.showinfo("成功", "批量处理完成！")
        except Exception as e:
            self.log_message(f"批量处理失败: {e}")
            messagebox.showerror("错误", f"批量处理失败: {e}")

    def create_preset_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="预设")

        input_frame = ttk.LabelFrame(tab, text="预设选择")
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="选择预设:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.preset_name_var = tk.StringVar(value="rock")
        preset_options = ['rock', 'pop', 'classical', 'vocal', 'bass_boost']
        ttk.Combobox(input_frame, textvariable=self.preset_name_var, values=preset_options, state="readonly").grid(row=0, column=1, padx=5, pady=2, sticky="w")

        output_frame = ttk.LabelFrame(tab, text="输出设置")
        output_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(output_frame, text="输出JSON:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.preset_output_json_entry = ttk.Entry(output_frame, width=50)
        self.preset_output_json_entry.grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(output_frame, text="保存为", command=lambda: self.select_file(self.preset_output_json_entry, "save_json")).grid(row=0, column=2, padx=5, pady=2)

        preset_button = ttk.Button(tab, text="创建预设EQ", command=self.run_preset)
        preset_button.pack(pady=10)

    def run_preset(self):
        preset_name = self.preset_name_var.get()
        output_json = self.preset_output_json_entry.get()

        if not output_json:
            messagebox.showerror("错误", "请填写输出JSON文件路径！")
            return

        try:
            self.log_message(f"开始创建预设EQ: {preset_name}...")
            self.eq_system.create_preset_eq(
                preset_name, output_json, log_callback=self.log_message
            )
            messagebox.showinfo("成功", "预设EQ创建完成！")
        except Exception as e:
            self.log_message(f"创建预设EQ失败: {e}")
            messagebox.showerror("错误", f"创建预设EQ失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioEQApp(root)
    root.mainloop()
