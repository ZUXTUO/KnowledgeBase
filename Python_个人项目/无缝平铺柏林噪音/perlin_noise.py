import numpy as np
import matplotlib.pyplot as plt

def generate_seamless_perlin_noise(shape, res):
    """
    生成可无缝平铺的2D Perlin噪声。
    
    Args:
        shape: 输出图像的尺寸 (h, w)
        res: 网格的分辨率 (res_x, res_y)，必须是形状的约数
    """
    def f(t):
        return 6*t**5 - 15*t**4 + 10*t**3

    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])

    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    
    # 生成梯度向量
    # 为了实现无缝平铺，我们在查找梯度时使用取模运算，
    # 但在生成梯度网格时，我们只需要生成一个周期的梯度即可。
    theta = 2 * np.pi * np.random.rand(res[0] + 1, res[1] + 1)
    gradients = np.stack((np.cos(theta), np.sin(theta)), axis=2)
    
    # 关键点：强制边缘梯度一致以实现平铺
    # 让最后一行等于第一行，最后一列等于第一列
    gradients[-1, :] = gradients[0, :]
    gradients[:, -1] = gradients[:, 0]

    g00 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g10 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    g01 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    g11 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)

    n00 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]  )) * g00, 2)
    n10 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]  )) * g10, 2)
    n01 = np.sum(np.dstack((grid[:,:,0]  , grid[:,:,1]-1)) * g01, 2)
    n11 = np.sum(np.dstack((grid[:,:,0]-1, grid[:,:,1]-1)) * g11, 2)

    t = f(grid)
    n0 = n00 * (1 - t[:,:,0]) + n10 * t[:,:,0]
    n1 = n01 * (1 - t[:,:,0]) + n11 * t[:,:,0]
    
    return np.sqrt(2) * ((1 - t[:,:,1]) * n0 + t[:,:,1] * n1)

def generate_seamless_fractal_noise(shape, res, octaves=5, persistence=0.5, lacunarity=2):
    """
    生成可无缝平铺的分形噪声（叠加多层Perlin噪声）。
    """
    noise = np.zeros(shape)
    frequency = 1
    amplitude = 1
    max_value = 0
    
    for _ in range(octaves):
        # 每一层的分辨率必须是整数
        current_res = (res[0] * frequency, res[1] * frequency)
        
        # 生成该层的噪声
        chunk = generate_seamless_perlin_noise(shape, current_res)
        noise += chunk * amplitude
        
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity
        
    return noise / max_value

# --- 主程序 ---
if __name__ == "__main__":
    np.random.seed(42) # 固定种子以便复现
    
    img_size = (512, 512) # 图像大小
    grid_res = (4, 4)     # 基础网格大小 (越小云团越大)

    print("正在生成无缝 Perlin 噪声...")
    # 1. 生成单层无缝 Perlin 噪声
    simple_noise = generate_seamless_perlin_noise(img_size, grid_res)
    
    print("正在生成无缝 Fractal 噪声 (细节更多)...")
    # 2. 生成多层分形无缝噪声 (细节更多，更像云层/地形)
    fractal_noise = generate_seamless_fractal_noise(img_size, grid_res, octaves=4, persistence=0.5)

    # --- 保存和可视化 ---
    
    # 保存功能函数
    def save_noise_img(data, filename):
        plt.figure(figsize=(5, 5))
        plt.imshow(data, cmap='gray', interpolation='lanczos')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close()
        print(f"已保存: {filename}")

    save_noise_img(simple_noise, 'seamless_perlin.png')
    save_noise_img(fractal_noise, 'seamless_fractal.png')

    # --- 验证平铺效果 ---
    # 生成一个 2x2 的拼接图来直观展示无缝效果
    print("正在生成 2x2 验证图...")
    tiled_data = np.concatenate([fractal_noise, fractal_noise], axis=1) # 左右拼接
    tiled_data = np.concatenate([tiled_data, tiled_data], axis=0)       # 上下拼接
    
    plt.figure(figsize=(8, 8))
    plt.title("2x2 Tiling Check (If you see seams, it failed. If smooth, it works!)")
    plt.imshow(tiled_data, cmap='gray', interpolation='lanczos')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('tiling_verification.png')
    plt.close()
    
    print("全部完成。请检查 tiling_verification.png 以确认无缝效果。")