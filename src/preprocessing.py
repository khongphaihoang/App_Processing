import cv2, tkinter as tk
from tkinter import messagebox

def undo_image(original_image):
    return None if original_image is None else original_image.copy()

def rotate_image(image):
    return None if image is None else cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

def resize_image(image, new_w, new_h):
    return None if image is None else cv2.resize(image, (new_w, new_h))

def crop_image(image, x, y, w, h):
    if image is None: return None
    h_img, w_img = image.shape[:2]
    x, y = max(0,x), max(0,y)
    w, h = min(w, w_img-x), min(h, h_img-y)
    return image[y:y+h, x:x+w]

# Các dialog nhập tham số (để tách UI khỏi app.py)
def resize_dialog(root, image, callback):
    if image is None: return image
    h, w = image.shape[:2]
    top = tk.Toplevel(root); top.title("Đổi cỡ ảnh")

    tk.Label(top, text="Chiều rộng:").grid(row=0,column=0,padx=5,pady=5)
    e_w = tk.Entry(top); e_w.insert(0,str(w)); e_w.grid(row=0,column=1)
    tk.Label(top, text="Chiều cao:").grid(row=1,column=0,padx=5,pady=5)
    e_h = tk.Entry(top); e_h.insert(0,str(h)); e_h.grid(row=1,column=1)

    def apply():
        try:
            new_w, new_h = int(e_w.get()), int(e_h.get())
            if new_w<=0 or new_h<=0: raise ValueError
            resized = resize_image(image,new_w,new_h)
            callback(resized); top.destroy()
        except: messagebox.showerror("Lỗi","Giá trị không hợp lệ")
    tk.Button(top,text="Áp dụng",command=apply).grid(row=2,column=0,columnspan=2,pady=10)
    return image

def crop_dialog(root, image, callback):
    if image is None: return image
    h, w = image.shape[:2]
    top = tk.Toplevel(root); top.title("Cắt ảnh")

    labels = ["x","y","width","height"]; defaults=[0,0,w,h]
    entries=[]
    for i,(lb,df) in enumerate(zip(labels,defaults)):
        tk.Label(top,text=lb).grid(row=i,column=0,padx=5,pady=5)
        e=tk.Entry(top); e.insert(0,str(df)); e.grid(row=i,column=1); entries.append(e)

    def apply():
        try:
            x,y,cw,ch = map(int,[e.get() for e in entries])
            cropped = crop_image(image,x,y,cw,ch)
            callback(cropped); top.destroy()
        except: messagebox.showerror("Lỗi","Giá trị không hợp lệ")
    tk.Button(top,text="Áp dụng",command=apply).grid(row=4,column=0,columnspan=2,pady=10)
    return image
