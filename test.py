import eval
import extract

if __name__ == '__main__':
    extract.main('data/Corpus.DEV.txt', 'data/Corpus.TRAIN.txt', 'data/TRAIN.annotations', 'output.dev.txt')
    eval.main('data/DEV.annotations', 'output.dev.txt')
