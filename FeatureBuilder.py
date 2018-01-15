import spacy
import random
from eval import annon_to_dict
FEATURES_LABEL = ['obj1 label','obj2 label']
ALL_LABELS = ['index'] + FEATURES_LABEL + ['Is live in']


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
            if ent.text.strip() != '':
                for ent2 in sent.ents:
                    if (ent.text != ent2.text) and ent2.text.strip() != '':
                        new_line = str(index) + ','
                        new_line += str(float(ent.label)) +','+ str(float(ent2.label))
                        #
                        # all other feature here
                        #
                        lines_list.append((index, (ent.text.strip(), ent2.text.strip()), new_line))
        return lines_list



    def feature_train_set(self, train_file_name, annotation_file,output_csv_file):
        # use feature_line(line) to make CVS file according ALL_LABELS
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
                        elif random.random() < 0.3:
                            out.write(feature_set[2] + ',0\n')


from sys import argv
from Train_Decision_Tree import Train_Decision_Tree as tree
if __name__ == '__main__':
    print ('convert to csv')
    builder = FeatureBuilder()
    builder.feature_train_set(argv[1], argv[3], argv[2])
    print ('build decision tree')
    dt = tree(argv[2])
    dt.train(argv[4], argv[5])
    print ('done')
