import sqlite3
import io
import hashlib
import mimetypes
import random
import os
import tarfile
import tempfile
import threading
import time
from flask import Flask, request, render_template_string, send_file, redirect, url_for, jsonify

CSS = '''
<style>
  /* PIXIV风格配色和设计 */
  * {
    box-sizing: border-box;
  }
  
  body { 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
    color: #333;
  }
  
  /* 移动端适配 */
  @media (max-width: 768px) {
    body {
      padding: 10px;
    }
  }
  
  h1, h2 { 
    color: #0096fa;
    font-weight: 600;
    margin-bottom: 20px;
  }
  h1 {
    font-size: 28px;
    border-bottom: 2px solid #0096fa;
    padding-bottom: 10px;
  }
  h2 {
    font-size: 22px;
  }
  
  @media (max-width: 768px) {
    h1 {
      font-size: 22px;
      padding-bottom: 8px;
    }
    h2 {
      font-size: 18px;
    }
  }
  
  input, button, select { 
    padding: 8px 12px;
    margin: 5px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }
  
  @media (max-width: 768px) {
    input, button, select {
      padding: 10px 14px;
      font-size: 16px;
      margin: 4px;
    }
  }
  
  button, .delete-all-btn, .view-switch-btn {
    background-color: #0096fa;
    color: white;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s;
    -webkit-tap-highlight-color: transparent;
  }
  button:hover, .delete-all-btn:hover {
    background-color: #0081d8;
  }
  button:active, .delete-all-btn:active {
    background-color: #006bb3;
  }
  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  table { 
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 20px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
  }
  
  /* 移动端表格优化 */
  @media (max-width: 768px) {
    table {
      font-size: 14px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
    
    th, td {
      padding: 8px 6px;
      font-size: 13px;
    }
    
    /* 隐藏部分列以节省空间 */
    .hide-mobile {
      display: none;
    }
  }
  
  th, td { 
    border: none;
    border-bottom: 1px solid #f0f0f0;
    padding: 12px 16px;
    text-align: left;
  }
  tr:nth-child(even) { 
    background-color: #fafafa;
  }
  tr:hover {
    background-color: #f0f8ff;
  }
  th { 
    background-color: #0096fa;
    color: white;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 12px;
    letter-spacing: 0.5px;
  }
  
  a { 
    color: #0096fa;
    text-decoration: none;
    transition: color 0.2s;
  }
  a:hover { 
    color: #0081d8;
    text-decoration: underline;
  }
  a:active {
    color: #006bb3;
  }
  
  progress { 
    width: 100%;
    height: 24px;
    border-radius: 12px;
    overflow: hidden;
  }
  progress::-webkit-progress-bar {
    background-color: #f0f0f0;
    border-radius: 12px;
  }
  progress::-webkit-progress-value {
    background-color: #0096fa;
    border-radius: 12px;
  }
  
  .page-jump { 
    margin-top: 15px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  }
  
  @media (max-width: 768px) {
    .page-jump {
      padding: 12px;
      font-size: 14px;
    }
  }
  
  .action-bar { 
    margin: 15px 0;
    padding: 15px;
    background: white;
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  @media (max-width: 768px) {
    .action-bar {
      padding: 10px;
      gap: 6px;
    }
    
    .action-bar button {
      font-size: 14px;
      padding: 8px 12px;
    }
  }
  
  .checkbox-column { 
    width: 40px;
    text-align: center;
  }
  
  @media (max-width: 768px) {
    .checkbox-column {
      width: 30px;
    }
  }
  
  .image-viewer {
    text-align: center;
    position: relative;
    touch-action: pan-y;
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  @media (max-width: 768px) {
    .image-viewer {
      padding: 0;
      border-radius: 0;
      box-shadow: none;
      margin: 0;
      width: 100%;
      max-width: 100%;
    }
  }
  
  .viewer-image {
    max-width: 100%;
    max-height: 70vh;
    margin: 10px auto;
    display: block;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    border-radius: 4px;
    object-fit: contain;
  }
  
  @media (max-width: 768px) {
    .viewer-image {
      max-height: 60vh;
      box-shadow: none;
      border-radius: 0;
      margin: 0 auto;
      width: 100%;
      height: auto;
    }
  }
  
  .image-controls {
    background: #fafafa;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  }
  
  @media (max-width: 768px) {
    .image-controls {
      padding: 15px;
      margin: 15px 10px 10px 10px;
      border-radius: 8px;
    }
  }
  
  .tag-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 12px 0;
  }
  
  @media (max-width: 768px) {
    .tag-container {
      gap: 4px;
      margin: 8px 0;
    }
  }
  
  .tag-item {
    background: #e6f3ff;
    color: #0096fa;
    padding: 4px 12px;
    border-radius: 12px;
    display: inline-block;
    font-size: 13px;
    font-weight: 500;
  }
  
  @media (max-width: 768px) {
    .tag-item {
      padding: 4px 10px;
      font-size: 12px;
    }
  }
  
  .image-info {
    margin-bottom: 15px;
    font-size: 15px;
    color: #666;
  }
  
  @media (max-width: 768px) {
    .image-info {
      font-size: 14px;
      margin-bottom: 10px;
    }
  }
  
  .rating-stars {
    font-size: 28px;
    cursor: pointer;
  }
  
  @media (max-width: 768px) {
    .rating-stars {
      font-size: 32px;
    }
  }
  
  .rating-stars span {
    margin: 0 3px;
    color: #ffa500;
    transition: transform 0.2s;
  }
  .rating-stars span:hover {
    transform: scale(1.2);
  }
  .rating-stars span:active {
    transform: scale(0.9);
  }
  
  .view-switcher {
    margin: 20px 0;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  @media (max-width: 768px) {
    .view-switcher {
      padding: 10px;
      gap: 8px;
      margin: 10px 0;
    }
  }
  
  .view-switcher button, .view-switcher a.view-switch-btn {
    background: #f5f5f5;
    border: 1px solid #ddd;
    padding: 10px 20px;
    margin-right: 8px;
    cursor: pointer;
    border-radius: 6px;
    text-decoration: none;
    color: #666;
    display: inline-block;
    font-weight: 500;
    transition: all 0.2s;
  }
  
  @media (max-width: 768px) {
    .view-switcher button, .view-switcher a.view-switch-btn {
      padding: 10px 16px;
      font-size: 14px;
      margin-right: 4px;
      flex: 1;
      min-width: 100px;
      text-align: center;
    }
  }
  
  .view-switcher button:hover, .view-switcher a.view-switch-btn:hover {
    background: #e8f4ff;
    border-color: #0096fa;
    color: #0096fa;
  }
  .view-switcher button.active, .view-switcher a.view-switch-btn.active {
    background: #0096fa;
    color: white;
    border-color: #0096fa;
  }
  
  .gallery-view {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }
  
  @media (max-width: 768px) {
    .gallery-view {
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      margin-top: 10px;
    }
  }
  
  @media (max-width: 480px) {
    .gallery-view {
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }
  }
  
  .thumbnail {
    border: none;
    border-radius: 8px;
    padding: 0;
    transition: transform 0.2s, box-shadow 0.2s;
    background: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  @media (max-width: 768px) {
    .thumbnail {
      border-radius: 4px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
    }
  }
  
  .thumbnail:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0,150,250,0.2);
  }
  
  @media (max-width: 768px) {
    .thumbnail:active {
      transform: scale(0.98);
      box-shadow: 0 2px 8px rgba(0,150,250,0.2);
    }
  }
  
  .thumbnail img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 8px 8px 0 0;
    margin-bottom: 0;
  }
  
  @media (max-width: 768px) {
    .thumbnail img {
      height: 150px;
      border-radius: 4px 4px 0 0;
    }
  }
  
  @media (max-width: 480px) {
    .thumbnail img {
      height: 120px;
    }
  }
  
  .thumbnail-info {
    font-size: 0.9em;
    line-height: 1.4;
    padding: 12px;
  }
  
  @media (max-width: 768px) {
    .thumbnail-info {
      font-size: 0.85em;
      padding: 8px;
      line-height: 1.3;
    }
  }
  
  .thumbnail-tags {
    color: #666;
    font-size: 0.8em;
    margin-top: 8px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  @media (max-width: 768px) {
    .thumbnail-tags {
      font-size: 0.75em;
      margin-top: 6px;
      -webkit-line-clamp: 1;
    }
  }
  
  .thumbnail-actions {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #f0f0f0;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  
  @media (max-width: 768px) {
    .thumbnail-actions {
      margin-top: 8px;
      padding-top: 8px;
      gap: 4px;
    }
  }
  
  .thumbnail-actions a, .thumbnail-actions span {
    font-size: 0.75em;
    padding: 4px 10px;
    background: #f5f5f5;
    border-radius: 4px;
    white-space: nowrap;
    color: #666;
  }
  
  @media (max-width: 768px) {
    .thumbnail-actions a, .thumbnail-actions span {
      font-size: 0.7em;
      padding: 4px 8px;
    }
  }
  
  .thumbnail-actions a:hover {
    background: #e8f4ff;
    color: #0096fa;
  }
  
  .tag-cloud-compact {
    margin: 20px 0;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  @media (max-width: 768px) {
    .tag-cloud-compact {
      padding: 12px;
      gap: 6px;
      margin: 10px 0;
    }
  }
  
  .tag-cloud-compact h3 {
    width: 100%;
    margin: 0 0 15px 0;
    font-size: 18px;
    color: #0096fa;
    font-weight: 600;
  }
  
  @media (max-width: 768px) {
    .tag-cloud-compact h3 {
      font-size: 16px;
      margin-bottom: 10px;
    }
  }
  
  .tag-cloud-compact a {
    font-size: 13px !important;
    padding: 6px 14px;
    background: #e6f3ff;
    border-radius: 16px;
    display: inline-flex;
    align-items: center;
    transition: all 0.2s;
    text-decoration: none;
    color: #0096fa;
    font-weight: 500;
  }
  
  @media (max-width: 768px) {
    .tag-cloud-compact a {
      font-size: 12px !important;
      padding: 5px 12px;
    }
  }
  
  .tag-cloud-compact a:hover {
    background: #0096fa;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,150,250,0.3);
  }
  
  @media (max-width: 768px) {
    .tag-cloud-compact a:active {
      background: #0096fa;
      color: white;
      transform: scale(0.95);
    }
  }
  
  .tag-cloud-compact .tag-count {
    font-size: 11px;
    margin-left: 6px;
    background: rgba(0,0,0,0.1);
    color: inherit;
    padding: 2px 8px;
    border-radius: 10px;
    font-weight: 600;
  }
  
  @media (max-width: 768px) {
    .tag-cloud-compact .tag-count {
      font-size: 10px;
      padding: 2px 6px;
    }
  }
  
  .pagination { 
    margin-top: 25px;
    text-align: center;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
  }
  
  @media (max-width: 768px) {
    .pagination {
      padding: 15px 10px;
      margin-top: 15px;
      font-size: 14px;
    }
  }
  
  .pagination a {
    display: inline-block;
    padding: 8px 16px;
    margin: 0 5px;
    background: #f5f5f5;
    border-radius: 6px;
    color: #0096fa;
    font-weight: 500;
  }
  
  @media (max-width: 768px) {
    .pagination a {
      padding: 10px 14px;
      margin: 0 3px;
      font-size: 14px;
    }
  }
  
  .pagination a:hover {
    background: #0096fa;
    color: white;
  }
  
  .nav-arrows { 
    display: flex;
    justify-content: space-between;
    padding: 0 10px;
    margin-bottom: 15px;
  }
  
  @media (max-width: 768px) {
    .nav-arrows {
      padding: 0;
      margin-bottom: 10px;
      position: fixed;
      bottom: 20px;
      left: 0;
      right: 0;
      z-index: 1000;
      background: transparent;
      pointer-events: none;
    }
  }
  
  .nav-arrow { 
    background: #0096fa;
    border: none;
    padding: 12px 20px;
    cursor: pointer;
    border-radius: 6px;
    font-size: 1.5em;
    color: white;
    transition: background-color 0.2s;
  }
  
  @media (max-width: 768px) {
    .nav-arrow {
      background: rgba(0, 150, 250, 0.9);
      padding: 16px 24px;
      border-radius: 50%;
      font-size: 1.8em;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      pointer-events: auto;
      backdrop-filter: blur(10px);
    }
  }
  
  .nav-arrow:hover { 
    background: #0081d8;
  }
  
  @media (max-width: 768px) {
    .nav-arrow:active {
      background: rgba(0, 107, 179, 0.9);
      transform: scale(0.95);
    }
  }
  
  .delete-all-btn {
    background-color: #ff4757;
    color: white;
    padding: 10px 18px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    margin-left: 10px;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  @media (max-width: 768px) {
    .delete-all-btn {
      padding: 8px 14px;
      font-size: 14px;
      margin-left: 5px;
    }
  }
  
  .delete-all-btn:hover {
    background-color: #ee5a6f;
  }
  
  .batch-actions-gallery {
    margin: 15px 0;
    padding: 15px;
    background: white;
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  @media (max-width: 768px) {
    .batch-actions-gallery {
      padding: 10px;
      gap: 6px;
    }
  }
  
  ul {
    background: white;
    padding: 25px 40px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    list-style: none;
  }
  
  @media (max-width: 768px) {
    ul {
      padding: 15px 20px;
    }
  }
  
  ul li {
    padding: 10px 0;
    border-bottom: 1px solid #f0f0f0;
  }
  ul li:last-child {
    border-bottom: none;
  }
  ul li a {
    font-size: 15px;
    font-weight: 500;
    display: block;
  }
  
  @media (max-width: 768px) {
    ul li {
      padding: 12px 0;
    }
    ul li a {
      font-size: 16px;
    }
  }
  
  input[type="text"], input[type="number"], select {
    border: 1px solid #ddd;
    padding: 8px 12px;
    border-radius: 6px;
    transition: border-color 0.2s;
  }
  input[type="text"]:focus, input[type="number"]:focus, select:focus {
    outline: none;
    border-color: #0096fa;
    box-shadow: 0 0 0 3px rgba(0,150,250,0.1);
  }
  
  #selection-count {
    color: #0096fa;
    font-weight: 600;
    padding: 8px 15px;
    background: #e6f3ff;
    border-radius: 6px;
  }
  
  @media (max-width: 768px) {
    #selection-count {
      padding: 6px 12px;
      font-size: 13px;
    }
  }
  
  /* 移动端优化：添加触摸反馈 */
  @media (max-width: 768px) {
    button:active, a:active, .thumbnail:active {
      opacity: 0.7;
    }
  }
  
  /* viewport meta标签优化 */
  @viewport {
    width: device-width;
    zoom: 1.0;
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

    def get_next_image_id(self, current_id, context='all', context_value=None):
        """根据上下文获取下一张图片ID"""
        cur = self.conn.cursor()
        
        if context == 'tag' and context_value:
            # 标签上下文：获取同一标签的下一张图片
            cur.execute('''
                SELECT i.id FROM images i
                JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id = ? AND i.id > ?
                ORDER BY i.id ASC LIMIT 1
            ''', (context_value, current_id))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到第一张
            cur.execute('''
                SELECT i.id FROM images i
                JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id = ?
                ORDER BY i.id ASC LIMIT 1
            ''', (context_value,))
        elif context == 'untagged':
            # 未标记上下文：获取下一张未标记的图片
            cur.execute('''
                SELECT i.id FROM images i
                LEFT JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id IS NULL AND i.id > ?
                ORDER BY i.id ASC LIMIT 1
            ''', (current_id,))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到第一张
            cur.execute('''
                SELECT i.id FROM images i
                LEFT JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id IS NULL
                ORDER BY i.id ASC LIMIT 1
            ''')
        elif context == 'score' and context_value is not None:
            # 评分上下文：获取同一评分的下一张图片
            cur.execute('''
                SELECT id FROM images
                WHERE score = ? AND id > ?
                ORDER BY id ASC LIMIT 1
            ''', (context_value, current_id))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到第一张
            cur.execute('''
                SELECT id FROM images
                WHERE score = ?
                ORDER BY id ASC LIMIT 1
            ''', (context_value,))
        else:
            # 默认：所有图片
            cur.execute('SELECT id FROM images WHERE id > ? ORDER BY id ASC LIMIT 1', (current_id,))
            result = cur.fetchone()
            if result:
                return result[0]
            cur.execute('SELECT id FROM images ORDER BY id ASC LIMIT 1')
        
        result = cur.fetchone()
        return result[0] if result else None

    def get_prev_image_id(self, current_id, context='all', context_value=None):
        """根据上下文获取上一张图片ID"""
        cur = self.conn.cursor()
        
        if context == 'tag' and context_value:
            # 标签上下文：获取同一标签的上一张图片
            cur.execute('''
                SELECT i.id FROM images i
                JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id = ? AND i.id < ?
                ORDER BY i.id DESC LIMIT 1
            ''', (context_value, current_id))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到最后一张
            cur.execute('''
                SELECT i.id FROM images i
                JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id = ?
                ORDER BY i.id DESC LIMIT 1
            ''', (context_value,))
        elif context == 'untagged':
            # 未标记上下文：获取上一张未标记的图片
            cur.execute('''
                SELECT i.id FROM images i
                LEFT JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id IS NULL AND i.id < ?
                ORDER BY i.id DESC LIMIT 1
            ''', (current_id,))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到最后一张
            cur.execute('''
                SELECT i.id FROM images i
                LEFT JOIN image_tags it ON i.id = it.image_id
                WHERE it.tag_id IS NULL
                ORDER BY i.id DESC LIMIT 1
            ''')
        elif context == 'score' and context_value is not None:
            # 评分上下文：获取同一评分的上一张图片
            cur.execute('''
                SELECT id FROM images
                WHERE score = ? AND id < ?
                ORDER BY id DESC LIMIT 1
            ''', (context_value, current_id))
            result = cur.fetchone()
            if result:
                return result[0]
            # 循环到最后一张
            cur.execute('''
                SELECT id FROM images
                WHERE score = ?
                ORDER BY id DESC LIMIT 1
            ''', (context_value,))
        else:
            # 默认：所有图片
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
PAGE_SIZE = 100
db = SimpleDatabase('data.db')

# 导出进度跟踪
export_progress = {
    'status': 'idle',  # idle, processing, completed, error
    'current': 0,
    'total': 0,
    'message': '',
    'file_path': None
}

INDEX_HTML = CSS + '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
  <li><a href="{{ url_for('export_page') }}">导出所有图像</a></li>
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<h2>图片浏览器</h2>

<div class="image-viewer" id="imageViewer">
  <div class="nav-arrows">
    <button class="nav-arrow" id="prevBtn">&lt;</button>
    <button class="nav-arrow" id="nextBtn">&gt;</button>
  </div>
  
  <img class="viewer-image" src="{{ url_for('get_image_route', image_id=image_id) }}" 
       alt="{{ filename }}" id="currentImage">
  
  <div class="image-controls">
    <div class="image-info">
      <strong>文件名:</strong> {{ filename }} | 
      <strong>ID:</strong> {{ image_id }}
    </div>

    <div style="margin-top: 15px;">
      <button id="deleteBtn" style="background: #ff4444; color: white;">删除图片</button>
    </div>
    
    <div>
      <strong>评分:</strong>
      <div class="rating-stars" id="ratingStars">
        {% for i in range(1, 6) %}
          <span class="star" data-rating="{{ i }}">{{ '★' if i <= current_score else '☆' }}</span>
        {% endfor %}
      </div>
    </div>
    
    <div style="margin-top: 15px;">
      <strong>标签:</strong>
      <div class="tag-container" id="tagList">
        {% for tag_id, tag_name in image_tags %}
          <span class="tag-item">{{ tag_name }}</span>
        {% endfor %}
      </div>
      <button id="editTagsBtn">编辑标签</button>
    </div>
    
    <div id="tagEditor" style="display: none; margin-top: 15px; padding: 10px; border: 1px solid #ddd; background: #f9f9f9;">
      <h4>编辑标签</h4>
      <div id="tagCheckboxes">
{% for tag_id, tag_name in all_tags %}
  <div>
    <input 
      type="checkbox" 
      id="tag_${{ tag_id }}" 
      class="tag-checkbox" 
      value="{{ tag_id }}"
      {% if tag_id in image_tags|map(attribute=0)|list %}checked{% endif %}
    >
    <label for="tag_${{ tag_id }}">{{ tag_name }}</label>
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
    const deleteBtn = document.getElementById('deleteBtn');
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    document.addEventListener('keydown', function(e) {
      if (e.key === 'ArrowLeft') {
        navigateToImage({{ prev_id }});
      } else if (e.key === 'ArrowRight') {
        navigateToImage({{ next_id }});
      }
    });
    
    prevBtn.addEventListener('click', function() {
      navigateToImage({{ prev_id }});
    });
    
    nextBtn.addEventListener('click', function() {
      navigateToImage({{ next_id }});
    });
    
    function navigateToImage(imageId) {
      if (!imageId) return;
      let url = '/random_viewer?id=' + imageId;
      const context = '{{ context }}';
      const contextValue = '{{ context_value }}';
      if (context && context !== 'all') {
        url += '&context=' + context;
        if (contextValue) {
          url += '&context_value=' + contextValue;
        }
      }
      window.location.href = url;
    }
    
    imageViewer.addEventListener('touchstart', function(e) {
      touchStartX = e.changedTouches[0].screenX;
    }, false);
    
    imageViewer.addEventListener('touchend', function(e) {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, false);
    
    function handleSwipe() {
      const swipeThreshold = 50;
      if (touchEndX < touchStartX - swipeThreshold) {
        navigateToImage({{ next_id }});
      }
      if (touchEndX > touchStartX + swipeThreshold) {
        navigateToImage({{ prev_id }});
      }
    }
    
    ratingStars.addEventListener('click', function(e) {
      if (e.target.classList.contains('star')) {
        const rating = e.target.dataset.rating;
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
            document.querySelectorAll('.star').forEach(star => {
              const starRating = parseInt(star.dataset.rating);
              star.textContent = starRating <= rating ? '★' : '☆';
            });
          }
        });
      }
    });
    
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
          window.location.reload();
        }
      });
    });
    
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

    deleteBtn.addEventListener('click', function() {
        if (confirm('确定要永久删除这张图片吗？')) {
            const urlParams = new URLSearchParams(window.location.search);
            const context = urlParams.get('context') || 'all';
            const contextValue = urlParams.get('context_value') || '';
            let deleteUrl = '/delete_image_from_viewer/' + currentImageId;
            if (context !== 'all') {
                deleteUrl += '?context=' + context;
                if (contextValue) {
                    deleteUrl += '&context_value=' + contextValue;
                }
            }
            
            fetch(deleteUrl, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else if (data.error) {
                    alert('删除失败: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('删除操作失败');
            });
        }
    });
  });
</script>
'''

@app.route('/delete_image_from_viewer/<int:image_id>', methods=['POST'])
def delete_image_from_viewer(image_id):
    try:
        # 获取上下文参数
        context = request.args.get('context', 'all')
        context_value = request.args.get('context_value', type=int)
        
        next_id_after_delete = db.get_next_image_id(image_id, context, context_value)
        prev_id_after_delete = db.get_prev_image_id(image_id, context, context_value)

        db.delete_image(image_id)

        if next_id_after_delete and next_id_after_delete != image_id:
            return jsonify({'redirect_url': url_for('random_viewer', id=next_id_after_delete, context=context, context_value=context_value)})
        elif prev_id_after_delete and prev_id_after_delete != image_id:
            return jsonify({'redirect_url': url_for('random_viewer', id=prev_id_after_delete, context=context, context_value=context_value)})
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
    context = request.args.get('context', 'all')  # all, tag, untagged, score
    context_value = request.args.get('context_value', type=int)  # tag_id or score value
    
    if not image_id:
        image_id = db.get_random_image_id()
        if not image_id:
            return "没有可用的图片", 404
        return redirect(url_for('random_viewer', id=image_id, context=context, context_value=context_value))

    filename, current_score = db.get_image_meta(image_id)
    if not filename:
        new_random_id = db.get_random_image_id()
        if new_random_id:
            return redirect(url_for('random_viewer', id=new_random_id, context=context, context_value=context_value))
        else:
            return "图片不存在，且数据库中已无其他图片。", 404

    # 根据上下文获取上一张和下一张图片ID
    prev_id = db.get_prev_image_id(image_id, context, context_value)
    next_id = db.get_next_image_id(image_id, context, context_value)

    image_tags = db.list_image_tags(image_id)
    all_tags = db.list_tags_paginated(0, 10000)

    return render_template_string(
        RANDOM_VIEWER_HTML,
        image_id=image_id,
        filename=filename,
        current_score=current_score,
        prev_id=prev_id,
        next_id=next_id,
        context=context,
        context_value=context_value or '',
        image_tags=image_tags,
        all_tags=all_tags
    )

IMAGES_HTML_BASE = CSS + '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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

<form id="batch-form" action="{{ url_for('batch_tags') }}" method="post">
  <input type="hidden" name="current_page" value="{{ page }}">
  <input type="hidden" name="current_view_type" value="{{ view_type }}">
  {% if tag_id %}<input type="hidden" name="current_tag_id" value="{{ tag_id }}">{% endif %}
  {% if untagged %}<input type="hidden" name="current_untagged" value="true">{% endif %}
  {% if one_star %}<input type="hidden" name="current_one_star" value="true">{% endif %}
  <div class="action-bar {% if view_type == 'gallery' %}batch-actions-gallery{% endif %}">
    <button type="submit" id="batch-tag-btn">批量修改标签</button>
    <button type="button" id="batch-rename-btn" onclick="submitToBatchRename()">批量重命名</button>
    <span id="selection-count">已选择: 0 个图片</span>
    <button type="button" id="select-all">全选</button>
    <button type="button" id="deselect-all">取消全选</button>
    <a href="{{ url_for('random_viewer') }}" style="float: right;">随机浏览图片</a>
  </div>

{% if view_type == 'list' %}
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
        <a href="{{ url_for('random_viewer', id=iid, context='tag' if tag_id else ('untagged' if untagged else ('score' if one_star else 'all')), context_value=tag_id if tag_id else (1 if one_star else None)) }}">浏览</a> |
        <a href="{{ url_for('rate_image', image_id=iid) }}">评分</a> |
        <a href="{{ url_for('assign_tags_route', image_id=iid) }}">标记标签</a> |
        <a href="{{ url_for('delete_image_from_list_route', image_id=iid, current_page=page, view_type=view_type, tag_id=tag_id if tag_id else '', untagged=untagged if untagged else '', one_star=one_star if one_star else '') }}" onclick="return confirm('确定删除图片 {{fname}} (ID: {{iid}})?')">删除</a>
      </td>
    </tr>
    {% endfor %}
  </table>
{% else %}
<div class="gallery-view">
  {% for iid, fname, score, tags in images %}
  <div class="thumbnail">
    <a href="{{ url_for('random_viewer', id=iid, context='tag' if tag_id else ('untagged' if untagged else ('score' if one_star else 'all')), context_value=tag_id if tag_id else (1 if one_star else None)) }}">
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
        <input type="checkbox" name="image_ids" value="{{ iid }}" class="image-checkbox" style="margin-left: auto;">
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endif %}
</form>

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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
            if not ext_part:
                ext_part = ''
            new_filename = f"{tag_prefix}_{index:03d}{ext_part}"
            db.rename_image(image_id, new_filename)
        else:
            print(f"警告: 批量重命名时未找到图片ID {image_id}。")
    return redirect(request.referrer or url_for('show_images'))


@app.route('/images')
def show_images():
    view_type = request.args.get('view', 'gallery')  # 默认相册视图
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
    view_type = request.args.get('view', 'gallery')  # 默认相册视图
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
    view_type = request.args.get('view', 'gallery')  # 默认相册视图
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
    view_type = request.args.get('view', 'gallery')  # 默认相册视图
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
        <input type="checkbox" name="tag_ids" value="{{ tid }}" id="tag_${{ tid }}">
        <label for="tag_${{ tid }}">{{ name }}</label>
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
    
    all_tags = db.list_tags_paginated(0, 1000)
    
    return render_template_string(BATCH_TAGS_HTML, image_ids=image_ids, all_tags=all_tags)

@app.route('/batch_tags_update', methods=['POST'])
def batch_tags_update():
    image_ids = [int(id) for id in request.form.getlist('image_ids')]
    tag_ids = [int(id) for id in request.form.getlist('tag_ids')]
    operation = request.form.get('operation', 'replace')

    current_page = request.form.get('current_page', '1', type=int)
    current_view_type = request.form.get('current_view_type', 'list')
    current_tag_id = request.form.get('current_tag_id', type=int)
    current_untagged = request.form.get('current_untagged') == 'true'
    current_one_star = request.form.get('current_one_star') == 'true'

    if not image_ids:
        if current_one_star:
            return redirect(url_for('show_one_star_images', page=current_page, view=current_view_type))
        elif current_untagged:
            return redirect(url_for('show_untagged_images', page=current_page, view=current_view_type))
        elif current_tag_id:
            return redirect(url_for('tag_images', tag_id=current_tag_id, page=current_page, view=current_view_type))
        else:
            return redirect(url_for('show_images', page=current_page, view=current_view_type))

    db.batch_update_tags(image_ids, tag_ids, operation)

    if current_one_star:
        redirect_url = url_for('show_one_star_images', page=current_page, view=current_view_type)
    elif current_untagged:
        redirect_url = url_for('show_untagged_images', page=current_page, view=current_view_type)
    elif current_tag_id:
        redirect_url = url_for('tag_images', tag_id=current_tag_id, page=current_page, view=current_view_type)
    else:
        redirect_url = url_for('show_images', page=current_page, view=current_view_type)
    
    return redirect(redirect_url)

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
            return jsonify({'success': True, 'id': existing_tag[0], 'name': tag_name, 'message': '标签已存在'})
        return jsonify({'success': False, 'error': '标签已存在但无法检索ID。'})
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
    fileStatus.textContent = `上传 ${i+1}/${files.length}: ${file.name}`;
    statusEl.appendChild(fileStatus);
    try {
      const res = await fetch('{{ url_for("upload_async") }}', { method: 'POST', body: form });
      const data = await res.json();
      if (res.ok && data.id) {
        fileStatus.textContent += ` 完成 (ID: ${data.id})`;
      } else {
        fileStatus.textContent += ` 失败: ${data.error || '未知错误'}`;
        fileStatus.style.color = 'red';
      }
    } catch (e) {
      fileStatus.textContent += ` 失败: ${e}`;
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
        return jsonify({'error': '没有文件'}), 400
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
        <input type="checkbox" name="tag_ids" value="{{ tid }}" id="assigntag_${{ tid }}" {% if tid in assigned_tag_ids %}checked{% endif %}>
        <label for="assigntag_${{ tid }}">{{ name }}</label>
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
        if (!document.getElementById(`assigntag_${data.id}`)) {
            const newTagHtml = `
            <div>
                <input type="checkbox" name="tag_ids" value="${data.id}" id="assigntag_${data.id}" checked>
                <label for="assigntag_${data.id}">${data.name}</label>
            </div>`;
            tagsContainer.insertAdjacentHTML('beforeend', newTagHtml);
        } else {
             document.getElementById(`assigntag_${data.id}`).checked = true;
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

EXPORT_PAGE_HTML = CSS + '''
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<h2>导出所有图像</h2>
<div style="max-width: 600px; margin: 20px auto;">
  <button id="startExportBtn" onclick="startExport()" style="padding: 10px 20px; font-size: 16px;">开始导出</button>
  <div id="progressContainer" style="display: none; margin-top: 20px;">
    <div style="margin-bottom: 10px;">
      <strong>进度：</strong><span id="progressText">0 / 0</span>
    </div>
    <progress id="progressBar" max="100" value="0" style="width: 100%; height: 30px;"></progress>
    <div id="statusMessage" style="margin-top: 10px; color: #666;"></div>
    <div id="downloadContainer" style="display: none; margin-top: 20px;">
      <a id="downloadLink" href="#" class="delete-all-btn" style="background-color: #4CAF50;">下载导出文件</a>
    </div>
  </div>
</div>
<a href="/">返回首页</a>

<script>
let progressCheckInterval = null;

function startExport() {
  document.getElementById('startExportBtn').disabled = true;
  document.getElementById('progressContainer').style.display = 'block';
  document.getElementById('downloadContainer').style.display = 'none';
  
  // 开始导出
  fetch('/api/start_export', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // 开始轮询进度
        progressCheckInterval = setInterval(checkProgress, 500);
      } else {
        alert('启动导出失败: ' + data.error);
        document.getElementById('startExportBtn').disabled = false;
      }
    })
    .catch(error => {
      alert('启动导出失败: ' + error);
      document.getElementById('startExportBtn').disabled = false;
    });
}

function checkProgress() {
  fetch('/api/export_progress')
    .then(response => response.json())
    .then(data => {
      const progressBar = document.getElementById('progressBar');
      const progressText = document.getElementById('progressText');
      const statusMessage = document.getElementById('statusMessage');
      
      progressText.textContent = data.current + ' / ' + data.total;
      statusMessage.textContent = data.message;
      
      if (data.total > 0) {
        const percent = Math.round((data.current / data.total) * 100);
        progressBar.value = percent;
      }
      
      if (data.status === 'completed') {
        clearInterval(progressCheckInterval);
        document.getElementById('downloadContainer').style.display = 'block';
        document.getElementById('downloadLink').href = '/download_export';
        statusMessage.textContent = '导出完成！';
        statusMessage.style.color = '#4CAF50';
      } else if (data.status === 'error') {
        clearInterval(progressCheckInterval);
        statusMessage.textContent = '导出失败: ' + data.message;
        statusMessage.style.color = '#ff4444';
        document.getElementById('startExportBtn').disabled = false;
      }
    })
    .catch(error => {
      console.error('检查进度失败:', error);
    });
}
</script>
'''

@app.route('/export_page')
def export_page():
    """导出页面"""
    return render_template_string(EXPORT_PAGE_HTML)

@app.route('/api/start_export', methods=['POST'])
def start_export():
    """开始导出任务"""
    global export_progress
    
    if export_progress['status'] == 'processing':
        return jsonify({'success': False, 'error': '已有导出任务正在进行中'})
    
    # 重置进度
    export_progress = {
        'status': 'processing',
        'current': 0,
        'total': 0,
        'message': '正在准备...',
        'file_path': None
    }
    
    # 在后台线程执行导出
    thread = threading.Thread(target=do_export)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True})

@app.route('/api/export_progress')
def get_export_progress():
    """获取导出进度"""
    return jsonify(export_progress)

@app.route('/download_export')
def download_export():
    """下载导出的文件"""
    global export_progress
    
    if export_progress['status'] != 'completed' or not export_progress['file_path']:
        return "文件未就绪", 404
    
    file_path = export_progress['file_path']
    if not os.path.exists(file_path):
        return "文件不存在", 404
    
    return send_file(
        file_path,
        mimetype='application/x-tar',
        as_attachment=True,
        download_name='exported_images.tar'
    )

def do_export():
    """执行导出任务（后台线程）"""
    global export_progress
    temp_tar = None
    
    try:
        # 获取所有图像ID
        all_image_ids = db.get_all_image_ids()
        
        if not all_image_ids:
            export_progress['status'] = 'error'
            export_progress['message'] = '没有可导出的图像'
            return
        
        export_progress['total'] = len(all_image_ids)
        export_progress['message'] = f'开始导出 {len(all_image_ids)} 张图片...'
        
        # 创建临时TAR文件（无压缩，速度更快）
        temp_tar = tempfile.NamedTemporaryFile(delete=False, suffix='.tar')
        
        with tarfile.open(temp_tar.name, 'w') as tarf:
            # 用于跟踪每个标签组合的序号
            name_counter = {}
            
            for idx, image_id in enumerate(all_image_ids, 1):
                # 更新进度
                export_progress['current'] = idx
                export_progress['message'] = f'正在处理第 {idx}/{len(all_image_ids)} 张图片...'
                
                # 获取图像数据和元信息
                filename, data = db.get_image(image_id)
                if not data or not filename:
                    continue
                
                # 获取图像的标签
                tags = db.list_image_tags(image_id)
                tag_names = [tag[1] for tag in tags]
                
                # 获取文件扩展名
                _, ext = os.path.splitext(filename)
                if not ext:
                    # 尝试从MIME类型推断扩展名
                    mime, _ = mimetypes.guess_type(filename)
                    if mime:
                        ext = mimetypes.guess_extension(mime) or ''
                
                # 构建新文件名
                if tag_names:
                    # 有标签：标签名1_标签名2_……__序号
                    tag_prefix = '_'.join(sorted(tag_names))
                else:
                    # 无标签：UKNOW_序号
                    tag_prefix = 'UKNOW'
                
                # 获取并更新序号
                if tag_prefix not in name_counter:
                    name_counter[tag_prefix] = 0
                name_counter[tag_prefix] += 1
                
                # 生成最终文件名
                if tag_names:
                    new_filename = f"{tag_prefix}__{name_counter[tag_prefix]:03d}{ext}"
                else:
                    new_filename = f"{tag_prefix}_{name_counter[tag_prefix]:03d}{ext}"
                
                # 写入TAR文件（使用BytesIO避免创建临时文件）
                tarinfo = tarfile.TarInfo(name=new_filename)
                tarinfo.size = len(data)
                tarf.addfile(tarinfo, io.BytesIO(data))
        
        # 导出完成
        export_progress['status'] = 'completed'
        export_progress['message'] = f'成功导出 {len(all_image_ids)} 张图片'
        export_progress['file_path'] = temp_tar.name
        
    except Exception as e:
        export_progress['status'] = 'error'
        export_progress['message'] = str(e)
        # 清理临时文件
        try:
            if temp_tar is not None:
                os.unlink(temp_tar.name)
        except:
            pass

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
