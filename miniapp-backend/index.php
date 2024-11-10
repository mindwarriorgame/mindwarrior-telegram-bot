<?php
header('Access-Control-Allow-Origin: *');
$data = json_decode(file_get_contents('php://input'), true);
$userData = $_GET['data'];
$queryId = $_GET['query_id'];

$tokens = [
    "test" => "telegram-token-1",
    "prod" => "telegram-token-2"
];

$botToken = $tokens[$_GET['env']];

if (empty($botToken)) {
    echo "Unknown env " . $_GET['env'];
    exit(0);
}

$telegramApiUrl = "https://api.telegram.org/bot$botToken/answerWebAppQuery";

$lang = [
    'en' => 'Submitting data... ',
    'ru' => 'Отправляем... ',
    'es' => 'Enviando datos... ',
    'fr' => 'Soumission des données... ',
    'de' => 'Daten werden übermittelt... ',
];


function checkStringFormat($str) {
    // Patterns for each shape
    $patterns = [
        'reviewed' => '/^reviewed_at:__timestamp__;next_review:.*$/',
        'start_game' => '/^start_game/',
        'letter_updated' => '/^letter_updated$/',
        'formula_updated' => '/^formula_updated$/',
        'set_difficulty:POSITIVE_INT_NUMBER' => '/^set_difficulty:\d+;next_review:.*$/',
        'delete_data_confirmed' => '/^delete_data_confirmed$/',
        'regenerate_achievements_button' => '/^regenerate_achievements_button$/'
    ];

    // Check the string against each pattern
    foreach ($patterns as $pattern) {
        if (preg_match($pattern, $str)) {
            return true;
        }
    }

    return false;
}

if (!checkStringFormat($userData)) {
    echo json_encode(['env' => $_GET['env'], 'status' => 400, 'response' => 'Invalid data format', 'query_id' => $queryId]);
    exit;
}

$userData = str_replace('__timestamp__', time(), $userData);

$postFields = [
    'web_app_query_id' => $queryId,
    'result' => json_encode([
        'type' => 'article',
        'id' => uniqid(),
        'title' => 'Data Transfer',
        'input_message_content' => [
            'message_text' => $lang[$_GET['lang_code']] . $userData,
            "parse_mode" => "HTML"
        ]
    ]),
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $telegramApiUrl);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postFields);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$httpcode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

echo json_encode(['env' => $_GET['env'], 'status' => $httpcode, 'response' => $response, 'query_id' => $queryId, 'data' => $userData]);

