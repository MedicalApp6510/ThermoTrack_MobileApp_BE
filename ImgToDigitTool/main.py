# Import necessary libraries
import sys
import cv2
from imutils.perspective import four_point_transform
from imutils import contours
import imutils
import urllib.request
import numpy as np
import ssl
import warnings

import json

# import requests
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

warnings.filterwarnings("ignore", category=DeprecationWarning)




# def ocr_space_url(url, overlay=False, api_key='helloworld', language='eng', OCREngine='2', filetype='JPG'):
#     """ OCR.space API request with remote file.
#         Python3.5 - not tested on 2.7
#     :param url: Image url.
#     :param overlay: Is OCR.space overlay required in your response.
#                     Defaults to False.
#     :param api_key: OCR.space API key.
#                     Defaults to 'helloworld'.
#     :param language: Language code to be used in OCR.
#                     List of available language codes can be found on https://ocr.space/OCRAPI
#                     Defaults to 'en'.
#     :return: Result in JSON format.
#     """
#
#     payload = {'url': url,
#                'isOverlayRequired': overlay,
#                'apikey': api_key,
#                'language': language,
#                'OCREngine': OCREngine,
#                'filetype': filetype,
#                }
#     r = requests.post('https://api.ocr.space/parse/image',
#                       data=payload,
#                       )
#     # return r.content.decode()
#     return r.json()
#

# Main function
def process_image(image_url):
    # Load the image from URL or file path
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    req = urllib.request.urlopen(image_url, context=ssl_context)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    print('arr loaded')
    image = cv2.imdecode(arr, -1)
    if image is None:
        raise ValueError("Image not found or unable to load.")
    # cv2.imshow("Example Image", image)
    # cv2.waitKey(0)

    # Preprocess the image
    print("2. Preprocessing image...")
    image = imutils.resize(image, height=500)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 255)
    # cv2.imshow("Edged Image", edged)
    # cv2.waitKey(0)

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

    # Extract and apply perspective transform to the display region
    print("4. Extracting and applying perspective transform to the display region...")
    warped = four_point_transform(gray, displayCnt.reshape(4, 2))
    output = four_point_transform(image, displayCnt.reshape(4, 2))
    # cv2.imshow("Warped Image", warped)
    # cv2.imshow("Output Image", output)
    # cv2.waitKey(0)

    # Threshold and apply morphological operations to the display region
    print("5. Thresholding and applying morphological operations to the display region...")
    # thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # set the const threshold
    THRESHOLD_VALUE = 100  # change it by the case
    thresh = cv2.threshold(warped, THRESHOLD_VALUE, 255, cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 4))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    # cv2.imshow("Thresholded Image", thresh)
    # cv2.waitKey(0)

    # Find contours of the digit regions
    print("6. Finding contours of the digit regions...")
    cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour_image = image.copy()
    cv2.drawContours(contour_image, cnts, -1, (0, 255, 0), 2)  # Draw all the contours in green
    # cv2.imshow("Contour Image", contour_image)
    # cv2.waitKey(0)

    # Iterate over digit region contours
    digitCnts = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        if w >= 15 and (h >= 60 and h <= 125):  # TODO: REFINE THIS NUM
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

            # Check if the segment is on
            if total / float(area) > 0.47:
                on[i] = 1

        # Find the digit and draw on the output image
        try:
            print("Number:", on)
            digit = DIGITS_LOOKUP[tuple(on)]
            digits.append(digit)
            # Display the digit area
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)  # Green color for recognized digits
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
    # cv2.imshow("Input", image)
    # cv2.imshow("Output", output)
    # cv2.waitKey(0)

    # Return the recognized digits
    return digits



##################################################################
#   You can use the following for local testing in the cmd line  #                 #
#   Format: python main.py <image_url>                           #
#   Example: python main.py https://example.com/image.jpg        #
##################################################################
if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python main.py <image_url>")
        sys.exit(1)

    # Get the image URL from command-line arguments
    image_url = sys.argv[1]

    # Process the image and print the result
    try:
        result = process_image(image_url)
    except Exception as e:
        print("Error:", e)


# if __name__ == "__main__":
#     # test_file = ocr_space_file(filename='2.jpg', language='eng', api_key='45ab054be488957', OCREngine='2')
#     # test_url = ocr_space_url(url='https://imgur.com/a/3333')
#     test_url = ocr_space_url(url='https://i.redd.it/m84cd3haccay.jpg', language='eng', api_key='45ab054be488957',
#                              OCREngine='2')
#
#     print(json.dumps(test_url, indent=4, ensure_ascii=False))
