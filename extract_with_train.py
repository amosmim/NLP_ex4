from time import time
import codecs
import spacy

nlp = spacy.load('en')

obj1_features = set()
obj2_features = set()

relations_for_obj1 = ['Live_In', 'Kill', 'Work_For']
relations_for_obj2 = ['OrgBased_In', 'Live_In', 'Kill', 'Located_In']
ner_obj1 = [u'PERSON']
ner_obj2 = [u'ORG', u'GPE', u'NORP', u'LOC']
pos_obj1 = [u'PROPN']


def read_lines(filename):
    for line in codecs.open(filename, encoding="utf8"):
        sent_id, sent = line.strip().split("\t")
        sent = sent.replace("-LRB-", "(")
        sent = sent.replace("-RRB-", ")")
        yield sent_id, sent


def find_relation_types_in(filename):
    """ find all the existed relations in the .annotations file """
    relation_types = set()
    with open(filename, 'r') as f:
        for line in f:
            relation_types.add(line.split('\t')[2])

    for i, rel in enumerate(relation_types):
        print rel


def features_from_given_relation(relation_type, obj, subject):
    if relation_type in relations_for_obj1:
        obj1_features.add(obj)
    if relation_type in relations_for_obj2:
        obj2_features.add(subject)


def features_from_ner(doc):
    ner = doc.ents
    for ne in ner:
        ne_type = ne.root.ent_type_
        if ne_type in ner_obj1:
            obj1_features.add(ne.text)
        elif ne_type in ner_obj2:
            obj2_features.add(ne.text)


def features_from_pos(doc):
    for token in doc:
        if token.pos_ in pos_obj1:
            obj1_features.add(token.text)


def extract_features(filename1, filename2):
    with open(filename1, 'r') as f:
        for line in f:
            """
            parts will be in next format:
                0      1        2       3       4
            sent_ith object relation subject sentence
            """
            parts = line.split('\t')
            features_from_given_relation(parts[2], parts[1], parts[3])

    for sent_id, sent in read_lines(filename2):
        doc = nlp(sent)
        features_from_ner(doc)
        features_from_pos(doc)


def apply_on(input_filename, out_filename):
    out_file = open(out_filename, 'w')
    for sent_id, sent in read_lines(input_filename):
        pass

    out_file.close()


if __name__ == '__main__':
    t0 = time()
    print 'start'

    extract_features('data/TRAIN.annotations', 'data/Corpus.TRAIN.txt')
    apply_on('data/Corpus.TRAIN.txt', 'output_2.txt')

    print 'time to run all:', time() - t0
