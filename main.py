# Import necessary libraries
import cv2
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
# At the beginning of your script, add this line:
import numpy as np

# Define mapping from seven-segment display states to digits
DIGITS_LOOKUP = {
    (1, 1, 1, 0, 1, 1, 1): 0,
    (0, 0, 1, 0, 0, 1, 0): 1,
    (1, 0, 1, 1, 1, 1, 0): 2,
    (1, 0, 1, 1, 0, 1, 1): 3,
    (0, 1, 1, 1, 0, 1, 0): 4,
    (1, 1, 0, 1, 0, 1, 1): 5,
    (1, 1, 0, 1, 1, 1, 1): 6,
    (1, 0, 1, 0, 0, 1, 0): 7,
    (1, 1, 1, 1, 1, 1, 1): 8,
    (1, 1, 1, 1, 0, 1, 1): 9
}
# DIGITS_LOOKUP[(1, 1, 1, 0, 0, 0, 1)] = '特殊符号'  # 这里的元组需要根据实际识别的结果来填写

# Load the example image
print("1. Loading example image...")
image = cv2.imread("2.jpg")
cv2.imshow("Example Image", image)
cv2.waitKey(0)

# Preprocess the image
print("2. Preprocessing image...")
image = imutils.resize(image, height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 50, 200, 255)
cv2.imshow("Edged Image", edged)
cv2.waitKey(0)

# Find contours of the display region
print("3. Finding contours of the display region...")
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
displayCnt = None

# Iterate over contours
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    if len(approx) == 4:
        displayCnt = approx
        break


# 假设displayCnt是找到的四个点
displayCnt = displayCnt.reshape(4, 2)
# 对四个点进行排序，以保证透视变换后图像不会旋转
rect = np.zeros((4, 2), dtype="float32")

# 计算左上、右上、右下和左下的点
# 这是基于点的x+y和x-y值
s = displayCnt.sum(axis=1)
rect[0] = displayCnt[np.argmin(s)]
rect[2] = displayCnt[np.argmax(s)]

diff = np.diff(displayCnt, axis=1)
rect[1] = displayCnt[np.argmin(diff)]
rect[3] = displayCnt[np.argmax(diff)]

# 透视变换
warped = four_point_transform(gray, rect)
output = four_point_transform(image, rect)


# Extract and apply perspective transform to the display region
print("4. Extracting and applying perspective transform to the display region...")
# warped = four_point_transform(gray, displayCnt.reshape(4, 2))
# output = four_point_transform(image, displayCnt.reshape(4, 2))
cv2.imshow("Warped Image", warped)
cv2.imshow("Output Image", output)
cv2.waitKey(0)

# Threshold and apply morphological operations to the display region
print("5. Thresholding and applying morphological operations to the display region...")
# thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
# 修改后的代码，设定固定阈值：
THRESHOLD_VALUE = 100  # 需要根据实际情况调整这个值
thresh = cv2.threshold(warped, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV)[1]

# 调整形态学操作：
# 形态学操作的目的是清理图像，但是过度的操作可能会破坏数字。减少操作的强度可能有助于保留数字的完整性。
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 2))  # 更小的核可能会更好
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
cv2.imshow("Thresholded Image", thresh)
cv2.waitKey(0)

# 在检测轮廓之前确保至少有一些轮廓被发现
if len(cnts) == 0:
    print("No contours found after thresholding and morphological operations.")
    exit()  # 如果没有轮廓，则退出程序

# Find contours of the digit regions
print("6. Finding contours of the digit regions...")
cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contour_image = image.copy()
cv2.drawContours(contour_image, cnts, -1, (0, 255, 0), 2)  # Draw all the contours in green
cv2.imshow("Contour Image", contour_image)
cv2.waitKey(0)

# 检查图像是否需要旋转，以纠正方向
# 这里的角度angle需要根据实际情况调整
angle = 0  # 这个角度需要你根据图像实际旋转的角度来设定
(h, w) = output.shape[:2]
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, angle, 1.0)
rotated = cv2.warpAffine(output, M, (w, h))

# 显示旋转后的图像
cv2.imshow("Rotated Image", rotated)
cv2.waitKey(0)


# Iterate over digit region contours
digitCnts = []
for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    # if w >= 15 and (h >= 60 and h <= 125): # TODO: REFINE THIS NUM
    if (w >= 10 and w <= 60) and (h >= 10 and h <= 180):  # 这里的值需要根据实际情况进行调整  #3.这个调完有点用
    # if w >= 5 and (h >= 30 and h <= 150):  #不行
        digitCnts.append(c)

# Sort digit contours from left to right
digitCnts = contours.sort_contours(digitCnts, method="left-to-right")[0]
digits = []

# Iterate over each digit
print("7. Current seven-segment display state:")
for c in digitCnts:
    (x, y, w, h) = cv2.boundingRect(c)
    roi = thresh[y:y + h, x:x + w]
    (roiH, roiW) = roi.shape
    (dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
    dHC = int(roiH * 0.05)
    segments = [
        ((0, 0), (w, dH)),  # top
        ((0, 0), (dW, h // 2)),  # top-left
        ((w - dW, 0), (w, h // 2)),  # top-right
        ((0, (h // 2) - dHC), (w, (h // 2) + dHC)),  # center
        ((0, h // 2), (dW, h)),  # bottom-left
        ((w - dW, h // 2), (w, h)),  # bottom-right
        ((0, h - dH), (w, h))  # bottom
    ]
    on = [0] * len(segments)

    # Iterate over each segment of the seven-segment display
    for (i, ((xA, yA), (xB, yB))) in enumerate(segments):
        segROI = roi[yA:yB, xA:xB]
        total = cv2.countNonZero(segROI)
        area = (xB - xA) * (yB - yA)
        # Check if the area is zero and skip if it is
        if area == 0:
            print("Segment area is zero, which may indicate an issue with segment ROI extraction.")
            continue  # Skip this segment and continue with the next

        SEGMENT_ON_THRESHOLD = 0.3  # This value may need to be adjusted based on your image
        if total / float(area) > SEGMENT_ON_THRESHOLD:
            on[i] = 1


        # 原代码中的判断条件：
        # if total / float(area) > 0.47:

        # 修改建议，调整比例：检查七段显示的识别逻辑：
        # 您当前的逻辑是用一个固定的比例来确定一个段是否是“开”。您可能需要调整这个比例，或者考虑实现更复杂的逻辑，例如考虑到各个段之间的相对亮度。
        SEGMENT_ON_THRESHOLD = 0.3  # 需要根据实际情况调整这个值  #大于0.5就不行了  0.01-0.25显示8   0.3显示9  0.4显示x
        if total / float(area) > SEGMENT_ON_THRESHOLD:
            on[i] = 1

    # Find the digit and draw on the output image
    try:
        print("Number:", on)
        digit = DIGITS_LOOKUP[tuple(on)]
        digits.append(digit)
        # Display the digit area
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1) # Green color for recognized digits
        cv2.putText(output, str(digit), (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    except KeyError:
        print(KeyError);
        digit = 'x'
        digits.append(digit)
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 0, 255), 1)  # Red color for unrecognized digits
        cv2.putText(output, str(digit), (x - 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

# Display recognition results
print("8. Recognized digits:", digits)
cv2.imshow("Input", image)
cv2.imshow("Output", output)
cv2.waitKey(0)
