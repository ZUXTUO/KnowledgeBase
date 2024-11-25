# 将软盘img文件转CDROM的iso文件工具
在`Ubuntu 20.04`上测试成功。<br>
可以将原本需要软盘引导的img虚拟软盘文件转成可以通过CDROM引导的iso文件。<br>
将`floppy.img`放在`img2iso.sh`同目录下，然后执行`img2iso.sh`，在`dist`文件夹里就会生成对应的iso文件。<br>

# Floppy Disk IMG to CDROM ISO Conversion Tool  
Tested successfully on `Ubuntu 20.04`.<br>
This tool can convert an IMG file of a virtual floppy disk, which originally requires floppy disk booting, into an ISO file that can be booted from CDROM.<br>
Place the `floppy.img` in the same directory as `img2iso.sh`, then execute `img2iso.sh`. The corresponding ISO file will be generated in the `dist` folder.<br>

# フロッピーディスクIMGファイルをCDROMのISOファイルに変換するツール  
`Ubuntu 20.04`で正常に動作することを確認しました。  <br>
このツールは、もともとフロッピーディスクで起動する必要があるIMGファイルを、CDROMから起動できるISOファイルに変換できます。<br>
`floppy.img`を`img2iso.sh`と同じディレクトリに置き、`img2iso.sh`を実行すると、`dist`フォルダに対応するISOファイルが生成されます。<br>

```
sudo apt install genisoimage
```