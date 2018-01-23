import sys
from collections import defaultdict

RELATION_LABEL = 'Live_In'


def annon_to_dict(file_name):
    data = defaultdict(list)
    labeled = 0.0
    with open(file_name, 'r') as f:
        for line in f:
            """
            parts will be in next format:
                0      1        2       3       4
            sent_ith object relation subject sentence
            """
            parts = line.split('\t')
            if parts[2] == RELATION_LABEL:
                labeled += 1
                # if (parts[1], parts[3]) in data[int(parts[0][4:])]:
                #   print ("Duplactated!!! == " + str((parts[1], parts[3])))
                data[int(parts[0][4:])].append((parts[1], parts[3]))
    return labeled, data


if __name__ == '__main__':
    gold_file_name = sys.argv[1]
    predict_file_name = sys.argv[2]
    false_positive = []
    false_negative = []

    print 'Start read annotations files'
    gold_segments, gold_data = annon_to_dict(gold_file_name)
    all_predicts, predict_data = annon_to_dict(predict_file_name)
    print 'Finished read annotations files'

    print 'Start compare the data'
    good_predicts = 0.0
    keys = gold_data.keys()
    keys.sort()
    for sentence_num in keys:
        for relation in gold_data[sentence_num]:
            if relation in predict_data[sentence_num]:
                good_predicts += 1
            else:
                false_negative.append((sentence_num,) + relation)

    good_predicts2 = 0
    keys = predict_data.keys()
    keys.sort()
    for sentence_num in keys:
        for relation in predict_data[sentence_num]:
            if relation not in gold_data[sentence_num]:
                false_positive.append((sentence_num,) + relation)
            else:
                good_predicts2 += 1
    print 'Finished compare the data'

    precision = good_predicts / all_predicts
    recall = good_predicts / gold_segments

    f1 = (precision * recall) * 2
    if f1 != 0.0:
        f1 /= precision + recall
    # Calculations tests
    right = len(false_positive) + good_predicts
    left = all_predicts
    if left != right:
        print ("calculate error No.1 {0}!={1}".format(left, right))
    right = good_predicts + len(false_negative)
    left = gold_segments
    if left != right:
        print "calculate error No.2 {0}!={1}".format(left, right)

    # print results
    print ('\nPrecision: ' + str(precision) + '\tRecall: ' + str(recall) + '\tF1: ' + str(f1))

    print ("\nFalse Negative:")
    for fn in false_negative:
        print "\tsentence No.{0}:\tobj1 {1},\tobj2 {2}".format(fn[0], fn[1], fn[2])

    print ("\n\nFalse Positive:")
    for fp in false_positive:
        print "\tsentence No.{0}:\tobj1 {1},\tobj2 {2}".format(fp[0], fp[1], fp[2])
