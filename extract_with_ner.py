from time import time
import codecs
import spacy

nlp = spacy.load('en')

# relation, and allowed types for each object in the relation
RELATION = 'Live_In'
obj1_options = [u'PERSON']
obj2_options = [u'ORG', u'GPE', u'NORP', u'LOC']


def read_lines(fname):
    for line in codecs.open(fname, encoding="utf8"):
        sent_id, sent = line.strip().split("\t")
        sent = sent.replace("-LRB-", "(")
        sent = sent.replace("-RRB-", ")")
        yield sent_id, sent


def apply_on(filename, out_filename):
    """
    goes through filename and write all the relations found,
    correspond to the relation mentioned on top,
    into out_filename
    """
    out_file = open(out_filename, 'w')
    for sent_id, line in read_lines(filename):
        sent = nlp(line)
        ner = sent.ents

        # extract candidates for each object in the relations
        obj1_list, obj2_list = [], []
        for ne in ner:
            ent_type = ne.root.ent_type_
            if ent_type in obj1_options:
                obj1_list.append(ne)
            elif ent_type in obj2_options:
                obj2_list.append(ne)

        # match objects to a relation
        for ne1 in obj1_list:
            for ne2 in obj2_list:
                out_file.write(sent_id + '\t' +
                               str(ne1) + '\t' + RELATION + '\t' + str(ne2) +
                               '\t( ' + line + ')\n')
    out_file.close()


if __name__ == '__main__':
    t0 = time()
    print 'start'

    apply_on('data/Corpus.DEV.txt', 'output_dev.txt')

    print 'time to run all:', time() - t0
