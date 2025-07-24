import os
import sqlite3
import io
import torch
import argparse
from PIL import Image
from torchvision import transforms, models
import torch.nn as nn
import numpy as np
from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename


class ImageTagPredictor:
    """使用训练好的模型对图像进行标签预测"""
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
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

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

    def predict_image(self, image_file):
        """预测上传图像的标签"""
        try:
            # 读取图像文件
            image = Image.open(image_file).convert('RGB')
            
            # 预处理图像
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # 推理
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probs = torch.sigmoid(outputs).cpu().numpy()[0]
                
            # 获取高置信度的预测
            tag_confidences = [(self.class_names[i], float(probs[i])) for i in range(len(probs)) 
                               if probs[i] >= self.confidence_threshold]
            tag_confidences.sort(key=lambda x: x[1], reverse=True)
            
            return tag_confidences
            
        except Exception as e:
            print(f"预测图像时出错: {e}")
            return []

    def save_image_with_tags(self, image_file, tags):
        """将图像和标签保存到数据库"""
        try:
            # 读取图像数据
            image_data = image_file.read()
            image_file.seek(0)  # 重置文件指针以便后续处理
            
            # 插入图像
            self.cursor.execute("INSERT INTO images (data) VALUES (?)", (image_data,))
            image_id = self.cursor.lastrowid
            
            # 为每个标签创建记录
            for tag_name, _ in tags:
                # 检查标签是否存在
                self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                result = self.cursor.fetchone()
                
                if result:
                    tag_id = result[0]
                else:
                    # 创建新标签
                    self.cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                    tag_id = self.cursor.lastrowid
                
                # 添加图像-标签关联
                self.cursor.execute("INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)", 
                                  (image_id, tag_id))
            
            self.conn.commit()
            return image_id
            
        except Exception as e:
            self.conn.rollback()
            print(f"保存图像和标签时出错: {e}")
            return None

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>图像标签预测器</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-form {
            margin: 20px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .result {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            display: {{ 'block' if prediction_results else 'none' }};
        }
        .tag {
            display: inline-block;
            background-color: #f1f1f1;
            padding: 5px 10px;
            margin: 5px;
            border-radius: 20px;
        }
        .confidence {
            color: #666;
            font-size: 0.8em;
        }
        img.preview {
            max-width: 100%;
            max-height: 400px;
            margin: 10px 0;
        }
        .save-option {
            margin-top: 20px;
        }
        .button {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 5px;
        }
        .message {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            background-color: {{ '#DFF2BF' if message_type == 'success' else '#FFBABA' }};
            color: {{ '#4F8A10' if message_type == 'success' else '#D8000C' }};
            display: {{ 'block' if message else 'none' }};
        }
    </style>
</head>
<body>
    <h1>图像标签预测器</h1>
    
    <div class="message">
        {{ message }}
    </div>
    
    <div class="upload-form">
        <h2>上传图像</h2>
        <form action="/" method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit" class="button">预测标签</button>
        </form>
    </div>
    
    <div class="result">
        <h2>预测结果</h2>
        {% if image_path %}
        <img src="{{ image_path }}" class="preview">
        {% endif %}
        
        <h3>预测的标签：</h3>
        {% for tag, confidence in prediction_results %}
        <div class="tag">
            {{ tag }} <span class="confidence">({{ "%.2f"|format(confidence*100) }}%)</span>
        </div>
        {% endfor %}
        
        {% if prediction_results %}
        <div class="save-option">
            <form action="/save" method="post" enctype="multipart/form-data">
                <input type="hidden" name="image_path" value="{{ image_path }}">
                {% for tag, confidence in prediction_results %}
                <input type="hidden" name="tags" value="{{ tag }}">
                <input type="hidden" name="confidences" value="{{ confidence }}">
                {% endfor %}
                <button type="submit" class="button">保存到数据库</button>
            </form>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


# 初始化Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局变量存储预测器实例
predictor = None


@app.route('/', methods=['GET', 'POST'])
def index():
    message = ''
    message_type = ''
    prediction_results = []
    image_path = ''
    
    if request.method == 'POST':
        # 检查是否有文件
        if 'image' not in request.files:
            message = '没有选择文件'
            message_type = 'error'
        else:
            file = request.files['image']
            
            # 检查文件是否为空
            if file.filename == '':
                message = '没有选择文件'
                message_type = 'error'
            else:
                try:
                    # 保存上传的文件
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # 复制一份文件用于预测（解决文件指针位置问题）
                    with open(filepath, 'rb') as f:
                        image_content = f.read()
                    image_file = io.BytesIO(image_content)
                    
                    # 预测标签
                    prediction_results = predictor.predict_image(image_file)
                    image_path = f'/uploads/{filename}'
                    
                    if not prediction_results:
                        message = '无法为此图像识别任何标签'
                        message_type = 'error'
                    
                except Exception as e:
                    message = f'处理图像时出错: {str(e)}'
                    message_type = 'error'
    
    return render_template_string(
        HTML_TEMPLATE, 
        prediction_results=prediction_results,
        image_path=image_path,
        message=message,
        message_type=message_type
    )


@app.route('/save', methods=['POST'])
def save_to_db():
    try:
        image_path = request.form.get('image_path')
        if not image_path:
            return redirect(url_for('index'))
        
        # 获取标签和置信度
        tags = request.form.getlist('tags')
        confidences = request.form.getlist('confidences')
        
        # 组合标签和置信度
        tag_confidences = list(zip(tags, [float(c) for c in confidences]))
        
        # 从路径中提取文件名 - 处理带有前缀的路径
        if image_path.startswith('/'):
            image_path = image_path[1:]  # 去掉开头的斜杠
        
        if image_path.startswith('uploads/'):
            filename = image_path[8:]  # 去掉 "uploads/" 前缀
        else:
            filename = os.path.basename(image_path)
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 打开文件并保存到数据库
        with open(filepath, 'rb') as f:
            image_id = predictor.save_image_with_tags(f, tag_confidences)
        
        if image_id:
            message = f'图像和标签已保存到数据库，ID: {image_id}'
            message_type = 'success'
        else:
            message = '保存到数据库失败'
            message_type = 'error'
            
    except Exception as e:
        message = f'保存到数据库时出错: {str(e)}'
        message_type = 'error'
    
    # 重定向到首页并显示消息
    return render_template_string(
        HTML_TEMPLATE,
        prediction_results=[],
        image_path='',
        message=message,
        message_type=message_type
    )


# 为静态文件（上传的图像）创建路由
@app.route('/uploads/<path:filename>')
def static_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"访问文件错误: {str(e)}")
        return "文件未找到", 404


def main():
    global predictor
    
    parser = argparse.ArgumentParser(description='启动图像标签预测网页应用')
    parser.add_argument('--db', type=str, default='data.db', help='SQLite数据库路径')
    parser.add_argument('--model', type=str, required=True, help='训练好的模型路径')
    parser.add_argument('--threshold', type=float, default=0.7, help='标签预测的置信度阈值')
    parser.add_argument('--model_type', type=str, default='resnet50', choices=['resnet50', 'resnet101'],
                        help='使用的模型类型: resnet50 或 resnet101')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务器主机')
    parser.add_argument('--port', type=int, default=5000, help='服务器端口')
    
    args = parser.parse_args()
    
    # 初始化预测器
    try:
        predictor = ImageTagPredictor(args.db, args.model, args.threshold, args.model_type)
        
        # 检查数据库表是否存在，如果不存在则创建
        predictor.cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data BLOB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        predictor.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        
        predictor.cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (image_id, tag_id),
                FOREIGN KEY (image_id) REFERENCES images (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id)
            )
        """)
        
        predictor.conn.commit()
        
        # 启动Flask应用
        print(f"服务器启动在 http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)
        
    except Exception as e:
        print(f"启动服务器时出错: {e}")
    finally:
        if predictor:
            predictor.close()


if __name__ == "__main__":
    main()