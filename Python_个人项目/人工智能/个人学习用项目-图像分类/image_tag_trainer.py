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


class ImageTagDataset(Dataset):
    """Dataset loading images and multi-labels directly from SQLite database"""
    def __init__(self, db_path, transform=None):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.transform = transform
        
        # Check database schema
        self.cursor.execute("PRAGMA table_info(images)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        # Determine if we have image data and filenames
        has_data = 'data' in columns
        has_filename = 'filename' in columns
        
        # Query for images with tags
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
        
        # Label binarization
        self.mlb = MultiLabelBinarizer()
        self.mlb.fit([list(all_tags)])
        
        # Record tag frequencies
        self.tag_counts = Counter()
        for _, _, _, tags in self.samples:
            self.tag_counts.update(tags)
        
        print(f"Loaded {len(self.samples)} images with {len(all_tags)} unique tags")
        print(f"Most common tags: {dict(self.tag_counts.most_common(5))}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_id, img_data, img_filename, labels = self.samples[idx]
        
        try:
            # Load image from binary data
            if img_data is None:
                # Create blank image if data is missing
                image = Image.new('RGB', (224, 224), color='gray')
                print(f"Warning: Image ID {img_id} has no data. Using blank image.")
            else:
                image = Image.open(io.BytesIO(img_data)).convert('RGB')
        except Exception as e:
            # Create blank image if loading fails
            print(f"Error loading image ID {img_id}: {e}")
            image = Image.new('RGB', (224, 224), color='gray')
        
        if self.transform:
            image = self.transform(image)
            
        label_vec = self.mlb.transform([labels])[0]
        label_tensor = torch.FloatTensor(label_vec)
        return image, label_tensor, img_id, img_filename


def save_anomalies_to_csv(anomalies, output_dir):
    """Save anomaly information to CSV file"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(output_dir, f"anomalies_{timestamp}.csv")
    
    headers = [
        'Image ID', 
        'Image Name',
        'True Labels', 
        'Predicted Labels',
        'Possibly Incorrect Labels', 
        'Possibly Missing Labels',
        'Confidence Scores'
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
    
    print(f"Anomalies saved to CSV: {filename}")
    return filename


class AnomalyDetector:
    """Detect potential label anomalies"""
    def __init__(self, model, dataset, device, threshold=0.5, confidence_threshold=0.9):
        self.model = model
        self.dataset = dataset
        self.device = device
        self.threshold = threshold
        self.confidence_threshold = confidence_threshold
        self.anomalies = []
        
    def detect(self, dataloader):
        """Detect anomalous labels using current model"""
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
                    
                    # Detect high confidence contradictions
                    false_positives = np.where((pred_probs > self.confidence_threshold) & (true_labels == 0))[0]
                    false_negatives = np.where((pred_probs < (1 - self.confidence_threshold)) & (true_labels == 1))[0]
                    
                    if len(false_positives) > 0 or len(false_negatives) > 0:
                        # Get anomalous tag names
                        fp_tags = [self.dataset.mlb.classes_[idx] for idx in false_positives]
                        fn_tags = [self.dataset.mlb.classes_[idx] for idx in false_negatives]
                        
                        # Get true and predicted tags
                        true_tags = [self.dataset.mlb.classes_[idx] for idx in np.where(true_labels == 1)[0]]
                        pred_tags = [self.dataset.mlb.classes_[idx] for idx in np.where(pred_probs > self.threshold)[0]]
                        
                        # Record anomaly
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
        
        print(f"Detected {len(self.anomalies)} potential label anomalies")
        return self.anomalies
    
    def save_anomalies(self, output_dir):
        """Save anomalies to CSV file"""
        return save_anomalies_to_csv(self.anomalies, output_dir)


def evaluate_model(model, dataloader, criterion, device, mlb):
    """Evaluate model performance on validation set"""
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
    
    # Calculate per-class metrics
    per_class_f1 = f1_score(all_targets, all_preds, average=None, zero_division=0)
    tag_f1_dict = {tag: score for tag, score in zip(mlb.classes_, per_class_f1)}
    worst_tags = sorted(tag_f1_dict.items(), key=lambda x: x[1])[:5]
    
    return val_loss / len(dataloader.dataset), precision, recall, f1, worst_tags


def train(db_path, num_epochs=20, batch_size=32, lr=1e-4, checkpoint_dir="checkpoints", 
          anomaly_dir="anomalies", val_ratio=0.2, anomaly_detection_start=3, 
          patience=5, weight_decay=1e-5):
    """Train model with improved workflow including early stopping and better validation"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Image preprocessing with augmentation
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

    # Load dataset
    try:
        full_dataset = ImageTagDataset(db_path, transform=None)
        
        # Split dataset
        dataset_size = len(full_dataset)
        val_size = int(val_ratio * dataset_size)
        train_size = dataset_size - val_size
        
        train_indices, val_indices = random_split(
            range(dataset_size), 
            [train_size, val_size], 
            generator=torch.Generator().manual_seed(42)
        )
        
        # Create dataset subsets with appropriate transforms
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
        
        # Create data loaders
        train_loader = DataLoader(
            train_dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=0  # SQLite doesn't support multiprocessing
        )
        
        val_loader = DataLoader(
            val_dataset, 
            batch_size=batch_size, 
            shuffle=False, 
            num_workers=0
        )
        
        print(f"Dataset loaded: {len(train_dataset)} training samples, {len(val_dataset)} validation samples")
        print(f"Total tags: {len(full_dataset.mlb.classes_)}")
        
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # Load pretrained model
    model = models.resnet50(pretrained=True)  # Using ResNet50 for better performance
    num_features = model.fc.in_features
    num_classes = len(full_dataset.mlb.classes_)
    model.fc = nn.Linear(num_features, num_classes)
    model = model.to(device)

    # Loss function and optimizer with weight decay
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    
    # Learning rate scheduler - cosine annealing with warm restarts
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=5, T_mult=2, eta_min=lr/10
    )

    # Create directories
    os.makedirs(checkpoint_dir, exist_ok=True)
    os.makedirs(anomaly_dir, exist_ok=True)
    
    # Initialize anomaly detector
    anomaly_detector = AnomalyDetector(model, full_dataset, device)
    
    # Tracking metrics
    train_losses = []
    val_losses = []
    precisions = []
    recalls = []
    f1_scores = []
    
    # Best model tracking
    best_val_f1 = 0.0
    best_model_path = ""
    patience_counter = 0
    
    # Excluded anomalous image IDs
    excluded_img_ids = set()
    
    # Training loop
    for epoch in range(1, num_epochs + 1):
        # Training phase
        model.train()
        running_loss = 0.0
        batch_count = 0
        
        for images, targets, img_ids, _ in train_loader:
            # Filter out anomalous images
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
            
            # Print progress for every 10 batches
            if batch_count % 10 == 0:
                print(f"Epoch {epoch}/{num_epochs}, Batch {batch_count}/{len(train_loader)}, "
                      f"Loss: {loss.item():.4f}")
        
        # Update learning rate
        scheduler.step()
        
        # Calculate epoch metrics
        epoch_train_loss = running_loss / (len(train_dataset) - len(excluded_img_ids))
        train_losses.append(epoch_train_loss)
        
        # Validation phase
        val_loss, precision, recall, f1, worst_tags = evaluate_model(
            model, val_loader, criterion, device, full_dataset.mlb
        )
        val_losses.append(val_loss)
        precisions.append(precision)
        recalls.append(recall)
        f1_scores.append(f1)
        
        print(f"Epoch {epoch}/{num_epochs}")
        print(f"  Train Loss: {epoch_train_loss:.4f}")
        print(f"  Val Loss: {val_loss:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        print(f"  Worst performing tags: {worst_tags}")
        
        # Save best model
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
                'classes': full_dataset.mlb.classes_.tolist(),
                'excluded_img_ids': list(excluded_img_ids)
            }, best_model_path)
            print(f"Saved best model to {best_model_path}")
            patience_counter = 0
        else:
            patience_counter += 1
            
        # Early stopping check
        if patience_counter >= patience:
            print(f"Early stopping triggered after {epoch} epochs")
            break
        
        # Save periodic checkpoint
        if epoch % 5 == 0 or epoch == num_epochs:
            checkpoint_path = os.path.join(checkpoint_dir, f"model_epoch{epoch}.pth")
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_f1': f1,
                'classes': full_dataset.mlb.classes_.tolist(),
                'excluded_img_ids': list(excluded_img_ids)
            }, checkpoint_path)
        
        # Perform anomaly detection (starting from specified epoch)
        if epoch >= anomaly_detection_start:
            print("Performing anomaly detection...")
            anomalies = anomaly_detector.detect(train_loader)
            
            if anomalies:
                # Save anomalies to CSV
                anomaly_file = anomaly_detector.save_anomalies(anomaly_dir)
                
                # Update exclusion list
                new_excluded = set(anomaly['img_id'] for anomaly in anomalies)
                excluded_img_ids.update(new_excluded)
                print(f"Found {len(new_excluded)} new anomalous images, total excluded: {len(excluded_img_ids)}")
    
    # Plot training metrics
    plot_training_metrics(train_losses, val_losses, precisions, recalls, f1_scores, checkpoint_dir)
    
    print("Training completed.")
    print(f"Best validation F1 score: {best_val_f1:.4f}, Model saved at: {best_model_path}")
    print(f"Total anomalous images excluded: {len(excluded_img_ids)}")
    
    return model, full_dataset.mlb, best_model_path


def plot_training_metrics(train_losses, val_losses, precisions, recalls, f1_scores, output_dir):
    """Plot training metrics over time"""
    epochs = range(1, len(train_losses) + 1)
    
    plt.figure(figsize=(15, 12))
    
    # Plot losses
    plt.subplot(2, 1, 1)
    plt.plot(epochs, train_losses, 'b-', label='Training Loss')
    plt.plot(epochs, val_losses, 'r-', label='Validation Loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Plot precision, recall and F1
    plt.subplot(2, 1, 2)
    plt.plot(epochs, precisions, 'g-', label='Precision')
    plt.plot(epochs, recalls, 'b-', label='Recall')
    plt.plot(epochs, f1_scores, 'r-', label='F1 Score')
    plt.title('Validation Metrics')
    plt.xlabel('Epochs')
    plt.ylabel('Score')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    metrics_plot_path = os.path.join(output_dir, 'training_metrics.png')
    plt.savefig(metrics_plot_path)
    plt.close()
    print(f"Training metrics plot saved to: {metrics_plot_path}")


def predict(model, image_path, mlb, device, transform=None, top_k=5, threshold=0.5):
    """Predict tags for a single image"""
    if transform is None:
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    # Load image
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Make prediction
    model.eval()
    with torch.no_grad():
        outputs = model(image_tensor)
        probs = torch.sigmoid(outputs)
    
    # Get predictions
    probs = probs.cpu().numpy()[0]
    
    # Get all tags above threshold
    predicted_tags = [(mlb.classes_[i], float(probs[i])) 
                      for i in range(len(mlb.classes_)) 
                      if probs[i] > threshold]
    
    # Sort by confidence
    predicted_tags.sort(key=lambda x: x[1], reverse=True)
    
    # Get top-k predictions
    top_predictions = predicted_tags[:top_k] if top_k > 0 else predicted_tags
    
    return top_predictions, predicted_tags


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Train multi-label image classifier and detect anomalies")
    parser.add_argument('--db', type=str, default='data.db', help='SQLite database path')
    parser.add_argument('--epochs', type=int, default=20, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints', help='Model checkpoint directory')
    parser.add_argument('--anomaly_dir', type=str, default='anomalies', help='Anomaly data directory')
    parser.add_argument('--val_ratio', type=float, default=0.2, help='Validation set ratio')
    parser.add_argument('--anomaly_detection_start', type=int, default=3, help='Epoch to start anomaly detection')
    parser.add_argument('--patience', type=int, default=5, help='Early stopping patience')
    parser.add_argument('--weight_decay', type=float, default=1e-5, help='Weight decay for regularization')
    
    args = parser.parse_args()
    
    # Train model
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
        args.weight_decay
    )