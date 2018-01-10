from time import time
import codecs

import spacy

nlp = spacy.load('en')

RELATION = 'Live_In'
obj1_options = [u'PERSON']
obj2_options = [u'ORG', u'GPE']


def read_lines(fname):
    for line in codecs.open(fname, encoding="utf8"):
        sent_id, sent = line.strip().split("\t")
        sent = sent.replace("-LRB-", "(")
        sent = sent.replace("-RRB-", ")")
        yield sent_id, sent


def apply_on(filename):
    out_file = open('output.txt', 'w')
    for sent_id, line in read_lines(filename):
        sent = nlp(line)
        ner = sent.ents

        obj1_list, obj2_list = [], []
        for ne in ner:
            ent_type = ne.root.ent_type_
            if ent_type in obj1_options:
                obj1_list.append(ne)
            elif ent_type in obj2_options:
                obj2_list.append(ne)
        for ne1 in obj1_list:
            for ne2 in obj2_list:
                out_file.write(sent_id + '\t' +
                               str(ne1) + '\t' + RELATION + '\t' + str(ne2) +
                               '\t( ' + line + ')\n')
    out_file.close()


if __name__ == '__main__':
    t0 = time()
    print 'start'

    apply_on('data/Corpus.TRAIN.txt')

    print 'time to run all:', time() - t0
