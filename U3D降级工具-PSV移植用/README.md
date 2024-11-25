# U3D设备锁（带QQ邮箱验证方法）
将两个cs文件放进Unity的资产文件夹中，修改`SendEmailSrc.cs`里的Mail_、Key_、Mail_Feedback部分。<br>
Mail_是发件邮箱。<br>
Key_需要自己通过QQ邮箱去申请开启POP3/SMTP服务，并且生成授权码。<br>
Mail_Feedback是收件邮箱<br><br>

在物体上挂上`Test.cs`并且启动就行，验证是否通过的逻辑可以在代码里添加修改。<br><br>

如果不需要通过发送邮箱获取验证，也可以自己改成别的方式。<br>