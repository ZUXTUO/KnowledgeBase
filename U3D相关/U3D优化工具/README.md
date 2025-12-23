# U3D优化工具

一个包含Unity项目优化工具的集合，用于提升项目性能和开发效率。

## 工具列表

### 1. Enter Play Mode Settings 自动启用工具

**文件**: `EnableEnterPlayModeOnLoad.cs`

**功能**:
- 自动启用Unity的"Enter Play Mode Settings"选项
- 避免每次打开项目时手动设置
- 可选地配置不重新加载Domain和场景

**使用方法**:
将脚本放置在Unity项目的`Assets`目录下的任何位置，工具将在Unity加载时自动运行。

### 2. 项目健康检查器

**文件**: `ProjectHealthChecker.cs`

**功能**:
- 全面检查Unity项目的优化问题
- 提供一键修复功能
- 涵盖多个方面的优化检查

**检查范围**:
- **编辑器设置**: ManagedStrippingLevel、AutoSyncTransforms等
- **纹理优化**: 尺寸、格式、压缩、mipmap等
- **音频优化**: Force To Mono、加载类型、流式传输等
- **FBX模型**: 读写标志、网格优化等
- **材质球**: GPU Instancing、双面GI等
- **预制件**: 粒子系统性能检查
- **着色器**: Pass数量检查
- **视频**: Android平台编码设置
- **脚本**: 空Update方法、OnGUI使用等

**使用方法**:
1. 将脚本放置在Unity项目的`Assets`目录下
2. 在Unity菜单栏中选择"工具/[优化]检查项目优化情况"
3. 在打开的窗口中可以设置优化参数
4. 点击"检查项目健康状况并应用优化"按钮开始检查
5. 查看检查结果并选择性修复问题

**优化参数**:
- 音频优化：可设置是否处理Force To Mono和加载类型
- 音乐长度阈值：超过此长度的音频将设为Streaming模式
- 纹理压缩率：控制纹理尺寸压缩比例

## 安装方法

将此文件夹中的C#脚本复制到Unity项目的`Assets`目录下即可。

## 适用版本

适用于Unity 2019.3及以上版本（支持Enter Play Mode功能）。