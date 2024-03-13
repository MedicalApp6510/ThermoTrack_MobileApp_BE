import cv2
import pytesseract

# 设置tesseract的路径
# 注意：这个路径需要根据你安装tesseract的实际路径来修改
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows示例

# 读取图像
image = cv2.imread("4.jpg")

# 转换为灰度图像
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 应用阈值化提高对比度
_, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# 自适应阈值
adaptive_thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)

# 形态学操作 - 腐蚀和膨胀
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
morph_image = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)

# 配置参数
custom_config = r'--oem 3 --psm 6 outputbase digits'

# 使用Pytesseract进行OCR识别
text = pytesseract.image_to_string(thresh_image, config=custom_config)

print("识别结果:", text)
