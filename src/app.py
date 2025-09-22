import os
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import preprocessing as pre
import edge_detection as ed

# ====== Biến toàn cục ======
current_image = None      # Ảnh hiện tại đang xử lý (kiểu numpy array - BGR)
display_image = None      # Ảnh hiển thị trên giao diện (kiểu ImageTk)
image_path = None         # Đường dẫn ảnh gốc
original_image = None     # Bản copy ảnh gốc (dùng để so sánh)

# Lịch sử undo/redo
history = []              # Danh sách lưu các phiên bản ảnh
history_index = -1        # Vị trí hiện tại trong history

# ====== Hàm phụ trợ ======
def cv2_to_tk(img_bgr, max_size=(800, 600)):
    """Chuyển ảnh OpenCV (BGR) sang định dạng ImageTk để hiển thị trên Tkinter"""
    h, w = img_bgr.shape[:2]
    # Tính hệ số scale để ảnh vừa khung
    scale = min(max_size[0]/w, max_size[1]/h, 1.0)
    img_resized = cv2.resize(img_bgr, (int(w*scale), int(h*scale)))
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)   # Chuyển sang RGB
    return ImageTk.PhotoImage(Image.fromarray(img_rgb))

def update_preview(img_bgr, save_history=True):
    """Cập nhật canvas hiển thị ảnh, đồng thời lưu ảnh vào history nếu cần"""
    global current_image, display_image, history, history_index
    if img_bgr is None:
        return
    current_image = img_bgr
    display_image = cv2_to_tk(img_bgr)
    canvas.config(image=display_image)
    canvas.image = display_image

    if save_history:
        # Xóa các bước redo cũ (nếu đã undo trước đó)
        history[:] = history[:history_index+1]
        history.append(img_bgr.copy())
        history_index += 1

# ====== Undo / Redo ======
def undo_action():
    """Quay lại ảnh trước đó"""
    global history_index
    if history_index > 0:
        history_index -= 1
        update_preview(history[history_index], save_history=False)

def redo_action():
    """Làm lại bước vừa undo"""
    global history_index
    if history_index < len(history)-1:
        history_index += 1
        update_preview(history[history_index], save_history=False)

# ====== Chức năng xử lý ảnh ======
def choose_image():
    """Mở hộp thoại chọn ảnh từ máy và hiển thị"""
    global image_path, original_image, history, history_index
    file = filedialog.askopenfilename(
        filetypes=[("Image files","*.jpg;*.png;*.webp;*.jpeg;*.bmp"),("All files","*.*")]
    )
    if not file: return
    # Đọc ảnh (cách này hỗ trợ cả đường dẫn có dấu tiếng Việt)
    img = cv2.imdecode(np.fromfile(file,dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        messagebox.showerror("Lỗi","Không mở được ảnh")
        return
    image_path, original_image = file, img.copy()
    history = [img.copy()]
    history_index = 0
    update_preview(img, save_history=False)

def save_image():
    """Lưu ảnh hiện tại ra file"""
    if current_image is None:
        messagebox.showwarning("Chưa có ảnh","Hãy chọn ảnh trước")
        return
    file = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG","*.png"),("JPEG","*.jpg"), ("WEBP", "*.webp"), ("All files","*.*")]
    )
    if file:
        cv2.imencode(os.path.splitext(file)[1], current_image)[1].tofile(file)
        messagebox.showinfo("Thành công",f"Đã lưu: {file}")

# ====== Popup so sánh ảnh ======
def compare_popup(title, img_top, label_top, img_bottom, label_bottom):
    """Hiển thị cửa sổ so sánh 2 ảnh theo chiều dọc"""
    win = tk.Toplevel(root)
    win.title(title)

    # Căn popup sang bên phải cửa sổ chính
    root.update_idletasks()
    main_x = root.winfo_x()
    main_y = root.winfo_y()
    main_w = root.winfo_width()
    win.geometry(f"+{main_x + main_w + 10}+{main_y}")

    # Ảnh trên
    tk_img1 = cv2_to_tk(img_top, max_size=(360,400))
    lbl1 = tk.Label(win, image=tk_img1, text=label_top, compound=tk.TOP)
    lbl1.image = tk_img1
    lbl1.pack(side=tk.TOP, pady=10)

    # Ảnh dưới
    tk_img2 = cv2_to_tk(img_bottom, max_size=(360,400))
    lbl2 = tk.Label(win, image=tk_img2, text=label_bottom, compound=tk.TOP)
    lbl2.image = tk_img2
    lbl2.pack(side=tk.TOP, pady=10)

# ====== Các popup so sánh cụ thể ======
def sobel_compare_popup():
    """So sánh ảnh gốc và ảnh Sobel"""
    if current_image is None: return
    processed = ed.sobel_detection(current_image)
    if processed is None: return
    compare_popup("So sánh ảnh gốc và Sobel", original_image, "Ảnh gốc", processed, "Ảnh Sobel")

def prewitt_compare_popup():
    """So sánh ảnh gốc và ảnh Prewitt"""
    if current_image is None: return
    processed = ed.prewitt_detection(current_image)
    if processed is None: return
    compare_popup("So sánh ảnh gốc và Prewitt", original_image, "Ảnh gốc", processed, "Ảnh Prewitt")

def sobel_prewitt_compare_popup():
    """So sánh trực tiếp ảnh Sobel và Prewitt"""
    if current_image is None: return
    sobel_img = ed.sobel_detection(current_image)
    prewitt_img = ed.prewitt_detection(current_image)
    if sobel_img is None or prewitt_img is None: return
    compare_popup("So sánh Sobel và Prewitt", sobel_img, "Ảnh Sobel", prewitt_img, "Ảnh Prewitt")

# ====== Xây dựng UI ======
root = tk.Tk()
root.title("Ứng dụng xử lý ảnh")
root.geometry("1020x750")
root.configure(bg="#ecf0f1")  # Màu nền sáng

# Thanh công cụ trên (chọn ảnh, lưu, undo, redo)
top_frame = tk.Frame(root, bg="#2c3e50", pady=10)
top_frame.pack(side=tk.TOP, fill=tk.X)

btn_choose = tk.Button(top_frame, text="📂 Chọn ảnh", command=choose_image, width=12,
                       bg="#27ae60", fg="white", activebackground="#2ecc71")
btn_choose.pack(side=tk.LEFT, padx=5)

btn_save = tk.Button(top_frame, text="💾 Lưu ảnh", command=save_image, width=12,
                     bg="#2980b9", fg="white", activebackground="#3498db")
btn_save.pack(side=tk.LEFT, padx=5)

btn_undo = tk.Button(top_frame, text="⏪", command=undo_action, width=5,
                     bg="#e67e22", fg="white", activebackground="#f39c12")
btn_undo.pack(side=tk.LEFT, padx=5)

btn_redo = tk.Button(top_frame, text="⏩", command=redo_action, width=5,
                     bg="#8e44ad", fg="white", activebackground="#9b59b6")
btn_redo.pack(side=tk.LEFT, padx=5)

# Vùng hiển thị ảnh
canvas = tk.Label(root, bg="lightgray", width=800, height=600, relief=tk.SUNKEN, bd=2)
canvas.pack(pady=10)

# Thanh nút dưới (các chức năng xử lý ảnh)
bottom_frame = tk.Frame(root, bg="#bdc3c7", pady=10)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Nhóm tiền xử lý (nút xanh lá)
tk.Button(bottom_frame, text="⟳ Xoay", command=lambda: update_preview(pre.rotate_image(current_image)),
          width=10, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="⇲ Đổi cỡ", command=lambda: pre.resize_dialog(root, current_image, update_preview),
          width=10, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="✂ Cắt", command=lambda: pre.crop_dialog(root, current_image, update_preview),
          width=10, bg="#2ecc71", fg="white").pack(side=tk.LEFT, padx=5)

# Nhóm phát hiện biên (nút xanh dương)
tk.Button(bottom_frame, text="Đen trắng", command=lambda: update_preview(ed.grayscale_image(current_image)),
          width=12, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="Làm mờ", command=lambda: update_preview(ed.blur_image(current_image)),
          width=12, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="Khử nhiễu TB", command=lambda: update_preview(ed.mean_denoise(current_image)),
          width=12, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="Khử nhiễu Median", command=lambda: update_preview(ed.median_denoise(current_image)),
          width=14, bg="#3498db", fg="white").pack(side=tk.LEFT, padx=5)

# Các thuật toán Sobel/Prewitt
tk.Button(bottom_frame, text="Sobel", command=sobel_compare_popup,
          width=12, bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="Prewitt", command=prewitt_compare_popup,
          width=12, bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)

tk.Button(bottom_frame, text="Sobel vs Prewitt", command=sobel_prewitt_compare_popup,
          width=16, bg="#9b59b6", fg="white").pack(side=tk.LEFT, padx=5)

# Chạy vòng lặp chính Tkinter
root.mainloop()
