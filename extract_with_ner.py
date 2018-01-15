from time import time
import codecs

import spacy
import wiki_exp

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
        line_copy = line
        sent = nlp(line)
        ner = sent.ents

        # extract candidates for each object in the relations
        obj1_list, obj2_list = [], []
        for ne in ner:
            ent_type = ne.root.ent_type_
            if ent_type in obj1_options:
                obj1_list.append(ne)
                line_copy = line_copy.replace(ne.text, '$', 1)
            elif ent_type in obj2_options:
                obj2_list.append(ne)
                line_copy = line_copy.replace(ne.text, '$', 1)

        obj1_cand_wiki = wiki_exp.extract_obj1_candidates(line_copy, window=2)
        line_copy_obj1 = line_copy
        for cand in obj1_cand_wiki:
            line_copy_obj1 = line_copy_obj1.replace(cand, '$', 1)
        obj1_cand_wiki.extend(wiki_exp.extract_obj1_candidates(line_copy_obj1, window=1))

        obj2_cand_wiki = wiki_exp.extract_obj2_candidates(line_copy, window=2)
        line_copy_obj2 = line_copy
        for cand in obj2_cand_wiki:
            line_copy_obj2 = line_copy_obj2.replace(cand, '$', 1)
        obj2_cand_wiki.extend(wiki_exp.extract_obj2_candidates(line_copy_obj2, window=1))

        obj1_list.extend(obj1_cand_wiki)
        obj2_list.extend(obj2_cand_wiki)

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

    apply_on('data/Corpus.TRAIN.txt', 'output_train.txt')

    print 'time to run all:', time() - t0

