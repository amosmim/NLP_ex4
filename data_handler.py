class DataHandler(object):
    def __init__(self, train_file_path):
        self._obj1_white_list = set()
        self._obj2_white_list = set()
        self._obj2_black_list = set()

        self._relations_for_obj1 = ['Live_In', 'Kill', 'Work_For']
        self._relations_for_obj2 = ['OrgBased_In', 'Live_In', 'Kill', 'Located_In']

        self._fill_candidates(train_file_path)
        self._fill_from_nationalities_file('list_of_nationalities.txt')

    def _features_from_given_relation(self, relation_type, obj, subject):
        """ given a relation and its pair, check if the data is associated to us """
        if relation_type in self._relations_for_obj1:
            self._obj1_white_list.add(obj)
        if relation_type in self._relations_for_obj2:
            self._obj2_white_list.add(subject)

    def _fill_candidates(self, filename):
        """ goes through filename and save relevant data """
        with open(filename, 'r') as f:
            for line in f:
                """
                parts will be in next format:
                    0      1        2       3       4
                sent_ith object relation subject sentence
                """
                parts = line.split('\t')
                self._features_from_given_relation(parts[2], parts[1], parts[3])

    def _fill_from_nationalities_file(self, file_path):
        """
        collect data of obj2 candidates and obj2 wrong candidates.
        :param file_path: contains list of nationalities.
        """
        with open(file_path, 'r') as f:
            for line in f:
                """ line is in format of 'place - nationality' """
                line = line.strip()
                place, nationality = line.split(' - ')
                self._obj2_white_list.add(place)
                self._obj2_black_list.add(nationality)

    def check_cand_obj1(self, phrase):
        """ 1 for good, 0 for neutral """
        if phrase in self._obj1_white_list:
            return 1
        return 0

    def check_cand_obj2(self, phrase):
        """ 1 for good, 0 for neutral, -1 for negative """
        if phrase in self._obj2_white_list:
            return 1
        if phrase in self._obj2_black_list:
            return -1
        return 0

    def add_obj1_cand(self, phrase_list):
        self._obj1_white_list.update(phrase_list)

    def add_obj2_cand(self, phrase_list):
        self._obj2_white_list.update(phrase_list)


if __name__ == '__main__':
    dh = DataHandler('data/TRAIN.annotations')
