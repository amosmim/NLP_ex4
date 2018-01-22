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


    def train(self, train_filename, train_annotation_filename):
        with open(train_annotation_filename, 'r') as f:
            answers = defaultdict(dict)
            j=0
            for line in f:
                parts = line.split('\t')
                relation = parts[2].strip()
                if relation not in self.map['label']:
                    self.map['label'][relation] = len(self.map['label']) + 1
                answers[int(parts[0][4:])][(parts[1].strip(), parts[3].strip())] = self.map['label'][relation]
            f.close()
            with open(train_filename, 'r') as fil:
                metrix =[]
                for line in fil:
                    parts = line.split('\t',1)
                    sen = parts[1].strip()
                    sen = sen.replace('-LRB-','(')
                    sen = sen.replace('-RRB-',')')
                    senNum = int(parts[0][4:])
                    #if senNum == 23:
                    #    pass
                    sent = self.nlp(unicode(sen))
                    if len(sent.ents) < 2:
                        continue
                    for ent in sent.ents:
                        ent_text = ent.text.strip()
                        for e in SPACY_MISTAKE_IN_ENTRY:
                            if e in ent_text:
                                ent_text = ent_text.replace(e, '').strip()
                        if ent_text != '':
                            for ent2 in sent.ents:
                                ent2_text = ent2.text.strip()
                                for e in SPACY_MISTAKE_IN_ENTRY:
                                    if e in ent2_text:
                                        ent2_text = ent2_text.replace(e, '').strip()
                                if ent2_text != '' and ent2_text != ent_text:
                                    # create vector with the label
                                    if (ent_text, ent2_text) in answers[senNum]:
                                        vector = [answers[senNum][(ent_text, ent2_text)]]
                                        del answers[senNum][(ent_text, ent2_text)]
                                        j +=1
                                    else:
                                        vector = [0]
                                    vector = vector + self.feature_for_2_entries(ent, ent2, True)
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
                y = metrix[:, :1]
                #print ("y="+str(y))

                X = metrix[:, 1:]
                #print ("X=" + str(X))
                self.model = SVC()
                self.model.fit(X, y)
                joblib.dump(self.model, 'filename.pkl')



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
        vector.append(self._get_feature_num('ent_type', ent.root.ent_type_, isTrain))
        # ent type of Obj2
        vector.append(self._get_feature_num('ent_type', ent2.root.ent_type_, isTrain))
        # POS of Obj1
        vector.append(self._get_feature_num('ent_pos', ent.root.pos_, isTrain))
        # POS of Obj2
        vector.append(self._get_feature_num('ent_pos', ent2.root.pos_, isTrain))





        return vector


fa = TrainFeature()
fa.train('Corpus.TRAIN.txt', 'TRAIN.annotations')
fa2 = TrainFeature.load_from_map()
print fa2.map