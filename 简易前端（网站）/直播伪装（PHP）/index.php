<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>直播模仿</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #000;
        }
        #video-container {
            position: relative;
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }
        #video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        #barrage {
            position: absolute;
            bottom: 80px;
            left: 10px;
            color: #fff;
            font-size: 20px;
            white-space: nowrap;
            max-height: calc(100% - 80px);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .input-container {
            position: fixed;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
        }
        #barrage-input {
            padding: 5px;
            margin-right: 10px;
        }
        .barrage-message {
            color: #fff;
            font-size: 14px;
			text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.7);
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <div id="video-container">
        <video id="video" autoplay loop>
        </video>
        <div id="barrage"></div>
    </div>
    <div class="input-container">
        <input type="text" id="barrage-input" placeholder="输入弹幕内容">
        <button onclick="sendBarrage()">发送</button>
        <button onclick="toggleVideo()">视频</button>
    </div>

    <script>
        var barrage = document.getElementById('barrage');
        var video = document.getElementById('video');
        var danmuData = [];
        var timer;
        fetch('danmu.txt')
            .then(response => response.text())
            .then(data => {
                danmuData = data.split('\n').filter(Boolean);
            });

        function sendBarrage() {
            var input = document.getElementById('barrage-input').value;
            if (input.trim() !== "") {
                var barrageMessage = document.createElement('div');
                barrageMessage.className = 'barrage-message';
                barrageMessage.innerText = '我：' + input;
                barrage.appendChild(barrageMessage);
                document.getElementById('barrage-input').value = '';
                var randomHeight = Math.floor(Math.random() * 100);
                barrageMessage.style.top = randomHeight + "px";

                setTimeout(function() {
                    barrage.removeChild(barrageMessage);
                }, 4000);
            }
        }

        function toggleVideo() {
            if (video.paused) {
                video.play();
                startBarrage();
            } else {
                video.pause();
                clearInterval(timer);
            }
        }
        fetch('get_videos.php')
            .then(response => response.json())
            .then(data => {
                var randomIndex = Math.floor(Math.random() * data.length);
                video.src = data[randomIndex];
            })
            .catch(error => {
                console.error('Error fetching video list: ', error);
            });

        function startBarrage() {
            timer = setInterval(function() {
                if (danmuData.length > 0) {
                    var randomIndex = Math.floor(Math.random() * danmuData.length);
                    var message = danmuData[randomIndex];
                    var barrageMessage = document.createElement('div');
                    barrageMessage.className = 'barrage-message';
                    barrageMessage.innerText = message;
                    var randomHeight = Math.floor(Math.random() * 100);
                    barrageMessage.style.top = randomHeight + "px";
                    barrage.appendChild(barrageMessage);
                    setTimeout(function() {
                        barrage.removeChild(barrageMessage);
                    }, 10000);
                }
            }, 1000);
        }
    </script>
</body>
</html>