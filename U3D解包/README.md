# Unity游戏解包指南

请注意，本文件的主要目的是为了学习研究所用，只有知道如何解包，才能明白如何通过加密或混淆之类手段来防止自己的游戏被解包。请勿将知识错用在非法渠道上。<br>

[此文件基于imadr提供的文件汉化编写](https://github.com/imadr/Unity-game-hacking) <br>

这是一个关于从使用Unity引擎制作的游戏中提取和修改资源或代码的简短指南。欢迎贡献内容。<br>

1. [Unity游戏文件夹结构](#unity游戏文件夹结构)
2. [提取和编辑代码](#提取和编辑代码)
3. [提取资源](#提取资源)
4. [内存黑客](#内存黑客)


## Unity游戏文件夹结构（Mono）

```
│  *.exe
└──*_Data
   │  globalgamemanagers
   │  globalgamemanagers.assets
   │  level0
   │  level0.resS
      ...
   |  levelN
   |  levelN.resS
   |  resources.assets
   |  resources.assets.resS
   |  resources.resource
   │  sharedassets0.assets
   │  sharedassets0.assets.resS
      ...
   |  sharedassetsN.assets
   |  sharedassetsN.assets.resS
   ├──Managed
   │    Assembly-CSharp.dll
   │    Assembly-UnityScript.dll
   │    Mono.Security.dll
   │    mscorlib.dll
   │    System.Core.dll
   │    System.dll
   │    UnityEngine.dll
   │    UnityEngine.dll.mdb
   │    UnityEngine.Networking.dll
   │    UnityEngine.UI.dll
   ├──Mono
   │  │  mono.dll
   │  └──etc
   │     └──mono
   │        │  browscap.ini
   │        │  config
   │        ├──1.0
   │        │     DefaultWsdlHelpGenerator.aspx
   │        │     machine.config
   │        ├──2.0
   │        │  │  DefaultWsdlHelpGenerator.aspx
   │        │  │  machine.config
   │        │  │  settings.map
   │        │  │  web.config
   │        │  └──Browsers
   │        │        Compat.browser
   │        └──mconfig
   │              config.xml
   └──Resources
        unity default resources
        unity_builtin_extra
```
只有类似以上这种目录的游戏才有较好的反编译的可能性。
如果dll文件有加密，安卓游戏可以通过`GG修改器`在游戏运行时把游戏的内存全部提取出来，然后把`get_dll_from_bin.exe`跟所有的内存文件放在一起，点击执行，如果没有兼容性等问题，在运行完成后目录里会出现例如0.dll、1.dll、2.dll……
通过`dnSpy`等工具可以了解dll的具体名称。此工具下方会介绍。

文件/目录 | 描述
--- | ---
*.exe | 游戏的可执行文件
`*_Data` | 包含游戏资源的数据文件夹
level0-levelN | 存储游戏场景数据的文件，每个场景有一个文件
sharedassets0-sharedassetsN | 游戏资源被分割成sharedassets和.resS文件（例如在Android/iOS平台上可能是sharedassets.assets.split0 - ..splitN）
resources.assets | 项目资源文件夹中的原始资产和它们的依赖项都存储在这个文件中（包括音频文件，即使它们不在Resources文件夹内，音频剪辑和指向.resource的引用，以及音频的大小/偏移信息都会存储在.assets中）
`Managed` | 包含Unity DLL的文件夹
Assembly-CSharp.dll | 包含已编译C#文件的DLL
Assembly-UnityScript.dll | 包含已编译UnityScript文件的DLL

**`*`** : 主可执行文件的名称（.exe）。

注意！IL2CPP打包的Unity游戏目前还没有特别好的反编译方法。
WebGL里：UnityWebData1.0或许有办法能解开代码，旧版本打包的UnityFS几乎无法反编译，因为代码被转成JS了。

## 提取和编辑代码

C#和UnityScript文件会被编译成Assembly-CSharp.dll（和Assembly-UnityScript.dll）DLL文件，分别可以在`Managed`文件夹中找到。

这些DLL文件可以使用ILSpy、dnSpy、DotPeek或JustAssembly等工具进行反编译，允许修改并重新编译程序集文件。

如果`Managed`目录中缺少DLL文件，可以尝试使用**MegaDumper**工具进行转储。

工具 | 描述
--- | ---
[ILSpy](https://github.com/icsharpcode/ILSpy) | 跨平台的.NET反编译器，支持PDB生成、ReadyToRun、元数据等功能。
[DotPeek](https://www.jetbrains.com/decompiler/) | JetBrains DotPeek是一个免费的.NET反编译器和程序集浏览器。
[dnSpyEx](https://github.com/dnSpyEx/dnSpy) | 已废弃的知名.NET调试器和程序集编辑器dnSpy的非官方复刻版。
[Telerik JustAssembly](https://www.telerik.com/justassembly) | 反编译并比较.NET程序集。支持二进制代码差异和方法差异比较。
[Cpp2IL](https://github.com/SamboyCoding/Cpp2IL) | 一个正在开发的工具，用于逆向Unity的IL2CPP工具链。
[Il2CppDumper](https://github.com/Perfare/Il2CppDumper) | Unity IL2CPP逆向工程工具。
[dnSpy](https://github.com/dnSpy/dnSpy) <br/> ![不再维护](https://img.shields.io/badge/No%20Longer%20Maintained-red.svg) | dnSpy是一个调试器和.NET程序集编辑器。即使没有源代码，也可以编辑和调试程序集文件。<br/> **已不再维护，建议使用``dnSpyEx``。**
[MegaDumper](https://github.com/CodeCracker-Tools/MegaDumper)  <br/> ![不再维护](https://img.shields.io/badge/No%20Longer%20Maintained-red.svg) | 用于转储本地和.NET程序集。

Il2CppDumper更多的是为了通过元文件找到代码所在的地址，再通过IDA等工具解析修改。
IL2CPP游戏的修改可以参考[这里](https://www.52pojie.cn/thread-618515-1-1.html)

## 提取资源

资源存储在.assets和.resS文件中。这些文件的内容可以使用以下工具提取：

工具 | 描述
--- | ---
[AssetRipper](https://github.com/AssetRipper/AssetRipper) | AssetRipper是一个从序列化文件（CAB-*, *.assets, *.sharedAssets等）和资源包（*.unity3d, *.bundle等）中提取资源并将它们转换为原生Unity引擎格式的工具。<br/> **uTinyRipper的复刻版**。
[Unity Assets Bundle Extractor](https://github.com/SeriousCache/UABE) | UABE是一个针对Unity 3.4+/4/5/2017-2021.3版本的.assets和AssetBundle文件编辑器，可以创建独立的mod安装包。
[QuickBMS](https://aluigi.altervista.org/quickbms.htm) 配合[此脚本](https://aluigi.altervista.org/bms/unity.bms)或[WebPlayer脚本](https://aluigi.altervista.org/bms/unity3d_webplayer.bms) | 一款通用的基于脚本的文件提取器和重新导入工具。QuickBMS支持众多游戏和文件格式、压缩、加密、混淆等算法。
[DevXUnityUnpacker](https://devxdevelopment.com/Unpacker) | 一款付费工具，具有友好的图形界面，旨在通过输入构建的游戏/应用程序恢复Unity项目，还带有预览功能（例如图像、十六进制、文本等）。
[uTinyRipper](https://github.com/mafaca/UtinyRipper) <br/> ![不再维护](https://img.shields.io/badge/No%20Longer%20Maintained-red.svg) | uTinyRipper是一个用于从序列化文件（CAB-*, *.assets, *.sharedAssets等）和资源包（*.unity3d, *.assetbundle等）中提取资源并将它们转换为原生引擎格式的工具。<br/> **建议使用``AssetRipper``。**
[Unity Studio / AssetStudio](https://github.com/RaduMC/AssetStudio) <br/> ![不再维护](https://img.shields.io/badge/No%20Longer%20Maintained-red.svg) | AssetStudio是一个独立的工具，用于浏览、提取和导出资产。
[Unity Assets Explorer](https://zenhax.com/viewtopic.php?t=36) <br/> ![不再维护](https://img.shields.io/badge/No%20Longer%20Maintained-red.svg) | Unity Assets Explorer用于查看Assets文件的内容（Unity 3D引擎）。支持提取所有文件、提取单个文件（通过右键菜单）、将tex文件转换为DDS格式（提取时）、将修改过的DDS图像导入到资源包中。

> **不要使用UnityEX**，它很可能是病毒。

目前优先推荐使用AssetRipper，可以将unity游戏反编译成unity项目。

### DDS文件：

[DDS](https://en.wikipedia.org/wiki/DirectDraw_Surface)文件可以使用以下工具打开/转换/编辑：

工具 | 教程
--- | ---
[Ninja Ripper](https://ninjaripper.com/) | 从游戏中提取（捕捉）3D场景并在3D编辑器（Blender、3D Max、Noesis等）中查看。<br/> [旧的指南](http://cgig.ru/en/2012/10/ho-to-use-ninja-ripper/)帮助使用Ninja Ripper。<br/> 官方[YouTube频道](https://www.youtube.com/channel/UCgT-ET20KlC4AcECNtW9gyw)可以提供最新的视频教程。
[RenderDoc](https://renderdoc.org/) | [教程](https://www.youtube.com/watch?v=yPLxCm3SyPU)教你如何使用RenderDoc

。
[NVIDIA纹理工具导出器](https://developer.nvidia.com/nvidia-texture-tools-exporter) | NVIDIA纹理工具导出器允许用户直接从图像源创建高度压缩的纹理文件，这些文件在磁盘和内存中都非常小。<br/> **可以作为独立软件使用或作为Adobe Photoshop插件。**
[Intel®图形性能分析工具](https://www.intel.com/content/www/us/en/developer/tools/graphics-performance-analyzers/overview.html) | 通过快速识别性能问题，改善游戏性能。<br/> [教程](https://forum.xentax.com/viewtopic.php?t=12262)介绍如何使用Intel图形性能分析工具提取图形资源。
[Gimp插件](https://code.google.com/archive/p/gimp-dds/downloads) | 这是GIMP 2.8.x版本的插件，允许你加载和保存Direct Draw Surface (DDS) 格式的图像。
[3D Ripper DX](http://www.deep-shadows.com/hax/3DRipperDX.htm) | 此软件不支持64位二进制文件。

## 内存黑客

Cheat Engine有一个叫做[Dissect Mono](https://wiki.cheatengine.org/index.php?title=Mono)的功能，可以帮助黑客攻击游戏内存。这个[视频系列](https://www.youtube.com/playlist?list=PLNffuWEygffbue0tvx7IusDmfAthqmgS7)讲解了如何使用Cheat Engine，非常有帮助。