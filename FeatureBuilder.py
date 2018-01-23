import spacy
import random
from eval import annon_to_dict
FEATURES_LABEL = ['obj1 label','obj2 label',  'obj1 root POS', 'obj2 root POS', 'heads abs diff', 'head diff direction','with (AP)']#,'obj1 norm vec', 'obj2 norm vec']
ALL_LABELS = ['index'] + FEATURES_LABEL + ['Is live in']

obj1_options = [u'PERSON']
obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']

#
# features values
#
OBJ1_TARGET = (2,[u'PERSON'])
OBJ1_EXCEPT = (1,[u'LOC',u'PRODUCT',u'GPE',u'ORG'])

OBJ2_TARGET = (2,[u'GPE'])
OBJ2_EXCEPT = (1,[u'NORP',u'PERSON',u'ORG', u'LOC'])

OBJ1_POS = (1, [u'PROPN'])
OBJ2_POS = (1.0, [u'PROPN'])
OBJ2_POS_EXCEPT = (0.5, [u'ADJ'])

contain_AP = u'-LRB- AP -RRB-'

###


class FeatureBuilder:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def feature_line(self, full_line):
        index, line = full_line.split('\t',1)
        index = int(index[4:])

        sent = self.nlp(unicode(line))
        lines_list = []
        if len(sent.ents) < 2:
            return lines_list
        for ent in sent.ents:
            if ent.text.strip() != '' and ent.root.ent_type_ in obj1_options:
                for ent2 in sent.ents:
                    if (ent.text != ent2.text) and ent2.text.strip() != '' \
                            and ent2.root.ent_type_ in obj2_options:
                        ## features start !!!!
                        new_line = str(index) + ','
                        if ent.label_ in OBJ1_TARGET[1]:
                            obj1_label = OBJ1_TARGET[0]
                        elif ent.label_ in OBJ1_EXCEPT[1]:
                            obj1_label = OBJ1_EXCEPT[0]
                        else:
                            #obj1_label = 0.0
                            obj1_label = 0

                        if ent2.label_ in OBJ2_TARGET[1]:
                            obj2_label = OBJ2_TARGET[0]
                        elif ent2.label_ in OBJ2_EXCEPT[1]:
                            obj2_label = OBJ2_EXCEPT[0]
                        else:
                            obj2_label = 0


                        new_line += str(obj1_label) + ',' + str(float(obj2_label))
                        if ent.root.pos_ in OBJ1_POS[1]:
                            pos_val = OBJ1_POS[0]
                        else:
                            pos_val = 0
                        if ent2.root.pos_ in OBJ2_POS[1]:
                            pos_val2 = OBJ2_POS[0]
                        elif ent2.root.pos_ in OBJ2_POS_EXCEPT[1]:
                            pos_val2 = OBJ2_POS_EXCEPT[0]
                        else:
                            pos_val2 = 0.0
                        new_line += ',' + str(pos_val) + ',' + str(pos_val2)


                        head_id = ent.root.head.i + 1  # we want ids to be 1 based
                        #if ent == ent.root.head:  # and the ROOT to be 0.
                            #assert (word.dep_ == "ROOT"), word.dep_
                        #    head_id = 0  # root
                        head_id2 = ent2.root.head.i + 1  # we want ids to be 1 based
                        #if ent2 == ent2.root.head:  # and the ROOT to be 0.
                            #assert (word.dep_ == "ROOT"), word.dep_
                        #    head_id2 = 0  # root

                        dif = head_id - head_id2
                        if dif < 0:
                            sign = -1
                            dif *= -1
                        elif dif > 0:
                            sign = 1
                        else:
                            sign = 0
                        new_line += ',' + str(dif) + ','+ str(sign)
                        if ent2.upper_.find(contain_AP) != -1:
                            ap = 1
                        else :
                            ap = 0
                        new_line += ',' + str(ap)
                        #
                        # all other feature here
                        #

                        #new_line += ',' + str(ent.vector_norm) + ',' + str(ent2.vector_norm)
                        lines_list.append((index, (ent.text.strip(), ent2.text.strip()), new_line))
                        ## features end !!!!
        return lines_list



    def feature_train_set(self, train_file_name, annotation_file,output_csv_file):
        # use feature_line(line) to make CVS file according ALL_LABELS
        yes =0
        no =0
        with open(train_file_name, 'r') as f:
            with open(output_csv_file, 'w') as out:
                dont_care, data = annon_to_dict(annotation_file)
                line = ''
                for label in ALL_LABELS:
                    line += label + ','
                out.write(line[:-1]+'\n')
                for line in f:
                    for feature_set in self.feature_line(line):
                        if feature_set[1] in data[feature_set[0]]:
                            out.write(feature_set[2] + ',1\n')
                            yes += 1
                        elif yes > no and random.random() < 0.5:
                            out.write(feature_set[2] + ',0\n')
                            no += 1


from sys import argv
from Train_Decision_Tree import Train_Decision_Tree as tree
def main (a,b,c,d,e):
    print ('convert to csv')
    builder = FeatureBuilder()
    builder.feature_train_set(a, c, b)
    print ('build decision tree')
    dt = tree(b)
    dt.train(d, e)
    print ('done')
if __name__ == '__main__':
    main(argv[1],argv[2],argv[3],argv[4],argv[5])

