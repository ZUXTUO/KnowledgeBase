import os
import shutil
import io
from PIL import Image
import numpy as np
import onnxruntime as ort
from torchvision import transforms

# 配置参数
ONNX_MODEL_PATH = "model/best_model_fp32.onnx"
CLASS_NAMES = ["hate", "like", "verylike"]  # 与训练时的顺序一致
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# 定义图片预处理流程，与 PyTorch 导出时保持一致
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    tensor = transform(image).unsqueeze(0)  # shape: [1, 3, 224, 224]
    return tensor.numpy().astype(np.float32)


def main():
    # 确保输出目录和子目录存在
    ensure_dir(OUTPUT_FOLDER)
    for cls in CLASS_NAMES:
        ensure_dir(os.path.join(OUTPUT_FOLDER, cls))

    # 创建 ONNX Runtime 会话
    session = ort.InferenceSession(ONNX_MODEL_PATH)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    # 遍历所有图片文件
    for root, _, files in os.walk(INPUT_FOLDER):
        for file in files:
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                print(f"Skipping non-image file: {file}")
                continue

            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                image_bytes = f.read()

            try:
                # 预处理并推理
                input_array = preprocess_image(image_bytes)
                outputs = session.run([output_name], {input_name: input_array})
                logits = outputs[0].squeeze(0)

                # 计算 softmax
                exp = np.exp(logits - np.max(logits))
                probs = exp / exp.sum()
                pred_idx = np.argmax(probs)
                class_name = CLASS_NAMES[pred_idx]
                confidence = probs[pred_idx]

                print(f"Image: {file} predicted as {class_name} (confidence: {confidence:.2f})")

                # 复制到对应类别文件夹
                dest = os.path.join(OUTPUT_FOLDER, class_name, file)
                shutil.copy(file_path, dest)

            except Exception as e:
                print(f"Error processing {file}: {e}")

if __name__ == '__main__':
    main()
