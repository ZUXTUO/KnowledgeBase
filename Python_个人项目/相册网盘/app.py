import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, g
import math

DATABASE = 'data.db'
IMAGES_PER_PAGE = 50
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
app.secret_key = os.urandom(24)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                data BLOB NOT NULL,
                score INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_tags (
                image_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (image_id, tag_id),
                FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')
        db.commit()

with app.app_context():
    init_db()

def get_image_tags_string(conn, image_id):
    tags_cursor = conn.execute('''
        SELECT t.name
        FROM tags t
        JOIN image_tags it ON t.id = it.tag_id
        WHERE it.image_id = ?
    ''', (image_id,))
    tags = [row['name'] for row in tags_cursor.fetchall()]
    return ', '.join(tags) if tags else ''

def query_images(page, tag_name=None, min_score=None):
    conn = get_db()
    offset = (page - 1) * IMAGES_PER_PAGE

    base_query_fields = "SELECT i.id, i.filename, i.score FROM images i "
    count_query_base = "SELECT COUNT(DISTINCT i.id) as total FROM images i "
    
    where_clauses = []
    params = []
    count_params = []

    if tag_name:
        join_clause = "JOIN image_tags it ON i.id = it.image_id JOIN tags t ON it.tag_id = t.id "
        where_clauses.append("t.name = ?")
        params.append(tag_name)
        count_params.append(tag_name)
    else:
        join_clause = ""

    if min_score is not None:
        where_clauses.append("i.score >= ?")
        params.append(min_score)
        count_params.append(min_score)

    where_string = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query_fields = base_query_fields + join_clause + where_string + " GROUP BY i.id ORDER BY i.id DESC LIMIT ? OFFSET ?"
    count_query = count_query_base + join_clause + where_string

    params.extend([IMAGES_PER_PAGE, offset])

    images_cursor = conn.execute(query_fields, tuple(params))
    images_data = images_cursor.fetchall()

    images = []
    for row in images_data:
        image_dict = dict(row)
        image_dict['tags_string'] = get_image_tags_string(conn, row['id'])
        images.append(image_dict)
    
    total_images_row = conn.execute(count_query, tuple(count_params)).fetchone()
    total_images = total_images_row['total'] if total_images_row else 0
    total_pages = math.ceil(total_images / IMAGES_PER_PAGE)
    
    return images, total_images, total_pages

@app.route('/')
@app.route('/page/<int:page>')
def index(page=1):
    images, total_images, total_pages = query_images(page)
    conn = get_db()
    all_tags_cursor = conn.execute('SELECT name FROM tags ORDER BY name')
    all_tags = [row['name'] for row in all_tags_cursor.fetchall()]
    return render_template('index.html', images=images, current_page=page, total_pages=total_pages, all_tags=all_tags, current_tag_name=None, total_images_count=total_images, current_page_type='all')

@app.route('/tag/<tag_name>')
@app.route('/tag/<tag_name>/page/<int:page>')
def tag_gallery(tag_name, page=1):
    images, total_images, total_pages = query_images(page, tag_name=tag_name)
    conn = get_db()
    all_tags_cursor = conn.execute('SELECT name FROM tags ORDER BY name')
    all_tags = [row['name'] for row in all_tags_cursor.fetchall()]
    return render_template('index.html', images=images, current_page=page, total_pages=total_pages, all_tags=all_tags, current_tag_name=tag_name, total_images_count=total_images, current_page_type='tag')

@app.route('/featured')
@app.route('/featured/page/<int:page>')
def featured_gallery(page=1):
    images, total_images, total_pages = query_images(page, min_score=5)
    conn = get_db()
    all_tags_cursor = conn.execute('SELECT name FROM tags ORDER BY name')
    all_tags = [row['name'] for row in all_tags_cursor.fetchall()]
    return render_template('index.html', images=images, current_page=page, total_pages=total_pages, all_tags=all_tags, current_tag_name=None, total_images_count=total_images, current_page_type='featured')

@app.route('/image/<int:image_id>')
def image_detail(image_id):
    conn = get_db()
    image_row = conn.execute('SELECT id, filename, score FROM images WHERE id = ?', (image_id,)).fetchone()
    if not image_row:
        return "Image not found", 404

    tags_string = get_image_tags_string(conn, image_id)
    image_data = dict(image_row)
    image_data['tags'] = tags_string

    # Get previous and next image IDs for navigation
    all_image_ids_cursor = conn.execute('SELECT id FROM images ORDER BY id DESC').fetchall()
    all_image_ids = [row['id'] for row in all_image_ids_cursor]
    
    current_index = -1
    try:
        current_index = all_image_ids.index(image_id)
    except ValueError:
        pass # image_id not found in the list, though it should be if image_row exists

    prev_image_id = None
    next_image_id = None

    if current_index != -1:
        if current_index < len(all_image_ids) - 1:
            next_image_id = all_image_ids[current_index + 1]
        if current_index > 0:
            prev_image_id = all_image_ids[current_index - 1]

    return render_template('image_detail.html', image=image_data, prev_image_id=prev_image_id, next_image_id=next_image_id)


@app.route('/image_data/<int:image_id>')
def get_image_data(image_id):
    conn = get_db()
    image_row = conn.execute('SELECT data, filename FROM images WHERE id = ?', (image_id,)).fetchone()
    if image_row and image_row['data']:
        mimetype = 'image/jpeg'
        if '.' in image_row['filename']:
            ext = image_row['filename'].rsplit('.', 1)[1].lower()
            if ext == 'png': mimetype = 'image/png'
            elif ext == 'gif': mimetype = 'image/gif'
            elif ext == 'webp': mimetype = 'image/webp'
        return Response(image_row['data'], mimetype=mimetype)
    return 'Image not found', 404

@app.route('/api/image_details/<int:image_id>')
def image_details_api(image_id):
    conn = get_db()
    image_row = conn.execute('SELECT id, filename, score FROM images WHERE id = ?', (image_id,)).fetchone()
    if not image_row:
        return jsonify({'error': 'Image not found'}), 404
    
    tags_string = get_image_tags_string(conn, image_id)
    
    image_data = dict(image_row)
    image_data['tags'] = tags_string
    return jsonify(image_data)

@app.route('/api/update_score/<int:image_id>', methods=['POST'])
def update_score_api(image_id):
    conn = get_db()
    try:
        score = int(request.form['score'])
        if not (0 <= score <= 5):
            return jsonify({'success': False, 'message': '评分必须在0到5之间'}), 400
        
        conn.execute('UPDATE images SET score = ? WHERE id = ?', (score, image_id))
        conn.commit()
        return jsonify({'success': True, 'message': '评分已更新'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/update_tags/<int:image_id>', methods=['POST'])
def update_tags_api(image_id):
    conn = get_db()
    try:
        tags_str = request.form.get('tags', '')
        tag_names = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        conn.execute('DELETE FROM image_tags WHERE image_id = ?', (image_id,))
        
        for tag_name in tag_names:
            tag_row = conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()
            if tag_row:
                tag_id = tag_row['id']
            else:
                cursor = conn.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                tag_id = cursor.lastrowid
            conn.execute('INSERT INTO image_tags (image_id, tag_id) VALUES (?, ?)', (image_id, tag_id))
        
        conn.commit()
        new_tags_string = get_image_tags_string(conn, image_id)
        return jsonify({'success': True, 'message': '标签已更新', 'new_tags_string': new_tags_string})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/all_tags')
def get_all_tags_api():
    conn = get_db()
    tags_cursor = conn.execute('SELECT id, name FROM tags ORDER BY name')
    tags_list = [{'id': row['id'], 'name': row['name']} for row in tags_cursor.fetchall()]
    return jsonify(tags_list)

@app.route('/api/upload_image', methods=['POST'])
def upload_image_api():
    conn = get_db()
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': '没有图片文件'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        if file:
            filename = file.filename
            data = file.read()
            cursor = conn.execute('INSERT INTO images (filename, data, score) VALUES (?, ?, ?)', (filename, data, 0))
            conn.commit()
            return jsonify({'success': True, 'message': '图片上传成功', 'image_id': cursor.lastrowid})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete_image/<int:image_id>', methods=['DELETE'])
def delete_image_api(image_id):
    conn = get_db()
    try:
        cursor = conn.execute('DELETE FROM images WHERE id = ?', (image_id,))
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '图片未找到'}), 404
        conn.commit()
        return jsonify({'success': True, 'message': '图片已删除'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/add_tag', methods=['POST'])
def add_tag_api():
    conn = get_db()
    try:
        tag_name = request.json.get('tag_name')
        if not tag_name:
            return jsonify({'success': False, 'message': '标签名称不能为空'}), 400
        
        existing_tag = conn.execute('SELECT id FROM tags WHERE name = ?', (tag_name,)).fetchone()
        if existing_tag:
            return jsonify({'success': False, 'message': '标签已存在', 'tag_id': existing_tag['id']}), 409
            
        cursor = conn.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        conn.commit()
        return jsonify({'success': True, 'message': '标签添加成功', 'tag_id': cursor.lastrowid, 'tag_name': tag_name})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/delete_tag/<int:tag_id>', methods=['DELETE'])
def delete_tag_api(tag_id):
    conn = get_db()
    try:
        cursor = conn.execute('DELETE FROM tags WHERE id = ?', (tag_id,))
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': '标签未找到'}), 404
        conn.commit()
        return jsonify({'success': True, 'message': '标签已删除'})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        print(f"数据库文件 '{DATABASE}' 不存在，正在创建...")
        init_db()
    
    app.run(debug=True)
