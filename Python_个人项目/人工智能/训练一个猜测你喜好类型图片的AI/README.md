# 图片喜好度预测AI

一个基于深度学习的图片喜好度预测系统，能够根据用户提供的图片样本训练模型，预测用户对新图片的喜好程度。

## 功能特性

- **三分类模型**：将图片分为"讨厌"、"喜欢"、"非常喜欢"三个等级
- **深度学习模型**：使用EfficientNet-B3作为基础网络结构
- **重复文件处理**：自动检测并根据优先级处理重复图片
- **Web界面**：提供网页界面进行图片上传和预测
- **持续训练**：支持从已保存的模型继续训练

## 项目结构

```
├── data/                   # 训练数据目录
│   ├── hate/             # 讨厌的图片
│   ├── like/             # 喜欢的图片
│   └── verylike/         # 非常喜欢的图片
├── model/                 # 模型保存目录
├── templates/             # Web界面模板
├── new_train.py          # 新建训练
├── continue_train.py     # 继续训练
├── predict.py            # 单张图片预测
├── www.py                # Web服务
├── ToONNX_fp32.py        # 模型转换为ONNX格式
├── data_processing.py    # 数据处理
└── requirements.txt      # 依赖包
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt
```

### 2. 准备数据

在`data`目录下创建三个子目录，分别存放不同喜好的图片：

- `data/hate/` - 讨厌的图片
- `data/like/` - 喜欢的图片
- `data/verylike/` - 非常喜欢的图片

### 3. 开始训练

```bash
# 新建训练
python new_train.py

# 或继续训练
python continue_train.py
```

### 4. 模型预测

```bash
# 单张图片预测
python predict.py test.jpg

# 启动Web界面
python www.py
```

## 使用说明

- **优先级处理**：系统会自动处理重复文件，优先级顺序为 `verylike > hate > like`
- **模型保存**：训练过程中会自动保存最佳模型到 `model/best_model.pth`
- **Web界面**：启动后访问 `http://localhost:5000` 进行交互式预测

## 技术细节

- **模型架构**：EfficientNet-B3
- **预处理**：随机裁剪、水平翻转、标准化
- **优化器**：Adam，学习率 1e-4
- **损失函数**：交叉熵损失
- **数据增强**：随机裁剪、水平翻转等