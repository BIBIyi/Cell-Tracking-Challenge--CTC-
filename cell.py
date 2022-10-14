'''
A identity for one cell's information
'''

import numpy as np
from collections import OrderedDict, defaultdict
# save all information of a cell, including task 3
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

class Cell():
    def __init__(self,id,contour,center,area,childCell=False):
        self.id = id        # unique
        self.contour = contour  # contour
        self.center = center       # center coordinates
        self.dist = 0  # the first image cells distance is 0
        self.area = area       #

        # record the track center coordinates
        self.pre_center = [center]  # include self cenetr
        self.childCell = childCell  # if true,dividing  need a thick red circle

    # 更新 cell 数据 update information
    def update_center(self, center):
        # 不包含自己中心点，center是父辈cell的center
        #在pre-center 开头插入旧的center list
        self.pre_center = center

    # 更新 cell 数据 update information
    def update(self, contour, center, area,dist):
        # 之前中心点，为了回头画track，can see the track finally
        # 轮廓
        self.contour = contour
        # 中心点,面积
        self.area = area
        self.center = center
        # 移动后添加当前点
        self.pre_center.append(center)
        # 计算当前图cell与上一张之间的位移
        #self.dist = self.distance(self.center, self.pre_center[-1])
        self.dist = dist
    #更新cell的状态，变成有丝中

    def change(self):
        self.childCell =True

    def get_id(self):
        return self.id

    def get_contour(self):
        return self.contour

    def get_center(self):
        return self.center

    def get_area(self):
        return self.area

    def get_dist(self):
        return self.dist
    def get_precenter(self):
        return self.pre_center

    def get_parentid(self):
        return self.parentid

    def get_childCell(self):
        return self.childCell


