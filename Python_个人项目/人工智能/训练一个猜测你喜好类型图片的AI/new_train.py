import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader, random_split
import os
from PIL import Image
import psutil
import time
import shutil
from collections import defaultdict

# 配置参数
BATCH_SIZE = 16
IMG_SIZE = 224
NUM_EPOCHS = 20
LEARNING_RATE = 1e-4
DATA_PATH = "data"
MODEL_SAVE_PATH = "model/best_model.pth"
NUM_CLASSES = 3

# 优先级顺序
PRIORITY_ORDER = ['verylike', 'hate', 'like']

def remove_duplicate_files(data_path, priority_order):
    """
    根据优先级删除重复文件
    priority_order: 优先级从高到低的文件夹列表
    """
    # 收集所有文件
    file_dict = defaultdict(list)
    
    # 遍历所有类别文件夹
    for class_name in os.listdir(data_path):
        class_path = os.path.join(data_path, class_name)
        if os.path.isdir(class_path):
            for filename in os.listdir(class_path):
                file_dict[filename].append(class_name)
    
    # 处理重复文件
    duplicates_removed = 0
    for filename, classes in file_dict.items():
        if len(classes) > 1:
            # 按照优先级排序
            sorted_classes = sorted(classes, 
                                   key=lambda x: priority_order.index(x) 
                                   if x in priority_order else len(priority_order))
            
            # 保留最高优先级的，删除其他的
            keep_class = sorted_classes[0]
            for class_name in sorted_classes[1:]:
                file_path = os.path.join(data_path, class_name, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    duplicates_removed += 1
                    print(f"Removed duplicate file: {file_path} (kept in {keep_class})")
    
    if duplicates_removed > 0:
        print(f"\nTotal duplicates removed: {duplicates_removed}")
    else:
        print("\nNo duplicate files found.")

# 在加载数据前先处理重复文件
print("Checking for duplicate files...")
remove_duplicate_files(DATA_PATH, PRIORITY_ORDER)

# 设备设置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\nUsing device: {device}")
if device.type == 'cuda':
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")

# 简化图像预处理
train_transform = transforms.Compose([
    transforms.Resize(256),  # 先缩放到稍大尺寸
    transforms.RandomCrop(IMG_SIZE),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225])
])

# 数据集加载
try:
    full_dataset = datasets.ImageFolder(root=DATA_PATH, transform=train_transform)
    print(f"\nDataset loaded successfully. Total samples: {len(full_dataset)}")
    print(f"Class names: {full_dataset.classes}")
    
    # 划分数据集
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    val_dataset.dataset.transform = val_transform
    
    # 数据加载器（减少num_workers）
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,  # 减少worker数量
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        num_workers=2,
        pin_memory=True
    )
    
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")
    print(f"First batch check passed: {next(iter(train_loader))[0].shape}")  # 检查第一个batch

except Exception as e:
    print(f"\nError loading dataset: {e}")
    exit()

# 模型初始化
try:
    model = models.efficientnet_b3(pretrained=True)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    model = model.to(device)
    
    # 打印模型信息
    print("\nModel Summary:")
    print(f"Total params: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")
    
    # 测试前向传播
    test_input = torch.randn(2, 3, IMG_SIZE, IMG_SIZE).to(device)
    print(f"Test forward pass output shape: {model(test_input).shape}")
    
except Exception as e:
    print(f"\nError initializing model: {e}")
    exit()

# 训练准备
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', factor=0.5, patience=3
)

# 训练监控函数
def print_system_stats():
    if device.type == 'cuda':
        mem = torch.cuda.memory_allocated(device)/1e9
        print(f"GPU Mem: {mem:.2f}GB | ", end='')
    print(f"CPU Mem: {psutil.virtual_memory().percent}%")

# 训练循环
print("\nStarting training...")
best_acc = 0.0

for epoch in range(NUM_EPOCHS):
    start_time = time.time()
    model.train()
    running_loss = 0.0
    
    # 训练阶段
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        batch_start = time.time()
        
        try:
            inputs = inputs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
            # 打印batch进度
            if batch_idx % 10 == 0:
                batch_time = time.time() - batch_start
                print(f"Epoch {epoch+1}/{NUM_EPOCHS} | Batch {batch_idx}/{len(train_loader)} "
                      f"| Loss: {loss.item():.4f} | Time: {batch_time:.2f}s")
                print_system_stats()
                
        except Exception as e:
            print(f"\nError in batch {batch_idx}: {e}")
            continue
    
    # 验证阶段
    model.eval()
    val_loss, correct, total = 0.0, 0, 0
    
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
    
    # 计算指标
    epoch_time = time.time() - start_time
    epoch_acc = correct / total
    epoch_train_loss = running_loss / len(train_dataset)
    epoch_val_loss = val_loss / len(val_dataset)
    
    # 学习率调整
    scheduler.step(epoch_acc)
    
    # 保存最佳模型
    if epoch_acc > best_acc:
        print("\n当前模型状态可以保存\n")
        best_acc = epoch_acc
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'best_acc': best_acc,
        }, MODEL_SAVE_PATH)
    else:
        print("\n当前模型状态不可以保存！\n")
    
    # 打印epoch总结
    print(f"\nEpoch {epoch+1} Summary:")
    print(f"Time: {epoch_time:.2f}s | Train Loss: {epoch_train_loss:.4f}")
    print(f"Val Loss: {epoch_val_loss:.4f} | Acc: {epoch_acc:.4f}")
    print(f"Best Acc: {best_acc:.4f}")
    print("-"*50)

print("Training complete!")