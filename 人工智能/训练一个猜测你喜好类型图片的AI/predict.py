import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import sys
import os

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
    
    def predict_image(self, image_path):
        """预测单张图片"""
        try:
            image = Image.open(image_path).convert('RGB')
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

def main():
    # 配置参数
    MODEL_PATH = "model/best_model.pth"
    CLASS_NAMES = ["hate", "like", "verylike"]  # 必须与训练时的顺序一致
    
    # 检查参数
    if len(sys.argv) < 2:
        print("使用方法: python predict.py <图片路径>")
        print("示例: python predict.py test.jpg")
        return
    
    img_path = sys.argv[1]
    if not os.path.exists(img_path):
        print(f"错误: 文件 '{img_path}' 不存在")
        return
    
    # 初始化预测器
    predictor = ImagePredictor(MODEL_PATH, CLASS_NAMES)
    
    # 执行预测
    result = predictor.predict_image(img_path)
    if result:
        print("\n预测结果：")
        print(f"分类: {result['class']}")
        print(f"置信度: {result['confidence']:.4f}")
        print("详细概率：")
        for cls, prob in result['probabilities'].items():
            print(f"{cls}: {prob:.4f}")
        print("-----------------------")

if __name__ == "__main__":
    main()