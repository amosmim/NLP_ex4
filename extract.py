"""
maimona5 301236287
moshiat 316131259
"""

from sys import argv
from TrainFeature import TrainFeature as Model


def main(a, train_filename, train_annotation_filename, output_filename):
    model = Model()
    model.train(train_filename, train_annotation_filename)

    with open(a, 'r') as f:
        with open(output_filename, 'w') as out:
            print ('Start')
            for line in f:
                if line[0] == '#':
                    print ('we need not process corpus!')
                    return
                parts = line.split('\t', 1)
                index = int(parts[0][4:])
                for pair in model.predict_line(parts[1]):
                    out.write("sent{0}\t{1}\tLive_In\t{2}\t( {3} )\n".format(index, pair[0], pair[1],
                                                                             parts[1].split('\n', 1)[0]))

            print ('Done')


if __name__ == '__main__':
    """
    args: file_to_predict_on train_file_path_txt train_annotations_path output_filename
    """
    main(argv[1], argv[2], argv[3], argv[4])
