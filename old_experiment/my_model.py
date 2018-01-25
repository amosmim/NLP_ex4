from collections import defaultdict
from time import time

import spacy
from sklearn.metrics import accuracy_score

from FeatureBuilder import FeatureBuilder
from LabelChecker import LabelChecker
from MyClassifier import MyClassifier


def annotation_to_dict(filename):
    """
    :param filename: path of annotation-file
    :return: dictionary that maps sentence-number to sub-dict,
                sub-dict maps relation (number representing it) to a list,
                the list contains tuples of (obj1, obj2)
             relation2i is a dict that maps relation (string) to an index.
    """
    data = defaultdict(dict)
    relation2i = {'non': 0}  # maps relation to the number representing it
    with open(filename, 'r') as f:
        for line in f:
            """
            parts will be in next format:
                0      1        2       3       4
            sent_ith object relation subject sentence
            """
            parts = line.split('\t')
            sent_num = int(parts[0][4:])
            relation = parts[2]

            # add relation to the relations-map
            if relation not in relation2i:
                relation2i[relation] = len(relation2i)

            # add the tuple to the dict
            relation_index = relation2i[relation]
            if relation_index not in data[sent_num]:
                data[sent_num][relation_index] = []
            data[sent_num][relation_index].append((parts[1], parts[3]))
    return data, relation2i


def accuracy_of(gold_labels, pred_labels):
    good = bad = 0.0
    for gold, pred in zip(gold_labels, pred_labels):
        if gold == pred == 1:
            good += 1
        elif gold == 1 or pred == 1:
            bad += 1
    return good / (good + bad)


def train_classifier(nlp, train_txt_file, train_annotation_file):
    fb = FeatureBuilder(nlp)
    features_matrix = fb.get_features_of_file(train_txt_file)

    annotation_dict, r2i = annotation_to_dict(train_annotation_file)
    lc = LabelChecker(annotation_dict, r2i)

    cls = MyClassifier(fb.features_to_index)
    gold_labels = lc.get_labels_of(features_matrix)
    cls.train_on(features_matrix, gold_labels)

    pred_labels = cls.predict(features_matrix)
    acc_all = accuracy_score(gold_labels, pred_labels)
    acc_filtered = accuracy_of(gold_labels, pred_labels)
    print 'train - accuracy all %0.2f%%' % (acc_all * 100.0)
    print 'train - accuracy filtered %0.2f%%' % (acc_filtered * 100.0)

    return cls


def predict(nlp, cls, file_path_txt, out_file_path):
    fb = FeatureBuilder(nlp)
    features_matrix_str = fb.get_features_of_file(file_path_txt)

    pred_labels = cls.predict(features_matrix_str)

    out_file = open(out_file_path, 'w')
    for (idxs, features_list), label in zip(features_matrix_str, pred_labels):
        if label == 1:
            sent_num, obj1, obj2 = idxs
            sent_num = 'sent' + str(sent_num)
            obj1, obj2 = str(obj1), str(obj2)
            out_file.write(sent_num + '\t' + obj1 + '\t' + 'Live_In' + '\t' + obj2 + '\t\n')

    out_file.close()


def main():
    t0 = time()
    print 'start extracting features'

    nlp = spacy.load('en')
    train_txt_file, train_annotation_file = 'data/Corpus.TRAIN.txt', 'data/TRAIN.annotations'
    cls = train_classifier(nlp, train_txt_file, train_annotation_file)

    test_txt_file, test_annotation_file = 'data/Corpus.DEV.txt', 'data/DEV.annotations'

    print 'time to pre:', time() - t0
    t0 = time()

    # predict(nlp, cls, train_txt_file, 'output.train.txt')
    predict(nlp, cls, test_txt_file, 'output.dev.txt')

    print 'time to predict and write:', time() - t0


if __name__ == '__main__':
    main()
