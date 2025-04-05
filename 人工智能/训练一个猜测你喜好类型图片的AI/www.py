import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
from flask import Flask, render_template, request, jsonify
import io

app = Flask(__name__)

# 配置参数
MODEL_PATH = "model/best_model.pth"
CLASS_NAMES = ["hate", "like", "verylike"]  # 必须与训练时的顺序一致

class ImagePredictor:
    def __init__(self, model_path, class_names):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = class_names
        self.model = self.load_model(model_path)
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self, model_path):
        """加载预训练模型"""
        model = models.efficientnet_b3(pretrained=False)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(num_ftrs, len(self.class_names))
        
        # 加载训练好的权重
        state_dict = torch.load(model_path, map_location=self.device)
        model.load_state_dict(state_dict['model_state_dict'])
        model = model.to(self.device)
        model.eval()
        return model
    
    def predict_image(self, image_bytes):
        """预测图片"""
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            input_tensor = self.transform(image)
            input_batch = input_tensor.unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(input_batch)
            
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, pred_idx = torch.max(probabilities, 0)
            
            return {
                "class": self.class_names[pred_idx.item()],
                "confidence": confidence.item(),
                "probabilities": {
                    cls_name: prob.item() for cls_name, prob in zip(
                        self.class_names, probabilities.cpu().numpy()
                    )
                }
            }
        except Exception as e:
            print(f"预测出错: {str(e)}")
            return None

# 初始化预测器
predictor = ImagePredictor(MODEL_PATH, CLASS_NAMES)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        image_bytes = file.read()
        result = predictor.predict_image(image_bytes)
        if result:
            return jsonify(result)
        else:
            return jsonify({'error': 'Prediction failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)