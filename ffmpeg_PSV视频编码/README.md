# PSV视频编码

## 带字幕
```
ffmpeg -i input.mkv -vf "scale=960:544,subtitles=input.ass" -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p -c:a aac -b:a 128k -ac 2 -y output.mp4
```

## 不带字幕
```
ffmpeg -i input.mkv -vf "scale=960:544" -c:v libx264 -profile:v baseline -level 3.0 -pix_fmt yuv420p -c:a aac -b:a 128k -ac 2 -y output.mp4
```