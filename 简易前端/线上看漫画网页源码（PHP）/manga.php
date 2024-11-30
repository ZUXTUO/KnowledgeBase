<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Manga</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: black;
        }

        .manga-images {
            padding: 0;
            margin: 0;
        }

        .manga-images img {
            display: block;
            width: 100%;
            height: auto;
            margin: 0;
            padding: 0;
        }
    </style>
</head>
<body>
    <div class="manga-images">
        <?php
            $mangaPath = 'manga';
            $folder = $_GET['folder'];
            if (!empty($folder)) {
                $folderPath = $mangaPath . '/' . $folder;
                if (is_dir($folderPath)) {
                    $images = glob($folderPath . '/*.*');
                    foreach ($images as $image) {
                        echo '<img src="' . $image . '" alt="Manga Image">';
                    }
                }
            }
        ?>
    </div>
</body>
</html>