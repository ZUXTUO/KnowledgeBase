# export_fp32_onnx.py

import torch
from torchvision import models
import torch.nn as nn

MODEL_PATH = "model/best_model.pth"
ONNX_PATH  = "model/best_model_fp32.onnx"
CLASS_NUM  = 3  # hate, like, verylike

# 1) 加载模型结构并载入权重
#    注意这里用 weights=None 代替过时的 pretrained 参数
model = models.efficientnet_b3(weights=None)
num_ftrs = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_ftrs, CLASS_NUM)

# 建议开启 weights_only=True，以避免 pickle 安全警告（PyTorch ≥1.13）
state = torch.load(MODEL_PATH, map_location="cpu", weights_only=True)
model.load_state_dict(state["model_state_dict"])
model.eval()

# 2) 导出为 ONNX（FP32）
dummy_input = torch.randn(1, 3, 224, 224, device="cpu")
torch.onnx.export(
    model,
    dummy_input,
    ONNX_PATH,
    input_names=["input"],
    output_names=["output"],
    opset_version=13,            # 推荐使用 ≥13
    do_constant_folding=True,    # 开启常量折叠优化
    dynamic_axes={               # 支持动态 batch size
        "input":  {0: "batch_size"},
        "output": {0: "batch_size"}
    }
)

print(f"ONNX model (FP32) has been saved to: {ONNX_PATH}")
