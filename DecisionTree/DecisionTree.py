'''
离散特征数据的测是文档是 DecisionTree.txt
离散加连续特征数据的测是文档是 DecisionTree_plus.txt
'''

import numpy as np
log2=np.log2

class Node(object):
    '''
    节点类
    self.dt:存储节点数据
    self.splitruler:节点参数划分规则
    self.sample_num:节点样本数目
    self.father:节点的父节点（对于根节点来说是None）
    self.son:节点的子节点（对于叶子来说是None)
    self.classname:节点被划分到的类
    '''
    def __init__(self,splitruler,dt,father=None,son=None):
        self.dt=dt
        self.splitruler=splitruler
        self.father=father
        self.sample_num=len(dt)
        self.son=son
        self.classname=self.GetClassName()
    def GetClassName(self):
        if self.sample_num==1:return self.dt[0,-1]
        t={}
        for x in self.dt[:,-1]:
            if x in t:
                t[x]+=1
            else:
                t[x]=1
        tp=0
        for x in t:
            if t[x]>tp:
                nx=x
                tp=t[x]
        return nx

class DecisionTree(object):
    '''
    决策树类
    self.continuous:数据中的连续型特征所在的列的标号。第n列的标号为n-1。
    self.dt:决策树的原始数据。必须是NumpyArray类型，且是二维的。首列表示ID，尾列是类。
    self.paraname:NumpyArray每一列的属性名称（包括首列和尾列的名称）
    self.n:决策树的最大深度
    self.tree:决策树的根节点
    self.method:所采用的划分策略。如gini,gain
    '''
    def __init__(self,paraname,dt,n=10,method='gain',continuous={}):
        self.continuous=continuous
        self.method=method
        self.paraname=paraname
        self.dt=dt
        self.n=n-1
        self.tree=Node(splitruler='All',dt=self.dt,father=None)
        print("This DecisionTree is initialized.")
        
    def TreeGenerate(self,curnode,n=0):
        if n>self.n:return curnode
        curylabel=set(curnode.dt[:,-1])
        if len(curylabel)==1:return curnode
        bestxi,cut,bestsplits=self.BestSplit(curnode.dt)
        if bestxi==None:return curnode
        curnode.son=[]
        for subdt in bestsplits:
            splitruler=str(self.paraname[bestxi])+'='+str(subdt[0,bestxi])
            sons=Node(splitruler,subdt)
            sons.father=curnode
            curnode.son.append(self.TreeGenerate(sons,n+1))
        if bestxi in self.continuous:
            curnode.son[0].splitruler=str(self.paraname[bestxi])+'<'+str(cut)
            curnode.son[1].splitruler=str(self.paraname[bestxi])+'>'+str(cut)
        if n==0:print("The Tree is generated.")
        return curnode
        
    def Split(self,dt,xi):
        xname=set(dt[:,xi])
        if len(xname)==1:return [1],[dt]
        c=[]
        cratio=[]
        sample_num=len(dt)
        for x in xname:
            c.append(dt[dt[:,xi]==x])
        for x in c:
            cratio.append(len(x)/sample_num)
        return cratio,c
        
    def Ent(self,dt):
        cname=np.unique(dt[:,-1])
        if len(cname)==1:return 0
        sample_num=len(dt)
        t=0
        for ci in cname:
            pk=np.count_nonzero(dt[:,-1]==ci)/sample_num
            t=t-pk*log2(pk)
        return t
    
    def Gain(self,dt,xi):
        ent=self.Ent(dt)
        cratio,c=self.Split(dt,xi)
        for i in range(len(cratio)):
            ent=ent-cratio[i]*self.Ent(c[i])
        return ent
    
    def Gini(self,dt):
        t={}
        for x in dt:
            if x[-1] in t:
                t[x[-1]]+=1
            else:
                t[x[-1]]=1
        tp=1
        l=len(dt)
        for y in t:
            tp-=(t[y]/l)**2
        return tp
    
    def Gini_index(self,dt,xi):
        giniindex=0
        cratio,c=self.Split(dt,xi)
        for i in range(len(cratio)):
            giniindex+=cratio[i]*self.Gini(c[i])
        return giniindex
    
    def BestSplit(self,dt):
        sample_num=len(dt)
        parameter_num=len(dt[0])-2
        xneeded=[]
        for i in range(1,parameter_num):
            if np.count_nonzero(dt[:,i]==dt[0,i])<sample_num:
                xneeded.append(i)
        if len(xneeded)==0:return None,None,dt
        if (self.method=='Gain')or(self.method=='gain'):
            bestgain=0
            bestxi=0
            for i in xneeded:
                if i in self.continuous:
                    tcut,tsplit,gain=self.Split_continuous(dt,i)
                else:
                    gain=self.Gain(dt,i)
                if gain>bestgain:
                    bestgain=gain
                    bestxi=i
        elif (self.method=='Gini')or(self.method=='gini'):
            bestginiindex=1
            bestxi=1
            for i in xneeded:
                if i in self.continuous:
                    tcut,tsplit,giniindex=self.Split_continuous(dt,i)
                else:
                    giniindex=self.Gini_index(dt,i)
                if giniindex<bestginiindex:
                    bestginiindex=giniindex
                    bestxi=i
        else:
            return print("error:BestSplit")
        if bestxi in self.continuous:
            tcut,bestsplit,t=self.Split_continuous(dt,bestxi)
        else:
            cratio,bestsplit=self.Split(dt,bestxi)
            tcut=None
        return bestxi,tcut,bestsplit
    
    def Split_continuous(self,dt,xi):
        sample_num=len(dt)
        dt=dt[dt[:,xi].argsort()]
        for cuti in range(1,sample_num):
            c1=dt[:cuti,:]
            c2=dt[cuti:,:]
            r1=cuti/sample_num
            r2=1-r1
            if (self.method=='Gain')or(self.method=='gain'):
                tp=self.Ent(dt)-r1*self.Ent(c1)-r2*self.Ent(c2)
                if cuti==1:
                    cut,g=1,tp
                elif tp>g:
                    cut,g=cuti,tp
            elif (self.method=='Gini')or(self.method=='gini'):
                tp=r1*self.Gini(c1)+r2*self.Gini(c2)
                if cuti==1:cut,g=cuti,tp
                elif tp<g:cut,g=cuti,tp
            else:
                return print("error:BestSplit_continuous")
        c=[dt[:cut],dt[cut:]]        
        return (dt[cut,xi]+dt[cut-1,xi])/2,c,g
    
    def showtree(self,tree,t=''):
        if tree.son==None:return print(t+tree.splitruler,'>>',tree.classname)
        print(t+tree.splitruler)
        t=t+'---'
        for x in tree.son:
            self.showtree(x,t)

if __name__=="__main__":
    import pandas as pd
    try:
        
#        ##这里是没有连续型数据的测试
#        dt=pd.read_csv("DecisionTree.txt",encoding='gbk',sep=' ')
#        mytree=DecisionTree(dt.columns,dt.values,method='gini')

        ##这里是连续型数据的测是，其中输入DecisionTree的NumpyArray中的第dt[:,7]和dt[:,8]是连续型数据
        dt=pd.read_csv("DecisionTree_plus.txt",encoding='gbk',sep=' ')
        mytree=DecisionTree(dt.columns,dt.values,method='gain',continuous={7,8})
        


        print("---原始数据---")
        print("===============================================")
        print(dt)
        print("===============================================\n\n")
        print("---决策树---")
        mytree.TreeGenerate(mytree.tree)
        mytree.showtree(mytree.tree)
    finally:
        pass
