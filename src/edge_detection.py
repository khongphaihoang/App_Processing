import cv2, numpy as np

def grayscale_image(image):
    if image is None: return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

def blur_image(image):
    return None if image is None else cv2.GaussianBlur(image,(5,5),0)

def sobel_detection(image):
    if image is None: return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    sobel_x = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F,1,0,ksize=3))
    sobel_y = cv2.convertScaleAbs(cv2.Sobel(gray, cv2.CV_64F,0,1,ksize=3))
    return cv2.cvtColor(cv2.addWeighted(sobel_x,0.5,sobel_y,0.5,0), cv2.COLOR_GRAY2BGR)

def prewitt_detection(image):
    if image is None: return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    kx = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
    ky = np.array([[-1,-1,-1],[0,0,0],[1,1,1]])
    px = cv2.convertScaleAbs(cv2.filter2D(gray,-1,kx))
    py = cv2.convertScaleAbs(cv2.filter2D(gray,-1,ky))
    return cv2.cvtColor(cv2.addWeighted(px,0.5,py,0.5,0), cv2.COLOR_GRAY2BGR)
def mean_denoise(image, ksize=5):
    """Khử nhiễu bằng lọc trung bình."""
    if image is None: return None
    return cv2.blur(image, (ksize, ksize))

def median_denoise(image, ksize=5):
    """Khử nhiễu bằng lọc trung vị."""
    if image is None: return None
    return cv2.medianBlur(image, ksize)
