# 基础PageRank算法
# 采用稀疏矩阵存储节点，节省空间
# 列表list遍历和查找效率过低，因此使用集合set

# 数据集请命名为WikiData.txt
# 数据集请放置于与该文件同一目录下
# 全部节点的PageRank值会输出在AllNodePageRank.txt文件中
# PageRank值前100会输出在Top100PageRank.txt文件中
# AllNodePageRank.txt和Top100PageRank.txt文件均与该文件同一目录中

import re
import time

# 稀疏矩阵结构
class SparseMatrix:
    nodeNum = 0  # 节点编号
    outDegree = 0  # 节点出度
    outSet = None  # 所有出度节点编号

    # 类构造函数
    def __init__(self, num):
        self.nodeNum = num
        self.outDegree = 1  # 初始化出度值为1
        self.outSet = set()

# 基础PageRank算法
class BasicPageRank:
    fromNode = set()  # from节点集合
    toNode = set()  # to节点集合
    allNode = None  # 全部节点集合
    deadEnds = None  # 死节点集合
    
    nodeCount = 0 # 全部节点个数
    RCount = 0  # R矩阵的大小，应等于最大节点编号

    matrix = set()  # 稀疏矩阵，每个都是SparseMatrix对象
    R = []  # PageRank矩阵

    BETA = 0.85  # β值
    randomWalk = 0.0  # 随机游走系数
    ERROR = 1E-10  # 误差阈值
    finalError = 0.0  # 最终误差值

    # 构造函数
    # 修改β值
    def updateBETA(self, beta):
        self.BETA = beta
        
    # 读文件
    def readFile(self, fileName):
        file = open(fileName)

        firstLine = file.readline()  # 读第一行
        arr = re.findall(r"\d+", firstLine)  # 正则表达式，取出一行中的数字
        arr0 = int(arr[0])
        arr1 = int(arr[1])
        self.fromNode.add(arr0)  # 第一个数字为fromNode，加入集合
        self.toNode.add(arr1)  # 第二个数字为toNode，加入集合
        sparseObj = SparseMatrix(arr0)  # 创建对象
        sparseObj.outSet.add(arr1)  # 添加出节点编号
        nowNode = arr0  # 当前节点编号
        self.matrix.add(sparseObj)  # 新对象加入稀疏矩阵中

        for line in file:  # 从第二行开始读
            arr = re.findall(r"\d+", line)  # 正则表达式，取出一行中的数字
            arr0 = int(arr[0])
            arr1 = int(arr[1])
            self.fromNode.add(arr0)  # 第一个数字为fromNode，加入集合
            self.toNode.add(arr1)  # 第二个数字为toNode，加入集合
            if nowNode == arr0:  # 读入的节点已经在稀疏矩阵中
                sparseObj.outDegree +=1  # 节点出度值自增1
                sparseObj.outSet.add(arr1)  # 添加出节点编号
                self.matrix.add(sparseObj)  # 更新稀疏矩阵的对象
            else:  # 读入的节点是新节点
                sparseObj = SparseMatrix(arr0)  # 创建对象
                sparseObj.outSet.add(arr1)  # 添加出节点编号
                nowNode = arr0  # 更新当前节点编号
                self.matrix.add(sparseObj)  # 新对象加入稀疏矩阵中
        file.close()

    # 处理死节点Dead Ends
    # 将死节点连接至全部节点，包括自身
    def handleDeadEnds(self):
        self.allNode = self.fromNode | self.toNode  # 全部节点的并集
        self.nodeCount = len(self.allNode)  # 全部节点个数
        self.deadEnds = self.toNode - self.fromNode  # 死节点集合为两个集合的差集
        for node in self.deadEnds:
            sparseObj = SparseMatrix(node)  # 创建对象
            sparseObj.outDegree = self.nodeCount  # 死节点出度个数为全部节点个数
            sparseObj.outSet = self.allNode  # 出节点为全部节点
            self.matrix.add(sparseObj)

    # 初始化R矩阵
    def genRMatrix(self):
        self.RCount = int(max(self.allNode))  # 最大节点编号
        self.randomWalk = (1 - self.BETA) / self.nodeCount  # 随机游走因子
        self.R = [0.0] * self.RCount  # 初始化R矩阵为全0矩阵
        for nodeNum in self.allNode:
            self.R[nodeNum - 1] = 1 / self.nodeCount  # 非孤立节点的值应为1/nodeCount

    # 迭代计算，更新R矩阵
    def updateR(self):
        tempR = [0.0] * self.RCount  # 迭代更新后的R矩阵  

        # 根据公式计算PageRank值
        # 具体原理可参考课件或实验报告
        for nodeObj in self.matrix:
            sigema = self.R[nodeObj.nodeNum - 1] / nodeObj.outDegree
            for outNum in nodeObj.outSet:
                tempR[outNum - 1] +=sigema
        i = 0
        while i < self.RCount:
            if tempR[i] != 0.0:
                tempR[i] = self.randomWalk + self.BETA * tempR[i]
            i +=1

        i = 0
        self.finalError = 0.0  # 更新后的R矩阵和未更新的R矩阵的误差值
        while i < self.RCount:
            if self.R[i] != 0.0:
                self.finalError = self.finalError + abs(self.R[i] - tempR[i])
            i +=1

        self.R = tempR
        if self.finalError <= self.ERROR:  # 误差值小于预设误差值
            return True
        return False

    # 将全部节点的PageRank值写入文件
    def writeAllNode(self, fileName):
        i = 0
        file = open(fileName, 'w')
        while i < self.RCount:
            if self.R[i] != 0.0:
                file.write(str(i + 1) + chr(9) + str(self.R[i]) + '\n')
            i +=1
        file.close()

    # 重写列表list的排序函数
    def getSecond(self, item):
        return item[1]

    # 将前100的节点写入文件
    def writeTop100(self, fileName):
        i = 0
        tupList = []
        while i < self.RCount:
            if self.R[i] != 0.0:
                tup = (i + 1, self.R[i])
                tupList.append(tup)
            i +=1
        tupList.sort(reverse = True, key = self.getSecond)  # 降序排序
        print("Maximum PageRank node is " + str(tupList[0][0]) + ".")
        print("Minimum PageRank node is " + str(tupList[self.nodeCount - 1][0]) +".")

        i = 0
        file = open(fileName, 'w')
        while i < 100:
            file.write(str(tupList[i][0]) + chr(9) + str(tupList[i][1]) + '\n')
            i +=1
        file.close()

# main
if __name__ == "__main__":
    Start = time.perf_counter()

    basic = BasicPageRank()
    fileName = "WikiData.txt"

    try:
        start = time.perf_counter()
        basic.readFile(fileName)
        end = time.perf_counter()
        print("readFile() running time: %s Seconds." % (end - start))
    except BaseException as e:
        print("Exception in readFile().")
        print(str(e))
        exit(1)
    print("Read " + fileName + " complete.")
    print("------------------------------------------------------------------")

    try:
        start = time.perf_counter()
        basic.handleDeadEnds()    
        end = time.perf_counter()
        print("handleDeadEnds() running time: %s Seconds." % (end - start)) 
    except BaseException as e:
        print("Exception in handleDeadEnds().")
        print(str(e))
        exit(1)
    print("Handling dead ends completed.")
    print("The number of Dead Ends is " + str(len(basic.deadEnds)) + ".")
    print("------------------------------------------------------------------")
    
    try:
        start = time.perf_counter()
        basic.genRMatrix()  
        end = time.perf_counter()
        print("genRMatrix() running time: %s Seconds." % (end - start))
    except BaseException as e:
        print("Exception in genRMatrix().")
        print(str(e))
        exit(1)
    print("Initialize R matrix complete.")
    print("The number of all nodes is " + str(basic.nodeCount) + ".")
    print("------------------------------------------------------------------")

    print("Start calculation...")
    try:
        start = time.perf_counter()
        while basic.updateR() == False:
            pass
        end = time.perf_counter()
        print("updateR() running time: %s Seconds." % (end - start))
    except BaseException as e:
        print("Exception in updateR().")
        print(str(e))
        exit(1)
    print("Pangerank calculation completed.")
    print("The error value of pangerank is " + str(basic.finalError) + ".")
    print("------------------------------------------------------------------")   
    
    print("Write data to AllNodePageRank.txt file...")
    try:
        start = time.perf_counter()
        basic.writeAllNode("AllNodePageRank.txt")
        end = time.perf_counter()
        print("writeAllNode() running time: %s Seconds." % (end - start))
    except BaseException as e:
        print("Exception in writeAllNode().")
        print(str(e))
        exit(1)
    print("Finished writing AllNodePageRank.txt file.")
    print("------------------------------------------------------------------")

    print("Write data to Top100PageRank.txt file")
    try:
        start = time.perf_counter()
        basic.writeTop100("Top100PageRank.txt")
        end = time.perf_counter()
        print("writeTop100() running time: %s Seconds." % (end - start))
    except BaseException as e:
        print("Exception in writeTop100().")
        print(str(e))
        exit(1)   
    print("Finished writing Top100PageRank.txt file.")
    print("------------------------------------------------------------------")

    End = time.perf_counter()
    print("Basic PageRank algorithm running time: %s Seconds." % (End - Start))
    print("Basic PageRank algorithm completed.")
    print("------------------------------------------------------------------")
    print("Please enter any key to continue...")
    input()