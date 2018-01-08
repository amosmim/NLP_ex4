import sys
from collections import defaultdict

RELATION_LABEL = 'Live_In'

def annon_to_dict(file_name):
    data = defaultdict(list)
    labeled = 0.0
    with open(file_name, 'r') as f:
        for line in f:
            parts = line.split('\t')
            if parts[2] == RELATION_LABEL:
                labeled += 1
                data[int(parts[0][4:])].append((parts[1], parts[3]))
    return labeled , data



if __name__ == '__main__':
    gold_file_name = sys.argv[1]
    predict_file_name = sys.argv[2]

    print ('Start read annotations files')
    gold_segments, gold_data = annon_to_dict(gold_file_name)
    all_predicts, predict_data = annon_to_dict(predict_file_name)
    print ('Finished read annotations files')
    print ('Start compare the data')
    good_predicts = 0.0
    for sentence_num in gold_data.keys():
        for relation in gold_data[sentence_num]:
            if relation in predict_data[sentence_num]:
                good_predicts += 1

    print  ('Finished compare the data')

    precision = good_predicts / all_predicts
    recall = good_predicts / gold_segments

    f1 = (precision * recall) * 2
    if f1 != 0.0 :
        f1 = f1 / (precision + recall)
    print ('precision: ' + str(precision) + '\tRecall: ' + str(recall) + '\tF1: ' + str(f1))
