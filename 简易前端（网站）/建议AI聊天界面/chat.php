<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
set_time_limit(0);

// 设置 SSE 相关头信息，确保浏览器不缓存、持续连接
header("Content-Type: text/event-stream");
header("Cache-Control: no-cache");
header("Connection: keep-alive");

// 获取用户输入
$user_message = isset($_POST['message']) ? trim($_POST['message']) : '';
if (empty($user_message)) {
    echo "data: " . json_encode(["error" => "未收到有效的消息"]) . "\n\n";
    exit;
}

// OpenAI API 配置
$api_key = "YOUR_OPENAI_API_KEY"; // 请替换为你的 API Key
$url = "http://127.0.0.1:8000/v1/chat/completions";

// 请求数据，开启流式返回
$data = [
    "model"       => "gpt-4",
    "messages"    => [["role" => "user", "content" => $user_message]],
    "temperature" => 0.7,
    "stream"      => true
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    "Content-Type: application/json",
    "Authorization: Bearer " . $api_key,
]);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

// 使用回调函数逐块输出接收到的数据，并立即 flush 到前端
curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $chunk) {
    echo $chunk;
    // 立即刷新输出缓冲区
    if (ob_get_length()) {
        @ob_flush();
    }
    flush();
    return strlen($chunk);
});

// 执行请求
$result = curl_exec($ch);
if ($result === false) {
    $error = curl_error($ch);
    echo "data: " . json_encode(["error" => "无法连接到 GPT 服务器: $error"]) . "\n\n";
}
curl_close($ch);
?>
