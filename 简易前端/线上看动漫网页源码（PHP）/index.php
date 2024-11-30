<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebAnime</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 20px;
        }

        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }

        .video-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin: -5px;
        }

        .video-item {
            width: 220px;
            margin: 5px;
            padding: 10px;
            background-color: #fff;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            border-radius: 4px;
            text-align: center;
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .video-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }

        .video-thumbnail {
            width: 100%;
            height: auto;
            border-radius: 4px;
        }

        .video-title {
            font-size: 16px;
            margin-top: 10px;
        }

        .video-link {
            display: block;
            color: #333;
            font-size: 14px;
            margin-top: 5px;
            text-decoration: none;
            border: 1px solid #ccc;
            padding: 5px;
            border-radius: 4px;
            transition: background-color 0.3s;
        }

        .video-link:hover {
            color: #007bff;
            background-color: #f0f0f0;
        }

        /* 移动设备适配 */
        @media only screen and (max-width: 600px) {
            .video-item {
                width: 100%;
            }
        }

        /* 搜索框样式 */
        .search-container {
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap;
        }

        .search-input {
            flex: 1;
            padding: 10px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 4px;
            outline: none;
        }

        .search-button {
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 4px;
            background-color: #007bff;
            color: #fff;
            border: none;
            cursor: pointer;
            outline: none;
        }

        /* 响应式样式 */
    </style>
</head>
<body>
    <h1>WebAnime</h1>
	
	<!-- 搜索框 -->
    <div class="search-container">
        <input type="text" id="search-input" class="search-input" placeholder="Videos Name">
        <button id="search-button" class="search-button">Search</button>
    </div>
	
    <div class="video-container">
<?php
$videosFolder = 'Videos';
if (file_exists($videosFolder) && is_dir($videosFolder)) {
    $directory = opendir($videosFolder);
    $videos = array();
    while (($file = readdir($directory)) !== false) {
        if ($file != '.' && $file != '..') {
            if (is_dir($videosFolder . '/' . $file)) {
                $videoPath = $videosFolder . '/' . $file;
                $videoTitle = $file;
                $thumbnailFolder = 'Img';
                $thumbnailFiles = scandir($thumbnailFolder);
                $thumbnailFiles = array_diff($thumbnailFiles, array('.', '..'));
                $randomThumbnail = $thumbnailFolder . '/' . $thumbnailFiles[array_rand($thumbnailFiles)];
                $thumbnailPath = $randomThumbnail;
                
                $videos[] = array(
                    'videoPath' => $videoPath,
                    'videoTitle' => $videoTitle,
                    'thumbnailPath' => $thumbnailPath
                );
            }
        }
    }
    usort($videos, function ($a, $b) {
        return strnatcasecmp($a['videoTitle'], $b['videoTitle']);
    });
    foreach ($videos as $video) {
        echo '<div class="video-item">';
        echo '<img class="video-thumbnail" src="' . $video['thumbnailPath'] . '" alt="VideoImage"><br>';
        echo '<span class="video-title">' . $video['videoTitle'] . '</span><br>';
        $subDirectory = opendir($video['videoPath']);
        while (($subFile = readdir($subDirectory)) !== false) {
            if ($subFile != '.' && $subFile != '..' && !is_dir($video['videoPath'] . '/' . $subFile)) {
                echo '<a class="video-link" href="play.php?video=' . $video['videoPath'] . '/' . $subFile . '">' . $subFile . '</a><br>';
            }
        }
        closedir($subDirectory);
        echo '</div>';
    }
    closedir($directory);
}
?>
    </div>

    <script>
        function playVideo(videoPath) {
            window.location.href = 'play.php?video=' + videoPath;
        }
    </script>
	
	    <script>
        document.getElementById('search-button').addEventListener('click', function() {
            var searchQuery = document.getElementById('search-input').value.toLowerCase();
            var videoItems = document.getElementsByClassName('video-item');
            for (var i = 0; i < videoItems.length; i++) {
                var videoTitle = videoItems[i].getElementsByClassName('video-title')[0].innerText.toLowerCase();
                if (videoTitle.includes(searchQuery)) {
                    videoItems[i].style.display = 'block';
                } else {
                    videoItems[i].style.display = 'none';
                }
            }
        });
    </script>
</body>
</html>