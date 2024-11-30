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

        .manga-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            grid-gap: 20px;
            padding: 20px;
        }

        .manga-item {
            text-align: center;
        }

        .manga-item img {
            width: 100%;
            height: auto;
        }

        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 20px;
        }

        .pagination a {
            margin: 0 10px;
            text-decoration: none;
            color: white;
        }

        .pagination a:hover {
            text-decoration: underline;
        }

        .pagination .active {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="manga-list">
        <?php
            $mangaPath = 'manga';
            $mangaFolders = scandir($mangaPath);
            $perPage = 20;
            $totalManga = count($mangaFolders) - 2; // 减去.和..两个目录

            // 获取当前页码
            $currentPage = isset($_GET['page']) ? $_GET['page'] : 1;

            // 计算总页数
            $totalPages = ceil($totalManga / $perPage);

            // 确保当前页码在有效范围内
            if ($currentPage < 1) {
                $currentPage = 1;
            } elseif ($currentPage > $totalPages) {
                $currentPage = $totalPages;
            }

            // 计算起始索引和结束索引
            $startIndex = ($currentPage - 1) * $perPage;
            $endIndex = $startIndex + $perPage;

            // 获取当前页需要显示的漫画
            $mangaToShow = array_slice($mangaFolders, 2); // 去除.和..两个目录
            $mangaToShow = array_slice($mangaToShow, $startIndex, $endIndex);

            foreach ($mangaToShow as $folder) {
                $folderPath = $mangaPath . '/' . $folder;
                if (is_dir($folderPath)) {
                    $images = glob($folderPath . '/*.*');
                    if (!empty($images)) {
                        $coverImage = $images[0];
                        echo '<div class="manga-item">';
                        echo '<a href="manga.php?folder=' . urlencode($folder) . '">';
                        echo '<img src="' . $coverImage . '" alt="Cover Image">';
                        echo '</a>';
                        echo '</div>';
                    }
                }
            }
        ?>
    </div>

    <div class="pagination">
        <?php
            // 显示分页链接
            $prevPage = $currentPage - 1;
            $nextPage = $currentPage + 1;

            echo '<a href="?page=1">First</a>';

            if ($prevPage > 1) {
                echo '<a href="?page=' . $prevPage . '">&lt;</a>';
            }

            if ($currentPage > 3) {
                echo '<a href="?page=1">1</a>';
                echo '<span>...</span>';
            }

            if ($currentPage > 2) {
                echo '<a href="?page=' . ($currentPage - 2) . '">' . ($currentPage - 2) . '</a>';
            }

            if ($currentPage > 1) {
                echo '<a href="?page=' . ($currentPage - 1) . '">' . ($currentPage - 1) . '</a>';
            }

            echo '<span class="active">' . $currentPage . '</span>';

            if ($currentPage < $totalPages) {
                echo '<a href="?page=' . ($currentPage + 1) . '">' . ($currentPage + 1) . '</a>';
            }

            if ($currentPage < ($totalPages - 1)) {
                echo '<a href="?page=' . ($currentPage + 2) . '">' . ($currentPage + 2) . '</a>';
            }

        echo '<a href="?page=' . $totalPages . '">Last</a>';
        ?>
    </div>
</body>
</html>