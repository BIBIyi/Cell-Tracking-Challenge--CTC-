import math
import numpy as np
import cv2
import matplotlib.pyplot as plt


"""
Preprocessor processes the original input images.
mask is the the Preprocessor images as a list.
no GT files images.
"""

# stretching image
def contrast_stretching(img):
    rows, cols = img.shape
    img_O = np.zeros((rows, cols), dtype=np.uint8)
    a = 0.
    b = 255.
    c = np.min(img)
    d = np.max(img)
    img_O = (img - c) * ((b - a) / (d - c)) + a
    return img_O.astype(np.uint8)

class Preprocessor:
    def __init__(self, images):
        self.original_images = images   # 存放原始图片 original images
        self.processor_img = self.pre_processing(images) # 存放改变后的图,无轮廓

        self.count_image = len(images)  # 图片总数 images count
        self.counter = 0 # 记录第几张图keep track of current image counter
        self.status = True  # True-运行中 False=done,no next

    def next(self):
        # Indicate when done 判断是否为最后一张
        # read next (i-counter) image 读取下一张原图和修改后的图
        image = cv2.imread(self.original_images[self.counter],cv2.IMREAD_GRAYSCALE)
        processor_img = self.processor_img[self.counter]
        self.counter += 1

        if int(self.count_image) <= self.counter + 1:
            self.status = False
        return image, processor_img

    # Image processing, easy to extract cell
    def pre_processing(self,images):
        processed = []
        for img in images:
            image = cv2.imread(img)
            imGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            img_gray = np.array(imGray)
            # Step 1 -stretching image
            img_gray = contrast_stretching(img_gray)
            # Step 2 - Binarize via thresholding
            ret, img_gray_th = cv2.threshold(img_gray, 0, 255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed.append(img_gray_th)

            #plt.title(f"the original image")
            #plt.imshow(image)
            #plt.show()
            #plt.title(f"step1 image")
            #plt.imshow(img_gray)
            #plt.show()
            #plt.title(f"step2 image")
            #plt.imshow(img_gray_th)
            #plt.show()

        #plt.imshow(processed[-1],'gray')
        #plt.show()
        return processed


