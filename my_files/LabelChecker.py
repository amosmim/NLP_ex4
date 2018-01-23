class LabelChecker(object):
    def __init__(self, annotation_dict, r2i):
        self.annotation_dict = annotation_dict
        self.r2i = r2i
        self.i2r = {i: r for r, i in r2i.iteritems()}

    def get_label_index_of(self, idxs):
        """
        :param idxs: list - sent_num obj1 obj2
        :return: label index.
        """
        sent_num, item = idxs[0], (idxs[1], idxs[2])
        options = self.annotation_dict[sent_num]
        for relation_index, tuples_list in options.iteritems():
            if item in tuples_list:
                return relation_index
        return self.r2i['non']  # no relation

    def get_labels_of(self, features_matrix):
        """
        :param features_matrix: list of lists, each is a features list
        :return: list of labels, the ith label is connected to the ith features-list.
        """
        labels = []
        for idxs, _ in features_matrix:
            labels.append(self.get_label_index_of(idxs))

        return labels
