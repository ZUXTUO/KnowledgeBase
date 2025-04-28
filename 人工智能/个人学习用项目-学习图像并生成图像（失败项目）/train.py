import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets, utils
from torch.utils.data import DataLoader
import os
import time

# 配置参数
BATCH_SIZE = 16
IMG_SIZE = 512
LATENT_DIM = 256
NUM_EPOCHS = 100
LEARNING_RATE = 0.0002
DATA_PATH = "data"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 数据预处理
transform = transforms.Compose([
    transforms.Resize(IMG_SIZE),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# 加载数据集
dataset = datasets.ImageFolder(root=DATA_PATH, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
print(f"Loaded {len(dataset)} images from {DATA_PATH}")

# 定义生成器 (添加spectral normalization和self-attention)
class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        
        def conv_block(in_c, out_c, k, s, p, bn=True):
            layers = [nn.ConvTranspose2d(in_c, out_c, k, s, p, bias=False)]
            if bn: layers.append(nn.BatchNorm2d(out_c))
            layers.append(nn.ReLU(True))
            return nn.Sequential(*layers)
        
        self.main = nn.Sequential(
            # 初始全连接层
            nn.Linear(LATENT_DIM, 512 * 4 * 4),
            nn.Unflatten(1, (512, 4, 4)),
            
            # 上采样块
            conv_block(512, 256, 4, 2, 1),
            conv_block(256, 128, 4, 2, 1),
            conv_block(128, 64, 4, 2, 1),
            conv_block(64, 32, 4, 2, 1),
            conv_block(32, 16, 4, 2, 1),
            conv_block(16, 8, 4, 2, 1),
            
            # 输出层
            nn.ConvTranspose2d(8, 3, 4, 2, 1, bias=False),
            nn.Tanh()
        )
        
    def forward(self, x):
        return self.main(x)

# 定义判别器 (添加spectral normalization)
class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        
        def conv_block(in_c, out_c, k, s, p, bn=True):
            layers = [nn.utils.spectral_norm(nn.Conv2d(in_c, out_c, k, s, p, bias=False))]
            if bn: layers.append(nn.BatchNorm2d(out_c))
            layers.append(nn.LeakyReLU(0.2, True))
            return nn.Sequential(*layers)
        
        self.main = nn.Sequential(
            # 输入: 3x512x512
            conv_block(3, 8, 4, 2, 1, bn=False),
            conv_block(8, 16, 4, 2, 1),
            conv_block(16, 32, 4, 2, 1),
            conv_block(32, 64, 4, 2, 1),
            conv_block(64, 128, 4, 2, 1),
            conv_block(128, 256, 4, 2, 1),
            conv_block(256, 512, 4, 2, 1),
            
            # 输出层
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.utils.spectral_norm(nn.Linear(512, 1)),
        )
        
    def forward(self, x):
        return self.main(x)

# 初始化模型
generator = Generator().to(DEVICE)
discriminator = Discriminator().to(DEVICE)

# 定义损失函数和优化器
criterion = nn.BCEWithLogitsLoss()  # 改用BCEWithLogitsLoss
optimizer_G = optim.Adam(generator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))
optimizer_D = optim.Adam(discriminator.parameters(), lr=LEARNING_RATE, betas=(0.5, 0.999))

# 训练循环
for epoch in range(NUM_EPOCHS):
    start_time = time.time()
    
    for i, (real_images, _) in enumerate(dataloader):
        real_images = real_images.to(DEVICE)
        batch_size = real_images.size(0)
        
        # 训练判别器
        optimizer_D.zero_grad()
        
        # 真实图像损失
        real_pred = discriminator(real_images)
        real_loss = criterion(real_pred, torch.ones(batch_size, 1, device=DEVICE))
        
        # 生成假图像
        z = torch.randn(batch_size, LATENT_DIM, device=DEVICE)
        fake_images = generator(z)
        
        # 假图像损失 (使用detach避免生成器更新)
        fake_pred = discriminator(fake_images.detach())
        fake_loss = criterion(fake_pred, torch.zeros(batch_size, 1, device=DEVICE))
        
        d_loss = (real_loss + fake_loss) / 2
        d_loss.backward()
        optimizer_D.step()
        
        # 训练生成器 (每2步训练一次生成器)
        if i % 2 == 0:
            optimizer_G.zero_grad()
            gen_pred = discriminator(fake_images)
            g_loss = criterion(gen_pred, torch.ones(batch_size, 1, device=DEVICE))
            g_loss.backward()
            optimizer_G.step()
        
        # 打印训练状态
        if i % 50 == 0:
            print(f"[Epoch {epoch}/{NUM_EPOCHS}] [Batch {i}/{len(dataloader)}] "
                  f"D_loss: {d_loss.item():.4f} G_loss: {g_loss.item():.4f}")
    
    # 保存检查点
    if epoch % 5 == 0:
        # 生成示例图像 (使用更大的batch_size避免BatchNorm问题)
        with torch.no_grad():
            generator.eval()
            z = torch.randn(16, LATENT_DIM, device=DEVICE)
            samples = generator(z).cpu()
            samples = (samples * 0.5 + 0.5).clamp(0, 1)
            utils.save_image(samples, f"samples_epoch_{epoch}.png", nrow=4)
            generator.train()
        
        # 保存模型
        torch.save({
            'epoch': epoch,
            'generator': generator.state_dict(),
            'discriminator': discriminator.state_dict(),
            'optimizer_G': optimizer_G.state_dict(),
            'optimizer_D': optimizer_D.state_dict(),
        }, f"checkpoint_epoch_{epoch}.pth")
    
    epoch_time = time.time() - start_time
    print(f"Epoch {epoch} completed in {epoch_time:.2f}s")

print("Training complete!")