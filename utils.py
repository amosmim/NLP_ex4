import codecs


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
