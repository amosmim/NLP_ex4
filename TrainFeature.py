import random
from collections import defaultdict
import spacy
import numpy as np
from sklearn.svm import SVC
from sklearn.externals import joblib
SPACY_MISTAKE_IN_ENTRY =('province', 'the')


class TrainFeature:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.map = defaultdict(dict)
        # [label/feature class] [label/feature type in the class] = index

        # [sentence number] [tuple (obj1, obj2)] = label of relation
    def get_all_entities(self, line):
        sen = line.strip()
        sen = sen.replace('-LRB-', '(')
        sen = sen.replace('-RRB-', ')')
        sent = self.nlp(unicode(sen))
        entities = {}
        for ent in sent.ents:
            text = ent.text.strip().rstrip('.')
            text = text.encode('ascii', 'ignore')
            for e in SPACY_MISTAKE_IN_ENTRY:
                if e in text:
                    text = text.replace(e, '').strip()
            entities[text] = {
                'text': text,
                'ent_type': ent.root.ent_type_,
                'dep': ent.root.dep_,
                'pos': ent.root.pos_
            }
        '''
        for chunk in sent.noun_chunks:
            text = chunk.text.strip().rstrip('.')
            text = text.encode('ascii', 'ignore')
            for e in SPACY_MISTAKE_IN_ENTRY:
                if e in text:
                    text = text.replace(e, '').strip()
            entities[text] = {
                'text': text,
                'ent_type': u'UNNOWN',
                'dep': chunk.root.dep_,
                'pos': chunk.root.pos_
            }'''

        return entities


    def train(self, train_filename, train_annotation_filename):
        with open(train_annotation_filename, 'r') as f:
            answers = defaultdict(dict)
            j=0
            for line in f:
                parts = line.split('\t')
                relation = parts[2].strip()
                if relation not in self.map['label']:
                    self.map['label'][relation] = len(self.map['label']) + 1
                answers[int(parts[0][4:])][(parts[1].strip().rstrip('.'), parts[3].strip().rstrip('.'))] = self.map['label'][relation]
            f.close()
            with open(train_filename, 'r') as fil:
                metrix =[]
                for line in fil:
                    parts = line.split('\t',1)
                    senNum = int(parts[0][4:])
                    ents = self.get_all_entities(parts[1])
                    if senNum == 138:
                        pass
                    if len(ents) < 2:
                        continue
                    for ent in ents.keys():
                        ent_text = ents[ent]['text']

                        if ent_text != '':
                            for ent2 in ents.keys():
                                ent2_text = ents[ent2]['text']

                                if ent2_text != '' and ent2_text != ent_text:
                                    # create vector with the label
                                    if (ent_text, ent2_text) in answers[senNum]:
                                        vector = [answers[senNum][(ent_text, ent2_text)]]
                                        del answers[senNum][(ent_text, ent2_text)]
                                        j += 1
                                    elif random.random() < 0.15 :
                                        vector = [0]
                                    else:
                                        continue
                                    vector = vector + self.feature_for_2_entries(ents[ent], ents[ent2], True)
                                    metrix.append(vector)
                    self.save_map()

                i = 0

                print ("not taged :\n")
                for linenum in answers.keys():
                    for objs in answers[linenum]:
                        i +=1
                        print (str(linenum) + " : " + str(objs))
                print ('############# ' + str(i) + " taged: " + str(j))
                fil.close()
                metrix = np.array(metrix)
                print (metrix.shape)
                y = metrix[:, :1].T[0]

                X = metrix[:, 1:]
                self.model = SVC()
                self.model.fit(X, y)
                joblib.dump(self.model, 'svmModel.pkl')

    def predict_line(self, line):
        result = []
        ents = self.get_all_entities(line)
        if len(ents) < 2:
            return result
        for ent in ents.keys():
            ent_text = ents[ent]['text']
            #for e in SPACY_MISTAKE_IN_ENTRY:
            #    if e in ent_text:
            #        ent_text = ent_text.replace(e, '').strip()
            if ent_text != '':
                for ent2 in ents.keys():
                    ent2_text = ents[ent2]['text']
                   ## for e in SPACY_MISTAKE_IN_ENTRY:
                     #   if e in ent2_text:
                      #      ent2_text = ent2_text.replace(e, '').strip()
                    if ent2_text != '' and ent2_text != ent_text:
                        vec = self.feature_for_2_entries(ents[ent], ents[ent2], False)
                        if self.predict(vec):
                            result.append((ent_text,ent2_text))
        return result

    def predict(self, feature_vec):
        predict = self.model.predict([feature_vec])
        return predict[0] == self.map['label']['Live_In']

    def save_map(self):
        with open('feature_map.txt','w') as out:
            for feature_class in self.map.keys():
                for feature_type in self.map[feature_class].keys():
                    out.write("{0},{1},{2}\n".format(feature_class,feature_type,self.map[feature_class][feature_type]))

    @classmethod
    def load_from_map(cls):
        c = cls()
        c.nlp = spacy.load('en_core_web_sm')
        c.map = defaultdict(dict)
        c.model = joblib.load('svmModel.pkl')
        with open('feature_map.txt', 'r') as f:
            for line in f:
                parts = line.split(',')
                c.map[parts[0]][parts[1]] = int(parts[2])
        return c

    def _get_feature_num(self, feature_class, feature_type ,isTrain):
        if feature_type in self.map[feature_class]:
            return self.map[feature_class][feature_type]
        elif isTrain:
            self.map[feature_class][feature_type] = len(self.map[feature_class]) + 1
            return self.map[feature_class][feature_type]
        else:
            return 0

    def feature_for_2_entries(self,ent, ent2, isTrain):
        vector = list()
        # ent type of Obj1
        vector.append(self._get_feature_num('ent_type', ent['ent_type'], isTrain))
        # ent type of Obj2
        vector.append(self._get_feature_num('ent_type', ent2['ent_type'], isTrain))
        # POS of Obj1
        vector.append(self._get_feature_num('ent_pos', ent['pos'], isTrain))
        # POS of Obj2
        vector.append(self._get_feature_num('ent_pos', ent2['pos'], isTrain))

        vector.append(self._get_feature_num('ent_dep', ent2['dep'], isTrain))

        vector.append(self._get_feature_num('ent_dep', ent2['dep'], isTrain))





        return vector


#fa = TrainFeature()
#fa.train('Corpus.TRAIN.txt', 'TRAIN.annotations')
#fa2 = TrainFeature.load_from_map()
#print fa2.map