<!DOCTYPE html>
<html>
<head>
    <title>Video</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: black;
        }

        video {
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
    </style>
</head>
<body>
    <video id="video-player" controls>
        <source src="<?php echo $_GET['video']; ?>" type="video/mp4">
    </video>

    <script>
        var video = document.getElementById('video-player');

        video.addEventListener('ended', videoEnded);

        function videoEnded() {
            video.currentTime = 0;
            video.pause();
        }

        document.addEventListener('click', toggleFullScreen);

        function toggleFullScreen() {
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.mozRequestFullScreen) {
                video.mozRequestFullScreen();
            } else if (video.webkitRequestFullscreen) {
                video.webkitRequestFullscreen();
            } else if (video.msRequestFullscreen) {
                video.msRequestFullscreen();
            }
        }
    </script>
</body>
</html>