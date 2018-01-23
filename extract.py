from sys import argv
from TrainFeature import TrainFeature as Model


def main(a):
    SVM = Model()
    SVM.train('Corpus.TRAIN.txt', 'TRAIN.annotations')

    with open(a, 'r') as f:
        with open('predict.annotations', 'w') as out:
            print ('Start')
            for line in f:
                if line[0] == '#':
                    print ('we need not process corpus!')
                    return
                parts = line.split('\t', 1)
                index = int(parts[0][4:])
                for pair in SVM.predict_line(parts[1]):
                    out.write("sent{0}\t{1}\tLive_In\t{2}\t( {3} )\n".format(index, pair[0], pair[1],
                                                parts[1].split('\n', 1)[0]))

            print ('Done')


if __name__ == '__main__':
    main(argv[1])