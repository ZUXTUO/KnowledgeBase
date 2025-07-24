import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import os
import datetime
import uuid
import hashlib
import threading
import queue
import math
import tempfile
import string

try:
    import fitz
except ImportError:
    messagebox.showwarning("警告", "未安装PyMuPDF库。PDF转换功能将不可用。\n请运行 'pip install PyMuPDF' 进行安装。")
    fitz = None

try:
    from blind_watermark import WaterMark
except ImportError:
    messagebox.showwarning("警告", "未安装blind-watermark库。数字盲水印功能将不可用。\n请运行 'pip install blind-watermark' 进行安装。")
    WaterMark = None

CUSTOM_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "HarmonyOS_Sans_SC_Medium.ttf")
CUSTOM_FONT_FAMILY = "HarmonyOS Sans SC Medium"

def get_pil_font(size):
    try:
        if os.path.exists(CUSTOM_FONT_PATH):
            return ImageFont.truetype(CUSTOM_FONT_PATH, size)
        else:
            messagebox.showwarning("警告", f"未找到字体文件: {CUSTOM_FONT_PATH}，将使用默认字体。")
            return ImageFont.load_default()
    except Exception as e:
        messagebox.showwarning("警告", f"加载自定义字体时发生错误: {e}，将使用默认字体。")
        return ImageFont.load_default()

class ImageViewer:
    def __init__(self, master, pil_images):
        self.master = master
        self.master.title("解密查看器（严禁保存）")
        self.master.geometry("900x700")
        self.master.configure(bg="#F8F8F8")

        self.pil_images = pil_images
        self.current_page_index = 0
        self.total_pages = len(pil_images)

        if not self.pil_images:
            messagebox.showerror("错误", "没有可供查看的图像。")
            self.master.destroy()
            return

        self.original_image = self.pil_images[self.current_page_index]
        self.current_image = self.original_image.copy()
        self.tk_image = ImageTk.PhotoImage(self.current_image)
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0

        self.canvas = tk.Canvas(master, bg="#EFEFEF", bd=2, relief=tk.FLAT, highlightbackground="#DDDDDD")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.master.after(100, self.fit_to_window)

        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        control_frame = tk.Frame(master, padx=15, pady=10, bg="#F8F8F8")
        control_frame.pack(side=tk.BOTTOM, fill=tk.X)

        button_style_args = {
            "height": 1,
            "width": 12,
            "font": (CUSTOM_FONT_FAMILY, 10, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "activebackground": "#45a049",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2"
        }

        tk.Button(control_frame, text="放大 (+)", command=self.zoom_in, **button_style_args).pack(side=tk.LEFT, padx=8, pady=5)
        tk.Button(control_frame, text="缩小 (-)", command=self.zoom_out, **button_style_args).pack(side=tk.LEFT, padx=8, pady=5)
        tk.Button(control_frame, text="还原大小 (1:1)", command=self.reset_zoom, **button_style_args).pack(side=tk.LEFT, padx=8, pady=5)
        tk.Button(control_frame, text="适应窗口", command=self.fit_to_window, **button_style_args).pack(side=tk.LEFT, padx=8, pady=5)

        self.prev_button = tk.Button(control_frame, text="上一页", command=self.prev_page, **button_style_args)
        self.prev_button.pack(side=tk.LEFT, padx=(20, 8), pady=5)

        self.page_label = tk.Label(control_frame, text=f"页码: {self.current_page_index + 1}/{self.total_pages}",
                                   font=(CUSTOM_FONT_FAMILY, 10, "bold"), bg="#F8F8F8", fg="#333333")
        self.page_label.pack(side=tk.LEFT, padx=8)

        self.next_button = tk.Button(control_frame, text="下一页", command=self.next_page, **button_style_args)
        self.next_button.pack(side=tk.LEFT, padx=8, pady=5)

        self._update_page_buttons_state()

    def center_image(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = self.current_image.width
        image_height = self.current_image.height

        x_offset = (canvas_width - image_width) / 2 if canvas_width > image_width else 0
        y_offset = (canvas_height - image_height) / 2 if canvas_height > image_height else 0

        self.canvas.coords(self.image_on_canvas, x_offset, y_offset)
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_on_canvas))

    def update_image_display(self):
        self.original_image = self.pil_images[self.current_page_index]
        new_width = int(self.original_image.width * self.zoom_level)
        new_height = int(self.original_image.height * self.zoom_level)

        if new_width <= 0 or new_height <= 0:
            return

        self.current_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.current_image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.tk_image)
        self.center_image()
        self.page_label.config(text=f"页码: {self.current_page_index + 1}/{self.total_pages}")
        self._update_page_buttons_state()

    def _update_page_buttons_state(self):
        if self.current_page_index == 0:
            self.prev_button.config(state=tk.DISABLED, bg="#CCCCCC")
        else:
            self.prev_button.config(state=tk.NORMAL, bg="#4CAF50")

        if self.current_page_index == self.total_pages - 1:
            self.next_button.config(state=tk.DISABLED, bg="#CCCCCC")
        else:
            self.next_button.config(state=tk.NORMAL, bg="#4CAF50")

    def next_page(self):
        if self.current_page_index < self.total_pages - 1:
            self.current_page_index += 1
            self.fit_to_window()

    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.fit_to_window()

    def on_mouse_wheel(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_level *= 1.1
        elif event.delta < 0 or event.num == 5:
            self.zoom_level /= 1.1

        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level))
        self.update_image_display()

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.zoom_level = min(self.max_zoom, self.zoom_level)
        self.update_image_display()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.zoom_level = max(self.min_zoom, self.zoom_level)
        self.update_image_display()

    def reset_zoom(self):
        self.zoom_level = 1.0
        self.update_image_display()

    def fit_to_window(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width == 0 or canvas_height == 0:
            self.master.after(100, self.fit_to_window)
            return

        img_width, img_height = self.original_image.size
        if img_width == 0 or img_height == 0:
            return

        width_ratio = canvas_width / img_width
        height_ratio = canvas_height / img_height
        self.zoom_level = min(width_ratio, height_ratio)
        self.zoom_level = max(self.min_zoom, min(self.max_zoom, self.zoom_level))
        self.update_image_display()

    def on_button_press(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def on_mouse_drag(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_canvas_resize(self, event):
        self.center_image()

def convert_pdf_to_images(pdf_path, q_log=None):
    if fitz is None:
        if q_log: q_log.put({'type': 'log', 'message': "错误: PyMuPDF库未安装，无法转换PDF。"})
        raise ImportError("PyMuPDF (fitz) is not installed.")

    images = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(200/72, 200/72))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        doc.close()
        if q_log: q_log.put({'type': 'log', 'message': f"PDF '{os.path.basename(pdf_path)}' 已转换为 {len(images)} 张图像。"})
        return images
    except Exception as e:
        if q_log: q_log.put({'type': 'log', 'message': f"转换PDF '{os.path.basename(pdf_path)}' 时发生错误: {e}"})
        raise e

def embed_blind_watermark(image_path, watermark_text, output_path, q_log, password_img=1, password_wm=1):
    if WaterMark is None:
        q_log.put({'type': 'log', 'message': "错误: blind-watermark库未安装，无法嵌入盲水印。"})
        return False, 0
    
    watermark_char_length = len(watermark_text)
    if not (100 <= watermark_char_length <= 200):
        q_log.put({'type': 'log', 'message': f"警告: 水印文字长度为 {watermark_char_length}，不在建议的100-200字符范围内。这可能会影响水印嵌入效果或导致解密失败。"})

    try:
        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        bwm.read_img(image_path)
        bwm.read_wm(watermark_text, mode='str')
        bwm.embed(output_path)
        return True, len(bwm.wm_bit)
    except Exception as e:
        q_log.put({'type': 'log', 'message': f"嵌入盲水印时发生错误: {e}"})
        return False, 0

def extract_blind_watermark_core(image_path, wm_shape, password_img=1, password_wm=1):
    if WaterMark is None:
        return None
    
    temp_img_path = None
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        original_ext = os.path.splitext(image_path)[1]
        if not original_ext:
            original_ext = '.png'

        with tempfile.NamedTemporaryFile(suffix=original_ext, delete=False) as temp_img_file:
            temp_img_path = temp_img_file.name
            temp_img_file.write(image_bytes)

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        wm_extract = bwm.extract(filename=temp_img_path, wm_shape=wm_shape, mode='str')

        return wm_extract
    except Exception as e:
        return None
    finally:
        if temp_img_path and os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except OSError as e:
                print(f"警告: 无法删除临时文件 {temp_img_path}: {e}")

def is_likely_readable_text(text):
    if not text:
        return False
    
    printable_and_chinese_chars = 0
    total_chars = len(text)
    
    for char in text:
        if 32 <= ord(char) <= 126:
            printable_and_chinese_chars += 1
        elif '\u4e00' <= char <= '\u9fff':
            printable_and_chinese_chars += 1
        elif '\u3000' <= char <= '\u303F':
            printable_and_chinese_chars += 1
        elif '\uFF00' <= char <= '\uFFEF':
            printable_and_chinese_chars += 1

    if total_chars == 0:
        return False
    
    valid_percentage = (printable_and_chinese_chars / total_chars) * 100
    
    if valid_percentage >= 80 and 1 <= total_chars <= 200:
        return True
    
    return False

class RSAImageEncryptorApp:
    def __init__(self, master):
        self.master = master
        master.title("公务文档图像加密工具 v1.0")
        master.geometry("700x750")
        master.resizable(False, False)
        master.configure(bg="#F5F5F5")

        self.private_key = None
        self.public_key = None

        self.selected_encrypt_file_paths = []
        self.selected_decrypt_file_path = tk.StringVar()
        self.selected_extract_watermark_file_path = tk.StringVar()
        self.signer_name_var = tk.StringVar()
        self.add_watermark_var = tk.BooleanVar(value=False)
        self.wm_shape_var = tk.IntVar(value=0)
        self.brute_force_wm_var = tk.BooleanVar(value=False)

        self.operation_queue = queue.Queue()
        self.is_operation_running = False

        self.menubar = tk.Menu(master, bg="#FFFFFF", fg="#333333", activebackground="#E3F2FD", 
                              activeforeground="#1976D2", font=(CUSTOM_FONT_FAMILY, 9))
        master.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0, bg="#FFFFFF", fg="#333333", 
                           activebackground="#E3F2FD", activeforeground="#1976D2", font=(CUSTOM_FONT_FAMILY, 9))
        self.menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="生成新的RSA密钥对", command=self.generate_keys)
        file_menu.add_command(label="载入公钥", command=self.load_public_key)
        file_menu.add_command(label="载入私钥", command=self.load_private_key)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=master.quit)

        self.guidance_label = tk.Label(master, text="欢迎使用！请先通过 '文件' 菜单生成或载入密钥。",
                                       font=(CUSTOM_FONT_FAMILY, 11), bg="#F5F5F5", fg="#1976D2", 
                                       wraplength=650, justify="center")
        self.guidance_label.pack(pady=(20, 20), padx=20)

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(pady=10, padx=20, fill="x", expand=True)

        self.encrypt_frame = tk.LabelFrame(self.notebook, text="图像加密", padx=20, pady=20, 
                                          bg="#FFFFFF", font=(CUSTOM_FONT_FAMILY, 12, "bold"), 
                                          fg="#333333", relief=tk.RAISED, bd=2)
        self.decrypt_frame = tk.LabelFrame(self.notebook, text="图像解密", padx=20, pady=20, 
                                          bg="#FFFFFF", font=(CUSTOM_FONT_FAMILY, 12, "bold"), 
                                          fg="#333333", relief=tk.RAISED, bd=2)
        
        self.notebook.add(self.encrypt_frame, text="图像加密")
        self.notebook.add(self.decrypt_frame, text="图像解密")

        self._setup_encrypt_ui()
        self._setup_decrypt_ui()

        progress_frame = tk.Frame(master, bg="#F5F5F5")
        progress_frame.pack(pady=15, padx=20, fill="x")

        self.progress_label = tk.Label(progress_frame, text="进度:", font=(CUSTOM_FONT_FAMILY, 10, "bold"), 
                                      bg="#F5F5F5", fg="#333333")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 10))

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                           length=400, mode="determinate",
                                           style="Custom.Horizontal.TProgressbar")
        self.progress_bar.pack(side=tk.LEFT, fill="x", expand=True)

        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", 
                       background="#4CAF50", troughcolor="#E0E0E0")
        style.configure("TNotebook", background="#F5F5F5")
        style.configure("TNotebook.Tab", background="#E0E0E0", foreground="#333333", font=(CUSTOM_FONT_FAMILY, 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#1976D2")])


        self.log_label = tk.Label(master, text="操作日志:", font=(CUSTOM_FONT_FAMILY, 11, "bold"), 
                                 bg="#F5F5F5", fg="#333333")
        self.log_label.pack(pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, height=12, bd=1, 
                                                 relief=tk.SUNKEN, font=(CUSTOM_FONT_FAMILY, 9), 
                                                 bg="#FAFAFA", fg="#333333",
                                                 selectbackground="#E3F2FD")
        self.log_text.pack(pady=(0, 15), padx=20, fill="both", expand=True)
        
        self.log_message("欢迎使用公务文档图像加密工具！")

        self.signer_name_var.trace_add("write", self._limit_signer_name_length)
        self.signer_name_var.trace_add("write", self._update_encrypt_button_state)
        self.selected_decrypt_file_path.trace_add("write", self._update_decrypt_button_state)
        self.selected_extract_watermark_file_path.trace_add("write", self._update_extract_watermark_button_state)
        self.wm_shape_var.trace_add("write", self._update_extract_watermark_button_state)
        self.brute_force_wm_var.trace_add("write", self._on_brute_force_checkbox_toggle)
        self._update_ui_state()
        self.master.after(100, self.process_queue)

    def _setup_encrypt_ui(self):
        tk.Label(self.encrypt_frame, text="已选择文件 (图像/PDF，可多选):", 
                bg="#FFFFFF", font=(CUSTOM_FONT_FAMILY, 10)).pack(anchor="w", pady=(0, 8))
        
        self.encrypt_file_listbox = tk.Listbox(self.encrypt_frame, height=3, width=70, 
                                              state="disabled", bg="#F8F8F8", fg="#333333", 
                                              selectbackground="#1976D2", selectforeground="white",
                                              font=(CUSTOM_FONT_FAMILY, 9), relief=tk.SUNKEN, bd=1)
        self.encrypt_file_listbox.pack(pady=(0, 15), fill="x")

        button_frame1 = tk.Frame(self.encrypt_frame, bg="#FFFFFF")
        button_frame1.pack(fill="x", pady=(0, 10))

        common_button_args = {
            "font": (CUSTOM_FONT_FAMILY, 10, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "activebackground": "#45a049",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 8
        }

        self.select_files_button = tk.Button(button_frame1, text="选择文件", 
                                            command=self.select_files_for_encryption, 
                                            state="disabled", **common_button_args)
        self.select_files_button.pack(side=tk.LEFT)

        input_frame = tk.Frame(self.encrypt_frame, bg="#FFFFFF")
        input_frame.pack(fill="x", pady=(0, 10))

        tk.Label(input_frame, text="签名人名称:", bg="#FFFFFF", 
                font=(CUSTOM_FONT_FAMILY, 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.signer_name_entry = tk.Entry(input_frame, textvariable=self.signer_name_var, 
                                         width=25, state="disabled", font=(CUSTOM_FONT_FAMILY, 10),
                                         relief=tk.SUNKEN, bd=1)
        self.signer_name_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 15))

        self.watermark_checkbox = tk.Checkbutton(input_frame, text="添加数字盲水印", 
                                                variable=self.add_watermark_var, 
                                                bg="#FFFFFF", state="disabled",
                                                font=(CUSTOM_FONT_FAMILY, 10))
        self.watermark_checkbox.pack(side=tk.LEFT)

        self.encrypt_button = tk.Button(self.encrypt_frame, text="加密并保存", 
                                       command=self.encrypt_files, state="disabled", 
                                       **common_button_args)
        self.encrypt_button.pack(pady=(10, 0))

    def _setup_decrypt_ui(self):
        tk.Label(self.decrypt_frame, text="已选择加密文件 (.osep):", 
                bg="#FFFFFF", font=(CUSTOM_FONT_FAMILY, 10)).pack(anchor="w", pady=(0, 8))
        
        self.decrypt_path_entry = tk.Entry(self.decrypt_frame, textvariable=self.selected_decrypt_file_path, 
                                          width=70, state="disabled", bg="#F8F8F8", fg="#333333",
                                          font=(CUSTOM_FONT_FAMILY, 9), relief=tk.SUNKEN, bd=1)
        self.decrypt_path_entry.pack(pady=(0, 15), fill="x")

        button_frame2 = tk.Frame(self.decrypt_frame, bg="#FFFFFF")
        button_frame2.pack(fill="x")

        common_button_args = {
            "font": (CUSTOM_FONT_FAMILY, 10, "bold"),
            "bg": "#2196F3",
            "fg": "white",
            "activebackground": "#1976D2",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 8
        }

        self.select_encrypted_file_button = tk.Button(button_frame2, text="选择加密文件", 
                                                     command=self.select_encrypted_file_for_decryption, 
                                                     state="disabled", **common_button_args)
        self.select_encrypted_file_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.decrypt_button = tk.Button(button_frame2, text="解密并查看", 
                                       command=self.decrypt_files, state="disabled", 
                                       **common_button_args)
        self.decrypt_button.pack(side=tk.LEFT)

        tk.Label(self.decrypt_frame, text="-----------------------------------------------------------------------------------------------------------------------", bg="#FFFFFF", fg="#CCCCCC").pack(pady=(20,10))
        tk.Label(self.decrypt_frame, text="从普通图像文件中提取数字盲水印:", 
                bg="#FFFFFF", font=(CUSTOM_FONT_FAMILY, 10, "bold")).pack(anchor="w", pady=(0, 8))

        extract_wm_frame = tk.Frame(self.decrypt_frame, bg="#FFFFFF")
        extract_wm_frame.pack(fill="x", pady=(0, 10))

        tk.Label(extract_wm_frame, text="选择图像文件:", bg="#FFFFFF", 
                font=(CUSTOM_FONT_FAMILY, 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.extract_wm_path_entry = tk.Entry(extract_wm_frame, textvariable=self.selected_extract_watermark_file_path, 
                                             width=40, state="disabled", bg="#F8F8F8", fg="#333333",
                                             font=(CUSTOM_FONT_FAMILY, 9), relief=tk.SUNKEN, bd=1)
        self.extract_wm_path_entry.pack(side=tk.LEFT, expand=True, fill="x", padx=(0, 10))

        self.select_extract_wm_file_button = tk.Button(extract_wm_frame, text="选择图像", 
                                                      command=self.select_file_for_watermark_extraction, 
                                                      state="disabled", **common_button_args)
        self.select_extract_wm_file_button.pack(side=tk.LEFT)

        wm_options_frame = tk.Frame(self.decrypt_frame, bg="#FFFFFF")
        wm_options_frame.pack(fill="x", pady=(0, 10))

        self.brute_force_checkbox = tk.Checkbutton(wm_options_frame, text="暴力破解水印长度",
                                                   variable=self.brute_force_wm_var,
                                                   bg="#FFFFFF", state="disabled",
                                                   font=(CUSTOM_FONT_FAMILY, 10))
        self.brute_force_checkbox.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(wm_options_frame, text="水印长度 (wm_shape):", bg="#FFFFFF", 
                font=(CUSTOM_FONT_FAMILY, 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.wm_shape_entry = tk.Entry(wm_options_frame, textvariable=self.wm_shape_var, 
                                      width=10, font=(CUSTOM_FONT_FAMILY, 10), relief=tk.SUNKEN, bd=1)
        self.wm_shape_entry.pack(side=tk.LEFT)

        self.extract_watermark_button = tk.Button(self.decrypt_frame, text="提取水印", 
                                                  command=self.extract_watermark_from_image, 
                                                  state="disabled", **common_button_args)
        self.extract_watermark_button.pack(pady=(10, 0))

    def _on_brute_force_checkbox_toggle(self, *args):
        if self.brute_force_wm_var.get():
            self.wm_shape_entry.config(state="disabled")
            self.wm_shape_var.set(0)
        else:
            self.wm_shape_entry.config(state="normal")
        self._update_extract_watermark_button_state()

    def _update_ui_state(self):
        encrypt_enabled = self.public_key is not None
        decrypt_enabled = self.private_key is not None

        self.select_files_button.config(state="disabled")
        self.signer_name_entry.config(state="disabled")
        self.watermark_checkbox.config(state="disabled")
        self.encrypt_button.config(state="disabled")
        self.encrypt_file_listbox.config(state="disabled")
        self.select_encrypted_file_button.config(state="disabled")
        self.decrypt_path_entry.config(state="disabled")
        self.decrypt_button.config(state="disabled")
        
        self.select_extract_wm_file_button.config(state="disabled")
        self.extract_wm_path_entry.config(state="disabled")
        self.wm_shape_entry.config(state="disabled")
        self.brute_force_checkbox.config(state="disabled")
        self.extract_watermark_button.config(state="disabled")


        if self.is_operation_running:
            self.guidance_label.config(text="操作进行中，请稍候...", fg="#FF5722")
        else:
            if encrypt_enabled:
                self.guidance_label.config(text="公钥已载入。您可以加密图像。", fg="#1976D2")
                self.select_files_button.config(state="normal")
                self.signer_name_entry.config(state="normal")
                self.watermark_checkbox.config(state="normal")
                self._update_encrypt_button_state()
                self.encrypt_file_listbox.config(state="normal")
            else:
                self.select_files_button.config(state="disabled")
                self.signer_name_entry.config(state="disabled")
                self.watermark_checkbox.config(state="disabled")
                self.encrypt_button.config(state="disabled")
                self.encrypt_file_listbox.config(state="disabled")

            if decrypt_enabled:
                if encrypt_enabled:
                    self.guidance_label.config(text="公钥和私钥都已载入。现在可以进行图像加密和解密操作。", fg="#4CAF50")
                else:
                    self.guidance_label.config(text="私钥已载入。您可以解密图像。", fg="#1976D2")

                self.select_encrypted_file_button.config(state="normal")
                self.decrypt_path_entry.config(state="normal")
                self._update_decrypt_button_state()
                
                self.select_extract_wm_file_button.config(state="normal")
                self.extract_wm_path_entry.config(state="normal")
                self.brute_force_checkbox.config(state="normal")
                self._on_brute_force_checkbox_toggle()
                self._update_extract_watermark_button_state()
            else:
                self.select_encrypted_file_button.config(state="disabled")
                self.decrypt_path_entry.config(state="disabled")
                self.decrypt_button.config(state="disabled")
                
                self.select_extract_wm_file_button.config(state="disabled")
                self.extract_wm_path_entry.config(state="disabled")
                self.wm_shape_entry.config(state="disabled")
                self.brute_force_checkbox.config(state="disabled")
                self.extract_watermark_button.config(state="disabled")


            if not encrypt_enabled and not decrypt_enabled:
                self.guidance_label.config(text="欢迎使用！请先通过 '文件' 菜单生成或载入密钥。", fg="#1976D2")

    def _update_encrypt_button_state(self, *args):
        if self.public_key is not None and self.selected_encrypt_file_paths and self.signer_name_var.get().strip():
            self.encrypt_button.config(state="normal")
        else:
            self.encrypt_button.config(state="disabled")

    def _update_decrypt_button_state(self, *args):
        if self.private_key is not None and self.selected_decrypt_file_path.get():
            self.decrypt_button.config(state="normal")
        else:
            self.decrypt_button.config(state="disabled")

    def _update_extract_watermark_button_state(self, *args):
        is_ready_for_extraction = False
        if self.private_key is not None and self.selected_extract_watermark_file_path.get():
            if self.brute_force_wm_var.get():
                is_ready_for_extraction = True
            else:
                try:
                    wm_shape_val = self.wm_shape_var.get()
                    if 100 <= wm_shape_val <= 300:
                        is_ready_for_extraction = True
                    elif wm_shape_val == 0:
                        is_ready_for_extraction = True
                except tk.TclError:
                    is_ready_for_extraction = False

        if is_ready_for_extraction:
            self.extract_watermark_button.config(state="normal")
        else:
            self.extract_watermark_button.config(state="disabled")

    def log_message(self, message):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        self.log_text.insert(tk.END, f"{timestamp} {message}\n")
        self.log_text.see(tk.END)

    def generate_keys(self):
        self.log_message("开始生成RSA密钥对...")
        try:
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            self.public_key = self.private_key.public_key()

            private_key_path = filedialog.asksaveasfilename(
                defaultextension=".pem", filetypes=[("PEM文件", "*.pem")], title="保存私钥文件"
            )
            if not private_key_path:
                self.log_message("私钥保存取消。")
                self.private_key = None
                self.public_key = None
                self._update_ui_state()
                return

            password = simpledialog.askstring("私钥密码", "请输入私钥密码 (用于加密私钥文件):", show='*')
            if not password:
                self.log_message("未输入私钥密码，私钥未保存。")
                self.private_key = None
                self.public_key = None
                self._update_ui_state()
                return

            with open(private_key_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
                ))
            self.log_message(f"私钥已保存到: {private_key_path}")

            public_key_path = filedialog.asksaveasfilename(
                defaultextension=".pub", filetypes=[("公钥文件", "*.pub")], title="保存公钥文件"
            )
            if not public_key_path:
                self.log_message("公钥保存取消。")
                self.public_key = None
                self._update_ui_state()
                return

            with open(public_key_path, "wb") as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))
            self.log_message(f"公钥已保存到: {public_key_path}")
            self.log_message("RSA密钥对生成并保存成功！")
            self._update_ui_state()

        except Exception as e:
            self.log_message(f"生成密钥对时发生错误: {e}")
            messagebox.showerror("错误", f"生成密钥对时发生错误: {e}")
            self.private_key = None
            self.public_key = None
            self._update_ui_state()

    def load_public_key(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("公钥文件", "*.pub"), ("PEM文件", "*.pem")], title="选择公钥文件"
        )
        if not file_path:
            self.log_message("载入公钥取消。")
            return
        try:
            with open(file_path, "rb") as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(), backend=default_backend()
                )
            self.log_message(f"公钥已成功载入: {file_path}")
            self._update_ui_state()
        except Exception as e:
            self.log_message(f"载入公钥时发生错误: {e}")
            messagebox.showerror("错误", f"载入公钥时发生错误: {e}")
            self.public_key = None
            self._update_ui_state()

    def load_private_key(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PEM文件", "*.pem")], title="选择私钥文件"
        )
        if not file_path:
            self.log_message("载入私钥取消。")
            return
        try:
            password = simpledialog.askstring("私钥密码", "请输入私钥密码:", show='*')
            if not password:
                self.log_message("未输入私钥密码，私钥未载入。")
                return
            with open(file_path, "rb") as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(), password=password.encode(), backend=default_backend()
                )
            self.log_message(f"私钥已成功载入: {file_path}")
            self._update_ui_state()
        except Exception as e:
            self.log_message(f"载入私钥时发生错误: {e}")
            messagebox.showerror("错误", f"载入私钥时发生错误: {e}")
            self.private_key = None
            self._update_ui_state()

    def select_files_for_encryption(self):
        file_types = [
            ("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("PDF文件", "*.pdf"),
            ("所有文件", "*.*")
        ]
        file_paths = filedialog.askopenfilenames(
            filetypes=file_types,
            title="选择要加密的图像或PDF文件 (可多选)"
        )
        if file_paths:
            self.selected_encrypt_file_paths = list(file_paths)
            self.encrypt_file_listbox.delete(0, tk.END)
            for path in self.selected_encrypt_file_paths:
                self.encrypt_file_listbox.insert(tk.END, os.path.basename(path))
            self.log_message(f"已选择 {len(self.selected_encrypt_file_paths)} 个文件。")
            self._update_encrypt_button_state()
        else:
            self.log_message("文件选择取消。")
            self.selected_encrypt_file_paths = []
            self.encrypt_file_listbox.delete(0, tk.END)
            self._update_encrypt_button_state()

    def encrypt_files(self):
        if self.public_key is None:
            messagebox.showwarning("警告", "公钥未载入，无法执行加密操作。")
            return
        if not self.selected_encrypt_file_paths:
            messagebox.showwarning("警告", "请先选择至少一个图像或PDF文件进行加密。")
            return

        signer_name = self.signer_name_var.get().strip()
        if not signer_name:
            messagebox.showwarning("警告", "请输入签名人名称。")
            return

        if self.add_watermark_var.get():
            if WaterMark is None:
                messagebox.showwarning("警告", "blind-watermark库未安装，无法验证水印长度。请安装后重试。")
                return
            try:
                temp_bwm = WaterMark(password_img=1, password_wm=1)
                temp_bwm.read_wm(signer_name, mode='str')
                calculated_wm_bit_length = len(temp_bwm.wm_bit) 

                if not (100 <= calculated_wm_bit_length <= 300):
                    messagebox.showwarning("警告", f"水印比特长度为 {calculated_wm_bit_length}，不在建议的100-300比特范围内。这可能会影响水印嵌入效果或导致解密失败。请调整签名人名称长度以使水印比特长度在100-300比特之间。")
                    return
            except Exception as e:
                messagebox.showerror("错误", f"计算水印比特长度时发生错误: {e}")
                return


        if self.is_operation_running:
            messagebox.showwarning("警告", "已有操作正在进行中，请等待其完成。")
            return

        total_images_to_encrypt = 0
        for path in self.selected_encrypt_file_paths:
            if path.lower().endswith('.pdf'):
                if fitz is None:
                    messagebox.showerror("错误", "PyMuPDF库未安装，无法处理PDF文件。请先安装。")
                    return
                try:
                    doc = fitz.open(path)
                    total_images_to_encrypt += doc.page_count
                    doc.close()
                except Exception as e:
                    messagebox.showerror("错误", f"无法打开或读取PDF文件 '{os.path.basename(path)}': {e}")
                    self.log_message(f"错误: 无法预处理PDF文件 '{os.path.basename(path)}': {e}")
                    return
            else:
                total_images_to_encrypt += 1

        if total_images_to_encrypt == 0:
            messagebox.showwarning("警告", "没有有效的图像或PDF页面可供加密。")
            return

        self.is_operation_running = True
        self._update_ui_state()
        self.progress_bar["value"] = 0
        self.progress_label.config(text="进度: 0%")
        self.log_message("开始多线程加密...")

        add_watermark = self.add_watermark_var.get()

        threading.Thread(target=self._encrypt_files_threaded, args=(
            self.selected_encrypt_file_paths,
            signer_name,
            self.public_key,
            self.operation_queue,
            total_images_to_encrypt,
            add_watermark
        )).start()

    def _encrypt_files_threaded(self, file_paths, signer_name, public_key, q, total_images_to_encrypt, add_watermark):
        try:
            machine_id = hashlib.sha256(str(uuid.getnode()).encode('utf-8')).hexdigest().encode('utf-8')
            creation_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            osep_content_parts = []
            osep_content_parts.append("OSEP_FORMAT_VERSION=1.0")
            osep_content_parts.append("SOURCE_APP=RSA_Multi_Image_Encryptor_Tool_v1.0")
            osep_content_parts.append(f"SIGNER_NAME={signer_name}")
            osep_content_parts.append(f"MACHINE_ID={machine_id.decode('utf-8')}")
            osep_content_parts.append(f"CREATION_TIME={creation_time}")
            osep_content_parts.append(f"IMAGE_COUNT={total_images_to_encrypt}")
            osep_content_parts.append(f"WATERMARK_ADDED={'True' if add_watermark else 'False'}")
            
            wm_bit_length_for_header = 0

            chunk_size = 190
            current_processed_images_count = 0

            for file_path in file_paths:
                if file_path.lower().endswith('.pdf'):
                    q.put({'type': 'log', 'message': f"转换PDF '{os.path.basename(file_path)}' 为图像..."})
                    images_to_process = convert_pdf_to_images(file_path, q)
                else:
                    try:
                        images_to_process = [Image.open(file_path).convert("RGB")]
                    except Exception as e:
                        q.put({'type': 'log', 'message': f"错误: 无法打开图像文件 '{os.path.basename(file_path)}': {e}，跳过。"})
                        continue

                for img_idx_in_file, img_pil in enumerate(images_to_process):
                    q.put({'type': 'log', 'message': f"处理图像 ({os.path.basename(file_path)} - 页/图 {img_idx_in_file + 1}): 开始加密。"})

                    temp_image_path = None
                    try:
                        temp_image_path = f"temp_image_{uuid.uuid4().hex}.png"
                        img_pil.save(temp_image_path)

                        if add_watermark:
                            q.put({'type': 'log', 'message': f"正在为图像 ({os.path.basename(file_path)} - 页/图 {img_idx_in_file + 1}) 添加数字盲水印..."})
                            watermark_to_embed = signer_name
                            success, wm_bit_length = embed_blind_watermark(temp_image_path, watermark_to_embed, temp_image_path, q)
                            if not success:
                                q.put({'type': 'log', 'message': f"警告: 图像 ({os.path.basename(file_path)} - 页/图 {img_idx_in_file + 1}) 嵌入盲水印失败，将不含水印进行加密。"})
                            else:
                                q.put({'type': 'log', 'message': f"成功嵌入水印。水印比特长度为: {wm_bit_length} (请在解密时使用此长度提取水印)"})
                                if wm_bit_length_for_header == 0:
                                    wm_bit_length_for_header = wm_bit_length
                        
                        img_pil_with_watermark = Image.open(temp_image_path).convert("RGB")

                        width, height = img_pil_with_watermark.size
                        pixel_data = list(img_pil_with_watermark.getdata())
                        flat_pixel_bytes = bytes([val for rgb_tuple in pixel_data for val in rgb_tuple])

                        encrypted_chunks = []
                        total_chunks_for_image = (len(flat_pixel_bytes) + chunk_size - 1) // chunk_size

                        for i in range(0, len(flat_pixel_bytes), chunk_size):
                            chunk = flat_pixel_bytes[i:i + chunk_size]
                            encrypted_chunk = public_key.encrypt(
                                chunk,
                                padding.OAEP(
                                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                    algorithm=hashes.SHA256(),
                                    label=None
                                )
                            )
                            encrypted_chunks.append(base64.b64encode(encrypted_chunk).decode('utf-8'))

                            chunk_progress_in_current_image = (i / total_chunks_for_image) if total_chunks_for_image > 0 else 0
                            overall_progress = ((current_processed_images_count + chunk_progress_in_current_image) / total_images_to_encrypt) * 100
                            q.put({'type': 'progress', 'value': overall_progress})

                        osep_content_parts.append("---IMAGE_START---")
                        osep_content_parts.append(f"IMAGE_INDEX={current_processed_images_count}")
                        osep_content_parts.append(f"IMAGE_WIDTH={width}")
                        osep_content_parts.append(f"IMAGE_HEIGHT={height}")
                        osep_content_parts.append("ENCRYPTED_DATA=" + ",".join(encrypted_chunks))
                        osep_content_parts.append("---IMAGE_END---")
                        osep_content_parts.append("\n")

                        current_processed_images_count += 1
                    finally:
                        if temp_image_path and os.path.exists(temp_image_path):
                            try:
                                os.remove(temp_image_path)
                            except OSError:
                                pass
            
            if add_watermark and wm_bit_length_for_header > 0:
                try:
                    image_count_index = osep_content_parts.index(f"IMAGE_COUNT={total_images_to_encrypt}")
                    osep_content_parts.insert(image_count_index + 1, f"WATERMARK_BIT_LENGTH={wm_bit_length_for_header}")
                except ValueError:
                    osep_content_parts.append(f"WATERMARK_BIT_LENGTH={wm_bit_length_for_header}")


            q.put({'type': 'progress', 'value': 100})
            q.put({'type': 'done', 'success': True, 'content_parts': osep_content_parts, 'message': "加密完成，请选择保存路径。"})

        except Exception as e:
            q.put({'type': 'done', 'success': False, 'message': f"加密过程中发生错误: {e}"})
        finally:
            for f in os.listdir('.'):
                if f.startswith('temp_image_') and f.endswith('.png'):
                    try:
                        os.remove(f)
                    except OSError:
                        pass

    def select_encrypted_file_for_decryption(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("OSEP加密图像文件", "*.osep")],
            title="选择要解密的OSEP加密文件"
        )
        if not file_path:
            self.log_message("加密文件选择取消。")
            return
        self.selected_decrypt_file_path.set(file_path)
        self.log_message(f"已选择加密文件: {file_path}")
        self._update_ui_state()

    def decrypt_files(self):
        if self.private_key is None:
            messagebox.showwarning("警告", "私钥未载入，无法执行解密操作。")
            return
        if not self.selected_decrypt_file_path.get():
            messagebox.showwarning("警告", "请先选择一个加密文件进行解密。")
            return

        if self.is_operation_running:
            messagebox.showwarning("警告", "已有操作正在进行中，请等待其完成。")
            return

        self.is_operation_running = True
        self._update_ui_state()
        self.progress_bar["value"] = 0
        self.progress_label.config(text="进度: 0%")
        self.log_message("开始多线程解密...")

        threading.Thread(target=self._decrypt_files_threaded, args=(
            self.selected_decrypt_file_path.get(),
            self.private_key,
            self.operation_queue
        )).start()

    def _decrypt_files_threaded(self, encrypted_file_path, private_key, q):
        try:
            with open(encrypted_file_path, "r") as f:
                lines = f.readlines()

            header_data = {}
            image_blocks_raw = []
            current_image_block = []
            in_image_block = False

            for line in lines:
                line = line.strip()
                if line.startswith("---IMAGE_START---"):
                    in_image_block = True
                    current_image_block = []
                    continue
                elif line.startswith("---IMAGE_END---"):
                    in_image_block = False
                    image_blocks_raw.append(current_image_block)
                    continue

                if in_image_block:
                    current_image_block.append(line)
                elif "=" in line:
                    key, value = line.split("=", 1)
                    header_data[key.strip()] = value.strip()

            q.put({'type': 'log', 'message': "--- 文件头信息 ---"})
            for key, value in header_data.items():
                q.put({'type': 'log', 'message': f"{key}: {value}"})
            q.put({'type': 'log', 'message': "------------------"})

            if "IMAGE_COUNT" not in header_data:
                raise ValueError("OSEP文件头缺少IMAGE_COUNT信息。")
            expected_image_count = int(header_data["IMAGE_COUNT"])
            if expected_image_count != len(image_blocks_raw):
                q.put({'type': 'log', 'message': f"警告: 文件头声明有 {expected_image_count} 张图像，但实际解析到 {len(image_blocks_raw)} 张。"})

            reconstructed_images = []
            chunk_size = 190

            for idx, block_lines in enumerate(image_blocks_raw):
                q.put({'type': 'log', 'message': f"解密图像块 {idx + 1}/{len(image_blocks_raw)}..."})
                img_meta = {}
                encrypted_data_str = ""
                for line in block_lines:
                    if "=" in line:
                        key, value = line.split("=", 1)
                        if key == "ENCRYPTED_DATA":
                            encrypted_data_str = value
                        else:
                            img_meta[key.strip()] = value.strip()

                width = int(img_meta.get("IMAGE_WIDTH", 0))
                height = int(img_meta.get("IMAGE_HEIGHT", 0))

                if not (width > 0 and height > 0 and encrypted_data_str):
                    q.put({'type': 'log', 'message': f"图像块 {idx} 数据不完整，跳过。"})
                    continue

                encrypted_chunks_b64 = encrypted_data_str.split(',')
                decrypted_flat_pixel_bytes = bytearray()

                total_chunks_for_image = len(encrypted_chunks_b64)
                for i, b64_chunk in enumerate(encrypted_chunks_b64):
                    encrypted_chunk = base64.b64decode(b64_chunk)
                    decrypted_chunk = private_key.decrypt(
                        encrypted_chunk,
                        padding.OAEP(
                            mgf=padding.MGF1(algorithm=hashes.SHA256()),
                            algorithm=hashes.SHA256(),
                            label=None
                        )
                    )
                    decrypted_flat_pixel_bytes.extend(decrypted_chunk)

                    current_image_progress = (i / total_chunks_for_image) * (100 / len(image_blocks_raw))
                    total_progress = (idx * (100 / len(image_blocks_raw))) + current_image_progress
                    q.put({'type': 'progress', 'value': total_progress})

                if len(decrypted_flat_pixel_bytes) != width * height * 3:
                    q.put({'type': 'log', 'message': f"警告: 图像 {idx} 解密后的像素数据字节数不匹配图像尺寸。预期: {width * height * 3}, 实际: {len(decrypted_flat_pixel_bytes)}"})
                    decrypted_flat_pixel_bytes = decrypted_flat_pixel_bytes[:width * height * 3]
                    if len(decrypted_flat_pixel_bytes) < width * height * 3:
                         decrypted_flat_pixel_bytes.extend(bytearray([0] * (width * height * 3 - len(decrypted_flat_pixel_bytes))))

                reconstructed_pixel_data = []
                for i in range(0, len(decrypted_flat_pixel_bytes), 3):
                    r = decrypted_flat_pixel_bytes[i]
                    g = decrypted_flat_pixel_bytes[i+1]
                    b = decrypted_flat_pixel_bytes[i+2]
                    reconstructed_pixel_data.append((r, g, b))

                reconstructed_img = Image.new("RGB", (width, height))
                reconstructed_img.putdata(reconstructed_pixel_data)
                reconstructed_images.append(reconstructed_img)

            q.put({'type': 'progress', 'value': 100})
            q.put({'type': 'done', 'success': True, 'images': reconstructed_images, 'message': f"解密完成，共解密 {len(reconstructed_images)} 张图像。"})

        except Exception as e:
            q.put({'type': 'done', 'success': False, 'message': f"解密过程中发生错误: {e}"})

    def select_file_for_watermark_extraction(self):
        file_types = [
            ("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
            ("所有文件", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            filetypes=file_types,
            title="选择要提取水印的图像文件"
        )
        if not file_path:
            self.log_message("提取水印文件选择取消。")
            return
        self.selected_extract_watermark_file_path.set(file_path)
        self.log_message(f"已选择用于提取水印的图像: {file_path}")
        self._update_extract_watermark_button_state()

    def extract_watermark_from_image(self):
        if WaterMark is None:
            messagebox.showerror("错误", "blind-watermark库未安装，无法提取盲水印。")
            return
        if self.private_key is None:
            messagebox.showwarning("警告", "私钥未载入，无法执行提取水印操作。")
            return
        file_path = self.selected_extract_watermark_file_path.get()
        if not file_path:
            messagebox.showwarning("警告", "请选择一个图像文件来提取水印。")
            return

        password_img = 1
        password_wm = 1

        if not self.brute_force_wm_var.get():
            wm_shape_to_use = 0
            if file_path.lower().endswith('.osep'):
                try:
                    with open(file_path, "r") as f:
                        lines = f.readlines()
                    header_data = {}
                    for line in lines:
                        line = line.strip()
                        if "=" in line and not line.startswith("---IMAGE"):
                            key, value = line.split("=", 1)
                            header_data[key.strip()] = value.strip()
                    if "WATERMARK_BIT_LENGTH" in header_data:
                        wm_shape_to_use = int(header_data["WATERMARK_BIT_LENGTH"])
                        self.log_message(f"从OSEP文件头读取到水印比特长度: {wm_shape_to_use}")
                except Exception as e:
                    self.log_message(f"读取OSEP文件头水印比特长度时发生错误: {e}")
            
            if wm_shape_to_use <= 0:
                try:
                    wm_shape_to_use = self.wm_shape_var.get()
                except tk.TclError:
                    messagebox.showwarning("警告", "水印长度 (wm_shape) 必须是有效的整数。")
                    return
            
            if wm_shape_to_use <= 0:
                messagebox.showwarning("警告", "请输入有效的水印长度 (wm_shape)，必须大于0。")
                return

            self.log_message(f"开始从 '{os.path.basename(file_path)}' 提取数字盲水印 (指定长度: {wm_shape_to_use})...")
            extracted_wm = extract_blind_watermark_core(file_path, wm_shape_to_use, password_img, password_wm)
            if extracted_wm is not None:
                messagebox.showinfo("水印提取结果", f"提取到的水印是: {extracted_wm}")
                self.log_message(f"成功提取水印: {extracted_wm}")
            else:
                messagebox.showerror("水印提取失败", "未能从图像中提取水印。\n请确保文件路径有效、文件未损坏，且水印长度 (wm_shape) 与嵌入时完全一致。")
                self.log_message("提取水印失败。")

        else: 
            self.log_message(f"开始对 '{os.path.basename(file_path)}' 进行暴力破解水印长度 (尝试100到200比特)...")
            all_extracted_wms = []
            
            for guess in range(100, 201, 1):
                self.log_message(f"尝试水印长度 (wm_shape): {guess}...")
                try:
                    wm_extract = extract_blind_watermark_core(file_path, guess, password_img, password_wm)
                    if wm_extract is not None:
                        valid_chars_count = sum(1 for c in wm_extract if 32 <= ord(c) <= 126 or ('\u4e00' <= c <= '\u9fff'))
                        valid_percentage = (valid_chars_count / len(wm_extract)) * 100 if len(wm_extract) > 0 else 0

                        if valid_percentage >= 80:
                            all_extracted_wms.append((guess, wm_extract))
                            self.log_message(f"成功提取内容（wm_shape={guess}）：\n{wm_extract}")
                            break 
                        else:
                            self.log_message(f"wm_shape={guess} → 乱码：{wm_extract}")
                    else:
                        self.log_message(f"wm_shape={guess} → 解码失败：无法提取水印")
                except Exception as e:
                    self.log_message(f"wm_shape={guess} → 解码失败：{e}")

            if all_extracted_wms:
                result_message = "暴力破解结果:\n"
                for length, wm_text in all_extracted_wms:
                    result_message += f"水印长度 (wm_shape) {length}: {wm_text}\n"
                messagebox.showinfo("水印提取结果", result_message)
                self.log_message(f"暴力破解完成。发现 {len(all_extracted_wms)} 个可能的水印。")
            else:
                messagebox.showerror("水印提取失败", "暴力破解未能找到有效水印。\n请尝试其他图像或检查图像是否包含盲水印。")
                self.log_message("暴力破解未能找到有效水印。")

    def _limit_signer_name_length(self, *args):
        current_text = self.signer_name_var.get()
        if len(current_text) > 50: 
            self.signer_name_var.set(current_text[:50])

    def process_queue(self):
        try:
            while True:
                message = self.operation_queue.get_nowait()
                if message['type'] == 'log':
                    self.log_message(message['message'])
                elif message['type'] == 'progress':
                    self.progress_bar["value"] = message['value']
                    self.progress_label.config(text=f"进度: {int(message['value'])}%")
                elif message['type'] == 'done':
                    self.is_operation_running = False
                    self._update_ui_state()
                    self.progress_bar["value"] = 0
                    self.progress_label.config(text="进度:")

                    if message['success']:
                        self.log_message(message['message'])
                        if 'content_parts' in message:
                            output_file_path = filedialog.asksaveasfilename(
                                defaultextension=".osep",
                                filetypes=[("OSEP加密图像文件", "*.osep")],
                                title="保存OSEP加密图像文件"
                            )
                            if not output_file_path:
                                self.log_message("加密文件保存取消。")
                            else:
                                with open(output_file_path, "w") as f:
                                    f.write("\n".join(message['content_parts']))
                                self.log_message(f"加密文件已保存到: {output_file_path}")
                                messagebox.showinfo("成功", "加密操作完成！文件已保存。")
                            self.selected_encrypt_file_paths = []
                            self.encrypt_file_listbox.delete(0, tk.END)
                            self.signer_name_var.set("")
                        elif 'images' in message:
                            viewer_window = tk.Toplevel(self.master)
                            ImageViewer(viewer_window, message['images'])
                            self.selected_decrypt_file_path.set("")
                    else:
                        self.log_message(f"操作失败: {message['message']}")
                        messagebox.showerror("错误", f"操作失败: {message['message']}")

        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.process_queue)

def main():
    root = tk.Tk()
    app = RSAImageEncryptorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
