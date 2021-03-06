# -*- coding:utf-8 -*-
# Author: Lu Liwen
# Modified Time: 2019-11-22

"""
LabelPropogation(标签传播算法）
可用少量的标注数据得到大量无标注数据的标签值

1.使用iris数据集，用测试样本作为标签值，用训练样本作为无标签值
2.使用自生成的环形数据集

1.半监督学习的数据存放方式(有标签样本放在上面）：
    标签数据————标签label
        +
    无标签数据
        =
    样本数据集和datamat
"""

from numpy import *
from lib import BasicFunction as Basic
from lib import GraphCalculate as Graph


# 自己创建环形数据集，返回带标签数据集，标签集和不带标签数据集(标签集为0，1）
def loadCircleData(num_data):
    center = array([5.0, 5.0])
    radiu_inner = 2
    radiu_outer = 4
    num_inner = num_data // 3
    num_outer = num_data - num_inner

    data = []
    theta = 0.0
    for i in range(num_inner):
        pho = (theta % 360) * math.pi / 180
        tmp = zeros(2, float32)
        tmp[0] = radiu_inner * math.cos(pho) + random.rand(1) + center[0]
        tmp[1] = radiu_inner * math.sin(pho) + random.rand(1) + center[1]
        data.append(tmp)
        theta += 2

    theta = 0.0
    for i in range(num_outer):
        pho = (theta % 360) * math.pi / 180
        tmp = zeros(2, float32)
        tmp[0] = radiu_outer * math.cos(pho) + random.rand(1) + center[0]
        tmp[1] = radiu_outer * math.sin(pho) + random.rand(1) + center[1]
        data.append(tmp)
        theta += 1

    Mat_Label = zeros((2, 2), float32)
    Mat_Label[0] = center + array([-radiu_inner + 0.5, 0])
    Mat_Label[1] = center + array([-radiu_outer + 0.5, 0])
    labels = [0, 1]
    Mat_Unlabel = vstack(data)
    return Mat_Label, labels, Mat_Unlabel


# 根据样本点构造k近邻图
# 输入：样本数据:datamat, 近邻选取数量:k
# 输出: k近邻关系
def constructKmat(datamat, k):
    kTup0 = ('knn', 'dist', 0, k)
    # kTup1 = ('dist',0)
    kmat = Graph.constructDist(datamat, kTup0)
    print('Kmat is done')
    return kmat


# 构建权值矩阵W
# 输入：近邻图:kmat, 权重计算方式:kTup
# 输出：权值矩阵W
def constructWmat(kmat, kTup):
    if kTup[0] == 'rbf':  # 选用rbf内核
        W = exp(-kmat / kTup[1] ** 2)
        print('W is done')
    else:
        raise NameError('还没定义' + kTup[0] + '这种方法')
    return W


# 构建传播概率矩阵
# 输入:权值矩阵：W
# 输出：传播概率矩阵：T
def constructT(W):
    # T = mat(zeros(shape(W)))
    col_sum = sum(W, 0)  # 按行缩减
    T = W / col_sum
    print('T is done')
    return T


# 进入标签传播循环
# 输入：传播概率矩阵T, 有标签数据标签列表:label, 最大循环次数:maxiter
# 输出：无标签数据的标签矩阵:Yuu_label
def propogation(T, label, maxiter):
    m_label = len(label)
    m_unlabel = shape(T)[0] - m_label
    Tul = T[m_label:m_label + m_unlabel, 0:m_label].copy()
    Tuu = T[m_label:m_label + m_unlabel, m_label:m_label + m_unlabel].copy()
    # 找到标签总个数
    Whole_labellist = []
    for label_index in range(m_label):
        if label[label_index] not in Whole_labellist:
            Whole_labellist.append(label[label_index])
        else:
            continue
    label_num = len(Whole_labellist)
    # 构建标签矩阵
    Yll = mat(zeros((m_label, label_num)))
    for i in range(m_label):
        collabel = Whole_labellist.index(label[i])  # 找出标签所在的列记号
        Yll[i, collabel] = 1
    Yuu = mat(ones((m_unlabel, label_num)))
    # 进入循环
    iter = 0
    while iter < maxiter:
        Yuu = Tul * Yll + Tuu * Yuu
        print('现在为第%d轮循环' % iter)
        iter += 1
    Yuu_label_list = argmax(Yuu, 1).T.A[0]  # 以每行的最大值索引作为标签值
    Yuu_label = []
    for j in Yuu_label_list:
        Yuu_label.append(Whole_labellist[j])
    return Yuu_label


# 标签传播算法
# 输入：有标签样本数据:label_mat,无标签样本数据:unlabel_mat,标签集和:label,权值计算方式：kTup,近邻选取数量:k,最大迭代次数:maxiter
# 输出：无标签样本数据：unlabel_list
def labelPropogation(label_mat, unlabel_mat, label, kTup, k, maxiter):
    # 构造数据集
    ml, nl = shape(label_mat)
    mu, nu = shape(unlabel_mat)
    if nl != nu:
        raise SystemError('样本维度不一致')
    else:
        datamat = mat(zeros((ml + mu, nu)))
        datamat[0:ml, :] = label_mat.copy()
        datamat[ml:ml + mu, :] = unlabel_mat.copy()
        kmat = constructKmat(datamat, k)
        Wmat = constructWmat(kmat, kTup)
        T = constructT(Wmat)
        unlabel_list = propogation(T, label, maxiter)
        Basic.plotdata(datamat,label+unlabel_list,[0,1])
        return unlabel_list


if __name__ == '__main__':
    path = './test/iris.txt'
    # training_data, training_label, test_data, test_label = Basic.readData(path)
    Mat_Label, labels, Mat_Unlabel = loadCircleData(800)
    kTup = ('rbf', 5)
    k = 10
    maxiter = 1000
    unlabel_list = labelPropogation(Mat_Label, Mat_Unlabel,labels,kTup,k,maxiter)
    # wrong = 0
    # for w in range(len(unlabel_list)):
    #     if unlabel_list[w] != training_label[w]:
    #         wrong += 1
    #     else:
    #         continue
    # print(wrong)
