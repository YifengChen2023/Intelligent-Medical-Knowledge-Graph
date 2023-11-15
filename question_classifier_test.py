import re
from types import MethodType, FunctionType

import jieba
import pandas
import fasttext.FastText as fasttext
import numpy as np
import os

def clean_txt(raw):
    fil = re.compile(r"[^0-9a-zA-Z\u4e00-\u9fa5]+")
    return fil.sub(' ', raw)


def seg(sentence, sw, apply=None):
    if isinstance(apply, FunctionType) or isinstance(apply, MethodType):
        sentence = apply(sentence)
    return ' '.join([i for i in jieba.cut(sentence) if i.strip() and i not in sw])


def stop_words():
    with open('./data/stopwords.txt', 'r', encoding='utf-8') as swf:
        return [line.strip() for line in swf]

class QuestionClassifierTest:
    def __init__(self):
        train_file = './training_data_for_trans_diseases.txt'
        dim = 200
        lr = 0.5
        epoch = 1000
        model = f'./data_dim{str(dim)}_lr0{str(lr)}_iter{str(epoch)}.model'

        self.classifier = self.train_model(ipt=train_file,
                                      opt=model,
                                      model=model,
                                      dim=dim, epoch=epoch, lr=0.5
                                      )
        print('模型已训练完成！')
        jieba.load_userdict(r"dict_for_trans_diseases.txt")
    def train_model(self, ipt=None, opt=None, model='', dim=100, epoch=5, lr=0.1, loss='softmax'):
        np.set_printoptions(suppress=True)
        if os.path.isfile(model):
            classifier = fasttext.load_model(model)
        else:
            classifier = fasttext.train_supervised(ipt, label='__label__', dim=dim, epoch=epoch,
                                                   lr=lr, wordNgrams=2, loss=loss)
            """
              训练一个监督模型, 返回一个模型对象
    
              @param input:           训练数据文件路径
              @param lr:              学习率
              @param dim:             向量维度
              @param ws:              cbow模型时使用
              @param epoch:           次数
              @param minCount:        词频阈值, 小于该值在初始化时会过滤掉
              @param minCountLabel:   类别阈值，类别小于该值初始化时会过滤掉
              @param minn:            构造subword时最小char个数
              @param maxn:            构造subword时最大char个数
              @param neg:             负采样
              @param wordNgrams:      n-gram个数
              @param loss:            损失函数类型, softmax, ns: 负采样, hs: 分层softmax
              @param bucket:          词扩充大小, [A, B]: A语料中包含的词向量, B不在语料中的词向量
              @param thread:          线程个数, 每个线程处理输入数据的一段, 0号线程负责loss输出
              @param lrUpdateRate:    学习率更新
              @param t:               负采样阈值
              @param label:           类别前缀
              @param verbose:         ??
              @param pretrainedVectors: 预训练的词向量文件路径, 如果word出现在文件夹中初始化不再随机
              @return model object
            """
            classifier.save_model(opt)
        return classifier

    def main(self, sent):

        sent = seg(sent, stop_words(), apply=clean_txt)
        result = self.classifier.predict(sent)
        result = str(result[0][0])[9:]

        return result

if __name__ == '__main__':
    classifier = QuestionClassifierTest()
    print(classifier.main('交叉配血试验能检查什么病'))
