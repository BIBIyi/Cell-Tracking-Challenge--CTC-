import math

import numpy as np
import cv2 as cv
import os
import matplotlib.pyplot as plt
import random

def contrast_stretching(img):
    a = 0.
    b = 255.
    c = np.min(img)
    d = np.max(img)
    img = (img - c) * ((b-a)/(d-c)) + a
    return img.astype('uint8')



path = 'Sequences'

pics_dir = os.listdir(path)

#01 - 04三个sequence文件夹里的图片路径分别放到img_list中
img_list = [[],[],[],[]]
idx = 0
for i in pics_dir:
    pic_dir = os.path.join(path,i)
    print(pic_dir)
    if pic_dir.endswith("GT"):
        continue
    for img in os.listdir(pic_dir):
        if img.endswith(".tif"):
            img_dir = os.path.join(pic_dir, img)
            img_list[idx].append(img_dir)
    idx += 1


#画第一张图片，生成xy_colar字典
def first_draw(new_contours,image):
    for i,j in zip(new_contours, range(len(new_contours))):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = (b,g,r)
        #print(color)
        cv.drawContours(image, i, -1, color, 3)
        M = cv.moments(i)  # 计算矩
        cx = int(M['m10'] / M['m00'])  # 计算重心
        cy = int(M['m01'] / M['m00'])

        cv.putText(image, str(j), (cx, cy), 1, 1, (255, 0, 255), 1)
        xy_color[(cx,cy)] = color


#根据画第一张图生成的xy_color字典里的颜色来
def draw(new_contours, image):
    area = 0
    new_add = [] #记录新添加到xy_color的元素
    for i,j in zip(new_contours, range(len(new_contours))):
        M = cv.moments(i)  # 计算矩
        cx = int(M['m10'] / M['m00'])  # 计算重心
        cy = int(M['m01'] / M['m00'])
        #找与第一张图中细胞重心相近位置对应的颜色，距离最小的(x,y)对应的颜色
        #min_distance = 0
        min_color = 0
        match_same = [] #可能有超过一个点满足条件，记录下来
        for key in xy_color.keys():
            #print(key)

            if math.sqrt((key[0]-cx)**2 + (key[1]-cy)**2) < 30:
                #min_distance = math.sqrt((key[0]-cx)**2 + (key[1]-cy)**2)
                dist = math.sqrt((key[0] - cx) ** 2 + (key[1] - cy) ** 2)
                #print('key:',key)
                match_same.append((key,dist))

        if len(match_same) == 1:
            #如果与之匹配的点也是刚新添加的，说明目前这个点是一个细胞分裂后的两个点之一，赋予新颜色
            if match_same[0][0] in new_add:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                xy_color[(cx, cy)] = (r,g,b)
                min_color = xy_color[(cx, cy)]
            else:
                #print('match_same:', match_same[0][0])
                xy_color[(cx,cy)] = xy_color[match_same[0][0]]
                print(xy_color[(cx,cy)])
                color = xy_color[(cx,cy)]
                del[xy_color[match_same[0][0]]]
                new_add.append((cx,cy))
                min_color = color
                #print('min_color:',min_color)
        #匹配到两个以上就取距离dist最小的那个
        elif len(match_same) > 1:
            sorted(match_same, key=lambda x:x[1])

            if match_same[0][0] in new_add:
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                xy_color[(cx, cy)] = (r,g,b)
                min_color = xy_color[(cx, cy)]
            else:
                xy_color[(cx, cy)] = xy_color[match_same[0][0]]
                color = xy_color[(cx, cy)]
                del[xy_color[match_same[0][0]]]
                new_add.append((cx, cy))
                min_color = color
        else:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            xy_color[(cx, cy)] = (r, g, b)
            min_color = xy_color[(cx, cy)]


        cv.drawContours(image, i, -1, min_color, 3)
        cv.putText(image, str(j), (cx, cy), 1, 1, (255, 0, 255), 1)


#将处于分裂过程的细胞用红圈标记出来，1。单独一个轮廓的细胞如轮廓面积大于平均面积的1.4判定为分裂状态
#2. 两个轮廓的细胞（也就是两个细胞）的各自最小外接圆相交，判定处于分裂状态
def draw_circle(new_contours, image, avg_area):
    point_r = []
    for i, j in zip(new_contours, range(len(new_contours))):
        (x, y), radius = cv.minEnclosingCircle(i)
        point_r.append((x,y,int(radius)))
    for point1 in point_r:
        for point2 in point_r:
            if point1 == point2:
                continue
            if math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2) < point1[2]+point2[2]-2:
                cv.circle(image, (int((point1[0]+point2[0])/2), int((point1[1]+point2[1])/2)), point1[2]+point2[2]+15, (255,0,0), 0)
                break

    for i, j in zip(new_contours, range(len(new_contours))):
        #print(cv.contourArea(i))
        if cv.contourArea(i) > avg_area * 1.4:
            (x, y), radius = cv.minEnclosingCircle(i)
            cv.circle(image, (int(x),int(y)) , int(radius+15), (255,0,0),0)




#{(1,1): (100,100,100),......} #细胞轮廓重心为(1,1)时对应的bgr颜色
xy_color = {}
flag = 0
#存画完后的图
image_res = []

#img_list[0] -> 第一个sequence目录下的图片，seqnence01
for img in img_list[0][0:10]:

    image = cv.imread(img)
    imGray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    img_gray = np.array(imGray)

    # print("img_shape:", img_gray.shape)
    # print("max_value:", np.max(img_gray))
    # print("min_value:", np.min(img_gray))

    img_gray = contrast_stretching(img_gray)

    # print("max_value:", np.max(img_gray))
    # print("min_value:", np.min(img_gray))

    ret, img_gray_th = cv.threshold(img_gray, 50, 255, 0)

    image1, contours, hierarchy = cv.findContours(img_gray_th, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    #提取轮廓面积大于60的细胞
    new_contours = [contour for contour in contours if cv.contourArea(contour) >= 60]
    #计算平均面积
    total_area = 0
    for contour in new_contours:
        area = cv.contourArea(contour)
        total_area = area + total_area
    avg_area = total_area/(len(new_contours)+1)
    #print("area:", area/(len(new_contours)+1))
    #计算图片有多少个细胞
    #print(len(new_contours))

    if flag == 0:
        first_draw(new_contours, image)
        flag = 1
        print(xy_color)
        draw_circle(new_contours, image, avg_area)




    else:
        draw(new_contours, image)
        draw_circle(new_contours, image, avg_area)


    image_res.append(image)

plt.imshow(image_res[0])
plt.title("1")
plt.show()


plt.imshow(image_res[1])
plt.title("2")
plt.show()


plt.imshow(image_res[2])
plt.title("3")
plt.show()


plt.imshow(image_res[3])
plt.title("4")
plt.show()

plt.imshow(image_res[4])
plt.title("5")
plt.show()

