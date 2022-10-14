"""
this part is to analyse the motion of cells
like add ,delete,update cells information
"""
# overall cells information from one Sequence
from cell import Cell
import cv2
import numpy as np
import matplotlib.pyplot as plt

Max_ratio = 0.7
Min_ratio =0.3
Max_dis = 15
def distance(p1, p2):
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# the contours of the mask image
def Contours(mask):
    # find contours from one mask image
    image = mask.copy()
    image1, contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # 提取轮廓面积大于60的细胞
    new_contours = [contour for contour in contours if cv2.contourArea(contour) >= 60]
    return image1,new_contours
#Gets rotation of ellipse
def ratio(contour):
    ellipse = cv2.fitEllipse(contour)
    centerE = ellipse[0]
    # Gets rotation of ellipse; same as rotation of contour
    rotation = ellipse[2]
    # Gets width and height of rotated ellipse
    widthE = ellipse[1][0]
    heightE = ellipse[1][1]
    ratio = widthE/heightE
    return ratio
# agv_area and centers
def area_center(Contours):
    centers =[]
    areas = []
    for i, j in zip(Contours, range(len(Contours))):
        M = cv2.moments(i)  # 计算矩
        cx = int(M['m10'] / M['m00'])  # 计算重心
        cy = int(M['m01'] / M['m00'])
        centers.append((cx,cy))
        areas.append(cv2.contourArea(i))
    return centers,areas

class Motion:
    def __init__(self,processed):
        self.Preprocessor =processed # 存储全部的imags 数据
        self.id_cell = 0 # 分配id 给cells，unique
        self.existing_cells = {} # 已经存在的cell信息 store cells information in dict

        self.agv_area = [] # task3-2 细胞大小平均值
        self.agv_dist =[] # task3-3 平均位移
        self.mitosis_count = [] #task3-4 正在分裂的细胞数

    # add a new cell
    def addCell(self,contour,center,area):
        #print(self.id_cell,self.count_cells)
        self.existing_cells[self.id_cell] = Cell(self.id_cell, contour, center, area)
        self.id_cell += 1

    # delete old cell
    def deleteCell(self,id):
        del self.existing_cells[id]

    # compare with pre image
    # updates cell information if a cell has a track or split in the current frame.
    # pre_pre_cells_his is the memory of cells for pre images, use this to compare the pre cells ,and find the same cells or split
    def next(self,cells_list):
        image, processor_img =self.Preprocessor.next()
        # 得到这张图的所有轮廓
        image1,contours = Contours(processor_img)
        # 得到全图中心点与平均细胞面积
        centers, areas = area_center(contours)

        all_dist = 0
        all_area =0
        mitosis_count = 0

        #print("===")
        #print("第几张图：", self.Preprocessor.counter)
        #print("新图片有几个轮廓:",len(contours))


        # first image ,add all new cells
        if len(cells_list) == 0:
            for contour, center, area in zip(contours, centers,areas):
                self.addCell(contour, center, area)
        #与前图进行比较
        else:
            #print("mis",mitosis_count)
            old_cells = cells_list[-1]
            # 清空，一个个作对比,满足的放进去
            self.existing_cells = {}
            # i is the id for cells, unique
            for i in old_cells:
                #print("第几个id：",i)

                old_id = Cell.get_id(old_cells[i])
                old_contour =Cell.get_contour(old_cells[i])
                old_center = Cell.get_center(old_cells[i])
                old_area =Cell.get_area(old_cells[i])
                old_status = Cell.get_childCell(old_cells[i])

                #计算每个中心点到这个old cell这个点的距离，找到最小的
                # the date of  contour, cent, area ,dist  for nearest cell for old cells
                #print("center:",old_center)


                dist = [(distance(centers[j],old_center), j) for j in range(len(contours))]

                sort_dist = sorted(dist, key=lambda x: x[0], reverse=False)

                min_dist, min_inddx= sort_dist[0]
                second_min_dist,second_index = sort_dist[1]

                min_contour = contours[min_inddx]
                #center
                min_center = centers[min_inddx]
                second_center = centers[second_index]
                # areas
                min_area = areas[min_inddx]
                second_area = areas[second_index]
                #print("area:",min_area,second_area)


                #判断old cell是否处于有丝分裂中
                #不是有丝分裂
                new_ratio = ratio(min_contour)
                if old_status == False:

                    #开始有丝分裂
                    if new_ratio < Max_ratio and (second_min_dist -min_dist) <Max_dis :
                        #print("starting diving...")
                        #print("parent id",i)

                        #print("min,second",min_center,second_center)

                        #更新他们的dist，要包含旧的parent的轨迹+自己的中心点
                        new_pre_center1 = [old_center]
                        new_pre_center1.append(min_center)

                        new_pre_center2 = [old_center]
                        new_pre_center2.append(second_center)


                        # 创建两个新id cell，删除旧的
                        self.addCell(contours[min_inddx], min_center, (areas[min_inddx]))
                        # 把pre_center 更新
                        self.existing_cells[self.id_cell-1].update_center(new_pre_center1)
                        # 把两个状态变成处于有丝分裂中
                        self.existing_cells[self.id_cell-1].childCell = True
                        #self.existing_cells[self.id_cell-1].change()
                        #print("change：",Cell.get_childCell(self.existing_cells[self.id_cell-1]))
                        #print("min_id:",self.existing_cells[self.id_cell-1].id)
                        #print("per_center:",self.existing_cells[self.id_cell-1].pre_center)

                        self.addCell(contours[second_index], second_center, areas[second_index])
                        # 把pre_center 更新
                        self.existing_cells[self.id_cell - 1].update_center(new_pre_center2)
                        #self.existing_cells[self.id_cell - 1].change()
                        self.existing_cells[self.id_cell - 1].childCell = True
                        #print("dividing tw oid:", self.id_cell - 2,self.id_cell - 1)

                        #更新总位移
                        all_dist += min_dist
                        all_dist += second_min_dist

                        #更新总面积
                        all_area += min_area
                        all_area += second_area
                        #多了两个有丝分裂细胞
                        mitosis_count = mitosis_count +2

                    else:
                        #print("没有有丝分裂")
                        #没有有丝分裂，选择最近的点，更新
                        self.existing_cells[old_id] = old_cells[i]
                        self.existing_cells[old_id].update(contours[min_inddx], centers[min_inddx],areas[min_inddx], min_dist)

                        all_dist += min_dist
                        all_area += min_area

                #有丝中,取最近的一个点
                else:

                    #判断是否还处于有丝状态中
                    #椭圆形
                    self.existing_cells[old_id] = old_cells[i]
                    self.existing_cells[old_id].update(contours[min_inddx], centers[min_inddx], areas[min_inddx], min_dist)

                    all_dist += min_dist
                    all_area += min_area

                    #still dividing
                    if new_ratio<Min_ratio :
                        #print("3")
                        #print("this cell is still dividing...id is ",i)
                        #有丝细胞数量+1
                        mitosis_count +=1
                        # 把上一张cell数据放入相同id里面

                    #finish dividing
                    else:
                        #print("4")
                        #print("finish dividing,id:",i)
                        self.existing_cells[old_id].childCell=False

        count_cells=len(self.existing_cells)

        #for i in self.existing_cells:
            #print(self.existing_cells[i].childCell)
        self.agv_dist.append(all_dist/count_cells)  # task3-3 平均位移
        self.mitosis_count.append(mitosis_count)  # task3-4 正在分裂的细胞数
        self.agv_area.append(all_area/count_cells)
        #print("mis",mitosis_count)
        #print(self.existing_cells)
        return self.existing_cells


