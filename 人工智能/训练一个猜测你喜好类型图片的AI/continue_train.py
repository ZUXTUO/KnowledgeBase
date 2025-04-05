import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models, datasets
from torch.utils.data import DataLoader, random_split
import os
from PIL import Image
import psutil
import time

# 配置参数
BATCH_SIZE = 16
IMG_SIZE = 224
NUM_EPOCHS = 15
LEARNING_RATE = 1e-4
DATA_PATH = "data"
MODEL_SAVE_PATH = "model/best_model.pth"
NUM_CLASSES = 3

# 设备设置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\nUsing device: {device}")
if device.type == 'cuda':
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"CUDA Version: {torch.version.cuda}")

# 图像预处理
train_transform = transforms.Compose([
    transforms.Resize(256),
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
    
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    val_dataset.dataset.transform = val_transform
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=2,
        pin_memory=True
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        num_workers=2,
        pin_memory=True
    )
    
    print(f"Train batches: {len(train_loader)}, Val batches: {len(val_loader)}")

except Exception as e:
    print(f"\nError loading dataset: {e}")
    exit()

# 模型初始化
try:
    model = models.efficientnet_b3(pretrained=True)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Linear(num_ftrs, NUM_CLASSES)
    model = model.to(device)
    
    # 定义损失函数（新增）
    criterion = nn.CrossEntropyLoss()
    
    # 加载已有模型
    start_epoch = 0
    best_acc = 0.0
    if os.path.exists(MODEL_SAVE_PATH):
        # 修复安全警告（新增weights_only=True）
        checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device, weights_only=True)
        model.load_state_dict(checkpoint['model_state_dict'])
        best_acc = checkpoint.get('best_acc', 0.0)
        print(f"\nLoaded existing model with best acc: {best_acc:.4f}")
    
    print(f"\nTotal params: {sum(p.numel() for p in model.parameters())/1e6:.2f}M")

except Exception as e:
    print(f"\nError initializing model: {e}")
    exit()

# 训练准备
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', factor=0.5, patience=3
)

# 加载优化器状态
if os.path.exists(MODEL_SAVE_PATH):
    checkpoint = torch.load(MODEL_SAVE_PATH, map_location=device, weights_only=True)
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    if 'scheduler_state_dict' in checkpoint:
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
    start_epoch = checkpoint.get('epoch', 0) + 1
    print(f"Resuming training from epoch {start_epoch}")

# 训练监控
def print_system_stats():
    if device.type == 'cuda':
        mem = torch.cuda.memory_allocated(device)/1e9
        print(f"GPU Mem: {mem:.2f}GB | ", end='')
    print(f"CPU Mem: {psutil.virtual_memory().percent}%")

# 训练循环
print("\nStarting training...")
for epoch in range(start_epoch, start_epoch + NUM_EPOCHS):
    start_time = time.time()
    model.train()
    running_loss = 0.0
    
    for batch_idx, (inputs, labels) in enumerate(train_loader):
        batch_start = time.time()
        
        try:
            inputs = inputs.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)  # 现在criterion已定义
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
            if batch_idx % 10 == 0:
                batch_time = time.time() - batch_start
                print(f"Epoch {epoch+1}/{start_epoch + NUM_EPOCHS} | Batch {batch_idx}/{len(train_loader)} "
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
    
    scheduler.step(epoch_acc)
    
    # 保存模型
    if epoch_acc > best_acc:
        print("\n当前模型状态可以保存\n")
        best_acc = epoch_acc
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'best_acc': best_acc,
        }, MODEL_SAVE_PATH)
    else:
        print("\n当前模型状态不可以保存！\n")

    print(f"\nEpoch {epoch+1} Summary:")
    print(f"Time: {epoch_time:.2f}s | Train Loss: {epoch_train_loss:.4f}")
    print(f"Val Loss: {epoch_val_loss:.4f} | Acc: {epoch_acc:.4f}")
    print(f"Best Acc: {best_acc:.4f}")
    print("-"*50)

print("Training complete!")