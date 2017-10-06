import math
from operator import itemgetter
import sys
import random


def read_behavior(file):
    data = []
    for line in file:
        line = line.strip('\n')
        linelist = line.split('\t')
        data.append([linelist[0], linelist[1]])

    return data


def read_user(file):
    result = []
    for line in file:
        line = line.strip('\n')
        linelist = line.split('\t')
        result.append(linelist[0])

    return result


# item_popular = {}
# item_count = 0




def UserSimilarity(train):
    ''' 计算用户相似度
        @param train 训练数据集Dict
        @return W    记录用户相似度的二维矩阵
    '''
    # 建立物品到用户之间的倒查表，降低计算用户相似度的时间复杂性
    item_users = dict()
    C = dict()
    N = dict()
    count = 0
    for u, items in train.items():
        for i in items:
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)

            # 计算用户之间共有的item的数目
    print('len: ', len(item_users.items()))
    for i, users in item_users.items():
        print('count: ', count)
        count += 1
        for u in users:
            if u not in N:
                N[u] = 0
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                if u not in C:
                    C[u] = {}
                if v not in C[u]:
                    C[u][v] = 0
                # 对热门物品进行了惩罚，采用这种方法被称做UserCF-IIF
                C[u][v] += 1

    W = dict()
    for u, related_users in C.items():
        if u not in W:
            W[u] = dict()
        for v, cuv in related_users.items():
            # 利用余弦相似度计算用户之间的相似度
            W[u][v] = cuv / math.sqrt(N[u] * N[v])

    with open('data/temp.txt', 'w') as f:
        for u in W.keys():
            for v in W[u].keys():
                f.write(u)
                f.write('\t')
                f.write(v)
                f.write('\t')
                f.write(W[u][v])
                f.write('\n')

    return W


def GetRecommendation(user, train, W, N, K):
    ''' 获取推荐结果
        @param user  输入的用户
        @param train 训练数据集Dict
        @param W     记录用户相似度的二维矩阵
        @param N     推荐结果的数目
        @param K     选取近邻的数目
    '''
    rank = dict()
    interacted_items = train[user]
    # 选取K个近邻计算得分
    for v, wuv in sorted(W[user].items(), key=itemgetter(1),
                         reverse=True)[0:K]:
        for i in train[v]:
            if i in interacted_items:
                continue
            rank.setdefault(i, 0)
            rank[i] += wuv

    # 取得分最高的N个item作为推荐结果
    rank = sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]

    return rank


def result_generate(train, user, W, N, K):
    recommned_items = set()
    rank = GetRecommendation(user, train, W, N, K)
    for item, pui in rank:
        recommned_items.add(item)
    return recommned_items


def Recall(train, test, W, N, K):
    ''' 计算推荐结果的召回率
        @param train 训练数据集Dict
        @param test  测试数据集Dict
        @param W     记录用户相似度的二维矩阵
        @param N     推荐结果的数目
        @param K     选取近邻的数目
    '''
    hit = 0
    all = 0
    for user in train.keys():
        if user in test:
            tu = test[user]
            rank = GetRecommendation(user, train, W, N, K)
            for item, pui in rank:
                if item in tu:
                    hit += 1
            all += len(tu)
    # print(hit)
    # print(all)
    return hit / (all * 1.0)


def Precision(train, test, W, N, K):
    ''' 计算推荐结果的准确率
        @param train 训练数据集Dict
        @param test  测试数据集Dict
        @param W     记录用户相似度的二维矩阵
        @param N     推荐结果的数目
        @param K     选取近邻的数目
    '''
    hit = 0
    all = 0
    for user in train.keys():
        if user in test:
            tu = test[user]
            rank = GetRecommendation(user, train, W, N, K)
            for item, pui in rank:
                if item in tu:
                    hit += 1
            all += N
    # print(hit)
    # print(all)
    return hit / (all * 1.0)


def get_data(data):
    train = dict()
    for user, item in data:
        if user in train:
            train[user].append(item)
        else:
            train[user] = []
    return train


if __name__ == '__main__':
    # M = 8
    key = 1
    # seed = 1
    N = 10
    K = 80
    W = dict()
    rank = dict()

    print('preparing data...')
    file = open('data/behavior_info.txt')
    data = read_behavior(file)
    # print('len data: ',len(data))

    print('getting data...')
    train = get_data(data)

    # result_temp = random_result(train)
    # print(train)
    #
    print('getting similarity..')
    W = UserSimilarity(train)
    # # recall = Recall(train, test, W, N, K)
    # # precision = Precision(train, test, W, N, K)
    # # popularity = Popularity(train, test, W, N, K)
    # # coverage = Coverage(train, test, W, N, K)
    # # print('recall: ', recall)
    # # print('precision: ', precision)
    # # print('popularity: ', popularity)
    # # print('coverage: ', coverage)
    #
    user_file = open('data/user_info.txt')
    users = read_user(user_file)
    print(len(users))
    result = []
    for user in users:
        recommends = result_generate(train, user, W, N, K)
        # if train.get(user, None) is not None:
        #     if len(train[user]) > 40:
        #         train[user] = train[user][0::38]
        #     recommends = train[user]
        #
        # else:
        #     temp = []
        #     num = int(random.random() * 28 + 4)
        #     for i in range(1, num):
        #         temp.append(str(random.random() * 485140 + 4))
        #     recommends = temp
        result.append([user, recommends])
        #
    with open('data/result.txt', 'w') as f:
        for value in result:
            recommend = value[1]
            for i in recommend:
                f.write(value[0])
                f.write('\t')
                f.write(i)
                f.write('\n')
