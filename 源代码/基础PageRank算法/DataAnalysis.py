# 测试不同BETA值下的pagerank值变化规律

from BasicPageRank import BasicPageRank
from random import randint

import matplotlib.pyplot as plt

# 选取随机节点进行分析
class NodeAnalysis:
    basic = None  # BasicPageRank对象
    nodeNum = 0  # 随机节点个数
    randNode = []  # 随机节点
    randNodePR = None  # 随机节点在不同β值下的PageRank值趋势矩阵

    maxNode = 4037  # 高入度值节点编号
    minNode = 8274  # 低入度值节点编号
    maxNodePR = []  # 高入度值节点在不同β值下的PageRank值趋势矩阵
    minNodePR = []  # 低入度值节点在不同β值下的PageRank值趋势矩阵

    # 选取n个随机节点进行分析
    def __init__(self, n):
        self.nodeNum = n
        self.basic = BasicPageRank()
        self.basic.updateBETA(0.05)
        self.basic.readFile("WikiData.txt")
        self.basic.handleDeadEnds()
        nodeList = list(self.basic.allNode - self.basic.deadEnds)  # 非死节点集合
        
        # 选取非死节点集合中的随机节点
        i = 0
        while i < self.nodeNum:
            self.randNode.append(self.genRandNum(len(nodeList) - 1))
            i +=1
        print("Generate " + str(self.nodeNum) + " random numbers complete.")
        
        i = 0
        while i < self.nodeNum:
            self.randNode[i] = nodeList[self.randNode[i]]
            i +=1
        self.randNode.sort()

    # 保证随机节点不重复
    # 返回随机节点编号
    def genRandNum(self, MAX):
        num = randint(0, MAX)
        while num in self.randNode:
            num = randint(0, MAX)
        return num
    
    # 迭代计算
    def nodeAnalysis(self):
        beta = 0.05  # β区间[0.05, 0.95]
        self.randNodePR = [[] for i in range(0, self.nodeNum)]  # 初始化

        while beta < 1.00:
        # while beta < 0.15:
            self.basic.updateBETA(beta)  # 修改β值
            self.basic.genRMatrix()  # 初始化R矩阵
            while self.basic.updateR() == False:  # 迭代计算PageRank值
                pass
            print("β = " + str(beta) + " PageRank calculation complete.")

            i = 0
            while i < self.nodeNum:
                self.randNodePR[i].append(self.basic.R[self.randNode[i] - 1])  # 取出随机节点的PageRank值
                i +=1
            self.maxNodePR.append(self.basic.R[4036])
            self.minNodePR.append(self.basic.R[8273])
            beta +=0.05  # β每次递增0.05
            beta = float(int(beta * 100) / 100)
    
    # 画出随机节点在不同β值下，PageRank值的变化曲线
    def drawRandom(self):
        X = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 
             0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]  # 横坐标
        # X = [0.05, 0.1]
        label = []  # 每一条曲线的标签

        # 画图
        plt.figure()
        i = 0
        while i < self.nodeNum:
            label.append("节点:" + str(self.randNode[i]))
            plt.plot(X, self.randNodePR[i], linewidth = 2.0)
            i +=1  
        plt.title("随机节点在不同β值下，PageRank值的变化曲线")
        plt.xlabel("β值")
        plt.ylabel("PageRank值")
        plt.legend(loc = "upper right", labels = label, fontsize = "small")
        plt.show()

    # 画出高低入度值节点在不同β值下，PageRank值的变化曲线
    def drawMaxAndMin(self):
        X = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 
             0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]  # 横坐标
        # X = [0.05, 0.1]
        label = ["高入度值节点4037", "低入度值节点8274"]

        # 画图
        fig = plt.figure()

        ax1 = fig.add_subplot(111)
        ax1.plot(X, self.maxNodePR, '-', label = label[0])
        ax2 = ax1.twinx()
        ax2.plot(X, self.minNodePR, '-r', label = label[1])

        ax1.set_xlabel("β值")
        ax1.set_ylabel(label[0])
        ax2.set_ylabel(label[1])
        fig.legend(loc = 1, bbox_to_anchor = (1,1), bbox_transform = ax1.transAxes)
        plt.show()

if __name__ == "__main__":
    try:
        dataAnalysis = NodeAnalysis(5)  # 随机选取5个点
    except BaseException as e:
        print("Exception in nodeAnalysis().")
        print(str(e))
        exit(1)
    
    try:
        dataAnalysis.nodeAnalysis()  # 开始迭代计算不同β值下PageRank值的变化
    except BaseException as e:
        print("Exception in nodeAnalysis().")
        print(str(e))
        exit(1)
    print("Random node analysis completed.")
    print("-----------------------------------")

    print("Drawing Random...")
    try:
        dataAnalysis.drawRandom()  # 画出随机节点的曲线图
    except BaseException as e:
        print("Exception in draw().")
        print(str(e))
        exit(1)
    
    print("Drawing MaxAndMin...")
    try:
        dataAnalysis.drawMaxAndMin()  # 画出高低入度值节点的曲线图
    except BaseException as e:
        print("Exception in draw().")
        print(str(e))
        exit(1)
    print("-----------------------------------")

    print("Please enter any key to continue...")
    input()