import sqlite3
import io
import hashlib
import mimetypes
import random
import os
from flask import Flask, request, render_template_string, send_file, redirect, url_for, jsonify

CSS = '''
<style>
  body { font-family: Arial, sans-serif; margin: 20px; }
  input, button, select { padding: 5px; margin: 5px; }
  h1, h2 { color: #333; }
  table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
  tr:nth-child(even) { background-color: #f9f9f9; }
  th { background-color: #4CAF50; color: white; }
  a { color: #0066cc; text-decoration: none; }
  a:hover { text-decoration: underline; }
  progress { width: 100%; height: 20px; }
  .page-jump { margin-top: 10px; }
  .action-bar { margin: 10px 0; padding: 10px; background: #f5f5f5; border: 1px solid #ddd; }
  .checkbox-column { width: 30px; text-align: center; }
  .image-viewer {
    text-align: center;
    position: relative;
    touch-action: pan-y;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
  }
  .viewer-image {
    max-width: 100%;
    max-height: 70vh;
    margin: 10px auto;
    display: block;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  }
  .image-controls {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    margin-top: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }
  .tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin: 10px 0;
  }
  .tag-item {
    background: #e0e0e0;
    padding: 3px 8px;
    border-radius: 3px;
    display: inline-block;
  }
  .image-info {
    margin-bottom: 15px;
    font-size: 16px;
  }
  .rating-stars {
    font-size: 24px;
    cursor: pointer;
  }
  .rating-stars span {
    margin: 0 2px;
  }
.view-switcher {
  margin: 15px 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}
.view-switcher button, .view-switcher a.view-switch-btn {
  background: none;
  border: 1px solid #ddd;
  padding: 8px 15px;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 4px;
  text-decoration: none;
  color: #333;
  display: inline-block;
}
.view-switcher button.active, .view-switcher a.view-switch-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.gallery-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}
.thumbnail {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  transition: transform 0.2s;
  background: white;
  position: relative;
  overflow: hidden;
}
.thumbnail:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.thumbnail img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 10px;
}
.thumbnail-info {
  font-size: 0.9em;
  line-height: 1.4;
}
.thumbnail-tags {
  color: #666;
  font-size: 0.8em;
  margin-top: 5px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.thumbnail-actions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.thumbnail-actions a, .thumbnail-actions span {
  font-size: 0.8em;
  padding: 3px 8px;
  background: #f0f0f0;
  border-radius: 4px;
  white-space: nowrap;
}
.tag-cloud-compact {
  margin: 15px 0;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}
.tag-cloud-compact h3 {
    width: 100%;
    margin-bottom: 10px;
    font-size: 1.2em;
}
.tag-cloud-compact a {
  font-size: 12px !important;
  padding: 4px 10px;
  background: #e9ecef;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s;
  text-decoration: none;
  color: #495057;
}
.tag-cloud-compact a:hover {
  background: #dee2e6;
  transform: translateY(-1px);
}
.tag-cloud-compact .tag-count {
  font-size: 10px;
  margin-left: 5px;
  background: #6c757d;
  color: white;
  padding: 2px 6px;
  border-radius: 8px;
}
.pagination { margin-top: 20px; text-align: center; }
.nav-arrows { display: flex; justify-content: space-between; padding: 0 10px; margin-bottom: 10px; }
.nav-arrow { background: #ddd; border: none; padding: 10px 15px; cursor: pointer; border-radius: 5px; font-size: 1.5em;}
.nav-arrow:hover { background: #ccc; }
.delete-all-btn {
    background-color: #ff4444;
    color: white;
    padding: 8px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin-left: 10px;
}
.delete-all-btn:hover {
    background-color: #cc0000;
}
</style>
'''

class SimpleDatabase:
    def __init__(self, db_path='data.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._create_tables()
        self._ensure_columns_and_index()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                data BLOB NOT NULL,
                hash TEXT,
                score INTEGER DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY(image_id, tag_id),
                FOREIGN KEY(image_id) REFERENCES images(id) ON DELETE CASCADE,
                FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def _ensure_columns_and_index(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA table_info(images)")
        cols = [c[1] for c in cur.fetchall()]
        if 'hash' not in cols:
            cur.execute('ALTER TABLE images ADD COLUMN hash TEXT')
        if 'score' not in cols:
            cur.execute('ALTER TABLE images ADD COLUMN score INTEGER DEFAULT 0')
        self.conn.commit()
        cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_images_hash ON images(hash)')
        self.conn.commit()

    def insert_image(self, file_storage):
        blob = file_storage.read()
        img_hash = hashlib.sha256(blob).hexdigest()
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM images WHERE hash = ?', (img_hash,))
        row = cur.fetchone()
        if row:
            return row[0]
        filename = file_storage.filename
        cur.execute('INSERT INTO images (filename, data, hash) VALUES (?, ?, ?)', (filename, blob, img_hash))
        self.conn.commit()
        return cur.lastrowid

    def list_images_paginated(self, offset, limit):
        cur = self.conn.cursor()
        cur.execute('SELECT id, filename, score FROM images ORDER BY id DESC LIMIT ? OFFSET ?', (limit, offset))
        return cur.fetchall()

    def count_images(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM images')
        return cur.fetchone()[0]

    def get_image(self, image_id):
        cur = self.conn.cursor()
        cur.execute('SELECT filename, data FROM images WHERE id = ?', (image_id,))
        return cur.fetchone() or (None, None)

    def get_image_meta(self, image_id):
        cur = self.conn.cursor()
        cur.execute('SELECT filename, score FROM images WHERE id = ?', (image_id,))
        return cur.fetchone() or (None, 0)

    def set_score(self, image_id, score):
        cur = self.conn.cursor()
        cur.execute('UPDATE images SET score = ? WHERE id = ?', (score, image_id))
        self.conn.commit()

    def delete_image(self, image_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM images WHERE id = ?', (image_id,))
        self.conn.commit()

    def rename_image(self, image_id, new_name):
        cur = self.conn.cursor()
        cur.execute('UPDATE images SET filename = ? WHERE id = ?', (new_name, image_id))
        self.conn.commit()

    def add_tags(self, names):
        cur = self.conn.cursor()
        ids = []
        for name in names:
            name = name.strip()
            if not name: continue
            cur.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (name,))
            cur.execute('SELECT id FROM tags WHERE name = ?', (name,))
            ids.append(cur.fetchone()[0])
        self.conn.commit()
        return ids

    def add_tag(self, name):
        return self.add_tags([name])[0] if name else None

    def list_tags_paginated(self, offset, limit):
        cur = self.conn.cursor()
        cur.execute('SELECT id, name FROM tags ORDER BY name LIMIT ? OFFSET ?', (limit, offset))
        return cur.fetchall()

    def count_tags(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM tags')
        return cur.fetchone()[0]

    def rename_tag(self, tag_id, new_name):
        cur = self.conn.cursor()
        cur.execute('UPDATE tags SET name = ? WHERE id = ?', (new_name, tag_id))
        self.conn.commit()

    def delete_tag(self, tag_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        self.conn.commit()

    def assign_tag(self, image_id, tag_id):
        cur = self.conn.cursor()
        cur.execute('INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)', (image_id, tag_id))
        self.conn.commit()

    def remove_tag(self, image_id, tag_id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM image_tags WHERE image_id = ? AND tag_id = ?', (image_id, tag_id))
        self.conn.commit()

    def list_image_tags(self, image_id):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT t.id, t.name FROM tags t
            JOIN image_tags it ON t.id = it.tag_id
            WHERE it.image_id = ?
        ''', (image_id,))
        return cur.fetchall()

    def batch_update_tags(self, image_ids, tag_ids, operation='add'):
        cur = self.conn.cursor()
        for image_id in image_ids:
            if operation == 'replace':
                cur.execute('DELETE FROM image_tags WHERE image_id = ?', (image_id,))
            for tag_id in tag_ids:
                if operation == 'add' or operation == 'replace':
                    cur.execute('INSERT OR IGNORE INTO image_tags (image_id, tag_id) VALUES (?, ?)',
                               (image_id, tag_id))
                elif operation == 'remove':
                    cur.execute('DELETE FROM image_tags WHERE image_id = ? AND tag_id = ?',
                               (image_id, tag_id))
        self.conn.commit()

    def get_random_image_id(self):
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM images ORDER BY RANDOM() LIMIT 1')
        result = cur.fetchone()
        return result[0] if result else None

    def get_next_image_id(self, current_id):
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM images WHERE id > ? ORDER BY id ASC LIMIT 1', (current_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute('SELECT id FROM images ORDER BY id ASC LIMIT 1')
        result = cur.fetchone()
        return result[0] if result else None

    def get_prev_image_id(self, current_id):
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM images WHERE id < ? ORDER BY id DESC LIMIT 1', (current_id,))
        result = cur.fetchone()
        if result:
            return result[0]
        cur.execute('SELECT id FROM images ORDER BY id DESC LIMIT 1')
        result = cur.fetchone()
        return result[0] if result else None

    def get_all_image_ids(self):
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM images ORDER BY id')
        return [row[0] for row in cur.fetchall()]

    def list_tags_with_count_paginated(self, offset, limit):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT t.id, t.name, COUNT(it.image_id) AS image_count
            FROM tags t
            LEFT JOIN image_tags it ON t.id = it.tag_id
            GROUP BY t.id
            ORDER BY t.name
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cur.fetchall()

    def count_images_by_tag(self, tag_id):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT COUNT(*)
            FROM image_tags
            WHERE tag_id = ?
        ''', (tag_id,))
        return cur.fetchone()[0]

    def list_images_by_tag_paginated(self, tag_id, offset, limit):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT i.id, i.filename, i.score
            FROM images i
            JOIN image_tags it ON i.id = it.image_id
            WHERE it.tag_id = ?
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?
        ''', (tag_id, limit, offset))
        return cur.fetchall()

    def count_untagged_images(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT COUNT(i.id)
            FROM images i
            LEFT JOIN image_tags it ON i.id = it.image_id
            WHERE it.tag_id IS NULL
        ''')
        return cur.fetchone()[0]

    def list_untagged_images_paginated(self, offset, limit):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT i.id, i.filename, i.score
            FROM images i
            LEFT JOIN image_tags it ON i.id = it.image_id
            WHERE it.tag_id IS NULL
            ORDER BY i.id DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        return cur.fetchall()

    def count_images_by_score(self, score):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM images WHERE score = ?', (score,))
        return cur.fetchone()[0]

    def list_images_by_score_paginated(self, score, offset, limit):
        cur = self.conn.cursor()
        cur.execute('SELECT id, filename, score FROM images WHERE score = ? ORDER BY id DESC LIMIT ? OFFSET ?', (score, limit, offset))
        return cur.fetchall()

    def delete_images_by_score(self, score):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM images WHERE score = ?', (score,))
        deleted_count = cur.rowcount
        self.conn.commit()
        return deleted_count


app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
PAGE_SIZE = 200
db = SimpleDatabase('data.db')

INDEX_HTML = CSS + '''
<h1>图片管理</h1>
<div class="tag-cloud-compact">
  <h3>标签云 (点击标签查看图片)</h3>
  {% for tid, name, count in tags %}
    <a href="{{ url_for('tag_images', tag_id=tid) }}">
      {{ name }}<span class="tag-count">{{ count }}</span>
    </a>
  {% endfor %}
</div>
<ul>
  <li><a href="{{ url_for('show_images') }}">查看所有图片</a></li>
  <li><a href="{{ url_for('show_untagged_images') }}">查看未标记标签的图片</a></li>
  <li><a href="{{ url_for('show_one_star_images') }}">查看1星评价的图片</a></li>
  <li><a href="{{ url_for('random_viewer') }}">随机浏览图片</a></li>
  <li><a href="{{ url_for('batch_upload') }}">批量异步上传</a></li>
  <li><a href="{{ url_for('manage_tags') }}">管理标签</a></li>
</ul>
'''

@app.route('/')
def index():
    cur = db.conn.cursor()
    cur.execute('''
        SELECT t.id, t.name, COUNT(it.image_id) AS count
        FROM tags t
        LEFT JOIN image_tags it ON t.id = it.tag_id
        GROUP BY t.id
        ORDER BY count DESC
        LIMIT 50
    ''')
    tags = cur.fetchall()
    return render_template_string(INDEX_HTML, tags=tags)

RANDOM_VIEWER_HTML = CSS + '''
<h2>图片浏览器</h2>

<div class="image-viewer" id="imageViewer">
  <!-- 图片显示区域 -->
  <div class="nav-arrows">
    <button class="nav-arrow" id="prevBtn">&lt;</button>
    <button class="nav-arrow" id="nextBtn">&gt;</button>
  </div>
  
  <img class="viewer-image" src="{{ url_for('get_image_route', image_id=image_id) }}" 
       alt="{{ filename }}" id="currentImage">
  
  <!-- 图片信息和控制区 -->
  <div class="image-controls">
    <div class="image-info">
      <strong>文件名:</strong> {{ filename }} | 
      <strong>ID:</strong> {{ image_id }}
    </div>

    <div style="margin-top: 15px;">
      <button id="deleteBtn" style="background: #ff4444; color: white;">删除图片</button>
    </div>
    
    <!-- 评分控制 -->
    <div>
      <strong>评分:</strong>
      <div class="rating-stars" id="ratingStars">
        {% for i in range(1, 6) %}
          <span class="star" data-rating="{{ i }}">{{ '★' if i <= current_score else '☆' }}</span>
        {% endfor %}
      </div>
    </div>
    
    <!-- 标签显示 -->
    <div style="margin-top: 15px;">
      <strong>标签:</strong>
      <div class="tag-container" id="tagList">
        {% for tag_id, tag_name in image_tags %}
          <span class="tag-item">{{ tag_name }}</span>
        {% endfor %}
      </div>
      <button id="editTagsBtn">编辑标签</button>
    </div>
    
    <!-- 标签编辑区（默认隐藏） -->
    <div id="tagEditor" style="display: none; margin-top: 15px; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
      <h4>编辑标签</h4>
      <div id="tagCheckboxes">
{% for tag_id, tag_name in all_tags %}
  <div>
    <input 
      type="checkbox" 
      id="tag_{{ tag_id }}" 
      class="tag-checkbox" 
      value="{{ tag_id }}"
      {% if tag_id in image_tags|map(attribute=0)|list %}checked{% endif %}
    >
    <label for="tag_{{ tag_id }}">{{ tag_name }}</label>
  </div>
{% endfor %}
      </div>
      <div style="margin-top: 10px;">
        <input type="text" id="newTagInput" placeholder="添加新标签">
        <button id="addNewTagBtn">添加</button>
      </div>
      <div style="margin-top: 10px;">
        <button id="saveTagsBtn">保存标签</button>
        <button id="cancelEditBtn">取消</button>
      </div>
    </div>
  </div>
</div>

<div style="text-align: center; margin-top: 20px;">
  <a href="/">返回首页</a>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const currentImageId = {{ image_id }};
    const imageViewer = document.getElementById('imageViewer');
    const currentImage = document.getElementById('currentImage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const ratingStars = document.getElementById('ratingStars');
    const editTagsBtn = document.getElementById('editTagsBtn');
    const tagEditor = document.getElementById('tagEditor');
    const saveTagsBtn = document.getElementById('saveTagsBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const addNewTagBtn = document.getElementById('addNewTagBtn');
    const newTagInput = document.getElementById('newTagInput');
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    // 监听键盘事件
    document.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowLeft') {
        window.location.href = '/random_viewer?id=' + {{ prev_id }};
      } else if (e.key === 'ArrowRight') {
        window.location.href = '/random_viewer?id=' + {{ next_id }};
      }
    });
    
    // 监听左右按钮点击
    prevBtn.addEventListener('click', function() {
      window.location.href = '/random_viewer?id=' + {{ prev_id }};
    });
    
    nextBtn.addEventListener('click', function() {
      window.location.href = '/random_viewer?id=' + {{ next_id }};
    });
    
    // 触摸滑动支持
    imageViewer.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
    }, false);
    
    imageViewer.addEventListener('touchend', function(e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, false);
    
    function handleSwipe() {
      const swipeThreshold = 50; // 滑动阈值
      if (touchEndX < touchStartX - swipeThreshold) {
        // 向左滑动 -> 下一张
        window.location.href = '/random_viewer?id=' + {{ next_id }};
      }
      if (touchEndX > touchStartX + swipeThreshold) {
        // 向右滑动 -> 上一张
        window.location.href = '/random_viewer?id=' + {{ prev_id }};
      }
    }
    
    // 评分功能
    ratingStars.addEventListener('click', function(e) {
      if (e.target.classList.contains('star')) {
        const rating = e.target.dataset.rating;
        // 发送评分请求
        fetch('/api/rate_image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image_id: currentImageId,
            score: rating
          })
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            // 更新星星显示
            document.querySelectorAll('.star').forEach(star => {
              const starRating = parseInt(star.dataset.rating);
              star.textContent = starRating <= rating ? '★' : '☆';
            });
          }
        });
      }
    });
    
    // 标签编辑功能
    editTagsBtn.addEventListener('click', function() {
      tagEditor.style.display = 'block';
    });
    
    cancelEditBtn.addEventListener('click', function() {
      tagEditor.style.display = 'none';
    });
    
    saveTagsBtn.addEventListener('click', function() {
      const selectedTags = Array.from(document.querySelectorAll('.tag-checkbox:checked')).map(cb => cb.value);
      
      fetch('/api/update_image_tags', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_id: currentImageId,
          tag_ids: selectedTags
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // 刷新页面显示更新后的标签
          window.location.reload();
        }
      });
    });
    
    // 添加新标签
    addNewTagBtn.addEventListener('click', function() {
      const newTagName = newTagInput.value.trim();
      if (!newTagName) return;
      
      fetch('/api/add_tag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: newTagName
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // 添加新的标签复选框
          const tagCheckboxes = document.getElementById('tagCheckboxes');
          const newTagHtml = `
            <div>
              <input type="checkbox" id="tag_${data.id}" class="tag-checkbox" value="${data.id}" checked>
              <label for="tag_${data.id}">${newTagName}</label>
            </div>
          `;
          tagCheckboxes.insertAdjacentHTML('beforeend', newTagHtml);
          newTagInput.value = '';
        }
      });
    });
  });

  // 在已有脚本中添加删除功能
  document.getElementById('deleteBtn').addEventListener('click', function() {
    if (confirm('确定要永久删除这张图片吗？')) {
      fetch('/delete_image/' + currentImageId, {
        method: 'POST'
      })
      .then(response => {
        if (response.ok) {
          // 尝试跳转到下一张图片
          window.location.href = '/random_viewer?id=' + {{ next_id }};
        } else {
          alert('删除失败');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('删除操作失败');
      });
    }
  });
</script>
'''

@app.route('/delete_image_from_viewer/<int:image_id>', methods=['POST'])
def delete_image_from_viewer(image_id):
    try:
        next_id_after_delete = db.get_next_image_id(image_id)
        prev_id_after_delete = db.get_prev_image_id(image_id)

        db.delete_image(image_id)

        if next_id_after_delete and next_id_after_delete != image_id:
            return jsonify({'redirect_url': url_for('random_viewer', id=next_id_after_delete)})
        elif prev_id_after_delete and prev_id_after_delete != image_id:
            return jsonify({'redirect_url': url_for('random_viewer', id=prev_id_after_delete)})
        else:
            remaining_image_id = db.get_random_image_id()
            if remaining_image_id:
                return jsonify({'redirect_url': url_for('random_viewer', id=remaining_image_id)})
            else:
                return jsonify({'redirect_url': url_for('index')})
    except Exception as e:
        print(f"Error in delete_image_from_viewer: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/random_viewer')
def random_viewer():
    image_id = request.args.get('id', type=int)
    if not image_id:
        image_id = db.get_random_image_id()
        if not image_id:
            return "没有可用的图片", 404
        return redirect(url_for('random_viewer', id=image_id))

    filename, current_score = db.get_image_meta(image_id)
    if not filename:
        new_random_id = db.get_random_image_id()
        if new_random_id:
            return redirect(url_for('random_viewer', id=new_random_id))
        else:
            return "图片不存在，且数据库中已无其他图片。", 404

    prev_id = db.get_prev_image_id(image_id)
    next_id = db.get_next_image_id(image_id)

    image_tags = db.list_image_tags(image_id)
    all_tags = db.list_tags_paginated(0, 10000)

    return render_template_string(
        RANDOM_VIEWER_HTML,
        image_id=image_id,
        filename=filename,
        current_score=current_score,
        prev_id=prev_id,
        next_id=next_id,
        image_tags=image_tags,
        all_tags=all_tags
    )

IMAGES_HTML_BASE = CSS + '''
<h2>{{ title }}</h2>
<div class="view-switcher">
  <a href="?view=list{% if tag_id %}&tag_id={{ tag_id }}{% elif untagged %}&untagged=true{% elif one_star %}&one_star=true{% endif %}" class="view-switch-btn {% if view_type == 'list' %}active{% endif %}">列表视图</a>
  <a href="?view=gallery{% if tag_id %}&tag_id={{ tag_id }}{% elif untagged %}&untagged=true{% elif one_star %}&one_star=true{% endif %}" class="view-switch-btn {% if view_type == 'gallery' %}active{% endif %}">相册视图</a>
  {% if one_star and total_images > 0 %}
    <form action="{{ url_for('delete_one_star_images_route') }}" method="post" style="display: inline-block; margin-left: 20px;" onsubmit="return confirm('确定要删除所有1星图片吗？此操作不可恢复。')">
        <button type="submit" class="delete-all-btn">一键清理所有1星图片</button>
    </form>
  {% endif %}
</div>

{% if view_type == 'list' %}
<form id="batch-form" action="{{ url_for('batch_tags') }}" method="post">
  <div class="action-bar">
    <button type="submit" id="batch-tag-btn">批量修改标签</button>
    <button type="button" id="batch-rename-btn" onclick="submitToBatchRename()">批量重命名</button>
    <span id="selection-count">已选择: 0 个图片</span>
    <button type="button" id="select-all">全选</button>
    <button type="button" id="deselect-all">取消全选</button>
    <a href="{{ url_for('random_viewer') }}" style="float: right;">随机浏览图片</a>
  </div>
  <table>
    <tr>
      <th class="checkbox-column"><input type="checkbox" id="toggle-all"></th>
      <th>ID</th><th>文件名</th><th>标签</th><th>评分</th><th>操作</th>
    </tr>
    {% for iid, fname, score, tags in images %}
    <tr>
      <td class="checkbox-column"><input type="checkbox" name="image_ids" value="{{ iid }}" class="image-checkbox"></td>
      <td>{{ iid }}</td>
      <td>{{ fname }}</td>
      <td>
        {% for tag_name in tags %}
          <span class="tag-item">{{ tag_name }}</span>
        {% else %}
          无标签
        {% endfor %}
      </td>
      <td>{{ score }}</td>
      <td>
        <a href="{{ url_for('get_image_route', image_id=iid) }}" target="_blank">查看</a> |
        <a href="{{ url_for('random_viewer', id=iid) }}">浏览</a> |
        <a href="{{ url_for('rate_image', image_id=iid) }}">评分</a> |
        <a href="{{ url_for('assign_tags_route', image_id=iid) }}">标记标签</a> |
        <a href="{{ url_for('delete_image_from_list_route', image_id=iid, current_page=page, view_type=view_type, tag_id=tag_id if tag_id else '', untagged=untagged if untagged else '', one_star=one_star if one_star else '') }}" onclick="return confirm('确定删除图片 {{fname}} (ID: {{iid}})?')">删除</a>
      </td>
    </tr>
    {% endfor %}
  </table>
</form>
{% else %}
<div class="gallery-view">
  {% for iid, fname, score, tags in images %}
  <div class="thumbnail">
    <a href="{{ url_for('random_viewer', id=iid) }}">
      <img src="{{ url_for('get_image_route', image_id=iid) }}" alt="{{ fname }}">
    </a>
    <div class="thumbnail-info">
      <div class="filename" title="{{ fname }}">{{ fname|truncate(25) }}</div>
      <div class="thumbnail-tags">
        {% for tag_name in tags %}<span class="tag-item">{{ tag_name }}</span>{% else %}无标签{% endfor %}
      </div>
      <div class="thumbnail-actions">
        <span>★{{ score }}</span>
        <a href="{{ url_for('assign_tags_route', image_id=iid) }}">编辑标签</a>
        <a href="{{ url_for('delete_image_from_list_route', image_id=iid, current_page=page, view_type=view_type, tag_id=tag_id if tag_id else '', untagged=untagged if untagged else '', one_star=one_star if one_star else '') }}" onclick="return confirm('确定删除图片 {{fname}} (ID: {{iid}})?')">删除</a>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}

<div class="pagination">
  {% if page > 1 %}
    <a href="?page={{ page-1 }}&view={{ view_type }}{% if tag_id %}&tag_id={{ tag_id }}{% elif untagged %}&untagged=true{% elif one_star %}&one_star=true{% endif %}">上一页</a>
  {% endif %}
  <span>第 {{ page }} 页 / 共 {{ pages }} 页 (共 {{total_images}} 张图片)</span>
  {% if page < pages %}
    <a href="?page={{ page+1 }}&view={{ view_type }}{% if tag_id %}&tag_id={{ tag_id }}{% elif untagged %}&untagged=true{% elif one_star %}&one_star=true{% endif %}">下一页</a>
  {% endif %}
</div>
<div class="page-jump">
  跳转到第 <form style="display:inline;" method="get">
    <input type="number" name="page" min="1" max="{{ pages }}" value="{{ page }}" style="width:60px;">
    <input type="hidden" name="view" value="{{ view_type }}">
    {% if tag_id %}<input type="hidden" name="tag_id" value="{{ tag_id }}">{% endif %}
    {% if untagged %}<input type="hidden" name="untagged" value="true">{% endif %}
    {% if one_star %}<input type="hidden" name="one_star" value="true">{% endif %}
    <button type="submit">GO</button>
  </form> 页
</div>
<a href="/">返回首页</a>
<script>
document.addEventListener('DOMContentLoaded', function() {
    const toggleAll = document.getElementById('toggle-all');
    const checkboxes = document.querySelectorAll('.image-checkbox');
    const selectionCount = document.getElementById('selection-count');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');

    function updateSelectionCount() {
        const count = document.querySelectorAll('.image-checkbox:checked').length;
        if (selectionCount) selectionCount.textContent = '已选择: ' + count + ' 个图片';
    }

    if (toggleAll) {
        toggleAll.addEventListener('change', function() {
            checkboxes.forEach(cb => cb.checked = toggleAll.checked);
            updateSelectionCount();
        });
    }

    checkboxes.forEach(cb => {
        cb.addEventListener('change', updateSelectionCount);
    });

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            checkboxes.forEach(cb => cb.checked = true);
            if(toggleAll) toggleAll.checked = true;
            updateSelectionCount();
        });
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', function() {
            checkboxes.forEach(cb => cb.checked = false);
            if(toggleAll) toggleAll.checked = false;
            updateSelectionCount();
        });
    }
    if (checkboxes.length > 0) { 
        updateSelectionCount();
    }
});
function submitToBatchRename() {
    const form = document.getElementById('batch-form');
    const selectedCheckboxes = form.querySelectorAll('input[name="image_ids"]:checked');
    if (selectedCheckboxes.length === 0) {
        alert('请至少选择一张图片进行重命名。');
        return;
    }
    form.action = "{{ url_for('batch_rename_form_route') }}";
    form.method = "post";
    form.submit();
}
</script>
'''

BATCH_RENAME_FORM_HTML = CSS + '''
<h2>批量重命名图片</h2>
<p>将为选中的 {{ image_ids|length }} 张图片基于提供的前缀和序号重命名。</p>
<form method="post" action="{{ url_for('batch_rename_execute_route') }}">
  {% for iid in image_ids %}
    <input type="hidden" name="image_ids" value="{{ iid }}">
  {% endfor %}
  <div>
    <label for="tag_prefix">名称前缀 (例如: MyHoliday):</label>
    <input type="text" name="tag_prefix" id="tag_prefix" required>
  </div>
  <div style="margin-top: 20px;">
    <button type="submit">开始重命名</button>
    <a href="{{ request.referrer or url_for('show_images') }}">取消</a>
  </div>
</form>
<p>重命名后的格式为: 前缀_序号.原扩展名 (例如: MyHoliday_001.jpg)</p>
'''

@app.route('/batch_rename_form', methods=['POST'])
def batch_rename_form_route():
    image_ids = request.form.getlist('image_ids')
    if not image_ids:
        return redirect(request.referrer or url_for('show_images'))
    return render_template_string(BATCH_RENAME_FORM_HTML, image_ids=image_ids, CSS=CSS)

@app.route('/batch_rename_execute', methods=['POST'])
def batch_rename_execute_route():
    image_ids_str = request.form.getlist('image_ids')
    tag_prefix = request.form.get('tag_prefix', '').strip()

    if not image_ids_str:
        return redirect(request.referrer or url_for('show_images'))
    if not tag_prefix:
        return redirect(request.referrer or url_for('show_images'))

    image_ids = [int(id_str) for id_str in image_ids_str]
    image_ids.sort()

    for index, image_id in enumerate(image_ids, 1):
        original_filename, _ = db.get_image_meta(image_id)
        if original_filename:
            _, ext_part = os.path.splitext(original_filename)
            if not ext_part: # Ensure there's a dot if os.path.splitext returns empty ext for names like 'filename'
                ext_part = '' # Or handle as an error, or assume a default like '.jpg'
            new_filename = f"{tag_prefix}_{index:03d}{ext_part}"
            db.rename_image(image_id, new_filename)
        else:
            print(f"Warning: Image ID {image_id} not found during batch rename.")
    return redirect(request.referrer or url_for('show_images'))


@app.route('/images')
def show_images():
    view_type = request.args.get('view', 'list')
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PAGE_SIZE
    total = db.count_images()
    raw = db.list_images_paginated(offset, PAGE_SIZE)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE or 1
    images_data = []
    for iid, fname, score in raw:
        tags = [t[1] for t in db.list_image_tags(iid)]
        images_data.append((iid, fname, score, tags))
    return render_template_string(IMAGES_HTML_BASE,
        title="所有图片",
        images=images_data,
        page=page,
        pages=pages,
        total_images=total,
        view_type=view_type,
        tag_id=None,
        untagged=False,
        one_star=False
    )

@app.route('/untagged_images')
def show_untagged_images():
    view_type = request.args.get('view', 'list')
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PAGE_SIZE
    total = db.count_untagged_images()
    raw = db.list_untagged_images_paginated(offset, PAGE_SIZE)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE or 1
    images_data = []
    for iid, fname, score in raw:
        images_data.append((iid, fname, score, []))
    return render_template_string(IMAGES_HTML_BASE,
        title="未标记标签的图片",
        images=images_data,
        page=page,
        pages=pages,
        total_images=total,
        view_type=view_type,
        tag_id=None,
        untagged=True,
        one_star=False
    )

@app.route('/one_star_images')
def show_one_star_images():
    view_type = request.args.get('view', 'list')
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PAGE_SIZE
    total = db.count_images_by_score(1)
    raw = db.list_images_by_score_paginated(1, offset, PAGE_SIZE)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE or 1
    images_data = []
    for iid, fname, score in raw:
        tags = [t[1] for t in db.list_image_tags(iid)]
        images_data.append((iid, fname, score, tags))
    return render_template_string(IMAGES_HTML_BASE,
        title="1星评价的图片",
        images=images_data,
        page=page,
        pages=pages,
        total_images=total,
        view_type=view_type,
        tag_id=None,
        untagged=False,
        one_star=True
    )

@app.route('/delete_one_star_images', methods=['POST'])
def delete_one_star_images_route():
    db.delete_images_by_score(1)
    return redirect(url_for('show_one_star_images'))


@app.route('/tag/<int:tag_id>/images')
def tag_images(tag_id):
    view_type = request.args.get('view', 'list')
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * PAGE_SIZE
    total = db.count_images_by_tag(tag_id)
    raw = db.list_images_by_tag_paginated(tag_id, offset, PAGE_SIZE)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE or 1

    cur = db.conn.cursor()
    cur.execute('SELECT name FROM tags WHERE id = ?', (tag_id,))
    tag_info = cur.fetchone()
    if not tag_info:
        return "标签不存在", 404
    tag_name = tag_info[0]

    images_data = []
    for iid, fname, score in raw:
        tags = [t[1] for t in db.list_image_tags(iid)]
        images_data.append((iid, fname, score, tags))

    return render_template_string(IMAGES_HTML_BASE,
        title=f"标签 \"{tag_name}\" 的图片",
        images=images_data,
        page=page,
        pages=pages,
        total_images=total,
        view_type=view_type,
        tag_id=tag_id,
        untagged=False,
        one_star=False
    )

BATCH_TAGS_HTML = CSS + '''
<h2>批量标签管理</h2>
<p>已选择 {{ image_ids|length }} 张图片</p>

<form method="post" action="/batch_tags_update">
  {% for iid in image_ids %}
    <input type="hidden" name="image_ids" value="{{ iid }}">
  {% endfor %}
  
  <h3>操作方式</h3>
  <select name="operation" id="operation">
    <option value="add">添加标签</option>
    <option value="remove">移除标签</option>
    <option value="replace">替换所有标签</option>
  </select>
  
  <h3>选择标签</h3>
  <div style="margin-bottom: 10px;">
    <input type="text" id="new-tag" placeholder="新标签名称">
    <button type="button" id="add-new-tag">添加新标签</button>
  </div>
  
  <div style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
    {% for tid, name in all_tags %}
      <div>
        <input type="checkbox" name="tag_ids" value="{{ tid }}" id="tag_{{ tid }}">
        <label for="tag_{{ tid }}">{{ name }}</label>
      </div>
    {% endfor %}
  </div>
  
  <div style="margin-top: 20px;">
    <button type="submit">应用标签更改</button>
    <a href="/images">取消</a>
  </div>
</form>

<script>
document.addEventListener('DOMContentLoaded', function() {
  // 添加新标签功能
  document.getElementById('add-new-tag').addEventListener('click', async function() {
    const newTagInput = document.getElementById('new-tag');
    const tagName = newTagInput.value.trim();
    
    if (!tagName) {
      alert('请输入标签名称');
      return;
    }
    
    try {
      const response = await fetch('/api/add_tag', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: tagName })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // 添加新的标签到列表并选中
        const tagsContainer = document.querySelector('div[style*="overflow-y: auto"]');
        const newTagHtml = `
          <div>
            <input type="checkbox" name="tag_ids" value="${data.id}" id="tag_${data.id}" checked>
            <label for="tag_${data.id}">${tagName}</label>
          </div>
        `;
        tagsContainer.insertAdjacentHTML('beforeend', newTagHtml);
        newTagInput.value = '';
      } else {
        alert('添加标签失败: ' + data.error);
      }
    } catch (err) {
      alert('操作失败: ' + err.message);
    }
  });
});
</script>
'''

@app.route('/batch_tags', methods=['POST'])
def batch_tags():
    image_ids = request.form.getlist('image_ids')
    if not image_ids:
        return redirect(url_for('show_images'))
    
    # 获取所有标签
    all_tags = db.list_tags_paginated(0, 1000)  # 获取所有标签，不分页
    
    return render_template_string(BATCH_TAGS_HTML, image_ids=image_ids, all_tags=all_tags)

@app.route('/batch_tags_update', methods=['POST'])
def batch_tags_update():
    image_ids = [int(id) for id in request.form.getlist('image_ids')]
    tag_ids = [int(id) for id in request.form.getlist('tag_ids')]
    operation = request.form.get('operation', 'replace')
    if not image_ids:
        return redirect(request.referrer or url_for('show_images'))
    db.batch_update_tags(image_ids, tag_ids, operation)
    return redirect(request.referrer or url_for('show_images'))

@app.route('/api/add_tag', methods=['POST'])
def api_add_tag():
    data = request.json
    tag_name = data.get('name', '').strip()
    if not tag_name:
        return jsonify({'success': False, 'error': '标签名称不能为空'})
    try:
        tag_id = db.add_tag(tag_name)
        return jsonify({'success': True, 'id': tag_id, 'name': tag_name})
    except sqlite3.IntegrityError:
        cur = db.conn.cursor()
        cur.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        existing_tag = cur.fetchone()
        if existing_tag:
            return jsonify({'success': True, 'id': existing_tag[0], 'name': tag_name, 'message': 'Tag already exists'})
        return jsonify({'success': False, 'error': 'Tag already exists but could not retrieve ID.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/rate_image', methods=['POST'])
def api_rate_image():
    data = request.json
    image_id = data.get('image_id')
    score = int(data.get('score', 0))
    if not image_id or not (1 <= score <= 5):
        return jsonify({'success': False, 'error': '参数无效'})
    try:
        db.set_score(image_id, score)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update_image_tags', methods=['POST'])
def api_update_image_tags():
    data = request.json
    image_id = data.get('image_id')
    tag_ids_str = data.get('tag_ids', [])
    tag_ids = [int(tid) for tid in tag_ids_str]

    if not image_id:
        return jsonify({'success': False, 'error': '缺少图片ID'})
    try:
        cur = db.conn.cursor()
        cur.execute('DELETE FROM image_tags WHERE image_id = ?', (image_id,))
        for tag_id in tag_ids:
            db.assign_tag(image_id, tag_id)
        db.conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.conn.rollback()
        return jsonify({'success': False, 'error': str(e)})

BATCH_HTML = CSS + '''
<h2>批量异步上传</h2>
<input type="file" id="files" multiple style="display:none;">
<button onclick="document.getElementById('files').click()">选择文件</button>
<button onclick="uploadAll()">开始上传</button>
<progress id="progress" max="100" value="0"></progress>
<div id="status"></div>
<a href="/">返回</a>
<script>
async function uploadAll() {
  const files = document.getElementById('files').files;
  if (!files.length) { alert('请选择文件'); return; }
  const statusEl = document.getElementById('status');
  const progressEl = document.getElementById('progress');
  statusEl.innerHTML = '';
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const form = new FormData(); form.append('file', file);
    const fileStatus = document.createElement('div');
    fileStatus.textContent = \`上传 \${i+1}/\${files.length}: \${file.name}\`;
    statusEl.appendChild(fileStatus);
    try {
      const res = await fetch('{{ url_for("upload_async") }}', { method: 'POST', body: form });
      const data = await res.json();
      if (res.ok && data.id) {
        fileStatus.textContent += \` 完成 (ID: \${data.id})\`;
      } else {
        fileStatus.textContent += \` 失败: \${data.error || '未知错误'}\`;
        fileStatus.style.color = 'red';
      }
    } catch (e) {
      fileStatus.textContent += \` 失败: \${e}\`;
      fileStatus.style.color = 'red';
    }
    progressEl.value = Math.round(((i+1)/files.length)*100);
  }
  const allDone = document.createElement('div');
  allDone.textContent = '全部完成';
  allDone.style.fontWeight = 'bold';
  statusEl.appendChild(allDone);
}
</script>
'''
@app.route('/batch_upload')
def batch_upload():
    return render_template_string(BATCH_HTML)

@app.route('/upload_async', methods=['POST'])
def upload_async():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'No file'}), 400
    try:
        image_id = db.insert_image(file)
        return jsonify({'id': image_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/image/<image_id>')
def get_image_route(image_id):
    try:
        iid = int(image_id)
    except ValueError:
        return '无效的图片ID格式', 400
    fname, data = db.get_image(iid)
    if data is None:
        return '未找到图片', 404
    mime, _ = mimetypes.guess_type(fname)
    if not mime:
        mime = 'application/octet-stream'
    return send_file(io.BytesIO(data), mimetype=mime, download_name=fname)

@app.route('/delete_image_from_list/<int:image_id>')
def delete_image_from_list_route(image_id):
    db.delete_image(image_id)
    current_page = request.args.get('current_page', '1')
    view_type = request.args.get('view_type', 'list')
    tag_id = request.args.get('tag_id')
    untagged = request.args.get('untagged')
    one_star = request.args.get('one_star')

    if one_star == 'True' or one_star == 'true':
        redirect_url = url_for('show_one_star_images', page=current_page, view=view_type)
    elif untagged == 'True' or untagged == 'true':
        redirect_url = url_for('show_untagged_images', page=current_page, view=view_type)
    elif tag_id:
        redirect_url = url_for('tag_images', tag_id=tag_id, page=current_page, view=view_type)
    else:
        redirect_url = url_for('show_images', page=current_page, view=view_type)
    return redirect(redirect_url)


RATE_HTML = CSS + '''
<h2>给图片 {{ id }} ({{filename}}) 打分</h2>
<img src="{{ url_for('get_image_route', image_id=id) }}" alt="Image {{id}}" style="max-width:300px; max-height:300px; display:block; margin-bottom:10px;"><br>
<form method="post">
  评分(1-5):
  <select name="score">
    {% for i in range(1,6) %}
      <option value="{{ i }}" {% if i==current_score %}selected{% endif %}>{{ i }}</option>
    {% endfor %}
  </select>
  <button type="submit">保存</button>
</form>
<a href="{{ request.referrer or url_for('show_images') }}">返回</a>
'''
@app.route('/rate/<image_id>', methods=['GET','POST'])
def rate_image(image_id):
    try:
        iid = int(image_id)
    except ValueError:
        return "无效的图片ID", 400

    filename, current_score = db.get_image_meta(iid)
    if not filename:
        return "图片未找到", 404

    if request.method == 'POST':
        score = int(request.form.get('score', 0))
        if 1 <= score <= 5:
            db.set_score(iid, score)
        return redirect(request.referrer or url_for('show_images', page=request.args.get('page', 1)))
    return render_template_string(RATE_HTML, id=iid, filename=filename, current_score=current_score)

TAGS_HTML = CSS + '''
<h2>标签管理</h2>
<form method="post" style="margin-bottom:20px;">
  新标签: <input type="text" name="tag_name" required>
  <button type="submit">添加标签</button>
</form>
<table>
  <tr><th>ID</th><th>名称</th><th>图片数量</th><th>操作</th></tr>
  {% for tid, name, count in tags %}
    <tr>
      <td>{{ tid }}</td>
      <td>
        <a href="{{ url_for('tag_images', tag_id=tid) }}" class="tag-link">{{ name }}</a>
      </td>
      <td>{{ count }}</td>
      <td>
        <a href="{{ url_for('rename_tag_route', tag_id=tid) }}">改名</a> |
        <a href="{{ url_for('delete_tag_route', tag_id=tid) }}" onclick="return confirm('确定删除标签 \\'{{name}}\\' 吗？这不会删除图片，只会移除这个标签。')">删除</a>
      </td>
    </tr>
  {% endfor %}
</table>
<div class="pagination">
  {% if page>1 %}<a href="?page={{ page-1 }}">上一页</a>{% endif %}
  第 {{ page }} 页 / 共 {{ pages }} 页 (共 {{total_tags}} 个标签)
  {% if page<pages %}<a href="?page={{ page+1 }}">下一页</a>{% endif %}
</div>
<a href="/">返回首页</a>
<style>
  .tag-link { color: #2c3e50; text-decoration: none; font-weight: 500; }
  table { margin-top: 15px; }
  th { background-color: #34495e; }
  tr:hover { background-color: #f5f6fa; }
</style>
'''

@app.route('/tags', methods=['GET','POST'])
def manage_tags():
    if request.method == 'POST':
        tag_name = request.form.get('tag_name','').strip()
        if tag_name:
            try:
                db.add_tag(tag_name)
            except sqlite3.IntegrityError:
                pass
        return redirect(url_for('manage_tags'))
    page = request.args.get('page', 1, type=int)
    total = db.count_tags()
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE or 1
    offset = (page - 1) * PAGE_SIZE
    tags_data = db.list_tags_with_count_paginated(offset, PAGE_SIZE)
    return render_template_string(TAGS_HTML, tags=tags_data, page=page, pages=pages, total_tags=total)


TAG_RENAME_HTML = CSS + '''
<h2>重命名标签 "{{ old_name }}" (ID: {{ tag_id }})</h2>
<form method="post">
  新名称: <input type="text" name="new_name" value="{{ old_name }}" required><br>
  <button type="submit">保存</button>
</form>
<a href="{{ url_for('manage_tags') }}">返回标签管理</a>
'''
@app.route('/tags/rename/<int:tag_id>', methods=['GET','POST'])
def rename_tag_route(tag_id):
    cur = db.conn.cursor()
    cur.execute("SELECT name FROM tags WHERE id = ?", (tag_id,))
    tag_data = cur.fetchone()
    if not tag_data:
        return '标签未找到', 404
    old_name = tag_data[0]

    if request.method == 'POST':
        new_name = request.form.get('new_name','').strip()
        if new_name and new_name != old_name:
            try:
                db.rename_tag(tag_id, new_name)
            except sqlite3.IntegrityError:
                 return f"错误：标签 '{new_name}' 已存在。", 400
        return redirect(url_for('manage_tags'))
    return render_template_string(TAG_RENAME_HTML, tag_id=tag_id, old_name=old_name)

@app.route('/tags/delete/<int:tag_id>')
def delete_tag_route(tag_id):
    db.delete_tag(tag_id)
    return redirect(url_for('manage_tags'))

ASSIGN_HTML = CSS + '''
<h2>图片 {{ image_id }} ({{filename}}) 的标签</h2>
<img src="{{ url_for('get_image_route', image_id=image_id) }}" alt="Image {{image_id}}" style="max-width:200px; max-height:200px; display:block; margin: 10px 0;">
<form method="post">
  <div style="margin-bottom: 10px;">
    <input type="text" id="new-tag-input-assign" placeholder="新标签名称">
    <button type="button" id="add-new-tag-btn-assign">添加并选中新标签</button>
  </div>
  <div id="tags-checkbox-container-assign" style="max-height: 300px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
    {% for tid,name in all_tags %}
      <div>
        <input type="checkbox" name="tag_ids" value="{{ tid }}" id="assigntag_{{ tid }}" {% if tid in assigned_tag_ids %}checked{% endif %}>
        <label for="assigntag_{{ tid }}">{{ name }}</label>
      </div>
    {% endfor %}
  </div>
  <button type="submit" style="margin-top:10px;">保存标签</button>
</form>
<a href="{{ request.referrer or url_for('show_images') }}">返回</a>
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('add-new-tag-btn-assign').addEventListener('click', async function() {
    const newTagInput = document.getElementById('new-tag-input-assign');
    const tagName = newTagInput.value.trim();
    if (!tagName) { alert('请输入标签名称'); return; }
    try {
      const response = await fetch('{{ url_for("api_add_tag") }}', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name: tagName })
      });
      const data = await response.json();
      if (data.success && data.id) {
        const tagsContainer = document.getElementById('tags-checkbox-container-assign');
        if (!document.getElementById(\`assigntag_\${data.id}\`)) {
            const newTagHtml = \`
            <div>
                <input type="checkbox" name="tag_ids" value="\${data.id}" id="assigntag_\${data.id}" checked>
                <label for="assigntag_\${data.id}">\${data.name}</label>
            </div>\`;
            tagsContainer.insertAdjacentHTML('beforeend', newTagHtml);
        } else {
             document.getElementById(\`assigntag_\${data.id}\`).checked = true;
        }
        newTagInput.value = '';
      } else { alert('添加标签失败: ' + (data.error || "未知错误")); }
    } catch (err) { alert('操作失败: ' + err.message); }
  });
});
</script>
'''
@app.route('/tags/<int:image_id>', methods=['GET','POST'])
def assign_tags_route(image_id):
    filename, _ = db.get_image_meta(image_id)
    if not filename:
        return "图片未找到", 404

    if request.method == 'POST':
        selected_tag_ids = [int(tid) for tid in request.form.getlist('tag_ids')]
        cur = db.conn.cursor()
        cur.execute('DELETE FROM image_tags WHERE image_id = ?', (image_id,))
        for tag_id in selected_tag_ids:
            db.assign_tag(image_id, tag_id)
        db.conn.commit()
        return redirect(request.referrer or url_for('show_images'))

    all_tags = db.list_tags_paginated(0, 10000)
    assigned_tags = db.list_image_tags(image_id)
    assigned_tag_ids = [t[0] for t in assigned_tags]
    return render_template_string(ASSIGN_HTML, image_id=image_id, filename=filename, all_tags=all_tags, assigned_tag_ids=assigned_tag_ids)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)