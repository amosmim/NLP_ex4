import eval, extract

if __name__ == '__main__':
    extract.main('Corpus.DEV.txt')
    eval.main('DEV.annotations', 'predict.annotations')
    # extract.main('Corpus.TRAIN.txt')
    # eval.main('TRAIN.annotations' ,'predict.annotations')
