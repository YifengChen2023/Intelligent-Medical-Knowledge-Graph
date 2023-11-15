import os
import json
from py2neo import Graph,Node

class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        self.data_path = os.path.join(cur_dir, 'data/newmedical_noenter.json')
        self.g = Graph(
            host="127.0.0.1",
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",
            password="xiuzq")

    '''读取文件'''
    def read_nodes(self):
        # 共6类节点
        drugs = [] # 药品
        foods = [] #　食物
        Check = [] # 检查
        producers = [] #药品大类
        diseases = [] #疾病
        symptoms = []#症状
        disease_infos = []#疾病信息

        # 构建节点实体关系
        relation_noteat = [] # 疾病－忌吃食物关系
        relation_doeat = [] # 疾病－宜吃食物关系
        relation_recommandeat = [] # 疾病－推荐吃食物关系
        relation_commonddrug = [] # 疾病－通用药品关系
        relation_recommanddrug = [] # 疾病－热门药品关系
        relation_check = [] # 疾病－检查关系
        relation_drug_producer = [] # 厂商－药物关系
        relation_symptom = [] #疾病症状关系
        relation_acompany = [] # 疾病并发关系
        relation_category = [] #　疾病与科室之间的关系


        cnt = 0
        for data in open(self.data_path,encoding='utf-8'):
            disease_dict = {}
            cnt += 1
            print(cnt)
            data_json = json.loads(data)
            disease = data_json['name']
            disease_dict['name'] = disease
            diseases.append(disease)
            disease_dict['desc'] = ''
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            if 'symptom' in data_json:
                symptoms += data_json['symptom']
                for symptom in data_json['symptom']:
                    relation_symptom.append([disease, symptom])

            if 'acompany' in data_json:
                for acompany in data_json['acompany']:
                    relation_acompany.append([disease, acompany])

            if 'desc' in data_json:
                disease_dict['desc'] = data_json['desc']

            if 'prevent' in data_json:
                disease_dict['prevent'] = data_json['prevent']

            if 'cause' in data_json:
                disease_dict['cause'] = data_json['cause']

            if 'get_prob' in data_json:
                disease_dict['get_prob'] = data_json['get_prob']

            if 'easy_get' in data_json:
                disease_dict['easy_get'] = data_json['easy_get']

            if 'cure_way' in data_json:
                disease_dict['cure_way'] = data_json['cure_way']

            if  'cure_lasttime' in data_json:
                disease_dict['cure_lasttime'] = data_json['cure_lasttime']

            if 'cured_prob' in data_json:
                disease_dict['cured_prob'] = data_json['cured_prob']

            if 'common_drug' in data_json:
                common_drug = data_json['common_drug']
                for drug in common_drug:
                    relation_commonddrug.append([disease, drug])
                drugs += common_drug

            if 'recommand_drug' in data_json:
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug
                for drug in recommand_drug:
                    relation_recommanddrug.append([disease, drug])

            if 'not_eat' in data_json:
                not_eat = data_json['not_eat']
                for _not in not_eat:
                    relation_noteat.append([disease, _not])

                foods += not_eat
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    relation_doeat.append([disease, _do])

                foods += do_eat
                recommand_eat = data_json['recommand_eat']

                for _recommand in recommand_eat:
                    relation_recommandeat.append([disease, _recommand])
                foods += recommand_eat

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    relation_check.append([disease, _check])
                Check += check
            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]
                relation_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                producers += producer
            disease_infos.append(disease_dict)
        return set(drugs), set(foods), set(Check), set(producers), set(symptoms), set(diseases), disease_infos, \
               relation_check, relation_recommandeat, relation_noteat, relation_doeat, relation_commonddrug, relation_drug_producer, relation_recommanddrug, \
               relation_symptom, relation_acompany, relation_category

    '''建立节点'''
    def create_node(self, label, nodes):
        count = 0
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)
            count += 1
            print(count, len(nodes))
        return

    '''创建知识图谱中心疾病的节点'''
    def create_diseases_nodes(self, disease_infos):
        count = 0
        for disease_dict in disease_infos:
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'] ,cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        ,cure_way=disease_dict['cure_way'] , cured_prob=disease_dict['cured_prob'])
            self.g.create(node)
            count += 1
            print(count)
        return

    '''创建知识图谱实体节点类型'''
    def create_graphnodes(self):
        Drugs, Foods, Checks,  Producers, Symptoms, Diseases, disease_infos,\
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_commonddrug, \
        rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug', Drugs)
        self.create_node('Food', Foods)
        self.create_node('Check', Checks)
        self.create_node('Producer', Producers)
        self.create_node('Symptom', Symptoms)
        return


    '''创建实体关系边'''
    def create_graphrels(self):
        Drugs, Foods, Checks, Producers, Symptoms, Diseases, disease_infos, \
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_commonddrug, rels_drug_producer, \
        rels_recommanddrug,rels_symptom, rels_acompany, rels_category = self.read_nodes()
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')


    '''创建实体关联边'''
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    '''导出数据'''
    def export_data(self):
        Drugs, Foods, Checks, Producers, Symptoms, Diseases, \
        disease_infos, rels_check, rels_recommandeat, rels_noteat, rels_doeat,  rels_commonddrug, \
        rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.read_nodes()
        f_drug = open('.\data_for_trans_diseases\drug.txt', 'w+', encoding='utf-8')
        f_food = open('.\data_for_trans_diseases/food.txt', 'w+', encoding='utf-8')
        f_check = open('.\data_for_trans_diseases\check.txt', 'w+', encoding='utf-8')
        f_producer = open('.\data_for_trans_diseases\producer.txt', 'w+', encoding='utf-8')
        f_symptom = open('.\data_for_trans_diseases\symptoms.txt', 'w+', encoding='utf-8')
        f_disease = open('.\data_for_trans_diseases\disease.txt', 'w+', encoding='utf-8')
        f_drug.write('\n'.join(list(Drugs)))
        f_food.write('\n'.join(list(Foods)))
        f_check.write('\n'.join(list(Checks)))
        f_producer.write('\n'.join(list(Producers)))
        f_symptom.write('\n'.join(list(Symptoms)))
        f_disease.write('\n'.join(list(Diseases)))
        f_drug.close()
        f_food.close()
        f_check.close()
        f_producer.close()
        f_symptom.close()
        f_disease.close()

        return



if __name__ == '__main__':
    handler = MedicalGraph()
    print("step1:::::导入图谱节点")
    handler.create_graphnodes()
    #handler.export_data()
    print("step2::::::导入图谱边")
    handler.create_graphrels()
    
