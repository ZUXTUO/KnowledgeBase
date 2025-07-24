import os
import sqlite3
import io
import torch
import argparse
from PIL import Image
from torchvision import transforms, models
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer


class ImageTagPredictor:
    """使用训练好的模型对数据库中的图像进行标签预测"""
    def __init__(self, db_path, model_path, confidence_threshold=0.7, model_type='resnet50'):
        self.db_path = db_path
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_type = model_type
        
        # 加载模型
        self.model, self.class_names = self._load_model()
        print(f"已加载{self.model_type}模型，支持的标签数量: {len(self.class_names)}")
        
        # 图像预处理：与训练时相同
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # 连接数据库
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # 初始化标签二值化器
        self.mlb = MultiLabelBinarizer()
        self.mlb.fit([self.class_names])

    def _load_model(self):
        """加载预训练的模型和标签"""
        # 加载检查点
        checkpoint = torch.load(self.model_path, map_location=self.device)
        class_names = checkpoint.get('classes', [])
        
        # 创建与训练时相同的模型架构
        if self.model_type == 'resnet50':
            model = models.resnet50(pretrained=False)
        elif self.model_type == 'resnet101':
            model = models.resnet101(pretrained=False)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
            
        # 获取特征数量并替换最后的全连接层
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, len(class_names))
        
        # 加载权重
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(self.device)
        model.eval()  # 设置为评估模式
        
        return model, class_names

    def predict_single_image(self, img_data):
        """预测单个图像的标签"""
        try:
            if img_data is None:
                return []
            
            # 从二进制数据加载图像
            image = Image.open(io.BytesIO(img_data)).convert('RGB')
            
            # 预处理图像
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probs = torch.sigmoid(outputs).cpu().numpy()[0]
                
            # 获取高置信度的预测
            predicted_indices = np.where(probs >= self.confidence_threshold)[0]
            predicted_tags = [self.class_names[idx] for idx in predicted_indices]
            
            # 返回预测标签和对应的置信度
            tag_confidences = [(self.class_names[i], float(probs[i])) for i in range(len(probs)) if probs[i] >= self.confidence_threshold]
            tag_confidences.sort(key=lambda x: x[1], reverse=True)
            
            return tag_confidences
            
        except Exception as e:
            print(f"预测图像时出错: {e}")
            return []

    def get_all_tagged_image_ids(self):
        """获取所有已标记图片的ID"""
        self.cursor.execute("SELECT DISTINCT image_id FROM image_tags")
        return set(row[0] for row in self.cursor.fetchall())

    def get_existing_tags_for_image(self, image_id):
        """获取图像已有的标签"""
        self.cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN image_tags it ON t.id = it.tag_id
            WHERE it.image_id = ?
        """, (image_id,))
        return set(row[0] for row in self.cursor.fetchall())

    def tag_exists(self, tag_name):
        """检查标签是否存在，返回ID或None"""
        self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def create_tag(self, tag_name):
        """创建新标签"""
        self.cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
        self.conn.commit()
        return self.cursor.lastrowid

    def add_tag_to_image(self, image_id, tag_id):
        """为图像添加标签"""
        try:
            self.cursor.execute("INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)", 
                               (image_id, tag_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 标签可能已经存在
            return False

    def process_all_images(self, limit=None, img_ids=None):
        """处理所有图像，添加预测的标签"""
        # 构建查询
        if img_ids:
            placeholders = ','.join('?' for _ in img_ids)
            query = f"SELECT id, data FROM images WHERE id IN ({placeholders})"
            params = img_ids
        else:
            query = "SELECT id, data FROM images"
            params = []
            
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        # 执行查询
        self.cursor.execute(query, params)
        total_processed = 0
        total_tags_added = 0
        
        # 处理每张图像
        for img_id, img_data in self.cursor.fetchall():
            existing_tags = self.get_existing_tags_for_image(img_id)
            predictions = self.predict_single_image(img_data)
            
            tags_added = 0
            for tag_name, confidence in predictions:
                # 如果标签已存在于图像中，跳过
                if tag_name in existing_tags:
                    continue
                
                # 检查标签是否存在，不存在则创建
                tag_id = self.tag_exists(tag_name)
                if tag_id is None:
                    tag_id = self.create_tag(tag_name)
                
                # 添加标签到图像
                success = self.add_tag_to_image(img_id, tag_id)
                if success:
                    tags_added += 1
                    total_tags_added += 1
                    print(f"图像 {img_id}: 添加标签 '{tag_name}' (置信度: {confidence:.4f})")
            
            total_processed += 1
            if total_processed % 10 == 0:
                print(f"已处理 {total_processed} 张图像，添加了 {total_tags_added} 个标签")
        
        print(f"完成！共处理 {total_processed} 张图像，添加了 {total_tags_added} 个标签")

    def process_untagged_images(self, limit=None):
        """处理没有标签的图像"""
        # 获取所有已标记图片的ID
        tagged_image_ids = self.get_all_tagged_image_ids()
        
        # 查询未标记的图像
        query = "SELECT id FROM images WHERE id NOT IN (SELECT DISTINCT image_id FROM image_tags)"
        if limit:
            query += f" LIMIT {limit}"
        
        self.cursor.execute(query)
        untagged_ids = [row[0] for row in self.cursor.fetchall()]
        
        print(f"找到 {len(untagged_ids)} 张未标记的图像")
        
        # 处理未标记的图像
        self.process_all_images(img_ids=untagged_ids)

    def process_partially_tagged_images(self, limit=None):
        """处理已有部分标签的图像，为它们添加新标签"""
        # 获取所有已标记图片的ID
        query = """
            SELECT i.id
            FROM images i
            JOIN image_tags it ON i.id = it.image_id
            GROUP BY i.id
            HAVING COUNT(it.tag_id) < 5  -- 例如，只处理标签少于5个的图像
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        self.cursor.execute(query)
        partially_tagged_ids = [row[0] for row in self.cursor.fetchall()]
        
        print(f"找到 {len(partially_tagged_ids)} 张部分标记的图像")
        
        # 处理这些图像
        self.process_all_images(img_ids=partially_tagged_ids)

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='为数据库中的图像预测并添加标签')
    parser.add_argument('--db', type=str, default='data.db', help='SQLite数据库路径')
    parser.add_argument('--model', type=str, required=True, help='训练好的模型路径')
    parser.add_argument('--threshold', type=float, default=0.7, help='标签预测的置信度阈值')
    parser.add_argument('--limit', type=int, default=None, help='处理的图像数量限制')
    parser.add_argument('--mode', type=str, default='all', choices=['all', 'untagged', 'partial'],
                        help='处理模式：全部、未标记或部分标记的图像')
    parser.add_argument('--model_type', type=str, default='resnet50', choices=['resnet50', 'resnet101'],
                        help='使用的模型类型: resnet50 或 resnet101')
    
    args = parser.parse_args()
    
    predictor = ImageTagPredictor(args.db, args.model, args.threshold, args.model_type)
    
    try:
        if args.mode == 'untagged':
            predictor.process_untagged_images(args.limit)
        elif args.mode == 'partial':
            predictor.process_partially_tagged_images(args.limit)
        else:  # 'all'
            predictor.process_all_images(args.limit)
    finally:
        predictor.close()


if __name__ == "__main__":
    main()