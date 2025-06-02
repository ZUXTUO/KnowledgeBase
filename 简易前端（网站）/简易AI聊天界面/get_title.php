<?php
if (isset($_GET['url']) && filter_var($_GET['url'], FILTER_VALIDATE_URL)) {
    $url = $_GET['url'];
    $context = stream_context_create([
        'http' => [
            'timeout' => 3, // 3秒超时
            'header' => "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
        ]
    ]);
    
    // 尝试获取网页内容
    $html = @file_get_contents($url, false, $context);
    
    if ($html) {
        // 提取标题（兼容多语言编码）
        preg_match('/<title>(.*?)<\/title>/i', $html, $matches);
        $title = isset($matches[1]) ? $matches[1] : '';
        
        // 转换编码为UTF-8
        if (!mb_check_encoding($title, 'UTF-8')) {
            $title = mb_convert_encoding($title, 'UTF-8', 'auto');
        }
        
        // 清理标题中的多余空格和换行
        $title = trim(preg_replace('/\s+/', ' ', $title));
        $title = $title ? htmlspecialchars($title) : '无标题';
    } else {
        // 获取失败时显示域名
        $title = parse_url($url, PHP_URL_HOST);
    }
    
    echo json_encode(['title' => $title]);
} else {
    echo json_encode(['error' => '无效的URL']);
}
?>