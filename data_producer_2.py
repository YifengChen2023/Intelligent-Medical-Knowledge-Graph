import os
import random
import re
from types import MethodType, FunctionType

import jieba


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

class data_producer:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        # 特征词路径
        self.disease_path = os.path.join(cur_dir, 'data_for_trans_diseases/disease.txt')
        self.department_path = os.path.join(cur_dir, 'data_for_trans_diseases/department.txt')
        self.check_path = os.path.join(cur_dir, 'data_for_trans_diseases/check.txt')
        self.drug_path = os.path.join(cur_dir, 'data_for_trans_diseases/drug.txt')
        self.food_path = os.path.join(cur_dir, 'data_for_trans_diseases/food.txt')
        self.producer_path = os.path.join(cur_dir, 'data_for_trans_diseases/producer.txt')
        self.symptom_path = os.path.join(cur_dir, 'data_for_trans_diseases/symptoms.txt')
        self.deny_path = os.path.join(cur_dir, 'data_for_trans_diseases/deny.txt')

        # 加载特征词
        self.disease_wds = [i.strip() for i in open(self.disease_path, encoding='utf-8') if i.strip()]
        self.department_wds = [i.strip() for i in open(self.department_path, encoding='utf-8') if i.strip()]
        self.check_wds = [i.strip() for i in open(self.check_path, encoding='utf-8') if i.strip()]
        self.drug_wds = [i.strip() for i in open(self.drug_path, encoding='utf-8') if i.strip()]
        self.food_wds = [i.strip() for i in open(self.food_path, encoding='utf-8') if i.strip()]
        self.producer_wds = [i.strip() for i in open(self.producer_path, encoding='utf-8') if i.strip()]
        self.symptom_wds = [i.strip() for i in open(self.symptom_path, encoding='utf-8') if i.strip()]
        self.deny_words = [i.strip() for i in open(self.deny_path, encoding='utf-8') if i.strip()]

        # 问句常用词
        self.symptom_qwds = ['什么症状', '什么症候', '有什么表现', '是怎样的', '是什么样的', '哪里不舒服', '哪里难受', '反应如何', '什么不适', '会怎样']
        self.cause_qwds = ['原因', '成因', '为什么', '怎么会传染', '怎样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会', '会导致', '会造成']
        self.disease_qwds = ['可能是什么病', '可能是什么造成的', '怎么回事', '是什么引起的', '可能是什么情况', '可能是啥疾病', '会是什么病']
        self.acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现']
        self.food_qwds = ['饮食什么比较好', '饮用什么比较好', '推荐吃什么食物', '应该食用', '推荐伙食', '应该补充膳食', '应该吃什么食物', '推荐食谱', '推荐菜谱', '推荐食用什么', '宜吃食物', '推荐补品']
        self.food_not_qwds = ['有什么忌口', '不推荐吃什么食物', '避免吃什么食物', '不宜吃什么食物', '不建议吃什么食物', '饮食注意什么', '不要食用什么食物']
        self.drug_qwds = ['应该用什么药', '使用什么药品', '推荐什么药', '口服什么药物', '外敷什么药', '内服什么药物', '开什么药物', '处方', '特效药', '处方药']
        self.prevent_qwds = ['怎样预防', '防范', '抵制', '抵御', '防止', '怎样才能不得', '怎么才能不得', '咋样才能不得', '咋才能不得', '如何才能不得', '注意什么']
        self.lasttime_qwds = ['治疗周期', '多久能好', '多长时间能治好', '多少时间恢复', '持续时间多久', '几天', '几年', '多少天', '多少小时', '几个小时', '多少年']
        self.cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '咋治']
        self.cureprob_qwds = ['多大概率能治好', '多大几率能治好', '治好希望大么', '几率', '几成', '比例', '可能性', '能治', '可治', '可以治', '可以医']
        self.easyget_qwds = ['易感人群', '容易感染', '易发人群', '什么人容易得', '哪些人易得', '被感染', '容易染上', '得上', '容易中招']
        self.check_qwds = ['做什么检查', '应该检查什么', '怎样查出', '做检查', '做什么测试', '怎么确定', '做哪些检测', '有哪些检查项目']
        self.check2disease_qwds = ['检查什么病', '检测出什么疾病', '目的是发现什么病', '预测啥病']
        self.cure_qwds = ['治疗什么', '治什么病', '治疗啥', '医治啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途',]
    def produce(self):

        file = open('training_data_for_trans_diseases.txt', 'w', encoding='utf-8')

        # 由症状找疾病
        for i in range(len(self.symptom_wds)):
            for j in range(len(self.disease_qwds)):
                file.write('__label__symptom_disease , ')
                symptom_disease = seg((self.disease_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.symptom_wds[i] + ' ' + symptom_disease)
                file.write('\n')

        # 由疾病找症状
        for i in range(len(self.disease_wds)):
            for j in range(len(self.symptom_qwds)):
                file.write('__label__disease_symptom , ')
                disease_symptom = seg((self.symptom_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_symptom)
                file.write('\n')

        # 由疾病找原因
        for i in range(len(self.disease_wds)):
            for j in range(len(self.cause_qwds)):
                file.write('__label__disease_cause , ')
                disease_cause = seg((self.cause_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_cause)
                file.write('\n')

        # 由疾病找并发症
        for i in range(len(self.disease_wds)):
            for j in range(len(self.acompany_qwds)):
                file.write('__label__disease_acompany , ')
                disease_acompany = seg((self.acompany_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_acompany)
                file.write('\n')

        # 由疾病找不宜食食物
        for i in range(len(self.disease_wds)):
            for j in range(len(self.food_not_qwds)):
                file.write('__label__disease_not_food , ')
                disease_not_food = seg((self.food_not_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_not_food)
                file.write('\n')

        # 由疾病找宜食食物
        for i in range(len(self.disease_wds)):
            for j in range(len(self.food_qwds)):
                file.write('__label__disease_do_food , ')
                disease_do_food = seg((self.food_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_do_food)
                file.write('\n')

        # 由疾病找药物
        for i in range(len(self.disease_wds)):
            for j in range(len(self.drug_qwds)):
                file.write('__label__disease_drug , ')
                disease_drug = seg((self.drug_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_drug)
                file.write('\n')

        # 由药物找疾病
        for i in range(len(self.drug_wds)):
            for j in range(len(self.cure_qwds)):
                file.write('__label__drug_disease , ')
                drug_disease = seg((self.cure_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.drug_wds[i] + ' ' + drug_disease)
                file.write('\n')

        # 由疾病找检查
        for i in range(len(self.disease_wds)):
            for j in range(len(self.check_qwds)):
                file.write('__label__disease_check , ')
                disease_check = seg((self.check_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_check)
                file.write('\n')

        # 由检查找疾病
        for i in range(len(self.check_wds)):
            for j in range(len(self.check2disease_qwds)):
                file.write('__label__check_disease , ')
                check_disease = seg((self.check2disease_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.check_wds[i] + ' ' + check_disease)
                file.write('\n')

        # 由疾病找预防
        for i in range(len(self.disease_wds)):
            for j in range(len(self.prevent_qwds)):
                file.write('__label__disease_prevent , ')
                disease_prevent = seg((self.prevent_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_prevent)
                file.write('\n')

        # 持续时间
        for i in range(len(self.disease_wds)):
            for j in range(len(self.lasttime_qwds)):
                file.write('__label__disease_lasttime , ')
                disease_lasttime = seg((self.lasttime_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_lasttime)
                file.write('\n')

        # 治疗方式
        for i in range(len(self.disease_wds)):
            for j in range(len(self.cureway_qwds)):
                file.write('__label__disease_cureway , ')
                disease_cureway = seg((self.cureway_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_cureway)
                file.write('\n')

        # 治愈可能性
        for i in range(len(self.disease_wds)):
            for j in range(len(self.cureprob_qwds)):
                file.write('__label__disease_cureprob , ')
                disease_cureprob = seg((self.cureprob_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_cureprob)
                file.write('\n')

        # 易感人群
        for i in range(len(self.disease_wds)):
            for j in range(len(self.easyget_qwds)):
                file.write('__label__disease_easyget , ')
                disease_easyget = seg((self.easyget_qwds[j]).lower().replace('\n', ''), stop_words(),apply=clean_txt)
                file.write(self.disease_wds[i] + ' ' + disease_easyget)
                file.write('\n')

        file.close()
        print('成功输出数据')
if __name__ == '__main__':
    handler = data_producer()
    handler.produce()

