<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
set_time_limit(0);

header("Content-Type: text/event-stream");
header("Cache-Control: no-cache");
header("Connection: keep-alive");

$user_message = isset($_POST['message']) ? trim($_POST['message']) : '';

if (empty($user_message)) {
    echo "data: " . json_encode(["error" => "未收到有效的消息"]) . "\n\n";
    exit;
}

// Stable Diffusion API 地址
$url = "http://127.0.0.1:7860/sdapi/v1/txt2img";

$data = [
    "prompt" => $user_message,
    "steps" => 20, // 默认步数
    "width" => 512,
    "height" => 512,
    "sampler_name" => "Euler a", // 默认采样器
    "n_iter" => 1, // 生成一张图片
    "batch_size" => 1 // 每批次一张图片
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "Accept: application/json",
]);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); // 获取返回内容

$result = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($result === false) {
    $error = curl_error($ch);
    echo "data: " . json_encode(["error" => "无法连接到 Stable Diffusion 服务器: $error"]) . "\n\n";
} else if ($http_code != 200) {
    // 尝试解析错误信息
    $error_data = json_decode($result, true);
    $error_message = isset($error_data['detail']) ? $error_data['detail'] : "未知错误";
    echo "data: " . json_encode(["error" => "Stable Diffusion API 错误 ({$http_code}): {$error_message}"]) . "\n\n";
} else {
    $response_data = json_decode($result, true);
    if (isset($response_data['images']) && count($response_data['images']) > 0) {
        $base64_image = $response_data['images'][0];
        echo "data: " . json_encode(["image" => $base64_image]) . "\n\n";
    } else {
        echo "data: " . json_encode(["error" => "Stable Diffusion 未返回图像。"]) . "\n\n";
    }
}
curl_close($ch);
?>
