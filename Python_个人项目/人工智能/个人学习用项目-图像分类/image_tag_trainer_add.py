import os
import sqlite3
import io
import csv
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
import time
import matplotlib.pyplot as plt
from collections import Counter
import pickle # 用于序列化MultiLabelBinarizer

# ImageTagDataset 类：从 SQLite 数据库加载图像和多标签
class ImageTagDataset(Dataset):
    """数据集类，用于从 SQLite 数据库加载图像及其多标签。"""
    def __init__(self, db_path, transform=None, mlb=None):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.transform = transform
        
        # 检查数据库schema
        self.cursor.execute("PRAGMA table_info(images)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        has_data = 'data' in columns
        has_filename = 'filename' in columns
        
        # 查询带有标签的图像
        query = f'''
            SELECT i.id,
                  {'i.data,' if has_data else ''} 
                  {'i.filename,' if has_filename else ''} 
                  GROUP_CONCAT(t.name) AS tags
            FROM images i
            JOIN image_tags it ON i.id = it.image_id
            JOIN tags t ON t.id = it.tag_id
            GROUP BY i.id
        '''
        
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        
        self.samples = []
        all_tags = set()
        
        for record in records:
            img_id = record[0]
            offset = 1
            
            img_data = record[offset] if has_data else None
            offset += 1 if has_data else 0
            
            img_filename = record[offset] if has_filename else None
            offset += 1 if has_filename else 0
            
            tag_str = record[offset]
            tag_list = tag_str.split(',') if tag_str else []
            
            self.samples.append((img_id, img_data, img_filename, tag_list))
            all_tags.update(tag_list)
        
        # 多标签二值化器 (MultiLabelBinarizer) 初始化
        if mlb:
            self.mlb = mlb
            # 更新 MLB 以包含新标签，同时保留旧标签
            new_tags = list(all_tags - set(self.mlb.classes_))
            if new_tags:
                print(f"检测到新标签: {new_tags}，更新 MultiLabelBinarizer。")
                # 重新 fit 包含所有新旧标签
                self.mlb.fit([list(all_tags)])
        else:
            self.mlb = MultiLabelBinarizer()
            self.mlb.fit([list(all_tags)])
        
        # 记录标签频率
        self.tag_counts = Counter()
        for _, _, _, tags in self.samples:
            self.tag_counts.update(tags)
        
        print(f"已加载 {len(self.samples)} 张图像，包含 {len(self.mlb.classes_)} 个唯一标签。")
        print(f"最常见的标签: {dict(self.tag_counts.most_common(5))}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_id, img_data, img_filename, labels = self.samples[idx]
        
        try:
            # 从二进制数据加载图像
            if img_data is None:
                # 如果数据缺失，创建一张空白图像
                image = Image.new('RGB', (224, 224), color='gray')
                print(f"警告: 图像 ID {img_id} 没有数据。使用空白图像。")
            else:
                image = Image.open(io.BytesIO(img_data)).convert('RGB')
        except Exception as e:
            # 如果加载失败，创建一张空白图像
            print(f"加载图像 ID {img_id} 失败: {e}。使用空白图像。")
            image = Image.new('RGB', (224, 224), color='gray')
        
        if self.transform:
            image = self.transform(image)
            
        label_vec = self.mlb.transform([labels])[0]
        label_tensor = torch.FloatTensor(label_vec)
        return image, label_tensor, img_id, img_filename


# save_anomalies_to_csv 函数：将异常信息保存到 CSV 文件
def save_anomalies_to_csv(anomalies, output_dir):
    """将异常信息保存到 CSV 文件中。"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(output_dir, f"anomalies_{timestamp}.csv")
    
    headers = [
        '图像 ID', 
        '图像名称',
        '真实标签', 
        '预测标签',
        '可能不正确的标签', 
        '可能缺失的标签',
        '置信度分数'
    ]
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for anomaly in anomalies:
            writer.writerow([
                anomaly['img_id'],
                anomaly['img_filename'] or 'N/A',
                ','.join(anomaly['true_tags']),
                ','.join(anomaly['pred_tags']),
                ','.join(anomaly['false_positives']),
                ','.join(anomaly['false_negatives']),
                ';'.join([f"{tag}:{score:.4f}" for tag, score in anomaly['confidence_scores'].items()])
            ])
    
    print(f"异常信息已保存到 CSV: {filename}")
    return filename


# AnomalyDetector 类：检测潜在的标签异常
class AnomalyDetector:
    """用于检测潜在标签异常的类。"""
    def __init__(self, model, dataset, device, threshold=0.5, confidence_threshold=0.9):
        self.model = model
        self.dataset = dataset
        self.device = device
        self.threshold = threshold
        self.confidence_threshold = confidence_threshold
        self.anomalies = []
        
    def detect(self, dataloader):
        """使用当前模型检测异常标签。"""
        self.model.eval()
        self.anomalies = []
        
        with torch.no_grad():
            for images, targets, img_ids, img_filenames in dataloader:
                images, targets = images.to(self.device), targets.to(self.device)
                outputs = torch.sigmoid(self.model(images))
                
                for i in range(outputs.size(0)):
                    img_id = img_ids[i].item()
                    img_filename = img_filenames[i] if img_filenames[i] else None
                    true_labels = targets[i].cpu().numpy()
                    pred_probs = outputs[i].cpu().numpy()
                    
                    # 检测高置信度矛盾
                    false_positives = np.where((pred_probs > self.confidence_threshold) & (true_labels == 0))[0]
                    false_negatives = np.where((pred_probs < (1 - self.confidence_threshold)) & (true_labels == 1))[0]
                    
                    if len(false_positives) > 0 or len(false_negatives) > 0:
                        # 获取异常标签名称
                        fp_tags = [self.dataset.mlb.classes_[idx] for idx in false_positives]
                        fn_tags = [self.dataset.mlb.classes_[idx] for idx in false_negatives]
                        
                        # 获取真实标签和预测标签
                        true_tags = [self.dataset.mlb.classes_[idx] for idx in np.where(true_labels == 1)[0]]
                        pred_tags = [self.dataset.mlb.classes_[idx] for idx in np.where(pred_probs > self.threshold)[0]]
                        
                        # 记录异常
                        self.anomalies.append({
                            'img_id': img_id,
                            'img_filename': img_filename,
                            'true_tags': true_tags,
                            'pred_tags': pred_tags,
                            'false_positives': fp_tags,
                            'false_negatives': fn_tags,
                            'confidence_scores': {
                                tag: float(pred_probs[i]) 
                                for i, tag in enumerate(self.dataset.mlb.classes_)
                                if i in false_positives or i in false_negatives
                            }
                        })
        
        print(f"检测到 {len(self.anomalies)} 个潜在标签异常。")
        return self.anomalies
    
    def save_anomalies(self, output_dir):
        """将异常保存到 CSV 文件。"""
        return save_anomalies_to_csv(self.anomalies, output_dir)


# evaluate_model 函数：评估模型性能
def evaluate_model(model, dataloader, criterion, device, mlb):
    """在验证集上评估模型性能。"""
    model.eval()
    val_loss = 0.0
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for images, targets, _, _ in dataloader:
            images, targets = images.to(device), targets.to(device)
            outputs = model(images)
            loss = criterion(outputs, targets)
            val_loss += loss.item() * images.size(0)
            
            preds = (torch.sigmoid(outputs) > 0.5).float().cpu().numpy()
            targets = targets.cpu().numpy()
            
            all_preds.append(preds)
            all_targets.append(targets)
    
    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)
    
    precision = precision_score(all_targets, all_preds, average='micro', zero_division=0)
    recall = recall_score(all_targets, all_preds, average='micro', zero_division=0)
    f1 = f1_score(all_targets, all_preds, average='micro', zero_division=0)
    
    # 计算每类指标
    per_class_f1 = f1_score(all_targets, all_preds, average=None, zero_division=0)
    tag_f1_dict = {tag: score for tag, score in zip(mlb.classes_, per_class_f1)}
    worst_tags = sorted(tag_f1_dict.items(), key=lambda x: x[1])[:5]
    
    return val_loss / len(dataloader.dataset), precision, recall, f1, worst_tags


# train 函数：训练模型
def train(db_path, num_epochs=20, batch_size=32, lr=1e-4, checkpoint_dir="checkpoints", 
          anomaly_dir="anomalies", val_ratio=0.2, anomaly_detection_start=3, 
          patience=5, weight_decay=1e-5, load_model_path=None):
    """
    训练模型，支持增量训练。
    db_path: SQLite 数据库路径
    num_epochs: 训练轮数
    batch_size: 批处理大小
    lr: 学习率
    checkpoint_dir: 模型保存目录
    anomaly_dir: 异常数据保存目录
    val_ratio: 验证集比例
    anomaly_detection_start: 开始异常检测的轮数
    patience: 早停耐心值
    weight_decay: 权重衰减
    load_model_path: 预训练模型路径，用于增量训练
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"使用设备: {device}")

    # 图像预处理与数据增强
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # 加载数据集
    try:
        # 如果存在预训练模型，尝试加载其 MLB
        mlb_from_checkpoint = None
        if load_model_path and os.path.exists(load_model_path):
            checkpoint = torch.load(load_model_path, map_location=device)
            # 确保 'mlb' 键存在并且是字节串，以便反序列化
            if 'mlb' in checkpoint and isinstance(checkpoint['mlb'], bytes):
                mlb_from_checkpoint = pickle.loads(checkpoint['mlb'])
                print(f"从 {load_model_path} 加载了 MultiLabelBinarizer 对象。")
            elif 'classes' in checkpoint: # 如果没有 mlb 对象，尝试从 classes 列表重建
                mlb_from_checkpoint = MultiLabelBinarizer()
                mlb_from_checkpoint.fit([checkpoint['classes']])
                print(f"从 {load_model_path} 加载了 {len(checkpoint['classes'])} 个旧标签并重建 MultiLabelBinarizer。")

        full_dataset = ImageTagDataset(db_path, transform=None, mlb=mlb_from_checkpoint)
        
        # 分割数据集
        dataset_size = len(full_dataset)
        val_size = int(val_ratio * dataset_size)
        train_size = dataset_size - val_size
        
        train_indices, val_indices = random_split(
            range(dataset_size), 
            [train_size, val_size], 
            generator=torch.Generator().manual_seed(42)
        )
        
        # 为训练集和验证集创建带转换器的数据集子集
        class TransformSubset(Dataset):
            def __init__(self, dataset, indices, transform):
                self.dataset = dataset
                self.indices = indices
                self.transform = transform
                
            def __len__(self):
                return len(self.indices)
                
            def __getitem__(self, idx):
                image, labels, img_id, img_filename = self.dataset[self.indices[idx]]
                if self.transform:
                    if isinstance(image, torch.Tensor):
                        image = transforms.ToPILImage()(image)
                    image = self.transform(image)
                return image, labels, img_id, img_filename
        
        train_dataset = TransformSubset(full_dataset, train_indices, train_transform)
        val_dataset = TransformSubset(full_dataset, val_indices, val_transform)
        
        # 创建数据加载器
        train_loader = DataLoader(
            train_dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=0  # SQLite 不支持多进程
        )
        
        val_loader = DataLoader(
            val_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=0
        )
        
        print(f"数据集加载完成: {len(train_dataset)} 个训练样本，{len(val_dataset)} 个验证样本。")
        print(f"总标签数: {len(full_dataset.mlb.classes_)}")
        
    except Exception as e:
        print(f"加载数据集时发生错误: {e}")
        return

    # 加载预训练模型或创建新模型
    model = models.resnet50(pretrained=True)  # 使用 ResNet50
    num_features = model.fc.in_features
    num_classes = len(full_dataset.mlb.classes_)

    checkpoint = None # 初始化 checkpoint 变量
    if load_model_path and os.path.exists(load_model_path):
        print(f"从 {load_model_path} 加载模型进行增量训练。")
        checkpoint = torch.load(load_model_path, map_location=device)
        
        # 尝试加载除 fc 层以外的所有层权重
        model_state_dict = model.state_dict()
        # 过滤掉不匹配的 fc 层权重，并更新模型状态字典
        pretrained_dict = {k: v for k, v in checkpoint['model_state_dict'].items() if k in model_state_dict and 'fc' not in k}
        model_state_dict.update(pretrained_dict)
        model.load_state_dict(model_state_dict, strict=False) # strict=False 允许加载不完全匹配的字典

        # 检查是否需要调整输出层
        old_num_classes = len(checkpoint['classes'])
        if old_num_classes != num_classes:
            print(f"模型输出层大小从 {old_num_classes} 调整到 {num_classes} 以适应新标签。")
            # 创建新的全连接层
            new_fc = nn.Linear(num_features, num_classes)
            # 复制旧权重到新层
            min_classes = min(old_num_classes, num_classes)
            if 'fc.weight' in checkpoint['model_state_dict']:
                new_fc.weight.data[:min_classes, :] = checkpoint['model_state_dict']['fc.weight'][:min_classes, :]
            if 'fc.bias' in checkpoint['model_state_dict']:
                new_fc.bias.data[:min_classes] = checkpoint['model_state_dict']['fc.bias'][:min_classes]
            model.fc = new_fc
        else: # 如果类别数不变，但 fc 层没有完全加载，则确保 fc 层被正确设置
             # 如果之前因为 strict=False 没有加载 fc 层，则手动加载
            if 'fc.weight' in checkpoint['model_state_dict'] and 'fc.bias' in checkpoint['model_state_dict']:
                model.fc = nn.Linear(num_features, num_classes) # 重新初始化以确保形状正确
                model.fc.weight.data = checkpoint['model_state_dict']['fc.weight']
                model.fc.bias.data = checkpoint['model_state_dict']['fc.bias']
            else: # 如果检查点中没有 fc 层，则保持当前模型新初始化的 fc 层
                 model.fc = nn.Linear(num_features, num_classes)

        print(f"模型已加载，并且输出层已调整。")
    else:
        print("未检测到预训练模型，从头开始训练。")
        model.fc = nn.Linear(num_features, num_classes)
    
    model = model.to(device)

    # 损失函数
    criterion = nn.BCEWithLogitsLoss()
    
    # 在模型结构确定后，重新初始化优化器，以确保其内部状态与模型参数匹配
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    print("优化器已重新初始化以匹配模型参数。")

    # 学习率调度器 - 带热重启的余弦退火
    # 调度器需要在优化器之后重新创建
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=5, T_mult=2, eta_min=lr/10
    )
    print("学习率调度器已重新初始化。")

    # 创建目录
    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(anomaly_dir, exist_ok=True)
    
    # 初始化异常检测器
    anomaly_detector = AnomalyDetector(model, full_dataset, device)
    
    # 跟踪指标
    train_losses = []
    val_losses = []
    precisions = []
    recalls = []
    f1_scores = []
    
    # 最佳模型跟踪
    best_val_f1 = 0.0
    best_model_path = ""
    patience_counter = 0
    
    # 排除的异常图像 ID
    excluded_img_ids = set()
    if checkpoint and 'excluded_img_ids' in checkpoint: # 检查 checkpoint 是否为 None
        excluded_img_ids.update(checkpoint['excluded_img_ids'])
        print(f"从检查点加载了 {len(excluded_img_ids)} 个已排除的图像 ID。")
    
    # 训练循环
    for epoch in range(1, num_epochs + 1):
        # 训练阶段
        model.train()
        running_loss = 0.0
        batch_count = 0
        
        for images, targets, img_ids, _ in train_loader:
            # 过滤掉异常图像
            valid_indices = torch.tensor([i for i, img_id in enumerate(img_ids) 
                                        if img_id.item() not in excluded_img_ids])
            
            if len(valid_indices) == 0:
                continue
                
            images = images[valid_indices].to(device)
            targets = targets[valid_indices].to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            batch_count += 1
            
            # 每 10 批次打印一次进度
            if batch_count % 10 == 0:
                print(f"轮次 {epoch}/{num_epochs}, 批次 {batch_count}/{len(train_loader)}, "
                      f"损失: {loss.item():.4f}")
        
        # 更新学习率
        scheduler.step()
        
        # 计算当前轮次的指标
        epoch_train_loss = running_loss / (len(train_dataset) - len(excluded_img_ids))
        train_losses.append(epoch_train_loss)
        
        # 验证阶段
        val_loss, precision, recall, f1, worst_tags = evaluate_model(
            model, val_loader, criterion, device, full_dataset.mlb
        )
        val_losses.append(val_loss)
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        
        print(f"轮次 {epoch}/{num_epochs}")
        print(f"  训练损失: {epoch_train_loss:.4f}")
        print(f"  验证损失: {val_loss:.4f}, 精确率: {precision:.4f}, 召回率: {recall:.4f}, F1分数: {f1:.4f}")
        print(f"  表现最差的标签: {worst_tags}")
        
        # 保存最佳模型
        if f1 > best_val_f1:
            best_val_f1 = f1
            best_model_path = os.path.join(checkpoint_dir, f"best_model_epoch{epoch}.pth")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_f1': f1,
                'val_precision': precision,
                'val_recall': recall,
                'classes': full_dataset.mlb.classes_.tolist(), # 保存标签列表
                'mlb': pickle.dumps(full_dataset.mlb), # 序列化MLB对象
                'excluded_img_ids': list(excluded_img_ids)
            }, best_model_path)
            print(f"已保存最佳模型到 {best_model_path}")
            patience_counter = 0
        else:
            patience_counter += 1
            
        # 早停检查
        if patience_counter >= patience:
            print(f"在 {epoch} 轮后触发早停。")
            break
        
        # 保存周期性检查点
        if epoch % 5 == 0 or epoch == num_epochs:
            checkpoint_path = os.path.join(checkpoint_dir, f"model_epoch{epoch}.pth")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_f1': f1,
                'classes': full_dataset.mlb.classes_.tolist(), # 保存标签列表
                'mlb': pickle.dumps(full_dataset.mlb), # 序列化MLB对象
                'excluded_img_ids': list(excluded_img_ids)
            }, checkpoint_path)
            print(f"已保存检查点模型到 {checkpoint_path}")
        
        # 执行异常检测 (从指定轮次开始)
        if epoch >= anomaly_detection_start:
            print("正在执行异常检测...")
            anomalies = anomaly_detector.detect(train_loader)
            
            if anomalies:
                # 保存异常到 CSV
                anomaly_file = anomaly_detector.save_anomalies(anomaly_dir)
                
                # 更新排除列表
                new_excluded = set(anomaly['img_id'] for anomaly in anomalies)
                excluded_img_ids.update(new_excluded)
                print(f"发现 {len(new_excluded)} 张新异常图像，总共排除: {len(excluded_img_ids)}")
    
    # 绘制训练指标图
    plot_training_metrics(train_losses, val_losses, precisions, recalls, f1_scores, checkpoint_dir)
    
    print("训练完成。")
    print(f"最佳验证 F1 分数: {best_val_f1:.4f}，模型保存路径: {best_model_path}")
    print(f"总共排除的异常图像数量: {len(excluded_img_ids)}")
    
    return model, full_dataset.mlb, best_model_path


# plot_training_metrics 函数：绘制训练指标图
def plot_training_metrics(train_losses, val_losses, precisions, recalls, f1_scores, output_dir):
    """绘制训练过程中的各项指标图表。"""
    epochs = range(1, len(train_losses) + 1)
    
    plt.figure(figsize=(15, 12))
    
    # 绘制损失曲线
    plt.subplot(2, 1, 1)
    plt.plot(epochs, train_losses, 'b-', label='训练损失')
    plt.plot(epochs, val_losses, 'r-', label='验证损失')
    plt.title('训练和验证损失')
    plt.xlabel('轮次')
    plt.ylabel('损失')
    plt.legend()
    plt.grid(True)
    
    # 绘制精确率、召回率和 F1 分数曲线
    plt.subplot(2, 1, 2)
    plt.plot(epochs, precisions, 'g-', label='精确率')
    plt.plot(epochs, recalls, 'b-', label='召回率')
    plt.plot(epochs, f1_scores, 'r-', label='F1 分数')
    plt.title('验证指标')
    plt.xlabel('轮次')
    plt.ylabel('分数')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    metrics_plot_path = os.path.join(output_dir, 'training_metrics.png')
    plt.savefig(metrics_plot_path)
    plt.close()
    print(f"训练指标图已保存到: {metrics_plot_path}")


# predict 函数：预测单张图像的标签
def predict(model, image_path, mlb, device, transform=None, top_k=5, threshold=0.5):
    """预测单张图像的标签。"""
    if transform is None:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    # 加载图像
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # 进行预测
    model.eval()
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.sigmoid(outputs)
    
    # 获取预测结果
    probs = probs.cpu().numpy()[0]
    
    # 获取所有高于阈值的标签
    predicted_tags = [(mlb.classes_[i], float(probs[i])) 
                      for i in range(len(mlb.classes_)) 
                      if probs[i] > threshold]
    
    # 按置信度排序
    predicted_tags.sort(key=lambda x: x[1], reverse=True)
    
    # 获取 Top-K 预测结果
    top_predictions = predicted_tags[:top_k] if top_k > 0 else predicted_tags
    
    return top_predictions, predicted_tags


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="训练多标签图像分类器并检测异常。")
    parser.add_argument('--db', type=str, default='data.db', help='SQLite 数据库路径。')
    parser.add_argument('--epochs', type=int, default=20, help='训练轮数。')
    parser.add_argument('--batch_size', type=int, default=32, help='批处理大小。')
    parser.add_argument('--lr', type=float, default=1e-4, help='学习率。')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints', help='模型检查点目录。')
    parser.add_argument('--anomaly_dir', type=str, default='anomalies', help='异常数据目录。')
    parser.add_argument('--val_ratio', type=float, default=0.2, help='验证集比例。')
    parser.add_argument('--anomaly_detection_start', type=int, default=3, help='开始异常检测的轮数。')
    parser.add_argument('--patience', type=int, default=5, help='早停耐心值。')
    parser.add_argument('--weight_decay', type=float, default=1e-5, help='正则化的权重衰减。')
    parser.add_argument('--load_model', type=str, default=None, help='要加载的预训练模型路径，用于增量训练。')
    
    args = parser.parse_args()
    
    # 训练模型
    model, mlb, best_model_path = train(
        args.db, 
        args.epochs, 
        args.batch_size, 
        args.lr, 
        args.checkpoint_dir,
        args.anomaly_dir,
        args.val_ratio,
        args.anomaly_detection_start,
        args.patience,
        args.weight_decay,
        args.load_model # 传递加载模型路径参数
    )
