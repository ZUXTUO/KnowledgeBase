<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
set_time_limit(0);

header("Content-Type: text/event-stream");
header("Cache-Control: no-cache");
header("Connection: keep-alive");

$user_message = isset($_POST['message']) ? trim($_POST['message']) : '';
$enable_context_memory = isset($_POST['enableContextMemory']) && $_POST['enableContextMemory'] === 'true';
$context_history = isset($_POST['contextHistory']) ? $_POST['contextHistory'] : '';
$is_first_message = isset($_POST['firstMessage']) && $_POST['firstMessage'] === 'true';

if (empty($user_message)) {
    echo "data: " . json_encode(["error" => "未收到有效的消息"]) . "\n\n";
    exit;
}

$api_key = "YOUR_OPENAI_API_KEY";
$url = "http://127.0.0.1:8000/v1/chat/completions";

$message_to_send = "";

if ($is_first_message) {
    $person_text = @file_get_contents('person.txt');
    if ($person_text !== false && trim($person_text) !== "") {
        $message_to_send .= "[Persona Context]\n" . trim($person_text) . "\n\n";
    }
}

if ($enable_context_memory && !empty($context_history)) {
    $message_to_send .= $context_history . "\nUser: " . $user_message;
} else {
    $message_to_send .= "User: " . $user_message;
}

function stripPunctuation($str) {
    return preg_replace('/[^\p{L}\p{N}\s]/u', '', $str);
}

function levenshtein_php($a, $b) {
    $len_a = mb_strlen($a, 'UTF-8');
    $len_b = mb_strlen($b, 'UTF-8');

    $dp = array_fill(0, $len_a + 1, array_fill(0, $len_b + 1, 0));

    for ($i = 0; $i <= $len_a; $i++) {
        $dp[$i][0] = $i;
    }
    for ($j = 0; $j <= $len_b; $j++) {
        $dp[0][$j] = $j;
    }

    for ($i = 1; $i <= $len_a; $i++) {
        for ($j = 1; $j <= $len_b; $j++) {
            $cost = (mb_substr($a, $i - 1, 1, 'UTF-8') == mb_substr($b, $j - 1, 1, 'UTF-8')) ? 0 : 1;
            $dp[$i][$j] = min(
                $dp[$i - 1][$j] + 1,
                $dp[$i][$j - 1] + 1,
                $dp[$i - 1][$j - 1] + $cost
            );
        }
    }
    return $dp[$len_a][$len_b];
}


function similarity_php($a, $b) {
    $a = stripPunctuation(mb_strtolower($a, 'UTF-8'));
    $b = stripPunctuation(mb_strtolower($b, 'UTF-8'));
    $distance = levenshtein_php($a, $b);
    $maxLen = max(mb_strlen($a, 'UTF-8'), mb_strlen($b, 'UTF-8'));
    if ($maxLen === 0) return 1;
    return 1 - $distance / $maxLen;
}

$time_questions = [
    "现在是几点", "现在是什么时间", "当前时间", "现在时间", "现在几点了",
    "几点钟了", "几点了", "现在是早上吗", "现在是早晨吗", "现在是中午吗",
    "现在是晚上吗", "现在是夜晚吗", "现在是下午吗",
];

$is_time_question = false;
foreach ($time_questions as $question) {
    if (similarity_php($user_message, $question) >= 0.6) {
        $is_time_question = true;
        break;
    }
}

if ($is_time_question) {
    date_default_timezone_set('Asia/Shanghai');
    $now_str = date('Y-m-d H:i:s');
    $message_to_send .= "\n[这是目前的系统时间，你可以告诉我这个时间: " . $now_str . "]";
}

$reference_data = [];
$data_jsonl_content = @file_get_contents('data.jsonl');
if ($data_jsonl_content !== false) {
    $lines = explode("\n", trim($data_jsonl_content));
    foreach ($lines as $line) {
        $line = trim($line);
        if (empty($line)) continue;
        $json_obj = json_decode($line, true);
        if ($json_obj && isset($json_obj['text'])) {
            $parts = explode("\n\n", $json_obj['text'], 2);
            if (count($parts) >= 2) {
                $user_part = preg_replace('/^User:\s*/i', '', $parts[0]);
                $assistant_part = preg_replace('/^Assistant:\s*/i', '', $parts[1]);
                $reference_data[] = ['user' => $user_part, 'assistant' => $assistant_part];
            }
        }
    }
}

$best_match = null;
$best_sim = 0;
if (!empty($reference_data)) {
    foreach ($reference_data as $ref) {
        $sim_user = similarity_php($user_message, $ref['user']);
        if ($sim_user > $best_sim) {
            $best_sim = $sim_user;
            $best_match = $ref;
        }
    }
}

if ($best_sim >= 0.85 && $best_match) {
    $message_to_send .= "\n[Knowledge Base Match - High Confidence]\nQuestion: " . $best_match['user'] . "\nAnswer: " . $best_match['assistant'] . "\n(Use this information to formulate your response, but do not directly copy the answer unless it's a perfect fit for the user's query style.)";
}

$navigation_regex = '/(带我去|导航到|怎么去)([\s\S]+)/iu';
if (preg_match($navigation_regex, $user_message, $nav_matches)) {
    $location = trim(preg_replace('/[。！？，、；：？]$/u', '', $nav_matches[2]));
    if (!empty($location)) {
        $encoded_location = urlencode($location);
        $message_to_send .= "\n[Navigation Request]\nLocation: {$location}\n(Generate a map search URL like: https://www.amap.com/search?query={$encoded_location} or similar for other map services if appropriate. Present it as a direct link.)";
    }
}

$data = [
    "model"       => "gpt-4",
    "messages"    => [["role" => "user", "content" => $message_to_send]],
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

curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $chunk) {
    echo $chunk;
    if (ob_get_length()) {
        @ob_flush();
    }
    flush();
    return strlen($chunk);
});

$result = curl_exec($ch);
if ($result === false) {
    $error = curl_error($ch);
    echo "data: " . json_encode(["error" => "无法连接到 GPT 服务器: $error"]) . "\n\n";
}
curl_close($ch);
?>