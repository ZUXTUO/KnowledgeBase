import os
import io
import shutil
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models

# 配置参数
MODEL_PATH = "model/best_model.pth"
CLASS_NAMES = ["hate", "like", "verylike"]  # 与训练时的顺序一致
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

class ImagePredictor:
    def __init__(self, model_path, class_names):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = class_names
        self.model = self.load_model(model_path)
        
        # 定义图片预处理流程
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self, model_path):
        """加载预训练模型并加载权重"""
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
        """对单张图片进行预测"""
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
            print(f"Error processing image: {str(e)}")
            return None

def ensure_dir(directory):
    """如果目录不存在则创建目录"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_images(input_folder, output_folder, predictor):
    # 确保输出文件夹及每个类别的子文件夹存在
    ensure_dir(output_folder)
    for cls in CLASS_NAMES:
        ensure_dir(os.path.join(output_folder, cls))
    
    # 遍历输入文件夹中所有文件（支持递归查找）
    for root, _, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            # 根据文件后缀判断是否为图片
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                print(f"Skipping non-image file: {file_path}")
                continue
            
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            
            result = predictor.predict_image(image_bytes)
            if result:
                class_name = result["class"]
                print(f"Image: {file} predicted as {class_name} (confidence: {result['confidence']:.2f})")
                # 将文件复制到对应类别的输出文件夹
                dest_folder = os.path.join(output_folder, class_name)
                dest_path = os.path.join(dest_folder, file)
                shutil.copy(file_path, dest_path)
            else:
                print(f"Prediction failed for image: {file_path}")

def main():
    # 初始化模型预测器（模型加载只执行一次，确保高效）
    predictor = ImagePredictor(MODEL_PATH, CLASS_NAMES)
    # 处理输入文件夹中的所有图片
    process_images(INPUT_FOLDER, OUTPUT_FOLDER, predictor)

if __name__ == '__main__':
    main()
