from question_classifier_test import *
from entity_detection_test import *
from answer_search import *

class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifierTest()
        self.detector = EntityDetection()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        # answer = '您好，我是小勇医药智能助理，希望可以帮到您。如果没答上来，那就没答上来。祝您身体棒棒！'
        no_answer = '抱歉，本知识库里没有相关的数据，您可以联系管理员@2037以更新数据！'
        res_classify = self.classifier.main(sent)
        if not res_classify:
            return no_answer
        res_sql = self.detector.entity_dectect(res_classify, sent)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return no_answer
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()
    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('小勇:', answer)
        # 由症状找疾病 # 由疾病找症状 # 由疾病找原因 # 由疾病找并发症 # 由疾病找不宜食食物
        # 由疾病找宜食食物 # 由疾病找药物 # 由药物找疾病 # 由疾病找检查 # 由检查找疾病 # 由疾病找预防 # 持续时间 # 治疗方式 # 治愈可能性 # 易感人群
