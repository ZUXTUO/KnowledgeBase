using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using Microsoft.ML.OnnxRuntime;
using Microsoft.ML.OnnxRuntime.Tensors;

namespace ImageClassifier
{
    class Program
    {
        // 配置参数
        private const string OnnxModelPath = "model/best_model_fp32.onnx";
        private static readonly string[] ClassNames = { "hate", "like", "verylike" }; // 与训练时的顺序一致
        private const string InputFolder = "input";
        private const string OutputFolder = "output";

        // 归一化参数（与 PyTorch 保持一致）
        private static readonly float[] Mean = { 0.485f, 0.456f, 0.406f };
        private static readonly float[] Std = { 0.229f, 0.224f, 0.225f };

        static void Main(string[] args)
        {
            try
            {
                // 确保输出目录和子目录存在
                EnsureDir(OutputFolder);
                foreach (var cls in ClassNames)
                {
                    EnsureDir(Path.Combine(OutputFolder, cls));
                }

                // 创建 ONNX Runtime 会话
                using (var session = new InferenceSession(OnnxModelPath))
                {
                    // 获取输入和输出节点的名称
                    var inputName = session.InputMetadata.Keys.First();
                    var outputName = session.OutputMetadata.Keys.First();

                    // 处理所有图像文件
                    ProcessImageFiles(session, inputName, outputName);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"程序异常: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }

            Console.WriteLine("处理完成，按任意键退出...");
            Console.ReadKey();
        }

        /// <summary>
        /// 处理所有图像文件
        /// </summary>
        private static void ProcessImageFiles(InferenceSession session, string inputName, string outputName)
        {
            // 获取所有图像文件
            var imageFiles = Directory.EnumerateFiles(InputFolder, "*.*", SearchOption.AllDirectories)
                .Where(IsImageFile)
                .ToList();

            Console.WriteLine($"找到 {imageFiles.Count} 个图像文件");

            foreach (var filePath in imageFiles)
            {
                var fileName = Path.GetFileName(filePath);
                try
                {
                    // 读取图像为字节数组
                    byte[] imageBytes = File.ReadAllBytes(filePath);

                    // 预处理图像
                    var inputTensor = PreprocessImage(imageBytes);

                    // 运行推理
                    var inputs = new List<NamedOnnxValue>
                    {
                        NamedOnnxValue.CreateFromTensor(inputName, inputTensor)
                    };

                    using (var results = session.Run(inputs))
                    {
                        // 获取输出并转换为数组
                        var outputTensor = results.First().AsTensor<float>();
                        var logits = outputTensor.ToArray();

                        // 计算 softmax - 与 Python 匹配精确实现
                        var maxLogit = logits.Max();
                        var exp = logits.Select(x => (float)Math.Exp(x - maxLogit)).ToArray();
                        var sumExp = exp.Sum();
                        var probs = exp.Select(x => x / sumExp).ToArray();

                        // 获取预测结果
                        var predIdx = Array.IndexOf(probs, probs.Max());
                        var className = ClassNames[predIdx];
                        var confidence = probs[predIdx];

                        Console.WriteLine($"图像: {fileName} 预测为 {className} (置信度: {confidence:F2})");

                        // 复制到对应类别文件夹
                        var destPath = Path.Combine(OutputFolder, className, fileName);
                        File.Copy(filePath, destPath, true);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"处理 {fileName} 时出错: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// 确保目录存在
        /// </summary>
        private static void EnsureDir(string directory)
        {
            if (!Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }

        /// <summary>
        /// 判断文件是否为图像文件
        /// </summary>
        private static bool IsImageFile(string filePath)
        {
            string ext = Path.GetExtension(filePath).ToLowerInvariant();
            return ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".bmp" || ext == ".gif";
        }

        /// <summary>
        /// 预处理图像：精确匹配 Python 的 torchvision transforms
        /// </summary>
        private static DenseTensor<float> PreprocessImage(byte[] imageBytes)
        {
            using (var memoryStream = new MemoryStream(imageBytes))
            using (var originalImage = Image.FromStream(memoryStream))
            {
                // 步骤 1: Resize 到 256x256 - 保持宽高比
                var resizedImage = ResizeWithAspectRatio(originalImage, 256);

                // 步骤 2: 中心裁剪到 224x224
                var croppedImage = CenterCrop(resizedImage, 224, 224);

                // 步骤 3: 转换为 tensor 并应用归一化
                return ImageToTensor(croppedImage);
            }
        }

        /// <summary>
        /// 保持宽高比调整图像大小
        /// </summary>
        private static Bitmap ResizeWithAspectRatio(Image image, int targetSize)
        {
            // 计算新的宽高，保持宽高比
            float ratio = Math.Max((float)image.Width / targetSize, (float)image.Height / targetSize);
            int newWidth = (int)(image.Width / ratio);
            int newHeight = (int)(image.Height / ratio);

            // 确保短边至少为 targetSize
            if (newWidth < targetSize)
            {
                newWidth = targetSize;
                newHeight = (int)(image.Height * ((float)targetSize / image.Width));
            }
            else if (newHeight < targetSize)
            {
                newHeight = targetSize;
                newWidth = (int)(image.Width * ((float)targetSize / image.Height));
            }

            var resizedImage = new Bitmap(newWidth, newHeight);
            using (var graphics = Graphics.FromImage(resizedImage))
            {
                graphics.CompositingQuality = CompositingQuality.HighQuality;
                graphics.InterpolationMode = InterpolationMode.HighQualityBicubic;
                graphics.SmoothingMode = SmoothingMode.HighQuality;
                graphics.DrawImage(image, 0, 0, newWidth, newHeight);
            }
            return resizedImage;
        }

        /// <summary>
        /// 中心裁剪图像
        /// </summary>
        private static Bitmap CenterCrop(Image image, int width, int height)
        {
            int x = (image.Width - width) / 2;
            int y = (image.Height - height) / 2;

            var croppedImage = new Bitmap(width, height);
            using (var graphics = Graphics.FromImage(croppedImage))
            {
                graphics.DrawImage(image, new Rectangle(0, 0, width, height),
                                  new Rectangle(x, y, width, height), GraphicsUnit.Pixel);
            }
            return croppedImage;
        }

        /// <summary>
        /// 将图像转换为张量并应用归一化 - 不使用unsafe代码的实现
        /// </summary>
        private static DenseTensor<float> ImageToTensor(Bitmap image)
        {
            // 创建一个形状为 [1, 3, 224, 224] 的张量
            var tensor = new DenseTensor<float>(new[] { 1, 3, image.Height, image.Width });

            // 使用GetPixel方法处理每个像素
            // 虽然性能不如unsafe代码，但更安全且能实现相同的准确度
            for (int y = 0; y < image.Height; y++)
            {
                for (int x = 0; x < image.Width; x++)
                {
                    Color pixelColor = image.GetPixel(x, y);

                    // 归一化并存储到张量 (使用与 PyTorch 相同的均值和标准差)
                    tensor[0, 0, y, x] = (pixelColor.R / 255f - Mean[0]) / Std[0]; // R 通道
                    tensor[0, 1, y, x] = (pixelColor.G / 255f - Mean[1]) / Std[1]; // G 通道
                    tensor[0, 2, y, x] = (pixelColor.B / 255f - Mean[2]) / Std[2]; // B 通道
                }
            }

            return tensor;
        }
    }
}