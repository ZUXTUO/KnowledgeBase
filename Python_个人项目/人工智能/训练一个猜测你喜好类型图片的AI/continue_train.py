import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader, random_split
import os
from PIL import Image
import psutil
import time
import hashlib
from collections import defaultdict

def get_file_hash(filepath):
    """计算文件的MD5哈希值，用于识别重复文件"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def remove_duplicate_files(data_path):
    """
    根据优先级移除重复文件（包括同一文件夹内的重复和跨文件夹的重复）
    使用哈希值确保真正的文件内容比较，而不仅仅是文件名
    """
    # 定义文件夹优先级 - 优先级从高到低
    priority_order = ['verylike', 'hate', 'like']
    
    # 收集所有文件及其哈希
    file_dict = defaultdict(list)
    duplicates_removed = 0
    
    print("第一步：处理同一文件夹内的重复文件...")
    # 首先处理同一文件夹内的重复
    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if not os.path.isdir(class_path):
            continue
            
        # 记录当前文件夹内已看到的哈希
        seen_hashes = set()
        
        for filename in os.listdir(class_path):
            filepath = os.path.join(class_path, filename)
            if not os.path.isfile(filepath):
                continue
                
            try:
                # 计算文件哈希值
                file_hash = get_file_hash(filepath)
                
                # 检查是否在当前文件夹内重复
                if file_hash in seen_hashes:
                    os.remove(filepath)
                    duplicates_removed += 1
                    print(f"已移除同一文件夹内的重复文件: {filepath}")
                    continue
                
                # 记录已处理过的哈希值
                seen_hashes.add(file_hash)
                # 记录文件信息以便后续跨文件夹比较
                file_dict[file_hash].append((class_name, filepath))
                
            except Exception as e:
                print(f"处理文件时出错 {filepath}: {e}")
                continue
    
    print("\n第二步：处理跨文件夹的重复文件...")
    # 然后处理跨文件夹的重复
    for file_hash, files in file_dict.items():
        if len(files) > 1:
            # 按优先级排序文件
            files_sorted = sorted(files, 
                                key=lambda x: priority_order.index(x[0]) 
                                if x[0] in priority_order else len(priority_order))
            
            # 保留优先级最高的文件，删除其他
            keep_class, keep_file = files_sorted[0]
            for class_name, filepath in files_sorted[1:]:
                try:
                    os.remove(filepath)
                    duplicates_removed += 1
                    print(f"已移除跨文件夹重复文件: {filepath} (保留 {keep_file})")
                except Exception as e:
                    print(f"移除文件时出错 {filepath}: {e}")
    
    if duplicates_removed > 0:
        print(f"\n总共移除了 {duplicates_removed} 个重复文件。")
    else:
        print("\n未发现重复文件。")
    
    return duplicates_removed

# 配置参数
BATCH_SIZE = 16        # 批处理大小
IMG_SIZE = 224         # 图像尺寸
NUM_EPOCHS = 15        # 训练轮数
LEARNING_RATE = 1e-4   # 学习率
DATA_PATH = "data"     # 数据路径
MODEL_SAVE_PATH = "model/best_model.pth"  # 模型保存路径
NUM_CLASSES = 3        # 分类数量

# 确保模型保存目录存在
os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

# 首先处理重复文件
print("检查并移除重复文件...")
remove_duplicate_files(DATA_PATH)

# 设备设置 - 优先使用GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n使用设备: {device}")
if device.type == 'cuda':
    print(f"GPU名称: {torch.cuda.get_device_name(0)}")
    print(f"CUDA版本: {torch.version.cuda}")
    # 清理GPU缓存
    torch.cuda.empty_cache()

# 图像预处理 - 分别定义训练和验证的数据增强
print("\n配置数据增强和预处理...")
train_transform = transforms.Compose([
    transforms.Resize(256),              # 首先调整大小
    transforms.RandomCrop(IMG_SIZE),     # 随机裁剪
    transforms.RandomHorizontalFlip(),   # 随机水平翻转
    transforms.RandomRotation(10),       # 随机旋转±10度 (新增)
    transforms.ColorJitter(brightness=0.1, contrast=0.1), # 颜色抖动 (新增)
    transforms.ToTensor(),               # 转换为张量
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # 标准化
                       std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),     # 中心裁剪
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

# 数据集加载
try:
    print("\n加载数据集...")
    full_dataset = datasets.ImageFolder(root=DATA_PATH, transform=train_transform)
    print(f"数据集加载成功。总样本数: {len(full_dataset)}")
    print(f"类别名称: {full_dataset.classes}")
    
    # 为每个类别计算样本数量
    class_counts = {}
    for idx, (path, class_idx) in enumerate(full_dataset.samples):
        class_name = full_dataset.classes[class_idx]
        if class_name not in class_counts:
            class_counts[class_name] = 0
        class_counts[class_name] += 1
    
    print("各类别样本数量:")
    for class_name, count in class_counts.items():
        print(f"  - {class_name}: {count}张图片")
    
    # 划分训练集和验证集
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    # 确保验证集使用正确的变换
    val_dataset.dataset.transform = val_transform
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,        # 根据CPU核心数适当调整
        pin_memory=True       # 加速GPU训练
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        num_workers=2,
        pin_memory=True
    )
    
    print(f"训练批次数: {len(train_loader)}, 验证批次数: {len(val_loader)}")

except Exception as e:
    print(f"\n加载数据集时出错: {e}")
    exit()

# 模型初始化
try:
    print("\n初始化模型...")
    # 使用预训练的EfficientNet-B3模型
    model = models.efficientnet_b3(pretrained=True)
    # 获取分类器输入特征数
    num_ftrs = model.classifier[1].in_features
    # 修改分类器以匹配我们的类别数
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    # 移动模型到指定设备
    model = model.to(device)
    
    # 定义损失函数
    criterion = nn.CrossEntropyLoss()
    
    # 初始化训练变量
    start_epoch = 0
    best_acc = 0.0
    
    # 加载已有模型（如果存在）
    if os.path.exists(MODEL_SAVE_PATH):
        print(f"\n发现已有模型，加载中: {MODEL_SAVE_PATH}")
        try:
            # 修复：正确加载模型检查点
            checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
            
            # 加载模型状态
            model.load_state_dict(checkpoint['model_state_dict'])
            
            # 获取保存的最佳准确率和结束轮次
            best_acc = checkpoint.get('best_acc', 0.0)
            start_epoch = checkpoint.get('epoch', 0) + 1
            
            print(f"成功加载已有模型！最佳准确率: {best_acc:.4f}, 继续从轮次 {start_epoch} 开始训练")
        except Exception as e:
            print(f"加载模型时出错: {e}")
            print("将使用新初始化的模型继续训练")
            start_epoch = 0
            best_acc = 0.0
    else:
        print("\n未找到已有模型，将从头开始训练")
    
    print(f"\n模型总参数量: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")

except Exception as e:
    print(f"\n初始化模型时出错: {e}")
    exit()

# 训练准备
print("\n配置优化器和学习率调度器...")
# 创建优化器
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# 创建学习率调度器 - 当验证准确率停止提升时降低学习率
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', factor=0.5, patience=3, verbose=True
)

# 如果有已保存的模型，加载优化器和调度器状态
if os.path.exists(MODEL_SAVE_PATH) and start_epoch > 0:
    try:
        checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
        
        # 加载优化器状态
        if 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            print("已恢复优化器状态")
            
        # 加载调度器状态
        if 'scheduler_state_dict' in checkpoint:
            scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            print("已恢复学习率调度器状态")
    except Exception as e:
        print(f"加载优化器/调度器状态时出错: {e}")
        print("将使用新初始化的优化器/调度器")

# 训练监控函数
def print_system_stats():
    """打印系统资源使用情况"""
    if device.type == 'cuda':
        mem = torch.cuda.memory_allocated(device)/1e9
        print(f"GPU内存: {mem:.2f}GB | ", end='')
    cpu_percent = psutil.cpu_percent()
    mem_percent = psutil.virtual_memory().percent
    print(f"CPU使用率: {cpu_percent}% | 内存使用率: {mem_percent}%")

# 验证函数
def validate_model(model, val_loader, criterion, device):
    """对模型进行验证并返回损失和准确率"""
    model.eval()
    val_loss = 0.0
    correct = 0
    total = 0
    
    # 收集每个类别的准确率
    class_correct = list(0. for i in range(NUM_CLASSES))
    class_total = list(0. for i in range(NUM_CLASSES))
    
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * inputs.size(0)
            
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            # 计算每个类别的准确率
            c = (predicted == labels).squeeze()
            for i in range(labels.size(0)):
                label = labels[i]
                class_correct[label] += c[i].item()
                class_total[label] += 1
    
    # 计算总体验证损失和准确率
    val_loss = val_loss / len(val_loader.dataset)
    val_acc = correct / total
    
    # 计算每个类别的准确率
    class_acc = {}
    for i in range(NUM_CLASSES):
        if class_total[i] > 0:
            class_acc[i] = class_correct[i] / class_total[i]
        else:
            class_acc[i] = 0
    
    return val_loss, val_acc, class_acc

# 训练循环
print("\n开始训练...")
for epoch in range(start_epoch, start_epoch + NUM_EPOCHS):
    epoch_start_time = time.time()
    
    # 训练阶段
    model.train()
    running_loss = 0.0
    
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        batch_start = time.time()
        
        try:
            # 移动数据到设备
            inputs = inputs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            # 前向传播
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # 反向传播和优化
            loss.backward()
            optimizer.step()
            
            # 累计损失
            running_loss += loss.item() * inputs.size(0)
            
            # 打印批次进度
            if batch_idx % 10 == 0:
                batch_time = time.time() - batch_start
                print(f"轮次 {epoch+1}/{start_epoch + NUM_EPOCHS} | 批次 {batch_idx}/{len(train_loader)} "
                     f"| 损失: {loss.item():.4f} | 批处理时间: {batch_time:.2f}秒")
                print_system_stats()
                
        except Exception as e:
            print(f"\n处理批次 {batch_idx} 时出错: {e}")
            continue
    
    # 验证阶段
    val_loss, val_acc, class_acc = validate_model(model, val_loader, criterion, device)
    
    # 计算训练损失
    epoch_train_loss = running_loss / len(train_dataset)
    
    # 更新学习率
    current_lr = optimizer.param_groups[0]['lr']
    scheduler.step(val_acc)
    new_lr = optimizer.param_groups[0]['lr']
    
    # 计算轮次时间
    epoch_time = time.time() - epoch_start_time
    
    # 保存模型（如果是最佳模型）
    if val_acc > best_acc:
        print("\n当前模型超过历史最佳结果，正在保存模型...")
        best_acc = val_acc
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_acc': best_acc,
        }, MODEL_SAVE_PATH)
        print(f"模型已保存到: {MODEL_SAVE_PATH}")
    else:
        print("\n当前模型未超过历史最佳结果，不保存模型")

    # 打印轮次总结
    print(f"\n轮次 {epoch+1} 总结:")
    print(f"耗时: {epoch_time:.2f}秒 | 训练损失: {epoch_train_loss:.4f}")
    print(f"验证损失: {val_loss:.4f} | 验证准确率: {val_acc:.4f}")
    
    # 打印学习率变化
    if new_lr != current_lr:
        print(f"学习率从 {current_lr} 调整为 {new_lr}")
    
    # 打印每个类别的准确率
    print("各类别准确率:")
    for i, class_name in enumerate(full_dataset.classes):
        if i in class_acc:
            print(f"  - {class_name}: {class_acc[i]:.4f}")
    
    print(f"历史最佳准确率: {best_acc:.4f}")
    print("-"*50)

# 训练完成
print("\n训练完成!")
print(f"最佳验证准确率: {best_acc:.4f}")
print(f"最佳模型已保存至: {MODEL_SAVE_PATH}")

# 最终验证
print("\n对最佳模型进行最终验证...")
# 加载最佳模型
best_checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device)
model.load_state_dict(best_checkpoint['model_state_dict'])
# 执行验证
final_loss, final_acc, final_class_acc = validate_model(model, val_loader, criterion, device)
print(f"最终验证损失: {final_loss:.4f}")
print(f"最终验证准确率: {final_acc:.4f}")
print("最终各类别准确率:")
for i, class_name in enumerate(full_dataset.classes):
    if i in final_class_acc:
        print(f"  - {class_name}: {final_class_acc[i]:.4f}")