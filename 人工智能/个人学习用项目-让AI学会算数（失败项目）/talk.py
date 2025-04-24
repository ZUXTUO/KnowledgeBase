# interactive_math.py

import torch
import torch.nn as nn

# ===========================
#   与训练脚本中完全相同的模型定义
# ===========================
class MathNet(nn.Module):
    """
    LSTM 回归模型：
      输入：[batch, seq=1, feat=6]， feat = [a, b, op_onehot(4)]
      输出：[batch, seq=1, 1]，回归预测结果
    """
    def __init__(self, hidden_size=128):
        super().__init__()
        self.embed = nn.Linear(6, hidden_size)
        self.lstm  = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.ln    = nn.LayerNorm(hidden_size)
        self.out   = nn.Linear(hidden_size, 1)
        self._init_weights()

    def _init_weights(self):
        # Xavier 初始化
        for p in self.parameters():
            if p.dim() >= 2:
                nn.init.xavier_normal_(p)
            else:
                nn.init.constant_(p, 0.0)

    def forward(self, x, hidden=None):
        # x: [B,1,6]
        h     = torch.relu(self.embed(x))
        out, new_h = self.lstm(h, hidden)
        out   = self.ln(out)
        pred  = self.out(out)   # [B,1,1]
        return pred, new_h

# ===========================
#   工具函数：解析用户输入
# ===========================
def parse_input(s: str):
    """
    接受一个包含 “a op b” 的字符串，支持 + - * /
    返回 (a: float, b: float, op_id: int)
    op_id: 0=加，1=减，2=乘，3=整除
    """
    tokens = s.strip().split()
    if len(tokens) != 3:
        raise ValueError("请输入格式：a op b，例如：3 + 5")
    a_str, op, b_str = tokens
    try:
        a = float(a_str)
        b = float(b_str)
    except:
        raise ValueError("a 和 b 必须是数字")
    if op == '+':
        op_id = 0
    elif op == '-':
        op_id = 1
    elif op == '*':
        op_id = 2
    elif op == '/':
        op_id = 3
    else:
        raise ValueError("运算符必须是 + - * / 之一")
    return a, b, op_id

def make_state_tensor(a, b, op_id, device):
    """
    根据 a, b, op_id 构造模型输入张量：
      [1,1,6] = [[a, b, onehot(op_id)]]
    """
    # one-hot op
    one_hot = [0.0]*4
    one_hot[op_id] = 1.0
    feats = [a, b] + one_hot
    arr = torch.tensor([[feats]], dtype=torch.float32, device=device)  # [1,1,6]
    return arr

# ===========================
#   主流程
# ===========================
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 1. 实例化模型并加载已训练好的参数
    model = MathNet(hidden_size=128).to(device)
    checkpoint = "math.pth"
    model.load_state_dict(torch.load(checkpoint, map_location=device))
    model.eval()
    print(f"已加载模型参数：{checkpoint}")
    print("请输入数学问题，例如：3 + 5，或输入 exit 退出。")

    hidden = None  # 保留 LSTM 的思考状态
    while True:
        try:
            s = input(">> ").strip()
        except EOFError:
            break
        if not s or s.lower() in ("exit", "quit"):
            print("拜拜！")
            break

        # 2. 解析输入
        try:
            a, b, op_id = parse_input(s)
        except ValueError as e:
            print("输入错误：", e)
            continue

        # 3. 构造模型输入并前向
        x = make_state_tensor(a, b, op_id, device)
        with torch.no_grad():
            pred, hidden = model(x, hidden)
        # 4. 四舍五入成整数，打印结果
        result = pred.item()
        result_int = int(torch.round(pred).item())
        print(f"模型预测（浮点）: {result:.4f}，四舍五入结果: {result_int}")

if __name__ == "__main__":
    main()
