# PageRank分块算法
# Block Stripe PageRank算法


# 数据集请命名为WikiData.txt
# 数据集请放置于与该文件同一目录下
# 迭代过程中生成的Matrix将存储在BlockFiles文件夹中
# 迭代过程中生成的R将存储在tempRFile文件夹中
# 全部节点的PageRank值会输出在AllNodePageRank.txt文件中
# PageRank值前100会输出在Top100PageRank.txt文件中
# AllNodePageRank.txt和Top100PageRank.txt文件均与该文件同一目录中

import re
import time
import struct
import os


# 稀疏矩阵结构
class SparseMatrix:
    nodeNum = 0  # 节点编号
    outDegree = 0  # 节点出度
    outSet = None  # 所有出度节点编号

    # 类构造函数
    def __init__(self, num):
        self.nodeNum = num
        self.outDegree = 0
        self.outSet = set()


# 分析数据
class DataAnalysis:
    fromNode = set()  # from节点集合
    toNode = set()  # to节点集合
    allNode = None  # 全部节点集合

    nodeCount = 0  # 全部节点个数
    RCount = 0  # R矩阵的大小

    matrix = set()  # 稀疏矩阵，每个都是SparseMatrix对象
    R = []  # PageRank矩阵

    BETA = 0.85  # β值
    ERROR = 1E-10  # 误差阈值
    finalError = 0.0  # 最终误差值

    BlockSize = 100  # 分块大小
    hash = [0] * 8298
    LinkCout = 0

    Round = 0  # R矩阵迭代的轮数
    MAXnum = 0 # 最大的节点编号

    # 类构造函数
    def __init__(self, fileName):
        start = time.perf_counter()
        try:
            self.readFile(fileName)
        except BaseException as e:
            print("Exception in readFile().")
            print(str(e))
            exit(1)
        end1 = time.perf_counter()
        T1 = end1 - start
        print("Read " + fileName + " complete.")
        print("cost: " + str(T1) + 's' )

        try:
            self.getNum()
        except BaseException as e:
            print("Exception in getNum().")
            print(str(e))
            exit(1)
        end2 = time.perf_counter()
        T2 = end2 - end1
        print("Get all nodes completed.")
        print("cost: " + str(T2) + 's')

        try:
            self.BS_genStripe()
        except BaseException as e:
            print("Exception in BS_genStripe().")
            print(str(e))
            exit(1)
        end3 = time.perf_counter()
        T3 = end3 - end2
        print("Preparing stripe blocks completed.")
        print("cost: " + str(T3) + 's')


        try:
            self.BS_genRMatrix()
        except BaseException as e:
            print("Exception in BS_genRMatrix().")
            print(str(e))
            exit(1)

        end4 = time.perf_counter()
        T4 = end4 - end3
        print("Initialize R matrix complete.")
        print("cost: " + str(T4) + 's')

        print("Start calculation...")
        try:
            while self.BS_updateR() == False:
                pass
        except BaseException as e:
            print("Exception in BS_updateR().")
            print(str(e))
            exit(1)
        print("The error value of pangerank is " + str(self.finalError) + ".")
        end5 = time.perf_counter()
        T5 = end5 - end4
        print("Pangerank calculation completed.")
        print("cost: " + str(T5) + 's')

        print("Write data to AllNodePageRank.txt file...")
        try:
            self.writeAllNode("AllNodePageRank.txt")
        except BaseException as e:
            print("Exception in writeAllNode().")
            print(str(e))
            exit(1)
        print("Finished writing AllNodePageRank.txt file.")

        print("Write data to Top100PageRank.txt file")
        try:
            self.writeTop100("Top100PageRank.txt")
        except BaseException as e:
            print("Exception in writeTop100().")
            print(str(e))
            exit(1)
        print("Finished writing Top100PageRank.txt file.")
        finalend = time.perf_counter()
        T = finalend - start
        print("Total time: "+ str(T)+'s')



    # 读文件
    def readFile(self, fileName):
        file = open(fileName)

        firstLine = file.readline()  # 读第一行
        arr = re.findall(r"\d+", firstLine)  # 正则表达式，取出一行中的数字
        arr0 = int(arr[0])
        arr1 = int(arr[1])
        self.fromNode.add(arr0)  # 第一个数字为fromNode，加入集合
        self.toNode.add(arr1)  # 第二个数字为toNode，加入集合
        self.hash[arr0] = 1
        self.hash[arr1] = 1
        sparseObj = SparseMatrix(arr0)  # 创建对象
        sparseObj.outDegree = 1  # 初始化出度值为1
        sparseObj.outSet.add(arr1)  # 添加出节点编号
        nowNode = arr0  # 当前节点编号
        self.matrix.add(sparseObj)  # 新对象加入稀疏矩阵中

        for line in file:  # 从第二行开始读
            arr = re.findall(r"\d+", line)  # 正则表达式，取出一行中的数字
            arr0 = int(arr[0])
            arr1 = int(arr[1])
            self.fromNode.add(arr0)  # 第一个数字为fromNode，加入集合
            self.toNode.add(arr1)  # 第二个数字为toNode，加入集合
            self.hash[arr0] = 1
            self.hash[arr1] = 1
            if nowNode == arr0:  # 读入的节点已经在稀疏矩阵中
                sparseObj.outDegree += 1  # 节点出度值自增1
                sparseObj.outSet.add(arr1)  # 添加出节点编号
                self.matrix.add(sparseObj)  # 更新稀疏矩阵的对象
            else:  # 读入的节点是新节点
                sparseObj = SparseMatrix(arr0)  # 创建对象
                sparseObj.outDegree = 1  # 初始化出度值为1
                sparseObj.outSet.add(arr1)  # 添加出节点编号
                nowNode = arr0  # 更新当前节点编号
                self.matrix.add(sparseObj)  # 新对象加入稀疏矩阵中
        file.close()
        for i in range(0, 8298):
            if self.hash[i] == 1:
                self.LinkCout += 1
        #print(self.LinkCout)

    # 统计一下所有节点数目及最大节点编号
    def getNum(self):
        self.allNode = self.fromNode | self.toNode  # 全部节点的并集
        self.nodeCount = len(self.allNode)  # 全部节点个数
        self.MAXnum = int(max(self.allNode)) # 最大节点编号
        print("The number of All Nodes is " + str(len(self.allNode)) + ".")
        print("The number of Max Node is " + str(self.MAXnum) + ".")

     # 分块文件预处理
    def BS_genStripe(self):
        if os.path.exists(r"./BlockFiles"):
            for root,dirs,files in os.walk("./BlockFiles"):
                for name in files:
                    os.remove(os.path.join(root,name))
        else:
            os.mkdir(r"./BlockFiles")
        for sparseObj in self.matrix:
            outset=sorted(sparseObj.outSet) # 将出度节点集合升序排列，方便分块
            line = str(sparseObj.nodeNum)+' '+str(sparseObj.outDegree) # 格式为 from|outdegree|tolist
            pre = 0 # 前一个出度节点的块编号
            i = 0
            if len(outset) == 1: # 若出度节点只有一个，不用比较，直接写入对应块
                for outObj in outset:
                    group = int(outObj/self.BlockSize)
                    line=line+' '+str(outObj)+'\n'
                    file=open('./BlockFiles/Matrix'+str(pre)+'.txt','a')
                    file.write(line)
            else:
                for outObj in outset:
                    group = int(outObj/self.BlockSize)
                    i=i+1
                    if group!=pre and i!=1: # 若块的编号发生变化，则开始写入
                        line = line +'\n'
                        file=open('./BlockFiles/Matrix'+str(pre)+'.txt','a')
                        file.write(line)
                        line = str(sparseObj.nodeNum)+' '+str(sparseObj.outDegree)
                    line=line+' '+str(outObj)
                    pre = group
                line = line +'\n'
                file=open('./BlockFiles/Matrix'+str(pre)+'.txt','a')
                file.write(line)
    # 分块初始化R矩阵
    def BS_genRMatrix(self):

        self.RCount = int(max(self.allNode)) + 1  # 最大节点编号
        self.R = [0.0] * self.RCount  # 初始化R矩阵为全0矩阵
        for i in range(0, self.RCount):
            if self.hash[i] == 0:
                continue
            self.R[i] = 1.0 / float(self.LinkCout)

        """
        # check
        rj_sum = 0
        for i in range(0, self.RCount):
            rj_sum += self.R[i]
        print("------------------")
        print("check:     " + str(rj_sum))
        """

        # 将初始化后的R矩阵二进制写入
        file = open("R.txt", 'wb+')
        data = struct.pack(('%df' % len(self.R)), *self.R)
        file.write(data)
        file.close()

        """
        # test txt格式写下初始化矩阵
        temp_R_file_name = "./tempRfile/R0.txt"
        temp_R_file = open(temp_R_file_name, 'w')
        for i in range(0, self.RCount):
            temp_R_file.write(str(self.R[i]) + '\n')
        temp_R_file.close()
        """


     # 迭代计算，更新R矩阵
    def BS_updateR(self):
        
        if os.path.exists(r"./tempRFile"):
            pass
        else:
            os.mkdir(r"./tempRFile")

        self.Round += 1
        groupCount = self.RCount / self.BlockSize + 1
        Rt = [0.0] * self.RCount  # 迭代更新后的R矩阵

        """
        rj_sum = 0
        for i in range(0, self.RCount):
            if self.R[i] != 0.0:
                rj_sum += self.R[i]
        print("------------------")
        print("check:     " + str(rj_sum))
        """

        R_file = open('R.txt', 'rb')  # 二进制模式打开R矩阵

        for i in range(0, int(groupCount)):

            filename = "./BlockFiles/Matrix" + "" + str(i) + ".txt"

            M_file = open(filename)  # 打开分块矩阵M
            #print("成功打开矩阵" + filename)

            for line in M_file:  # 按行读分块文件内的信息

                arr = re.findall(r"\d+", line)  # 正则表达式，取出一行中的数字
                src = int(arr[0])
                deg = int(arr[1])
                # print(arr)
                # 根据src，按照指针从R矩阵读取对应rank值
                size = 4
                R_file.seek(src * size, 0)
                bin = R_file.read(size)
                len_s = len(bin)
                ri = struct.unpack(('%df' % (len_s / 4)), bin)[0]
                # print(ri)
                add = self.BETA * ri / float(deg)

                # 读取dst列表

                for j in range(2, len(arr) ):
                    dst = arr[j]
                    Rt[int(dst)] += add

            M_file.close()

        R_file.close()

        # 补充泄露的能量
        rj_sum = 0
        for i in range(0, self.RCount):
            if self.hash[i] != 0:
                rj_sum += Rt[i]

        Leak = 1 - rj_sum
        Leak = Leak / self.LinkCout

        for i in range(0, self.RCount):
            if self.hash[i] != 0:
                Rt[i] += Leak

        # 一直迭代直到小于阈值
        self.finalError = 0.0  # 更新后的R矩阵和未更新的R矩阵的误差值
        for i in range(0, self.RCount):
            self.finalError = self.finalError + abs(self.R[i] - Rt[i])
        self.R = Rt

        # 二进制模式写回R矩阵
        # 将更新后的Rt矩阵二进制写入
        R_file = open("R.txt", 'wb+')
        data = struct.pack(('%df' % len(self.R)), *self.R)
        R_file.write(data)
        R_file.close()

        # test
        # txt模式写出来
        temp_R_file_name = "./tempRfile/R" + str(self.Round) + ".txt"
        temp_R_file = open(temp_R_file_name, 'w')
        for i in range(0, self.RCount):
            temp_R_file.write(str(self.R[i]) + '\n')
        temp_R_file.close()

        if self.finalError <= self.ERROR:  # 误差值小于预设误差值
            return True
        return False

    # 将全部节点的PageRank值写入文件
    def writeAllNode(self, fileName):
        file = open(fileName, 'w')
        for i in range(0, self.RCount):
            if self.R[i] != 0.0:
                # file.write(str(i + 1) + chr(9) + str(self.R[i]) + '\n')
                file.write(str(i) + chr(9) + str(self.R[i]) + '\n')
        file.close()

    # 重写列表list的排序函数
    def getSecond(self, item):
        return item[1]

    # 将前100的节点写入文件
    def writeTop100(self, fileName):
        tupList = []
        for i in range(0, self.RCount):
            if self.R[i] != 0.0:
                # tup = (i + 1, self.R[i])
                tup = (i, self.R[i])
                tupList.append(tup)
        tupList.sort(reverse=True, key=self.getSecond)  # 降序排序

        file = open(fileName, 'w')
        for i in range(0, 100):
            file.write(str(tupList[i][0]) + chr(9) + str(tupList[i][1]) + '\n')
        file.close()

# main
if __name__ == "__main__":
    DataAnalysis("WikiData.txt")
    print("--------------------------------------")
    print("Block Strip PageRank algorithm completed.")
    print("Please enter any key to continue...")
    input()