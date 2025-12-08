```
sudo apt update
sudo apt upgrade
sudo apt install ffmpeg
```

创建一个input文件夹，把需要处理的音频文件放到里面，支持子目录。

```
chmod +x set.sh
bash set.sh
```

如果出现了类似：

```
set.sh: line 2: $'\r': command not found
set.sh: line 5: $'\r': command not found
set.sh: line 12: $'\r': command not found
set.sh: line 48: syntax error near unexpected token `done'
'et.sh: line 48: `done < <(find "$WORK_DIR" -type f \( \
```

这种情况，说明你是从Windows系统复制的set.sh文件到Linux系统中的。

---

解决方法：
在Linux系统中，使用以下命令将set.sh文件的换行符转换为\n：

```
sed -i 's/\r$//' set.sh
```

---
# 注意！注意！注意！
此脚本处理是直接处理替换掉原音频，一定要注意备份！！！