# Digitize and Visualize Data from Medical Devices

The **Digitize and Visualize Data from Medical Devices** project aims to address the need for digitizing and visualizing data from medical devices using computer vision techniques. This project is essential for enabling remote monitoring of medical devices that still rely on analog displays, making it challenging to access real-time data remotely. Additionally, the application extends to the agricultural industry, where analog tools are prevalent.

## Project Overview

The project involves converting numerical information displayed on analog gauge displays into digital data and transmitting it to a cloud-based database. The stored data will then be made accessible for visualization through Grafana. Furthermore, the project aims to apply machine learning techniques to predict future values or trends based on the collected data.


## Project Approach 

The core focus of this project lies in the process of converting numerical information displayed into digital data. We have devised a step-by-step approach to achieve this:

1. **LCD Localization**:
   - Edge detection to pinpoint the LCD on the device.
   
2. **LCD Extraction**:
   - Utilize edge map for contour identification.
   - Extract the largest rectangular region corresponding to the LCD using perspective transform.

3. **Digit Region Extraction**:
   - Utilize thresholding and morphological operations to extract digit regions within the LCD.

4. **Digit Identification**:
   - Divide digit regions into seven segments for digit recognition using OpenCV.

## How to Use

1. **Install pip:**
   - Ensure you have pip installed on your system. If not, follow the instructions provided on the [pip website](https://pip.pypa.io/en/stable/installation/) to install pip.

2. **Install Required Packages:**
   - Use pip to install the necessary packages by running the following command in your terminal or command prompt:
     ```
     pip install scipy opencv-python imutils flask flask_cors google-cloud google-cloud-vision google-api-core
     ```

3. **Run the Application:**
   - Once the required packages are installed, navigate to the directory containing the `main.py` file in your terminal or command prompt.
   - Run the `main.py` script using the following command:
     ```
     python main.py
     ```
