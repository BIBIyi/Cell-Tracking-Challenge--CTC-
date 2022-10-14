'''
python 3.7
openc 3.4.2
'''
import math
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt
import random

from Draw import Drawer
import processor
import Motion
# 取三位小数 Three decimal point

if __name__ == '__main__':
    path = 'Sequences'
    pics_dir = os.listdir(path)

    # read images form 4 packages
    # 输出所有文件和文件夹
    # 01 - 04三个sequence文件夹里的图片路径分别放到img_list中
    img_list = [[], [], [], []]
    idx = 0
    for i in pics_dir:
        pic_dir = os.path.join(path, i)
        #print(pic_dir)

        if pic_dir.endswith("GT"):
            continue
        for img in os.listdir(pic_dir):
            if img.endswith(".tif"):
                img_dir = os.path.join(pic_dir, img)
                img_list[idx].append(img_dir)
        idx += 1

    print('install all the cells...')
    print('choose the data from 1-4 files')
    filenb = int(input("file_number: "))-1
    #filenb = 0

    # img_list[0] -> 第一个sequence目录下的图片，seqnence01
    # 处理图片
    # Image processing, easy to extract cell
    pre_images = processor.Preprocessor(img_list[filenb][:15])
    # 设置轮廓，处理不要的轮廓,设置cells
    Mo_images = Motion.Motion(pre_images)
    drawer = Drawer(Mo_images, pre_images)

    drawer.Draw()
    # the image yu want to display:

    while True:
        #
        print("input the number of integer(1,2,3...),if you want to finish,input no-integer")
        img_number = input("the image you want to see:")
        if img_number.isdigit():
            img, img_track = drawer.display(int(img_number)-1)
            plt.title(f"the {img_number} image")
            plt.imshow(img)
            plt.show()
            #plt.savefig(f"the {img_number} image")
            plt.title(f"the {img_number} track image")
            plt.imshow(img_track)
            plt.show()
        else:
            print("finish... ")
            break










