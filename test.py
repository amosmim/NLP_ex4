import eval, extract

if __name__ == '__main__':
    extract.main('data/Corpus.DEV.txt')
    eval.main('data/DEV.annotations', 'output.dev.txt')
    # extract.main('Corpus.TRAIN.txt')
    # eval.main('TRAIN.annotations' ,'predict.annotations')
