# 图像分类与标签系统

一个基于深度学习的图像多标签分类系统，使用PyTorch训练ResNet模型，并提供Web界面进行图像管理和标签预测。

## 功能特性

- **多标签分类**：使用ResNet50模型对图像进行多标签分类
- **SQLite数据库**：存储图像数据和标签信息
- **增量训练**：支持在已有模型基础上继续训练
- **异常检测**：自动检测可能错误的标签
- **Web界面**：提供图像浏览、评分和标签管理功能
- **批量处理**：支持批量上传和标签预测

## 技术架构

- **深度学习框架**：PyTorch
- **模型架构**：ResNet50（预训练模型）
- **数据库**：SQLite
- **Web框架**：Flask
- **标签处理**：MultiLabelBinarizer

## 主要文件

- `image_tag_trainer.py`：训练模型的主脚本
- `image_tag_trainer_add.py`：增量训练脚本
- `AI_to_Database.py`：将预测结果存入数据库
- `AI_to_Web.py`：Web界面，支持上传图像并预测标签
- `web.py`：数据库中图像的管理界面

## 使用方法

### 训练模型
```bash
python image_tag_trainer.py --db data.db --epochs 40 --batch_size 32 --lr 1e-4
```

### 增量训练
```bash
python image_tag_trainer_add.py --db data.db --epochs 40 --load_model checkpoints/best_model_epoch5.pth
```

### 预测并保存到数据库
```bash
python AI_to_Database.py --db data.db --model checkpoints/best_model_epoch3.pth --threshold 0.98
```

### 启动Web界面
```bash
python AI_to_Web.py --model checkpoints/best_model_epoch3.pth --db data.db
```