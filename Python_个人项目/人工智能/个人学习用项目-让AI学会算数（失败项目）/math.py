import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.nn.utils import clip_grad_norm_

# =======================
#   超参数和配置
# =======================
DEVICE            = torch.device("cuda" if torch.cuda.is_available() else "cpu")
HIDDEN_SIZE       = 128         # LSTM 隐状态维度
LR                = 1e-3        # 学习率
BATCH_SIZE        = 256         # 每个 epoch 的训练样本数
SEQ_LEN           = 5           # 每条“思考”序列包含多少道题
ACC_THRESHOLD     = 0.999        # 验证集上准确率 ≥ 阈值时提升难度
VALIDATE_INTERVAL = 10          # 每多少个 epoch 做一次验证
GRAD_CLIP         = 1.0         # 梯度裁剪阈值
MAX_EPOCHS        = 10_000_000  # 最大 epoch 数（无限循环可设置很大）
SAVE_INTERVAL     = 50000         # 每多少 epoch 保存一次模型
SAVE_PATH         = "math.pth"

# =======================
#      模型定义
# =======================
class MathNet(nn.Module):
    """
    LSTM 回归网络，用于预测四则运算结果。
    输入： [batch, seq_len, 6]，特征由 [a, b, op_onehot(4)] 拼成
    输出： [batch, seq_len, 1]，一个实数预测
    """
    def __init__(self):
        super().__init__()
        self.embed = nn.Linear(6, HIDDEN_SIZE)    # 6→hidden
        self.lstm  = nn.LSTM(HIDDEN_SIZE, HIDDEN_SIZE, batch_first=True)
        self.ln    = nn.LayerNorm(HIDDEN_SIZE)
        self.out   = nn.Linear(HIDDEN_SIZE, 1)    # hidden→1
        self._init_weights()

    def _init_weights(self):
        # Xavier 初始化 weight，bias 置 0
        for p in self.parameters():
            if p.dim() >= 2:
                nn.init.xavier_normal_(p)
            else:
                nn.init.constant_(p, 0.0)

    def forward(self, x, hidden=None):
        """
        x: [B, S, 6]
        hidden: LSTM 的 (h, c) 状态
        返回：
          preds: [B, S, 1] 回归预测
          new_hidden: 更新后的 (h, c)
        """
        h        = torch.relu(self.embed(x))   # [B,S,hidden]
        out, hcn = self.lstm(h, hidden)        # [B,S,hidden]
        out      = self.ln(out)
        preds    = self.out(out)               # [B,S,1]
        return preds, hcn

# =======================
#   训练器：分离验证＆动态难度
# =======================
class DynamicTrainer:
    def __init__(self):
        self.device    = DEVICE
        self.model     = MathNet().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=LR)
        self.criterion = nn.MSELoss()
        # 当前题目数值范围从 [1, max_val]
        self.max_val   = 2

    def _make_batch(self):
        """
        随机生成一批训练/验证数据：
          a, b ∼ Uniform(1, max_val)
          op ∼ {0:+,1:-,2:*,3:/}
        返回：
          x: [BATCH_SIZE, SEQ_LEN, 6] 输入特征
          y: [BATCH_SIZE, SEQ_LEN, 1] 真实结果
        """
        B, S = BATCH_SIZE, SEQ_LEN
        # 随机采样 a, b, op
        a  = torch.randint(1, self.max_val+1, (B, S), device=self.device).float()
        b  = torch.randint(1, self.max_val+1, (B, S), device=self.device).float()
        op = torch.randint(0, 4, (B, S), device=self.device)  # 0,1,2,3

        # one-hot 编码 op → [B,S,4]
        op_onehot = torch.nn.functional.one_hot(op, num_classes=4).float()
        # 拼成 [a, b, onehot4] → [B,S,6]
        x = torch.cat([a.unsqueeze(-1), b.unsqueeze(-1), op_onehot], dim=-1)

        # 计算 y：对应的四则运算结果
        # 加：a+b；减：a-b；乘：a*b；整除：floor(a/b)
        with torch.no_grad():
            y = torch.zeros(B, S, device=self.device)
            idx = (op == 0)
            y[idx] = a[idx] + b[idx]
            idx = (op == 1)
            y[idx] = a[idx] - b[idx]
            idx = (op == 2)
            y[idx] = a[idx] * b[idx]
            idx = (op == 3)
            y[idx] = torch.div(a[idx], b[idx], rounding_mode='floor')
            y = y.unsqueeze(-1)  # [B,S,1]
        return x, y

    def train(self):
        """
        主训练循环：
          - 训练：每个 epoch 在一批新数据上更新模型
          - 验证：每 VALIDATE_INTERVAL 轮，用另一批新数据算 val_acc
          - 难度：val_acc ≥ ACC_THRESHOLD 时 max_val += 1
          - 保存：每 SAVE_INTERVAL 轮存一次 checkpoint
        """
        for epoch in range(1, MAX_EPOCHS + 1):
            # —— 1. 训练步骤 —— #
            self.model.train()
            x_train, y_train = self._make_batch()
            preds, _ = self.model(x_train)             # [B,S,1]
            loss = self.criterion(preds, y_train)
            self.optimizer.zero_grad()
            loss.backward()
            clip_grad_norm_(self.model.parameters(), GRAD_CLIP)
            self.optimizer.step()

            # —— 2. 验证步骤 —— #
            if epoch % VALIDATE_INTERVAL == 0:
                self.model.eval()
                x_val, y_val = self._make_batch()      # 新批数据
                with torch.no_grad():
                    preds_val, _ = self.model(x_val)
                    # 四舍五入后比较
                    acc = (preds_val.round() == y_val).float().mean().item()

                # print(f"[Epoch {epoch:04d}] "
                #       f"max_val=1~{self.max_val:<3d}  "
                #       f"TrainLoss={loss.item():.4f}  "
                #       f"ValAcc={acc:.4f}")

                # —— 3. 动态提升难度 —— #
                if acc >= ACC_THRESHOLD:
                    old = self.max_val
                    self.max_val += 1
                    print(f"验证准确率 {acc:.3f} ≥ {ACC_THRESHOLD}，"
                          f"数值范围 → 1~{self.max_val}")

            # —— 4. 定期保存模型 —— #
            if epoch % SAVE_INTERVAL == 0:
                torch.save(self.model.state_dict(), SAVE_PATH)
                # print(f"—— 模型已保存到 {SAVE_PATH} ——")

        # 训练结束，保存最终模型
        torch.save(self.model.state_dict(), SAVE_PATH)
        print(f"训练完成，模型保存在 {SAVE_PATH}")

if __name__ == "__main__":
    trainer = DynamicTrainer()
    trainer.train()
