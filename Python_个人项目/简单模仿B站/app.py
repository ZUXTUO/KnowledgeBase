from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import sqlite3
import time
import os
import uuid
import subprocess
from werkzeug.utils import secure_filename
import random
import glob

app = Flask(__name__)

DATABASE = 'videos.db'
UPLOAD_FOLDER = 'uploads'
THUMBNAIL_FOLDER = 'thumbnails'
IMG_FOLDER = 'img'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['THUMBNAIL_FOLDER'] = THUMBNAIL_FOLDER
app.config['IMG_FOLDER'] = IMG_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(THUMBNAIL_FOLDER):
    os.makedirs(THUMBNAIL_FOLDER)
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            video_url TEXT NOT NULL,
            cover_url TEXT,
            upload_time INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            video_id TEXT NOT NULL,
            author TEXT DEFAULT '匿名用户',
            content TEXT NOT NULL,
            comment_time INTEGER,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_thumbnail(video_path, thumbnail_path):
    try:
        subprocess.run([
            'ffmpeg', '-i', video_path, '-ss', '00:00:01', '-vframes', '1',
            '-vf', 'scale=320:180', thumbnail_path, '-y'
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

@app.route('/uploads/<filename>')
def static_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/thumbnails/<filename>')
def static_thumbnails(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/img/<filename>')
def static_img(filename):
    return send_from_directory(app.config['IMG_FOLDER'], filename)

def get_random_cover_url(title=""):
    image_files = glob.glob(os.path.join(app.config['IMG_FOLDER'], '*.[jJpP][pPeE][gG]')) + \
                  glob.glob(os.path.join(app.config['IMG_FOLDER'], '*.[pP][nN][gG]'))
    if image_files:
        random_image = random.choice(image_files)
        cover_filename = os.path.basename(random_image)
        return url_for('static_img', filename=cover_filename)
    else:
        cover_text = title[:2] if title else "视频"
        return f"https://placehold.co/320x180/00A1D6/FFFFFF?text={cover_text}"

HOME_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title> (゜-゜)つロ 干杯~</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f4f5f7; }
        .nav-compact { height: 56px; }
        .bblili-pink { color: #fb7299; }
        .bblili-blue { background: #00a1d6; }
        .search-bar { background: #e3e5e7; border-radius: 8px; }
        .video-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .video-card:hover {
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }
        .thumbnail {
            aspect-ratio: 16/9;
            object-fit: cover;
            width: 100%;
            display: block;
        }
        .play-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.6);
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
            backdrop-filter: blur(5px);
        }
        .video-card:hover .play-btn { opacity: 1; }
        .bblili-logo-animation {
            animation: bounceIn 0.8s ease-out;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); opacity: 1; }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        .search-button-hover:hover {
            background-color: #008ccb;
        }
        .upload-button-hover:hover {
            background-color: #e65c82;
        }
    </style>
</head>
<body>
    <nav class="bg-white shadow-sm nav-compact flex items-center px-4 sticky top-0 z-50">
        <div class="container mx-auto flex items-center justify-between h-full">
            <div class="flex items-center space-x-4 lg:space-x-6">
                <a href="/" class="flex items-center space-x-2">
                    <div class="w-9 h-9 bg-gradient-to-br from-pink-400 to-blue-400 rounded-full flex items-center justify-center bblili-logo-animation">
                        <span class="text-white text-lg font-bold">B</span>
                    </div>
                    <span class="text-xl font-semibold bblili-pink hidden sm:block">bblili</span>
                </a>
            </div>

            <div class="flex-1 max-w-md mx-2 lg:mx-8 search-bar-container">
                <form action="/search" method="get" class="flex">
                    <input type="text" name="query" placeholder="搜索视频、UP主或番剧"
                           class="flex-1 px-4 py-2 search-bar text-sm border-0 outline-none focus:ring-2 focus:ring-blue-300 transition-all duration-200">
                    <button type="submit" class="bblili-blue text-white px-4 py-2 rounded-r-lg text-sm search-button-hover transition-colors duration-200">搜索</button>
                </form>
            </div>

            <div class="flex items-center space-x-3">
                <a href="/upload" class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1.5 rounded-md text-xs font-medium sm:px-4 sm:py-2 sm:text-sm upload-button-hover transition-colors duration-200">投稿</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-4 py-6">
        <div class="flex items-center mb-6">
            <h2 class="text-xl font-bold text-gray-800">推荐视频</h2>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 video-card-grid">
            {% for video in videos %}
            <div class="video-card" onclick="location.href='/video/{{ video.id }}'">
                <div class="relative">
                    <img src="{{ video.cover_url }}" alt="{{ video.title }}" class="thumbnail">
                    <div class="play-btn">
                        <svg class="w-6 h-6 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                        </svg>
                    </div>
                </div>
                <div class="p-3">
                    <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-2 leading-tight">{{ video.title }}</h3>
                    <div class="flex items-center text-xs text-gray-500 space-x-2">
                        <span>{{ (video.upload_time * 1000) | format_relative_time }}</span>
                        <span>•</span>
                        <span>{{ range(1000, 50000) | random }}播放</span>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="col-span-full text-center py-12">
                <p class="text-gray-500 text-lg">暂无视频内容，快来投稿吧！</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

UPLOAD_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>创作中心</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f4f5f7; }
        .nav-compact { height: 56px; }
        .bblili-pink { color: #fb7299; }
        .bblili-blue { background: #00a1d6; }
        .search-bar { background: #e3e5e7; border-radius: 8px; }
        .form-input { border: 1px solid #e1e5e9; border-radius: 8px; padding: 0.75rem 1rem; }
        .form-input:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0,161,214,0.15); outline: none; }
        .submit-button {
            background-color: #fb7299;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(251,114,153,0.2);
        }
        .submit-button:hover {
            background-color: #e65c82;
            box-shadow: 0 6px 10px rgba(251,114,153,0.3);
            transform: translateY(-2px);
        }
        .bblili-logo-animation {
            animation: bounceIn 0.8s ease-out;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); opacity: 1; }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        .search-button-hover:hover {
            background-color: #008ccb;
        }
        .upload-button-hover:hover {
            background-color: #e65c82;
        }
    </style>
</head>
<body>
    <nav class="bg-white shadow-sm nav-compact flex items-center px-4 sticky top-0 z-50">
        <div class="container mx-auto flex items-center justify-between h-full">
            <div class="flex items-center space-x-4 lg:space-x-6">
                <a href="/" class="flex items-center space-x-2">
                    <div class="w-9 h-9 bg-gradient-to-br from-pink-400 to-blue-400 rounded-full flex items-center justify-center bblili-logo-animation">
                        <span class="text-white text-lg font-bold">B</span>
                    </div>
                    <span class="text-xl font-semibold bblili-pink hidden sm:block">bblili</span>
                </a>
            </div>

            <div class="flex-1 max-w-md mx-2 lg:mx-8 search-bar-container">
                <form action="/search" method="get" class="flex">
                    <input type="text" name="query" placeholder="搜索视频、UP主或番剧"
                           class="flex-1 px-4 py-2 search-bar text-sm border-0 outline-none focus:ring-2 focus:ring-blue-300 transition-all duration-200">
                    <button type="submit" class="bblili-blue text-white px-4 py-2 rounded-r-lg text-sm search-button-hover transition-colors duration-200">搜索</button>
                </form>
            </div>

            <div class="flex items-center space-x-3">
                <a href="/upload" class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1.5 rounded-md text-xs font-medium sm:px-4 sm:py-2 sm:text-sm upload-button-hover transition-colors duration-200">投稿</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-4 py-8">
        <div class="max-w-2xl mx-auto bg-white rounded-lg p-6 shadow-lg">
            <h1 class="text-2xl font-bold text-gray-800 mb-6">视频投稿</h1>

            <form action="/upload" method="post" enctype="multipart/form-data" class="space-y-6">
                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">视频标题</label>
                    <input type="text" name="title" class="form-input w-full" required maxlength="80" placeholder="填写视频标题">
                    <p class="text-xs text-gray-500 mt-1">好的标题能获得更多播放</p>
                </div>

                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">视频简介</label>
                    <textarea name="description" rows="4" class="form-input w-full resize-none" maxlength="250" placeholder="填写视频简介"></textarea>
                    <p class="text-xs text-gray-500 mt-1">填写更全面的相关信息，让更多的人能搜索到你的视频吧</p>
                </div>

                <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">选择视频文件</label>
                    <input type="file" name="video_file" accept="video/*" class="form-input w-full file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" required>
                    <p class="text-xs text-gray-500 mt-1">支持mp4、avi、mov等格式，文件大小不超过500MB</p>
                </div>

                <div class="pt-4">
                    <button type="submit" class="w-full py-2 rounded-lg text-white font-semibold submit-button">
                        立即投稿
                    </button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""

SEARCH_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ query }} - 搜索结果</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f4f5f7; }
        .nav-compact { height: 56px; }
        .bblili-pink { color: #fb7299; }
        .bblili-blue { background: #00a1d6; }
        .search-bar { background: #e3e5e7; border-radius: 8px; }
        .video-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            cursor: pointer;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .video-card:hover {
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            transform: translateY(-5px);
        }
        .thumbnail {
            aspect-ratio: 16/9;
            object-fit: cover;
            width: 100%;
            display: block;
        }
        .play-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(0,0,0,0.6);
            border-radius: 50%;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
            backdrop-filter: blur(5px);
        }
        .video-card:hover .play-btn { opacity: 1; }
        .bblili-logo-animation {
            animation: bounceIn 0.8s ease-out;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); opacity: 1; }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        .search-button-hover:hover {
            background-color: #008ccb;
        }
        .upload-button-hover:hover {
            background-color: #e65c82;
        }
    </style>
</head>
<body>
    <nav class="bg-white shadow-sm nav-compact flex items-center px-4 sticky top-0 z-50">
        <div class="container mx-auto flex items-center justify-between h-full">
            <div class="flex items-center space-x-4 lg:space-x-6">
                <a href="/" class="flex items-center space-x-2">
                    <div class="w-9 h-9 bg-gradient-to-br from-pink-400 to-blue-400 rounded-full flex items-center justify-center bblili-logo-animation">
                        <span class="text-white text-lg font-bold">B</span>
                    </div>
                    <span class="text-xl font-semibold bblili-pink hidden sm:block">bblili</span>
                </a>
            </div>

            <div class="flex-1 max-w-md mx-2 lg:mx-8 search-bar-container">
                <form action="/search" method="get" class="flex">
                    <input type="text" name="query" placeholder="搜索视频、UP主或番剧" value="{{ query }}"
                           class="flex-1 px-4 py-2 search-bar text-sm border-0 outline-none focus:ring-2 focus:ring-blue-300 transition-all duration-200">
                    <button type="submit" class="bblili-blue text-white px-4 py-2 rounded-r-lg text-sm search-button-hover transition-colors duration-200">搜索</button>
                </form>
            </div>

            <div class="flex items-center space-x-3">
                <a href="/upload" class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1.5 rounded-md text-xs font-medium sm:px-4 sm:py-2 sm:text-sm upload-button-hover transition-colors duration-200">投稿</a>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-4 py-6">
        <div class="flex items-center mb-6">
            <h2 class="text-xl font-bold text-gray-800">搜索 "{{ query }}" 的结果</h2>
            <span class="text-sm text-gray-500 ml-2">共 {{ videos|length }} 个结果</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 video-card-grid">
            {% for video in videos %}
            <div class="video-card" onclick="location.href='/video/{{ video.id }}'">
                <div class="relative">
                    <img src="{{ video.cover_url }}" alt="{{ video.title }}" class="thumbnail">
                    <div class="play-btn">
                        <svg class="w-6 h-6 text-white ml-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z"/>
                        </svg>
                    </div>
                </div>
                <div class="p-3">
                    <h3 class="text-sm font-medium text-gray-900 mb-1 line-clamp-2 leading-tight">{{ video.title }}</h3>
                    <div class="flex items-center text-xs text-gray-500 space-x-2">
                        <span>{{ (video.upload_time * 1000) | format_relative_time }}</span>
                        <span>•</span>
                        <span>{{ range(1000, 50000) | random }}播放</span>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="col-span-full text-center py-12">
                <p class="text-gray-500 text-lg">没有找到相关视频</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

VIDEO_PLAY_PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ video.title }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background: #f4f5f7; }
        .nav-compact { height: 56px; }
        .bblili-pink { color: #fb7299; }
        .bblili-blue { background: #00a1d6; }
        .search-bar { background: #e3e5e7; border-radius: 8px; }
        .video-player { border-radius: 8px; background: #000; }
        .comment-input { border: 1px solid #e1e5e9; border-radius: 8px; padding: 0.75rem 1rem; }
        .comment-input:focus { border-color: #00a1d6; box-shadow: 0 0 0 3px rgba(0,161,214,0.15); outline: none; }
        .comment-button {
            background-color: #00a1d6;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,161,214,0.2);
        }
        .comment-button:hover {
            background-color: #008ccb;
            box-shadow: 0 6px 10px rgba(0,161,214,0.3);
            transform: translateY(-2px);
        }
        .bblili-logo-animation {
            animation: bounceIn 0.8s ease-out;
        }
        @keyframes bounceIn {
            0% { transform: scale(0.3); opacity: 0; }
            50% { transform: scale(1.05); opacity: 1; }
            70% { transform: scale(0.9); }
            100% { transform: scale(1); }
        }
        .search-button-hover:hover {
            background-color: #008ccb;
        }
        .upload-button-hover:hover {
            background-color: #e65c82;
        }
        /* Modal styles */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background-color: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            width: 90%;
            max-width: 400px;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="bg-white shadow-sm nav-compact flex items-center px-4 sticky top-0 z-50">
        <div class="container mx-auto flex items-center justify-between h-full">
            <div class="flex items-center space-x-4 lg:space-x-6">
                <a href="/" class="flex items-center space-x-2">
                    <div class="w-9 h-9 bg-gradient-to-br from-pink-400 to-blue-400 rounded-full flex items-center justify-center bblili-logo-animation">
                        <span class="text-white text-lg font-bold">B</span>
                    </div>
                    <span class="text-xl font-semibold bblili-pink hidden sm:block">bblili</span>
                </a>
            </div>

            <div class="flex-1 max-w-md mx-2 lg:mx-8 search-bar-container">
                <form action="/search" method="get" class="flex">
                    <input type="text" name="query" placeholder="搜索视频、UP主或番剧"
                           class="flex-1 px-4 py-2 search-bar text-sm border-0 outline-none focus:ring-2 focus:ring-blue-300 transition-all duration-200">
                    <button type="submit" class="bblili-blue text-white px-4 py-2 rounded-r-lg text-sm search-button-hover transition-colors duration-200">搜索</button>
                </form>
            </div>

            <div class="flex items-center space-x-3">
                <a href="/upload" class="bg-pink-500 hover:bg-pink-600 text-white px-3 py-1.5 rounded-md text-xs font-medium sm:px-4 sm:py-2 sm:text-sm upload-button-hover transition-colors duration-200">投稿</a>
            </div>
        </div>
    </nav>

    {% if video %}
    <div class="container mx-auto px-4 py-6">
        <div class="flex flex-col lg:flex-row gap-6 video-player-container">
            <div class="lg:flex-1">
                <div class="bg-black rounded-lg overflow-hidden mb-4 shadow-lg">
                    <video class="video-player w-full" controls preload="auto">
                        <source src="{{ video.video_url }}" type="video/mp4">
                        您的浏览器不支持视频播放
                    </video>
                </div>

                <div class="bg-white rounded-lg p-5 shadow-sm">
                    <h1 class="text-xl md:text-2xl font-bold text-gray-900 mb-3">{{ video.title }}</h1>
                    <div class="flex items-center text-sm text-gray-500 mb-4 space-x-4">
                        <span>{{ (video.upload_time * 1000) | format_relative_time }}</span>
                        <span>{{ range(1000, 50000) | random }}播放</span>
                        <span>{{ comments|length }}评论</span>
                    </div>
                    {% if video.description %}
                    <p class="text-gray-700 leading-relaxed text-sm md:text-base">{{ video.description }}</p>
                    {% endif %}
                    <div class="mt-4 flex justify-end">
                        <button id="deleteVideoBtn" class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200">删除视频</button>
                    </div>
                </div>
            </div>

            <div class="lg:w-96 comment-section">
                <div class="bg-white rounded-lg p-4 shadow-sm">
                    <h3 class="font-bold text-lg mb-4 text-gray-800">评论 {{ comments|length }}</h3>

                    <form action="/comment" method="post" class="mb-4">
                        <input type="hidden" name="video_id" value="{{ video.id }}">
                        <textarea name="content" rows="3" placeholder="发一条友善的评论"
                                class="comment-input w-full resize-none outline-none focus:ring-blue-300 transition-all duration-200" required></textarea>
                        <div class="flex justify-end mt-3">
                            <button type="submit" class="text-white px-5 py-2 rounded-lg text-sm font-medium comment-button">发布</button>
                        </div>
                    </form>

                    <div class="space-y-5 max-h-96 lg:max-h-screen overflow-y-auto pr-2">
                        {% for comment in comments %}
                        <div class="flex space-x-3">
                            <div class="w-9 h-9 bg-gray-200 rounded-full flex-shrink-0 flex items-center justify-center text-gray-600 text-sm">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a4 4 0 00-4 4h8a4 4 0 00-4-4z" clip-rule="evenodd" />
                                </svg>
                            </div>
                            <div class="flex-1">
                                <div class="flex items-center space-x-2 mb-1">
                                    <span class="text-sm font-semibold text-gray-800">{{ comment.author }}</span>
                                    <span class="text-xs text-gray-500">{{ (comment.comment_time * 1000) | format_relative_time }}</span>
                                </div>
                                <p class="text-sm text-gray-700 leading-relaxed">{{ comment.content }}</p>
                            </div>
                        </div>
                        {% else %}
                        <p class="text-center text-gray-500 py-8 text-base">暂无评论，快来发表你的看法吧！</p>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="deleteModal" class="modal-overlay hidden">
        <div class="modal-content">
            <p class="text-lg font-semibold mb-4">确认删除视频？</p>
            <p class="text-gray-700 mb-6">此操作将永久删除视频及其所有评论，无法恢复。</p>
            <div class="flex justify-center space-x-4">
                <button id="cancelDeleteBtn" class="px-5 py-2 rounded-md text-gray-700 bg-gray-200 hover:bg-gray-300 transition-colors duration-200">取消</button>
                <form id="deleteForm" method="post" action="/delete_video/{{ video.id }}">
                    <button type="submit" class="px-5 py-2 rounded-md text-white bg-red-500 hover:bg-red-600 transition-colors duration-200">确认删除</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('deleteVideoBtn').addEventListener('click', function() {
            document.getElementById('deleteModal').classList.remove('hidden');
        });

        document.getElementById('cancelDeleteBtn').addEventListener('click', function() {
            document.getElementById('deleteModal').classList.add('hidden');
        });
    </script>
    {% else %}
    <div class="container mx-auto px-4 py-12 text-center">
        <p class="text-gray-500 text-lg">视频不存在或已被删除。</p>
        <a href="/" class="mt-4 inline-block bblili-blue text-white px-6 py-2 rounded-md font-medium hover:bg-blue-600 transition-colors duration-200">返回首页</a>
    </div>
    {% endif %}
</body>
</html>
"""

@app.template_filter('format_relative_time')
def format_relative_time(timestamp):
    now = int(time.time() * 1000)
    diff = now - timestamp

    if diff < 60000:
        return "刚刚"
    elif diff < 3600000:
        return f"{diff // 60000}分钟前"
    elif diff < 86400000:
        return f"{diff // 3600000}小时前"
    elif diff < 2592000000:
        return f"{diff // 86400000}天前"
    else:
        return time.strftime('%Y-%m-%d', time.localtime(timestamp // 1000))

@app.route('/')
def index():
    conn = get_db_connection()
    videos = conn.execute('SELECT * FROM videos ORDER BY upload_time DESC').fetchall()
    conn.close()

    videos_with_random_covers = []
    for video in videos:
        video_dict = dict(video)
        video_dict['cover_url'] = get_random_cover_url(video_dict.get('title', ''))
        videos_with_random_covers.append(video_dict)

    return render_template_string(HOME_PAGE_TEMPLATE, videos=videos_with_random_covers)

@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        video_file = request.files.get('video_file')

        if not video_file or video_file.filename == '':
            return "没有选择视频文件", 400

        if video_file and allowed_file(video_file.filename):
            filename = secure_filename(video_file.filename)
            unique_filename = str(uuid.uuid4()) + "_" + filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            video_file.save(video_path)
            
            video_url = url_for('static_uploads', filename=unique_filename)
            
            cover_url = get_random_cover_url(title)
            
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO videos (id, title, description, video_url, cover_url, upload_time) VALUES (?, ?, ?, ?, ?, ?)',
                (str(uuid.uuid4()), title, description, video_url, cover_url, int(time.time()))
            )
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            return "不支持的文件类型", 400
    return render_template_string(UPLOAD_PAGE_TEMPLATE)

@app.route('/search')
def search():
    query = request.args.get('query', '')
    conn = get_db_connection()
    videos = conn.execute(
        'SELECT * FROM videos WHERE title LIKE ? OR description LIKE ? ORDER BY upload_time DESC',
        (f'%{query}%', f'%{query}%')
    ).fetchall()
    conn.close()

    videos_with_random_covers = []
    for video in videos:
        video_dict = dict(video)
        video_dict['cover_url'] = get_random_cover_url(video_dict.get('title', ''))
        videos_with_random_covers.append(video_dict)

    return render_template_string(SEARCH_PAGE_TEMPLATE, videos=videos_with_random_covers, query=query)

@app.route('/video/<video_id>')
def play_video(video_id):
    conn = get_db_connection()
    video = conn.execute('SELECT * FROM videos WHERE id = ?', (video_id,)).fetchone()
    comments = conn.execute('SELECT * FROM comments WHERE video_id = ? ORDER BY comment_time DESC', (video_id,)).fetchall()
    conn.close()
    return render_template_string(VIDEO_PLAY_PAGE_TEMPLATE, video=video, comments=comments)

@app.route('/comment', methods=('POST',))
def add_comment():
    video_id = request.form['video_id']
    content = request.form['content']

    if not content:
        return "评论内容不能为空", 400

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO comments (id, video_id, content, comment_time) VALUES (?, ?, ?, ?)',
        (str(uuid.uuid4()), video_id, content, int(time.time()))
    )
    conn.commit()
    conn.close()
    return redirect(url_for('play_video', video_id=video_id))

@app.route('/delete_video/<video_id>', methods=['POST'])
def delete_video(video_id):
    conn = get_db_connection()
    video = conn.execute('SELECT video_url, cover_url FROM videos WHERE id = ?', (video_id,)).fetchone()

    if video:
        video_url = video['video_url']
        cover_url = video['cover_url']

        conn.execute('DELETE FROM comments WHERE video_id = ?', (video_id,))

        conn.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()

        if video_url.startswith(url_for('static_uploads', filename='')):
            video_filename = video_url.split('/')[-1]
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            if os.path.exists(video_path):
                os.remove(video_path)

        if cover_url.startswith(url_for('static_img', filename='')):
            cover_filename = cover_url.split('/')[-1]
            cover_path = os.path.join(app.config['IMG_FOLDER'], cover_filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)
        elif cover_url.startswith(url_for('static_thumbnails', filename='')):
            cover_filename = cover_url.split('/')[-1]
            cover_path = os.path.join(app.config['THUMBNAIL_FOLDER'], cover_filename)
            if os.path.exists(cover_path):
                os.remove(cover_path)

    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)