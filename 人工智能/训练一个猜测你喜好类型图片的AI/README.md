我自己有一个小图库，里面存了大概两万六千多张图片，我希望能根据它们训练一个AI，让这个AI能够判别我喜欢的图片类型。<br>
data   里面有三个文件夹，分别是hate\like\verylike，你可以存放你讨厌的、喜欢的、非常喜欢的图片<br>
new_train.py   新开始一个训练<br>
continue_train.py   继续之前的训练（需要先有一个训练出的模型）<br>
predict.py   测试模型，用法：python3 predict.py test.jpg<br>
www.py   开启一个网页来测试模型<br><br>
本项目最低支持python3.8<br>
使用前先安装好环境：pip install -r requirements.txt<br>