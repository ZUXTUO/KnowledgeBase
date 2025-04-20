<?php
$videoFolder = 'LiveVideo/';

$videos = [];
$files = scandir($videoFolder);
foreach ($files as $file) {
  if ($file !== '.' && $file !== '..') {
    $videos[] = $videoFolder . $file;
  }
}

header('Content-Type: application/json');
echo json_encode($videos);
?>