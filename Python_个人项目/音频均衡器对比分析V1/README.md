# 音频均衡器对比分析

## 原理
通过对比原音乐以及经过均衡器或者二次处理翻录的音频，生成对应的配置文件。<br>
然后通过这个配置文件去处理其他音频，以达到类似的均衡器或者翻录效果。

## 测试
提取了某网友通过大奥耳机播放出来的音频然后录制下来的母带，对比了原音频的母带，最终生成了对应的`eq_settings.json`

## 如何使用
### 关于生成配置文件
首先你需要先找到WAV格式的原音频母带，以及处理或者翻录过的WAV格式母带（一定要保证二者的时长以及对应的时间轴相同！），然后分别命名为`audio_A.wav`和`audio_B.wav`。<br>
通过`测试用`文件夹里的`in.py`来生成。
```
python3 in.py
```

### 关于生成测试音频
在生成完`eq_settings.json`之后，通过`测试用`文件夹里的`out.py`来生成测试音频。
```
python3 out.py
```
最终生成`audio_C.wav`。你可以自己听或者对比频谱图来查看C音频是否和处理或翻录过的母带效果相似。

### 关于最终使用
```
python3 test.py eq_settings.json 音频.mp3
```
你可以自由使用各类音频，或者使用其他名称的配置文件。

## 声明
最终你能听到的效果依然取决于你的耳机或者外放等，本项目仅仅是娱乐性质！

# 进阶部分

## 使用方法
需要事先安装`separator`
```
pip install separator
```
然后下载对应的模型：https://github.com/deezer/spleeter/releases/tag/v1.4.0<br>
下载`2stems.tar.gz`<br>
解压放置在`pretrained_models/2stems`<br>
然后执行python文件处理音频：
```
python3 test2.py eq_settings.json 音频.mp3
```

## 原理
通过separator简单分析出人声，略微增强人声后，添加到输出的wav音频文件里，组成三声道音频。同时稍微优化下低频和高频部分。