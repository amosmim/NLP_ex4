def get_tok_of(ne, docs):
    ne_text = ne.text
    for tok in docs:
        if tok.text in ne_text:
            return tok
    raise Exception('no token found!')


def get_noun_chunk_of(ne, docs):
    ne_text = ne.text
    for chunk in docs.noun_chunks:
        if ne_text in chunk.text:
            return chunk
    return None


def get_ner_of(tok, ner):
    tok_text = tok.text
    for ne in ner:
        if tok_text in ne.text:
            return ne
    return None


class FeatureBuilder(object):
    def __init__(self, nlp):
        self.nlp = nlp
        self.features_to_index = dict()  # encode features

    def features_for_pair_tok(self, tok1, tok2, docs):
        features = ['TOK']

        ner = docs.ents
        ne1 = get_ner_of(tok1, ner)
        ne2 = get_ner_of(tok2, ner)
        helper = []

        try:
            features.append(ne1.root.ent_type_)
            features.append(ne2.root.ent_type_)

            features.append(ne1.root.ent_iob_)
            features.append(ne2.root.ent_iob_)

            features.append(ne2.root.text)
            features.append(ne2.root.lemma_)
        except:
            for _ in range(5 - len(list(helper))):
                helper.append('-')
        features.extend(helper)

        features.append(tok1.pos_)
        features.append(tok2.pos_)

        features.append(tok1.tag_)
        features.append(tok2.tag_)

        features.append(tok1.dep_)
        features.append(tok2.dep_)

        features.append(str(tok1.n_lefts))
        features.append(str(tok1.n_rights))
        features.append(str(tok2.n_lefts))
        features.append(str(tok2.n_rights))

        heads = []
        try:
            heads.append(tok1.head.pos_)
            heads.append(tok1.head.head.pos_)
            heads.append(tok2.head.pos_)
            heads.append(tok2.head.head.pos_)

            chunk2 = get_noun_chunk_of(ne2, docs)
            heads.append(chunk2.root.dep_)
        except:
            for _ in range(5 - len(list(heads))):
                heads.append('-')
        features.extend(heads)

        return features

    def features_for_pair_ne(self, ne1, ne2, docs):
        tok1 = get_tok_of(ne1, docs)
        tok2 = get_tok_of(ne2, docs)
        chunk2 = get_noun_chunk_of(ne2, docs)

        features = ['NER']

        features.append(ne1.root.ent_type_)
        features.append(ne2.root.ent_type_)

        features.append(ne1.root.ent_iob_)
        features.append(ne2.root.ent_iob_)

        features.append(ne2.root.text)
        features.append(ne2.root.lemma_)

        features.append(tok1.pos_)
        features.append(tok2.pos_)

        features.append(tok1.tag_)
        features.append(tok2.tag_)

        features.append(tok1.dep_)
        features.append(tok2.dep_)

        features.append(str(tok1.n_lefts))
        features.append(str(tok1.n_rights))
        features.append(str(tok2.n_lefts))
        features.append(str(tok2.n_rights))

        heads = []
        try:
            heads.append(tok1.head.pos_)
            heads.append(tok1.head.head.pos_)
            heads.append(tok2.head.pos_)
            heads.append(tok2.head.head.pos_)

            heads.append(chunk2.root.dep_)
        except:
            for _ in range(5 - len(list(heads))):
                heads.append('-')
        features.extend(heads)

        return features

    def features_for_pair_chunks(self):
        pass

    def get_features_of_line(self, line):
        """
        :param line: string in the following format - sentith \t real_line EOL,
                        sentith is a string like 'sent10',
                        real_line is a string,
                        EOL is '\n'
        :return: list of lists, each sub-list contains features
        """
        features_matrix = []

        # extract parts frm line
        line = line.strip()
        sent_num, line = line.split('\t')
        sent_num = int(sent_num[4:])

        # extract features from line
        docs = self.nlp(unicode(line))

        for tok1 in docs:
            # check for add encoding
            if tok1.text not in self.features_to_index:
                self.features_to_index[tok1.text] = len(self.features_to_index)
            for tok2 in docs:
                if tok1 == tok2:
                    continue

                idxs = []
                idxs.append(sent_num)
                idxs.append(tok1.text)
                idxs.append(tok2.text)

                features = self.features_for_pair_tok(tok1, tok2, docs)
                features_matrix.append((idxs, features))

        ner = docs.ents
        for ne1 in ner:
            # check for add encoding
            if ne1.text not in self.features_to_index:
                self.features_to_index[ne1.text] = len(self.features_to_index)
            for ne2 in ner:
                if ne1 == ne2:
                    continue

                idxs = []
                idxs.append(sent_num)
                idxs.append(ne1.text)
                idxs.append(ne2.text)

                features = self.features_for_pair_tok(ne1, ne2, docs)
                features_matrix.append((idxs, features))

        return features_matrix

    def get_features_of_file(self, file_path):
        """
        :param file_path: path to file to process.
        :return: list of lists, each sub list contains features
        """
        features = []
        with open(file_path, 'r') as f:
            for line in f:
                features.extend(self.get_features_of_line(line))

        return features
