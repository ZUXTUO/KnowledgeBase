# save as make_silence.py
import wave

def make_silence(path='silence.wav', duration_s=1.0, samplerate=44100, nchannels=1, sampwidth=2):
    nframes = int(samplerate * duration_s)
    # 对于 16-bit PCM，静音的帧就是每帧 sampwidth 个零字节
    silence_frame = b'\x00' * sampwidth
    frames = silence_frame * nframes * nchannels

    with wave.open(path, 'wb') as wf:
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(samplerate)
        wf.writeframes(frames)

if __name__ == '__main__':
    make_silence('silence.wav', duration_s=1.0)
    print('已生成 silence.wav（1 秒静音）')
