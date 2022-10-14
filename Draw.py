import cv2
import copy
import matplotlib.pyplot as plt
from Motion import Motion
import random

"""
 drawing contours and tracks images with  unique color 
"""

class Drawer:
    def __init__(self,Motion, Preprocessor):
        self.Motion = Motion
        self.Preprocessor = Preprocessor

        self.final_images= []  # 存放全部的含轮廓的images
        self.track_images = []  # 存放全部的 track image

        self.cells_list = [] # 存放每张图的cells历史
        self.color_list = self.color()

    def color(self):
        list1 = []
        for i in range(300):
            rbg = [random.randrange(256)for x in range(3)]
            list1.append(rbg)
        return list1

    def Draw(self):
        #print("color",self.color_list)
        while self.Preprocessor.status !=False:
            #读取当前图片与cells信息
            cells =self.Motion.next(self.cells_list)
            self.cells_list.append(copy.deepcopy(cells))

            for index in range(self.Preprocessor.counter):
                # print("index",index)
                current_image = cv2.imread(self.Preprocessor.original_images[self.Preprocessor.counter])
                current_image = cv2.cvtColor(current_image, cv2.COLOR_BGR2RGB)

            final_image = current_image.copy()
            # 遍历每个cell
            for cell in cells.values():
                # print(cell.get_childCell())

                color = self.color_list[cell.get_id()]
                final_image = cv2.drawContours(final_image, cell.get_contour(), -1, color, 3)
                cv2.putText(final_image, str(cell.get_id()), cell.get_center(), 1, 1, (0, 0, 0), 1)

                # 判断是否处于有丝中，如果是，则要红圈标记，不是则不用
                if cell.get_childCell() == True:
                    # print("index",index)
                    (x, y), radius = cv2.minEnclosingCircle(cell.get_contour())
                    final_image = cv2.circle(final_image, (int(x), int(y)), int(radius + 10), (255, 0, 0), 0)

                # 显示每个细胞根据id由不同颜色
                # Draw previous track image
                pre_centers = cell.get_precenter()
                #### draw with different color
                for k in range(len(pre_centers) - 1):
                    current_image = cv2.line(current_image, pre_centers[k], pre_centers[k + 1], color, 2, 4)
                cv2.putText( current_image, str(cell.get_id()), cell.pre_center[0], 1, 1, (0, 0, 0), 1)

            self.final_images.append(final_image)
            self.track_images.append(current_image)


    #展示所需的图片
    def display(self,number):
        img = self.final_images[number]
        img_track =self.track_images[number]

        #task3-1.3-2。3-3.3-4
        cell_count = len(self.cells_list[number])
        cell_avg_area = self.Motion.agv_area[number]
        cell_avg_dist = self.Motion.agv_dist[number]
        cell_dividing_count = self.Motion.mitosis_count[number]

        img= cv2.putText(img, f'avg_area:{round(cell_avg_area,3)}',(30,30), 1, 1, (0, 0, 0), 1)
        img = cv2.putText(img, f'avg_dist:{round(cell_avg_dist,3)}', (30, 45), 1, 1, (0, 0, 0), 1)
        img = cv2.putText(img, f'cell count:{cell_count}, dividing cells count:{cell_dividing_count}',
                          (30, 60), 1, 1, (0, 0, 0), 1)

        return img,img_track
