"""
maimona5 301236287
moshiat 316131259
"""

import random
from collections import defaultdict

import numpy as np
import spacy
import xgboost as xgb
from sklearn.externals import joblib

from eval import contain as contain

SPACY_MISTAKE_IN_ENTRY = ('province', 'the')
DROP_RATE = 0.2


def get_tok_of(ne, docs):
    ne_text = ne.text
    for i, tok in enumerate(docs):
        if tok.text in ne_text:
            return i
    raise Exception('no token found!')


class TrainFeature:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.map = defaultdict(dict)
        # [label/feature class] [label/feature type in the class] = index

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
            tok_index = get_tok_of(ent, sent)
            entities[text] = {
                'text': text,
                'ent_type': ent.root.ent_type_,
                'dep': ent.root.dep_,
                'pos': ent.root.pos_,
                'iob': ent.root.ent_iob_,
                # 'root_text': ent.root.text,
                # 'root_lemma': ent.root.lemma_,
                # 'prefix2': text[:2],
                # 'prefix3': text[:3],
                # 'suffix2': text[-2:],
                # 'suffix3': text[-3:],
                # 'tok_pos': sent[tok_index].pos_,
                # 'tok_tag': sent[tok_index].tag_,
                'tok_dep': sent[tok_index].dep_,

                # 'tok_n_lefts': sent[tok_index].n_lefts,
                # 'tok_n_rights': sent[tok_index].n_rights,
                # 'tok_pos_before': sent[tok_index - 1].pos_ if tok_index > 0 else '-',
                # 'root_head_text': ent.root.head.text,
                # 'root_head_dep': ent.root.head.dep_,
                # 'root_head_pos': ent.root.head.pos_,
                'before_tok_dep': sent[tok_index - 1].dep_ if tok_index > 0 else 'START',
                'after_tok_dep': sent[tok_index + 1].dep_ if tok_index < len(sent) - 1 else 'END',

                'before_tok_pos': sent[tok_index - 1].pos_ if tok_index > 0 else 'START',
                'after_tok_pos': sent[tok_index + 1].pos_ if tok_index < len(sent) - 1 else 'END',
                'before_tok_tag': sent[tok_index - 1].tag_ if tok_index > 0 else 'START',
                'after_tok_tag': sent[tok_index + 1].tag_ if tok_index < len(sent) - 1 else 'END',

                'before_tok_text': sent[tok_index - 1].text if tok_index > 0 else 'START',
                'after_tok_text': sent[tok_index + 1].text if tok_index < len(sent) - 1 else 'END',
                # 'before_tok_lemma': sent[tok_index - 1].lemma_ if tok_index > 0 else 'START',
                # 'after_tok_lemma': sent[tok_index + 1].lemma_ if tok_index < len(sent) - 1 else 'END',
                # 'titled': str(text.istitle()),
                # 'tok_titled': str(sent[tok_index].text.istitle()),
                # 'is_upper': str(True if '.' not in text and text.isupper() else False),
            }
        return entities

    def feature_for_2_entries(self, ent, ent2, isTrain):
        vector = list()
        vector.append(self._get_feature_num('ent_type', ent['ent_type'], isTrain))
        vector.append(self._get_feature_num('ent_type', ent2['ent_type'], isTrain))

        vector.append(self._get_feature_num('ent_dep', ent2['dep'], isTrain))
        vector.append(self._get_feature_num('ent_iob', ent['iob'], isTrain))
        vector.append(self._get_feature_num('ent_pos', ent['pos'], isTrain))
        vector.append(self._get_feature_num('tok_dep', ent['tok_dep'], isTrain))

        vector.append(self._get_feature_num('before_tok_dep', ent['before_tok_dep'], isTrain))
        vector.append(self._get_feature_num('before_tok_dep', ent2['before_tok_dep'], isTrain))
        vector.append(self._get_feature_num('after_tok_dep', ent2['after_tok_dep'], isTrain))

        vector.append(self._get_feature_num('before_tok_text', ent['before_tok_text'], isTrain))
        vector.append(self._get_feature_num('before_tok_text', ent2['before_tok_text'], isTrain))
        vector.append(self._get_feature_num('after_tok_text', ent['after_tok_text'], isTrain))
        vector.append(self._get_feature_num('after_tok_text', ent2['after_tok_text'], isTrain))

        # start duplicate
        vector.append(self._get_feature_num('before_tok_dep', ent['before_tok_dep'], isTrain))
        vector.append(self._get_feature_num('before_tok_dep', ent2['before_tok_dep'], isTrain))
        vector.append(self._get_feature_num('after_tok_dep', ent2['after_tok_dep'], isTrain))

        vector.append(self._get_feature_num('before_tok_text', ent['before_tok_text'], isTrain))
        vector.append(self._get_feature_num('before_tok_text', ent2['before_tok_text'], isTrain))
        vector.append(self._get_feature_num('after_tok_text', ent['after_tok_text'], isTrain))
        vector.append(self._get_feature_num('after_tok_text', ent2['after_tok_text'], isTrain))
        # end duplicate

        # vector.append(self._get_feature_num('tok_tag', ent['tok_tag'], isTrain))

        return vector

    def train(self, train_filename, train_annotation_filename):
        with open(train_annotation_filename, 'r') as f:
            answers = defaultdict(dict)
            # [sentence number] [tuple (obj1, obj2)] = label of relation
            j = 0
            for line in f:
                parts = line.split('\t')
                relation = parts[2].strip()
                if relation not in self.map['label']:
                    self.map['label'][relation] = len(self.map['label']) + 1
                answers[int(parts[0][4:])][(parts[1].strip().rstrip('.'), parts[3].strip().rstrip('.'))] = \
                    self.map['label'][relation]
            f.close()
            with open(train_filename, 'r') as fil:
                metrix = []
                for line in fil:
                    parts = line.split('\t', 1)
                    senNum = int(parts[0][4:])
                    ents = self.get_all_entities(parts[1])

                    if len(ents) < 2:
                        continue
                    for ent in ents.keys():
                        ent_text = ents[ent]['text']

                        if ent_text != '':
                            for ent2 in ents.keys():
                                ent2_text = ents[ent2]['text']

                                if ent2_text != '' and ent2_text != ent_text:
                                    # create vector with the label
                                    key = contain((ent_text, ent2_text), answers[senNum].keys())
                                    if key != None:
                                        # if (ent_text, ent2_text) in answers[senNum]:
                                        vector = [answers[senNum][key]]
                                        #    vector = [answers[senNum][(ent_text, ent2_text)]]
                                        #   del answers[senNum][(ent_text, ent2_text)]
                                        del answers[senNum][key]
                                        j += 1
                                        # print (str(key) + '=='+ str((ent_text, ent2_text)))
                                    elif random.random() < DROP_RATE:
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
                        i += 1
                        print (str(linenum) + " : " + str(objs))
                print ('############# ' + str(i) + " tagged: " + str(j))
                fil.close()
                metrix = np.array(metrix)
                print (metrix.shape)
                y = metrix[:, :1].T[0]

                X = metrix[:, 1:]
                self.model = xgb.XGBClassifier(
                    learning_rate=0.7, n_estimators=7, objective='multi:softprob',
                    subsample=0.8, colsample_bytree=0.3)
                self.model.fit(X, y, eval_metric='mlogloss')
                joblib.dump(self.model, 'svmModel.pkl')

    def predict_line(self, line):
        result = []
        ents = self.get_all_entities(line)
        if len(ents) < 2:
            return result
        for ent in ents.keys():
            ent_text = ents[ent]['text']
            if ent_text != '':
                for ent2 in ents.keys():
                    ent2_text = ents[ent2]['text']
                    if ent2_text != '' and ent2_text != ent_text:
                        vec = self.feature_for_2_entries(ents[ent], ents[ent2], False)
                        if self.predict(vec):
                            result.append((ent_text, ent2_text))
        return result

    def predict(self, feature_vec):
        predict = self.model.predict([feature_vec])
        return predict[0] == self.map['label']['Live_In']

    def save_map(self):
        with open('feature_map.txt', 'w') as out:
            for feature_class in self.map.keys():
                for feature_type in self.map[feature_class].keys():
                    out.write(
                        "{0},{1},{2}\n".format(feature_class, feature_type, self.map[feature_class][feature_type]))

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

    def _get_feature_num(self, feature_class, feature_type, isTrain):
        if feature_type in self.map[feature_class]:
            return self.map[feature_class][feature_type]
        elif isTrain:
            self.map[feature_class][feature_type] = len(self.map[feature_class]) + 1
            return self.map[feature_class][feature_type]
        else:
            return 0
